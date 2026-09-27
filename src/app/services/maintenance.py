"""Maintenance jobs. Expired sessions plus soft-delete purge.

Retention policy:
- Sessions past expires_at are hard deleted.
- Soft-deleted threads and single messages past THREAD_PURGE_DAYS
  are hard deleted.
- Customers get a reminder 3 days before a thread is purged.
  The API exposes purge_at, days_remaining, and needs_reminder so
  the UI can show the warning without a mailer.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.messages import Message
from app.models.sessions import UserSession
from app.models.threads import Thread

THREAD_PURGE_DAYS = 30
PURGE_WARNING_DAYS = 3


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def purge_info(
    deleted_at: datetime | None, now: datetime | None = None
) -> dict | None:
    """Return purge timing for a soft-deleted row."""
    if deleted_at is None:
        return None
    at = now or _utcnow()
    marked = deleted_at
    if marked.tzinfo is None:
        marked = marked.replace(tzinfo=timezone.utc)
    current = at
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    purge_at = marked + timedelta(days=THREAD_PURGE_DAYS)
    remaining = (purge_at - current).total_seconds() / 86400.0
    days_remaining = max(0, int(remaining)) if remaining > 0 else 0
    return {
        "purge_at": purge_at,
        "days_remaining": days_remaining,
        "needs_reminder": 0 < remaining <= PURGE_WARNING_DAYS,
        "is_overdue": remaining <= 0,
    }


def cleanup_expired_sessions(db: Session) -> int:
    """Delete sessions past expiry. Returns row count."""
    stmt = delete(UserSession).where(UserSession.expires_at <= _utcnow())
    result = db.execute(stmt)
    db.commit()
    return int(result.rowcount or 0)


def purge_soft_deleted(db: Session, retention_days: int = THREAD_PURGE_DAYS) -> dict:
    """Hard delete old soft-deleted threads and messages."""
    cutoff = _utcnow() - timedelta(days=retention_days)
    thread_stmt = delete(Thread).where(
        Thread.deleted_at.is_not(None),
        Thread.deleted_at <= cutoff,
    )
    thread_result = db.execute(thread_stmt)
    threads = int(thread_result.rowcount or 0)
    # Single messages whose thread is still live but the message
    # itself stayed deleted past retention.
    message_stmt = delete(Message).where(
        Message.deleted_at.is_not(None),
        Message.deleted_at <= cutoff,
    )
    message_result = db.execute(message_stmt)
    messages = int(message_result.rowcount or 0)
    db.commit()
    return {"threads": threads, "messages": messages}


def list_deleted_threads(db: Session, owner_id: UUID) -> list[dict]:
    """Soft-deleted threads for one owner with purge timing."""
    stmt = (
        select(Thread)
        .where(
            Thread.owner_id == owner_id,
            Thread.deleted_at.is_not(None),
        )
        .order_by(Thread.deleted_at.desc())
    )
    rows = list(db.execute(stmt).scalars().all())
    now = _utcnow()
    out: list[dict] = []
    for row in rows:
        info = purge_info(row.deleted_at, now) or {}
        out.append(
            {
                "thread_id": row.id,
                "title": row.title,
                "deleted_at": row.deleted_at,
                "purge_at": info.get("purge_at"),
                "days_remaining": info.get("days_remaining", 0),
                "needs_reminder": bool(info.get("needs_reminder", False)),
            }
        )
    return out


def list_purge_reminders(
    db: Session, owner_id: UUID, warning_days: int = PURGE_WARNING_DAYS
) -> list[dict]:
    """Threads due for the 3-day purge reminder."""
    _ = warning_days
    return [
        item for item in list_deleted_threads(db, owner_id)
        if item["needs_reminder"]
    ]


def prune_checkpoints(db: Session, max_age_days: int = 30) -> int:
    """Drop checkpoint rows older than 30 days."""
    from app.models.thread_checkpoints import ThreadCheckpoint

    cutoff = _utcnow() - timedelta(days=max_age_days)
    result = db.execute(
        delete(ThreadCheckpoint).where(ThreadCheckpoint.created_at <= cutoff)
    )
    db.commit()
    return int(result.rowcount or 0)


def run_maintenance(db: Session) -> dict:
    """Run all jobs. Used by cron and manual triggers."""
    sessions = cleanup_expired_sessions(db)
    purged = purge_soft_deleted(db)
    try:
        checkpoints = prune_checkpoints(db)
    except Exception:
        checkpoints = 0
    return {
        "expired_sessions": sessions,
        "purged_threads": purged["threads"],
        "purged_messages": purged["messages"],
        "pruned_checkpoints": checkpoints,
    }
