"""Small, dependency-free MelonMe business core.

FruitStack supplies discovery, reasoning and publishing capabilities.
MelonMe decides on opportunities and integrates existing partner APIs.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler


class PartnerError(Exception):
    """A local partner failure: never a global opportunity-search failure."""


def _https_url(value: str) -> bool:
    try:
        p = urlparse(value)
        return p.scheme == "https" and bool(p.hostname) and not p.username and not p.password
    except ValueError:
        return False


def _product_url(value: str) -> bool:
    # Awin explicitly permits both HTTP and HTTPS merchant destinations.
    # Only API calls and bearer-token transport must require HTTPS.
    try:
        p = urlparse(value)
        return (p.scheme in ("http", "https") and bool(p.hostname)
                and not p.username and not p.password and len(value) <= 2000)
    except ValueError:
        return False


def _json_request(url: str, token: str, payload: dict | None = None) -> Any:
    if not _https_url(url):
        raise PartnerError("INVALID_HTTPS_ENDPOINT")
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    # urllib's default redirect handler can copy Authorization onto a redirected
    # request. Awin tokens and FruitStack bridge tokens must never be forwarded
    # to a different host under an API-controlled Location header.
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    try:
        with build_opener(NoRedirect).open(req, timeout=8) as reply:
            raw = reply.read(2_000_001)
            if len(raw) > 2_000_000:
                raise PartnerError("RESPONSE_TOO_LARGE")
            return json.loads(raw.decode("utf-8"))
    except HTTPError as err:
        raise PartnerError("HTTP_" + str(err.code)) from None
    except (URLError, TimeoutError, ValueError, UnicodeDecodeError) as err:
        raise PartnerError(type(err).__name__) from None


class Awin:
    """Uses the publisher's own token; no credentials or program access invented."""

    def __init__(self, publisher_id: str, token: str):
        if not re.fullmatch(r"\d+", publisher_id):
            raise PartnerError("INVALID_PUBLISHER_ID")
        if not token:
            raise PartnerError("AWIN_TOKEN_MISSING")
        self.publisher_id = publisher_id
        self.base = "https://api.awin.com/publishers/" + publisher_id
        self.token = token

    @classmethod
    def from_env(cls) -> Awin | None:
        publisher = os.environ.get("AWIN_PUBLISHER_ID", "")
        token = os.environ.get("AWIN_API_TOKEN", "")
        return cls(publisher, token) if publisher and token else None

    def programmes(self, market: str) -> list[dict]:
        if not re.fullmatch(r"[A-Z]{2}", market):
            raise PartnerError("MARKET_REQUIRED")
        query = urlencode({"relationship": "joined", "countryCode": market})
        result = _json_request(self.base + "/programmes?" + query, self.token)
        if not isinstance(result, list):
            raise PartnerError("INVALID_PROGRAMMES_RESPONSE")
        return result

    def link(self, advertiser_id: int, destination: str, clickref: str) -> str:
        if not _product_url(destination):
            raise PartnerError("INVALID_DESTINATION")
        payload: dict[str, Any] = {
            "advertiserId": int(advertiser_id),
            "destinationUrl": destination,
            "parameters": {"clickref": clickref[:50]},
        }
        result = _json_request(self.base + "/linkbuilder/generate", self.token, payload)
        link = result.get("url") if isinstance(result, dict) else None
        if not isinstance(link, str) or not _https_url(link):
            raise PartnerError("LINK_NOT_RETURNED")
        return link

    def promotions(self, market: str, *, max_pages: int = 2) -> list[dict]:
        """Read joined Awin offers without silently treating page one as exhaustive."""
        if not re.fullmatch(r"[A-Z]{2}", market):
            raise PartnerError("MARKET_REQUIRED")
        page_size = 100
        max_pages = min(max(int(max_pages), 1), 5)
        offers: dict[str, dict] = {}
        self.last_promotions_pages = 0
        self.last_promotions_partial = False
        for page in range(1, max_pages + 1):
            payload = {
                "filters": {"membership": "joined", "regionCodes": [market],
                            "status": "active", "type": "all"},
                "pagination": {"page": page, "pageSize": page_size},
            }
            data = _json_request(
                "https://api.awin.com/publisher/" + self.publisher_id + "/promotions",
                self.token, payload,
            )
            if isinstance(data, list):
                raw = data
            elif isinstance(data, dict):
                raw = next((data[key] for key in ("promotions", "items", "data", "results")
                            if isinstance(data.get(key), list)), None)
            else:
                raw = None
            if raw is None:
                raise PartnerError("PROMOTIONS_RESPONSE_UNRECOGNIZED")
            self.last_promotions_pages = page
            for item in raw:
                if not isinstance(item, dict):
                    continue
                advertiser = item.get("advertiser") or {}
                regions = item.get("regions") or {}
                if not isinstance(advertiser, dict) or advertiser.get("joined") is not True:
                    continue
                if isinstance(regions, dict) and not regions.get("all"):
                    listed = regions.get("list") or []
                    if not any(isinstance(v, dict) and v.get("countryCode") == market
                               for v in listed):
                        continue
                url = item.get("url")
                track = item.get("urlTracking")
                if not isinstance(url, str) or not _product_url(url):
                    continue
                key = str(advertiser.get("id")) + "|" + str(item.get("promotionId"))
                offers[key] = {
                    "provider": "awin_promotion", "advertiser_id": advertiser.get("id"),
                    "product_id": "promotion:" + str(item.get("promotionId")),
                    "title": str(item.get("title") or ""),
                    "description": str(item.get("description") or "")[:500],
                    "url": url, "market": market,
                    "affiliate_url": track if isinstance(track, str) and _https_url(track) else None,
                    "affiliate_verified": isinstance(track, str) and _https_url(track),
                    "available": True, "source": "awin_promotion",
                    "terms": item.get("terms"),
                }
            if len(raw) < page_size:
                break
        else:
            # The returned data may be useful, but there may be more pages.
            self.last_promotions_partial = True
        return list(offers.values())

    def transactions(self, start: str, end: str) -> list[dict]:
        # Awin documents a maximum window of 31 days per API request.
        from datetime import datetime
        try:
            fmt = "%Y-%m-%dT%H:%M:%S"
            delta = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
        except ValueError:
            raise PartnerError("INVALID_DATE_RANGE") from None
        if not 0 <= delta.total_seconds() <= 31 * 86400:
            raise PartnerError("DATE_RANGE_EXCEEDS_31_DAYS")
        query = urlencode({"startDate": start, "endDate": end, "timezone": "UTC"})
        result = _json_request(self.base + "/transactions/?" + query, self.token)
        if not isinstance(result, list):
            raise PartnerError("INVALID_TRANSACTIONS_RESPONSE")
        return result


