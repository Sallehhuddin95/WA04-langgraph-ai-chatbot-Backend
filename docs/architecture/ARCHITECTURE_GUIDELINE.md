# Architecture Guideline

This document defines the architecture governance rules for the project. It exists to keep implementation decisions consistent across features, contributors, and AI agents.

The goal is not to over-prescribe every implementation detail. The goal is to establish stable boundaries, predictable dependency flow, and consistent decision-making.

---

## 1. Architecture Goals

- Keep the system easy to reason about as it grows.
- Preserve strong feature boundaries.
- Reduce accidental coupling across modules.
- Make testing, refactoring, and agent-assisted development predictable.
- Prefer explicit, repeatable architectural choices over one-off local optimizations.

---

## 2. Governance Principles

- Prefer simple architecture that can evolve safely.
- Enforce separation of concerns across layers and features.
- Favor composition over inheritance.
- Keep business rules out of presentation-only modules.
- Centralize cross-cutting concerns instead of re-implementing them in each feature.
- Record non-trivial architectural decisions in ADRs.

---

## 3. High-Level System Shape

This repository should evolve around clearly separated concerns:

- User-facing application layer
- Feature/domain modules
- Shared cross-cutting infrastructure
- External integration boundaries
- Testing layers
- Specification and decision records

At a minimum, architecture must answer these questions consistently:

- Where does UI logic live?
- Where does domain behavior live?
- Where does data access live?
- Which modules may depend on which other modules?
- How are security, error handling, logging, and testing applied consistently?

---

## 4. Layering Rules

Use directional dependency flow. Higher-level modules may depend on lower-level stable contracts, but lower-level modules must not depend on feature-specific UI or route concerns.

Preferred direction:

1. App and routing layer
2. Feature/domain layer
3. Shared infrastructure and utilities
4. External systems and transport boundaries

Rules:

- Route files should orchestrate, not contain feature business logic.
- Feature modules own business-facing UI, workflows, and contracts.
- Shared modules must stay domain-agnostic.
- External integrations must be isolated behind explicit service or adapter boundaries.

---

## 5. Feature Ownership

Features are the primary organizational unit for business capabilities.

Each feature should own:

- feature-scoped components
- feature-scoped hooks
- feature-scoped services
- feature-scoped schemas
- feature-scoped types
- feature-scoped tests

Promote code to shared space only when it is reused by multiple independent features and has become genuinely domain-agnostic.

---

## 6. Cross-Cutting Concerns

The following concerns must be handled consistently across the system:

- authentication and authorization
- error handling
- logging and observability
- validation
- caching and performance
- testing strategy

These concerns should be governed by shared rules, not redefined ad hoc inside individual features.

---

## 7. Decision Discipline

When introducing a new pattern, dependency, or structural rule:

- prefer existing project conventions first
- prefer the smallest viable change
- avoid introducing a second competing pattern for the same concern
- document meaningful architectural decisions in `docs/adr/`

If a change affects boundaries, dependencies, ownership, or lifecycle rules, it is an architecture decision and should be reviewed as such.

---

## 8. AI and Agent Governance

AI agents must follow project architecture documents before generating or modifying code.

Agents should:

- respect feature boundaries
- avoid introducing new architectural patterns without clear need
- reuse existing conventions before inventing new ones
- update documentation when architectural behavior changes
- treat ADRs and specs as source-of-truth context for non-trivial changes

---

## 9. Definition of Architectural Drift

Architectural drift includes:

- business logic leaking into route or view-only files
- feature internals being imported directly across feature boundaries
- multiple patterns for the same concern without justification
- inconsistent auth, error, or validation handling across features
- undocumented structural decisions that change future implementation direction

Architectural drift should be corrected early, before it becomes a project-wide convention by accident.

---

## 10. Review Checklist

Use this checklist for architecture-sensitive changes:

- Does the change respect existing feature boundaries?
- Does dependency direction remain correct?
- Is a shared concern being implemented consistently?
- Is this a new architectural pattern, and if so, does it need an ADR?
- Does the change improve or weaken long-term maintainability?
