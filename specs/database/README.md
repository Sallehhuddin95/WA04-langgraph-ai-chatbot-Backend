# Database Specs

Database specs describe persistence-facing structures and constraints when those details matter to application behavior.

These specs are especially useful when schema or lifecycle rules affect API, feature, or migration design.

---

## Template

```md
# Schema or Persistence Concern

## Status

Draft

## Purpose

Why does this data structure exist?

## Entities or Tables

List the main structures involved.

## Key Fields

Describe important fields and their meaning.

## Relationships

Describe ownership and references.

## Constraints

Describe uniqueness, nullability, lifecycle, or integrity rules.

## Query or Access Notes

Describe important read/write patterns.

## Migration Notes

Describe important migration risks or compatibility notes.
```

---

## Writing Rules

- Focus on business-relevant persistence behavior.
- Document constraints that influence application logic.
- Keep migration-sensitive assumptions explicit.
