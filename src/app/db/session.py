"""Engine and session helpers. No connect at import time."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_session_factory: sessionmaker | None = None


def get_session_factory() -> sessionmaker:
    global _session_factory
    if _session_factory is None:
        settings = get_settings()
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is not set")
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        _session_factory = sessionmaker(
            bind=engine, autoflush=False, expire_on_commit=False
        )
    return _session_factory


def get_db() -> Iterator[Session]:
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()
