# Agent Usage Guide

Use this file to decide which Copilot custom agent to use for a given task.

These agents are not interchangeable. Each one is tuned for a different kind of work.

---

## Quick Selector

Use:

- `Architect` when the question is about structure, boundaries, dependency direction, or whether a change needs an ADR or spec update
- `Next.js Feature-Driven Architect` when implementing or shaping frontend work in a Next.js App Router codebase
- `Angular Feature-Driven Architect` when implementing or shaping frontend work in an Angular (standalone components) codebase
- `FastAPI Service Architect` when implementing or shaping backend work in a FastAPI codebase
- `Django Service Architect` when implementing or shaping backend work in a Django codebase
- `Express Service Architect` when implementing or shaping backend work in an Express + TypeScript codebase
- `React Native Mobile Architect` when implementing or shaping mobile work in a React Native (Expo) codebase
- `Reviewer` when you want findings, risks, regressions, and missing tests before merge
- `Tester` when you want test strategy, test design, or test implementation guidance
- `Refactor` when you want structure improvement without changing intended behavior
- `Documentation` when you want docs, ADRs, specs, workflow guides, or conventions kept aligned with reality

---

## Comparison Table

| Agent                              | Goal                            | Best For                                                                                         | Avoid When                                                     |
| ---------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| `Architect`                        | Protect architecture quality    | boundaries, dependency direction, ADR/spec decisions, ownership questions                        | routine feature implementation                                 |
| `Next.js Feature-Driven Architect` | Build frontend work correctly   | Next.js feature implementation, rendering choices, frontend structure, frontend testing patterns | backend tasks, review-only work, doc-only work                 |
| `Angular Feature-Driven Architect` | Build frontend work correctly   | Angular standalone feature implementation, server-state and signals, frontend structure, testing | backend tasks, review-only work, doc-only work                 |
| `FastAPI Service Architect`        | Build backend work correctly    | FastAPI endpoints, service layering, contracts, validation, server trust boundaries              | frontend tasks, review-only work, doc-only work                |
| `Django Service Architect`        | Build backend work correctly    | Django apps, DRF contracts, service layering, migrations, server trust boundaries                | frontend tasks, review-only work, doc-only work                |
| `Express Service Architect`       | Build backend work correctly    | Express routes, zod contracts, service layering, Prisma repositories, server trust boundaries    | frontend tasks, review-only work, doc-only work                |
| `React Native Mobile Architect`    | Build mobile work correctly     | React Native (Expo) screens, navigation, secure token storage, mobile testing patterns           | frontend or backend tasks, review-only work, doc-only work     |
| `Reviewer`                         | Evaluate merge readiness        | bugs, regressions, architecture drift, security risk, missing tests                              | net-new implementation                                         |
| `Tester`                           | Design and implement validation | test strategy, right test layer, regression coverage, auth/contract/error tests                  | primary feature implementation, general architecture decisions |
| `Refactor`                         | Improve structure safely        | cleanup, duplication reduction, naming, boundary repair, behavior-preserving change              | net-new features, review-only work                             |
| `Documentation`                    | Keep docs aligned with reality  | ADRs, workflow docs, specs, architecture docs, cross-doc consistency                             | feature implementation, deep code review, test-only work       |

---

## When to Use Each Agent

### Architect

Use this agent when you need help with:

- deciding where code should live
- checking module boundaries
- checking dependency direction
- identifying architecture drift
- deciding whether a change needs an ADR
- deciding whether a spec or workflow doc should be updated

Good prompts:

- `Review this feature plan for boundary issues.`
- `Should this shared helper stay in shared or move into a feature module?`
- `Does this change need an ADR?`

Do not use this agent as your default implementation agent.

### Next.js Feature-Driven Architect

Use this agent when the task is frontend implementation or frontend design within a Next.js App Router project.

Best for:

- feature structure
- server vs client component decisions
- TanStack Query usage
- frontend error handling
- frontend testing coverage decisions
- enforcing the frontend guideline during implementation

