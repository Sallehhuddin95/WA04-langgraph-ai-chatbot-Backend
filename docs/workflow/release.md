# Release Workflow

This document defines the minimum workflow for preparing and validating releases.

The goal is to reduce avoidable regressions and make release readiness explicit.

---

## 1. Release Readiness Principles

- Release quality is the result of consistent validation, not late-stage heroics.
- Critical flows must be validated before release.
- Known risks should be explicit, not discovered accidentally after deployment.

---

## 2. Pre-Release Checks

Before release, confirm:

- core tests pass
- critical feature flows are validated
- authentication and authorization flows are still correct
- error states remain usable
- contract changes are documented
- any required environment or migration steps are known

---

## 3. Release Validation Areas

At minimum, review:

- critical routes and user journeys
- login and protected areas if auth exists
- primary create, update, and read workflows
- failure and retry behavior for important operations
- any newly introduced contract or schema changes

---

## 4. Documentation Expectations

Release-affecting changes should keep documentation aligned:

- specs updated when behavior changed
- ADRs updated when architecture direction changed
- workflow or shared rules updated when conventions changed
- versioning and compatibility notes updated when contract or release semantics changed

---

## 5. Versioning Checks

Before release, confirm:

- any breaking API or contract changes are identified explicitly
- any required route or contract version changes follow `docs/shared/versioning.md`
- deprecations remain documented and time-bounded
- release version numbers match the intended change scope

---

## 6. Completion Checklist

- Is the release scope understood?
- Are critical validations complete?
- Are contract and auth-sensitive changes confirmed?
- Are versioning implications understood and documented?
- Are known risks documented clearly?
- Are required follow-up tasks explicit?
