# Feature Specs

Feature specs describe a business capability from the product and implementation point of view.

Use one file per feature or bounded feature slice.

---

## Template

```md
# Feature Name

## Status

Draft

## Goal

What problem does this feature solve?

## Scope

What is included?

## Out of Scope

What is explicitly not included?

## Actors

Who uses or triggers this feature?

## Preconditions

What must already be true?

## Main Flow

Describe the expected behavior step by step.

## Alternate Flows

Describe important branching behavior.

## Error and Empty States

What happens when data is missing, invalid, unavailable, or forbidden?

## Acceptance Criteria

- Criterion 1
- Criterion 2

## Related Specs

- API:
- UI:
- Acceptance:
```

---

## Writing Rules

- Keep the feature goal explicit.
- Define scope and out-of-scope behavior clearly.
- Include important empty, failed, unauthorized, or retry behavior.
- Write acceptance criteria in observable terms.