_STOP = set(("best which what does should with from have that this please looking seeking "
             "welche welcher welches suche gesucht möchte besten oder eine einen guten "
             "nach über dem den die das und für mit bei ohne beste").split())


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[^\W_]+", text.casefold()) if len(w) >= 2 and w not in _STOP}


def _market(value: Any) -> str:
    market = str(value or "").upper().strip()
    return market if re.fullmatch(r"[A-Z]{2}", market) else ""


def _offer_match(question: dict, offer: dict, market: str) -> float:
    offer_market = _market(offer.get("market"))
    if not market or offer_market != market:
        return 0.0
    if offer.get("available") is False:
        return 0.0
    title = str(offer.get("title") or "")
    if not title or not _product_url(str(offer.get("url") or "")):
        return 0.0
    extra = question.get("search_terms") or []
    translated = " ".join(str(t) for t in extra[:30]) if isinstance(extra, list) else ""
    terms = _words(str(question.get("query") or question.get("text") or "") + " " + translated)
    keywords = _words(str(offer.get("keywords") or title) + " " +
                      str(offer.get("brand") or "") + " " +
                      str(offer.get("product_id") or "") + " " +
                      str(offer.get("description") or "")[:300])
    common = len(terms & keywords)
    if common == 0:
        return 0.0
    return round(common / max(len(terms), 1), 4)


