# Writing Style

This document defines how text produced by agents and contributors should read, so generated content does not look machine-written.

It applies to UI copy, error messages, documentation, specs, PR descriptions, commit messages, code comments, and any other user-visible or repo-visible text.

---

## 1. Core Principles

- Write like a human being, not like an AI assistant.
- Prefer plain ASCII punctuation over typographic punctuation.
- Prefer short, direct sentences over polished, verbose ones.
- Match the tone of the surrounding project instead of imposing a uniform style.
- When in doubt, copy the phrasing pattern the project already uses.

---

## 2. Punctuation Rules

Use the plain hyphen `-` for hyphenated words and compound modifiers.

Use the plain hyphen `-`, not the em dash `—` or en dash `–`, in the following cases:

- separating clauses (prefer splitting the sentence or using a colon instead)
- parenthetical asides (prefer commas or restructure)
- ranges such as `1-3` or `v1-v2`
- number or name ranges

Rules:

- Do not use the em dash `—` anywhere.
- Do not use the en dash `–` anywhere.
- Do not use Unicode quotes, ellipses, or other typographic characters by default.
- Use a colon or a new sentence instead of a dash when separating two clauses.

Examples:

- Good: `This covers web and mobile.` `Retry after 5-10 seconds.` `Fix the bug: the token was stale.`
- Bad: `This covers web - and mobile.` (spaced hyphen) `This covers web and mobile - the main platforms.` `Retry after 5 - 10 seconds.`

---

## 3. Other AI Tells to Avoid

Avoid words and phrases that are common in generated text but rare in real writing:

- `delve`, `leverage`, `utilize`, `seamlessly`, `robust`, `comprehensive`
- `moreover`, `furthermore`, `in conclusion`, `it is important to note`
- `in the realm of`, `at the end of the day`, `game-changer`
- `ensure` and `guarantee` when the sentence would be fine without them

Rules:

- Prefer the plain word over the inflated one (`use` over `utilize`, `fix` over `resolve the issue`).
- Do not pad sentences to make them sound more complete.
- Do not add transitions like `Furthermore` or `Moreover` unless they carry real meaning.

---

## 4. Sentence and Tone Rules

- Keep sentences short and concrete.
- Say what happened and what to do next, without commentary.
- Avoid identical sentence openers in consecutive sentences.
- Do not repeat the same claim in different wording to add length.
- Match the existing voice of the file or product; do not make everything uniformly formal.
- Never use emojis unless the user or product explicitly uses them.

---

## 5. Where This Applies

- user-facing UI copy and empty or error states
- error messages and validation feedback
- API and spec documentation
- PR descriptions and commit messages
- code comments
- agent chat replies inside governed repos

This rule is a hard requirement for anything written into files. Chat replies should follow the same spirit: short, direct, and free of AI-typical phrasing.

---

## 6. Review Checklist

- Are there em dashes or en dashes anywhere?
- Are there Unicode quotes or typographic characters that should be plain ASCII?
- Does the text use inflated AI-style vocabulary?
- Are sentences short, concrete, and varied?
- Does the tone match the surrounding project instead of a generic voice?