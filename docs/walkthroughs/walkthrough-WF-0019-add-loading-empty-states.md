# WF-0019 — Add Loading & Empty States

Artifact: walkthrough
Version: v0.2
Status: Completed
Last Updated: 2026-02-18

## Summary

Workflow focuses on replacing plain loading text and strengthening onboarding empty states in core app routes.

## Task 1 — Audit Findings

Routes inspected:
- `frontend/src/app/app/page.tsx`
- `frontend/src/app/app/reviews/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`

Findings:
- `/app`: loading is currently embedded in `<option>` copy (`Loading calls...`, `Loading sections...`) with no visible skeleton layout.
- `/app`: no dedicated empty state when calls list resolves empty; UI remains form-first and unclear.
- `/app/reviews`: loading state already has simple pulse bars but can be made more structured and consistent with card layout.
- `/app/reviews`: empty state exists and has CTA; copy can be made slightly more onboarding-focused.
- `/app/reviews/[reviewId]`: loading state still uses plain text (`Loading review...`).

Implementation direction locked:
- Add lightweight reusable skeleton blocks and state cards.
- Keep API contracts and navigation behavior unchanged.

## Implemented Changes

- `/app`:
  - Added full-page skeleton loading state while calls load.
  - Removed loading copy from select placeholders and added section-loading skeleton hints.
  - Added explicit no-calls empty state with deterministic CTA actions:
    - `Retry loading calls`
    - `Go to My Reviews`
- `/app/reviews`:
  - Upgraded loading placeholders to structured card-like skeletons.
  - Tightened empty-state onboarding copy while keeping CTA to `/app`.
- `/app/reviews/[reviewId]`:
  - Replaced plain `Loading review...` text with structured skeleton UI.

## How To Run

```bash
source ~/.nvm/nvm.sh
nvm use v22.17.0
cd frontend
npm run dev
```

## How To Verify

Automated:

```bash
cd frontend
npm run lint
```

Manual scenarios:
1. `/app` initial load: confirm full skeleton UI (not plain text) before form appears.
2. `/app` no-calls state: simulate empty calls response and confirm onboarding guidance + retry/reviews actions.
3. `/app/reviews` initial load: confirm card-like skeleton list appears.
4. `/app/reviews` empty state: confirm onboarding copy + `Start a Review` CTA.
5. `/app/reviews/[reviewId]` load: confirm skeleton state appears before review content/error branches.

## Known Limitations

- Manual scenario checks were documented but not fully executed in this environment (no mocked empty API response harness was added in this WF).
- Skeleton styles are route-local and intentionally minimal; a global shared state-component system is deferred.
