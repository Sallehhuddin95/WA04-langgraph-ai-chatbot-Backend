"""Generator node. Writes grounded replies plus direct answers.

Grounded turns cite retrieved docs. Simple chat takes the direct
path: a short model-written reply marked ungrounded. Model choice
comes from state (per-turn dropdown) with an env default.
"""

from __future__ import annotations

import os

from app.services.graph.state import ChatState, Citation

MODEL_GENERATOR = os.getenv("MODEL_GENERATOR", "")

SINGULARITY_PERSONA = (
    "Your name is Singularity. You are the chatbot of this app, and this app "
    "is called Singularity. You are one continuous assistant: every reply comes "
    "from Singularity no matter which model powers this turn. "
    "Never identify as DeepSeek, Muse, or any other model or company, and never "
    "mention a different creator. The underlying model is an implementation detail "
    "the user never needs to hear about. If asked for the app or chatbot name, "
    "answer Singularity. "
    "Stay consistent with the conversation history and never claim a fresh start, "
    "a reset session, or missing access when history is present."
)


def _selected_model(state: ChatState) -> str:
    from app.services.model_registry import DEFAULT_MODEL

    return state.get("model") or MODEL_GENERATOR or DEFAULT_MODEL


def _history_messages(
    messages: list[dict], current_text: str, keep: int = 30
) -> list[dict]:
    """Prior turns as chat roles, excluding the current message tail."""
    tail = [
        {"role": "user" if m.get("role") == "user" else "assistant", "text": str(m.get("text", ""))}
        for m in (messages or [])[:-1]
        if str(m.get("text", "")).strip()
    ]
    return tail[-keep:]


def _generate_text(
    model: str,
    system: str,
    user_text: str,
    images: list[str],
    session_id: str | None,
    max_tokens: int,
    history: list[dict] | None = None,
) -> str:
    """Call the selected model. Dispatches chat vs responses API."""
    from app.services import llm_client
    from app.services.model_registry import model_api, provider_model

    persona_system = f"{SINGULARITY_PERSONA} {system}"
    past = history or []
    target = provider_model(model)
    if model_api(model) == "responses":
        lines = [persona_system, ""]
        for item in past[-30:]:
            role = "User" if item.get("role") == "user" else "Singularity"
            lines.append(f"{role}: {item.get('text', '')}")
        lines.append(f"User: {user_text}")
        return llm_client.responses_text(
            target,
            "\n".join(lines),
            timeout_s=30.0,
            session_id=session_id,
            images=images or None,
        )
    content: object = user_text
    if images:
        parts: list[dict] = [{"type": "text", "text": user_text}]
        parts.extend(
            {"type": "image_url", "image_url": {"url": url}}
            for url in images[:5]
        )
        content = parts
    chat_messages: list[dict] = [{"role": "system", "content": persona_system}]
    for item in past[-30:]:
        role = "user" if item.get("role") == "user" else "assistant"
        chat_messages.append({"role": role, "content": item.get("text", "")})
    chat_messages.append({"role": "user", "content": content})
    return llm_client.chat_text(
        target,
        chat_messages,
        timeout_s=30.0,
        max_tokens=max_tokens,
        session_id=session_id,
    )


def _history_and_docs(messages: list[dict], docs: list[dict]) -> str:
    snippets = "\n".join(
        f"[{i}] {str(d.get('text', ''))[:500]}"
        for i, d in enumerate(docs[:8], start=1)
    )
    history = "\n".join(
        f"{m.get('role', 'user')}: {m.get('text', '')}" for m in messages[-6:]
    )
    return f"History:\n{history}\nDocs:\n{snippets}"


def _opencode_generate(state: ChatState, docs: list[dict]) -> str | None:
    """Draft a grounded reply. None when no model key is set."""
    from app.services.llm_client import is_configured

    if not is_configured():
        return None
    images = state.get("image_urls") or []
    messages = state.get("messages") or []
    current = ""
    for entry in reversed(messages):
        if entry.get("role") == "user":
            current = entry.get("text", "")
            break
    context = _history_and_docs(messages, docs)
    return _generate_text(
        _selected_model(state),
        (
            "Answer the user using only the docs below. "
            "Cite sources with [1], [2] markers. "
            "If the docs do not support an answer, say so plainly. "
            "Use the conversation history for context."
        ),
        f"{context}\n\nCurrent question: {current}",
        images,
        state.get("thread_id"),
        1024,
        _history_messages(messages, current),
    )


