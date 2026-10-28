"""Offline contract tests: no partner credentials, network access or paid models."""
import unittest
import io
import json
from melonme import awin_inventory
from unittest.mock import patch

from melonme import core


Q = {"id": "q-1", "text": "Suche Sport Kopfhörer", "market": "AT",
     "language": "de", "channel": "forum", "source_url": "https://forum.example/q/1"}
O = {"title": "Sport Kopfhörer", "url": "https://shop.example/sport",
     "provider": "host", "market": "AT", "price": "49.99",
     "currency": "EUR", "verified_facts": ["Bluetooth"]}
BAD_O = {**O, "market": "DE"}


class FakeAwin:
    def __init__(self, fail=False):
        self.fail = fail
        self.requests = []

    def programmes(self, market):
        self.requests.append(("programmes", market))
        if self.fail:
            raise core.PartnerError("HTTP_403")
        return [{"id": 7, "status": "active", "linkStatus": "online"}]

    def link(self, advertiser_id, destination, clickref):
        self.requests.append(("link", advertiser_id, destination, clickref))
        if self.fail:
            raise core.PartnerError("HTTP_429")
        return "https://www.awin1.com/tracked"

    def transactions(self, start, end):
        if self.fail:
            raise core.PartnerError("HTTP_401")
        return [{"id": "awin-1", "currency": "EUR", "status": "approved",
                 "commissionAmount": {"amount": "5.25", "currency": "EUR"}}]


class FindTests(unittest.TestCase):
    def test_relevant_market_offer_and_language_independent(self):
        result = core.find({"questions": [Q], "offers": [BAD_O, O]})
        self.assertEqual(result["opportunities"][0]["decision"], "READY")
        self.assertEqual(len(result["opportunities"][0]["offers"]), 1)
        self.assertEqual(result["opportunities"][0]["language"], "de")
        self.assertEqual(result["opportunities"][0]["market"], "AT")

    def test_one_unknown_market_does_not_block_another(self):
        r = core.find({"questions": [{**Q, "id": "q-2", "market": None}, Q], "offers": [O]})
        self.assertEqual(r["checked"], 2)
        self.assertEqual(len(r["opportunities"]), 1)
        self.assertEqual(r["errors"][0]["code"], "MARKET_UNKNOWN")

    def test_no_match_is_not_global_failure(self):
        r = core.find({"questions": [Q], "offers": [BAD_O]})
        self.assertEqual(r["opportunities"][0]["decision"], "NO_MATCH")

    def test_local_awin_failure_preserves_offers(self):
        r = core.find({"questions": [Q], "offers": [O], "probe_awin": True},
                      awin=FakeAwin(fail=True))
        self.assertEqual(r["opportunities"][0]["decision"], "READY")
        self.assertIn("HTTP_403", [x["code"] for x in r["errors"]])

    def test_live_programme_count_only_reports_observed_value(self):
        r = core.find({"questions": [Q], "offers": [O], "probe_awin": True},
                      awin=FakeAwin())
        self.assertEqual(r["provider_checks"][0]["joined_programmes"], 1)

    def test_invalid_input_is_local_result(self):
        self.assertEqual(core.find({"questions": "not-list"})["errors"][0]["code"], "INVALID_INPUT")


