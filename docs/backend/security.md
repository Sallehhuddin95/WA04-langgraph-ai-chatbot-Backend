# Backend Security Guidelines

This document defines backend security rules relevant to request handling, data mutation, and trust boundaries.

---

## 1. Core Principle

The client is untrusted.

Frontend UI constraints, hidden fields, disabled inputs, and visible workflows are not security controls. The backend must verify every sensitive rule independently.

---

## 2. Request Trust Rules

- Validate every incoming request on the server.
- Accept only explicit allowed fields.
- Reject unknown, forbidden, or ownership-sensitive field changes.
- Derive identity- or ownership-sensitive values from authenticated server context whenever possible.

---

## 3. Tampered Payload Rules

If a user intercepts a frontend API request and changes the payload:

- the backend must revalidate the payload
- the backend must enforce authorization and ownership rules
- the backend must reject unauthorized or invalid changes with a failure response
- the backend must not return success for a mutation that violates the contract or permissions

This is mandatory behavior, not an optional defense.

---

## 4. Authorization Rules

- Authorization must be server-enforced.
- Use centralized permission logic where practical.
- Distinguish clearly between unauthenticated and forbidden behavior.
- Never rely on the frontend alone to prevent access or mutation.

---

## 5. Data Exposure Rules

- Return the minimum required data.
- Avoid exposing internal implementation details in error responses.
- Do not leak security-sensitive fields unless explicitly required.

---

## 6. Review Checklist

- Are server-side validation and authorization both enforced?
- Are protected fields derived or verified server-side?
- Does a tampered payload fail instead of succeeding?
- Are error responses safe and structured?
