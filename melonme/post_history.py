"""Minimal, durable, per-discussion posting memory.

Keeps no page content, product details, user identity or full URLs.
One table: target hash, state, last posted time and external receipt.
It prevents repeated writes to one discussion across local worker processes;
distributed publishers must also honour MelonMe's idempotency key.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import sqlite3
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import uuid


# These parameters identify page position or analytics, not the discussion.
_IGNORED_QUERIES = {"page", "start", "sort", "order", "fbclid", "gclid"}
# Discourse /t/slug/thread-id/page-number
_DISCOURSE_ROOT = "/t/"


def target_key(channel: str, url: str) -> str:
    """Stable identity of one discussion, independent of discovery source ID."""
    parts = urlsplit(url)
    if parts.scheme not in ("https", "http") or not parts.hostname:
        raise ValueError("THREAD_URL_REQUIRED")
    if parts.username or parts.password:
        raise ValueError("INVALID_THREAD_URL")
    host = (parts.hostname or "").lower()
    if parts.port and parts.port not in (80, 443):
        host += ":" + str(parts.port)
    path = parts.path.rstrip("/") or "/"
    segments = path.strip("/").split("/")
    if (path.startswith(_DISCOURSE_ROOT) and len(segments) >= 4
            and segments[2].isdigit() and segments[3].isdigit()):
        path = "/" + "/".join(segments[:3])
    query = urlencode(sorted(
        (key, val) for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if key.casefold() not in _IGNORED_QUERIES
        and not key.casefold().startswith("utm_")
    ))
    canonical = urlunsplit(("", host, path, query, ""))
    return hashlib.sha256((str(channel).strip().casefold() + "\n" + canonical).encode()).hexdigest()


def _timestamp(now: float) -> str:
    return datetime.fromtimestamp(now, timezone.utc).isoformat(timespec="seconds")


class PostHistory:
    """Local single-table store; only one active claim per discussion."""

    def __init__(self, path: str | Path, *, cooldown_days: int = 180,
                 lease_seconds: int = 300, clock=time.time):
        if not 1 <= int(cooldown_days) <= 3650:
            raise ValueError("INVALID_COOLDOWN_DAYS")
        self.path = str(path)
        self.cooldown_seconds = int(cooldown_days) * 86400
        self.lease_seconds = int(lease_seconds)
        self.clock = clock
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    target_key TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    posted_at REAL,
                    external_id TEXT,
                    attempted_at REAL NOT NULL,
                    token TEXT
                )
            """)

    @classmethod
    def from_env(cls) -> PostHistory:
        path = os.environ.get("MELONME_POST_HISTORY_DB") or (
            Path.home() / ".melonme" / "posting.sqlite3")
        raw = os.environ.get("MELONME_REPOST_DAYS", "180")
        try:
            return cls(path, cooldown_days=int(raw))
        except ValueError as exc:
            raise ValueError("INVALID_POST_HISTORY_CONFIG") from exc

    def _db(self):
        return sqlite3.connect(self.path, timeout=10, isolation_level=None)

    def _status(self, row, now: float) -> dict | None:
        if not row:
            return None
        state, posted, external_id, attempted = row
        if state == "POSTED" and posted is not None and now - posted < self.cooldown_seconds:
            return {"status": "ALREADY_POSTED", "last_posted_at": _timestamp(posted),
                    "external_id": external_id}
        if state == "UNCERTAIN":
            return {"status": "PUBLISH_UNCERTAIN", "last_attempt_at": _timestamp(attempted)}
        if state == "PENDING":
            if now - attempted < self.lease_seconds:
                return {"status": "POST_IN_PROGRESS", "last_attempt_at": _timestamp(attempted)}
            # The worker may have published just before crashing. Don't blindly
            # start another post without checking the existing target/receipt.
            return {"status": "PUBLISH_UNCERTAIN", "last_attempt_at": _timestamp(attempted)}
        return None

    def check(self, channel: str, url: str) -> dict | None:
        key = target_key(channel, url)
        with self._db() as db:
            row = db.execute(
                "SELECT state,posted_at,external_id,attempted_at FROM posts WHERE target_key=?",
                (key,),
            ).fetchone()
        return self._status(row, self.clock())

    def claim(self, channel: str, url: str) -> tuple[str | None, dict | None]:
        key = target_key(channel, url)
        token = uuid.uuid4().hex
        now = self.clock()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT state,posted_at,external_id,attempted_at FROM posts WHERE target_key=?",
                (key,),
            ).fetchone()
            existing = self._status(row, now)
            if existing:
                db.rollback()
                return None, existing
            db.execute("""
                INSERT INTO posts(target_key,state,posted_at,external_id,attempted_at,token)
                VALUES (?, 'PENDING', NULL, NULL, ?, ?)
                ON CONFLICT(target_key) DO UPDATE SET
                    state='PENDING',posted_at=NULL,external_id=NULL,
                    attempted_at=excluded.attempted_at,token=excluded.token
            """, (key, now, token))
            db.commit()
        return token, None

    def complete(self, channel: str, url: str, token: str, external_id: str) -> bool:
        if not external_id:
            return False
        with self._db() as db:
            result = db.execute("""
                UPDATE posts SET state='POSTED',posted_at=?,external_id=?,token=NULL
                WHERE target_key=? AND state='PENDING' AND token=?
            """, (self.clock(), str(external_id)[:256],
                  target_key(channel, url), token))
            return result.rowcount == 1

    def uncertain(self, channel: str, url: str, token: str) -> None:
        with self._db() as db:
            db.execute("""
                UPDATE posts SET state='UNCERTAIN',token=NULL
                WHERE target_key=? AND state='PENDING' AND token=?
            """, (target_key(channel, url), token))
