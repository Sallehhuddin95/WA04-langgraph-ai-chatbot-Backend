"""Model select, attachments, thread list, history citations, throttle."""

from __future__ import annotations

import base64
import uuid

import pytest

import app.services.auth_service as auth_service_mod

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def test_thread_list_orders_newest_first(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("thread-list")
    first = client.post(
        "/api/chat/threads", json={"title": "a"}, cookies=cookies
    ).json()
    second = client.post(
        "/api/chat/threads", json={"title": "b"}, cookies=cookies
    ).json()
    created.extend([first["thread_id"], second["thread_id"]])
    body = client.get("/api/chat/threads", cookies=cookies).json()
    ids = [row["thread_id"] for row in body["threads"]]
    assert ids[0] == second["thread_id"]
    assert first["thread_id"] in ids


def test_thread_list_without_cookie_is_401(live_client) -> None:
    client, _, _ = live_client
    assert client.get("/api/chat/threads").status_code == 401


def test_history_carries_citations(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("history-cite")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "what is the refund policy?"},
        cookies=cookies,
    )
    page = client.get(
        f"/api/chat/threads/{thread['thread_id']}/turns", cookies=cookies
    ).json()
    assistant = [item for item in page["items"] if item["role"] == "assistant"]
    assert len(assistant) == 1
    assert len(assistant[0]["citations"]) >= 1
    assert "chunk_id" in assistant[0]["citations"][0]


def test_history_orders_user_before_assistant(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("history-order")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "hi there"},
        cookies=cookies,
    )
    page = client.get(
        f"/api/chat/threads/{thread['thread_id']}/turns", cookies=cookies
    ).json()
    roles = [item["role"] for item in page["items"]]
    assert roles == ["user", "assistant"]
    assert page["items"][0]["created_at"] < page["items"][1]["created_at"]


def test_unknown_model_is_422(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("bad-model")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    res = client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "hi", "model": "nope-1"},
        cookies=cookies,
    )
    assert res.status_code == 422


def test_upload_image_then_reject_on_plain_model(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("upload-flow")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    tid = thread["thread_id"]
    up = client.post(
        f"/api/chat/threads/{tid}/attachments",
        files={"file": ("tiny.png", PNG, "image/png")},
        cookies=cookies,
    )
    assert up.status_code == 200, up.text
    aid = up.json()["attachment_id"]
    res = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={"message": "what is this?", "attachment_ids": [aid]},
        cookies=cookies,
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "model_no_vision"


def test_muse_accepts_image_without_vision_error(live_client) -> None:
    from app.services.model_registry import supports_vision

    assert supports_vision("muse-spark-1.3") is True
    assert supports_vision("deepseek-v4-flash-vision-exp") is True
    assert supports_vision("deepseek-v4-flash") is False
    client, created, signup = live_client
    cookies = signup("muse-vision")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    tid = thread["thread_id"]
    up = client.post(
        f"/api/chat/threads/{tid}/attachments",
        files={"file": ("tiny.png", PNG, "image/png")},
        cookies=cookies,
    ).json()
    res = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={
            "message": "what is this?",
            "model": "muse-spark-1.3",
            "attachment_ids": [up["attachment_id"]],
        },
        cookies=cookies,
    )
    assert res.status_code == 200, res.text


def test_upload_rejects_non_image(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("upload-bad")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    res = client.post(
        f"/api/chat/threads/{thread['thread_id']}/attachments",
        files={"file": ("note.txt", b"hello", "text/plain")},
        cookies=cookies,
    )
    assert res.status_code == 422


def test_vision_turn_accepts_image(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("vision-turn")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    tid = thread["thread_id"]
    up = client.post(
        f"/api/chat/threads/{tid}/attachments",
        files={"file": ("tiny.png", PNG, "image/png")},
        cookies=cookies,
    ).json()
    res = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={
            "message": "what is this?",
            "model": "deepseek-v4-flash-vision-exp",
            "attachment_ids": [up["attachment_id"]],
        },
        cookies=cookies,
    )
    assert res.status_code == 200, res.text
    assert res.json()["attachments"][0]["attachment_id"] == up["attachment_id"]


def test_login_throttle_after_fails(live_client) -> None:
    client, _, _ = live_client
    email = f"throttle-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/signup",
        json={"email": email, "password": "password123"},
    )
    for _ in range(5):
        res = client.post(
            "/api/auth/login",
            json={"email": email, "password": "wrong-wrong-wrong"},
        )
        assert res.status_code == 401
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": "wrong-wrong-wrong"},
    )
    assert res.status_code == 429
    assert res.json()["error"]["code"] == "rate_limited"
    auth_service_mod._LOGIN_FAILS.pop(email, None)
