"""Chat flow tests. Covers bypass, grounding, fallback, and idempotency."""

from __future__ import annotations

import uuid

import pytest

from app.services.chat_service import ChatService


def _fresh_service() -> tuple[ChatService, object, object]:
    service = ChatService()
    owner = uuid.uuid4()
    thread = service.create_thread(owner, "test thread")
    return service, owner, thread["thread_id"]


def test_simple_bypass_skips_retrieval() -> None:
    service, owner, thread_id = _fresh_service()
    result = service.create_turn(owner, thread_id, "hi there", uuid.uuid4())
    assert result["intent_category"] == "simple_chat"
    assert result["is_grounded"] is False
    assert result["citations"] == []


def test_grounded_answer_carries_citations() -> None:
    service, owner, thread_id = _fresh_service()
    result = service.create_turn(owner, thread_id, "what is the refund policy?", uuid.uuid4())
    assert result["intent_category"] == "rag_search"
    assert result["is_grounded"] is True
    assert len(result["citations"]) >= 1
    assert "[1]" in result["reply_text"]


def test_fallback_when_no_docs_match() -> None:
    service, owner, thread_id = _fresh_service()
    result = service.create_turn(owner, thread_id, "zxqv wobble florp quantum banana", uuid.uuid4())
    assert result["is_grounded"] is False
    assert result["citations"] == []
    assert "not ground" in result["reply_text"].lower()


def test_idempotent_retry_returns_same_trace() -> None:
    service, owner, thread_id = _fresh_service()
    key = uuid.uuid4()
    first = service.create_turn(owner, thread_id, "what is the refund policy?", key)
    second = service.create_turn(owner, thread_id, "what is the refund policy?", key)
    assert first["turn_id"] == second["turn_id"]
    assert first["trace_id"] == second["trace_id"]
    page = service.list_turns(owner, thread_id, limit=50)
    assistant_turns = [item for item in page["items"] if item["role"] == "assistant"]
    assert len(assistant_turns) == 1


def test_creative_requests_skip_retrieval() -> None:
    from app.services.graph.router import classify_intent

    assert classify_intent("tell me a joke about zuck") == "simple_chat"
    assert classify_intent("what do you think of this?") == "simple_chat"
    assert classify_intent("what is the refund policy?") == "rag_search"
    assert (
        classify_intent("compare the refund and shipping policies")
        == "complex_task"
    )


def test_ungrounded_gets_direct_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.services.graph.generator as gen

    monkeypatch.setattr(
        gen, "direct_answer", lambda state: "Direct opinion here."
    )
    service, owner, thread_id = _fresh_service()
    result = service.create_turn(
        owner, thread_id, "zxqv wobble florp quantum", uuid.uuid4()
    )
    assert result["reply_text"] == "Direct opinion here."
    assert result["is_grounded"] is False
    assert result["citations"] == []
