# API Specs

API specs define request, response, validation, and error behavior for transport contracts.

Use these specs alongside shared API contract guidance in `docs/shared/api-contract.md`.

If compatibility, deprecation, or route versioning is relevant, also follow `docs/shared/versioning.md`.

---

## Template

```md
# API Contract Name

## Status

Draft

## Endpoint or Operation

`METHOD /path`

## Purpose

What does this contract do?

## Authentication

What auth or permission rules apply?

## Request

### Params

### Query

### Headers

### Body

## Response

### Success Shape

### Error Shapes

## Validation Rules

What inputs are required, optional, or constrained?

## Notes

Any versioning, pagination, or compatibility expectations.
```

---

## Writing Rules

- Keep request and response shapes explicit.
- Document validation and error payload behavior.
- Record auth requirements and permission expectations.
- Document any compatibility, deprecation, or versioning rule when it affects the contract.
- Reference OpenAPI or generated schemas if they exist.