class ExecuteTests(unittest.TestCase):
    def test_draft_without_publisher(self):
        result = core.execute({**Q, "offers": [{**O}]})
        self.assertEqual(result["status"], "DRAFT_ONLY")
        self.assertNotIn("external_id", result)
        self.assertIn("Sport Kopfhörer", result["draft"])
        self.assertFalse(result["tracked"])

    def test_missing_offers_no_action(self):
        self.assertEqual(core.execute({**Q, "offers": []})["status"], "NO_ACTION")

    def test_market_mismatch_rejected_locally(self):
        self.assertEqual(core.execute({**Q, "offers": [BAD_O]})["reason"], "MARKET_MISMATCH")

    def test_published_only_with_external_receipt(self):
        sent = []
        def publisher(payload):
            sent.append(payload)
            return {"external_id": "real-post-123", "url": "https://forum.example/p/123"}
        o = {**Q, "offers": [O], "publish": True}
        r = core.execute(o, publisher=publisher)
        self.assertEqual(r["status"], "PUBLISHED")
        self.assertEqual(r["external_id"], "real-post-123")
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["idempotency_key"], r["fingerprint"])

    def test_publishing_without_receipt_stays_draft(self):
        r = core.execute({**Q, "offers": [O], "publish": True},
                         publisher=lambda _: {"ok": True})
        self.assertEqual(r["status"], "DRAFT_ONLY")
        self.assertEqual(r["reason"], "EXTERNAL_RECEIPT_MISSING")

    def test_one_failed_publish_does_not_throw_or_fake_success(self):
        def failure(_):
            raise RuntimeError("external error")
        r = core.execute({**Q, "offers": [O], "publish": True}, publisher=failure)
        self.assertEqual(r["status"], "DRAFT_ONLY")
        self.assertEqual(r["reason"], "PUBLISH_FAILED")

    def test_partial_awin_access_generates_actual_link(self):
        offer = {**O, "provider": "awin", "advertiser_id": 7}
        fake = FakeAwin()
        r = core.execute({**Q, "offers": [offer]}, awin=fake)
        self.assertTrue(r["tracked"])
        self.assertIn("awin1.com", r["draft"])
        self.assertEqual(fake.requests[0][0], "link")

    def test_failed_awin_call_falls_back_to_factual_draft(self):
        offer = {**O, "provider": "awin", "advertiser_id": 7}
        r = core.execute({**Q, "offers": [offer]}, awin=FakeAwin(fail=True))
        self.assertEqual(r["status"], "DRAFT_ONLY")
        self.assertFalse(r["tracked"])
        self.assertIn("AWIN_HTTP_429", r["warnings"])

    def test_external_author_text_without_link_not_marked_tracked(self):
        offer = {**O, "affiliate_url": "https://aw.example/tracked"}
        r = core.execute({**Q, "offers": [offer], "answer_text": "My tested answer"})
        self.assertFalse(r["tracked"])


class LearnTests(unittest.TestCase):
    def test_approved_not_cash_and_deduplicate(self):
        trans = {"id": "tx-1", "provider": "awin", "currency": "EUR",
                 "status": "approved", "commission": "12.50"}
        r = core.learn({"transactions": [trans, trans],
                        "payouts": [{"payment_id": "pay-1", "currency": "EUR", "amount": "10"}],
                        "costs": [{"currency": "EUR", "amount": "3.20"}]})
        self.assertEqual(r["transactions_counted"], 1)
        self.assertEqual(r["currencies"]["EUR"]["approved"], "12.50")
        self.assertEqual(r["currencies"]["EUR"]["net_cash"], "6.80")

    def test_approved_does_not_imply_paid(self):
        r = core.learn({"transactions": [{"id": 1, "status": "approved",
                                          "currency": "EUR", "commission": "10"}]})
        self.assertEqual(r["currencies"]["EUR"]["paid"], "0")
        self.assertEqual(r["currencies"]["EUR"]["net_cash"], "0")

    def test_multiple_currencies_not_mixed(self):
        r = core.learn({"costs": [{"currency": "EUR", "amount": 4},
                                  {"currency": "USD", "amount": 2}]})
        self.assertEqual(r["currencies"]["EUR"]["net_cash"], "-4")
        self.assertEqual(r["currencies"]["USD"]["net_cash"], "-2")

    def test_live_awin_failure_does_not_discard_local_data(self):
        r = core.learn({"sync_awin": True, "start": "2026-10-01T00:00:00",
                        "end": "2026-10-02T00:00:00",
                        "costs": [{"currency": "EUR", "amount": "1"}]},
                       awin=FakeAwin(fail=True))
        self.assertEqual(r["currencies"]["EUR"]["net_cash"], "-1")
        self.assertEqual(r["errors"][0]["code"], "HTTP_401")

    def test_awin_transaction_observed_without_payout(self):
        r = core.learn({"sync_awin": True, "start": "2026-10-01T00:00:00",
                        "end": "2026-10-02T00:00:00"}, awin=FakeAwin())
        self.assertEqual(r["currencies"]["EUR"]["approved"], "5.25")
        self.assertEqual(r["currencies"]["EUR"]["paid"], "0")


