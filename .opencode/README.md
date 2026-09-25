# opencode Usage Guide

This folder ships opencode configuration and custom agents that mirror the Copilot custom agents in `.github/agents/`.

It lets a target repo use the same governance with [opencode](https://opencode.ai) instead of Copilot. Both agent sets share the same prompts and point at the same `docs/` and `specs/` sources of truth, so they behave consistently.

---

## What Is Installed

- `opencode.json`: loads the repo rules (`CONSTITUTION.md`, `docs/architecture/`, `docs/shared/`, `docs/adr/README.md`) into every opencode session via `instructions`.
- `agents/`: eleven custom agents, one per Copilot agent.

opencode loads project config from `.opencode/` automatically when you run `opencode` in the repo root. No extra setup is required.

---

## How to Use the Agents

The agents are defined as `mode: all`, so they work both ways:

- **Primary agents**: press **Tab** in the TUI to cycle to them, then use them as your main conversation agent.
- **Subagents**: `@mention` them in any message, e.g. `@reviewer review these changes`.

The build agent (default) can also invoke them automatically based on their descriptions.

---

## Quick Selector

Use:

- `architect` when the question is about structure, boundaries, dependency direction, or whether a change needs an ADR or spec update
- `nextjs-architect` when implementing or shaping frontend work in a Next.js App Router codebase
- `angular-architect` when implementing or shaping frontend work in an Angular (standalone components) codebase
- `fastapi-architect` when implementing or shaping backend work in a FastAPI codebase
- `django-architect` when implementing or shaping backend work in a Django codebase
- `express-architect` when implementing or shaping backend work in an Express + TypeScript codebase
- `react-native-architect` when implementing or shaping mobile work in a React Native (Expo) codebase
- `reviewer` when you want findings, risks, regressions, and missing tests before merge
- `tester` when you want test strategy, test design, or test implementation guidance
- `refactor` when you want structure improvement without changing intended behavior
- `documentation` when you want docs, ADRs, specs, workflow guides, or conventions kept aligned with reality

---

## Agent Comparison

| Agent                    | Goal                            | Best For                                                                                         | Avoid When                                                     |
| ------------------------ | ------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| `architect`              | Protect architecture quality    | boundaries, dependency direction, ADR/spec decisions, ownership questions                        | routine feature implementation                                 |
| `nextjs-architect`       | Build frontend work correctly   | Next.js feature implementation, rendering choices, frontend structure, frontend testing patterns | backend tasks, review-only work, doc-only work                 |
| `angular-architect`      | Build frontend work correctly   | Angular standalone feature implementation, server-state and signals, frontend structure, testing | backend tasks, review-only work, doc-only work                 |
| `fastapi-architect`      | Build backend work correctly    | FastAPI endpoints, service layering, contracts, validation, server trust boundaries              | frontend tasks, review-only work, doc-only work                |
| `django-architect`       | Build backend work correctly    | Django apps, DRF contracts, service layering, migrations, server trust boundaries                | frontend tasks, review-only work, doc-only work                |
| `express-architect`      | Build backend work correctly    | Express routes, zod contracts, service layering, Prisma repositories, server trust boundaries    | frontend tasks, review-only work, doc-only work                |
| `react-native-architect` | Build mobile work correctly     | React Native (Expo) screens, navigation, secure token storage, mobile testing patterns           | frontend or backend tasks, review-only work, doc-only work     |
| `reviewer`               | Evaluate merge readiness        | bugs, regressions, architecture drift, security risk, missing tests                              | net-new implementation                                         |
| `tester`                 | Design and implement validation | test strategy, right test layer, regression coverage, auth/contract/error tests                  | primary feature implementation, general architecture decisions |
| `refactor`               | Improve structure safely        | cleanup, duplication reduction, naming, boundary repair, behavior-preserving change              | net-new features, review-only work                             |
| `documentation`          | Keep docs aligned with reality  | ADRs, workflow docs, specs, architecture docs, cross-doc consistency                             | feature implementation, deep code review, test-only work       |

---

## Simple Decision Rules

If the main question is:

- `Where should this go?` use `@architect`
- `How should I build this frontend work?` use `@nextjs-architect` or `@angular-architect`
- `How should I build this backend work?` use `@fastapi-architect`, `@django-architect`, or `@express-architect`
- `How should I build this mobile work?` use `@react-native-architect`
- `Is this safe and correct to merge?` use `@reviewer`
- `How should this be tested?` use `@tester`
- `How can I clean this up safely?` use `@refactor`
- `Which docs or ADRs should change?` use `@documentation`

---

## Notes

- The agents read `docs/` and `specs/` from the target repo, so the referenced guidance must exist there. The installer copies the matching docs alongside `.opencode/`.
- Agents use the default configured model; they do not pin a provider.
- If you edit `.opencode/`, quit and restart opencode so the changes take effect.