def find(context: dict, awin: Awin | None = None,
         inventory_lookup: Any | None = None) -> dict:
    """Rank host-supplied real questions and real offers without inventing inventory.

    This function is deliberately host-driven: FruitStack discovers questions and
    obtains product catalogs; MelonMe neither scrapes arbitrarily nor assumes accounts.
    """
    questions = context.get("questions") or []
    offers = context.get("offers") or []
    if not isinstance(questions, list) or not isinstance(offers, list):
        return {"opportunities": [], "errors": [{"code": "INVALID_INPUT"}]}
    results: list[dict] = []
    errors: list[dict] = []
    try:
        limit = min(max(int(context.get("limit", 20)), 1), 100)
    except (TypeError, ValueError):
        limit = 20
        errors.append({"code": "INVALID_LIMIT_USED_DEFAULT"})
    # Bridge only to an already-existing FruitStack product/inventory capability.
    # The host can batch queries; MelonMe does not build a second crawler.
    if inventory_lookup is not None and context.get("use_inventory_bridge", True):
        payload = {
            "questions": [{
                "id": q.get("id") or q.get("source_url"),
                "text": q.get("query") or q.get("text"),
                "market": _market(q.get("market") or context.get("market")),
                "language": q.get("language") or context.get("language"),
                "search_terms": q.get("search_terms") or [],
            } for q in questions[:100] if isinstance(q, dict)],
            "limit_per_question": 10,
        }
        try:
            received = inventory_lookup(payload)
            new_offers = received.get("offers") if isinstance(received, dict) else None
            if not isinstance(new_offers, list):
                raise PartnerError("INVENTORY_RESPONSE_INVALID")
            offers = [*offers, *new_offers[:1000]]
        except Exception as err:
            errors.append({"provider": "fruitstack_inventory",
                           "code": (str(err) if isinstance(err, PartnerError)
                                    else type(err).__name__)})
    # Awin's actual enhanced feed is a product source, not a catalogue of
    # programmes. Each optional feed is downloaded once, for all questions in
    # its market; no silent assumption that the full market was searched.
    offers = offers[:2000]
    inventory_checks: list[dict] = []
    feed_requests = context.get("awin_feeds") or []
    if isinstance(feed_requests, list) and feed_requests:
        from melonme.awin_inventory import scan_enhanced_feed
        client = awin if awin is not None else Awin.from_env()
        for spec in feed_requests[:2]:
            if not isinstance(spec, dict):
                continue
            feed_market = _market(spec.get("market"))
            locale = str(spec.get("locale") or "")
            advertiser_id = spec.get("advertiser_id")
            feed_query = [str(q.get("query") or q.get("text") or "") + " " +
                          " ".join(str(x) for x in q.get("search_terms", [])[:20])
                          for q in questions[:100] if isinstance(q, dict)
                          and _market(q.get("market") or context.get("market")) == feed_market]
            if not feed_query:
                continue
            if client is None or not getattr(client, "publisher_id", None):
                errors.append({"provider": "awin_feed", "market": feed_market,
                               "code": "NOT_CONFIGURED"})
                continue
            try:
                scan = scan_enhanced_feed(
                    client.publisher_id, client.token, int(advertiser_id), locale,
                    feed_market, feed_query, max_rows=spec.get("max_rows", 5000),
                    limit=50)
                offers = [*offers, *scan["offers"]]
                inventory_checks.append({k: v for k, v in scan.items() if k != "offers"})
            except (ValueError, TypeError, PartnerError) as err:
                errors.append({"provider": "awin_feed", "market": feed_market,
                               "advertiser_id": advertiser_id, "code": str(err)})
    # Awin promotions are actual merchant offers, distinct from catalogue
    # products. Only an explicit opt-in calls the external offers endpoint.
    provider_checks: list[dict] = []
    if context.get("awin_promotions"):
        client = awin if awin is not None else Awin.from_env()
        for promo_market in sorted({
            _market(q.get("market") or context.get("market"))
            for q in questions[:100] if isinstance(q, dict)
        } - {""})[:3]:
            if client is None:
                errors.append({"provider": "awin_promotions",
                               "market": promo_market, "code": "NOT_CONFIGURED"})
                continue
            try:
                promotions = client.promotions(promo_market)
                offers = [*offers, *promotions]
                provider_checks.append({"provider": "awin_promotions",
                                        "market": promo_market, "offers": len(promotions),
                                        "pages": getattr(client, "last_promotions_pages", None),
                                        "partial": getattr(client, "last_promotions_partial", None)})
            except (PartnerError, ValueError) as err:
                errors.append({"provider": "awin_promotions",
                               "market": promo_market, "code": str(err)})
    for q in questions[:500]:
        if not isinstance(q, dict):
            continue
        qid = str(q.get("id") or q.get("source_url") or "").strip()
        if not qid or not (q.get("text") or q.get("query")):
            errors.append({"question_id": qid, "code": "QUESTION_INCOMPLETE"})
            continue
        market = _market(q.get("market") or context.get("market"))
        language = str(q.get("language") or context.get("language") or "")
        if not market:
            errors.append({"question_id": qid, "code": "MARKET_UNKNOWN"})
            continue  # Skip only this question, never others.
        matching = []
        # Include actual appended partner results; slicing to the first 2000
        # previously hid Awin inventory whenever the host filled its quota.
        for offer in offers[:6000]:
            if not isinstance(offer, dict):
                continue
            score = _offer_match(q, offer, market)
            if score:
                matching.append({
                    "title": str(offer["title"]),
                    "url": str(offer["url"]),
                    "provider": str(offer.get("provider") or "host"),
                    "market": market,
                    "price": offer.get("price"), "currency": offer.get("currency"),
                    "affiliate_url": offer.get("affiliate_url"),
                    "affiliate_verified": offer.get("affiliate_verified") is True,
                    "advertiser_id": offer.get("advertiser_id"),
                    "verified_facts": offer.get("verified_facts") or [],
                    "product_id": offer.get("product_id"),
                    "brand": offer.get("brand"),
                    "description": offer.get("description"),
                    "source": offer.get("source"),
                    "relevance": score,
                })
        matching.sort(key=lambda x: (-x["relevance"], x["title"].casefold()))
        results.append({
            "id": qid, "source_url": q.get("source_url"), "text": q.get("text") or q.get("query"),
            "market": market, "language": language, "channel": q.get("channel"),
            "offers": matching[:5],
            "decision": "READY" if matching else "NO_MATCH",
        })
    # Optional live partner capability probe; failure does not invalidate any other result.
    if context.get("probe_awin"):
        client = awin if awin is not None else Awin.from_env()
        for market in sorted({r["market"] for r in results}):
            if client is None:
                errors.append({"provider": "awin", "market": market, "code": "NOT_CONFIGURED"})
                continue
            try:
                programmes = client.programmes(market)
                provider_checks.append({"provider": "awin", "market": market, "code": "PROBED",
                                        "joined_programmes": len(programmes)})
            except PartnerError as exc:
                errors.append({"provider": "awin", "market": market, "code": str(exc)})
    results.sort(key=lambda r: (r["decision"] != "READY", -len(r["offers"])))
    return {"opportunities": results[:limit], "errors": errors,
            "inventory_checks": inventory_checks, "provider_checks": provider_checks,
            "checked": len(questions[:500])}


