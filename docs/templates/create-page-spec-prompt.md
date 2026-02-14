# Page Spec Prompt (Full)

## Purpose

A structured prompt template to generate a complete, strategy-aligned, implementation-ready page specification.

This is used for pages where:

- UX clarity matters
- Business logic is non-trivial
- Conversion or positioning is important
- The page drives core workflow

This is NOT a design exercise.
This is a thinking tool to eliminate ambiguity before PRD and implementation.

---

## When To Use

Use this for:

- Landing pages
- Core workflow pages (e.g., review flow, submission flow)
- Revenue-critical pages
- Onboarding flows
- Pages with complex state logic
- Pages that require clear positioning or persuasion

Do NOT use this for:

- Simple CRUD screens
- Internal tools
- Minor feature extensions
- Cosmetic UI updates
- Small modals or components

If speed > strategic depth → use the Lite version instead.

---

## Why This Exists

Without a structured spec:

- Strategy and UI drift apart
- Scope expands mid-build
- Primary action becomes unclear
- State handling is underdefined
- Edge cases are ignored
- PRDs become vague
- Tasks become reactive instead of planned

This template forces:

- Clear page purpose
- Explicit user state
- Defined success criteria
- Controlled scope
- Explicit data/state requirements
- A layout plan before coding

It prevents premature implementation.

---

## Output Location

The generated spec must be saved to:

docs/pages/<page-name>-spec.md

One page = one spec file.
No mixing multiple pages into one spec.

---

## Prompt Template

Copy the block below into Codex chat while your brainstorm/notes file is open.

---

You are acting as a senior product strategist and UX designer.

I have a brainstorm or notes file open in the editor.
Your task is to synthesize it into ONE definitive source-of-truth page specification file.

Instructions:

1. Read the entire open file.
2. Extract only what is essential for THIS specific page.
3. Do NOT invent new features.
4. Do NOT expand scope.
5. Optimize for clarity, usability, and implementation-readiness.
6. Create a new file: docs/pages/<page-name>-spec.md
7. Keep it concise but complete.
8. This file must be usable to generate PRD, tasks, and components later.

Use EXACTLY this structure:

# <Page Name> — Page Spec (MVP)

## 1. Page Purpose

- Why this page exists
- What user outcome it enables
- When user reaches this page in journey

## 2. Target User State

- What they know
- What they want
- What confusion or risk exists

## 3. Core Action

- Primary action on this page
- Exact CTA label
- What happens after click

## 4. Success Criteria

- What must be true for this page to be considered successful (user + product perspective)

## 5. Page Sections (Top → Bottom)

For each section include:

- Goal
- Key message / information
- Functional elements (forms, tables, cards, filters, etc.)
- Dependencies (API data, state, permissions)
- Notes on visual emphasis (not styling)

## 6. Data & State Requirements

- Required data inputs
- Loading states
- Empty states
- Error states
- Permissions (if any)
- Validation rules (if applicable)

## 7. Edge Cases

- Failure scenarios
- Misuse scenarios
- Partial completion cases

## 8. Scope Guard

Explicitly list what is NOT part of MVP for this page.

---

## Desktop Wireframe (Low Fidelity)

Create a clear ASCII desktop wireframe.

Requirements:

- Assume 1200px centered container (unless app shell layout differs)
- Show section separation
- Show column structure where relevant
- Use placeholders only:
  [Header]
  [Sidebar]
  [Form Section]
  [Table]
  [Card x3]
  [Primary CTA]
  etc.
- No marketing copy.
- No mobile layout.

Format:

==================================================
DESKTOP WIREFRAME
==================================================

<ASCII layout>

---

## UX Rationale (Short)

- Attention flow
- Interaction hierarchy
- What is above the fold
- Where friction may occur

Constraints:

- Avoid fluff.
- Avoid buzzwords.
- Keep readable in under 5 minutes.
- Must feel implementation-ready.

---

## Review Checklist (Before Moving to PRD)

Before proceeding:

- Is the page purpose explicit and measurable?
- Is the primary action unmistakable?
- Are all required states defined?
- Are dependencies clear?
- Is scope tightly controlled?
- Could a developer implement this without guessing?

If not, refine the spec before generating PRD.