class AwinClientTests(unittest.TestCase):
    def test_programmes_request_uses_bearer_and_market(self):
        awin = core.Awin("1234", "secret")
        with patch("melonme.core._json_request", return_value=[{"id": 7}]) as request:
            programs = awin.programmes("DE")
            self.assertEqual(programs[0]["id"], 7)
            self.assertIn("countryCode=DE", request.call_args.args[0])
            self.assertEqual(request.call_args.args[1], "secret")

    def test_link_requires_secure_destination(self):
        with self.assertRaises(core.PartnerError):
            core.Awin("1234", "secret").link(7, "http://shop.example", "click")

    def test_transaction_window_bounded(self):
        with self.assertRaises(core.PartnerError):
            core.Awin("1234", "secret").transactions("2026-01-01T00:00:00",
                                                     "2026-02-15T00:00:00")


    def test_badly_formatted_money_is_not_silently_zeroed(self):
        r = core.learn({"transactions": [{"id": "bad-1", "status": "approved",
                                           "currency": "EUR", "commission": "not-a-number"}]})
        self.assertEqual(r["transactions_counted"], 0)
        self.assertEqual(r["errors"][0]["code"], "INVALID_AMOUNT")

    def test_payout_receipt_is_only_counted_once(self):
        payout = {"payment_id": "bank-42", "currency": "EUR", "amount": "8.50"}
        r = core.learn({"payouts": [payout, payout]})
        self.assertEqual(r["currencies"]["EUR"]["paid"], "8.50")

    def test_invalid_limit_uses_default_without_aborting(self):
        r = core.find({"questions": [Q], "offers": [O], "limit": "broken"})
        self.assertEqual(r["opportunities"][0]["decision"], "READY")
        self.assertEqual(r["errors"][0]["code"], "INVALID_LIMIT_USED_DEFAULT")


