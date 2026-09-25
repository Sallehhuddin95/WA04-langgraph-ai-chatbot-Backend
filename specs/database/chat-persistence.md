# Chat Persistence

## Status

Draft

## Purpose

Store threads, messages, doc chunks, and graph checkpoints in one Postgres with Alembic control. Support owner checks, history paging, vector recall, and resume after restart.

Related: `specs/features/chat-agent.md`, `specs/api/chat-api.md`, ADR 0006.

## Entities or Tables

- `threads`: one row per chat thread
- `messages`: one row per user or assistant turn part
- `document_chunks`: one row per embedded chunk
- checkpoint tables from `langgraph-checkpoint-postgres`: `checkpoints`, `checkpoint_writes`, `checkpoint_blobs`

## Key Fields

### threads

- `id: UUID PK, default gen_random_uuid()`
- `owner_id: UUID NOT NULL` (from session, never from client)
- `title: VARCHAR(120) NULL`
- `created_at: TIMESTAMPTZ NOT NULL DEFAULT now()`
- `updated_at: TIMESTAMPTZ NOT NULL DEFAULT now()`

### messages

- `id: UUID PK`
- `thread_id: UUID NOT NULL FK -> threads.id`
- `role: VARCHAR(16) NOT NULL` (`user`, `assistant`, `system`)
- `text: TEXT NOT NULL`
- `intent_category: VARCHAR(32) NULL` (set on assistant rows)
- `is_grounded: BOOLEAN NULL` (set on assistant rows)
- `trace_id: UUID NOT NULL`
- `idempotency_key: UUID NULL`
- `created_at: TIMESTAMPTZ NOT NULL DEFAULT now()`

### document_chunks

- `id: UUID PK`
- `document_id: UUID NOT NULL`
- `chunk_index: INT NOT NULL`
- `text: TEXT NOT NULL`
- `embedding: vector(1536) NOT NULL` (dim follows embedding model, record in migration)
- `meta: JSONB NOT NULL DEFAULT '{}'`
- `created_at: TIMESTAMPTZ NOT NULL DEFAULT now()`

### checkpoints

Managed by `langgraph-checkpoint-postgres`. Adapter owns access via `repositories/checkpoint_adapter.py`.

- `thread_id: TEXT NOT NULL` (maps to app `threads.id` as text)
- `checkpoint_id: TEXT NOT NULL`
- `parent_id: TEXT NULL`
- `state: BYTEA or JSONB per lib version`
- `created_at: TIMESTAMPTZ NOT NULL`

## Relationships

- `threads 1-n messages` via `messages.thread_id`, `ON DELETE CASCADE`
- `document_chunks` has no FK to threads; link at read time via retrieval ids stored in logs or message meta
- checkpoints link by `thread_id` text; no DB FK to `threads.id` to keep lib upgrades safe; service joins by id string

## Constraints

- `messages.role` check: `role IN ('user','assistant','system')`
- `messages.intent_category` check when not null: `IN ('simple_chat','rag_search','complex_task')`
- `document_chunks` unique: `(document_id, chunk_index)`
- `messages` unique: `(owner scope idempotency)` via partial unique on `(thread_id, idempotency_key)` where key not null
- `threads.owner_id` never null, never client-set
- vector column uses `USING hnsw` or `ivfflat` per ops note; keep recall and build time in migration comment

## Query or Access Notes

- owner read: `WHERE id = :id AND owner_id = :user_id`, 403 on miss with valid session and existing id
- history page: `WHERE thread_id = :id ORDER BY created_at ASC, id ASC LIMIT :limit`, cursor is `(created_at, id)`
- vector recall: `ORDER BY embedding <=> :query_vec LIMIT :k`, filter by doc scope before order when needed
- resume: adapter loads latest checkpoint by `thread_id`, graph restores `ChatState`
- idempotent turn: lookup `(thread_id, idempotency_key)` before graph run

Indexes:

- `threads(owner_id, updated_at DESC)`
- `messages(thread_id, created_at ASC, id ASC)`
- `messages(trace_id)`
- `messages(thread_id, idempotency_key)` partial where key not null
- `document_chunks(document_id, chunk_index)`
- `document_chunks` vector index on `embedding`
- checkpoint index on `(thread_id, created_at DESC)`

## Migration Notes

Alembic plan:

1. `0001` extensions: `pgcrypto` or `pgcrypto` alt plus `vector`
2. `0002` `threads` plus `messages` with FKs and checks
3. `0003` `document_chunks` with vector column and indexes
4. `0004` checkpoint tables via lib SQL, wrapped in one migration with prefix `ckpt_`
5. later dims or index type changes get their own migration with reindex step

Rules:

- one concern per migration
- reversible where practical, with explicit data loss note when not
- record embedding dim and distance op in migration message
- keep app code and schema compatible in deploy order per `docs/backend/migrations.md`

Retention:

- threads and messages: keep until user delete or policy purge; hard delete cascades messages
- idempotency keys: 24 hours, then null them by job
- checkpoints: keep last 50 per thread or 30 days, prune by job
- logs keep `trace_id` mapping for 90 days
