"""Maintenance jobs. Purge timing, session cleanup, soft-delete purge."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services.maintenance import (
    PURGE_WARNING_DAYS,
    THREAD_PURGE_DAYS,
    list_purge_reminders,
    purge_info,
)


def test_purge_info_marks_reminder_window() -> None:
    now = datetime.now(timezone.utc)
    recent = now - timedelta(days=THREAD_PURGE_DAYS - 2)
    info = purge_info(recent, now)
    assert info is not None
    assert info["days_remaining"] == 2
    assert info["needs_reminder"] is True
    assert info["is_overdue"] is False


def test_purge_info_no_reminder_when_far_out() -> None:
    now = datetime.now(timezone.utc)
    recent = now - timedelta(days=1)
    info = purge_info(recent, now)
    assert info is not None
    assert info["needs_reminder"] is False
    assert info["days_remaining"] > PURGE_WARNING_DAYS


def test_purge_info_overdue() -> None:
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=THREAD_PURGE_DAYS + 1)
    info = purge_info(old, now)
    assert info is not None
    assert info["is_overdue"] is True
    assert info["days_remaining"] == 0


def test_delete_returns_purge_date(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("purge-date")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    tid = thread["thread_id"]
    created.append(tid)
    res = client.delete(f"/api/chat/threads/{tid}", cookies=cookies)
    assert res.status_code == 200
    body = res.json()
    assert body["thread_id"] == tid
    assert body["purge_at"] is not None
    assert body["days_remaining"] == THREAD_PURGE_DAYS
    # Restore so the live cleanup fixture stays simple.
    client.post(f"/api/chat/threads/{tid}/restore", cookies=cookies)


def test_deleted_list_and_reminders(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("purge-list")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    tid = thread["thread_id"]
    created.append(tid)
    client.delete(f"/api/chat/threads/{tid}", cookies=cookies)
    listed = client.get("/api/chat/threads/deleted/list", cookies=cookies)
    assert listed.status_code == 200
    ids = [row["thread_id"] for row in listed.json()["threads"]]
    assert tid in ids
    reminders = client.get(
        "/api/chat/threads/purge-reminders/list", cookies=cookies
    )
    assert reminders.status_code == 200
    # Fresh delete is 30 days out, so no 3-day reminder yet.
    assert all(
        row["needs_reminder"] is False
        for row in reminders.json()["threads"]
    )
    assert list_purge_reminders.__name__ == "list_purge_reminders"
    client.post(f"/api/chat/threads/{tid}/restore", cookies=cookies)
