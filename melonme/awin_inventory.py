"""Lean Awin inventory access. Products != promotions != joined programmes.

Feed downloads can be enormous: scan a bounded number of JSONL rows and
explicitly report partial coverage. Never claim the scan was exhaustive.
No credentials are stored here, and no arbitrary host may be contacted.
"""
from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

_STOP = frozenset(("which what from about would please suche einen einer einem welche "
                  "the and for with best that this good looking empfehlen nach die der "
                  "das und mit für ohne oder eine how who was").split())


def _terms(value: object) -> set[str]:
    return {w for w in re.findall(r"[^\W_]+", str(value or "").casefold())
            if len(w) >= 3 and w not in _STOP}


def _score(query: str, item: dict) -> float:
    wanted = _terms(query)
    if not wanted:
        return 0.0
    title = str(item.get("title") or "")
    brand = str(item.get("brand") or "")
    description = str(item.get("description") or "")
    title_words = _terms(title + " " + brand)
    detail_words = _terms(description[:500])
    score = (2 * len(wanted & title_words) + len(wanted & (detail_words - title_words)))
    return score / (2 * max(1, len(wanted)))


def _normalize(raw: dict, advertiser_id: int, market: str) -> dict | None:
    # Awin's JSONL example contains structured sections (meta/product_basic).
    # Different advertisers expose fields across sections. Normalize them
    # without assuming that title, link, price and stock share one subobject.
    if "error" in raw:
        return None
    product = {}
    for key, section in raw.items():
        if key.startswith("product_") and isinstance(section, dict):
            product.update(section)
    product.update({k: v for k, v in raw.items() if not isinstance(v, dict)})
    if not product:
        return None
    title = str(product.get("title") or "").strip()
    url = str(product.get("link") or "").strip()
    # Awin's documented non-tracking product link may be HTTP or HTTPS.
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        valid = parsed.scheme in ("http", "https") and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        valid = False
    if not title or not valid:
        return None
    availability = str(product.get("availability") or "").lower().strip()
    if availability in ("out_of_stock", "discontinued"):
        return None
    price = str(product.get("sale_price") or product.get("price") or "")
    number = None
    currency = None
    match = re.fullmatch(r"\s*(\d+(?:\.\d{1,2})?)\s+([A-Z]{3})\s*", price)
    if match:
        number, currency = match.groups()
    result = {
        "provider": "awin",
        "advertiser_id": advertiser_id,
        "product_id": str(product.get("id") or ""),
        "title": title,
        "description": str(product.get("description") or "")[:500],
        "brand": str(product.get("brand") or ""),
        "url": url,
        "market": market,
        "available": True if availability == "in_stock" else None,
        "price": number,
        "currency": currency,
        "source": "awin_enhanced_feed",
    }
    return result


def _no_redirect_open(request: Request, timeout: int = 12):
    # Bearer credentials must not be forwarded to HTTP redirect targets.
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    return build_opener(NoRedirect).open(request, timeout=timeout)


def scan_enhanced_feed(
    publisher_id: str, token: str, advertiser_id: int, locale: str,
    market: str, query: str | list[str], *, max_rows: int = 5000, limit: int = 10
) -> dict:
    """Read at most max_rows JSONL products with bounded memory.

    Awin publisher feed usage: <= 5 feed requests/minute, not concurrent per
    advertiser feed. Caller must coordinate request rate across workers.
    A partial scan cannot establish absence of suitable products.
    """
    if not re.fullmatch(r"\d+", str(publisher_id)) or not re.fullmatch(r"\d+", str(advertiser_id)):
        raise ValueError("INVALID_FEED_IDENTIFIERS")
    if not re.fullmatch(r"[a-z]{2}_[A-Z]{2}", locale or ""):
        raise ValueError("INVALID_FEED_LOCALE")
    if not re.fullmatch(r"[A-Z]{2}", market or ""):
        raise ValueError("INVALID_FEED_MARKET")
    if locale[-2:] != market:
        raise ValueError("LOCALE_MARKET_MISMATCH")
    if not token:
        raise ValueError("TOKEN_MISSING")
    max_rows = min(max(1, int(max_rows)), 100000)
    limit = min(max(1, int(limit)), 50)
    url = (
        "https://api.awin.com/publishers/" + str(publisher_id)
        + "/awinfeeds/download/" + str(advertiser_id)
        + "-retail-" + locale + ".jsonl"
    )
    req = Request(url, headers={"Authorization": "Bearer " + token,
                                "Accept": "application/x-ndjson"})
    # Score each actual buyer request independently. Joining 100 unrelated
    # questions previously suppressed almost every product match.
    queries = [str(q).strip() for q in (query if isinstance(query, list) else [query])
               if str(q).strip()][:100]
    if not queries:
        raise ValueError("QUERY_MISSING")
    per_query: list[list[dict]] = [[] for _ in queries]
    rows = 0
    complete = False
    try:
        with _no_redirect_open(req, timeout=12) as response:
            while rows < max_rows:
                line = response.readline(131073)
                if not line:
                    complete = True
                    break
                if len(line) > 131072:
                    raise ValueError("FEED_LINE_TOO_LARGE")
                rows += 1
                try:
                    raw = json.loads(line.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    raise ValueError("INVALID_FEED_JSONL") from None
                if not isinstance(raw, dict):
                    continue
                if "error" in raw:
                    raise ValueError("AWIN_FEED_ERROR_TRAILER")
                item = _normalize(raw, int(advertiser_id), market)
                if item is None:
                    continue
                for qidx, candidate_query in enumerate(queries):
                    score = _score(candidate_query, item)
                    if score <= 0:
                        continue
                    candidate = {**item, "relevance": round(score, 4)}
                    bucket = per_query[qidx]
                    bucket.append(candidate)
                    if len(bucket) > limit * 2:
                        bucket.sort(key=lambda x: (-x["relevance"], x["title"]))
                        del bucket[limit:]
    except HTTPError as err:
        raise ValueError("FEED_HTTP_" + str(err.code)) from None
    except (URLError, TimeoutError) as err:
        raise ValueError("FEED_" + type(err).__name__) from None
    # Keep up to 'limit' matches per buyer query, deduplicating products.
    # The same feed is downloaded only once, regardless of question count.
    matches: dict[tuple[str, str], dict] = {}
    for bucket in per_query:
        for item in sorted(bucket, key=lambda x: (-x["relevance"], x["title"]))[:limit]:
            key = (str(item.get("advertiser_id")), str(item.get("product_id") or item["url"]))
            old = matches.get(key)
            if old is None or item["relevance"] > old["relevance"]:
                matches[key] = item
    ordered = sorted(matches.values(), key=lambda x: (-x["relevance"], x["title"]))
    return {
        "offers": ordered[:min(1000, limit * len(queries))],
        "query_count": len(queries),
        "scanned_rows": rows,
        "complete": complete,
        "partial": not complete,
        "source": "awin_enhanced_feed",
        "advertiser_id": int(advertiser_id),
        "locale": locale,
        "market": market,
    }