_AD_LABELS = {
    "de": "Werbung: Affiliate-Link.",
    "en": "Disclosure: affiliate link.",
    "fr": "Publicité : lien affilié.",
    "es": "Publicidad: enlace de afiliado.",
    "it": "Pubblicità: link di affiliazione.",
    "nl": "Advertentie: affiliatelink.",
    "pt": "Publicidade: link de afiliado.",
    "th": "โฆษณา: ลิงก์พันธมิตร",
}


def _disclosure(language: object) -> str:
    return _AD_LABELS.get(str(language or "en").lower().split("-")[0], _AD_LABELS["en"])


def _draft(opportunity: dict, offer: dict, link: str, tracked: bool) -> str:
    prefix = _disclosure(opportunity.get("language")) + "\n" if tracked else ""
    price = ""
    if offer.get("price") is not None and offer.get("currency"):
        price = " — " + str(offer["price"]) + " " + str(offer["currency"])
    facts = offer.get("verified_facts") or []
    detail = "\n" + "\n".join("- " + str(f) for f in facts[:5]) if isinstance(facts, list) else ""
    return prefix + str(offer["title"]) + price + detail + "\n" + link


def _resolve_offer(offer: dict, oid: str, market: str, awin: Awin | None) -> tuple[str, bool, str | None, list[str]]:
    """Try actual external link generation; errors affect this offer only."""
    warnings: list[str] = []
    link = str(offer["url"])
    tracked = False
    actual_clickref = None
    if str(offer.get("provider") or "").lower() == "awin" and offer.get("advertiser_id") is not None:
        client = awin if awin is not None else Awin.from_env()
        if client is None:
            warnings.append("AWIN_NOT_CONFIGURED")
        else:
            # Direct real link attempt: absence from an unrelated programme list
            # must not create another AVCOS-style false global restriction.
            try:
                clickref = hashlib.sha256((oid + "|" + link).encode("utf-8")).hexdigest()[:24]
                link = client.link(int(offer["advertiser_id"]), link, clickref)
                tracked = True
                actual_clickref = clickref
            except (PartnerError, ValueError, TypeError) as exc:
                warnings.append("AWIN_" + str(exc))
    elif offer.get("affiliate_url"):
        existing = offer["affiliate_url"]
        if isinstance(existing, str) and _https_url(existing) and offer.get("affiliate_verified") is True:
            link, tracked = existing, True
        else:
            warnings.append("AFFILIATE_LINK_UNVERIFIED")
    return link, tracked, actual_clickref, warnings


