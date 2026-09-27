"""StateGraph parity tests. Compiled graph must match run_turn."""

from __future__ import annotations

import pytest

from app.core.config import get_settings
from app.services.graph.graph import build_graph, run_turn


@pytest.fixture(autouse=True)
def _no_llm_keys(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="module")
def graph():
    return build_graph()


def _invoke(graph, message: str, tag: str) -> dict:
    base = {
        "messages": [{"role": "user", "text": message}],
        "thread_id": "test-thread",
        "trace_id": f"trace-{tag}",
        "retry_count": 0,
    }
    expected = run_turn(dict(base))
    got = graph.invoke(
        dict(base), config={"configurable": {"thread_id": f"parity-{tag}"}}
    )
    return expected, got


@pytest.mark.parametrize(
    "message,tag,intent,grounded",
    [
        ("hi", "simple", "simple_chat", False),
        ("what is the refund policy?", "rag", "rag_search", True),
        ("zxqv wobble florp quantum banana", "fallback", "rag_search", False),
    ],
)
def test_graph_matches_runner(graph, message, tag, intent, grounded) -> None:
    expected, got = _invoke(graph, message, tag)
    assert got["intent_category"] == intent == expected["intent_category"]
    assert got["is_grounded"] is grounded
    assert got["is_grounded"] == expected["is_grounded"]
    assert got["reply_text"] == expected["reply_text"]
    assert (got.get("citations") or []) == (expected.get("citations") or [])


def test_vision_path_matches_runner(graph) -> None:
    base = {
        "messages": [{"role": "user", "text": "what is this?"}],
        "thread_id": "vision-thread",
        "trace_id": "trace-vision",
        "retry_count": 0,
        "model": "deepseek-v4-flash-vision-exp",
        "image_urls": ["data:image/png;base64,AAAA"],
    }
    expected = run_turn(dict(base))
    got = graph.invoke(
        dict(base), config={"configurable": {"thread_id": "parity-vision"}}
    )
    assert got["reply_text"] == expected["reply_text"]
    assert got["is_grounded"] is False
    assert (got.get("citations") or []) == []
