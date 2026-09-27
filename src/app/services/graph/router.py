"""Router node. Classifies each turn into an intent category.

Mock classifier using keyword plus length heuristics. The
``classify_intent`` signature stays stable so a DeepSeek Flash call
can replace the body later without touching callers.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence

from app.services.graph.state import ChatState, IntentCategory

# Model name comes from env, never hardcoded. Unused while mocked,
# kept so the LLM swap only fills in _llm_classify.
MODEL_ROUTER = os.getenv("MODEL_ROUTER", "")

SIMPLE_PHRASES = (
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "thanks",
    "thank you",
    "bye",
    "goodbye",
    "ok",
    "okay",
    "cool",
    "great",
    "nice",
)

COMPLEX_KEYWORDS = (
    "plan",
    "steps",
    "step by step",
    "roadmap",
    "compare",
    "analysis",
    "analyze",
    "strategy",
    "design",
    "report",
    "summarize",
    "migration",
    "multi",
    "workflow",
    "project",
)

# Creative requests never need docs, so they skip retrieval even
# when the wording looks like a question.
CREATIVE_MARKERS = (
    "joke",
    "funny",
    "make me laugh",
    "opinion",
    "what do you think",
    "do you think",
    "favorite",
    "favourite",
    "poem",
    "riddle",
    "tell me a story",
    "bedtime story",
)

# Swap point for DeepSeek Flash. Set a callable
# ``(message, history) -> IntentCategory | None`` to override the
# heuristic. Return None from the hook to fall back to heuristics.
LlmClassifier = Callable[[str, Sequence[Mapping[str, str]]], "IntentCategory | None"]
_llm_classify: LlmClassifier | None = None


def set_llm_classifier(fn: LlmClassifier | None) -> None:
    """Register or clear the LLM classifier hook. Used by the model swap."""
    global _llm_classify
    _llm_classify = fn


def _history_tail(state: ChatState, keep: int = 6) -> list[Mapping[str, str]]:
    messages = state.get("messages") or []
    return list(messages[-keep:])


def _opencode_classify(
    message: str,
    history: Sequence[Mapping[str, str]],
    session_id: str | None = None,
) -> IntentCategory | None:
    """Classify via MODEL_ROUTER on opencode inference. None on low signal."""
    from app.services.llm_client import chat_text, is_configured

    if not is_configured() or not MODEL_ROUTER:
        return None
    tail = list(history[-6:])
    lines = [f"{m.get('role', 'user')}: {m.get('text', '')}" for m in tail]
    lines.append(f"user: {message}")
    prompt = (
        "Classify the last user message into exactly one value: "
        "simple_chat, rag_search, or complex_task. "
        "simple_chat is greeting, small talk, jokes, stories, poems, "
        "opinions, favorites, or any creative request with no doc need. "
        "rag_search is a fact question over docs. "
        "complex_task is a multi-step task needing docs plus planning. "
        "Reply with only the value."
    )
    try:
        raw = chat_text(
            MODEL_ROUTER,
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "\n".join(lines)},
            ],
            max_tokens=16,
            session_id=session_id,
        ).strip().lower()
    except Exception:
        return None
    if raw in ("simple_chat", "rag_search", "complex_task"):
        return raw  # type: ignore[return-value]
    return None


def classify_intent(
    message: str,
    history: Sequence[Mapping[str, str]] | None = None,
    session_id: str | None = None,
) -> IntentCategory:
    """Return simple_chat, rag_search, or complex_task for one turn."""
    text = (message or "").strip()
    lowered = text.lower()
    history = list(history or [])

    if _llm_classify is not None:
        decided = _llm_classify(text, history[-6:])
        if decided in ("simple_chat", "rag_search", "complex_task"):
            return decided

    decided = _opencode_classify(text, history, session_id)
    if decided is not None:
        return decided

    if not lowered:
        return "rag_search"

    for phrase in SIMPLE_PHRASES:
        if lowered == phrase or lowered in (
            f"{phrase}!",
            f"{phrase}.",
            f"{phrase} there",
            f"{phrase} there!",
        ):
            return "simple_chat"
    if len(text) <= 24 and not ("?" in text or "what" in lowered or "how" in lowered):
        words = lowered.split()
        if len(words) <= 4 and not any(
            k in lowered for k in ("policy", "refund", "doc", "document", "search", "find")
        ):
            return "simple_chat"

    if len(text) > 250 or text.count("?") >= 2:
        return "complex_task"
    if any(keyword in lowered for keyword in COMPLEX_KEYWORDS):
        return "complex_task"
    if any(marker in lowered for marker in CREATIVE_MARKERS):
        return "simple_chat"

    # Default on low confidence per chat-agent spec.
    return "rag_search"


def route_turn(state: ChatState) -> ChatState:
    """Set intent_category from the latest user message plus tail history."""
    messages = state.get("messages") or []
    current = ""
    for entry in reversed(messages):
        if entry.get("role") == "user":
            current = entry.get("text", "")
            break
    if not current and messages:
        current = messages[-1].get("text", "")
    state["intent_category"] = classify_intent(
        current, _history_tail(state), state.get("thread_id")
    )
    return state
