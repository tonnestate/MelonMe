"""Posting memory tests: only thread hash, time and external receipt are persisted."""
import sqlite3
import tempfile
from pathlib import Path
import unittest

from melonme import core
from melonme.post_history import PostHistory, target_key


Q = {
    "id": "source-q-1",
    "channel": "forum",
    "source_url": "https://forum.example/t/sport-headphones/42/2?utm_source=search",
    "text": "Sport Kopfhörer",
    "market": "AT",
    "language": "de",
    "offers": [{"title": "Sport Kopfhörer", "market": "AT",
                "url": "https://shop.example/sport"}],
    "publish": True,
}


class PostHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.now = [1_800_000_000.0]
        self.file = Path(self.temp.name) / "post-history.sqlite3"
        self.history = PostHistory(self.file, cooldown_days=180, clock=lambda: self.now[0])

    def test_same_thread_different_discovery_urls_share_key(self):
        a = target_key("forum", "https://forum.example/t/sport-headphones/42/2?utm_source=mail")
        b = target_key("FORUM", "https://FORUM.example/t/sport-headphones/42/8?page=3")
        self.assertEqual(a, b)

    def test_thread_identity_keeps_real_query_ids(self):
        a = target_key("forum", "https://forum.example/topic.php?t=42")
        b = target_key("forum", "https://forum.example/topic.php?t=43")
        self.assertNotEqual(a, b)

    def test_persistent_post_time_and_receipt(self):
        token, existing = self.history.claim(Q["channel"], Q["source_url"])
        self.assertIsNone(existing)
        self.assertTrue(self.history.complete(Q["channel"], Q["source_url"], token, "external-777"))
        # Open a fresh instance to establish real durability across restarts.
        reopened = PostHistory(self.file, clock=lambda: self.now[0])
        result = reopened.check(Q["channel"], Q["source_url"])
        self.assertEqual(result["status"], "ALREADY_POSTED")
        self.assertEqual(result["external_id"], "external-777")
        self.assertIn("T", result["last_posted_at"])

    def test_repeated_claim_does_not_double_publish(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.complete(Q["channel"], Q["source_url"], token, "post-1")
        second, previous = self.history.claim("forum",
            "https://forum.example/t/sport-headphones/42/99")
        self.assertIsNone(second)
        self.assertEqual(previous["status"], "ALREADY_POSTED")

    def test_concurrent_claim_same_thread_only_one_wins(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        other = PostHistory(self.file, clock=lambda: self.now[0])
        second, previous = other.claim(Q["channel"], Q["source_url"])
        self.assertIsNotNone(token)
        self.assertIsNone(second)
        self.assertEqual(previous["status"], "POST_IN_PROGRESS")

    def test_crashed_pending_request_needs_local_reconciliation(self):
        self.history.claim(Q["channel"], Q["source_url"])
        self.now[0] += 600
        self.assertEqual(self.history.check(Q["channel"], Q["source_url"])["status"],
                         "PUBLISH_UNCERTAIN")

    def test_ambiguous_result_does_not_pretend_posted(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.uncertain(Q["channel"], Q["source_url"], token)
        r = self.history.check(Q["channel"], Q["source_url"])
        self.assertEqual(r["status"], "PUBLISH_UNCERTAIN")
        self.assertNotIn("last_posted_at", r)

    def test_other_thread_not_affected(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.uncertain(Q["channel"], Q["source_url"], token)
        other_url = "https://forum.example/t/coffee/77"
        self.assertIsNone(self.history.check("forum", other_url))
        other, previous = self.history.claim("forum", other_url)
        self.assertIsNotNone(other)
        self.assertIsNone(previous)

    def test_cooldown_expires_without_erasing_history_content(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.complete(Q["channel"], Q["source_url"], token, "old-post")
        self.now[0] += 181 * 86400
        self.assertIsNone(self.history.check(Q["channel"], Q["source_url"]))
        again, previous = self.history.claim(Q["channel"], Q["source_url"])
        self.assertIsNotNone(again)
        self.assertIsNone(previous)

    def test_only_minimal_columns_no_full_url_or_message(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.complete(Q["channel"], Q["source_url"], token, "external-1")
        db = sqlite3.connect(self.file)
        try:
            columns = {r[1] for r in db.execute("PRAGMA table_info(posts)").fetchall()}
            self.assertEqual(columns, {
                "target_key", "state", "posted_at", "external_id", "attempted_at", "token"})
            stored = db.execute("SELECT * FROM posts").fetchall()
        finally:
            db.close()
        self.assertEqual(len(stored), 1)
        self.assertNotIn("forum.example", repr(stored))
        self.assertNotIn("Sport Kopfhörer", repr(stored))

    def test_execute_duplicate_check_precedes_partner_calls(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.complete(Q["channel"], Q["source_url"], token, "post-9")
        class ShouldNotCall:
            def link(self, *args):
                raise AssertionError("Link builder must not run")
        opportunity = {
            **Q, "id": "different-discovery-id",
            "offers": [{**Q["offers"][0], "provider": "awin", "advertiser_id": 7}],
        }
        def should_not_publish(_):
            raise AssertionError("Publisher must not run")
        result = core.execute(opportunity, awin=ShouldNotCall(),
                              publisher=should_not_publish, post_history=self.history)
        self.assertEqual(result["status"], "ALREADY_POSTED")
        self.assertEqual(result["external_id"], "post-9")

    def test_execute_records_success_and_later_skips(self):
        sent = []
        def send(payload):
            sent.append(payload)
            return {"external_id": "post-123"}
        first = core.execute(Q, publisher=send, post_history=self.history)
        self.assertEqual(first["status"], "PUBLISHED")
        self.assertTrue(first["post_history_recorded"])
        different_source_id = {**Q, "id": "other-search-result"}
        second = core.execute(different_source_id, publisher=send, post_history=self.history)
        self.assertEqual(second["status"], "ALREADY_POSTED")
        self.assertEqual(len(sent), 1)

    def test_ambiguous_post_fails_only_this_thread(self):
        def failing(_):
            raise TimeoutError("could have reached the forum")
        first = core.execute(Q, publisher=failing, post_history=self.history)
        self.assertEqual(first["status"], "DRAFT_ONLY")
        second = core.execute(Q, publisher=failing, post_history=self.history)
        self.assertEqual(second["status"], "PUBLISH_UNCERTAIN")
        self.assertEqual(
            core.execute({**Q, "source_url": "https://forum.example/t/other-topic/99"},
                         publisher=lambda _: {"external_id": "posted-new"},
                         post_history=self.history)["status"], "PUBLISHED")

    def test_find_returns_previous_post_time_without_searching_products(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.complete(Q["channel"], Q["source_url"], token, "post-99")
        def no_inventory(_):
            raise AssertionError("No product lookup for answered thread")
        result = core.find({"questions": [Q], "offers": []},
                           inventory_lookup=no_inventory, post_history=self.history)
        self.assertEqual(result["opportunities"], [])
        self.assertEqual(result["posted"][0]["status"], "ALREADY_POSTED")
        self.assertEqual(result["posted"][0]["external_id"], "post-99")
        self.assertIn("last_posted_at", result["posted"][0])

    def test_answered_thread_skips_but_other_questions_still_run(self):
        token, _ = self.history.claim(Q["channel"], Q["source_url"])
        self.history.complete(Q["channel"], Q["source_url"], token, "post-10")
        fresh = {**Q, "id": "fresh", "source_url": "https://forum.example/t/other/88"}
        called = []
        def inventory(payload):
            called.extend(payload["questions"])
            return {"offers": Q["offers"]}
        result = core.find({"questions": [Q, fresh], "offers": []},
                           inventory_lookup=inventory, post_history=self.history)
        self.assertEqual(result["posted"][0]["status"], "ALREADY_POSTED")
        self.assertEqual([item["id"] for item in result["opportunities"]], ["fresh"])
        self.assertEqual([item["id"] for item in called], ["fresh"])

    def test_publication_idempotency_follows_thread_not_discovery_id(self):
        first = core.execute({**Q, "publish": False})
        second = core.execute({
            **Q, "id": "other-discovery-id", "publish": False,
            "source_url": "https://forum.example/t/sport-headphones/42/8?page=10"})
        self.assertEqual(first["publication_key"], second["publication_key"])


if __name__ == "__main__":
    unittest.main()
