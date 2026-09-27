"""429 Retry-After header. Unit plus live integration."""

from __future__ import annotations

import uuid

import pytest

import app.services.chat_service as chat_service_mod
from app.routes.auth import _auth_error as auth_error
from app.routes.chat import _from_service_error as chat_error_response
from app.services.auth_service import _LOGIN_FAILS, _login_retry_after
from app.services.chat_service import ChatError, ChatService


def test_in_memory_rate_limit_carries_retry_after() -> None:
    service = ChatService()
    owner = uuid.uuid4()
    service.thread_hits[str(owner)] = [0.0] * 20
    import time

    now = time.monotonic()
    service.thread_hits[str(owner)] = [now] * chat_service_mod.THREAD_RATE_LIMIT
    with pytest.raises(ChatError) as exc_info:
        service.create_thread(owner, "t")
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after is not None
    assert exc_info.value.retry_after >= 1


def test_from_service_error_sets_retry_after_header() -> None:
    exc = ChatError("rate_limited", "slow down", 429, retry_after=42)
    res = chat_error_response(exc)
    assert res.status_code == 429
    assert res.headers.get("retry-after") == "42"


def test_auth_error_sets_retry_after_header() -> None:
    exc = ChatError("rate_limited", "slow down", 429, retry_after=17)
    res = auth_error(exc)
    assert res.status_code == 429
    assert res.headers.get("retry-after") == "17"


def test_login_retry_after_counts_window() -> None:
    email = f"throttle-{uuid.uuid4().hex}@example.com"
    import time

    now = time.monotonic()
    _LOGIN_FAILS[email] = [now] * 5
    try:
        assert _login_retry_after(email) >= 1
    finally:
        _LOGIN_FAILS.pop(email, None)


def test_live_turn_rate_limit_has_retry_after_header(
    live_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, created, signup = live_client
    monkeypatch.setattr(chat_service_mod, "TURN_RATE_LIMIT", 2)
    cookies = signup("retry-after")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    tid = thread["thread_id"]
    for _ in range(2):
        assert (
            client.post(
                f"/api/chat/threads/{tid}/turns",
                json={"message": "hi"},
                cookies=cookies,
            ).status_code
            == 200
        )
    res = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={"message": "hi"},
        cookies=cookies,
    )
    assert res.status_code == 429
    assert res.headers.get("retry-after") is not None
    assert int(res.headers["retry-after"]) >= 1
