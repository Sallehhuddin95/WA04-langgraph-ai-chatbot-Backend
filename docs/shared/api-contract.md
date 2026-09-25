# API Contract Guidelines

This document defines shared rules for API contracts across the system.

It applies to transport-level contracts, request and response shapes, validation boundaries, and error payload consistency.

Use it together with `docs/shared/versioning.md` when contract evolution or compatibility is involved.

---

## 1. Core Principles

- Contracts must be explicit and stable.
- Request and response shapes should be predictable and version-aware when necessary.
- Validation should happen at the boundary, not after malformed data has already leaked inward.
- Contract design should prioritize clarity over convenience.

---

## 2. Contract Ownership

- API contracts must have a clear owner.
- Shared contracts should not be changed casually because they affect multiple layers.
- Frontend and backend must align through documented schemas, specs, or generated types when appropriate.

---

## 3. Request Design Rules

- Use explicit request models.
- Validate input at the boundary.
- Keep request shapes narrow and purposeful.
- Avoid overly generic payloads that hide intent.
- Accept only allowed fields and reject out-of-contract or protected-field mutations.

Examples of intent-revealing request names:

- `CreateUserPayload`
- `UpdateProfilePayload`
- `ListInvoicesParams`

---

## 4. Response Design Rules

- Keep response shapes consistent for similar resource types.
- Avoid unnecessary transport noise.
- Return only the fields required by consumers.
- Distinguish raw transport models from internal domain models when needed.

Where pagination is used, prefer a stable envelope with item data and pagination metadata.

---

## 5. Error Contract Rules

- Use consistent error payloads.
- Distinguish validation failures from authorization, not found, conflict, and unexpected server errors.
- Ensure the frontend can map errors to useful user-facing states.
- Invalid, tampered, or unauthorized payload changes must result in failure responses, not success responses.

---

## 6. Evolution Rules

- Avoid breaking contract changes when a non-breaking alternative exists.
- Document meaningful contract changes.
- Use explicit API versioning only when compatibility pressure or breaking evolution requires it.
- If a contract shift changes architecture or cross-feature behavior, consider an ADR.
- Keep deprecated fields or endpoints intentional and time-bounded.

---

## 7. Frontend and Backend Alignment

- Frontend should not guess response shapes.
- Backend should not change contract structure silently.
- Shared types or schemas should reflect the documented contract, not replace it.
- Specs should remain the source of truth for significant contract behavior.

---

## 8. Review Checklist

- Is the request shape explicit and validated?
- Is the response shape stable and intentional?
- Are error payloads consistent?
- Does the contract expose only necessary data?
- Does this change require spec or ADR updates?
