"""DB turn path. History plus identity must reach the model.

Runs DbChatService against a fake session (no live Postgres) with a
captured run_turn, so this fails if create_turn ever drops history or
the Singularity persona again.
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID, uuid4

import app.services.chat_service as chat_service_mod
from app.repositories.conversation_repository import ConversationRepository
from app.services.chat_service import DbChatService


class _FakeScalars:
    def __init__(self, rows: list) -> None:
        self._rows = rows

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


class _FakeResult:
    def __init__(self, rows: list | None = None, rowcount: int = 0) -> None:
        self._rows = rows or []
        self.rowcount = rowcount

    def scalars(self):
        return _FakeScalars(self._rows)


class _FakeSession:
    """Stands in for a SQLAlchemy session. No rows persist."""

    def __init__(self, thread: SimpleNamespace) -> None:
        self._thread = thread

    def get(self, model, tid):
        return self._thread

    def add(self, row) -> None:
        return None

    def flush(self) -> None:
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def execute(self, stmt):
        return _FakeResult()


def _service(owner: UUID) -> tuple[DbChatService, SimpleNamespace]:
    from datetime import datetime, timezone

    thread = SimpleNamespace(
        id=uuid4(),
        owner_id=owner,
        title="t",
        updated_at=datetime.now(timezone.utc),
        deleted_at=None,
    )
    return DbChatService(_FakeSession(thread)), thread


def test_db_turn_carries_thread_history(monkeypatch) -> None:
    captured: list = []

    def fake_run_turn(state):
        captured.append(list(state.get("messages") or []))
        return {
            "reply_text": "ok",
            "citations": [],
            "intent_category": "simple_chat",
            "is_grounded": False,
        }

    monkeypatch.setattr(chat_service_mod, "run_turn", fake_run_turn)
    store: list = []

    def fake_add(self, thread_id, role, text, trace_id, **kwargs):
        row = SimpleNamespace(
            thread_id=thread_id,
            role=role,
            text=text,
            id=uuid4(),
            intent_category=kwargs.get("intent_category"),
            is_grounded=kwargs.get("is_grounded"),
            trace_id=trace_id,
            citations=[],
        )
        store.append(row)
        return row

    def fake_recent(self, thread_id, limit=50):
        return [row for row in store if row.thread_id == thread_id][-limit:]

    monkeypatch.setattr(ConversationRepository, "add_message", fake_add)
    monkeypatch.setattr(
        ConversationRepository, "list_recent_messages", fake_recent
    )
    owner = uuid4()
    service, thread = _service(owner)
    service.create_turn(owner, thread.id, "the app name is Singularity", uuid4())
    service.create_turn(owner, thread.id, "what do you think about the name?", uuid4())
    assert len(captured) == 2
    texts = [m["text"] for m in captured[1]]
    assert "the app name is Singularity" in texts
    assert "what do you think about the name?" in texts


def test_model_payload_names_singularity_not_provider(monkeypatch) -> None:
    captured: dict = {}

    def fake_chat_text(model, messages, **kwargs):
        captured["messages"] = messages
        return "Singularity it is."

    monkeypatch.setattr("app.services.llm_client.chat_text", fake_chat_text)
    monkeypatch.setattr("app.services.llm_client.is_configured", lambda: True)
    monkeypatch.setattr(
        "app.services.model_registry.model_api", lambda model: "chat"
    )
    monkeypatch.setattr(
        "app.services.model_registry.provider_model", lambda model: model
    )
    import app.services.graph.generator as gen

    state = {
        "messages": [{"role": "user", "text": "what is this app name?"}],
        "model": "deepseek-v4-flash",
        "thread_id": "tid",
    }
    assert gen.direct_answer(state) == "Singularity it is."  # type: ignore[arg-type]
    system = captured["messages"][0]["content"]
    assert "Singularity" in system
    assert "Never identify as DeepSeek" in system