class RealAwinContractTests(unittest.TestCase):
    def test_actual_awin_commission_status_is_used(self):
        r = core.learn({"transactions": [
            {"id": 1001, "advertiserId": 7, "commissionStatus": "approved",
             "commissionAmount": {"amount": "12.33", "currency": "EUR"}}
        ]})
        self.assertEqual(r["transactions_counted"], 1)
        self.assertEqual(r["currencies"]["EUR"]["approved"], "12.33")
        self.assertEqual(r["currencies"]["EUR"]["paid"], "0")

    def test_amended_transaction_replaces_older_pending_snapshot(self):
        r = core.learn({"transactions": [
            {"id": 1001, "commissionStatus": "pending",
             "commissionAmount": {"amount": "10", "currency": "EUR"}},
            {"id": 1001, "commissionStatus": "approved",
             "commissionAmount": {"amount": "8", "currency": "EUR"}}
        ]})
        self.assertEqual(r["transactions_counted"], 1)
        self.assertEqual(r["currencies"]["EUR"]["approved"], "8")
        self.assertEqual(r["currencies"]["EUR"]["pending"], "0")

    def test_changed_transaction_updates_amount_not_twice(self):
        r = core.learn({"transactions": [
            {"id": 1001, "commissionStatus": "approved", "validationDate": "2026-10-01",
             "commissionAmount": {"amount": "5", "currency": "EUR"}},
            {"id": 1001, "commissionStatus": "approved", "validationDate": "2026-10-09",
             "commissionAmount": {"amount": "4", "currency": "EUR"}}
        ]})
        self.assertEqual(r["transactions_counted"], 1)
        self.assertEqual(r["currencies"]["EUR"]["approved"], "4")

    def test_host_supplied_affiliate_url_needs_verified_attestation(self):
        o = {**O, "affiliate_url": "https://affiliate.example/id"}
        r = core.execute({**Q, "offers": [o]})
        self.assertFalse(r["tracked"])
        self.assertEqual(r["offer_url"], O["url"])
        self.assertIn("AFFILIATE_LINK_UNVERIFIED", r["warnings"])

    def test_verified_affiliate_url_and_language_disclosure(self):
        o = {**O, "affiliate_url": "https://affiliate.example/id",
             "affiliate_verified": True}
        r = core.execute({**Q, "language": "en", "offers": [o]})
        self.assertTrue(r["tracked"])
        self.assertIn("Disclosure: affiliate link.", r["draft"])

    def test_awin_success_is_possible_without_programme_list(self):
        class LinkOnly:
            def link(self, advertiser_id, url, clickref):
                return "https://www.awin1.com/cread.php?id=7"
            def programmes(self, market):
                raise core.PartnerError("HTTP_403")
        o = {**O, "advertiser_id": 7, "provider": "awin"}
        r = core.execute({**Q, "offers": [o]}, awin=LinkOnly())
        self.assertTrue(r["tracked"])

    def test_other_offer_can_recover_failed_affiliate(self):
        class Mixed:
            def link(self, advertiser_id, url, clickref):
                if advertiser_id == 1:
                    raise core.PartnerError("HTTP_403")
                return "https://www.awin1.com/tracked-two"
        first = {**O, "provider": "awin", "advertiser_id": 1, "relevance": 0.95}
        second = {**O, "provider": "awin", "advertiser_id": 2, "relevance": 0.94}
        r = core.execute({**Q, "offers": [first, second]}, awin=Mixed())
        self.assertTrue(r["tracked"])
        self.assertEqual(r["alternatives_checked"], 2)
        self.assertIn("AWIN_HTTP_403", r["warnings"])

    def test_bad_score_does_not_crash_execution(self):
        r = core.execute({**Q, "offers": [{**O, "relevance": "not-a-number"}]})
        self.assertEqual(r["status"], "DRAFT_ONLY")


class AwinFeedTests(unittest.TestCase):
    def _response(self):
        product = {"id": "S-12", "title": "Sport Kopfhörer",
                   "link": "https://shop.example/sku-12", "price": "29.90 EUR",
                   "availability": "in_stock", "brand": "Test"}
        return io.BytesIO((json.dumps(product) + "\n").encode())

    def test_actual_enhanced_feed_product_is_found(self):
        with patch("melonme.awin_inventory.urlopen", return_value=self._response()) as http:
            r = awin_inventory.scan_enhanced_feed(
                "1234", "secret", 7, "de_AT", "AT", "Sport Kopfhörer")
        self.assertTrue(r["complete"])
        self.assertEqual(r["offers"][0]["price"], "29.90")
        self.assertEqual(r["offers"][0]["market"], "AT")
        self.assertIn("api.awin.com", http.call_args.args[0].full_url)
        self.assertNotIn("secret", http.call_args.args[0].full_url)

    def test_feed_is_wired_into_find(self):
        with patch("melonme.awin_inventory.urlopen", return_value=self._response()):
            r = core.find({"questions": [Q], "offers": [],
                           "awin_feeds": [{"market": "AT", "locale": "de_AT",
                                           "advertiser_id": 7}]},
                          awin=core.Awin("1234", "secret"))
        self.assertEqual(r["opportunities"][0]["decision"], "READY")
        self.assertEqual(r["opportunities"][0]["offers"][0]["provider"], "awin")
        self.assertEqual(r["inventory_checks"][0]["scanned_rows"], 1)

    def test_partial_feed_is_not_claimed_complete(self):
        with patch("melonme.awin_inventory.urlopen", return_value=self._response()):
            r = awin_inventory.scan_enhanced_feed(
                "1234", "secret", 7, "de_AT", "AT", "No match",
                max_rows=1)
        self.assertTrue(r["partial"])

    def test_trailer_error_never_masquerades_as_a_complete_feed(self):
        data = (json.dumps({"id": "1", "title": "Sport Kopfhörer",
                            "link": "https://shop.example/test"})
                + "\n" + json.dumps({"error": 500, "message": "incomplete"}) + "\n")
        with patch("melonme.awin_inventory.urlopen", return_value=io.BytesIO(data.encode())):
            with self.assertRaisesRegex(ValueError, "AWIN_FEED_ERROR_TRAILER"):
                awin_inventory.scan_enhanced_feed(
                    "1234", "secret", 7, "de_AT", "AT", "Sport Kopfhörer")

    def test_feed_failure_is_local_to_source_not_all_questions(self):
        with patch("melonme.awin_inventory.urlopen",
                   side_effect=TimeoutError("unreachable")):
            r = core.find({"questions": [Q], "offers": [O],
                           "awin_feeds": [{"market": "AT", "locale": "de_AT",
                                           "advertiser_id": 7}]},
                          awin=core.Awin("1234", "secret"))
        self.assertEqual(r["opportunities"][0]["decision"], "READY")
        self.assertEqual(r["errors"][0]["provider"], "awin_feed")

    def test_invalid_locale_rejected_without_network(self):
        with self.assertRaisesRegex(ValueError, "LOCALE_MARKET_MISMATCH"):
            awin_inventory.scan_enhanced_feed(
                "1234", "secret", 7, "de_DE", "AT", "Sport Kopfhörer")


