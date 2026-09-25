# Module Boundaries

This document defines which modules own which responsibilities and where code should live.

Strong module boundaries are required to keep the codebase maintainable and to prevent silent architecture drift.

---

## 1. Core Boundary Rule

Every module should have a clear reason to exist and a narrow responsibility. If ownership is unclear, the code is probably in the wrong place.

---

## 2. Frontend Boundaries

### App Layer

The app or route layer may:

- define routes and layouts
- coordinate top-level rendering behavior
- invoke feature entry points
- define route-level loading and error boundaries

The app or route layer must not:

- hold feature business logic
- become the primary location for data transformation rules
- implement reusable feature services directly

### Feature Modules

Feature modules may:

- define business-facing UI
- define feature hooks and service wrappers
- hold feature-local schemas and types
- coordinate feature-specific workflows

Feature modules must not:

- import private internals from another feature
- leak domain-specific logic into shared folders without proven reuse

### Mobile Boundaries

Mobile (React Native/Expo) follows the same layering model as web frontend, adapted for a native runtime.

The app/entry layer (for example Expo Router `app/`) may:

- define routes, screens, and navigation structure
- coordinate top-level rendering and layout behavior
- invoke feature entry points
- define route-level loading and error boundaries

The app/entry layer must not:

- hold feature business logic
- become the primary location for data transformation rules
- implement reusable feature services directly

Mobile feature modules follow the same ownership rules as web feature modules above, and mobile shares the Shared Modules rules defined in this document. Do not duplicate mobile-specific shared logic into web-only folders or vice versa; keep `docs/frontend/`, `docs/backend/`, and `docs/mobile/` as independent stack boundaries.

### Shared Modules

Shared modules may:

- provide reusable, domain-agnostic primitives
- provide infrastructure helpers
- provide generic utilities and contracts

Shared modules must not:

- depend on feature-specific business rules
- become a dumping ground for unclear code ownership

---

## 3. Cross-Feature Interaction

Cross-feature dependencies should be minimized.

Rules:

- Prefer independent feature ownership.
- If multiple features need the same concept, hoist a stable abstraction deliberately.
- If one feature needs another feature's internal detail, the boundary is likely wrong.

---

## 4. Service and Integration Boundaries

Network and integration logic should be isolated.

Rules:

- UI components should not directly own transport details.
- Service modules should expose meaningful business actions, not only raw request plumbing.
- Validation and transformation should happen near the contract boundary, not scattered through unrelated views.

---

## 5. Testing Boundaries

Testing modules must respect architectural ownership.

- unit tests validate isolated logic
- integration tests validate behavior across a bounded slice
- e2e tests validate user journeys and route-level behavior

Tests should reinforce boundaries, not blur them.

---

## 6. Documentation Boundaries

Project documentation should also follow boundaries:

- architecture docs define structural rules
- frontend docs define frontend-specific rules
- backend docs define backend-specific rules
- mobile docs define mobile-specific rules
- shared docs define cross-stack rules
- workflow docs define process
- ADRs define why major decisions exist

---

## 7. Boundary Smells

Review code placement when you see:

- route files growing into feature controllers
- one feature importing another feature's internal files
- shared folders filled with domain-specific logic
- repeated auth or error logic per feature
- utility folders owning business rules

These are signs that the boundary model is being violated.
