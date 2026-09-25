# Static Analysis

This document defines how to treat findings from static analysis tools such as SonarQube.

It applies to any automated code quality check surfaced in the IDE, in CI, or through extensions that flag code issues.

---

## 1. Core Principles

- Tool findings are advisory signals, not automatic mandates.
- Every finding gets an explicit decision: fix it, or consciously dismiss it.
- Do not ignore findings silently, and do not apply them blindly.
- Repo guidance wins over tool advice when the two conflict.

---

## 2. When to Address a Finding

Address a finding only when all three conditions are true:

1. it is a good suggestion
2. it is not a false positive
3. it will improve the code and its quality

If any condition fails, the finding should be dismissed, not applied.

---

## 3. When to Dismiss a Finding

Dismiss a finding when:

- it is a false positive
- the suggested change conflicts with an architecture, shared, or stack rule in this repo
- the change would reduce clarity, safety, or performance without real benefit
- the finding is a style preference that contradicts established project conventions
- applying it would add risk or churn out of proportion to the gain

A dismissal is not a refusal to look. It is a reasoned decision that the finding does not meet the three conditions in section 2.

---

## 4. Handling Rules

- Fix valid findings in the same change when practical.
- Do not disable rules globally to silence noise.
- When a tool supports targeted suppression, use it with a short justification instead of leaving the finding unexplained.
- Treat repeated false positives as a configuration problem, not a code problem.
- Keep dismissed findings visible to reviewers so the decision can be challenged.

---

## 5. Agents

Agents must apply the same three conditions before acting on a tool finding:

- If the finding is a good suggestion, not a false positive, and improves quality, fix it.
- If it conflicts with repo guidance, follow the repo and say why.
- If the finding cannot be verified, surface it instead of guessing.

---

## 6. Review Checklist

- Was every tool finding either fixed or consciously dismissed?
- Are dismissals justified and visible?
- Were rules disabled only with reason, never globally out of convenience?
- Did any fix follow repo guidance over tool advice?