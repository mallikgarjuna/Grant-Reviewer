# WF-0031 — Accessibility pass (forms + results) PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-25

## Changelog

- v0.1 (2026-02-25): Initial PRD from brainstorm

## 0. User Stories (MVP)

- **US1 (Keyboard Forms)**: As a keyboard-only user, I want to clearly see which input has focus and navigate through the `/app` form in a logical tab order, so that I can submit a proposal without using a mouse.
- **US2 (Keyboard Errors)**: As a keyboard-only user, I want my focus to move to the first invalid field when I try to submit an incomplete form, so that I don't have to guess what went wrong or hunt for the error.
- **US3 (Screen Reader Errors)**: As a screen-reader user, I want to hear validation messages and form submission alerts announced immediately, so that I know what action is required.
- **US4 (Results Readability)**: As a screen-reader/keyboard user, I want the `/app/reviews/[id]` results page to be structurally navigable using standard semantic landmarks, so that I can easily find and read my evaluation.

## Deferred Stories (Not in MVP)

- **DS1 (Global Contrast)**: As a low-vision user, I want the entire application shell to meet WCAG AA color contrast standards.
- **DS2 (Legal Accessibility)**: As an assistive tech user, I want the landing page, Terms of Service, and Privacy Policy to be fully accessible.
- **DS3 (Custom ARIA Widgets)**: As a power screen-reader user, I want complex interactive components (like nested accordions) to provide rich custom ARIA feedback beyond native HTML semantics.

## 1. In Scope

- `/app` submission form: logical tabbing, visual focus states, error focus trapping (native `autofocus` or standard React refs).
- `/app` submission form: `aria-live` regions or `aria-describedby` for validation errors and submission status.
- `/app/reviews/[id]` results page: addition of semantic landmarks (`<main>`, `<section>`, `<article>`, `<header>`) without breaking markdown rendering.
- Radix UI primitives: leverage existing accessible primitives where applicable instead of building from scratch.

## 2. Out of Scope

- Automated screen-reader integration tests (e.g., Playwright + a11y plugins).
- Remediation of the Landing Page (`/`), Privacy Page (`/privacy`), or Terms of Service (`/terms`).
- App-wide color contrast or font scaling adjustments.
- Building complex custom ARIA hooks or widgets.

## 3. User / System Flow

- **Happy Path (Submission)**:
  1. User navigates to `/app` (US1).
  2. User inputs data using `Tab` and keyboard entry (US1).
  3. User presses "Submit" (US1).
  4. System announces success (if applicable) and navigates to the results page (US3).
- **Failure Path (Validation Error)**:
  1. User presses "Submit" with invalid data (US1).
  2. System intercepts submission and displays inline errors.
  3. System programmatically shifts focus to the first invalid input field (US2).
  4. Screen reader announces the specific error message associated with that field (US3).
- **Happy Path (Results Review)**:
  1. User lands on `/app/reviews/[id]` (US4).
  2. User uses screen reader shortcut keys to jump between major structural landmarks or sections to read the evaluation (US4).

## 4. Functional Requirements

- **FR1 (US1)**: All interactive elements on `/app` must be reachable via the `Tab` key in a logical top-to-bottom, left-to-right DOM order.
- **FR2 (US1)**: All interactive elements on `/app` must have a clearly visible CSS `:focus` or `:focus-visible` state.
- **FR3 (US2)**: Upon form submission failure, the React component must identify the first invalid field and programmatically call `.focus()` on its ref.
- **FR4 (US3)**: Form fields with validation errors must use `aria-invalid="true"` and `aria-describedby` pointing to the error message ID.
- **FR5 (US3)**: High-priority application alerts (e.g., "Submission failed") must be rendered within an `aria-live="assertive"` region.
- **FR6 (US4)**: The `/app/reviews/[id]` page must wrap its core content in a `<main>` tag, and logical evaluation blocks in `<section>` or `<article>` tags with appropriate heading (`<h1>`-`<h6>`) hierarchy.

## 5. Data & API Contracts

- No API backend or data schema changes are required for this workflow. All changes are frontend DOM structural and React state management additions to comply with FR1-FR6.

## 6. Components / Modules

- **Submission Form (Frontend)**:
  - Add refs to input fields for focus management (FR3).
  - Add standard `aria-` attributes (FR4, FR5).
  - Likely touched files: generic input components in `frontend/src/components/ui/` (e.g., Input, Textarea, Label) and the main form page/component.
- **Results Page (Frontend)**:
  - Add semantic wrapper tags (FR6) around the existing markdown renderer.
  - Likely touched files: `frontend/src/app/reviews/[id]/page.tsx` (or equivalent React route component layout).

## 7. Edge Cases

- **Edge Case 1 (US2)**: If the first invalid field is inside a closed/hidden or virtually scrolled container, `.focus()` may fail or cause erratic scrolling. (Mitigation: ensure the form MVP does not hide invalid fields at submission time).
- **Edge Case 2 (US4)**: Markdown renderer outputs arbitrary HTML that might conflict with or duplicate wrapper landmarks. (Mitigation: carefully inspect the DOM output of the markdown component to ensure the wrapper semantics remain valid).

## 8. Testing Decisions (TDD)

- **Manual Verification**: Since automated a11y tooling is out of scope (OOS), developers must verify the behavior locally:
  - Press `Tab` repeatedly to ensure all fields are reachable and focus is visible (FR1, FR2).
  - Submit an empty form and ensure focus jumps to the first required field (FR3).
- **Component Tests (Optional/If existing)**: If existing React testing library tests exist for the form, assert that `aria-invalid` is applied correctly. Do not write an entirely new suite if none exists, as the primary verification is manual keyboard checking.

## 9. Telemetry (Minimal)

- N/A

## 10. Deferred / Not in MVP

- Comprehensive automated a11y testing (Playwright).
- Universal contrast changes.

## 11. Open Questions

- None at this time.

## 12. Changelog

- v0.1 (2026-02-25): Initial PRD from brainstorm
