# 0006 Use PGVector and Postgres Checkpointer

## Status

Accepted

## Context

The chat agent needs two stores. It needs vector search for grounding. It needs durable graph state for resume after restart.

Running two systems on day one adds ops cost and backup drift. One Postgres can cover both needs with extensions and the langgraph checkpoint package.

## Decision

Use one PostgreSQL instance with two roles:

- `pgvector` for `document_chunks.embedding` search
- `langgraph-checkpoint-postgres` for graph checkpoints on the same Postgres

Manage all schema through Alembic. This includes app tables and checkpoint tables. Checkpoint access goes through `repositories/checkpoint_adapter.py`. No route or node touches checkpoint tables directly.

Keep a future migration path open. If vector load outgrows Postgres, move only the vector index to a dedicated store. Keep threads, messages, and checkpoints in Postgres. A move needs a new ADR and a dual-read plan.

## Consequences

Benefits:

- one backup and one deploy target
- joins between threads, messages, and chunks stay simple
- resume works from the same transaction store
- Alembic keeps schema review in one flow

Costs and tradeoffs:

- vector tuning shares resources with app queries
- checkpoint writes add row churn in Postgres
- a later vector move needs reindex and backfill work

## Alternatives Considered

### Qdrant on Day One

Rejected for day one. It adds a second service, second backup, and ID sync between stores. It can return later if recall, scale, or latency data supports it.

### Separate Checkpoint Database

Rejected. Separate stores break atomic resume and add failure modes during restart. One store keeps thread state and graph state aligned.

### File or Memory Checkpoints

Rejected. They do not survive restart. They break resume and multi-worker runs.
