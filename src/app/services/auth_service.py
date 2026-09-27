"""Auth service. Owns users, password checks, and cookie sessions.

Passwords hash with bcrypt. Session cookies carry random tokens;
only SHA256 hashes persist. Raw tokens never hit logs.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sessions import UserSession
from app.models.users import User
from app.services.chat_service import ChatError

SESSION_COOKIE_NAME = "session"
SESSION_DAYS = 30

_LOGIN_FAILS: dict[str, list[float]] = {}
LOGIN_MAX_FAILS = 5
LOGIN_WINDOW_SECONDS = 600.0


def _login_allowed(email: str) -> bool:
    import time

    now = time.monotonic()
    hits = _LOGIN_FAILS.setdefault(email, [])
    fresh = [hit for hit in hits if now - hit < LOGIN_WINDOW_SECONDS]
    hits[:] = fresh
    return len(fresh) < LOGIN_MAX_FAILS


def _login_retry_after(email: str) -> int:
    import math
    import time

    now = time.monotonic()
    hits = _LOGIN_FAILS.get(email, [])
    fresh = [hit for hit in hits if now - hit < LOGIN_WINDOW_SECONDS]
    if not fresh:
        return 1
    oldest = min(fresh)
    return max(1, int(math.ceil(oldest + LOGIN_WINDOW_SECONDS - now)))


def _record_login_fail(email: str) -> None:
    import time

    _LOGIN_FAILS.setdefault(email, []).append(time.monotonic())


def _norm_email(email: str) -> str:
    return email.strip().lower()


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def _new_session(db: Session, user_id: UUID) -> str:
    raw = secrets.token_urlsafe(32)
    db.add(
        UserSession(
            user_id=user_id,
            token_hash=_hash_token(raw),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=SESSION_DAYS),
        )
    )
    db.flush()
    return raw


def signup(db: Session, email: str, password: str) -> tuple[dict, str]:
    address = _norm_email(email)
    exists = db.execute(
        select(User).where(User.email == address).limit(1)
    ).scalars().first()
    if exists is not None:
        raise ChatError("conflict", "email already registered", 409)
    user = User(email=address, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    token = _new_session(db, user.id)
    db.commit()
    return {"user_id": user.id, "email": user.email}, token


def login(db: Session, email: str, password: str) -> tuple[dict, str]:
    address = _norm_email(email)
    if not _login_allowed(address):
        raise ChatError(
            "rate_limited",
            "too many attempts, retry later",
            429,
            retry_after=_login_retry_after(address),
        )
    user = db.execute(
        select(User).where(User.email == address).limit(1)
    ).scalars().first()
    if user is None or not verify_password(password, user.password_hash):
        _record_login_fail(address)
        raise ChatError("unauthorized", "invalid email or password", 401)
    _LOGIN_FAILS.pop(address, None)
    token = _new_session(db, user.id)
    db.commit()
    return {"user_id": user.id, "email": user.email}, token


def logout(db: Session, raw_token: str | None) -> None:
    if not raw_token:
        return
    row = db.execute(
        select(UserSession)
        .where(UserSession.token_hash == _hash_token(raw_token))
        .limit(1)
    ).scalars().first()
    if row is not None:
        db.delete(row)
        db.commit()


def get_current_user(db: Session, raw_token: str | None) -> User | None:
    if not raw_token:
        return None
    row = db.execute(
        select(UserSession)
        .where(UserSession.token_hash == _hash_token(raw_token))
        .limit(1)
    ).scalars().first()
    if row is None or row.expires_at <= datetime.now(timezone.utc):
        return None
    return db.get(User, row.user_id)


def resolve_owner_id(db: Session, raw_token: str | None) -> UUID:
    """Map the session cookie to a user id. Raises 401 when invalid."""
    user = get_current_user(db, raw_token)
    if user is None:
        raise ChatError("unauthorized", "missing or expired session", 401)
    return user.id
