# Chat Agent

## Status

Draft

## Goal

Give one backend-owned chat flow that answers small talk fast and grounds doc questions in retrieved chunks.

## Scope

Included:

- intent routing per turn
- LangGraph nodes for router, retriever, grader, and generator
- edge rules on `intent_category` and `is_grounded`
- max 2 grader retries with fallback
- citations on grounded replies
- `trace_id` and latency logs per turn

## Out of Scope

Non-goals:

- frontend prompt building
- doc upload or chunk pipeline tuning
- Qdrant or external vector store
- multi-user shared threads
- auto re-index on doc edit (covered by ingestion work, not this spec)

## Actors

- signed-in user sending a chat turn
- FastAPI service running the graph
- retriever reading `document_chunks`
- grader checking draft support
- generator writing the final reply

## Preconditions

- user has a valid session cookie
- thread exists and belongs to the user
- `pgvector` index and checkpoint tables exist
- model keys for DeepSeek V4 Flash and Muse Spark 1.3 are set

## Intent Taxonomy

| Intent | Meaning | Path |
| --- | --- | --- |
| `simple_chat` | greeting or small talk, no docs needed | router to generator, skip retrieval |
| `rag_search` | fact question over docs | router to retriever to grader to generator |
| `complex_task` | multi-step task needing docs plus planning | router to retriever to grader to generator with plan step |

Router input: current user text plus last 6 messages. Router output: one enum value. Default on low confidence: `rag_search`.

## Node I/O

### router

- input: `messages` (tail), no docs
- output: `intent_category`
- model: DeepSeek V4 Flash

### retriever

- input: user text, `intent_category`
- output: `retrieved_docs` (top k with chunk id, doc id, score, text)
- k default: 5 for `rag_search`, 8 for `complex_task`, 0 for `simple_chat`
- no LLM call

### grader

- input: draft answer plus `retrieved_docs`
- output: `is_grounded` (bool) plus numeric score
- model: DeepSeek V4 Flash

### generator

- input: `messages`, filtered `retrieved_docs`, `intent_category`
- output: `reply_text`, `citations`, `is_grounded`
- model: Muse Spark 1.3

### graph

- file: `services/graph/graph.py`
- owns edge order and retry counter
- owns checkpoint save and resume keys

## Main Flow

1. `POST /api/chat/threads/{thread_id}/turns` stores the user message.
2. Router sets `intent_category`.
3. If `simple_chat`, generator answers directly with `is_grounded=false`.
4. If `rag_search` or `complex_task`, retriever loads chunks.
5. Generator drafts a reply from docs.
6. Grader sets `is_grounded`.
7. Graph returns reply with `citations`, `intent_category`, `is_grounded`, and `trace_id`.

## Edge Conditions

- `intent_category == simple_chat`: skip retriever and grader. Set `is_grounded=false`. Set `citations=[]`.
- `intent_category in (rag_search, complex_task)` and `is_grounded == true`: return reply with 1-n citations.
- `is_grounded == false` and retries < 2: refetch docs, regenerate, regrade.
- `is_grounded == false` and retries >= 2: return fallback. Set `is_grounded=false`. Set `citations=[]`.
- empty retrieval: treat as `is_grounded=false`. Follow retry then fallback path.

## Retry and Fallback

- max 2 grader retries per turn
- retry changes the query or filter, not just the same call
- fallback text states the answer is not grounded in docs and suggests a follow-up
- fallback carries a new `trace_id` linked to the same turn
- retry count and scores go to logs, not to the client

## Citation Rule

- `is_grounded=true` requires at least one citation
- each citation has `chunk_id`, `document_id`, and `quote` or `offset`
- chunk ids must match `retrieved_docs` ids for that turn
- `is_grounded=false` must send `citations=[]`
- frontend must not render citation UI when the list is empty

## Observability

- `trace_id`: UUIDv4 per turn, made server-side, returned in response and SSE
- log per turn: `trace_id`, `thread_id`, `intent_category`, `is_grounded`, retry count, model names, latency ms per node
- latency: router, retriever, grader, generator, total
- never log session cookie values or raw model keys

## Error and Empty States

- no docs found: fallback with `is_grounded=false`
- grader fails: count as one retry, then retry or fallback
- generator fails: return 502 with `trace_id`
- model timeout: return 504 with `trace_id`
- cross-owner thread: 403, no graph run

## Acceptance Criteria

- `simple_chat` skips retrieval and returns with no citations
- `rag_search` with good docs returns `is_grounded=true` plus citations
- 2 failed grades return fallback with `is_grounded=false`
- resume after restart loads checkpoint and keeps history
- cross-owner access returns 403
- LLM outage returns 502 with safe shape and `trace_id`

## Related Specs

- API: `specs/api/chat-api.md`
- Database: `specs/database/chat-persistence.md`
- Acceptance: `specs/acceptance/chat-acceptance.md`
- ADRs: `docs/adr/0005-use-python-langgraph-runtime.md`, `docs/adr/0006-use-pgvector-and-postgres-checkpointer.md`, `docs/adr/0007-use-multi-model-routing-with-bounded-grounding.md`, `docs/adr/0008-use-server-session-scoped-chat-threads.md`
