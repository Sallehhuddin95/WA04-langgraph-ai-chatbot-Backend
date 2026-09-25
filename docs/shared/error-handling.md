# Error Handling

This document defines shared error handling rules across frontend and backend.

The goal is to keep failures isolated, observable, and understandable without leaking internal details to end users.

---

## 1. Core Principles

- Errors should be contained at the smallest practical boundary.
- User-facing surfaces should communicate failures in clear product language.
- Internal diagnostic detail belongs in logs, traces, and monitoring systems, not in UI copy.
- Error handling must support both recovery and observability.

---

## 2. User-Facing Error Rules

- Show meaningful, actionable messages.
- Prefer product-language explanations over technical exception phrasing.
- Offer the next safe action when possible: retry, refresh, return, or contact support.
- Never expose raw stack traces, backend exception payloads, or internal error codes directly to end users.

Examples:

- Good: `We couldn't load your dashboard right now. Please try again.`
- Bad: `NullReferenceException in metrics service.`

---

## 3. Frontend Error Boundaries

Frontend should use layered error containment:

- route-level boundaries for route crashes
- component-level or client error boundaries for unstable interactive slices
- local form validation feedback for input problems
- localized async feedback for recoverable request failures

Rules:

- isolate failures so one broken area does not take down the full screen when avoidable
- keep retry and loading behavior scoped to the relevant UI slice
- design explicit empty, loading, retry, and failed states

---

## 4. Backend Error Rules

Backend should:

- return consistent error shapes
- distinguish validation, authentication, authorization, not found, conflict, and unexpected server errors
- log enough structured detail for diagnosis
- avoid leaking internals in public responses

Backend should not:

- return inconsistent free-form error payloads for similar failures
- mix business validation errors with generic 500-style failures

---

## 5. Validation Errors

- Map validation errors to the exact field, section, or request contract that failed.
- Prefer precise guidance over generic invalid-state messages.
- Keep validation rules consistent across client and server where appropriate.

---

## 6. Observability and Diagnostics

- Log internal error detail centrally.
- Correlate user-visible failures with traceable backend or client diagnostics where supported.
- Preserve enough context to debug recurring issues without reproducing from scratch.

---

## 7. Review Checklist

- Is the failure isolated at the smallest practical boundary?
- Are user-facing messages meaningful and safe?
- Are backend error responses consistent?
- Are validation errors specific and actionable?
- Are internal diagnostics captured outside the user interface?