def execute(opportunity: dict, awin: Awin | None = None,
            publisher: Any | None = None) -> dict:
    """Generate an answer from actual offers, try local link alternatives.

    The publication target and channel are supplied by the host. A
    PUBLISHED claim requires an external receipt; no global stop.
    """
    oid = str(opportunity.get("id") or "")
    offers = opportunity.get("offers") or []
    if not isinstance(offers, list) or not offers:
        return {"status": "NO_ACTION", "id": oid, "reason": "NO_MATCH"}
    market = _market(opportunity.get("market"))
    if not market:
        return {"status": "NO_ACTION", "id": oid, "reason": "MARKET_UNKNOWN"}
    eligible = [
        offer for offer in offers[:10]
        if isinstance(offer, dict)
        and _market(offer.get("market")) == market
        and offer.get("available") is not False
        and offer.get("title")
        and _product_url(str(offer.get("url") or ""))
    ]
    if not eligible:
        reason = "MARKET_MISMATCH" if any(
            isinstance(o, dict) and _market(o.get("market")) != market for o in offers
        ) else "INVALID_OFFER"
        return {"status": "NO_ACTION", "id": oid, "reason": reason}
    # Preserve independent product relevance before any affiliate optimisation.
    def relevance(offer: dict) -> float:
        try:
            value = float(offer.get("relevance") or 0)
            return value if value == value and value >= 0 and value != float("inf") else 0
        except (TypeError, ValueError):
            return 0
    eligible.sort(key=lambda x: -relevance(x))
    peak = relevance(eligible[0])
    resolved: list[dict] = []
    warnings: list[str] = []
    for offer in eligible[:5]:
        link, tracked, clickref, local_warnings = _resolve_offer(offer, oid, market, awin)
        warnings.extend(local_warnings)
        resolved.append({"offer": offer, "link": link, "tracked": tracked, "clickref": clickref})
    # A tracked offer may win only if suitability is nearly identical.
    selected = next(
        (x for x in resolved if x["tracked"] and
         relevance(x["offer"]) >= 0.95 * peak),
        resolved[0],
    )
    authored = str(opportunity.get("answer_text") or "").strip()
    # Prevent affiliate links being added to copy referring to another product.
    if authored:
        host_product_id = str(opportunity.get("answer_offer_id") or "")
        matches = [x for x in resolved if
                   (host_product_id and str(x["offer"].get("product_id") or "") == host_product_id)
                   or (len(str(x["offer"].get("title") or "")) >= 5 and
                       str(x["offer"]["title"]).casefold() in authored.casefold())]
        if matches:
            matches.sort(key=lambda x: -relevance(x["offer"]))
            selected = matches[0]
        else:
            warnings.append("HOST_ANSWER_OFFER_MISMATCH_REBUILT")
            authored = ""
    offer, link, tracked = selected["offer"], selected["link"], selected["tracked"]
    if authored:
        answer = authored
        if tracked:
            if link not in answer:
                answer = answer.rstrip() + "\n" + link
            disclosure = _disclosure(opportunity.get("language"))
            if disclosure not in answer:
                answer = disclosure + "\n" + answer
    else:
        answer = _draft(opportunity, offer, link, tracked)
    fingerprint = hashlib.sha256(
        (oid + "\n" + str(opportunity.get("source_url") or "") + "\n" + answer).encode("utf-8")
    ).hexdigest()
    # Stable per target; editing prose must not create a new post on retries.
    publication_key = hashlib.sha256(
        (oid + "|" + str(opportunity.get("channel") or "") + "|" +
         str(opportunity.get("source_url") or "")).encode("utf-8")
    ).hexdigest()
    base = {
        "id": oid, "draft": answer, "tracked": tracked,
        "offer_url": link, "fingerprint": fingerprint,
        "publication_key": publication_key, "clickref": selected["clickref"],
        "warnings": warnings,
        "alternatives_checked": len(resolved),
        "selected_provider": str(offer.get("provider") or "host"),
        "selected_product_id": offer.get("product_id"),
    }
    if not opportunity.get("publish"):
        return {"status": "DRAFT_ONLY", **base}
    if publisher is None:
        return {"status": "DRAFT_ONLY", **base, "reason": "PUBLISH_ADAPTER_NOT_CONFIGURED"}
    if not opportunity.get("channel") or not opportunity.get("source_url"):
        return {"status": "DRAFT_ONLY", **base, "reason": "PUBLISH_TARGET_MISSING"}
    payload = {
        "id": oid, "channel": opportunity["channel"],
        "source_url": opportunity["source_url"],
        "text": answer, "idempotency_key": publication_key,
    }
    try:
        receipt = publisher(payload)
        external_id = receipt.get("external_id") if isinstance(receipt, dict) else None
        if not external_id:
            return {"status": "DRAFT_ONLY", **base, "reason": "EXTERNAL_RECEIPT_MISSING"}
        return {"status": "PUBLISHED", **base, "external_id": str(external_id),
                "external_url": receipt.get("url")}
    except Exception as exc:
        return {"status": "DRAFT_ONLY", **base,
                "reason": "PUBLISH_FAILED", "error_type": type(exc).__name__}


