# WF-0018 — Harden Submit Flow UX

Artifact: walkthrough
Version: v0.1
Status: In progress
Last Updated: 2026-02-18

## Task 1 Contract Lock (Route + Reset)

- Canonical create-review route confirmed from app navigation and existing links: `/app`.
- Canonical reviews list route confirmed: `/app/reviews`.
- Canonical public entry route for sign-out confirmed: `/`.
- Reset boundary for "Start new review": clear session-scoped review attempt (`gr.review_attempt.v1`) before navigating to `/app`.
- PRD route assumption note (`/app/review/new`) will be treated as "equivalent create-review route" and implemented as `/app` to match current router structure.

## Verification Notes (Task 1)

- Route references inspected in:
  - `frontend/src/app/app/layout.tsx`
  - `frontend/src/app/app/reviews/page.tsx`
  - `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - `frontend/src/proxy.ts`
- Lint baseline checked before implementation changes.
