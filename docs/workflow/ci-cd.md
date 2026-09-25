# CI/CD Workflow

This document defines the expected continuous integration and delivery behavior for the project.

It covers both GitHub Actions and Jenkins. The pipeline expectations are the same regardless of the tool.

Use it with `docs/workflow/release.md` and `docs/shared/versioning.md`.

---

## 1. Core Principles

- CI is a quality gate, not a formality.
- Pipelines should be reproducible: what runs in CI should be runnable locally.
- Failures must be visible, actionable, and never silently ignored.
- Secrets belong in the CI secret store, never in workflow files or repository files.
- CD should deploy only what CI already validated.

---

## 2. Minimum Pipeline Stages

Every project should run at least these stages in CI:

- static analysis and linting
- type checking
- unit tests
- build or bundling
- integration tests for bounded slices
- contract or schema checks where contracts exist

Treat `docs/shared/static-analysis.md` as the rule set for tool findings in CI.

Security-sensitive projects should also run dependency scanning and secret scanning.

---

## 3. PR Gating Rules

- Required checks must pass before a pull request merges.
- The main branch should be protected from direct pushes.
- Do not allow merge bypasses for failing checks as a habit.
- Flaky tests are defects. Fix them or quarantine them with an explicit ticket, do not disable them silently.

---

## 4. Branch and Trigger Rules

- Run CI on every pull request and on pushes to main.
- Deploy to production only from main or an explicit release branch or tag.
- Prefer manual approval for production deploys.
- Keep staging and production promotion explicit in the pipeline, not ad hoc.

---

## 5. Secrets and Credentials

- Store credentials in the CI tool secret store (GitHub Actions secrets or Jenkins credentials).
- Never commit secrets, tokens, or private keys to the repository.
- Scope credentials to the smallest permission set required.
- Rotate credentials on a schedule or when a breach is suspected.

---

## 6. Tool Choice

Each project should pick one CI/CD tool and use it consistently:

- GitHub Actions when the repo lives on GitHub and native integration is enough
- Jenkins when self-hosted infrastructure, existing build farms, or non-GitHub repos require it

Rules:

- Do not run two overlapping CI systems for the same repo.
- Keep the pipeline stages in section 2 identical regardless of tool.
- Record a major tool choice as an ADR when it affects delivery standards.

---

## 7. Pipeline Configuration as Code

- Store pipeline definitions in the repository when the tool supports it.
- Review pipeline changes like code changes.
- Keep pipeline definitions small enough to understand at a glance.
- Prefer shared, versioned helper steps over copied step blocks.

---

## 8. Failure Handling

- A red build or blocked merge is a first-class problem, not background noise.
- Investigate failures promptly and fix the root cause.
- If a failure is not actionable, make it actionable: add logs, split stages, or isolate the flake.
- Never green a pipeline by weakening checks without a documented reason.

---

## 9. Release Alignment

- The release steps must follow `docs/workflow/release.md`.
- Version bumps and contract evolution must follow `docs/shared/versioning.md`.
- Build artifacts should be traceable to the commit and tag that produced them.
- Production deploys should be reversible or at least explicitly rollback-ready.

---

## 10. Completion Checklist

- Do required checks run on every pull request and main push?
- Are main protection and merge gating enforced?
- Are secrets stored only in the CI secret store?
- Are pipeline definitions stored and reviewed as code?
- Are flaky or failing checks treated as defects, not silenced?
- Does the pipeline align with release and versioning docs?
- Is one CI/CD tool chosen and used consistently?