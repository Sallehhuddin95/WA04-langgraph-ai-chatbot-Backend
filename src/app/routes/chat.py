"""Chat routes. Thin HTTP entry, no business rules."""

from __future__ import annotations

import json
import uuid
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, File, Header, Query, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attachments import MAX_ATTACHMENT_BYTES
from app.repositories.attachment_repository import AttachmentRepository
from app.schemas.chat import (
    CheckpointResponse,
    CreateThreadRequest,
    CreateThreadResponse,
    CreateTurnRequest,
    CreateTurnResponse,
    DeletedThreadInfo,
    DeleteThreadResponse,
    ListDeletedThreadsResponse,
    ListThreadsResponse,
    ListTurnsResponse,
    PinThreadRequest,
    RenameThreadRequest,
    ReorderPinsRequest,
    ThreadSummary,
    TurnItem,
    UploadAttachmentResponse,
)
from app.services import auth_service
from app.services.auth_service import SESSION_COOKIE_NAME
from app.services.chat_service import ChatError, DbChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _error(
    code: str,
    message: str,
    status_code: int,
    trace_id: UUID,
    retry_after: int | None = None,
) -> JSONResponse:
    headers = {"Retry-After": str(retry_after)} if retry_after is not None else None
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "trace_id": str(trace_id)}},
        headers=headers,
    )


def _from_service_error(exc: ChatError) -> JSONResponse:
    return _error(
        exc.code, exc.message, exc.status_code, exc.trace_id, exc.retry_after
    )


