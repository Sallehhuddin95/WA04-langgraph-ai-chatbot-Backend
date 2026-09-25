# Chat Acceptance

## Status

Draft

## Scope

Backend acceptance for `specs/features/chat-agent.md` and `specs/api/chat-api.md`. Covers bypass, grounding, retry fallback, resume, auth, and outage shape.

## Scenarios

### Scenario: Simple chat bypass

Given a signed-in user with an owned thread
When the user posts `hi there` with a fresh idempotency key
Then the API returns 200 with `intent_category` `simple_chat`
And `is_grounded` is false with `citations` empty
And no retriever latency appears in the turn log

### Scenario: Grounded answer with citations

Given an owned thread and indexed docs about refunds
When the user posts `what is the refund policy?`
Then the API returns 200 with `intent_category` `rag_search`
And `is_grounded` is true with at least one citation
And each `chunk_id` matches a retrieved chunk for that `trace_id`

### Scenario: Retry then fallback

Given retrieval returns weak chunks that fail grading twice
When the user posts a doc question
Then the graph retries at most 2 times
And the API returns 200 with `is_grounded` false and `citations` empty
And the reply states it is not grounded in docs
And the log shows retry count 2 with scores

### Scenario: Resume after restart

Given a thread with 3 prior turns and a saved checkpoint
When the backend restarts and the user posts a follow-up
Then history `GET` returns all prior turns in order
And the new turn uses prior state without data loss
And the new `trace_id` differs from prior turns

### Scenario: Cross-user denied

Given user A owns the thread
When user B with a valid session calls `POST` turn, `GET` turns, or `GET` stream on that thread
Then the API returns 403 with the error envelope
And no graph run starts and no rows change

### Scenario: LLM outage stays safe

Given the generator times out or returns 5xx
When the user posts a turn
Then the API returns 502 for failure or 504 for timeout
And the body has `code`, `message`, and `trace_id`
And no partial assistant row is stored as success
