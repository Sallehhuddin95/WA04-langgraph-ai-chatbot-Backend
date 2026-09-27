"""Attachment repository. Owns image rows for vision turns."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attachments import Attachment


class AttachmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self, thread_id: UUID, filename: str, mime: str, data: bytes
    ) -> Attachment:
        row = Attachment(
            thread_id=thread_id,
            filename=filename,
            mime=mime,
            size=len(data),
            data=data,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_for_turn(
        self, thread_id: UUID, attachment_ids: list[UUID]
    ) -> list[Attachment]:
        if not attachment_ids:
            return []
        stmt = select(Attachment).where(Attachment.id.in_(attachment_ids))
        rows = list(self.db.execute(stmt).scalars().all())
        found = {row.id for row in rows}
        missing = [key for key in attachment_ids if key not in found]
        if missing:
            raise LookupError(f"attachments not found: {missing}")
        foreign = [row for row in rows if row.thread_id != thread_id]
        if foreign:
            raise PermissionError("cross-thread attachments denied")
        by_id = {row.id: row for row in rows}
        return [by_id[key] for key in attachment_ids]
