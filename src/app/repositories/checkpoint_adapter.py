"""Checkpoint adapter. Postgres resume store with memory fallback.

Postgres is the source of truth when a db session is available.
The in-memory dict stays for unit tests and keyless dev mode.
"""

from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

_MAX_ENTRIES = 500
_KEEP_LAST = 50
_MAX_AGE_DAYS = 30


class CheckpointAdapter:
    """Thread-keyed state store used for resume after restart."""

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    @staticmethod
    def _key(thread_id: UUID | str) -> str:
        return str(thread_id)

    def load_latest(self, thread_id: UUID | str) -> dict | None:
        """Return the latest saved state copy, or None when missing."""
        saved = self._store.get(self._key(thread_id))
        return copy.deepcopy(saved) if saved is not None else None

    def save(self, thread_id: UUID | str, state: dict) -> None:
        """Persist a copy of graph state for resume."""
        if len(self._store) >= _MAX_ENTRIES and self._key(thread_id) not in self._store:
            oldest = next(iter(self._store))
            del self._store[oldest]
        self._store[self._key(thread_id)] = copy.deepcopy(dict(state))

    def prune(self, thread_id: UUID | str, keep_last: int = 50) -> None:
        """Drop saved state for one thread. Stub keeps one slot per thread."""
        _ = keep_last
        self._store.pop(self._key(thread_id), None)

    def clear(self) -> None:
        """Reset all entries. Used by tests."""
        self._store.clear()

    def save_to_db(
        self, db: Session, thread_id: UUID | str, state: dict
    ) -> None:
        """Write one checkpoint row plus prune to policy."""
        from app.models.thread_checkpoints import ThreadCheckpoint

        tid = UUID(str(thread_id))
        trace_raw = state.get("trace_id")
        try:
            trace_id = UUID(str(trace_raw)) if trace_raw else None
        except ValueError:
            trace_id = None
        row = ThreadCheckpoint(
            thread_id=tid,
            trace_id=trace_id,
            intent_category=str(state.get("intent_category"))
            if state.get("intent_category")
            else None,
            is_grounded=bool(state.get("is_grounded"))
            if state.get("is_grounded") is not None
            else None,
            state=dict(state),
        )
        db.add(row)
        db.flush()
        self.prune_db(db, tid)
        # Keep memory in sync so unit paths see the same state.
        self.save(tid, state)

    def load_latest_from_db(
        self, db: Session, thread_id: UUID | str
    ) -> dict | None:
        """Return the newest checkpoint row as a state dict."""
        from app.models.thread_checkpoints import ThreadCheckpoint

        tid = UUID(str(thread_id))
        stmt = (
            select(ThreadCheckpoint)
            .where(ThreadCheckpoint.thread_id == tid)
            .order_by(
                ThreadCheckpoint.created_at.desc(),
                ThreadCheckpoint.id.desc(),
            )
            .limit(1)
        )
        row = db.execute(stmt).scalars().first()
        if row is None:
            return self.load_latest(tid)
        saved = dict(row.state or {})
        saved.setdefault("thread_id", str(tid))
        if row.trace_id:
            saved.setdefault("trace_id", str(row.trace_id))
        self._store[self._key(tid)] = copy.deepcopy(saved)
        return copy.deepcopy(saved)

    def prune_db(
        self,
        db: Session,
        thread_id: UUID | str,
        keep_last: int = _KEEP_LAST,
        max_age_days: int = _MAX_AGE_DAYS,
    ) -> int:
        """Keep last N rows per thread and drop rows older than 30 days."""
        from app.models.thread_checkpoints import ThreadCheckpoint

        tid = UUID(str(thread_id))
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        old_stmt = delete(ThreadCheckpoint).where(
            ThreadCheckpoint.thread_id == tid,
            ThreadCheckpoint.created_at <= cutoff,
        )
        old_result = db.execute(old_stmt)
        removed = int(old_result.rowcount or 0)
        ids_stmt = (
            select(ThreadCheckpoint.id)
            .where(ThreadCheckpoint.thread_id == tid)
            .order_by(
                ThreadCheckpoint.created_at.desc(),
                ThreadCheckpoint.id.desc(),
            )
            .offset(keep_last)
        )
        stale_ids = list(db.execute(ids_stmt).scalars().all())
        if stale_ids:
            trim_stmt = delete(ThreadCheckpoint).where(
                ThreadCheckpoint.id.in_(stale_ids)
            )
            trim_result = db.execute(trim_stmt)
            removed += int(trim_result.rowcount or 0)
        return removed
