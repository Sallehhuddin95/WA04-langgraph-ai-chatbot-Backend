# 0009 Lock Embedding Model

## Status

Accepted

## Context

`document_chunks.embedding` is `vector(1536)` with no locked model. The dim, distance op, top-k, and index type are open. This blocks stable migrations and recall tuning.

The schema already uses `vector(1536)`. A choice that fits this dim avoids a schema break. The retriever needs one default top-k for day-one behavior.

Related: `specs/database/chat-persistence.md`, `specs/features/chat-agent.md`, ADR 0006.

## Decision

Use OpenAI `text-embedding-3-small` for all `document_chunks` embeddings.

Lock these values:

- model: `text-embedding-3-small`
- dim: 1536
- distance: cosine via `<=>`
- top-k default: 5
- index: HNSW on `embedding`

No schema change is needed. The current `vector(1536)` column already matches. Record model, dim, and op in each related migration message. Any change to model, dim, distance, or index type needs a new ADR plus a new migration with reindex.

## Consequences

Benefits:

- one stable dim for schema, code, and tests
- no migration or backfill for day one
- recall path is fixed: HNSW plus `<=>` plus top-k 5
- model change cost is clear: new ADR, new migration, re-embed

Costs and tradeoffs:

- all chunks must use the same model; mixed dims will fail inserts
- top-k 5 may miss for large docs; callers must pass explicit k when needed
- a future model move needs full re-embed and reindex work

## Alternatives Considered

### Larger Model (text-embedding-3-large or Similar)

Rejected for day one. It adds cost and latency with no proven recall gain on current docs. It also breaks the `vector(1536)` column and forces a migration plus backfill.

### IVFFlat Instead of HNSW

Rejected. HNSW fits small to mid-size recall with stable read latency. IVFFlat needs list tuning per data size and adds retune work on growth.

### Other Distance Ops (L2 or Inner Product)

Rejected. Cosine fits normalized text embeddings and matches current query shape (`ORDER BY embedding <=> :query_vec`). A change would need proof from recall tests.
