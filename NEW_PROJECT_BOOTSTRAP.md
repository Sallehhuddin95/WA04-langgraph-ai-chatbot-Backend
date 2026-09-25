# New Project Bootstrap Checklist

Use this checklist when you create a new repo and want to apply this guidelines repository effectively without copying unnecessary material.

---

## 1. Confirm the Project Shape

Before copying anything, decide:

- is the repo frontend only, backend only, mobile only, or some combination?
- what framework and runtime will actually be used?
- will the team use specs, ADRs, and custom agents (Copilot and/or opencode) from day one?

Do not copy guidance for stacks or workflows the project will not use.

---

## 2. Copy the Minimum Baseline

Always start with:

- `docs/architecture/`
- `docs/shared/`
- `docs/adr/README.md`
- `specs/README.md`

Then add only what matches the project:

- `docs/frontend/` for frontend work
- `docs/backend/` for backend work
- `docs/mobile/` for mobile (React Native/Expo) work
- `docs/workflow/` if the team will actually follow workflow docs
- `.github/agents/` if the repo will use Copilot custom agents
- `.opencode/` if the repo will use opencode agents

---

## 3. Tailor the Copied Docs Immediately

Update the copied files so they describe the real project.

Check:

- architecture boundaries
- naming rules
- testing approach
- auth model
- API contract expectations
- release and review flow

Remove or rewrite anything that does not match reality.

---

## 4. Keep Only True ADRs

If you copy ADRs from this repo:

- keep only the decisions that are already true in the new project
- rewrite any ADR that needs different wording or scope
- delete copied ADRs from the new repo if they are not actually adopted there

ADR history should reflect real decisions, not inherited assumptions.

---

## 5. Set the Day-1 Working Rules

Before feature work starts, make sure the team knows:

- where code should live
- what dependencies are allowed
- how naming should work
- how testing should work
- how auth, error handling, and contracts are enforced
- when to write a spec
- when to write an ADR

If these are not explicit early, the copied docs will not shape implementation.

---

## 6. Write the First Spec Before the First Real Feature

For the first meaningful feature, API, or workflow:

1. create a narrow spec
2. align the implementation to that spec
3. review against the architecture and shared rules

This is the point where the new repo starts using the guidance rather than just storing it.

---

## 7. Add Agents Only If They Will Be Used

If the team uses custom agents:

- copy the relevant agent files from `.github/agents/` (Copilot) and/or `.opencode/` (opencode)
- make sure every referenced doc exists in the new repo
- remove agents that do not match the project stack

If the team will not use agents, skip them. Dead agent configuration is noise.

---

## 8. Review After the First Week

After the first few changes in the new repo, check:

- which docs were actually used
- which rules were unclear
- which copied files were unnecessary
- whether a new ADR is needed
- whether the specs flow is too heavy or too light

Then simplify or strengthen the documentation set based on real usage.

---

## Minimal Defaults

If you want the lightest useful setup, use this minimum:

1. `docs/architecture/`
2. `docs/shared/`
3. one stack-specific folder: `docs/frontend/` or `docs/backend/`
4. `docs/adr/README.md`
5. `specs/README.md`

That is usually enough to start a clean repo without over-documenting it.
