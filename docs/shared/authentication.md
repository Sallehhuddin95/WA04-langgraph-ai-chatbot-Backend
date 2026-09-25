# Authentication and Authorization

This document defines shared authentication and authorization rules for the system.

It applies across frontend, backend, middleware, route handlers, APIs, and any supporting infrastructure that participates in identity or access control.

---

## 1. Core Principles

- Treat authentication as a security concern first and a UI concern second.
- Treat authorization as a server-enforced rule, not a client-enforced rule.
- Prefer simple, auditable defaults over token-heavy browser-side complexity.
- Expose only the minimum user and session data required by each surface.

---

## 2. Preferred Default

For web applications, prefer server-managed session cookies.

Rules:

- use secure cookies
- use `httpOnly` cookies where appropriate
- scope cookies as narrowly as practical
- keep the server as the source of truth for session validity

This model reduces client-side token handling risk and keeps authorization decisions close to the protected resources.

---

## 3. OAuth 2.0 and OpenID Connect

Use OAuth 2.0 with OpenID Connect when:

- third-party login is required
- enterprise SSO is required
- external identity federation is required
- delegated identity or access flows are required

Rules:

- do not choose OAuth 2.0 in the browser by default if simpler session-based auth is sufficient
- if external identity is used, prefer converting provider identity into a server-managed session when architecture allows
- keep identity protocol details out of unrelated application modules

---

## 4. Token Handling Rules

- Do not store access tokens or refresh tokens in `localStorage`.
- Avoid exposing long-lived credentials to client JavaScript.
- Keep refresh token handling on the server whenever possible.
- Do not leak raw token details into client state when not required.

If tokens must be used in architecture, they should still be wrapped in strict lifecycle, storage, and revocation discipline.

---

## 5. Authorization Rules

- Perform authorization checks on the server whenever possible.
- Treat client-side guards as UX assistance, not the primary security boundary.
- Centralize permission logic so rules remain consistent across routes and APIs.
- Distinguish clearly between unauthenticated, unauthorized, forbidden, and expired-session states.
- Derive or verify ownership-sensitive and permission-sensitive fields on the server; do not trust the client to preserve them correctly.

---

## 6. Data Exposure Rules

- Return only the user/session fields required by the consuming feature.
- Do not expose internal security claims to the UI unless the product explicitly needs them.
- Avoid broad “current user” payloads when smaller view-specific contracts are sufficient.

---

## 7. Frontend Responsibilities

Frontend should:

- render auth-aware flows cleanly
- route users appropriately based on server-provided auth state
- treat auth state as display state, not the root trust boundary
- provide explicit UX for session expiration, forbidden access, and sign-in requirements

Frontend should not:

- own primary authorization logic
- store long-lived auth secrets unsafely
- assume a visible button hide is sufficient access control

---

## 7a. Mobile-Specific Responsibilities

Mobile clients cannot rely on browser cookies, so the token-handling rules above apply differently on native platforms.

Mobile should:

- store access and refresh tokens using secure platform storage (for example `expo-secure-store` or platform keychain/keystore equivalents), never unencrypted storage such as `AsyncStorage`
- use short-lived access tokens with a refresh flow coordinated through the backend session/auth service
- handle OAuth via in-app browser flows and deep/universal links, then exchange the result for securely stored session tokens
- treat navigation guards as UX assistance, not the primary security boundary

Mobile should not:

- store tokens in unencrypted local storage
- log tokens or embed them in crash reports or analytics events
- assume a hidden navigation route is sufficient access control

---

## 8. Backend Responsibilities

Backend should:

- validate session or token authenticity
- enforce authorization decisions on protected resources
- return clear, structured auth-related error responses
- centralize auth policy wherever possible
- reject tampered or unauthorized payload mutations even when the frontend originally hid, disabled, or omitted those fields

Backend should not:

- rely on client checks as sufficient enforcement
- duplicate inconsistent permission logic across unrelated handlers

---

## 9. Review Checklist

- Is authentication source-of-truth server-controlled?
- Are authorization checks enforced on the server?
- Are tokens stored safely and minimally?
- Are auth-related flows explicit for unauthenticated and forbidden states?
- Is sensitive identity data exposure minimized?
