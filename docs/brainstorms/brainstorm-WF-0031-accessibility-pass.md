# WF-0031 — Accessibility pass (forms + results)

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-02-25

---

## 1. Problem Statement

The application forms (`/app` submission) and results pages (`/app/reviews/[id]`) currently lack proper accessibility support.
This prevents keyboard-only users and individuals relying on screen-readers from successfully navigating, completing submissions, or reading returned evaluations.
With real users (including academic researchers) expected to use the platform soon, this is a P1 launch blocker.

---

## 2. Desired Outcome

Forms and results pages must support seamless keyboard navigation (logical tab order, visible focus states, focus trapping on errors).
Screen-reader users must receive context-appropriate announcements (using `aria-live` regions for dynamic errors/alerts and validation feedback).
The MVP outcome focuses strictly on these two critical pathways and defers sweeping app-shell color contrast or semantic updates.

**Brainstorming Q&A:**

**Q1: How should we scope the desired outcome for this accessibility pass?**
- A) Focus strictly on keyboard navigation and screen-reader announcements for the forms and results pages.
- B) Option A + a sweeping audit for color contrast, semantic HTML tags, and `/privacy` / `/terms`.
- C) Custom approach.
> Recommendation: A — Keeps the MVP tight, highly testable, and immediately unblocks the most critical user flows.
> **Selected: A**

---

## 3. Target User / Actor

Target users are individuals with motor disabilities who rely entirely on keyboard navigation, and individuals with visual impairments who rely on screen readers.

**Brainstorming Q&A:**

**Q1 (Target User & Scope): Which forms/pages are the highest priority for this pass?**
- A) Only the core submission form (`/app`) and the initial results view (`/app/reviews/[id]`). This directly solves the P1 launch blocker.
- B) All forms, including potential future login/signup components, settings profiles, and the landing page.
> Recommendation: A — Directly solves the P1 launch blocker.
> **Selected: A**

---

## 4. Rough Idea (Unstructured Thinking)

The simplest approach is to augment the existing React components rather than rewriting them. We will use native HTML5 `autofocus` or standard React refs to jump focus to invalid fields on submission. We will utilize standard Radix UI primitives if already present, ensuring we stay close to established patterns.

**Brainstorming Q&A:**

**Q2 (Implementation Strategy): How should we handle focus management for validation errors?**
- A) Rely on native HTML5 `autofocus` (or React refs) to jump focus to the *first invalid field* upon submission, and use standard Radix UI primitives if already in the project.
- B) Write custom React hooks to trap and manage focus across all interactive components manually.
> Recommendation: A — Leverages native/existing primitives, keeping the implementation simple and standard.
> **Selected: A**

---

## 5. Constraints

We have limited ability to test with native screen readers (VoiceOver/NVDA) via the AI agent. We will rely on semantic HTML validation and manual keyboard tabbing.
We are intentionally constraining this pass strictly to the forms and results pages.

**Brainstorming Q&A:**

**Q3 (Constraints): What is our testing strategy for screen reader compatibility, given the AI coding constraints?**
- A) Rely strictly on structural semantic HTML validation (e.g., proper `<label>` associations, `aria-` attributes) and manual keyboard tabbing verification; defer actual VoiceOver/NVDA testing to manual human QA.
- B) Attempt to configure and run automated screen-reader integration tests (e.g., Playwright a11y plugins) as part of this workflow.
> Recommendation: A — Acknowledges testing limits and secures the baseline structurally before manual QA.
> **Selected: A**

---

## 6. Risks / Unknowns

The biggest risk is unintentionally breaking the visual layout or markdown rendering of the results page when wrapping elements in new semantic landmarks or focusable targets.

**Brainstorming Q&A:**

**Q4 (Risks & Unknowns): What is the biggest risk with modifying the results page (`/app/reviews/[id]`)?**
- A) Breaking the existing Markdown rendering or disrupting visual layout when adding semantic landmarks and focusable regions.
- B) Performance degradation from excessive ARIA attributes.
> Recommendation: A — Visual layout and Markdown rendering are fragile, requiring careful structural updates.
> **Selected: A**

---

## 7. MVP Definition

The MVP requires shipping proper semantic landmarks, native HTML form controls, and basic `aria-live` error announcements for the `/app` and `/app/reviews/[id]` pages. We will explicitly NOT build complex custom ARIA widgets.

**Brainstorming Q&A:**

**Q5 (MVP Definition): If we had to ship this in 1 day, what do we explicitly exclude?**
- A) Exclude building complex custom ARIA widgets. Rely entirely on native HTML form controls, basic semantic landmarks, and simple `aria-live` error announcements.
- B) Exclude visible focus states and only add hidden screen-reader text.
> Recommendation: A — Maximizes reliability by relying on proven native and simple implementations.
> **Selected: A**

---

## 8. Explicit Non-Goals

- No comprehensive automated Playwright a11y test suites.
- No remediation of the Landing Page, Privacy Page, or Terms of Service.
- No remediation of app-wide color contrast or font scaling (handled globally later).
- No complex custom ARIA hooks/widgets.
