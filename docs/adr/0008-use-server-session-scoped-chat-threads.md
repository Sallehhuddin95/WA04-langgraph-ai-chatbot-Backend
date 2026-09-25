# 0008 Use Server Session Scoped Chat Threads

## Status

Accepted

## Context

Chat threads belong to one user. The API must block cross-owner reads and writes. The client cannot be trusted to keep `owner_id` or `thread_id` honest.

The repo already uses server-managed sessions per ADR 0003. It already rejects tampered protected fields per ADR 0004. Chat needs the same pattern applied to threads and turns.

## Decision

Use cookie session as truth for chat ownership:

- auth comes from secure `httpOnly` session cookie
- server maps cookie to `user_id` on every chat call
- `thread.owner_id` is set from server context at create time
- client cannot set or change `owner_id`

Verify owner in the service layer:

- `conversation` repository loads thread by id
- service compares `thread.owner_id` with session `user_id`
- mismatch returns 403
- missing session returns 401
- missing thread returns 404

Reject tampered fields:

- accept only explicit fields per contract
- ignore or reject `owner_id`, `trace_id`, or `is_grounded` sent by the client
- derive `trace_id` server-side per turn
- derive `is_grounded` from the grader only

## Consequences

Benefits:

- ownership checks live in one service path
- routes stay thin and consistent with ADR 0002
- tampered payloads fail instead of leaking data
- session model matches ADR 0003 with no new token flow

Costs and tradeoffs:

- every chat call needs a session lookup
- tests must cover owner mismatch and tampered fields
- non-browser clients need cookie handling or a documented agent path

## Alternatives Considered

### Trust Client Sent owner_id

Rejected. It breaks ADR 0004. Any user could read other user threads by editing the payload.

### Route Level Owner Check Only

Rejected. Route checks drift across endpoints. Service checks keep one rule for turns, history, and stream.

### Bearer Token per Request as Default

Rejected. It adds client storage risk for the web app. Server sessions already give the needed identity.
