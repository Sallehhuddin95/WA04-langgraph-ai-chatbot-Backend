# Chat API

## Status

Draft

## Endpoint or Operation

- `POST /api/auth/signup`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` (see `specs/api/auth.md`)
- `GET /api/chat/threads` (list own threads, newest first)
- `POST /api/chat/threads`
- `POST /api/chat/threads/{thread_id}/turns` (body gains `model`, `attachment_ids`)
- `POST /api/chat/threads/{thread_id}/attachments` (image upload, 5MB max)
- `GET /api/chat/threads/{thread_id}/turns` (items gain `citations`)
- `GET /api/chat/threads/{thread_id}/turns/{turn_id}/stream`
- `DELETE /api/chat/threads/{thread_id}` (soft delete)
- `POST /api/chat/threads/{thread_id}/restore` (undo within 10 seconds)
- `DELETE /api/chat/threads/{thread_id}/turns/{turn_id}` (one message)
- `POST /api/chat/threads/{thread_id}/turns/{turn_id}/restore` (undo within 10 seconds)

No `/v1` prefix. Additive changes only. See `docs/shared/versioning.md`. Contract rules follow `docs/shared/api-contract.md` and `docs/backend/api-design.md`.

## Purpose

Expose thread create, turn create, history read, and SSE stream for the chat agent in `specs/features/chat-agent.md`.

## Authentication

- cookie session required on all four endpoints
- server maps cookie to `user_id` per ADR 0008
- `401` for missing or expired session
- `403` for cross-owner thread access
- service verifies owner, routes do not trust client fields

## Request

### POST /api/chat/threads

Body (`CreateThreadRequest`):

```json
{
  "title": "trip plan"
}
```

- `title`: optional string, max 120 chars

### POST /api/chat/threads/{thread_id}/turns

Params:

- `thread_id`: UUID path param, required

Body (`CreateTurnRequest`):

```json
{
  "message": "what is the refund policy?",
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000",
  "model": "deepseek-v4-flash",
  "attachment_ids": []
}
```

- `message`: required string, 1-4000 chars
- `idempotency_key`: optional UUID, dedupes retries for 24 hours
- `model`: one of `deepseek-v4-flash`, `deepseek-v4-flash-vision-exp`, `muse-spark-1.3`; default `deepseek-v4-flash`; unknown values get 422
- `attachment_ids`: up to 5 uploaded image ids from the attachments endpoint; images with plain `deepseek-v4-flash` get 422 `model_no_vision` (vision models: `deepseek-v4-flash-vision-exp`, `muse-spark-1.3`)

### POST /api/chat/threads/{thread_id}/attachments

Multipart form with one `file` field. Images only, non-empty, max 5MB. Returns `{attachment_id, filename, mime, size}`. Wrong type or size gets 422.

Headers:

- `Cookie`: session cookie, required
- `Idempotency-Key`: optional alias for body key, header wins if both set

### GET /api/chat/threads/{thread_id}/turns

Query (`ListTurnsParams`):

- `limit`: optional int, default 20, range 1-50
- `cursor`: optional opaque string from prior page

### GET stream

Params:

- `thread_id`: UUID path param
- `turn_id`: UUID path param

Headers:

- `Cookie`: session cookie, required
- `Accept`: `text/event-stream`

## Response

### POST /api/chat/threads, 200

```json
{
  "thread_id": "uuid",
  "title": "trip plan",
  "created_at": "2026-09-25T10:00:00Z"
}
```

### POST turns, 200 (`CreateTurnResponse`)

```json
{
  "thread_id": "uuid",
  "turn_id": "uuid",
  "reply_text": "refunds close in 30 days...",
  "citations": [
    {"chunk_id": "uuid", "document_id": "uuid", "quote": "refunds close in 30 days"}
  ],
  "intent_category": "rag_search",
  "is_grounded": true,
  "trace_id": "uuid"
}
```

Pydantic shapes:

- `CitationResponse`: `chunk_id: UUID`, `document_id: UUID`, `quote: str`
- `CreateTurnResponse`: `thread_id: UUID`, `turn_id: UUID`, `reply_text: str`, `citations: list[CitationResponse]`, `intent_category: Literal["simple_chat","rag_search","complex_task"]`, `is_grounded: bool`, `trace_id: UUID`

### GET turns, 200

```json
{
  "items": [
    {"turn_id": "uuid", "role": "user", "text": "hi", "created_at": "2026-09-25T10:00:00Z"},
    {"turn_id": "uuid", "role": "assistant", "text": "hello", "intent_category": "simple_chat", "is_grounded": false, "trace_id": "uuid", "created_at": "2026-09-25T10:00:05Z"}
  ],
  "next_cursor": "opaque-or-null"
}
```

### GET stream, 200 SSE

Event format:

```text
event: delta
data: {"turn_id":"uuid","trace_id":"uuid","delta":"hello "}

