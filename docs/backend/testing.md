# Backend Testing Guidelines

This document defines testing expectations for the FastAPI backend using pytest.

---

## 1. Testing Layers

Use the smallest sufficient layer for the risk under test.

- route tests for HTTP behavior, request validation, and response contracts
- service tests for business rules and orchestration
- repository tests for persistence-specific behavior when important
- integration tests for meaningful backend slices across layers

---

## 2. Core Rules

- Prefer behavior-focused tests over implementation-coupled tests.
- Keep tests deterministic.
- Validate auth, ownership, and tampered payload rejection where relevant.
- Use focused tests for regression-prone defect fixes.

---

## 3. Security-Sensitive Coverage

Tests should explicitly cover:

- unauthorized access
- forbidden access
- invalid payloads
- tampered payloads that attempt to change protected fields
- incorrect ownership or cross-tenant access where relevant

The backend must return failure responses for invalid or unauthorized mutations.

---

## 4. Test Design Rules

- Use Arrange, Act, Assert structure where practical.
- Prefer red-green-refactor discipline for behavior changes and bug fixes.
- Keep fixtures intentional and readable.
- Avoid over-mocking when it hides business risk.

---

## 5. Review Checklist

- Is the chosen test layer appropriate?
- Are auth and validation failures covered where relevant?
- Is tampered payload behavior explicitly tested when sensitive fields exist?
- Are tests readable, deterministic, and behavior-focused?
