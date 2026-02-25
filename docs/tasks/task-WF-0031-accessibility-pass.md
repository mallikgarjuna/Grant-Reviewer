# WF-0031 — Accessibility pass (forms + results) Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-25

## Changelog

- v0.1 (2026-02-25): Initial task breakdown from PRD
- v0.2 (2026-02-25): Applied task review (split Task 1 for atomicity)

## Task Breakdown (Sequential Order)

### [x] Task 1.1 — Add visual focus states to form UI global CSS (Tracer Bullet)
Goal: Ensure global focus-visible utilities are defined and not swallowed by existing resets.
Slice: Keyboard Navigation
User Stories: US1
PRD Requirements: FR1, FR2
Files to modify: `frontend/src/app/globals.css` (or equivalent global stylesheet)
Acceptance Criteria: A clear, high-contrast `:focus-visible` ring is defined globally for interactive elements.
Verification Steps:
1. Run local dev server.
2. Inspect CSS output to ensure `focus-visible` rule is active.
Risks: Overriding existing Tailwind `focus:ring` utilities.

### [x] Task 1.2 — Apply visual focus states to form components
Goal: Ensure all interactive elements on the `/app` submission form utilize the global focus state and logical tab order.
Slice: Keyboard Navigation
User Stories: US1
PRD Requirements: FR1, FR2
Files to modify: `frontend/src/components/ui/input.tsx`, `frontend/src/components/ui/textarea.tsx`, `frontend/src/components/ui/button.tsx`
Acceptance Criteria: Pressing `Tab` visibly highlights every input, button, and select element in sequence on the `/app` form.
Verification Steps:
1. Run local dev server.
2. Navigate to `/app` without using a mouse.
3. Verify `Tab` moves through all fields in logical order.
4. Verify CSS `:focus` or `:focus-visible` is clearly visible on each active component.
Risks: Conflicting component-level focus styles vs global styles.

### [x] Task 2 — Implement focus trapping for validation errors
Goal: Programmatically shift focus to the first invalid field upon a failed form submission.
Slice: Error Recovery
User Stories: US2
PRD Requirements: FR3
Files to modify: `frontend/src/app/page.tsx` (or whatever rendering the submission form)
Acceptance Criteria: Submitting an incomplete form immediately moves keyboard focus into the first input with a validation error.
Verification Steps:
1. Load `/app`.
2. Leave required fields blank.
3. Press `Enter` or click "Submit".
4. Verify focus is placed inside the first invalid field.
Risks: React refs not being properly forwarded to generic UI components (`forwardRef`).

### [x] Task 3 — Add `aria` attributes for form validation
Goal: Ensure screen readers announce validation errors associated with specific fields.
Slice: Screen Reader Announcements
User Stories: US3
PRD Requirements: FR4
Files to modify: Form rendering component (`frontend/src/app/page.tsx`), UI components if needed (`frontend/src/components/ui/input.tsx`).
Acceptance Criteria: Invalid fields have `aria-invalid="true"` and `aria-describedby` linking to the error message element ID.
Verification Steps:
1. Trigger a validation error on `/app`.
2. Inspect the DOM of the invalid field.
3. Verify `aria-invalid="true"` exists.
4. Verify `aria-describedby` matches the `id` of the text element rendering the error.
5. (Manual) Listen with VoiceOver/NVDA to ensure the error text is read when the field receives focus.
Risks: ID collisions if multiple forms exist; ensure unique IDs for error messages.

### [ ] Task 4 — Add `aria-live` regions for submission status
Goal: Ensure screen readers announce high-priority application alerts (e.g., "Submission failed").
Slice: Screen Reader Announcements
User Stories: US3
PRD Requirements: FR5
Files to modify: Form rendering component (`frontend/src/app/page.tsx`) or global toast/alert component.
Acceptance Criteria: A dedicated node with `aria-live="assertive"` exists and updates when a global submission error occurs.
Verification Steps:
1. Fake a network failure or global submission error.
2. Inspect the DOM to ensure the error text is injected into the `aria-live="assertive"` region.
3. (Manual) Listen with VoiceOver/NVDA to ensure the error is announced immediately without needing to move focus.
Risks: `aria-live` region must exist in the DOM *before* the error is injected for screen readers to notice the change.

### [ ] Task 5 — Add semantic landmarks to results page
Goal: Wrap the `/app/reviews/[id]` results in proper HTML landmarks (`<main>`, `<section>`, etc.) without breaking markdown.
Slice: Results Readability
User Stories: US4
PRD Requirements: FR6
Files to modify: `frontend/src/app/reviews/[id]/page.tsx` (or equivalent results layout component).
Acceptance Criteria: The page structural layout uses `<main>`, `<header>`, and logical `<section>` tags around major evaluation blocks.
Verification Steps:
1. Submit a valid form to reach `/app/reviews/[id]`.
2. Inspect DOM to verify `<main>` tag exists wrapping the core review content.
3. Use VoiceOver Rotor (or NVDA elements list) to verify landmarks and headings (`<h1>`-`<h6>`) are navigable.
Risks: Breaking the visual styling of the markdown output by wrapping it incorrectly or altering CSS combinators.
