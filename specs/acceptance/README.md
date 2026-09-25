# Acceptance Specs

Acceptance specs define the observable conditions that must be true for a change to be considered complete.

These specs should align closely with real user behavior and review expectations.

---

## Template

```md
# Acceptance Scenario Group

## Status

Draft

## Scope

What feature or flow does this cover?

## Scenarios

### Scenario: Successful path

Given ...
When ...
Then ...

### Scenario: Validation failure

Given ...
When ...
Then ...

### Scenario: Unauthorized access

Given ...
When ...
Then ...
```

---

## Writing Rules

- Write observable outcomes.
- Keep scenarios focused on user-visible behavior.
- Include success, failure, and permission-sensitive cases where relevant.
- Use these specs to guide end-to-end and integration coverage.
