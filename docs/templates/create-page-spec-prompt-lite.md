# Page Spec Prompt (Lite)

## Purpose

A lightweight prompt template to quickly generate an implementation-ready page specification for simple or internal pages.

This is optimized for:

- Speed
- Clarity
- MVP shipping
- Avoiding over-design

---

## When To Use

Use this for:

- Dashboard views
- CRUD pages
- Admin panels
- Results screens
- Settings pages
- Simple authenticated app pages

Do NOT use this for:

- Public landing pages
- Complex multi-step flows
- Revenue-critical pages
- Pages requiring positioning or persuasion
- Pages with heavy UX ambiguity

If strategic positioning or conversion matters → use the full page-spec template instead.

---

## Why This Exists

Without a lightweight spec:

- Pages get implemented directly from brainstorm notes.
- Scope drifts mid-implementation.
- Edge cases are forgotten.
- Loading / empty / error states are ignored.
- UI becomes inconsistent.

This template forces:

- Clear primary action
- Explicit state handling
- Defined scope boundaries
- A quick desktop layout plan

It prevents premature coding.

---

## Output Location

The generated spec should be appended to the active WF brainstorm:

- `docs/brainstorms/brainstorm-WF-XXXX-<slug>.md`

Append as a new section named: `## Appendix — Page Spec (MVP)`

---

## Prompt Template

Copy the block below into Codex chat while your brainstorm/notes file is open.

---

You are acting as a senior product thinker focused on shipping MVP quickly.

I have a brainstorm or notes file open in the editor.
Your task is to synthesize it into a concise, implementation-ready page spec.

Instructions:

1. Read the entire open file.
2. Extract only what is essential for THIS page.
3. Do NOT invent features.
4. Do NOT expand scope.
5. Optimize for clarity and fast implementation.
6. Append/update: `## Appendix — Page Spec (MVP)` in the brainstorm file
7. Keep it short. This is a lightweight spec.

Use EXACTLY this structure:

# <Page Name> — Page Spec (MVP Lite)

## 1. Page Goal

- Why this page exists
- Primary user outcome

## 2. Primary Action

- Main CTA (exact label)
- What happens after click

## 3. Key Elements (Top → Bottom)

List sections or major components in order.
For each include:

- Purpose
- Functional elements (form, table, cards, etc.)
- Required data (if any)

## 4. Data & States (Minimal)

- Required API/data
- Loading state
- Empty state
- Error state

## 5. Out of Scope

Explicitly list what is NOT included in MVP.

---

## Desktop Wireframe (Low Fidelity)

Provide a simple ASCII desktop layout.
Assume app shell unless specified.

Use placeholders only:
[Header]
[Form]
[Table]
[Card x3]
[Primary CTA]

No marketing copy.
No mobile layout.

Keep everything concise and implementation-ready.

---

## Review Checklist (Before Moving to PRD)

Before proceeding:

- Is the primary action painfully clear?
- Are loading / empty / error states defined?
- Is scope tightly controlled?
- Can this be implemented without guessing?

If not, refine the spec before moving forward.
