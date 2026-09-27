"""Retriever node. In-memory stub with top-k rule.

Real recall (pgvector cosine) replaces ``score_chunk`` and
``MOCK_CHUNKS`` later. The k rule stays: 5 for rag_search,
8 for complex_task, 0 for simple_chat.
"""

from __future__ import annotations

import re
import uuid

from app.services.graph.state import ChatState, RetrievedDoc

TOP_K_RAG = 5
TOP_K_COMPLEX = 8

_WORD = re.compile(r"[a-z0-9]+")


def _chunk(document_text: str, namespace: str, index: int) -> RetrievedDoc:
    return {
        "chunk_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"mock-chunk:{namespace}:{index}")),
        "document_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"mock-doc:{namespace}")),
        "score": 0.0,
        "text": document_text,
    }


MOCK_CHUNKS: list[RetrievedDoc] = [
    _chunk("Refunds close in 30 days with a receipt. Contact support for help.", "refunds", 1),
    _chunk("Refund requests need the order id and purchase date.", "refunds", 2),
    _chunk("Shipping takes 3-5 business days. Express options exist at checkout.", "shipping", 1),
    _chunk("Warranty covers defects for 12 months from delivery.", "warranty", 1),
    _chunk("Password reset links expire after 60 minutes.", "account", 1),
    _chunk("Pricing tiers are starter, team, and enterprise, billed monthly.", "pricing", 1),
    _chunk("Data exports are available as CSV from the settings page.", "exports", 1),
    _chunk("Support hours are weekdays 9-5 UTC with 24h response target.", "support", 1),
]

_STOPWORDS = frozenset(
    "a an the is are was were be been to of in on for and or what when where which who how "
    "does do did can could would should i me my you your it its this that these those with "
    "there here please tell give show".split()
)


def tokenize(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS}


def score_chunk(query: str, chunk_text: str) -> float:
    """Keyword overlap score between 0 and 1."""
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0.0
    chunk_tokens = tokenize(chunk_text)
    return len(query_tokens & chunk_tokens) / len(query_tokens)


def top_k_for(intent: str) -> int:
    if intent == "complex_task":
        return TOP_K_COMPLEX
    if intent == "rag_search":
        return TOP_K_RAG
    return 0


def set_mock_chunks(chunks: list[RetrievedDoc]) -> None:
    """Replace the stub corpus. Used by tests and local runs."""
    global MOCK_CHUNKS
    MOCK_CHUNKS = list(chunks)


def search_stub(query: str, limit: int) -> list[RetrievedDoc]:
    """Return top-k mock chunks with score > 0, ranked by overlap."""
    if limit <= 0:
        return []
    ranked: list[RetrievedDoc] = []
    for chunk in MOCK_CHUNKS:
        score = score_chunk(query, chunk["text"])
        if score > 0:
            ranked.append({**chunk, "score": score})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]


def retrieve_docs(state: ChatState) -> ChatState:
    """Fill retrieved_docs for the latest user message."""
    intent = state.get("intent_category", "rag_search")
    limit = top_k_for(intent)
    if limit <= 0:
        state["retrieved_docs"] = []
        return state
    prefetched = state.get("prefetched_docs")
    if prefetched is not None:
        state["retrieved_docs"] = list(prefetched)[:limit]
        return state
    messages = state.get("messages") or []
    query = ""
    for entry in reversed(messages):
        if entry.get("role") == "user":
            query = entry.get("text", "")
            break
    state["retrieved_docs"] = search_stub(query, limit)
    return state


def prefetch_vector_docs(query: str, limit: int, db) -> list[RetrievedDoc] | None:
    """Try pgvector recall. Returns None when embeddings are unavailable."""
    from app.repositories.document_repository import DocumentRepository
    from app.services.embeddings import embed_query

    if limit <= 0:
        return []
    vector = embed_query(query)
    if vector is None:
        return None
    try:
        rows = DocumentRepository(db).search_chunks(vector, limit)
    except Exception:
        return None
    docs: list[RetrievedDoc] = []
    for row in rows:
        docs.append(
            {
                "chunk_id": str(row.id),
                "document_id": str(row.document_id),
                "score": 1.0,
                "text": str(row.text),
            }
        )
    return docs
