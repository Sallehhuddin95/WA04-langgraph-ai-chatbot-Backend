# Migration Guidelines

This document defines migration rules for Alembic-managed schema changes.

---

## 1. Core Principles

- Every schema change must be tracked through Alembic.
- Migrations must be reviewable and understandable.
- Schema evolution must stay aligned with application rollout expectations.

---

## 2. Migration Rules

- Create explicit migrations for schema changes.
- Keep migration intent clear.
- Avoid combining unrelated schema changes into one migration without reason.
- Prefer safe incremental changes over risky one-shot structural rewrites.

---

## 3. Compatibility Rules

- Application code and schema changes must remain compatible for the intended deployment order.
- Breaking data-shape changes should be staged when practical.
- Destructive migration steps should be deliberate and reviewed carefully.

---

## 4. Data Safety Rules

- Treat existing production data as a primary constraint.
- Backfill and data transition behavior should be explicit when needed.
- Review ownership, defaults, nullability, and uniqueness carefully.

---

## 5. Review Checklist

- Is the migration intent clear?
- Is the schema change tightly scoped?
- Is deployment compatibility preserved?
- Are destructive or risky changes explicit?
- Does the application code remain aligned with the migrated schema?
