"""Postgres checkpoints. Memory fallback plus live resume."""

from __future__ import annotations

import uuid

from app.repositories.checkpoint_adapter import CheckpointAdapter


def test_memory_save_and_load_round_trip() -> None:
    adapter = CheckpointAdapter()
    tid = uuid.uuid4()
    adapter.save(tid, {"thread_id": str(tid), "is_grounded": True})
    loaded = adapter.load_latest(tid)
    assert loaded is not None
    assert loaded["is_grounded"] is True


def test_prune_keeps_policy_shape() -> None:
    adapter = CheckpointAdapter()
    tid = uuid.uuid4()
    adapter.save(tid, {"thread_id": str(tid)})
    adapter.prune(tid, keep_last=50)
    assert adapter.load_latest(tid) is None


def test_live_checkpoint_resume(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("checkpoint")
    thread = client.post(
        "/api/chat/threads", json={"title": "t"}, cookies=cookies
    ).json()
    tid = thread["thread_id"]
    created.append(tid)
    turn = client.post(
        f"/api/chat/threads/{tid}/turns",
        json={"message": "hi"},
        cookies=cookies,
    )
    assert turn.status_code == 200
    res = client.get(
        f"/api/chat/threads/{tid}/checkpoint", cookies=cookies
    )
    assert res.status_code == 200
    body = res.json()
    assert body["thread_id"] == tid
    assert body["trace_id"] is not None
