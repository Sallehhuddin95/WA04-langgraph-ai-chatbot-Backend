"""Auth flow tests. Signup, login, logout, me, and chat guard."""

from __future__ import annotations


def test_signup_sets_session_cookie(live_client) -> None:
    client, _, signup = live_client
    cookies = signup("flow-signup")
    assert cookies["session"]
    me = client.get("/api/auth/me", cookies=cookies).json()
    assert me["email"].startswith("progress-flow-signup-")


def test_signup_duplicate_email_conflicts(live_client) -> None:
    client, _, _ = live_client
    import uuid

    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    first = client.post(
        "/api/auth/signup",
        json={"email": email, "password": "password123"},
    )
    assert first.status_code == 201
    second = client.post(
        "/api/auth/signup",
        json={"email": email, "password": "password123"},
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "conflict"


def test_login_round_trip(live_client) -> None:
    client, _, _ = live_client
    import uuid

    email = f"login-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/signup",
        json={"email": email, "password": "password123"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert res.status_code == 200
    assert res.cookies.get("session")
    assert res.json()["email"] == email


def test_login_wrong_password_is_401(live_client) -> None:
    client, _, _ = live_client
    import uuid

    email = f"wrong-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/signup",
        json={"email": email, "password": "password123"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": "nope-nope-nope"},
    )
    assert res.status_code == 401
    res = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "nope-nope-nope"},
    )
    assert res.status_code == 401


def test_me_without_cookie_is_401(live_client) -> None:
    client, _, _ = live_client
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_logout_clears_session(live_client) -> None:
    client, _, signup = live_client
    cookies = signup("flow-logout")
    assert client.get("/api/auth/me", cookies=cookies).status_code == 200
    res = client.post("/api/auth/logout", cookies=cookies)
    assert res.status_code == 200
    assert client.get("/api/auth/me", cookies=cookies).status_code == 401


def test_chat_end_to_end_with_real_session(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("flow-chat")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    turn = client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "hi"},
        cookies=cookies,
    ).json()
    assert turn["reply_text"]
    page = client.get(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        cookies=cookies,
    ).json()
    assert len(page["items"]) == 2
