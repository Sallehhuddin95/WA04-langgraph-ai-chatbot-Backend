"""Grader node. Keyword-overlap relevance stub.

The interface matches the planned DeepSeek Flash grader: input is the
user query plus retrieved docs, output is ``is_grounded`` plus a
numeric score kept for logs. Retry budget lives here as MAX_RETRIES
and is enforced by the graph loop.
"""

from __future__ import annotations

from app.services.graph.retriever import score_chunk
from app.services.graph.state import ChatState

MAX_RETRIES = 2
GROUNDED_THRESHOLD = 0.2

MODEL_ROUTER = ""
try:
    import os as _os

    MODEL_ROUTER = _os.getenv("MODEL_ROUTER", "")
except Exception:
    MODEL_ROUTER = ""


def _opencode_score(
    query: str, docs: list[dict], session_id: str | None = None
) -> float | None:
    """Score draft support via MODEL_ROUTER. None when unusable."""
    from app.services.llm_client import chat_text, is_configured

    if not is_configured() or not MODEL_ROUTER or not docs:
        return None
    snippets = "\n".join(
        f"[{i}] {str(d.get('text', ''))[:300]}"
        for i, d in enumerate(docs[:8], start=1)
    )
    try:
        raw = chat_text(
            MODEL_ROUTER,
            [
                {
                    "role": "system",
                    "content": (
                        "Rate how well the docs support an answer to the "
                        "query. Reply with only a number from 0 to 1."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\nDocs:\n{snippets}",
                },
            ],
            max_tokens=16,
            session_id=session_id,
        ).strip()
    except Exception:
        return None
    try:
        return max(0.0, min(1.0, float(raw.split()[0])))
    except (ValueError, IndexError):
        return None


def score_relevance(query: str, docs: list[dict]) -> float:
    """Best chunk overlap score, 0 when no docs."""
    if not docs:
        return 0.0
    return max(score_chunk(query, doc.get("text", "")) for doc in docs)


def needs_retry(state: ChatState) -> bool:
    """True when ungrounded and the retry budget is not spent."""
    return not state.get("is_grounded", False) and int(state.get("retry_count", 0)) < MAX_RETRIES


def grade_draft(state: ChatState) -> ChatState:
    """Set is_grounded plus grounding_score from keyword overlap."""
    messages = state.get("messages") or []
    query = ""
    for entry in reversed(messages):
        if entry.get("role") == "user":
            query = entry.get("text", "")
            break
    docs = state.get("retrieved_docs") or []
    score = _opencode_score(query, docs, state.get("thread_id"))
    if score is None:
        score = score_relevance(query, docs)
    state["grounding_score"] = score
    state["is_grounded"] = bool(docs) and score >= GROUNDED_THRESHOLD
    return state
