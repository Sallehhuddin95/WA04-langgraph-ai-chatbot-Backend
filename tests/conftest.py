"""Shared fixtures. LLM keys stripped, live DB gated with cleanup."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

import app.services.chat_service as chat_service_mod
from app.core.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def _no_llm_keys(monkeypatch: pytest.MonkeyPatch):
    """Force the mock model path so tests never depend on funds."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _db_url() -> str:
    return os.getenv("DATABASE_URL", "")


def _db_reachable(url: str) -> bool:
    if not url:
        return False
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


@pytest.fixture()
def live_client():
    url = _db_url()
    if not _db_reachable(url):
        pytest.skip("live Postgres not reachable")
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    from app.repositories.conversation_repository import (
        ConversationRepository,
    )

    chat_service_mod._TURN_HITS.clear()
    chat_service_mod._THREAD_HITS.clear()
    from app.services import auth_service as auth_service_mod

    auth_service_mod._LOGIN_FAILS.clear()
    created: list[str] = []
    client = TestClient(create_app())

    def signup(tag: str, password: str = "password123") -> dict:
        email = f"progress-{tag}-{uuid.uuid4().hex[:8]}@example.com"
        res = client.post(
            "/api/auth/signup",
            json={"email": email, "password": password},
        )
        assert res.status_code == 201, res.text
        return {"session": res.cookies.get("session")}

    yield client, created, signup

    engine = create_engine(url)
    session = sessionmaker(bind=engine)()
    try:
        repo = ConversationRepository(session)
        for thread_id in created:
            repo.delete_thread(uuid.UUID(thread_id))
        session.execute(
            text(
                "DELETE FROM users "
                "WHERE email LIKE 'progress-%@example.com'"
            )
        )
        session.commit()
    finally:
        session.close()
        engine.dispose()
    chat_service_mod._TURN_HITS.clear()
    chat_service_mod._THREAD_HITS.clear()
    from app.services import auth_service as auth_service_mod

    auth_service_mod._LOGIN_FAILS.clear()
