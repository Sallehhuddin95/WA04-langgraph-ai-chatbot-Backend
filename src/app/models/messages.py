"""Message ORM model. Maps to messages table."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, Text
from sqlalchemy import DateTime, func
from sqlalchemy import text as sql_text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

from app.models.base import Base


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')", name="ck_messages_role"
        ),
        CheckConstraint(
            "intent_category IS NULL OR intent_category IN "
            "('simple_chat', 'rag_search', 'complex_task')",
            name="ck_messages_intent_category",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    intent_category: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    is_grounded: Mapped[bool | None] = mapped_column(
        Boolean(), nullable=True
    )
    trace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    idempotency_key: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    citations: Mapped[list] = mapped_column(
        JSONB(), nullable=False, server_default=sql_text("'[]'::jsonb")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        server_default=func.now(),
    )
