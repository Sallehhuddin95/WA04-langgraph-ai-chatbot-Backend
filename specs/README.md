# Specifications

This folder contains the source-of-truth specifications for planned and implemented behavior.

Specs exist to align architecture, implementation, testing, and review before code drifts into undocumented behavior.

---

## Start Here

Use this folder when a change needs clear behavior definition before implementation.

Start with this rule of thumb:

- if the work changes product behavior, write or update a spec
- if the work changes architecture or a durable technical decision, write or update an ADR instead

Suggested first step:

1. Create a feature spec in `features/`.
2. Add related API, UI, database, or acceptance specs only if the change needs them.
3. Keep the spec narrow and tied to one bounded concern.

---

## Structure

- `features/`: feature-level behavior and scope
- `api/`: transport and endpoint contracts
- `database/`: schema and persistence-oriented design notes
- `ui/`: user interface behavior and screen-level expectations
- `acceptance/`: user-visible acceptance criteria and scenario definitions

---

## Usage Rules

- Write or update specs before or alongside meaningful behavior changes.
- Keep specs concrete enough to guide implementation and testing.
- Prefer one spec per bounded concern instead of one giant catch-all document.
- Update specs when contracts, flows, or acceptance behavior changes.
- If a change is architectural rather than feature-specific, document it in `docs/adr/` instead.

---

## Recommended Flow

1. Define or update the feature spec.
2. Add or refine related API, UI, database, or acceptance specs as needed.
3. Implement against the spec.
4. Validate tests and behavior against the documented expectations.
5. Keep the spec current after review changes.
