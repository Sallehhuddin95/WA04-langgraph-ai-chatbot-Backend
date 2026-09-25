# Code Review Workflow

This document defines the expected review process for changes.

Review is not only for correctness. It also protects architecture, consistency, and maintainability.

---

## 1. Primary Review Priorities

Review in this order:

1. correctness
2. regression risk
3. architecture and boundary compliance
4. security and data exposure
5. testing adequacy
6. maintainability and clarity

---

## 2. Reviewer Expectations

Reviewers should ask:

- Does the code do the right thing?
- Does it break any existing contract or workflow?
- Does it respect architecture and feature ownership?
- Are auth, error, and validation concerns handled consistently?
- Are tests sufficient for the risk level?
- Is the change understandable six months from now?

---

## 3. Review Rules

- Prefer concrete findings over vague style preferences.
- Flag new patterns that compete with existing standards.
- Separate must-fix issues from optional improvements.
- Do not accept architectural drift because the change is small.

---

## 4. Author Expectations

Authors should provide enough context for efficient review:

- what changed
- why it changed
- how it was validated
- what docs or specs were updated
- whether any tradeoff or follow-up remains open

---

## 5. Completion Checklist

- Are there unresolved correctness or risk concerns?
- Does the change conform to architecture and shared rules?
- Are tests and validation appropriate?
- Are follow-up items explicit if anything is intentionally deferred?
- Are static analysis findings fixed or consciously dismissed per `docs/shared/static-analysis.md`?
- Does any new or changed text follow `docs/shared/writing-style.md` (no em or en dashes, no AI-typical phrasing)?
