# Refactoring Workflow

This document defines how to improve existing code without changing behavior.

Refactoring should increase clarity, maintainability, and consistency without introducing hidden functional scope.

---

## 1. Definition

Refactoring means changing structure without changing intended external behavior.

If behavior changes, the work is not pure refactoring and should be treated as a feature or bug-fix workflow.

---

## 2. Recommended Workflow

1. Define the motivation for the refactor.
2. Identify the current behavior that must remain unchanged.
3. Ensure there is sufficient validation coverage for the touched slice.
4. Make small, reviewable structural improvements.
5. Re-run relevant tests after each meaningful step when practical.
6. Stop when the intended structural improvement is achieved.

---

## 3. Good Reasons to Refactor

- reduce duplication after real reuse is proven
- clarify module ownership
- improve naming and readability
- simplify dependency direction
- isolate side effects or transport details
- align legacy code with agreed architecture rules

---

## 4. Refactoring Rules

- Do not mix product behavior changes into a refactor by accident.
- Prefer incremental refactors over one-shot rewrites.
- Keep architecture boundaries clearer after the refactor than before.
- Preserve tests or improve them where they are too implementation-coupled.

---

## 5. Completion Checklist

- Was behavior preserved?
- Is ownership clearer now?
- Is dependency direction improved or at least not worsened?
- Did the refactor reduce complexity or duplication meaningfully?
