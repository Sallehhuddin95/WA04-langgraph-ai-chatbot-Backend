# Backend Database Guidelines

This document defines persistence and data access guidance for the PostgreSQL backend.

---

## 1. Core Principles

- PostgreSQL is the persistent source of truth.
- Repositories own persistence access boundaries.
- Data integrity rules must be enforced deliberately at the correct layer.
- Schema changes must remain aligned with migrations and contracts.

---

## 2. Repository Rules

- Repositories encapsulate persistence interaction.
- Keep query behavior explicit and testable.
- Avoid scattering database access across routes and services.
- Repositories should expose business-meaningful data access operations where possible.

---

## 3. Model Rules

- Models should represent persistence structures clearly.
- Keep transport schemas separate from persistence-facing models.
- Avoid coupling database representation directly to every API response shape.

---

## 4. Integrity Rules

- Enforce uniqueness, ownership, and lifecycle-sensitive data rules intentionally.
- Do not rely on frontend behavior to preserve data integrity.
- Validate or derive protected fields server-side where mutation safety matters.

---

## 5. Query Discipline

- Keep filtering, sorting, and lookup behavior explicit.
- Avoid hidden query side effects.
- Optimize only after identifying real query or load problems.

---

## 6. Review Checklist

- Is persistence access isolated to repositories?
- Are persistence models separated from transport contracts?
- Are integrity-sensitive fields protected server-side?
- Is the data access behavior explicit and testable?
