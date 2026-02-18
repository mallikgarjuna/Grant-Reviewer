# WF-0019 — Add Loading & Empty States

Artifact: task
Version: v0.3
Status: Completed
Last Updated: 2026-02-18

## Task Breakdown (Sequential Order)

### Task 1 — Audit current loading/empty state surfaces

Goal:
- Identify exact in-scope routes/components still using plain loading text or weak empty states.

Files to modify:
- `frontend/src/app/app/page.tsx`
- `frontend/src/app/app/reviews/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `docs/walkthroughs/walkthrough-WF-0019-add-loading-empty-states.md`

Acceptance Criteria:
- In-scope routes and target states are confirmed before implementation.
- Route-specific behavior notes are recorded for verification.

Verification Steps:
- Inspect in-scope files for loading/empty branches.
- `cd frontend && npm run lint`

Risks (if any):
- Missing a surface can leave plain loading copy in production.

### Task 2 — Implement loading skeletons in in-scope routes

Goal:
- Replace plain `Loading...` UI with skeleton/shimmer placeholders in in-scope routes.

Files to modify:
- `frontend/src/app/app/page.tsx`
- `frontend/src/app/app/reviews/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- optional shared component file(s) under `frontend/src/components/**`

Acceptance Criteria:
- No plain `Loading...` remains in in-scope routes.
- Skeletons render responsively and resemble target layouts.

Verification Steps:
- Manual route checks for loading branch UI.
- `cd frontend && npm run lint`

Risks (if any):
- Layout mismatch or flicker if skeleton dimensions are poor.

### Task 3 — Add onboarding empty states with deterministic CTAs

Goal:
- Add clear no-data guidance for empty calls and empty reviews states.

Files to modify:
- `frontend/src/app/app/page.tsx`
- `frontend/src/app/app/reviews/page.tsx`
- optional shared empty-state component under `frontend/src/components/**`

Acceptance Criteria:
- Empty calls state explains condition and provides clear next step.
- Empty reviews state provides CTA to `/app`.
- Empty states are shown only after loading completes.

Verification Steps:
- Manual checks for no-data routes/states.
- `cd frontend && npm run lint`

Risks (if any):
- CTA target mismatch could create dead-end navigation.

### Task 4 — Verify behavior and capture walkthrough

Goal:
- Validate final UX behavior and record reproducible verification notes.

Files to modify:
- `docs/walkthroughs/walkthrough-WF-0019-add-loading-empty-states.md`
- `docs/tasks/task-WF-0019-add-loading-empty-states.md` (progress updates)

Acceptance Criteria:
- Walkthrough contains run + verify instructions and known limitations.
- Verification evidence covers loading and empty-state behavior in all in-scope routes.

Verification Steps:
- `cd frontend && npm run lint`
- Manual checks for `/app`, `/app/reviews`, `/app/reviews/[reviewId]` states.

Risks (if any):
- Incomplete manual coverage can miss regressions.

## Changelog

- v0.1 (2026-02-18): Initial task breakdown from PRD
- v0.2 (2026-02-18): Tightened task scope and marked Ready for Implementation
- v0.3 (2026-02-18): Completed implementation across Tasks 1-4
