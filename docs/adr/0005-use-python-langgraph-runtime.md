# 0005 Use Python LangGraph Runtime

## Status

Accepted

## Context

The backend owns all agent behavior for Project 2. Chat requests need routing, retrieval, grading, and generation in one traceable flow.

A TypeScript runtime would split agent logic across stacks. That split adds port drift and duplicate state models. Python keeps graph code close to the model clients and the Postgres store.

Without a fixed layout, graph nodes drift into routes. Routes become hard to test.

## Decision

Use Python 3.11+ with `langgraph` inside the FastAPI backend. Place graph code under `services/graph/` with this layout:

- `services/graph/state.py`: `ChatState` definition only
- `services/graph/router.py`: intent classification node
- `services/graph/retriever.py`: vector search node
- `services/graph/grader.py`: grounding check node
- `services/graph/generator.py`: answer generation node
- `services/graph/graph.py`: node wiring and edge rules

Keep `routes/chat.py` thin. It maps HTTP to service calls. It holds no prompt logic and no edge logic.

Keep transport shapes in `schemas/chat.py`. Keep persistence in `repositories/` (`conversation`, `document`, `checkpoint_adapter`), `models/`, and `db/`. Keep config and auth helpers in `core/`. Cover graph edges and services in `tests/`.

`ChatState` stays internal. It holds `messages`, `retrieved_docs`, `intent_category`, and `is_grounded`. The API exposes only `thread_id`, `reply_text` or stream deltas, `citations`, `intent_category`, `is_grounded`, and `trace_id`.

## Consequences

Benefits:

- one runtime owns agent logic
- graph edges stay reviewable in one folder
- routes stay thin per ADR 0002
- state shape stays internal and stable
- tests can target nodes without HTTP

Costs and tradeoffs:

- backend team must know Python async and langgraph
- graph library upgrades can touch all nodes at once
- model client code must stay behind service bounds to avoid leaks into routes

## Alternatives Considered

### TypeScript Parallel Runtime

Rejected. It would duplicate state, prompt, and retrieval logic. It would force contract sync between two agent stacks with no clear owner.

### Single LLM Call Without Graph

Rejected. A single call cannot express bypass, retrieve, grade, retry, and fallback as explicit edges. Branch rules would hide inside prompts.

### Graph Logic Inside Routes

Rejected. It breaks ADR 0002. Routes would own business flow and become hard to test.
