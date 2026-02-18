# WF-0019 — Add Loading & Empty States

Artifact: spec
Version: v0.1
Status: Draft
Last Updated: 2026-02-18

## 1. Purpose

Improve user trust and clarity in the app by replacing plain loading text with polished loaders and by adding guided onboarding empty states where data is absent.

## 2. User / System Context

- Primary users are signed-in researchers using `/app` and `/app/reviews`.
- Current experience exposes plain `Loading...` text and weak no-data guidance.
- Key states include call list loading, review list loading, and review-detail loading.
- Empty states are most visible for first-time users with no prior reviews or unavailable call data.

## 3. Core Behavior

- Replace plain loading copy in key routes with skeleton/shimmer loading UI that matches layout intent.
- Add explicit empty-state messaging with clear next-action CTA in core no-data situations.
- Keep behavior and route flow unchanged; only improve state presentation and guidance.

## 4. In Scope

- Loading-state UX improvements in core app routes (submit, reviews list, review detail).
- Empty-state UX for:
  - no available calls for selection
  - no reviews yet in review-history/list context
- CTA text and action targets for each empty state.
- Manual verification checklist and lint verification for changed surfaces.

## 5. Out of Scope

- Backend/API/schema changes.
- New async processing logic or polling behavior changes.
- Legal page work (`/terms`, `/privacy` expansion).
- Node hierarchy selector redesign.
- Broad app-wide accessibility remediation sweep.

## 6. Data & Dependencies

- Existing frontend routes/components under `frontend/src/app/app/**`.
- Existing client-side request/state handling for calls/reviews.
- Existing design tokens/components currently used in app surfaces.
- No new external dependencies required for MVP implementation.

## 7. Edge Considerations

- Loading skeletons should avoid layout mismatch that causes visual jump.
- Empty-state CTAs must route to valid, deterministic destinations.
- States should avoid false negatives (brief loading should not flash empty state prematurely).
- Copy should remain concise and avoid implying system errors for ordinary empty data.

## Changelog

- v0.1 (2026-02-18): Initial spec from brainstorm
