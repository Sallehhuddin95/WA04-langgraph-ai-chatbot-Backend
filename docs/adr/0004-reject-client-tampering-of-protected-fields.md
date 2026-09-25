# 0004 Reject Client Tampering of Protected Fields

## Status

Accepted

## Context

The system already treats authorization and sensitive state as server-enforced concerns.

In web applications, the client can modify requests regardless of what the UI hides, disables, or omits. If the backend accepts ownership-sensitive, permission-sensitive, pricing-sensitive, or otherwise protected field changes without explicit server verification, the system can produce unauthorized or invalid state transitions.

The shared authentication, API contract, and error-handling guidance already assumes a strict server trust boundary. This decision should be recorded explicitly so future contributors do not weaken it during endpoint or schema changes.

## Decision

Client payloads are untrusted by default.

The server must derive, verify, ignore, or reject protected-field values based on the contract and the use case. When a request attempts to mutate server-owned, authorization-sensitive, or otherwise disallowed fields, the system must return a failure response rather than silently accepting the change.

This rule applies across:

- authentication and authorization flows
- create and update endpoints
- route handlers, services, repositories, and validation layers
- frontend interactions that submit user-controlled payloads

## Consequences

Benefits:

- stronger authorization enforcement
- clearer server trust boundaries
- reduced risk from hidden-field or modified-request attacks
- better alignment between shared contracts, backend validation, and error responses

Costs and tradeoffs:

- some endpoints require more explicit allowlists or server-side field derivation
- validation and error contracts must remain disciplined as APIs evolve
- frontend developers cannot assume UI restrictions are sufficient security controls

## Alternatives Considered

### Trusting Hidden or Disabled Client Fields

Rejected because client-side presentation does not create a security boundary and requests can be modified outside the intended UI flow.

### Silently Ignoring All Invalid Protected-Field Changes

Rejected as the default because it can hide security-relevant misuse or contract violations. Endpoints should fail when the request attempts unauthorized or out-of-contract mutations unless the contract explicitly defines a server-derived value that ignores client input.
