"""Chat service. Owns ownership checks, idempotency, and graph runs.

Routes stay thin: they resolve the session cookie to an owner id and
delegate here. Owner ids come from the session stub, thread ownership
is verified per call, and idempotent retries return the first result.
"""

from __future__ import annotations

import base64
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.messages import Message
from app.models.threads import Thread
from app.repositories.checkpoint_adapter import CheckpointAdapter
from app.repositories.conversation_repository import ConversationRepository
from app.services.graph.graph import run_turn
from app.services.graph.state import ChatState

SESSION_COOKIE_NAME = "session"

TURN_RATE_LIMIT = 60
THREAD_RATE_LIMIT = 10
RATE_WINDOW_SECONDS = 60.0


class ChatError(Exception):
    """Service failure with an API error code and HTTP status."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        trace_id: UUID | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.trace_id = trace_id or uuid.uuid4()
        self.retry_after = retry_after


def _retry_after_for(hits: list[float], now: float, window: float) -> int:
    """Seconds until the oldest hit leaves the window. At least 1."""
    import math

    if not hits:
        return 1
    oldest = min(hits)
    remaining = oldest + window - now
    return max(1, int(math.ceil(remaining)))


@dataclass
class StoredThread:
    thread_id: UUID
    owner_id: UUID
    title: str | None
    created_at: datetime


@dataclass
class StoredTurn:
    turn_id: UUID
    thread_id: UUID
    role: str
    text: str
    intent_category: str | None = None
    is_grounded: bool | None = None
    trace_id: UUID | None = None
    citations: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ChatService:
    """In-memory chat store plus graph invocation."""

    threads: dict[str, StoredThread] = field(default_factory=dict)
    turns: dict[str, list[StoredTurn]] = field(default_factory=dict)
    idempotency: dict[str, dict] = field(default_factory=dict)
    checkpoints: CheckpointAdapter = field(default_factory=CheckpointAdapter)
    turn_hits: dict[str, list[float]] = field(default_factory=dict)
    thread_hits: dict[str, list[float]] = field(default_factory=dict)

    def reset(self) -> None:
        self.threads.clear()
        self.turns.clear()
        self.idempotency.clear()
        self.turn_hits.clear()
        self.thread_hits.clear()
        self.checkpoints.clear()

    def _check_rate(self, owner_id: UUID, kind: str) -> None:
        now = time.monotonic()
        if kind == "turn":
            hits = self.turn_hits.setdefault(str(owner_id), [])
            limit = TURN_RATE_LIMIT
        else:
            hits = self.thread_hits.setdefault(str(owner_id), [])
            limit = THREAD_RATE_LIMIT
        fresh = [hit for hit in hits if now - hit < RATE_WINDOW_SECONDS]
        hits[:] = fresh
        if len(fresh) >= limit:
            retry_after = _retry_after_for(fresh, now, RATE_WINDOW_SECONDS)
            raise ChatError(
                "rate_limited", "rate limit hit, retry later", 429,
                retry_after=retry_after,
            )
        hits.append(now)

    def _owned_thread(self, owner_id: UUID, thread_id: UUID) -> StoredThread:
        thread = self.threads.get(str(thread_id))
        if thread is None:
            raise ChatError("not_found", "thread not found", 404)
        if thread.owner_id != owner_id:
            raise ChatError("forbidden", "cross-owner access denied", 403)
        return thread

    def create_thread(self, owner_id: UUID, title: str | None) -> dict:
        self._check_rate(owner_id, "thread")
        thread_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        self.threads[str(thread_id)] = StoredThread(
            thread_id=thread_id,
            owner_id=owner_id,
            title=title,
            created_at=now,
        )
        self.turns[str(thread_id)] = []
        return {"thread_id": thread_id, "title": title, "created_at": now}

    def create_turn(
        self,
        owner_id: UUID,
        thread_id: UUID,
        message: str,
        idempotency_key: UUID | None = None,
    ) -> dict:
        thread = self._owned_thread(owner_id, thread_id)
        _ = thread
        self._check_rate(owner_id, "turn")

        if idempotency_key is not None:
            cached = self.idempotency.get(f"{owner_id}:{thread_id}:{idempotency_key}")
            if cached is not None:
                return cached

        trace_id = uuid.uuid4()
        prior = self.turns.get(str(thread_id), [])[-50:]
        state: ChatState = {
            "messages": [
                *({"role": turn.role, "text": turn.text} for turn in prior),
                {"role": "user", "text": message},
            ],
            "thread_id": str(thread_id),
            "trace_id": str(trace_id),
            "retry_count": 0,
        }
        try:
            # TimeoutError maps to 504 so slow models stay explicit.
            outcome = run_turn(state)
        except TimeoutError as exc:
            raise ChatError("model_timeout", f"model timeout: {exc}", 504, trace_id) from exc
        except ChatError:
            raise
        except Exception as exc:
            raise ChatError("model_error", f"model or retriever outage: {exc}", 502, trace_id) from exc

        turn_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        citations = []
        for item in outcome.get("citations") or []:
            citations.append(
                {
                    "chunk_id": UUID(str(item["chunk_id"])),
                    "document_id": UUID(str(item["document_id"])),
                    "quote": str(item["quote"]),
                }
            )
        response = {
            "thread_id": thread_id,
            "turn_id": turn_id,
            "reply_text": str(outcome.get("reply_text", "")),
            "citations": citations,
            "intent_category": str(outcome.get("intent_category", "rag_search")),
            "is_grounded": bool(outcome.get("is_grounded", False)),
            "trace_id": trace_id,
        }

        history = self.turns.setdefault(str(thread_id), [])
        history.append(
            StoredTurn(
                turn_id=uuid.uuid4(),
                thread_id=thread_id,
                role="user",
                text=message,
                trace_id=trace_id,
                created_at=now,
            )
        )
        history.append(
            StoredTurn(
                turn_id=turn_id,
                thread_id=thread_id,
                role="assistant",
                text=response["reply_text"],
                intent_category=response["intent_category"],
                is_grounded=response["is_grounded"],
                trace_id=trace_id,
                citations=[
                    {
                        "chunk_id": str(item["chunk_id"]),
                        "document_id": str(item["document_id"]),
                        "quote": str(item["quote"]),
                    }
                    for item in citations
                ],
                created_at=datetime.now(timezone.utc),
            )
        )
        self.checkpoints.save(
            thread_id,
            {
                "thread_id": str(thread_id),
                "trace_id": str(trace_id),
                "intent_category": response["intent_category"],
                "is_grounded": response["is_grounded"],
                "turn_count": len(history),
            },
        )
        if idempotency_key is not None:
            self.idempotency[f"{owner_id}:{thread_id}:{idempotency_key}"] = response
        return response

    def list_turns(
        self, owner_id: UUID, thread_id: UUID, limit: int = 20, cursor: str | None = None
    ) -> dict:
        self._owned_thread(owner_id, thread_id)
        history = self.turns.get(str(thread_id), [])
        offset = 0
        if cursor is not None:
            try:
                offset = int(base64.urlsafe_b64decode(cursor.encode()).decode())
            except Exception as exc:
                raise ChatError("bad_request", "bad cursor", 400) from exc
            if offset < 0 or offset > len(history):
                raise ChatError("bad_request", "bad cursor", 400)
        page = history[offset : offset + limit]
        items = [
            {
                "turn_id": turn.turn_id,
                "role": turn.role,
                "text": turn.text,
                "intent_category": turn.intent_category,
                "is_grounded": turn.is_grounded,
                "trace_id": turn.trace_id,
                "created_at": turn.created_at,
            }
            for turn in page
        ]
        next_offset = offset + len(page)
        next_cursor = None
        if next_offset < len(history):
            next_cursor = base64.urlsafe_b64encode(str(next_offset).encode()).decode()
        return {"items": items, "next_cursor": next_cursor}

    def get_turn(self, owner_id: UUID, thread_id: UUID, turn_id: UUID) -> StoredTurn:
        self._owned_thread(owner_id, thread_id)
        for turn in self.turns.get(str(thread_id), []):
            if turn.turn_id == turn_id and turn.role == "assistant":
                return turn
        raise ChatError("not_found", "turn not found", 404)


default_service = ChatService()

# Shared process-local state for request-scoped DB service instances.
_TURN_HITS: dict[str, list[float]] = {}
_THREAD_HITS: dict[str, list[float]] = {}
_shared_checkpoints = CheckpointAdapter()

UNDO_SECONDS = 10


def _undo_open(deleted_at) -> bool:
    from datetime import datetime, timezone

    if deleted_at is None:
        return False
    now = datetime.now(timezone.utc)
    marked = deleted_at
    if marked.tzinfo is None:
        marked = marked.replace(tzinfo=timezone.utc)
    return (now - marked).total_seconds() <= UNDO_SECONDS


def _check_rate_limit(owner_id: UUID, kind: str) -> None:
    now = time.monotonic()
    if kind == "turn":
        hits = _TURN_HITS.setdefault(str(owner_id), [])
        limit = TURN_RATE_LIMIT
    else:
        hits = _THREAD_HITS.setdefault(str(owner_id), [])
        limit = THREAD_RATE_LIMIT
    fresh = [hit for hit in hits if now - hit < RATE_WINDOW_SECONDS]
    hits[:] = fresh
    if len(fresh) >= limit:
        retry_after = _retry_after_for(fresh, now, RATE_WINDOW_SECONDS)
        raise ChatError(
            "rate_limited", "rate limit hit, retry later", 429,
            retry_after=retry_after,
        )
    hits.append(now)


def _row_to_item(row: Message) -> dict:
    return {
        "turn_id": row.id,
        "role": row.role,
        "text": row.text,
        "intent_category": row.intent_category,
        "is_grounded": row.is_grounded,
        "trace_id": row.trace_id,
        "citations": [
            {
                "chunk_id": UUID(str(item["chunk_id"])),
                "document_id": UUID(str(item["document_id"])),
                "quote": str(item["quote"]),
            }
            for item in (row.citations or [])
        ],
        "created_at": row.created_at,
    }


def _row_to_response(thread_id: UUID, row: Message) -> dict:
    return {
        "thread_id": thread_id,
        "turn_id": row.id,
        "reply_text": row.text,
        "citations": [
            {
                "chunk_id": UUID(str(item["chunk_id"])),
                "document_id": UUID(str(item["document_id"])),
                "quote": str(item["quote"]),
            }
            for item in (row.citations or [])
        ],
        "intent_category": str(row.intent_category or "rag_search"),
        "is_grounded": bool(row.is_grounded),
        "trace_id": row.trace_id,
        "attachments": [],
    }


def _data_url(mime: str, data: bytes) -> str:
    import base64

    return f"data:{mime};base64," + base64.b64encode(data).decode()


class DbChatService:
    """Postgres-backed chat service. Routes use one instance per request."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ConversationRepository(db)
        self.checkpoints = _shared_checkpoints

    def _owned_thread(self, owner_id: UUID, thread_id: UUID) -> Thread:
        thread = self.repo.get_thread_any_owner(thread_id)
        if thread is None:
            raise ChatError("not_found", "thread not found", 404)
        if thread.owner_id != owner_id:
            raise ChatError("forbidden", "cross-owner access denied", 403)
        return thread

    def create_thread(self, owner_id: UUID, title: str | None) -> dict:
        _check_rate_limit(owner_id, "thread")
        try:
            row = self.repo.create_thread(owner_id, title)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {
            "thread_id": row.id,
            "title": row.title,
            "created_at": row.created_at,
        }

    def _load_attachments(
        self, thread_id: UUID, attachment_ids: list[UUID]
    ) -> list:
        from app.repositories.attachment_repository import (
            AttachmentRepository,
        )

        try:
            return AttachmentRepository(self.db).list_for_turn(
                thread_id, attachment_ids
            )
        except LookupError as exc:
            raise ChatError("not_found", f"attachment {exc}", 404) from exc
        except PermissionError as exc:
            raise ChatError("forbidden", str(exc), 403) from exc

    def create_turn(
        self,
        owner_id: UUID,
        thread_id: UUID,
        message: str,
        idempotency_key: UUID | None = None,
        model: str = "deepseek-v4-flash",
        attachment_ids: list[UUID] | None = None,
    ) -> dict:
        from datetime import datetime, timezone

        from app.services.model_registry import is_known_model, supports_vision

        if not is_known_model(model):
            raise ChatError(
                "validation_failed", f"unknown model: {model}", 422
            )
        thread = self._owned_thread(owner_id, thread_id)
        _check_rate_limit(owner_id, "turn")

        attachments = self._load_attachments(thread_id, attachment_ids or [])
        if attachments and not supports_vision(model):
            raise ChatError(
                "model_no_vision",
                "this model does not support images",
                422,
            )

        if idempotency_key is not None:
            cached = self.repo.find_turn_by_idempotency_key(
                thread_id, idempotency_key
            )
            if cached is not None:
                response = _row_to_response(thread_id, cached)
                response["attachments"] = [
                    {
                        "attachment_id": row.id,
                        "filename": row.filename,
                        "mime": row.mime,
                    }
                    for row in attachments
                ]
                return response

        trace_id = uuid.uuid4()
        try:
            prior_rows = self.repo.list_recent_messages(thread_id, limit=50)
        except Exception:
            prior_rows = []
        history_messages: list[dict] = [
            {"role": row.role, "text": row.text} for row in prior_rows
        ]
        state: ChatState = {
            "messages": [
                *history_messages,
                {"role": "user", "text": message},
            ],
            "thread_id": str(thread_id),
            "trace_id": str(trace_id),
            "retry_count": 0,
            "model": model,
            "image_urls": [
                _data_url(row.mime, bytes(row.data)) for row in attachments
            ],
        }
        try:
            from app.services.graph.retriever import (
                TOP_K_COMPLEX,
                prefetch_vector_docs,
            )

            prefetched = prefetch_vector_docs(message, TOP_K_COMPLEX, self.db)
            if prefetched is not None:
                state["prefetched_docs"] = prefetched
        except Exception:
            pass
        try:
            outcome = run_turn(state)
        except TimeoutError as exc:
            raise ChatError(
                "model_timeout", f"model timeout: {exc}", 504, trace_id
            ) from exc
        except ChatError:
            raise
        except Exception as exc:
            raise ChatError(
                "model_error",
                f"model or retriever outage: {exc}",
                502,
                trace_id,
            ) from exc

        citations = [
            {
                "chunk_id": str(item["chunk_id"]),
                "document_id": str(item["document_id"]),
                "quote": str(item["quote"]),
            }
            for item in outcome.get("citations") or []
        ]
        try:
            from datetime import datetime, timezone

            self.repo.add_message(thread_id, "user", message, trace_id)
            assistant = self.repo.add_message(
                thread_id,
                "assistant",
                str(outcome.get("reply_text", "")),
                trace_id,
                idempotency_key=idempotency_key,
                intent_category=str(
                    outcome.get("intent_category", "rag_search")
                ),
                is_grounded=bool(outcome.get("is_grounded", False)),
            )
            assistant.citations = citations
            thread.updated_at = datetime.now(timezone.utc)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        checkpoint_state = {
            "thread_id": str(thread_id),
            "trace_id": str(trace_id),
            "intent_category": str(
                outcome.get("intent_category", "rag_search")
            ),
            "is_grounded": bool(outcome.get("is_grounded", False)),
        }
        try:
            self.checkpoints.save_to_db(self.db, thread_id, checkpoint_state)
            self.db.commit()
        except Exception:
            self.db.rollback()
            self.checkpoints.save(thread_id, checkpoint_state)
        response = _row_to_response(thread_id, assistant)
        response["attachments"] = [
            {
                "attachment_id": row.id,
                "filename": row.filename,
                "mime": row.mime,
            }
            for row in attachments
        ]
        return response

    def list_threads(self, owner_id: UUID, limit: int = 50) -> dict:
        rows = self.repo.list_threads(owner_id, limit)
        return {
            "threads": [
                {
                    "thread_id": row.id,
                    "title": row.title,
                    "updated_at": row.updated_at,
                    "is_pinned": bool(row.is_pinned),
                    "pin_order": row.pin_order,
                }
                for row in rows
            ]
        }

    def rename_thread(
        self, owner_id: UUID, thread_id: UUID, title: str
    ) -> dict:
        thread = self._owned_thread(owner_id, thread_id)
        try:
            self.repo.rename_thread(thread_id, title)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {
            "thread_id": thread.id,
            "title": title,
            "updated_at": thread.updated_at,
            "is_pinned": bool(thread.is_pinned),
            "pin_order": thread.pin_order,
        }

    def pin_thread(
        self, owner_id: UUID, thread_id: UUID, position: int | None
    ) -> dict:
        from app.services.pin_rules import MAX_PINS

        thread = self._owned_thread(owner_id, thread_id)
        pinned = [
            row
            for row in self.repo.pinned_threads(owner_id)
            if row.id != thread_id
        ]
        if not thread.is_pinned and len(pinned) >= MAX_PINS:
            raise ChatError("pin_limit", "at most 5 pinned chats", 409)
        slot = len(pinned) if position is None else max(0, min(position, len(pinned)))
        ordered = pinned[:slot] + [thread] + pinned[slot:]
        try:
            for index, row in enumerate(ordered):
                self.repo.set_pin(row.id, True, index)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"thread_id": thread_id}

    def unpin_thread(self, owner_id: UUID, thread_id: UUID) -> dict:
        thread = self._owned_thread(owner_id, thread_id)
        if not thread.is_pinned:
            raise ChatError("not_pinned", "thread is not pinned", 409)
        try:
            self.repo.set_pin(thread_id, False, None)
            rest = [
                row
                for row in self.repo.pinned_threads(owner_id)
                if row.id != thread_id
            ]
            for index, row in enumerate(rest):
                self.repo.set_pin(row.id, True, index)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"thread_id": thread_id}

    def reorder_pins(
        self, owner_id: UUID, ordered_ids: list[UUID]
    ) -> dict:
        current = self.repo.pinned_threads(owner_id)
        if {row.id for row in current} != set(ordered_ids) or len(
            ordered_ids
        ) != len(current):
            raise ChatError(
                "validation_failed",
                "order must list every pinned chat once",
                422,
            )
        try:
            for index, tid in enumerate(ordered_ids):
                self._owned_thread(owner_id, tid)
                self.repo.set_pin(tid, True, index)
            self.db.commit()
        except ChatError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise
        return {"thread_ids": ordered_ids}

    def list_turns(
        self, owner_id: UUID, thread_id: UUID, limit: int = 20,
        cursor: str | None = None,
    ) -> dict:
        self._owned_thread(owner_id, thread_id)
        try:
            page = self.repo.list_turns(thread_id, limit, cursor)
        except ValueError as exc:
            raise ChatError("bad_request", "bad cursor", 400) from exc
        return {
            "items": [_row_to_item(row) for row in page["items"]],
            "next_cursor": page["next_cursor"],
        }

    def get_turn(
        self, owner_id: UUID, thread_id: UUID, turn_id: UUID
    ) -> Message:
        self._owned_thread(owner_id, thread_id)
        row = self.db.get(Message, turn_id)
        if (
            row is None
            or row.thread_id != thread_id
            or row.role != "assistant"
            or row.deleted_at is not None
        ):
            raise ChatError("not_found", "turn not found", 404)
        return row

    def get_checkpoint(self, owner_id: UUID, thread_id: UUID) -> dict | None:
        self._owned_thread(owner_id, thread_id)
        try:
            return self.checkpoints.load_latest_from_db(self.db, thread_id)
        except Exception:
            return self.checkpoints.load_latest(thread_id)

    def _owned_thread_with_deleted(
        self, owner_id: UUID, thread_id: UUID
    ) -> Thread:
        thread = self.repo.get_thread_with_deleted(thread_id)
        if thread is None:
            raise ChatError("not_found", "thread not found", 404)
        if thread.owner_id != owner_id:
            raise ChatError("forbidden", "cross-owner access denied", 403)
        return thread

    def delete_thread(self, owner_id: UUID, thread_id: UUID) -> dict:
        from datetime import datetime, timezone

        from app.services.maintenance import THREAD_PURGE_DAYS, purge_info

        self._owned_thread(owner_id, thread_id)
        now = datetime.now(timezone.utc)
        try:
            self.repo.soft_delete_thread(thread_id, now)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        info = purge_info(now, now) or {}
        return {
            "thread_id": thread_id,
            "deleted_at": now,
            "purge_at": info.get("purge_at"),
            "days_remaining": info.get("days_remaining", THREAD_PURGE_DAYS),
        }

    def restore_thread(self, owner_id: UUID, thread_id: UUID) -> dict:
        thread = self._owned_thread_with_deleted(owner_id, thread_id)
        if thread.deleted_at is None:
            raise ChatError("not_deleted", "thread is not deleted", 409)
        if not _undo_open(thread.deleted_at):
            raise ChatError("gone", "undo window passed", 410)
        try:
            self.repo.restore_thread(thread_id, since=thread.deleted_at)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"thread_id": thread_id}

    def delete_message(
        self, owner_id: UUID, thread_id: UUID, turn_id: UUID
    ) -> dict:
        from datetime import datetime, timezone

        self._owned_thread(owner_id, thread_id)
        row = self.repo.get_message(thread_id, turn_id)
        if row is None:
            raise ChatError("not_found", "turn not found", 404)
        try:
            self.repo.soft_delete_message(
                row, datetime.now(timezone.utc)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"turn_id": turn_id}

    def restore_message(
        self, owner_id: UUID, thread_id: UUID, turn_id: UUID
    ) -> dict:
        self._owned_thread_with_deleted(owner_id, thread_id)
        row = self.repo.get_message(thread_id, turn_id, include_deleted=True)
        if row is None:
            raise ChatError("not_found", "turn not found", 404)
        if row.deleted_at is None:
            raise ChatError("not_deleted", "message is not deleted", 409)
        if not _undo_open(row.deleted_at):
            raise ChatError("gone", "undo window passed", 410)
        try:
            self.repo.restore_message(row)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"turn_id": turn_id}
