"""Pydantic v2 contracts for the chat API. Mirrors specs/api/chat-api.md."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

IntentCategory = Literal["simple_chat", "rag_search", "complex_task"]
Role = Literal["user", "assistant", "system"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateThreadRequest(StrictModel):
    title: str | None = Field(default=None, max_length=120)


class CreateThreadResponse(BaseModel):
    thread_id: UUID
    title: str | None = None
    created_at: datetime


class CreateTurnRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4000)
    idempotency_key: UUID | None = None
    model: str = Field(default="deepseek-v4-flash", max_length=64)
    attachment_ids: list[UUID] = Field(default_factory=list, max_length=5)


class CitationResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    quote: str


class TurnAttachment(BaseModel):
    attachment_id: UUID
    filename: str
    mime: str


class CreateTurnResponse(BaseModel):
    thread_id: UUID
    turn_id: UUID
    reply_text: str
    citations: list[CitationResponse] = Field(default_factory=list)
    intent_category: IntentCategory
    is_grounded: bool
    trace_id: UUID
    attachments: list[TurnAttachment] = Field(default_factory=list)


class TurnItem(BaseModel):
    turn_id: UUID
    role: Role
    text: str
    intent_category: IntentCategory | None = None
    is_grounded: bool | None = None
    trace_id: UUID | None = None
    citations: list[CitationResponse] = Field(default_factory=list)
    created_at: datetime


class ThreadSummary(BaseModel):
    thread_id: UUID
    title: str | None = None
    updated_at: datetime
    is_pinned: bool = False
    pin_order: int | None = None


class ListThreadsResponse(BaseModel):
    threads: list[ThreadSummary]


class RenameThreadRequest(StrictModel):
    title: str = Field(min_length=1, max_length=120)


class PinThreadRequest(StrictModel):
    position: int | None = Field(default=None, ge=0)


class ReorderPinsRequest(StrictModel):
    thread_ids: list[UUID] = Field(min_length=1, max_length=5)


class UploadAttachmentResponse(BaseModel):
    attachment_id: UUID
    filename: str
    mime: str
    size: int


class ListTurnsParams(StrictModel):
    limit: int = Field(default=20, ge=1, le=50)
    cursor: str | None = None


class ListTurnsResponse(BaseModel):
    items: list[TurnItem]
    next_cursor: str | None = None


class StreamDelta(BaseModel):
    turn_id: UUID
    trace_id: UUID
    delta: str


class StreamDone(BaseModel):
    turn_id: UUID
    trace_id: UUID
    intent_category: IntentCategory
    is_grounded: bool


class DeleteThreadResponse(BaseModel):
    thread_id: UUID
    deleted_at: datetime | None = None
    purge_at: datetime | None = None
    days_remaining: int | None = None


class DeletedThreadInfo(BaseModel):
    thread_id: UUID
    title: str | None = None
    deleted_at: datetime
    purge_at: datetime
    days_remaining: int
    needs_reminder: bool


class ListDeletedThreadsResponse(BaseModel):
    threads: list[DeletedThreadInfo]


class CheckpointResponse(BaseModel):
    thread_id: UUID
    trace_id: UUID | None = None
    intent_category: str | None = None
    is_grounded: bool | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    trace_id: UUID


class ErrorResponse(BaseModel):
    error: ErrorDetail