Good prompts:

- `Implement this dashboard feature using the local frontend guideline.`
- `Where should these hooks, services, and types live in this Next.js feature?`
- `Add tests for this client-side query flow.`

Use this only when the target repo actually uses the documented Next.js-oriented stack.

### FastAPI Service Architect

Use this agent when the task is backend implementation or backend design in a FastAPI project.

Best for:

- route, schema, service, repository, and model boundaries
- API contract shaping
- Pydantic v2 validation design
- server-side auth and trust-boundary enforcement
- Alembic and PostgreSQL-aware backend decisions

Good prompts:

- `Design this endpoint using the backend guideline.`
- `Refactor this route so business logic moves into the service layer.`
- `Add validation and tests for this protected-field update flow.`

Use this only when the target repo actually uses the documented FastAPI-oriented stack.

### React Native Mobile Architect

Use this agent when the task is mobile implementation or mobile design in a React Native (Expo) project.

Best for:

- feature/screen structure
- Expo Router navigation decisions
- TanStack Query usage on mobile
- secure token storage and auth-aware navigation
- mobile testing coverage decisions (Jest/RNTL/Maestro)

Good prompts:

- `Implement this onboarding flow using the local mobile guideline.`
- `Where should these hooks, services, and types live in this Expo feature?`
- `Add tests for this screen's async data flow.`

Use this only when the target repo actually uses the documented React Native (Expo) stack.

### Reviewer

Use this agent when you want a merge-readiness review.

Best for:

- bug finding
- regression risk detection
- architecture drift detection
- security-sensitive review
- missing or weak test identification

Good prompts:

- `Review this PR for correctness and regression risk.`
- `Look for contract, auth, and testing issues in these changes.`

Use this after implementation or when evaluating an in-progress diff.

### Tester

Use this agent when you need help choosing or writing tests.

Best for:

- deciding the right test layer
- designing meaningful test cases
- improving regression coverage
- validating contracts, auth flows, and error behavior

Good prompts:

- `What is the smallest sufficient test coverage for this change?`
- `Add integration tests for this async UI flow.`
- `Design pytest coverage for this service and route behavior.`

Use this when the main problem is validation quality, not implementation structure.

### Refactor

Use this agent when the goal is to improve code structure without intentionally changing behavior.

Best for:

- cleanup of messy modules
- duplication reduction after reuse is proven
- module boundary repair
- naming and placement improvement
- incremental structural simplification

Good prompts:

- `Refactor this feature to reduce coupling without behavior changes.`
- `Clean up this module and keep behavior stable.`

Do not use this when the real task is a new feature or a product redesign.

### Documentation

Use this agent when the main deliverable is documentation accuracy or documentation maintenance.

Best for:

- updating architecture docs
- updating workflow docs
- adding or revising ADRs
- updating specs after behavior changes
- keeping guidance aligned with current implementation

Good prompts:

- `Update the docs to reflect this new auth rule.`
- `Write an ADR for this architecture decision.`
- `Align the workflow docs with the current release process.`

Use this when the output should primarily be governance or specification content.

---

## Simple Decision Rules

If the main question is:

- `Where should this go?` use `Architect`
- `How should I build this frontend work?` use `Next.js Feature-Driven Architect` or `Angular Feature-Driven Architect`
- `How should I build this backend work?` use `FastAPI Service Architect`, `Django Service Architect`, or `Express Service Architect`
- `How should I build this mobile work?` use `React Native Mobile Architect`
- `Is this safe and correct to merge?` use `Reviewer`
- `How should this be tested?` use `Tester`
- `How can I clean this up safely?` use `Refactor`
- `Which docs or ADRs should change?` use `Documentation`

---

## Practical Rule

Choose the agent based on the main decision the task requires, not just the file type.

For example:

- a frontend file with boundary problems may still need `Architect`
- a backend change that mainly needs test coverage may still need `Tester`
- a code change that is ready for evaluation may need `Reviewer` rather than an implementation agent