class AwinPromotionTests(unittest.TestCase):
    def test_actual_joined_promotion_is_found(self):
        promotion = {
            "promotionId": 99, "title": "Sport Kopfhörer Rabatt",
            "advertiser": {"id": 7, "name": "Shop", "joined": True},
            "url": "https://shop.example/sport",
            "urlTracking": "https://www.awin1.com/cread.php?id=99",
            "regions": {"list": [{"countryCode": "AT"}]},
            "description": "10% auf Sport Kopfhörer",
        }
        with patch("melonme.core._json_request", return_value={"promotions": [promotion]}) as request:
            r = core.find({"questions": [Q], "awin_promotions": True, "offers": []},
                          awin=core.Awin("1234", "secret"))
        self.assertEqual(r["opportunities"][0]["decision"], "READY")
        self.assertTrue(r["opportunities"][0]["offers"][0]["affiliate_verified"])
        self.assertEqual(r["provider_checks"][0]["offers"], 1)
        self.assertIn("/publisher/1234/promotions", request.call_args.args[0])
        self.assertEqual(request.call_args.args[2]["filters"]["membership"], "joined")

    def test_not_joined_promotion_is_not_assumed_monetizable(self):
        promo = {"promotionId": 1, "title": "Sport Kopfhörer",
                 "advertiser": {"id": 7, "joined": False},
                 "url": "https://shop.example/sport",
                 "urlTracking": "https://www.awin1.com/link",
                 "regions": {"all": True}}
        with patch("melonme.core._json_request", return_value={"promotions": [promo]}):
            r = core.find({"questions": [Q], "awin_promotions": True, "offers": []},
                          awin=core.Awin("1234", "secret"))
        self.assertEqual(r["opportunities"][0]["decision"], "NO_MATCH")
        self.assertEqual(r["provider_checks"][0]["offers"], 0)

    def test_promotion_response_error_does_not_erase_other_offers(self):
        with patch("melonme.core._json_request", return_value={"unexpected": "shape"}):
            r = core.find({"questions": [Q], "awin_promotions": True, "offers": [O]},
                          awin=core.Awin("1234", "secret"))
        self.assertEqual(r["opportunities"][0]["decision"], "READY")
        self.assertEqual(r["errors"][0]["code"], "PROMOTIONS_RESPONSE_UNRECOGNIZED")


if __name__ == "__main__":
    unittest.main()
