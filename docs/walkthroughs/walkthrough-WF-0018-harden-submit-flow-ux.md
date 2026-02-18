# WF-0018 — Harden Submit Flow UX

Artifact: walkthrough
Version: v0.2
Status: Completed
Last Updated: 2026-02-18

## Summary

Implemented submit-flow hardening focused on restart clarity, actionable slow-state guidance, auth round-trip safety, and deterministic sign-out return behavior.

## Task 1 Contract Lock (Route + Reset)

- Canonical create-review route confirmed from app navigation and existing links: `/app`.
- Canonical reviews list route confirmed: `/app/reviews`.
- Canonical public entry route for sign-out confirmed: `/`.
- Reset boundary for "Start new review": clear session-scoped review attempt (`gr.review_attempt.v1`) before navigating to `/app`.
- PRD route assumption note (`/app/review/new`) will be treated as "equivalent create-review route" and implemented as `/app` to match current router structure.

## Implemented Changes

- Added shared route constants in `frontend/src/lib/routes.ts`.
- Added `Start new review` action on review detail page and wired it to clear session attempt state before navigation.
- Added direct "My reviews" action in review detail actions.
- Replaced passive slow-processing hint with explicit next-step guidance in submit page.
- Tightened auth redirect safety:
  - proxy return path now enforces `/app*` target fallback.
  - sign-in redirect target sanitization now enforces in-app targets and blocks unsafe forms.
  - sign-in continuation links now use encoded query parameters.
- Centralized app-shell sign-out and nav route usage onto shared route constants.

## How To Run

```bash
source ~/.nvm/nvm.sh
nvm use v22.17.0
cd frontend
npm run dev
```

## How To Verify

### Automated

```bash
cd frontend
npm run lint
```

Result: passed after each implementation task and at final verification.

### Manual Scenario Checklist

1. Submit-flow restart:
   - Complete or fail a review at `/app/reviews/<id>`.
   - Click `Start new review`.
   - Confirm navigation to `/app` and clean draft/start state.
2. Slow-state guidance:
   - Trigger a slow submit path on `/app`.
   - Confirm the hint includes explicit next actions and link to `My Reviews`.
3. Auth deep-link continuity:
   - Open `/app/reviews/<id>` while signed out.
   - Sign in and confirm return to intended review path.
4. Sign-out redirect:
   - Sign out from `/app` or `/app/reviews/<id>`.
   - Confirm redirect to `/`.

## Verification Notes

- Route references inspected in:
  - `frontend/src/app/app/layout.tsx`
  - `frontend/src/app/app/reviews/page.tsx`
  - `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - `frontend/src/proxy.ts`
- Lint baseline checked before implementation changes.

## Known Limitations

- No automated e2e test suite was added in this WF; manual scenario execution is still required for full confidence.
- Redirect safety is intentionally constrained to in-app paths for this workflow and may need expansion if future flows require non-`/app` destinations.
