# Feature Development Workflow

This document defines the default workflow for implementing a new feature.

The goal is to make feature work consistent, reviewable, and aligned with architecture and specs.

---

## 1. Start Conditions

Before implementation begins, the feature should have:

- a clear problem statement
- defined scope boundaries
- acceptance criteria
- identified affected layers
- known architecture or contract constraints

If those are missing, define them before coding.

---

## 2. Recommended Workflow

1. Confirm the feature goal and out-of-scope items.
2. Identify which feature module or system area owns the change.
3. Review relevant docs:
   - architecture guidance
   - frontend, backend, or mobile rules
   - shared auth, error, or API rules
   - relevant ADRs and specs
4. Update or create the feature spec if behavior is not already documented.
5. Design the change at the smallest architecture-consistent slice.
6. Write or update tests for the intended behavior where practical.
7. Implement the feature.
8. Validate behavior, tests, and architecture boundaries.
9. Update docs if the feature changes contracts, flows, or conventions.

---

## 3. Implementation Rules

- Respect ownership boundaries.
- Prefer extending existing patterns over inventing new ones.
- Avoid mixing multiple unrelated concerns in one change set.
- Use the smallest sufficient layer for validation.
- If the feature introduces a structural or cross-cutting change, consider an ADR.

---

## 4. Testing Expectations

- Add unit tests for isolated logic.
- Add integration tests for interactive or async UI behavior.
- Add end-to-end coverage for critical route or user journey changes.
- Prefer behavior-focused tests over implementation-coupled tests.

---

## 5. Completion Checklist

- Is the feature scope clear and still controlled?
- Does the implementation respect module boundaries?
- Are tests added or updated at the correct level?
- Are shared contracts still valid?
- Does the change require doc, spec, or ADR updates?