def _parse_idempotency(header_value: str | None, body_value: UUID | None) -> UUID | None:
    """Header wins over body per chat-api spec. Bad header is a 422."""
    if header_value is not None:
        try:
            return UUID(header_value)
        except ValueError as exc:
            raise ChatError("validation_failed", "bad idempotency key", 422) from exc
    return body_value


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/threads", status_code=200, response_model=ListThreadsResponse)
def list_threads(
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        page = DbChatService(db).list_threads(owner_id)
        return ListThreadsResponse(
            threads=[ThreadSummary(**item) for item in page["threads"]]
        )
    except ChatError as exc:
        return _from_service_error(exc)


@router.post("/threads/reorder", status_code=200)
def reorder_pins(
    body: ReorderPinsRequest,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        result = DbChatService(db).reorder_pins(
            owner_id, list(body.thread_ids)
        )
        return {"thread_ids": [str(tid) for tid in result["thread_ids"]]}
    except ChatError as exc:
        return _from_service_error(exc)


@router.patch(
    "/threads/{thread_id}", status_code=200, response_model=ThreadSummary
)
def rename_thread(
    thread_id: UUID,
    body: RenameThreadRequest,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        updated = DbChatService(db).rename_thread(
            owner_id, thread_id, body.title.strip()
        )
        return ThreadSummary(**updated)
    except ChatError as exc:
        return _from_service_error(exc)


@router.post("/threads/{thread_id}/pin", status_code=200)
def pin_thread(
    thread_id: UUID,
    body: PinThreadRequest,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        result = DbChatService(db).pin_thread(
            owner_id, thread_id, body.position
        )
        return {"thread_id": str(result["thread_id"])}
    except ChatError as exc:
        return _from_service_error(exc)


@router.post("/threads/{thread_id}/unpin", status_code=200)
def unpin_thread(
    thread_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        result = DbChatService(db).unpin_thread(owner_id, thread_id)
        return {"thread_id": str(result["thread_id"])}
    except ChatError as exc:
        return _from_service_error(exc)


@router.post("/threads", status_code=200, response_model=CreateThreadResponse)
def create_thread(
    body: CreateThreadRequest,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        created = DbChatService(db).create_thread(owner_id, body.title)
        return CreateThreadResponse(**created)
    except ChatError as exc:
        return _from_service_error(exc)


@router.post("/threads/{thread_id}/turns", status_code=200, response_model=CreateTurnResponse)
def create_turn(
    thread_id: UUID,
    body: CreateTurnRequest,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        key = _parse_idempotency(idempotency_key, body.idempotency_key)
        result = DbChatService(db).create_turn(
            owner_id,
            thread_id,
            body.message,
            key,
            model=body.model,
            attachment_ids=list(body.attachment_ids),
        )
        return CreateTurnResponse(**result)
    except ChatError as exc:
        return _from_service_error(exc)


@router.get("/threads/{thread_id}/turns", status_code=200, response_model=ListTurnsResponse)
def list_turns(
    thread_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    cursor: Annotated[str | None, Query()] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        page = DbChatService(db).list_turns(owner_id, thread_id, limit, cursor)
        return ListTurnsResponse(
            items=[TurnItem(**item) for item in page["items"]],
            next_cursor=page["next_cursor"],
        )
    except ChatError as exc:
        return _from_service_error(exc)


@router.post(
    "/threads/{thread_id}/attachments",
    status_code=200,
    response_model=UploadAttachmentResponse,
)
def upload_attachment(
    thread_id: UUID,
    file: Annotated[UploadFile, File()],
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        service = DbChatService(db)
        service._owned_thread(owner_id, thread_id)
        data = file.file.read()
        mime = file.content_type or "application/octet-stream"
        if not mime.startswith("image/"):
            raise ChatError(
                "validation_failed",
                "only image uploads are supported",
                422,
            )
        if len(data) == 0 or len(data) > MAX_ATTACHMENT_BYTES:
            raise ChatError(
                "validation_failed",
                "image must be non-empty and under 5MB",
                422,
            )
        row = AttachmentRepository(db).create(
            thread_id, file.filename or "image", mime, data
        )
        db.commit()
        return UploadAttachmentResponse(
            attachment_id=row.id,
            filename=row.filename,
            mime=row.mime,
            size=row.size,
        )
    except ChatError as exc:
        db.rollback()
        return _from_service_error(exc)


@router.get(
    "/threads/deleted/list",
    status_code=200,
    response_model=ListDeletedThreadsResponse,
)
def list_deleted_threads(
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    """Soft-deleted threads with purge timing and 3-day reminder flag."""
    from app.services import maintenance as maintenance_service

    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        items = maintenance_service.list_deleted_threads(db, owner_id)
        return ListDeletedThreadsResponse(
            threads=[DeletedThreadInfo(**item) for item in items]
        )
    except ChatError as exc:
        return _from_service_error(exc)


@router.get(
    "/threads/purge-reminders/list",
    status_code=200,
    response_model=ListDeletedThreadsResponse,
)
def list_purge_reminders(
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    """Threads within 3 days of permanent deletion."""
    from app.services import maintenance as maintenance_service

    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        items = maintenance_service.list_purge_reminders(db, owner_id)
        return ListDeletedThreadsResponse(
            threads=[DeletedThreadInfo(**item) for item in items]
        )
    except ChatError as exc:
        return _from_service_error(exc)


@router.delete(
    "/threads/{thread_id}", status_code=200, response_model=DeleteThreadResponse
)
def delete_thread(
    thread_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        result = DbChatService(db).delete_thread(owner_id, thread_id)
        return DeleteThreadResponse(**result)
    except ChatError as exc:
        return _from_service_error(exc)


@router.post("/threads/{thread_id}/restore", status_code=200)
def restore_thread(
    thread_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        result = DbChatService(db).restore_thread(owner_id, thread_id)
        return {"thread_id": str(result["thread_id"])}
    except ChatError as exc:
        return _from_service_error(exc)


@router.delete(
    "/threads/{thread_id}/turns/{turn_id}", status_code=200
)
def delete_message(
    thread_id: UUID,
    turn_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        result = DbChatService(db).delete_message(
            owner_id, thread_id, turn_id
        )
        return {"turn_id": str(result["turn_id"])}
    except ChatError as exc:
        return _from_service_error(exc)


@router.post(
    "/threads/{thread_id}/turns/{turn_id}/restore", status_code=200
)
def restore_message(
    thread_id: UUID,
    turn_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        result = DbChatService(db).restore_message(
            owner_id, thread_id, turn_id
        )
        return {"turn_id": str(result["turn_id"])}
    except ChatError as exc:
        return _from_service_error(exc)


@router.get(
    "/threads/{thread_id}/checkpoint",
    status_code=200,
    response_model=CheckpointResponse | None,
)
def get_checkpoint(
    thread_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    """Latest graph checkpoint for resume after restart."""
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        saved = DbChatService(db).get_checkpoint(owner_id, thread_id)
        if saved is None:
            return None
        return CheckpointResponse(
            thread_id=thread_id,
            trace_id=saved.get("trace_id"),
            intent_category=saved.get("intent_category"),
            is_grounded=saved.get("is_grounded"),
        )
    except ChatError as exc:
        return _from_service_error(exc)


@router.post("/maintenance/run", status_code=200)
def run_maintenance_job(
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    """Run session cleanup plus soft-delete purge. Returns counts."""
    from app.services import maintenance as maintenance_service

    try:
        auth_service.resolve_owner_id(db, session)
        return maintenance_service.run_maintenance(db)
    except ChatError as exc:
        return _from_service_error(exc)


@router.get("/threads/{thread_id}/turns/{turn_id}/stream")
def stream_turn(
    thread_id: UUID,
    turn_id: UUID,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    db: Session = Depends(get_db),
):
    try:
        owner_id = auth_service.resolve_owner_id(db, session)
        turn = DbChatService(db).get_turn(owner_id, thread_id, turn_id)
    except ChatError as exc:
        return _from_service_error(exc)

    trace_id = turn.trace_id or uuid.uuid4()

    def event_stream():
        text = turn.text or ""
        words = text.split(" ") if text else [""]
        for index, word in enumerate(words):
            piece = word if index == len(words) - 1 else word + " "
            payload = {"turn_id": str(turn_id), "trace_id": str(trace_id), "delta": piece}
            yield f"event: delta\ndata: {json.dumps(payload)}\n\n"
        for item in turn.citations or []:
            yield f"event: citation\ndata: {json.dumps(item)}\n\n"
        done = {
            "turn_id": str(turn_id),
            "trace_id": str(trace_id),
            "intent_category": turn.intent_category or "rag_search",
            "is_grounded": bool(turn.is_grounded),
        }
        yield f"event: done\ndata: {json.dumps(done)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
