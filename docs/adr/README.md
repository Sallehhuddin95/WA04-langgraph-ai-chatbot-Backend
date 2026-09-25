# Architecture Decision Records

This folder stores Architecture Decision Records (ADRs).

ADRs explain why an important architectural decision exists. They are not changelogs. They are durable records of decisions that affect structure, standards, or future implementation direction.

---

## 1. When to Create an ADR

Create an ADR when a decision affects one or more of the following:

- architecture boundaries
- dependency direction
- major framework or library choices
- authentication or security model
- error handling model
- testing strategy
- deployment or observability standards
- any change that future contributors will otherwise try to reverse without understanding why it was chosen

---

## 2. Naming Format

Use zero-padded numbering followed by a short slug.

Examples:

- `0001-use-nextjs-app-router.md`
- `0002-adopt-feature-driven-frontend.md`
- `0003-use-server-managed-sessions.md`

Numbers should increase over time and never be reused.

---

## 3. ADR Template

Use this structure:

```md
# 0001 Title

## Status

Accepted

## Context

What problem or pressure caused this decision?

## Decision

What was chosen?

## Consequences

What benefits, costs, and tradeoffs follow from this decision?

## Alternatives Considered

What other options were considered and why were they not chosen?
```

---

## 4. Status Values

Use one of these status values:

- Proposed
- Accepted
- Superseded
- Rejected

If an ADR is replaced, do not delete it. Mark it `Superseded` and link to the newer record.

---

## 5. Writing Rules

- Be specific.
- Focus on decision quality, not persuasion language.
- Record tradeoffs honestly.
- Prefer short, durable explanations over implementation detail.
- Link to related architecture docs or specs when relevant.

---

## 6. Review Questions

Before accepting an ADR, ask:

- Is the problem statement clear?
- Does the decision affect architecture beyond one local implementation?
- Are alternatives and tradeoffs documented honestly?
- Will a future contributor understand why this choice exists?
