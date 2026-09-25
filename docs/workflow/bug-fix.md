# Bug Fix Workflow

This document defines the preferred workflow for fixing defects.

The goal is to fix the root cause with the smallest safe change and preserve confidence through focused validation.

---

## 1. Start Conditions

Before fixing the bug, gather:

- observed behavior
- expected behavior
- affected feature or route
- reproduction steps when available
- any existing failing test or user-visible symptom

---

## 2. Recommended Workflow

1. Reproduce the bug or identify the closest reliable symptom.
2. Locate the controlling code path, not only the visible failure surface.
3. Form a falsifiable hypothesis for the root cause.
4. Add or update a focused test when practical.
5. Apply the smallest change that fixes the root cause.
6. Re-run the most relevant narrow validation.
7. Update related docs only if the bug exposed a missing or unclear rule.

---

## 3. Fix Rules

- Prefer root-cause fixes over defensive patch stacking.
- Avoid unrelated cleanup in the same change unless it is required for the fix.
- If the failure is architectural, document the pattern gap or consider an ADR.
- Preserve existing conventions unless they directly caused the defect.

---

## 4. Validation Expectations

- Use the narrowest meaningful test first.
- Confirm the original symptom is resolved.
- Confirm no adjacent behavior regressed in the touched slice.

---

## 5. Completion Checklist

- Was the root cause identified clearly?
- Was the fix kept narrow?
- Was the bug covered by a test or targeted validation?
- Did the bug expose a reusable lesson that should be documented?
