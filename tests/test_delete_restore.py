"""Delete plus 10-second undo tests for threads and messages."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def _thread_with_turn(live_client, tag: str):
    client, created, signup = live_client
    cookies = signup(tag)
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    created.append(thread["thread_id"])
    turn = client.post(
        f"/api/chat/threads/{thread['thread_id']}/turns",
        json={"message": "hi there"},
        cookies=cookies,
    ).json()
    return client, created, cookies, thread["thread_id"], turn["turn_id"]


def test_delete_thread_hides_it_from_list(live_client) -> None:
    client, created, cookies, tid, _ = _thread_with_turn(
        live_client, "del-thread"
    )
    assert client.delete(
        f"/api/chat/threads/{tid}", cookies=cookies
    ).status_code == 200
    ids = [
        row["thread_id"]
        for row in client.get("/api/chat/threads", cookies=cookies).json()[
            "threads"
        ]
    ]
    assert tid not in ids
    assert (
        client.get(f"/api/chat/threads/{tid}/turns", cookies=cookies)
    ).status_code == 404


def test_restore_thread_within_window(live_client) -> None:
    client, created, cookies, tid, _ = _thread_with_turn(
        live_client, "restore-thread"
    )
    client.delete(f"/api/chat/threads/{tid}", cookies=cookies)
    res = client.post(f"/api/chat/threads/{tid}/restore", cookies=cookies)
    assert res.status_code == 200
    page = client.get(
        f"/api/chat/threads/{tid}/turns", cookies=cookies
    ).json()
    assert len(page["items"]) == 2


def test_restore_thread_after_window_is_gone(live_client) -> None:
    client, created, cookies, tid, _ = _thread_with_turn(
        live_client, "restore-late"
    )
    client.delete(f"/api/chat/threads/{tid}", cookies=cookies)
    engine = create_engine(os.getenv("DATABASE_URL", ""))
    session = sessionmaker(bind=engine)()
    try:
        old = datetime.now(timezone.utc) - timedelta(seconds=11)
        session.execute(
            text("UPDATE threads SET deleted_at = :old WHERE id = :tid"),
            {"old": old, "tid": str(uuid.UUID(tid))},
        )
        session.commit()
    finally:
        session.close()
        engine.dispose()
    res = client.post(f"/api/chat/threads/{tid}/restore", cookies=cookies)
    assert res.status_code == 410
    assert res.json()["error"]["code"] == "gone"


def test_delete_message_keeps_sibling(live_client) -> None:
    client, created, cookies, tid, turn_id = _thread_with_turn(
        live_client, "del-message"
    )
    page = client.get(
        f"/api/chat/threads/{tid}/turns", cookies=cookies
    ).json()
    user_row = [item for item in page["items"] if item["role"] == "user"][0]
    assert (
        client.delete(
            f"/api/chat/threads/{tid}/turns/{user_row['turn_id']}",
            cookies=cookies,
        ).status_code
        == 200
    )
    rest = client.get(
        f"/api/chat/threads/{tid}/turns", cookies=cookies
    ).json()["items"]
    assert [item["turn_id"] for item in rest] == [turn_id]
    assert (
        client.post(
            f"/api/chat/threads/{tid}/turns/{user_row['turn_id']}/restore",
            cookies=cookies,
        ).status_code
        == 200
    )
    full = client.get(
        f"/api/chat/threads/{tid}/turns", cookies=cookies
    ).json()["items"]
    assert len(full) == 2


def test_delete_missing_is_404(live_client) -> None:
    client, _, signup = live_client
    cookies = signup("del-missing")
    missing = uuid.uuid4()
    assert (
        client.delete(
            f"/api/chat/threads/{missing}", cookies=cookies
        ).status_code
        == 404
    )
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    assert (
        client.delete(
            f"/api/chat/threads/{thread['thread_id']}/turns/{missing}",
            cookies=cookies,
        ).status_code
        == 404
    )
