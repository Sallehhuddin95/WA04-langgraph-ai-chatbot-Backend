# LangGraph Agentic RAG Chatbot Backend

API and agent runtime for the chat app. It owns chat logic, storage, and auth. The frontend holds no agent logic.

## Owns

- FastAPI routes and request checks
- LangGraph graph in `services/graph/`
- Postgres plus PGVector for app data and vectors, plus checkpoint-postgres for graph state
- Server session auth and per session thread scope

## Stack

- Python with FastAPI
- LangGraph with checkpoint-postgres
- Postgres with PGVector
- Alembic for migrations
- uv for deps, uvicorn to serve

## Folder map

- `routes/` : HTTP entry, no business rules
- `schemas/` : request and response shapes
- `services/graph/` : graph, nodes, retrieval, generation
- `repositories/` : DB access only
- `models/` : ORM models
- `db/` : engine, session, base
- `core/` : config, auth, errors
- `tests/` : unit, integration, contract

## Run

```sh
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Copy `.env.example` to `.env` first. Set `DATABASE_URL` and model keys.

## Specs

- `specs/features/chat-agent.md`
- `specs/api/chat-api.md`
- `specs/database/chat-persistence.md`
- `specs/README.md`

## ADRs

- `docs/adr/0005-use-python-langgraph-runtime.md`
- `docs/adr/0006-use-pgvector-and-postgres-checkpointer.md`
- `docs/adr/0007-use-multi-model-routing-with-bounded-grounding.md`
- `docs/adr/0008-use-server-session-scoped-chat-threads.md`
- `docs/adr/README.md`

## Governance

- `CONSTITUTION.md`
- `docs/architecture/system-overview.md`
