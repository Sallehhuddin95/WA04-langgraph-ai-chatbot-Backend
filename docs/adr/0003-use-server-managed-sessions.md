# 0003 Use Server-Managed Sessions

## Status

Accepted

## Context

The system needs a secure default authentication model for web applications.

If browser-side tokens become the default without a strong reason, client code takes on unnecessary responsibility for token storage, refresh behavior, and credential safety.

## Decision

For web application authentication, the default model is server-managed sessions using secure cookies.

OAuth 2.0 with OpenID Connect may still be used when third-party login, SSO, or external identity federation is required, but the preferred web-app outcome remains a secure server-managed session where architecture allows.

## Consequences

Benefits:

- reduced client-side token exposure
- simpler frontend auth handling
- easier server-side authorization enforcement
- stronger alignment with route handlers, middleware, and server-rendered application flows

Costs and tradeoffs:

- session management must be implemented carefully on the server
- some external identity integrations may still require token-aware backend infrastructure

## Alternatives Considered

### Frontend-Managed JWT by Default

Rejected because it increases client-side security and lifecycle complexity without being the best default for a web application.

### Local Storage Token Storage

Rejected because it increases exposure risk and weakens the security posture compared with server-managed session handling.
