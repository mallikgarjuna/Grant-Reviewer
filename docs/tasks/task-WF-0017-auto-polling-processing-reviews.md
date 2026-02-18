# WF-0017 — Auto Polling for Processing Reviews

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-18

## Task Breakdown (Sequential Order)

### Task 1 — Confirm status semantics and polling constants

Goal:
- Lock implementation constants for polling interval/cap and map PRD “processing” behavior to actual runtime status enum (`PENDING` in codebase).

Files to modify:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`

Acceptance Criteria:
- Polling trigger status is unambiguous in code.
- Interval is 3 seconds and cap is 90 seconds via explicit constants.
- No status-name mismatch remains in implementation logic.

Verification Steps:
- Manual code-path check for `PENDING` -> terminal transitions.
- `cd frontend && npm run lint`.

Risks (if any):
- Incorrect status mapping can prevent polling from starting.

### Task 2 — Implement bounded polling lifecycle in review detail page

Goal:
- Add client polling loop for pending reviews with proper start/stop behavior and cleanup on unmount/navigation.

Files to modify:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`

Acceptance Criteria:
- Poll starts for pending reviews and does not run for terminal reviews.
- Poll stops on terminal state, cap reached, and unmount/navigation.
- Only one active polling loop exists per page instance.

Verification Steps:
- Manual run in app: observe pending review auto-transition to terminal state without manual refresh.
- `cd frontend && npm run lint`.

Risks (if any):
- Duplicate intervals from rerenders or stale closures.

### Task 3 — Add capped long-processing fallback UX

Goal:
- Show explicit fallback guidance when pending status remains after cap without marking review failed client-side.

Files to modify:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`

Acceptance Criteria:
- After 90 seconds in pending, polling stops and fallback message appears.
- Message clearly states processing may still be ongoing and suggests later refresh/check.
- Failed state UI remains reserved for backend `FAILED`.

Verification Steps:
- Manual behavior test with stubbed/slow processing path.
- `cd frontend && npm run lint`.

Risks (if any):
- Messaging confusion between cap fallback and true failure.

### Task 4 — Handle transient polling request errors safely

Goal:
- Keep polling bounded under transient fetch failures without timer duplication or cap reset.

Files to modify:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`

Acceptance Criteria:
- Transient fetch errors do not spawn extra loops.
- Cap timer behavior remains bounded and does not reset unintentionally.
- UI remains in pending context unless terminal state is returned.

Verification Steps:
- Manual simulation of intermittent network error during polling while confirming cap timer does not reset.
- `cd frontend && npm run lint`.

Risks (if any):
- Silent failure could leave users in unclear state.

### Task 5 — Verify end-to-end polling behavior and document results

Goal:
- Run targeted verification for both terminal auto-transition and cap fallback scenarios; capture results in walkthrough.

Files to modify:
- `docs/walkthroughs/walkthrough-WF-0017-auto-polling-processing-reviews.md`
- `docs/tasks/task-WF-0017-auto-polling-processing-reviews.md` (checkbox/progress updates if used)

Acceptance Criteria:
- Evidence logged for:
  - pending -> terminal auto-transition path
  - pending -> cap fallback path
- Verification commands and outcomes are recorded.

Verification Steps:
- `cd frontend && npm run lint`
- Manual app verification with local environment/stub modes as applicable.

Risks (if any):
- Incomplete verification can miss lifecycle regressions.

## Changelog

- v0.1 (2026-02-18): Initial task breakdown from PRD
- v0.2 (2026-02-18): Applied task review refinements and marked ready for implementation
