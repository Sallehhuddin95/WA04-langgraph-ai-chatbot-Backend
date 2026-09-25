# Repository Constitution

This document defines the repo-wide constitution for this guidelines repository.

It exists to make the repository's purpose, non-negotiable principles, source-of-truth order, and governance expectations explicit.

This is not a detailed implementation guide. It is the top-level rule set that all other guidance in this repository should align with.

---

## 1. Purpose

This repository exists to provide reusable governance for software projects.

It is intended to help teams and AI agents:

- start new repositories with clearer standards
- improve existing repositories without uncontrolled drift
- keep architecture, contracts, testing, workflow, and documentation aligned
- make important technical decisions explicit and durable

This repository is not an application or feature codebase.

---

## 2. Scope

This repository governs:

- architecture and boundaries
- shared cross-stack concerns
- frontend, backend, and mobile engineering conventions
- ADR usage
- specs usage
- workflow expectations
- AI and agent behavior within governed repos

This repository does not attempt to replace product requirements, business strategy, or project-specific delivery judgment.

---

## 3. Non-Negotiable Principles

The following principles apply across the repository:

1. Reality over aspiration.
   Documentation must describe the rules and behavior the target project actually intends to follow.

2. One concern, one source of truth.
   Guidance for a concern should have a clear owning document rather than multiple competing descriptions.

3. Explicit boundaries over convenience.
   Architecture, contracts, and responsibilities should remain clear even when shortcuts would be faster locally.

4. Small, durable rules over broad vague advice.
   Guidance should be specific enough to shape decisions and stable enough to survive normal project change.

5. Shared concerns must be governed consistently.
   Authentication, authorization, contracts, error handling, versioning, testing, and similar cross-cutting rules must not be redefined ad hoc in isolated areas.

6. Specs and ADRs exist to reduce drift, not to create ceremony.
   Use them when they clarify real behavior or durable decisions.

7. AI agents must follow repository guidance before generic best practice.
   If local project guidance exists and is authoritative, it wins.

8. Prefer latest stable dependency versions when compatible.
   New projects and planned upgrades should prefer the latest stable framework and library versions unless known compatibility, peer dependency, build, runtime, or platform issues justify staying behind.

---

## 4. Source-of-Truth Order

When guidance appears to conflict, resolve it in this order:

1. this constitution for repo-wide intent and non-negotiable governance
2. ADRs for accepted durable architectural decisions
3. architecture and shared docs for structural and cross-cutting rules
4. stack-specific docs for frontend or backend conventions
5. specs for concrete feature, API, UI, database, or acceptance behavior
6. workflow docs for process expectations
7. agents, which must enforce and apply the documents above rather than invent competing policy

If two documents conflict at the same level, the more specific and actively maintained source should be corrected so the conflict disappears.

---

## 5. Architecture and Shared Governance Rules

- Architecture rules must stay explicit and directional.
- Shared concerns must be documented once and referenced consistently.
- New patterns should reuse existing governance unless there is a clear reason to introduce a different one.
- Competing patterns for the same concern should be treated as drift until justified and documented.

If a change affects boundaries, dependency direction, contract evolution, or long-term structure, it is a governance-sensitive change.

---

## 6. ADR Rules

Use ADRs for decisions that meaningfully affect future implementation direction.

ADRs should be used when a decision affects one or more of the following:

- architecture boundaries
- dependency rules
- major framework or platform choices
- versioning or compatibility policy
- authentication or trust-boundary rules
- cross-stack contract expectations
- process rules that materially affect how the project evolves

Do not write ADRs for trivial implementation details.

---

## 7. Specs and Workflow Rules

- Specs should define meaningful behavior before or alongside implementation when behavior clarity matters.
- Workflow docs should support real delivery work, not ceremonial process.
- Specs and workflow documents must remain lightweight enough to be used consistently.
- If a process or behavior is not actually followed, the docs should be corrected rather than preserved as fiction.

---

## 8. Agent Governance

Agents in this repository are execution helpers, not policy authors.

Agents must:

- read the relevant governing docs before acting
- follow documented repo rules over generic habits
- avoid inventing competing policy when a governing document already exists
- update documentation when their changes alter governed behavior
- treat ADRs and specs as authoritative when relevant

Agent descriptions and usage guides must remain aligned with the real document set.

---

## 9. Change Management for This Repository

When changing this repository:

- prefer updating the smallest correct source of truth
- avoid duplicating the same rule across many files without reason
- add new documents only when existing documents cannot own the concern cleanly
- keep onboarding paths simple for both new and existing projects
- validate that new guidance fits the current repository structure

If a new document changes repo-wide expectations, update the root README and any affected agent or workflow guidance.

---

## 10. Definition of Failure

This repository is failing its purpose when:

- contributors cannot tell which document governs a decision
- multiple files describe the same concern differently
- agents encourage patterns that conflict with the docs
- copied guidance is too abstract to shape real work
- the repo grows by adding documents faster than it improves clarity

The goal is not to maximize documentation count. The goal is to maximize clarity, alignment, and useful decision support.