event: citation
data: {"chunk_id":"uuid","document_id":"uuid","quote":"..."}

event: done
data: {"turn_id":"uuid","trace_id":"uuid","intent_category":"rag_search","is_grounded":true}
```

- `delta` events carry text slices in order
- `citation` events map to final `citations` list
- `done` closes the turn with final flags

### Error Shapes

Error envelope for all failures:

```json
{
  "error": {"code": "not_found", "message": "thread not found", "trace_id": "uuid"}
}
```

Code map:

- `200`: success
- `400`: bad cursor or bad stream state
- `422`: validation fail on `message`, `title`, `limit`
- `401`: missing or expired session
- `403`: cross-owner access or tampered protected field
- `404`: thread or turn not found
- `429`: rate limit hit
- `502`: model or retriever outage
- `504`: model timeout

## Rename, Pin, and Order

- `PATCH /api/chat/threads/{thread_id}` body `{title}` (1-120 chars, trimmed).
- `POST /api/chat/threads/{thread_id}/pin` body `{} or {position}`. Sixth pin gets 409 `pin_limit`.
- `POST /api/chat/threads/{thread_id}/unpin` body `{}`. Unpinning live rows gets 409 `not_pinned`.
- `POST /api/chat/threads/reorder` body `{thread_ids}` must list every pinned chat once, else 422.
- List order: pinned by `pin_order` first, then recency. At most 5 pins per owner.

## Delete and Undo

Delete is soft (`deleted_at`). Reads skip soft-deleted rows. Restore clears the stamp only within 10 seconds of deletion, else 410 `gone`. Restoring a live row is 409 `not_deleted`. Thread restore revives only messages deleted with the thread, not older individual deletes.
Purge policy: soft-deleted threads and messages are hard deleted after 30 days by `app/services/maintenance.py`. Delete responses carry `purge_at` plus `days_remaining`. `GET /api/chat/threads/deleted/list` lists soft-deleted threads with purge timing. `GET /api/chat/threads/purge-reminders/list` lists threads within 3 days of purge. The UI reminds the customer 3 days before permanent removal.

## Validation Rules

- reject unknown fields with `422`
- reject client-sent `owner_id`, `is_grounded`, `trace_id` with `403` or `422` per contract
- `message` length 1-4000, `title` max 120, `limit` 1-50
- `thread_id` and `turn_id` must be UUID
- idempotent replay returns the first stored result, not a new graph run

## Notes

- rate limits: 60 turns per user per minute, 10 thread creates per minute, 5 streams per thread at once; `429` carries `Retry-After`
- idempotency: key scope is user plus key, held 24 hours
- pagination: cursor is opaque, do not parse it client-side
- versioning: additive fields only, no rename or removal without a new ADR; never add `/v1` by reflex
- related docs: `docs/shared/api-contract.md`, `docs/backend/api-design.md`, `docs/shared/versioning.md`, `docs/shared/error-handling.md`
