# Backend Architecture and Development Guidelines

This document defines architecture, folder structure, validation boundaries, data access rules, security expectations, and testing standards for the FastAPI backend.

The backend stack is:

- FastAPI
- PostgreSQL
- Alembic
- uv
- Pydantic v2
- pytest

All backend code must follow SOLID and DRY pragmatically, with strong preference for explicit boundaries and maintainable service design.

---

## 1. Core Stack

### Runtime and Framework

- Framework: FastAPI
- Python package and environment management: uv
- Data store: PostgreSQL
- Migrations: Alembic
- Validation and serialization: Pydantic v2
- Testing: pytest

---

## 2. Backend Architecture Shape

Use a layered backend structure with clear ownership boundaries.

Preferred structure:

```text
backend/
├── routes/          # HTTP entrypoints and transport mapping
├── schemas/         # Pydantic request/response contracts
├── services/        # business workflows and orchestration
├── repositories/    # persistence access and query boundaries
├── models/          # persistence-facing models/entities
├── db/              # engine, session, and database infrastructure
├── core/            # config, security, shared backend primitives
└── tests/           # pytest suites
```

Required flow:

1. `routes` accept HTTP requests and map them to service calls.
2. `schemas` define validated input and output contracts.
3. `services` enforce business logic and orchestration.
4. `repositories` perform database interaction.
5. `models` represent persistence structures.

---

## 3. Layer Responsibilities

### Routes

Routes may:

- define endpoints
- parse validated inputs
- invoke services
- map service results to response contracts
- raise or translate HTTP-facing errors

Routes must not:

- hold business rules
- perform direct database access when a repository boundary exists
- contain large data transformation logic better suited to services or schemas

### Schemas

Schemas may:

- validate requests
- serialize responses
- normalize transport-facing fields

Schemas must not:

- contain persistence access
- contain workflow orchestration

### Services

Services may:

- enforce business rules
- coordinate repositories and cross-cutting concerns
- enforce authorization or ownership rules with validated auth context
- define transaction-level workflow boundaries where appropriate

Services must not:

- become transport-aware beyond what the use case requires
- leak raw repository internals upward unnecessarily

### Repositories

Repositories may:

- query and persist data
- encapsulate persistence-specific filtering and lookup behavior

Repositories must not:

- enforce unrelated transport or HTTP behavior
- become business workflow coordinators

### Models

Models represent persistence-facing structures and should remain aligned with repository and migration discipline.

---

## 4. SOLID and DRY Rules

Apply SOLID and DRY as practical guardrails, not as excuses for premature abstraction.

- Single responsibility:
  - routes handle HTTP transport
  - schemas validate transport contracts
  - services enforce business behavior
  - repositories own persistence interaction
- Open/closed:
  - extend behavior through clear service composition and well-scoped abstractions
- Interface segregation:
  - keep request, response, and service inputs narrow and purposeful
- Dependency inversion:
  - services depend on stable repository and contract boundaries, not scattered persistence details
- DRY:
  - remove repeated logic only when reuse is clear and stable
  - do not centralize unrelated behavior into giant helper modules

---

## 5. Validation and Contract Boundaries

- Validate all external input at the API boundary.
- Use explicit Pydantic v2 schemas for request and response models.
- Do not trust frontend payload shape, field presence, field ownership, or hidden UI restrictions.
- Reject malformed, unauthorized, or out-of-contract payload changes with explicit client error responses.
- Never rely on the frontend to prevent forbidden field changes.

---

## 6. Security and Server Trust Rules

The backend must treat the client as untrusted.

- Every request must be validated on the server.
- Ownership and permission-sensitive fields must be derived from authenticated server context where possible, not accepted blindly from the client.
- If a user intercepts and changes a payload, the backend must reject unauthorized or invalid changes with a failure response.
- A tampered payload must never succeed only because the frontend originally hid or disabled the field.
- Mass-assignment style behavior must be avoided; only allow explicit fields to be accepted and persisted.

---

## 7. Database and Migration Rules

- PostgreSQL is the source of persistent truth.
- Schema changes must be tracked through Alembic.
- Migrations must be explicit, reviewable, and reversible where practical.
- Application code and schema changes must remain compatible throughout the intended deployment sequence.

---

## 8. Testing Expectations

Use pytest to validate backend behavior at the right level.

- route tests validate transport behavior, status codes, and contract mapping
- service tests validate business rules and orchestration
- repository tests validate persistence behavior where needed
- integration tests validate important end-to-end backend slices

Prefer the smallest sufficient test layer for the risk being covered.

---

## 9. Review Checklist

- Are routes thin and transport-focused?
- Are schemas explicit and Pydantic v2 based?
- Does business logic live in services rather than routes or repositories?
- Are repositories the only place persistence access is coordinated?
- Are tampered or unauthorized payload changes rejected on the server?
- Are migrations and contracts aligned with the code change?

---

## Dedicated Guides

For backend-specific detail, refer to:

- `naming.md`: naming, casing, and backend symbol conventions.
- `api-design.md`: endpoint, request, response, and status code design.
- `database.md`: repository and persistence boundaries.
- `migrations.md`: Alembic migration discipline.
- `security.md`: server trust rules and tamper-resistant request handling.
- `testing.md`: pytest strategy and validation coverage.
