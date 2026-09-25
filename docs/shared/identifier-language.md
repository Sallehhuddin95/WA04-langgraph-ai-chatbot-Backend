# Identifier Language

This document defines the language of code identifiers when the product serves one or more non-English languages.

It applies to function names, variable names, parameters, types, classes, files, folders, API endpoints, query parameters, schema fields, database columns, enum values, and test names.

It does not apply to user-visible text. User-facing copy and error messages follow `docs/shared/writing-style.md` and the product language of the app.

---

## 1. Core Principles

- Code reads in English even when the product speaks another language.
- Identifier language is a code concern, not a content concern.
- Mixed-language identifiers are treated as drift, not as local flavor.
- Deviations require an explicit user or team request, not personal preference.

---

## 2. Default Rule

Use English for all code identifiers by default, regardless of the app's UI language.

If the app is in Bahasa Malaysia, French, Arabic, or any other language, the identifiers stay English:

- `getUserProfile`, not `dapatProfilPengguna`
- `createInvoice`, not `ciptaFaktur`
- `/api/v1/invoices`, not `/api/v1/faktur`
- `user.full_name`, not `user.nama_penuh`

This keeps the codebase consistent, searchable, and understandable to contributors and AI agents who do not share the product language.

---

## 3. What Counts as an Identifier

Everything that names something in code:

- functions, methods, parameters, variables, constants
- types, interfaces, classes, enums, enum values
- files, folders, route segments, feature module names
- API paths, query parameters, request and response field names
- schema fields, database tables and columns
- test names and test file names
- state keys, storage keys, and cache keys

---

## 4. What Is Not an Identifier

The following stay in the product language and are not covered by this rule:

- user-visible UI copy, labels, and empty states
- user-facing error and validation messages
- translatable content stored as data (for example a `title` column holding Malay text)
- user-provided data values

Stored data is data. Column names stay English even when the data inside them is Malay.

---

## 5. When to Deviate

Deviate from English identifiers only when:

- the user or team explicitly requests identifiers in a specific language
- an established domain term or brand name has no practical English equivalent and the team already uses it untranslated

When a deviation is requested, apply it consistently across the affected module and note it in the relevant spec or ADR so the choice is not silently reversed later.

---

## 6. Multi-Language Apps

An app that supports several languages still uses English identifiers.

Translations live in the UI layer through the app's i18n mechanism, not in code names. Each locale owns its translated strings; the identifiers that reference them stay English.

---

## 7. Review Checklist

- Are all function, variable, and type names English?
- Are API paths, query parameters, and field names English?
- Are file, folder, and test names English?
- Are database and schema field names English?
- Are any non-English identifiers justified by an explicit request or documented domain term?