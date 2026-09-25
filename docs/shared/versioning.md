# Versioning Guidelines

This document defines how to think about API versioning, contract evolution, deprecation, and release version numbers.

Use it with `docs/shared/api-contract.md` and `docs/workflow/release.md`.

---

## 1. Core Principles

- Prefer stable contracts over frequent version churn.
- Avoid breaking changes when a non-breaking path is practical.
- Version only when compatibility pressure is real, not by reflex.
- Make deprecations explicit, documented, and time-bounded.
- Keep release version numbers honest about change scope.

---

## 2. API Versioning Default

Do not introduce `/api/v1` or equivalent route versioning by default on day one unless the system already has a clear compatibility need.

Default approach:

- keep the contract explicit and stable
- evolve it through additive, non-breaking changes where practical
- document contract expectations in specs and shared API guidance

This avoids premature version sprawl in early-stage systems.

---

## 3. When to Introduce Explicit API Versions

Introduce explicit API versioning when one or more of these is true:

- external consumers depend on long-lived contract stability
- a breaking contract change cannot be avoided safely
- multiple client versions must be supported at the same time
- migration must happen gradually instead of through a single coordinated cutover

If none of these conditions exist, prefer evolving the current contract carefully instead of adding a new API version.

---

## 4. Preferred API Versioning Style

If explicit API versioning is needed, prefer path-based major versioning for public or long-lived HTTP APIs.

Example:

- `/api/v1/users`
- `/api/v2/users`

Rules:

- use the version in the path only for major breaking contract boundaries
- do not create `/v2` just because new optional fields were added
- keep version naming simple and predictable
- avoid mixing multiple versioning strategies unless there is a strong reason

For internal systems with tightly coordinated clients and servers, explicit route versioning may still be unnecessary if compatibility is managed safely.

---

## 5. What Counts as a Breaking API Change

Treat changes like these as breaking unless the contract explicitly allowed them:

- removing a field
- renaming a field
- changing field meaning incompatibly
- making a previously optional field required
- changing validation in a way that rejects previously valid requests
- changing response shape in a way existing clients cannot safely ignore
- changing authentication or authorization expectations incompatibly

Breaking changes require explicit review and usually require versioning, a migration plan, or both.

---

## 6. Preferred Non-Breaking Evolution Patterns

Prefer these patterns before creating a new version:

- add new optional fields
- add new endpoints instead of changing old ones incompatibly
- add new enum values only when consumers can tolerate unknown values
- support parallel fields temporarily during migration
- deprecate first, remove later

The goal is to keep existing consumers working while moving toward the better contract.

---

## 7. Deprecation Rules

- Mark deprecated fields, endpoints, or behaviors clearly in specs and docs.
- Give deprecations an owner and a removal expectation.
- Do not leave deprecated behavior undocumented or indefinite by accident.
- If a deprecation has broad architecture or product impact, consider an ADR.

When relevant, document:

- what is deprecated
- why it is deprecated
- what replaces it
- when removal is expected

---

## 8. Release Versioning

For projects, packages, or services that publish versions, prefer semantic versioning:

- `MAJOR`: incompatible or breaking changes
- `MINOR`: backward-compatible additions or enhancements
- `PATCH`: backward-compatible fixes

Example:

- `1.4.2`

Use semantic versioning when the target repo has releases, packages, or deployable artifacts where version numbers are meaningful to consumers.

If a repo does not publish versions formally, still use the semantic versioning mindset to describe release impact.

---

## 9. Specs and Review Expectations

When versioning matters, specs and reviews should make it explicit.

Check:

- whether the change is breaking or non-breaking
- whether an explicit API version is required
- whether a deprecation path is documented
- whether release notes or compatibility notes are needed
- whether an ADR is needed for a major compatibility decision

---

## 10. Practical Defaults

If you need a simple default policy, use this:

1. do not add `/api/v1` on day one unless there is a real compatibility need
2. prefer additive, non-breaking contract evolution
3. if a breaking API change is unavoidable, use a new major API version and document migration
4. use semantic versioning for releases when the repo publishes versioned artifacts
5. make deprecations explicit and time-bounded
