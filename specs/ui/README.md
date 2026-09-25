# UI Specs

UI specs describe screen-level behavior, states, and interactions.

Use them to make implementation and review more consistent across design, frontend logic, and testing.

---

## Template

```md
# UI Surface Name

## Status

Draft

## Goal

What user-facing problem does this UI solve?

## Entry Points

How does the user reach this screen or component?

## Layout and Sections

Describe the main visible areas.

## Interactive Elements

Describe inputs, actions, toggles, and navigation.

## Loading State

What appears while data or actions are pending?

## Empty State

What appears when no data exists?

## Error State

What appears when something fails?

## Responsive Behavior

What changes across viewport sizes?

## Accessibility Notes

What semantic, keyboard, or focus expectations matter?
```

---

## Writing Rules

- Focus on observable behavior.
- Include loading, empty, retry, and error states.
- Document accessibility-relevant expectations when important.
- Keep copy guidance precise when it affects validation or recovery behavior.
