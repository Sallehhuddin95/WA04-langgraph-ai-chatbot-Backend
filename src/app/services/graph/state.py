"""Graph state. Tracks messages, docs, intent, and grounding."""

from typing import Literal, TypedDict
from uuid import UUID

IntentCategory = Literal["simple_chat", "rag_search", "complex_task"]


class RetrievedDoc(TypedDict):
    chunk_id: str
    document_id: str
    score: float
    text: str


class ChatMessage(TypedDict):
    role: str
    text: str


class Citation(TypedDict):
    chunk_id: str
    document_id: str
    quote: str


class ChatState(TypedDict, total=False):
    messages: list[ChatMessage]
    retrieved_docs: list[RetrievedDoc]
    prefetched_docs: list[RetrievedDoc] | None
    intent_category: IntentCategory
    is_grounded: bool
    retry_count: int
    trace_id: str
    thread_id: str
    draft_text: str
    reply_text: str
    citations: list[Citation]
    grounding_score: float
    model: str
    image_urls: list[str]