def direct_answer(state: ChatState) -> str | None:
    """Write a short direct reply. None when no model key is set."""
    from app.services.llm_client import is_configured

    if not is_configured():
        return None
    messages = state.get("messages") or []
    current = ""
    for entry in reversed(messages):
        if entry.get("role") == "user":
            current = entry.get("text", "")
            break
    return _generate_text(
        _selected_model(state),
        "Reply briefly and directly in a friendly tone. Use the conversation history for context.",
        current or "Continue the conversation.",
        [],
        state.get("thread_id"),
        512,
        _history_messages(messages, current),
    )


FALLBACK_TEXT = (
    "I could not ground this answer in the available docs. "
    "Try rephrasing with more detail or a narrower topic."
)


def _quote(text: str, limit: int = 120) -> str:
    snippet = " ".join(text.split())
    return snippet[:limit]


def build_citations(docs: list[dict]) -> list[Citation]:
    citations: list[Citation] = []
    for doc in docs:
        citations.append(
            {
                "chunk_id": str(doc.get("chunk_id", "")),
                "document_id": str(doc.get("document_id", "")),
                "quote": _quote(doc.get("text", "")),
            }
        )
    return citations


def vision_reply(state: ChatState) -> ChatState:
    """Answer about attached images. Ungrounded, no citations."""
    from app.services.llm_client import is_configured

    images = state.get("image_urls") or []
    if not is_configured() or not images:
        return fallback_reply(state)
    messages = state.get("messages") or []
    query = ""
    for entry in reversed(messages):
        if entry.get("role") == "user":
            query = entry.get("text", "")
            break
    try:
        state["reply_text"] = _generate_text(
            _selected_model(state),
            "Describe or answer about the attached images directly. Use the conversation history for context.",
            query,
            images,
            state.get("thread_id"),
            1024,
            _history_messages(messages, query),
        )
    except Exception:
        return fallback_reply(state)
    state["citations"] = []
    state["is_grounded"] = False
    return state


def direct_reply(state: ChatState) -> ChatState:
    """Answer small talk directly. Ungrounded, no citations."""
    drafted = direct_answer(state)
    if drafted is None:
        return fallback_reply(state)
    state["reply_text"] = drafted
    state["citations"] = []
    state["is_grounded"] = False
    return state


def generate_reply(state: ChatState) -> ChatState:
    """Write reply_text plus citations from the graded docs."""
    docs = state.get("retrieved_docs") or []
    grounded = bool(state.get("is_grounded", False)) and bool(docs)
    if not grounded:
        return fallback_reply(state)
    drafted = _opencode_generate(state, docs)
    if drafted is None:
        parts: list[str] = []
        for index, doc in enumerate(docs[:2], start=1):
            parts.append(f"{_quote(doc.get('text', ''))} [{index}]")
        state["reply_text"] = "Based on the docs: " + " ".join(parts)
    else:
        state["reply_text"] = drafted
    state["citations"] = build_citations(docs[:2])
    state["is_grounded"] = True
    return state


def fallback_reply(state: ChatState) -> ChatState:
    """Return the ungrounded fallback after empty recall or failed grades."""
    state["reply_text"] = FALLBACK_TEXT
    state["citations"] = []
    state["is_grounded"] = False
    return state


def ungrounded_reply(state: ChatState) -> ChatState:
    """Answer from model knowledge when docs do not support a reply.

    Falls back to the static text only when no model key is set.
    The reply stays ungrounded with no citations either way.
    """
    drafted = direct_answer(state)
    if drafted is None:
        return fallback_reply(state)
    state["reply_text"] = drafted
    state["citations"] = []
    state["is_grounded"] = False
    return state
