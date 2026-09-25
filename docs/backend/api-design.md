# Backend API Design

This document defines API design rules for the FastAPI backend.

Use it together with `docs/shared/api-contract.md`.

---

## 1. Core Principles

- APIs must be explicit, predictable, and validated.
- Endpoints should reflect clear business intent.
- Request and response contracts must be defined through explicit schemas.
- Error behavior must be consistent and meaningful.

---

## 2. Endpoint Design Rules

- Prefer resource- and action-revealing route design.
- Keep route handlers thin.
- Use HTTP methods intentionally.
- Avoid endpoint behavior that depends on undocumented client conventions.

---

## 3. Request Rules

- Validate all request bodies, query params, and path params.
- Accept only explicit fields.
- Reject unknown, forbidden, or invalid payload changes when the contract does not allow them.
- Do not trust the client to preserve hidden or readonly field invariants.

---

## 4. Response Rules

- Return explicit response schemas.
- Keep response fields intentional and minimal.
- Do not leak internal persistence or security details.
- Keep error responses structured and predictable.

---

## 5. Status Code Rules

- `2xx` for successful operations only
- `4xx` for client-caused failures such as invalid input, forbidden access, or missing resources when appropriate
- `5xx` for unexpected server failures

A tampered or invalid payload must never result in a success response.

---

## 6. Pagination and Filtering

- Use explicit pagination inputs for large collections.
- Keep filtering and sorting parameters documented and validated.
- Avoid returning unbounded large datasets when pagination is the safer default.

---

## 7. Review Checklist

- Is the endpoint purpose clear?
- Are request and response schemas explicit?
- Are invalid or tampered payloads rejected correctly?
- Are status codes consistent with behavior?
- Is pagination or filtering necessary for large result sets?
