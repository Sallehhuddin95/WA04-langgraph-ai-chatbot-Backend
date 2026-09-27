"""Rename, pin, unpin, and reorder tests. Cap is 5."""

from __future__ import annotations


def _two_threads(live_client, tag: str):
    client, created, signup = live_client
    cookies = signup(tag)
    first = client.post(
        "/api/chat/threads", json={"title": "a"}, cookies=cookies
    ).json()
    second = client.post(
        "/api/chat/threads", json={"title": "b"}, cookies=cookies
    ).json()
    created.extend([first["thread_id"], second["thread_id"]])
    return client, created, cookies, first["thread_id"], second["thread_id"]


def test_rename_thread(live_client) -> None:
    client, _, cookies, tid, _ = _two_threads(live_client, "rename")
    res = client.patch(
        f"/api/chat/threads/{tid}", json={"title": "renamed"}, cookies=cookies
    )
    assert res.status_code == 200
    assert res.json()["title"] == "renamed"
    assert (
        client.patch(
            f"/api/chat/threads/{tid}", json={"title": ""}, cookies=cookies
        ).status_code
        == 422
    )


def test_pin_orders_first(live_client) -> None:
    client, _, cookies, first, second = _two_threads(live_client, "pin")
    assert (
        client.post(
            f"/api/chat/threads/{first}/pin", json={}, cookies=cookies
        ).status_code
        == 200
    )
    ids = [
        row["thread_id"]
        for row in client.get("/api/chat/threads", cookies=cookies).json()[
            "threads"
        ]
    ]
    assert ids[0] == first
    assert ids[1] == second


def test_pin_cap_is_five(live_client) -> None:
    client, created, signup = live_client
    cookies = signup("pin-cap")
    ids = []
    for index in range(6):
        thread = client.post(
            "/api/chat/threads",
            json={"title": f"t{index}"},
            cookies=cookies,
        ).json()
        ids.append(thread["thread_id"])
    created.extend(ids)
    for tid in ids[:5]:
        assert (
            client.post(
                f"/api/chat/threads/{tid}/pin", json={}, cookies=cookies
            ).status_code
            == 200
        )
    sixth = client.post(
        f"/api/chat/threads/{ids[5]}/pin", json={}, cookies=cookies
    )
    assert sixth.status_code == 409
    assert sixth.json()["error"]["code"] == "pin_limit"


def test_unpin_and_reorder(live_client) -> None:
    client, _, cookies, first, second = _two_threads(live_client, "reorder")
    client.post(f"/api/chat/threads/{first}/pin", json={}, cookies=cookies)
    client.post(f"/api/chat/threads/{second}/pin", json={}, cookies=cookies)
    res = client.post(
        "/api/chat/threads/reorder",
        json={"thread_ids": [second, first]},
        cookies=cookies,
    )
    assert res.status_code == 200
    ids = [
        row["thread_id"]
        for row in client.get("/api/chat/threads", cookies=cookies).json()[
            "threads"
        ]
    ]
    assert ids[:2] == [second, first]
    assert (
        client.post(
            f"/api/chat/threads/{first}/unpin", json={}, cookies=cookies
        ).status_code
        == 200
    )
    ids = [
        row["thread_id"]
        for row in client.get("/api/chat/threads", cookies=cookies).json()[
            "threads"
        ]
    ]
    assert ids[0] == second
    assert ids[1] == first


def test_reorder_rejects_partial_set(live_client) -> None:
    client, _, cookies, first, second = _two_threads(
        live_client, "reorder-bad"
    )
    client.post(f"/api/chat/threads/{first}/pin", json={}, cookies=cookies)
    client.post(f"/api/chat/threads/{second}/pin", json={}, cookies=cookies)
    res = client.post(
        "/api/chat/threads/reorder",
        json={"thread_ids": [second]},
        cookies=cookies,
    )
    assert res.status_code == 422
