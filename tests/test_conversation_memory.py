"""Single-entity memory. History crosses model switches."""

from __future__ import annotations

import uuid

import app.services.chat_service as chat_service_mod
import app.services.graph.generator as gen
from app.services.chat_service import ChatService


def test_in_memory_turn_carries_prior_messages(
    monkeypatch,
) -> None:
    captured: dict = {}

    def fake_run_turn(state):
        captured["messages"] = list(state.get("messages") or [])
        return {
            "reply_text": "ok",
            "citations": [],
            "intent_category": "simple_chat",
            "is_grounded": False,
        }

    monkeypatch.setattr(chat_service_mod, "run_turn", fake_run_turn)
    service = ChatService()
    owner = uuid.uuid4()
    thread_id = service.create_thread(owner, "t")["thread_id"]
    service.create_turn(owner, thread_id, "my dog is named Bingo", uuid.uuid4())
    service.create_turn(owner, thread_id, "what is my dog called?", uuid.uuid4())
    texts = [m["text"] for m in captured["messages"]]
    assert "my dog is named Bingo" in texts
    assert "what is my dog called?" in texts


def test_long_thread_keeps_early_turns(monkeypatch) -> None:
    captured: dict = {}

    def fake_run_turn(state):
        captured["messages"] = list(state.get("messages") or [])
        return {
            "reply_text": "ok",
            "citations": [],
            "intent_category": "simple_chat",
            "is_grounded": False,
        }

    monkeypatch.setattr(chat_service_mod, "run_turn", fake_run_turn)
    service = ChatService()
    owner = uuid.uuid4()
    thread_id = service.create_thread(owner, "t")["thread_id"]
    service.create_turn(owner, thread_id, "first calc was 42", uuid.uuid4())
    for index in range(14):
        service.create_turn(owner, thread_id, f"filler {index}", uuid.uuid4())
    service.create_turn(owner, thread_id, "repeat the first calc", uuid.uuid4())
    texts = [m["text"] for m in captured["messages"]]
    assert "first calc was 42" in texts


def test_chat_payload_keeps_history_and_persona(monkeypatch) -> None:
    captured: dict = {}

    def fake_chat_text(model, messages, **kwargs):
        captured["messages"] = messages
        return "remembered"

    monkeypatch.setattr("app.services.llm_client.chat_text", fake_chat_text)
    monkeypatch.setattr(
        "app.services.llm_client.is_configured", lambda: True
    )
    monkeypatch.setattr(
        "app.services.model_registry.model_api", lambda model: "chat"
    )
    monkeypatch.setattr(
        "app.services.model_registry.provider_model", lambda model: model
    )
    state = {
        "messages": [
            {"role": "user", "text": "my dog is named Bingo"},
            {"role": "assistant", "text": "cute name"},
            {"role": "user", "text": "what is my dog called?"},
        ],
        "model": "deepseek-v4-flash",
        "thread_id": "tid",
    }
    assert gen.direct_answer(state) == "remembered"  # type: ignore[arg-type]
    payload = captured["messages"]
    assert "Singularity" in payload[0]["content"]
    roles = [m["role"] for m in payload]
    assert roles.count("assistant") >= 1
    assert payload[-1]["content"] == "what is my dog called?"
