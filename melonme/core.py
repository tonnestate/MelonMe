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
from urllib.request import Request, urlopen


class PartnerError(Exception):
    """A local partner failure: never a global opportunity-search failure."""


def _https_url(value: str) -> bool:
    try:
        p = urlparse(value)
        return p.scheme == "https" and bool(p.hostname) and not p.username and not p.password
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
    try:
        with urlopen(req, timeout=8) as reply:
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
        if not _https_url(destination):
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
    return {w for w in re.findall(r"[^\W_]+", text.casefold()) if len(w) > 3 and w not in _STOP}


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
    if not title or not _https_url(str(offer.get("url") or "")):
        return 0.0
    terms = _words(str(question.get("query") or question.get("text") or ""))
    keywords = _words(str(offer.get("keywords") or title))
    common = len(terms & keywords)
    if common == 0:
        return 0.0
    return round(common / max(len(terms), 1), 4)


def find(context: dict, awin: Awin | None = None) -> dict:
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
            feed_query = " ".join(str(q.get("query") or q.get("text") or "")
                                  for q in questions[:100] if isinstance(q, dict)
                                  and _market(q.get("market") or context.get("market")) == feed_market)
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
        for offer in offers[:2000]:
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
                errors.append({"provider": "awin", "market": market, "code": "PROBED",
                               "joined_programmes": len(programmes)})
            except PartnerError as exc:
                errors.append({"provider": "awin", "market": market, "code": str(exc)})
    results.sort(key=lambda r: (r["decision"] != "READY", -len(r["offers"])))
    return {"opportunities": results[:limit], "errors": errors,
            "inventory_checks": inventory_checks, "checked": len(questions[:500])}


def _draft(opportunity: dict, offer: dict, link: str) -> str:
    prefix = "Werbehinweis: Affiliate-Link.\n" if link != offer.get("url") else ""
    price = ""
    if offer.get("price") is not None and offer.get("currency"):
        price = " — " + str(offer["price"]) + " " + str(offer["currency"])
    facts = offer.get("verified_facts") or []
    detail = "\n" + "\n".join("- " + str(f) for f in facts[:5]) if isinstance(facts, list) else ""
    return prefix + str(offer["title"]) + price + detail + "\n" + link


def execute(opportunity: dict, awin: Awin | None = None,
            publisher: Any | None = None) -> dict:
    """Build a truthful draft. Live publishing requires a host-owned publisher adapter.

    Publisher adapter callable(payload) must return {"external_id": ..., "url": ...}.
    """
    oid = str(opportunity.get("id") or "")
    offers = opportunity.get("offers") or []
    if not isinstance(offers, list) or not offers:
        return {"status": "NO_ACTION", "id": oid, "reason": "NO_MATCH"}
    offer = offers[0]  # Relevance was computed without commission preference.
    if not isinstance(offer, dict) or not _https_url(str(offer.get("url") or "")):
        return {"status": "NO_ACTION", "id": oid, "reason": "INVALID_OFFER"}
    market = _market(opportunity.get("market"))
    if market != _market(offer.get("market")):
        return {"status": "NO_ACTION", "id": oid, "reason": "MARKET_MISMATCH"}
    warnings: list[str] = []
    link = str(offer["url"])
    tracked = False
    existing = offer.get("affiliate_url")
    if isinstance(existing, str) and _https_url(existing):
        link, tracked = existing, True
    elif offer.get("provider", "").lower() == "awin" and offer.get("advertiser_id"):
        client = awin if awin is not None else Awin.from_env()
        if client:
            try:
                joined = client.programmes(market)
                match = next((p for p in joined
                              if str(p.get("id")) == str(offer["advertiser_id"])
                              and p.get("status", "active").lower() == "active"
                              and p.get("linkStatus", "online").lower() == "online"), None)
                if match is None:
                    warnings.append("AWIN_PROGRAMME_NOT_ACTIVE_FOR_MARKET")
                else:
                    clickref = hashlib.sha256(oid.encode("utf-8")).hexdigest()[:24]
                    link = client.link(int(offer["advertiser_id"]), link, clickref)
                    tracked = True
            except (PartnerError, TypeError, ValueError) as err:
                warnings.append("AWIN_" + str(err))
        else:
            warnings.append("AWIN_NOT_CONFIGURED")
    answer = str(opportunity.get("answer_text") or _draft(opportunity, offer, link))
    if tracked and opportunity.get("answer_text") and link not in answer:
        # The host's answer must actually contain the tracked URL.
        warnings.append("TRACKING_LINK_NOT_IN_ANSWER")
        tracked = False
    fingerprint = hashlib.sha256((oid + "\n" + answer).encode("utf-8")).hexdigest()
    base = {"id": oid, "draft": answer, "tracked": tracked,
            "offer_url": link, "fingerprint": fingerprint, "warnings": warnings}
    if not opportunity.get("publish"):
        return {"status": "DRAFT_ONLY", **base}
    if publisher is None:
        return {"status": "DRAFT_ONLY", **base, "reason": "PUBLISH_ADAPTER_NOT_CONFIGURED"}
    if not opportunity.get("channel") or not opportunity.get("source_url"):
        return {"status": "DRAFT_ONLY", **base, "reason": "PUBLISH_TARGET_MISSING"}
    payload = {"id": oid, "channel": opportunity["channel"],
               "source_url": opportunity["source_url"],
               "text": answer, "idempotency_key": fingerprint}
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
    seen: set[tuple[str, str]] = set()
    count = 0
    for item in transactions:
        if not isinstance(item, dict):
            continue
        tid = str(item.get("id") or item.get("transactionId") or "")
        provider = str(item.get("provider") or "awin")
        if not tid or (provider, tid) in seen:
            continue
        seen.add((provider, tid))
        currency = str(item.get("currency") or item.get("commissionCurrency") or "").upper()
        if not re.fullmatch(r"[A-Z]{3}", currency):
            errors.append({"transaction": tid, "code": "CURRENCY_MISSING"})
            continue
        commission = item.get("commissionAmount", item.get("commission", 0))
        if isinstance(commission, dict):
            currency = str(commission.get("currency") or currency).upper()
            commission = commission.get("amount", 0)
        # Awin's actual transaction JSON uses commissionStatus, not status.
        # Support generic host records too; do not infer payout from approval.
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
