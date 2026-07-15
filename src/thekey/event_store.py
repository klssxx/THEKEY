"""Append-only SQLite event store + minimal state machine (task 5).

This is the AUDIT event store of THEKEY Core: every governed action emits an
integrity-checked event appended to a SQLite database. Events are hash-chained
(each record commits the SHA-256 of the previous event body) so the log is
tamper-evident. The existing ``StateMachine`` remains the authoritative run-state
machine; this module is the durable, queryable audit trail that backs it.

No model output may write here directly -- only the deterministic orchestrator
appends events. Reads are unrestricted (audit).

Schema (SQLite, WAL):

    events(
        seq            INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type     TEXT,    -- transition|approval|evidence|gate|review
        run_id         TEXT,
        actor          TEXT,
        prev_hash      TEXT,    -- SHA-256 of previous event body
        body_hash      TEXT,    -- SHA-256 of this event body
        payload        TEXT,    -- JSON
        created_at     TEXT
    )
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EventStore:
    """Append-only, hash-chained event store backed by SQLite."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), isolation_level=None)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                seq         INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type  TEXT NOT NULL,
                run_id      TEXT NOT NULL,
                actor       TEXT NOT NULL,
                prev_hash   TEXT NOT NULL,
                body_hash   TEXT NOT NULL,
                payload     TEXT NOT NULL,
                created_at  TEXT NOT NULL
            );
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_run ON events(run_id);"
        )

    def append(
        self,
        event_type: str,
        run_id: str,
        actor: str,
        payload: dict,
    ) -> dict:
        prev_hash = self._last_body_hash()
        body = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        body_hash = _sha256_text(body)
        created_at = _utcnow()
        cur = self._conn.execute(
            """
            INSERT INTO events (event_type, run_id, actor, prev_hash, body_hash, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (event_type, run_id, actor, prev_hash, body_hash, body, created_at),
        )
        return {
            "seq": cur.lastrowid,
            "event_type": event_type,
            "run_id": run_id,
            "actor": actor,
            "prev_hash": prev_hash,
            "body_hash": body_hash,
            "payload": payload,
            "created_at": created_at,
        }

    def _last_body_hash(self) -> str:
        row = self._conn.execute(
            "SELECT body_hash FROM events ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "0" * 64

    def events(self, run_id: str | None = None) -> list[dict]:
        if run_id is None:
            rows = self._conn.execute(
                "SELECT seq, event_type, run_id, actor, prev_hash, body_hash, payload, created_at "
                "FROM events ORDER BY seq ASC"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT seq, event_type, run_id, actor, prev_hash, body_hash, payload, created_at "
                "FROM events WHERE run_id = ? ORDER BY seq ASC",
                (run_id,),
            ).fetchall()
        out = []
        for seq, et, rid, actor, prev, bhash, payload, ts in rows:
            out.append(
                {
                    "seq": seq,
                    "event_type": et,
                    "run_id": rid,
                    "actor": actor,
                    "prev_hash": prev,
                    "body_hash": bhash,
                    "payload": json.loads(payload),
                    "created_at": ts,
                }
            )
        return out

    def verify_chain(self) -> dict:
        """Re-walk the chain; confirm each event's prev_hash matches the body
        hash of the preceding event. Returns an integrity report."""
        rows = self._conn.execute(
            "SELECT seq, prev_hash, body_hash, payload FROM events ORDER BY seq ASC"
        ).fetchall()
        prev_expected = "0" * 64
        breaks = []
        for seq, prev, bhash, payload in rows:
            if prev != prev_expected:
                breaks.append({"seq": seq, "expected_prev": prev_expected, "found_prev": prev})
            if _sha256_text(payload) != bhash:
                breaks.append({"seq": seq, "expected_body_hash": _sha256_text(payload), "found_body_hash": bhash})
            prev_expected = bhash
        return {
            "event_count": len(rows),
            "integrity_status": "VALID" if not breaks else "BROKEN",
            "breaks": breaks,
        }

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
