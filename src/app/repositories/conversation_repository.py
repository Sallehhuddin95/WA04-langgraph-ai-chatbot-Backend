"""Conversation repository. Owns threads and messages persistence.

Delete is soft (deleted_at). Reads skip soft-deleted rows unless
the caller asks for them (restore flows). A purge job owns hard
removal later.
"""

from __future__ import annotations

import base64
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.messages import Message
from app.models.threads import Thread


def _decode_offset(cursor: str | None, total: int) -> int:
    if cursor is None:
        return 0
    offset = int(base64.urlsafe_b64decode(cursor.encode()).decode())
    if offset < 0 or offset > total:
        raise ValueError("bad cursor")
    return offset


class ConversationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_thread(self, thread_id: UUID, owner_id: UUID) -> Thread | None:
        row = self.db.get(Thread, thread_id)
        if (
            row is None
            or row.owner_id != owner_id
            or row.deleted_at is not None
        ):
            return None
        return row

    def get_thread_any_owner(self, thread_id: UUID) -> Thread | None:
        row = self.db.get(Thread, thread_id)
        if row is None or row.deleted_at is not None:
            return None
        return row

    def get_thread_with_deleted(self, thread_id: UUID) -> Thread | None:
        return self.db.get(Thread, thread_id)

    def create_thread(self, owner_id: UUID, title: str | None) -> Thread:
        row = Thread(owner_id=owner_id, title=title)
        self.db.add(row)
        self.db.flush()
        return row

    def list_threads(self, owner_id: UUID, limit: int = 50) -> list[Thread]:
        from sqlalchemy import case

        stmt = (
            select(Thread)
            .where(
                Thread.owner_id == owner_id,
                Thread.deleted_at.is_(None),
            )
            .order_by(
                Thread.is_pinned.desc(),
                case((Thread.pin_order.is_(None), 1), else_=0),
                Thread.pin_order.asc(),
                Thread.updated_at.desc(),
                Thread.id.desc(),
            )
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def pinned_threads(self, owner_id: UUID) -> list[Thread]:
        stmt = (
            select(Thread)
            .where(
                Thread.owner_id == owner_id,
                Thread.deleted_at.is_(None),
                Thread.is_pinned.is_(True),
            )
            .order_by(Thread.pin_order.asc(), Thread.id.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def rename_thread(self, thread_id: UUID, title: str) -> None:
        row = self.db.get(Thread, thread_id)
        if row is not None:
            row.title = title
            self.db.flush()

    def set_pin(
        self, thread_id: UUID, pinned: bool, position: int | None
    ) -> None:
        row = self.db.get(Thread, thread_id)
        if row is None:
            return
        row.is_pinned = pinned
        row.pin_order = position
        self.db.flush()

    def delete_thread(self, thread_id: UUID) -> None:
        """Hard delete a thread. Messages cascade. Tests and purge only."""
        row = self.db.get(Thread, thread_id)
        if row is not None:
            self.db.delete(row)
            self.db.flush()

    def soft_delete_thread(self, thread_id: UUID, now: datetime) -> None:
        thread = self.db.get(Thread, thread_id)
        if thread is None:
            return
        thread.deleted_at = now
        for row in (
            self.db.execute(
                select(Message).where(Message.thread_id == thread_id)
            )
            .scalars()
            .all()
        ):
            if row.deleted_at is None:
                row.deleted_at = now
        self.db.flush()

    def restore_thread(
        self, thread_id: UUID, since: datetime | None = None
    ) -> None:
        thread = self.db.get(Thread, thread_id)
        if thread is None:
            return
        thread.deleted_at = None
        for row in (
            self.db.execute(
                select(Message).where(Message.thread_id == thread_id)
            )
            .scalars()
            .all()
        ):
            if row.deleted_at is None:
                continue
            if since is not None and row.deleted_at < since:
                continue
            row.deleted_at = None
        self.db.flush()

    def find_turn_by_idempotency_key(
        self, thread_id: UUID, idempotency_key: UUID
    ) -> Message | None:
        stmt = (
            select(Message)
            .where(
                Message.thread_id == thread_id,
                Message.idempotency_key == idempotency_key,
                Message.role == "assistant",
                Message.deleted_at.is_(None),
            )
            .limit(1)
        )
        return self.db.execute(stmt).scalars().first()

    def get_message(
        self, thread_id: UUID, turn_id: UUID, include_deleted: bool = False
    ) -> Message | None:
        row = self.db.get(Message, turn_id)
        if row is None or row.thread_id != thread_id:
            return None
        if not include_deleted and row.deleted_at is not None:
            return None
        return row

    def soft_delete_message(self, row: Message, now: datetime) -> None:
        row.deleted_at = now
        self.db.flush()

    def restore_message(self, row: Message) -> None:
        row.deleted_at = None
        self.db.flush()

    def list_turns(
        self, thread_id: UUID, limit: int = 20, cursor: str | None = None
    ) -> dict:
        scope = (
            Message.thread_id == thread_id,
            Message.deleted_at.is_(None),
        )
        count_stmt = select(Message).where(*scope)
        total = len(self.db.execute(count_stmt).scalars().all())
        offset = _decode_offset(cursor, total)
        stmt = (
            select(Message)
            .where(*scope)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .offset(offset)
            .limit(limit)
        )
        items = list(self.db.execute(stmt).scalars().all())
        next_offset = offset + len(items)
        next_cursor = None
        if next_offset < total:
            next_cursor = base64.urlsafe_b64encode(
                str(next_offset).encode()
            ).decode()
        return {"items": items, "next_cursor": next_cursor}

    def list_recent_messages(
        self, thread_id: UUID, limit: int = 50
    ) -> list:
        """Newest-last messages for model memory. Skips soft-deleted rows."""
        count = max(1, min(limit, 100))
        stmt = (
            select(Message)
            .where(
                Message.thread_id == thread_id,
                Message.deleted_at.is_(None),
            )
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(count)
        )
        rows = list(self.db.execute(stmt).scalars().all())
        rows.reverse()
        return rows

    def add_message(
        self,
        thread_id: UUID,
        role: str,
        text: str,
        trace_id: UUID,
        idempotency_key: UUID | None = None,
        intent_category: str | None = None,
        is_grounded: bool | None = None,
    ) -> Message:
        row = Message(
            thread_id=thread_id,
            role=role,
            text=text,
            trace_id=trace_id,
            idempotency_key=idempotency_key,
            intent_category=intent_category,
            is_grounded=is_grounded,
        )
        self.db.add(row)
        self.db.flush()
        return row
