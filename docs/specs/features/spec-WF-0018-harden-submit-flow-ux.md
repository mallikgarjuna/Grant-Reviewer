# WF-0018 — Harden Submit Flow UX

Artifact: spec
Version: v0.2
Status: Ready for PRD
Last Updated: 2026-02-18

## 1. Purpose

Improve trust and continuity in the review submit flow by removing ambiguous post-submit states and giving users explicit recovery actions.

## 2. User / System Context

- Primary users: first-time signed-in users submitting a review.
- Secondary users: returning users doing repeated attempts.
- Current pain: users perceive the app as stuck when processing is slow and are unsure whether to wait, retry, or restart.
- Interaction context: in-app review submission, post-submit waiting state, and auth transitions (sign-in return/sign-out redirect).

## 3. Core Behavior

- Provide a clear `Start new review` action that resets active draft/attempt state and returns users to a clean submission start.
- Replace passive slow-processing hint with actionable guidance that tells users exactly what to do next.
- Preserve continuity across auth deep-link round-trip so users return to intended submit flow context after sign-in.
- Ensure sign-out redirect lands users on the correct public entry point (no dead-end state).

Behavioral definitions:
- `Start new review`: clears current draft/attempt identifiers tied to the active submit flow and lands on the base review creation step.
- `Actionable slow-processing guidance`: includes at least one direct next action (wait/check status, start over, or return path) instead of passive text.
- `Auth deep-link round-trip`: if auth interrupts submit flow, returning from sign-in restores the intended in-app destination.

## 4. In Scope

- Submit-flow UX hardening only.
- `Start new review` UX and state-reset behavior.
- Actionable slow-processing guidance in the submit/wait flow.
- Validation and hardening of sign-in deep-link return behavior for the submit flow.
- Validation and hardening of sign-out redirect behavior relevant to submit flow continuity.
- Manual verification scenarios covering submit, wait, restart, and auth transitions.

## 5. Out of Scope

- Full loading/empty-state redesign across the app.
- Terms/privacy/legal content work.
- Full accessibility audit.
- New backend endpoints or protocol changes.
- Broader app-shell/navigation redesign outside submit-flow touchpoints.

## 6. Data & Dependencies

- Existing frontend review submission and review-status UX components.
- Existing auth stack and redirect/deep-link behavior.
- Existing backend contracts for review creation/status retrieval (no API expansion in this spec).
- Session/local state handling for draft/attempt reset behavior.

## 7. Edge Considerations

- Prevent stale draft/attempt state after `Start new review`.
- Ensure redirect target survives sign-in and returns users to expected flow location.
- Ensure sign-out from submit-related views consistently returns to a usable public page.
- Clarify user guidance for slow processing without implying incorrect failure states.
- Avoid introducing contradictory actions (e.g., duplicate restart/submit paths).

## 8. Verification Expectations

- Scenario 1: From a completed or failed review state, `Start new review` lands on clean submit state with no stale payload.
- Scenario 2: During slow processing, users see explicit next actions and can proceed without confusion.
- Scenario 3: Auth interruption returns users to intended submit-flow location (deep-link continuity).
- Scenario 4: Sign-out from submit-related pages redirects to expected public entry and does not trap navigation.
- Scenario 5: No dead-end path across submit, wait, restart, sign-in return, and sign-out transitions.

## Changelog

- v0.1 (2026-02-18): Initial spec from brainstorm
- v0.2 (2026-02-18): Added behavioral definitions and verification expectations; marked Ready for PRD
