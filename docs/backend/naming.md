# Backend Naming Conventions

This document defines naming rules for the FastAPI backend.

The goal is to keep route handlers, schemas, services, repositories, models, migrations, and tests predictable and consistent across the backend.

---

## 1. Naming Principles

- Prefer explicit, business-meaningful names over short generic names.
- Keep one concept under one stable name across routes, schemas, services, repositories, and tests.
- Use names that reveal layer responsibility.
- Avoid suffix noise unless it clarifies intent.
- Code identifiers must be English by default, even when the app UI is in another language. See `docs/shared/identifier-language.md`.

---

## 2. File and Module Naming

Use Python module naming rules consistently.

| Element            | Rule                                          | Example                                 |
| ------------------ | --------------------------------------------- | --------------------------------------- |
| Python files       | `snake_case.py`                               | `user_profile.py`                       |
| Route modules      | `snake_case.py` by resource or capability     | `auth.py`, `billing.py`                 |
| Schema modules     | `snake_case.py` by bounded concern            | `user_schema.py`, `invoice_schema.py`   |
| Service modules    | `snake_case.py` by use case or domain concern | `user_service.py`, `billing_service.py` |
| Repository modules | `snake_case.py` by aggregate or resource      | `user_repository.py`                    |
| Model modules      | `snake_case.py` by entity                     | `user.py`, `invoice.py`                 |
| Test files         | `test_*.py`                                   | `test_auth_routes.py`                   |

Rules:

- Do not use ambiguous names like `helpers.py`, `misc.py`, or `common.py` unless the contents are truly generic and stable.
- Prefer explicit file names over oversized catch-all modules.

---

## 3. Class Naming

- Use `PascalCase` for classes.
- Pydantic schemas, ORM models, and exception classes should use names that reveal their role.

Examples:

- `UserCreateRequest`
- `UserResponse`
- `UserModel`
- `UserRepository`
- `UserService`
- `AuthorizationError`

---

## 4. Function and Variable Naming

- Use `snake_case`.
- Use verb-first names for behavior.
- Use clear boolean prefixes such as `is_`, `has_`, `can_`, or `should_`.

Examples:

- `get_user_by_id`
- `create_session`
- `update_invoice_status`
- `is_active`
- `has_access`

---

## 5. Route Handler Naming

- Name route handlers by the action they perform.
- Avoid generic names like `handler` or `process`.

Examples:

- `create_user`
- `list_invoices`
- `refresh_session`

Route paths should remain transport-facing and resource-revealing. Function names should remain implementation-facing and action-revealing.

---

## 6. Schema Naming

Use role-revealing schema names.

Recommended suffixes:

- `Request` for request bodies
- `Response` for response payloads
- `Params` for path or query input groupings when needed
- `Filter` for validated filtering inputs

Examples:

- `CreateUserRequest`
- `UserResponse`
- `ListInvoicesParams`

Avoid weak names like `UserSchema` when the schema role can be made explicit.

---

## 7. Service and Repository Naming

- Service classes or modules should be named by the domain capability they coordinate.
- Repository classes or modules should be named by the entity or aggregate they persist.

Examples:

- `UserService`
- `BillingService`
- `UserRepository`
- `InvoiceRepository`

Use method names that reveal business or persistence intent clearly:

- `create_user`
- `get_active_subscription`
- `save_invoice`
- `list_visible_projects`

---

## 8. Model Naming

- Use stable entity-oriented names for persistence models.
- If disambiguation is needed between ORM model and domain contract, make it explicit.

Examples:

- `User`
- `Invoice`
- `AuditLog`
- `UserModel` when a plain `User` name is already owned by another layer

---

## 9. Exception Naming

- Use explicit error names tied to the domain or failure class.
- Prefer names that communicate meaning rather than transport status alone.

Examples:

- `AuthenticationError`
- `AuthorizationError`
- `ResourceConflictError`
- `InvalidStateError`

---

## 10. Constant Naming

- Use `UPPER_SNAKE_CASE` for module-level constants.
- Keep constant names specific and purpose-revealing.

Examples:

- `DEFAULT_PAGE_SIZE`
- `MAX_LOGIN_ATTEMPTS`
- `ACCESS_TOKEN_TTL_MINUTES`

---

## 11. Review Checklist

- Are module names explicit and `snake_case`?
- Do classes use `PascalCase` and reveal layer role?
- Do schema names make request and response roles obvious?
- Are service and repository names aligned with actual ownership?
- Are function names verb-first and business-meaningful?
- Are ambiguous catch-all names avoided?
