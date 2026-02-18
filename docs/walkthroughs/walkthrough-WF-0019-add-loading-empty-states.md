# WF-0019 — Add Loading & Empty States

Artifact: walkthrough
Version: v0.1
Status: In Progress
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
