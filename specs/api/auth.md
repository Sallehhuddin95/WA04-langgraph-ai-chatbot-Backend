# Auth API

## Status

Accepted

## Endpoint or Operation

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

No `/v1` prefix. Additive changes only. Contract rules follow `docs/shared/api-contract.md` and `docs/backend/api-design.md`.

## Purpose

Issue server-managed session cookies for chat. Chat endpoints keep requiring the cookie per `specs/api/chat-api.md` and ADR 0008.

## Authentication

Cookie named `session`:

- `httpOnly`, `SameSite=Lax`, path `/`, 30 day expiry
- `Secure` is off for local http dev and must be on in production
- value is a random token, only its SHA256 hash persists
- raw tokens never appear in logs

## Request

### POST /api/auth/signup, 201

Body (`SignupRequest`):

```json
{
  "email": "user@example.com",
  "password": "secret-password"
}
```

- `email`: valid format, max 320 chars, stored lowercased
- `password`: 8-72 chars, bcrypt hash persisted (72 byte limit, ascii)
- duplicate email returns 409 `conflict`

### POST /api/auth/login, 200

Body (`LoginRequest`): same shape, password min 1 char.

- unknown email and wrong password both return 401 `unauthorized` with identical copy
- success sets a fresh session cookie

### POST /api/auth/logout, 200

- deletes the session row, clears the cookie
- always returns `{"status": "ok"}` even without a cookie

### GET /api/auth/me, 200

- returns `{user_id, email}` for a valid session
- returns 401 `unauthorized` otherwise

## Response

Success shape (`AuthUserResponse`):

```json
{
  "user_id": "uuid",
  "email": "user@example.com"
}
```

### Error Shapes

Envelope matches chat: `{error: {code, message, trace_id}}`.

Code map:

- `201`: signup created
- `200`: success
- `400`: unused, validation uses 422
- `422`: bad email, short or long password, unknown field
- `401`: bad credentials, missing or expired session
- `409`: email already registered

## Validation Rules

- reject unknown fields with `422`
- email format checked server-side with length cap
- password never echoed back in any response

## Notes

- login throttling is deferred and recorded in TODOLIST
- session cleanup of expired rows is a future job
- related docs: `docs/shared/authentication.md`, `docs/backend/security.md`, ADR 0008
