"""Auth routes. Signup, login, logout, and current user."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AuthUserResponse, LoginRequest, SignupRequest
from app.services import auth_service
from app.services.auth_service import SESSION_COOKIE_NAME
from app.services.chat_service import ChatError

router = APIRouter(prefix="/api/auth", tags=["auth"])

_COOKIE_KWARGS = {
    "key": SESSION_COOKIE_NAME,
    "httponly": True,
    "samesite": "lax",
    "secure": False,  # Local http dev. Production must flip to True.
    "path": "/",
    "max_age": 30 * 24 * 3600,
}


def _auth_error(exc: ChatError) -> JSONResponse:
    headers = (
        {"Retry-After": str(exc.retry_after)}
        if exc.retry_after is not None
        else None
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "trace_id": str(exc.trace_id),
            }
        },
        headers=headers,
    )


@router.post("/signup", status_code=201)
def signup(
    body: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user, token = auth_service.signup(
            db, str(body.email), body.password
        )
    except ChatError as exc:
        return _auth_error(exc)
    response.set_cookie(value=token, **_COOKIE_KWARGS)
    return AuthUserResponse(**user)


@router.post("/login", status_code=200)
def login(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user, token = auth_service.login(db, str(body.email), body.password)
    except ChatError as exc:
        return _auth_error(exc)
    response.set_cookie(value=token, **_COOKIE_KWARGS)
    return AuthUserResponse(**user)


@router.post("/logout", status_code=200)
def logout(
    response: Response,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    auth_service.logout(db, session)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return {"status": "ok"}


@router.get("/me", status_code=200)
def me(
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    user = auth_service.get_current_user(db, session)
    if user is None:
        return _auth_error(
            ChatError("unauthorized", "missing or expired session", 401)
        )
    return AuthUserResponse(user_id=user.id, email=user.email)
