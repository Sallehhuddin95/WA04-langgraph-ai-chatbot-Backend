# Dependency Rules

This document defines allowed dependency direction and prohibited coupling patterns.

These rules are required to keep the project predictable for both human contributors and AI agents.

---

## 1. General Rule

Dependencies must flow toward stable, lower-volatility modules.

Prefer:

- app layer depends on feature entry points
- feature modules depend on shared infrastructure and local contracts
- shared modules remain domain-agnostic

Avoid:

- shared modules depending on features
- circular dependencies across features
- route layers depending on feature internals in inconsistent ways

---

## 2. Frontend Dependency Direction

Allowed direction:

1. `app` -> `features`
2. `features` -> `shared` or stable infrastructure
3. `components/ui`, `hooks`, `lib`, `utils`, `types` remain generic

Disallowed direction:

1. `shared` -> `features`
2. one feature importing another feature's private internals
3. route files importing scattered transport helpers instead of feature entry points when a feature boundary exists

---

## 3. Mobile Dependency Direction

Allowed direction:

1. `app` (Expo Router entry/screens) -> `features`
2. `features` -> `shared` or stable infrastructure
3. `components/ui`, `hooks`, `lib`, `utils`, `types` remain generic

Disallowed direction:

1. `shared` -> `features`
2. one feature importing another feature's private internals
3. screen/route files importing scattered transport helpers instead of feature entry points when a feature boundary exists

Mobile follows the same dependency direction as web frontend. Do not introduce a second, incompatible dependency model for mobile without a documented reason (see `docs/adr/`).

---

## 4. Import Rules

- Prefer feature public APIs when a feature exports one.
- Do not deep-import into another module's internal implementation without explicit justification.
- Keep relative imports local when the scope is truly local.
- Use stable aliases for shared or cross-folder imports when configured.

---

## 5. Shared Code Promotion Rules

Promote code into shared space only when:

- multiple independent features use it
- its behavior is truly domain-agnostic
- its public contract is stable enough to be reused safely

Do not promote code only to reduce file count or to satisfy premature DRY instincts.

---

## 6. External Dependency Discipline

- Add new libraries only when project conventions or native platform features are insufficient.
- Avoid overlapping libraries for the same responsibility.
- Prefer explicit wrappers around important third-party integrations.
- Keep external dependencies from leaking framework-specific assumptions into unrelated modules.

---

## 7. Change Review Questions

Before merging a structural change, ask:

- Does this introduce a new dependency direction?
- Does this bypass a feature boundary?
- Does this create a second pattern for an already-solved concern?
- Should this decision be recorded as an ADR?