def _money(raw: Any) -> Decimal:
    try:
        value = Decimal(str(raw))
        if not value.is_finite():
            raise InvalidOperation
        return value
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError("INVALID_AMOUNT") from None


def learn(results: dict, awin: Awin | None = None) -> dict:
    """Summarize externally supplied transactions, payments and attributable costs.

    No currency conversion, no assumed payouts, and no invented conversion rate.
    """
    transactions = list(results.get("transactions") or [])
    errors: list[dict] = []
    if results.get("sync_awin"):
        client = awin if awin is not None else Awin.from_env()
        if client is None:
            errors.append({"provider": "awin", "code": "NOT_CONFIGURED"})
        else:
            try:
                start, end = results["start"], results["end"]
                transactions.extend(client.transactions(start, end))
            except (PartnerError, KeyError) as exc:
                errors.append({"provider": "awin", "code": str(exc)})
    totals: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"pending": Decimal(0), "approved": Decimal(0),
                 "declined": Decimal(0), "deleted": Decimal(0),
                 "paid": Decimal(0), "cost": Decimal(0)})
    # Awin can return the same transaction again after validation or amendment.
    # Select one current state per provider/id; never sum snapshots as sales.
    by_id: dict[tuple[str, str], dict] = {}
    rank = {"pending": 0, "approved": 1, "declined": 1, "deleted": 1}
    for item in transactions:
        if not isinstance(item, dict):
            continue
        tid = str(item.get("id") or item.get("transactionId") or "")
        provider = str(item.get("provider") or "awin")
        if not tid:
            continue
        key = (provider, tid)
        old = by_id.get(key)
        if old is None:
            by_id[key] = item
            continue
        new_status = str(item.get("commissionStatus") or item.get("status") or "").lower()
        old_status = str(old.get("commissionStatus") or old.get("status") or "").lower()
        new_time = str(item.get("amendmentDate") or item.get("validationDate") or "")
        old_time = str(old.get("amendmentDate") or old.get("validationDate") or "")
        if new_time and old_time:
            if new_time >= old_time:
                by_id[key] = item
        elif rank.get(new_status, -1) >= rank.get(old_status, -1):
            by_id[key] = item
    count = 0
    for (_, tid), item in by_id.items():
        currency = str(item.get("currency") or item.get("commissionCurrency") or "").upper()
        commission = item.get("commissionAmount", item.get("commission"))
        if isinstance(commission, dict):
            currency = str(commission.get("currency") or currency).upper()
            commission = commission.get("amount")
        if not re.fullmatch(r"[A-Z]{3}", currency):
            errors.append({"transaction": tid, "code": "CURRENCY_MISSING"})
            continue
        status = str(item.get("commissionStatus") or item.get("status") or "").lower()
        if status not in ("pending", "approved", "declined", "deleted"):
            errors.append({"transaction": tid, "code": "STATUS_UNKNOWN"})
            continue
        try:
            amount = _money(commission)
        except ValueError:
            errors.append({"transaction": tid, "code": "INVALID_AMOUNT"})
            continue
        totals[currency][status] += amount
        count += 1
    seen_payouts: set[str] = set()
    for item in results.get("payouts") or []:
        if not isinstance(item, dict) or not item.get("payment_id"):
            continue
        payment_id = str(item["payment_id"])
        if payment_id in seen_payouts:
            continue
        seen_payouts.add(payment_id)
        currency = str(item.get("currency") or "").upper()
        if re.fullmatch(r"[A-Z]{3}", currency):
            try:
                totals[currency]["paid"] += _money(item.get("amount"))
            except ValueError:
                errors.append({"payment_id": payment_id, "code": "INVALID_AMOUNT"})
    for item in results.get("costs") or []:
        if not isinstance(item, dict):
            continue
        currency = str(item.get("currency") or "").upper()
        if re.fullmatch(r"[A-Z]{3}", currency):
            try:
                totals[currency]["cost"] += _money(item.get("amount"))
            except ValueError:
                errors.append({"cost_id": item.get("id"), "code": "INVALID_AMOUNT"})
    report: dict[str, dict[str, str]] = {}
    for currency, amounts in sorted(totals.items()):
        report[currency] = {k: str(v) for k, v in amounts.items()}
        report[currency]["net_cash"] = str(amounts["paid"] - amounts["cost"])
        report[currency]["approved_less_cost"] = str(amounts["approved"] - amounts["cost"])
    return {"currencies": report, "transactions_counted": count, "errors": errors,
            "note": "Awin approved transactions are not cash payouts; payout entries require real payment evidence."}
