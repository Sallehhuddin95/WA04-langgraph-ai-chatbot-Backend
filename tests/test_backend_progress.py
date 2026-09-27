"""Progress tests for config, CORS, SSE citations, and error contract.

Route tests use live_client from conftest (real signup sessions).
"""

from __future__ import annotations

import os
import uuid

import pytest

import app.services.chat_service as chat_service_mod
from app.core.config import get_settings
from app.main import create_app
from app.services import llm_client


def test_openai_base_url_default() -> None:
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert (
            settings.openai_base_url
            == "https://opencode.ai/inference/openai/v1"
        )
    finally:
        get_settings.cache_clear()


def test_cors_allows_frontend_with_credentials() -> None:
    app = create_app()
    origins: list = []
    for item in app.user_middleware:
        options = item.kwargs if hasattr(item, "kwargs") else item[1]
        for origin in options.get("allow_origins", []):
            origins.append(origin)
    assert "http://localhost:3000" in origins


def test_llm_falls_back_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    try:
        assert llm_client.is_configured() is False
    finally:
        get_settings.cache_clear()


def test_stream_emits_citation_events(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("stream-cite")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    turn = client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "what is the refund policy?"},
        cookies=cookies,
    ).json()
    assert turn["is_grounded"] is True
    body = client.get(
        f"/api/chat/threads/{thread['thread_id']}"
        f"/turns/{turn['turn_id']}/stream",
        cookies=cookies,
    ).text
    assert "event: delta" in body
    assert "event: citation" in body
    assert "event: done" in body


def test_stream_simple_chat_has_no_citations(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("stream-simple")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    turn = client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "hi"},
        cookies=cookies,
    ).json()
    assert turn["is_grounded"] is False
    body = client.get(
        f"/api/chat/threads/{thread['thread_id']}"
        f"/turns/{turn['turn_id']}/stream",
        cookies=cookies,
    ).text
    assert "event: delta" in body
    assert "event: citation" not in body


def test_unauthorized_without_cookie(live_client) -> None:
    client, _, _ = live_client
    thread_id = uuid.uuid4()
    assert client.post("/api/chat/threads", json={}).status_code == 401
    assert (
        client.post(
            f"/api/chat/threads/{thread_id}/turns",
            json={"message": "hi"},
        ).status_code
        == 401
    )
    assert (
        client.get(f"/api/chat/threads/{thread_id}/turns").status_code
        == 401
    )


def test_forbidden_cross_owner(live_client) -> None:
    client, created, signup = live_client
    mine = signup("owner-a")
    other = signup("owner-b")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=mine
    ).json()
    created.append(thread["thread_id"])
    assert (
        client.get(
            f"/api/chat/threads/{thread['thread_id']}/turns",
            cookies=other,
        ).status_code
        == 403
    )


def test_not_found_thread(live_client) -> None:
    client, _, signup = live_client
    cookies = signup("not-found")
    missing = uuid.uuid4()
    res = client.get(
        f"/api/chat/threads/{missing}/turns", cookies=cookies
    )
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "not_found"


def test_validation_failures(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("validation")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    tid = thread["thread_id"]
    assert (
        client.post(
            f"/api/chat/threads/{tid}/turns",
            json={"message": ""},
            cookies=cookies,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/chat/threads",
            json={"title": "x" * 121},
            cookies=cookies,
        ).status_code
        == 422
    )
    assert (
        client.get(
            f"/api/chat/threads/{tid}/turns?limit=99",
            cookies=cookies,
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/api/chat/threads/{tid}/turns",
            json={"message": "hi"},
            headers={"Idempotency-Key": "not-a-uuid"},
            cookies=cookies,
        ).status_code
        == 422
    )


def test_rate_limited_turns(
    live_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, created, signup = live_client
    monkeypatch.setattr(chat_service_mod, "TURN_RATE_LIMIT", 2)
    cookies = signup("rate-limit")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    tid = thread["thread_id"]
    for _ in range(2):
        res = client.post(
            f"/api/chat/threads/{tid}/turns",
            json={"message": "hi"},
            cookies=cookies,
        )
        assert res.status_code == 200
    res = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={"message": "hi"},
        cookies=cookies,
    )
    assert res.status_code == 429
    assert res.json()["error"]["code"] == "rate_limited"


def test_model_outage_maps_to_502(
    live_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, created, signup = live_client

    def boom(state):
        raise RuntimeError("retriever down")

    monkeypatch.setattr(chat_service_mod, "run_turn", boom)
    cookies = signup("outage")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    res = client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "what is the refund policy?"},
        cookies=cookies,
    )
    assert res.status_code == 502
    assert "trace_id" in res.json()["error"]


def test_model_timeout_maps_to_504(
    live_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, created, signup = live_client

    def slow(state):
        raise TimeoutError("too slow")

    monkeypatch.setattr(chat_service_mod, "run_turn", slow)
    cookies = signup("timeout")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    res = client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "what is the refund policy?"},
        cookies=cookies,
    )
    assert res.status_code == 504


def test_idempotent_replay_returns_same_turn(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("idempotent")
    key = str(uuid.uuid4())
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    tid = thread["thread_id"]
    first = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={
            "message": "what is the refund policy?",
            "idempotency_key": key,
        },
        cookies=cookies,
    ).json()
    second = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={
            "message": "what is the refund policy?",
            "idempotency_key": key,
        },
        headers={"Idempotency-Key": key},
        cookies=cookies,
    ).json()
    assert first["turn_id"] == second["turn_id"]
    assert first["trace_id"] == second["trace_id"]


def test_repos_need_live_pgvector() -> None:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        pytest.skip("DATABASE_URL not set in test env")
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            names = [
                row[0]
                for row in conn.execute(
                    text("SELECT name FROM pg_available_extensions")
                )
            ]
        engine.dispose()
    except Exception as exc:
        pytest.skip(f"DB unreachable: {exc}")
    if "vector" not in names:
        pytest.skip("pgvector extension missing on server")
