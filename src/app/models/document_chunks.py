"""Document chunk ORM model. Embedding uses Vector(1536)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, Text, UniqueConstraint, func
from sqlalchemy import text as sql_text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pgvector.sqlalchemy import Vector

from app.models.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "chunk_index", name="uq_document_chunks_doc_chunk"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer(), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    embedding: Mapped[Any] = mapped_column(Vector(1536), nullable=False)
    meta: Mapped[dict] = mapped_column(
        "meta", JSONB(), nullable=False, server_default=sql_text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
