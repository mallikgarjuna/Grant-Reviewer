# WF-0018 — Harden Submit Flow UX

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-18

## Task Breakdown (Sequential Order)

### Task 1 — Confirm route and state-reset contracts

Goal:
- Lock the canonical create-review route and restart-reset boundary used by implementation.

Files to modify:
- `frontend/src/app/app/**` route entrypoints for create-review flow
- `frontend/src/lib/**` flow-state utilities (if route/reset contract is encoded there)
- `docs/walkthroughs/walkthrough-WF-0018-harden-submit-flow-ux.md`

Acceptance Criteria:
- Canonical restart destination is confirmed against actual frontend routes.
- Reset boundary is explicit enough to implement without ambiguity.
- Any route-name mismatch vs PRD assumptions is resolved in implementation notes before Task 2.

Verification Steps:
- Inspect current route definitions in `frontend/src/app/app/**`.
- Record confirmed contract in walkthrough notes.
- `cd frontend && npm run lint`

Risks (if any):
- Wrong route assumption can break restart flow.

### Task 2 — Implement `Start new review` action and clean reset

Goal:
- Add restart action in submit-related states and ensure stale draft/attempt context is cleared.

Files to modify:
- `frontend/src/app/app/**` submit/result flow pages/components
- `frontend/src/lib/**` flow-state helpers (if needed)

Acceptance Criteria:
- `Start new review` is visible in intended states.
- Restart always lands on clean create-review start.
- Previous draft/attempt context does not leak into new attempt.

Verification Steps:
- Manual scenario: completed/failed -> start new review -> clean form/start state.
- `cd frontend && npm run lint`

Risks (if any):
- Partial reset could leave stale state.

### Task 3 — Replace slow-processing hint with actionable guidance

Goal:
- Ensure slow/pending processing UI gives explicit next-step actions.

Files to modify:
- `frontend/src/app/app/**` review status/result components

Acceptance Criteria:
- Waiting UI contains direct actions/instructions (not passive copy only).
- Guidance does not incorrectly imply failure state.

Verification Steps:
- Manual scenario: pending/slow processing state shows actionable copy.
- `cd frontend && npm run lint`

Risks (if any):
- Ambiguous messaging may still cause user confusion.

### Task 4 — Harden auth deep-link round-trip continuity

Goal:
- Ensure auth interruptions return users to intended submit-flow destination.

Files to modify:
- `frontend/src/middleware.ts`
- `frontend/src/app/**` auth redirect handling points (as needed)

Acceptance Criteria:
- Post-sign-in return preserves intended submit-flow location.
- Missing/invalid return targets fail safely to deterministic in-app entry.

Verification Steps:
- Manual scenario: trigger auth interruption mid-flow and verify return target.
- `cd frontend && npm run lint`

Risks (if any):
- Middleware/redirect drift can break continuity.

### Task 5 — Harden sign-out redirect from submit-related views

Goal:
- Ensure sign-out always returns user to expected public entry route.

Files to modify:
- `frontend/src/components/**` sign-out trigger surface(s)
- `frontend/src/app/**` auth/sign-out integration points (as needed)

Acceptance Criteria:
- Sign-out from submit-related pages lands on canonical public route.
- No dead-end routes after sign-out.

Verification Steps:
- Manual scenario: sign out from submit-related pages and validate destination.
- `cd frontend && npm run lint`

Risks (if any):
- Inconsistent sign-out behavior across entry points.

### Task 6 — End-to-end verification and walkthrough capture

Goal:
- Validate all core submit-flow hardening scenarios and record outcomes.

Files to modify:
- `docs/walkthroughs/walkthrough-WF-0018-harden-submit-flow-ux.md`
- `docs/tasks/task-WF-0018-harden-submit-flow-ux.md` (optional progress marks)

Acceptance Criteria:
- Evidence logged for restart reset, actionable slow-state guidance, auth round-trip, and sign-out redirect.
- Any unresolved issues are explicitly captured with follow-up notes.

Verification Steps:
- `cd frontend && npm run lint`
- Manual scenario pass for all PRD flow requirements.

Risks (if any):
- Missing scenario coverage may hide regressions.

## Changelog

- v0.1 (2026-02-18): Initial task breakdown from PRD
- v0.2 (2026-02-18): Clarified route-contract task files/acceptance criteria; marked Ready for Implementation
