"""Thread checkpoint ORM model. Postgres resume store."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy import text as sql_text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ThreadCheckpoint(Base):
    __tablename__ = "thread_checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # No FK to threads.id by design. Checkpoints survive thread
    # deletes until the purge job removes them.
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    trace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    intent_category: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    is_grounded: Mapped[bool | None] = mapped_column(
        Boolean(), nullable=True
    )
    state: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sql_text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
