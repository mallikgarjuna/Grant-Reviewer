# WF-0019 — Add Loading & Empty States

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-02-18

## 1. In Scope

- Replace plain loading copy with skeleton/shimmer loaders in core app routes:
  - `/app`
  - `/app/reviews`
  - `/app/reviews/[reviewId]`
- Add no-data onboarding empty states for:
  - no available calls in submit flow
  - no existing reviews in review-history page
- Add explicit next-action CTA in each empty state.
- Keep existing route and API behavior unchanged.

## 2. Out of Scope

- Backend endpoint changes or schema updates.
- Polling/state-machine changes for review processing.
- Legal/privacy page work.
- Node selector redesign and other unrelated P1 items.
- Full accessibility refactor beyond touched state components.

## 3. User / System Flow

Happy path:
1. User opens `/app` and sees structured loading skeleton while calls load.
2. If calls are available, normal submit form appears.
3. User opens `/app/reviews` and sees structured loading skeleton while reviews load.
4. If reviews exist, review list appears as-is.

Failure path A - no calls:
1. `/app` call fetch completes with empty list.
2. User sees empty-state explanation and clear next step.
3. User is not left with blank/ambiguous UI.

Failure path B - no reviews:
1. `/app/reviews` fetch completes with empty list.
2. User sees onboarding empty state with CTA to start a review.
3. Navigation remains deterministic.

Failure path C - review detail fetch delay:
1. User opens `/app/reviews/[reviewId]`.
2. Detail request takes time.
3. User sees structured loading state instead of plain text and can wait confidently.

## 4. Functional Requirements

- FR1: No plain `Loading...` text remains in the three in-scope routes.
- FR2: Loaders reflect page layout intent and do not break responsiveness.
- FR3: `/app` empty call data shows onboarding message plus clear action.
- FR4: `/app/reviews` empty reviews state shows guidance and CTA to `/app`.
- FR5: Existing error handling and authorization behavior remain unchanged.
- FR6: Empty states are shown only after fetch resolves (not during initial loading).
- FR7: All new copy remains concise and aligned with existing product tone.

## 5. Data & API Contracts

Request/response shapes:
- Reuse existing `GET calls`, `GET reviews`, and `GET review detail` frontend contracts unchanged.

Validation rules:
- Empty state logic depends on resolved response arrays being length `0`.
- Loading state logic depends on existing fetch lifecycle flags.

State transitions:
- initial load -> skeleton state -> content state or empty state
- no-data state -> CTA navigation to deterministic route (`/app` where applicable)

## 6. Components / Modules

Boundaries and responsibilities:
- Page-level route components manage loading vs empty vs content branching.
- Shared lightweight loading-state components handle skeleton visuals.
- Empty-state UI components provide guidance copy + CTA action.

Suggested file paths:
- `frontend/src/app/app/page.tsx`
- `frontend/src/app/app/reviews/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- optional shared UI state helpers under `frontend/src/components/**` or `frontend/src/lib/**`

## 7. Edge Cases

- Very fast responses should avoid visible flicker between loader and content.
- Empty-state CTA should not appear for transient network errors.
- Review-detail not-found/error states must remain distinct from loading/empty states.
- Mobile layout should preserve readable skeleton and empty-state spacing.

## 8. Telemetry (Minimal)

- No new telemetry pipeline required in MVP.
- Optional console diagnostics are allowed during local verification but should not ship as persistent logging behavior.

## Deferred / Not in MVP

- Animated progressive placeholders beyond simple shimmer/skeleton.
- Cross-app global loading framework.
- Dedicated analytics for empty-state conversion.

## Open Questions (if any)

- Use a small shared set of state UI helpers where practical, but avoid broad framework extraction.

## Changelog

- v0.1 (2026-02-18): Initial PRD from spec
- v0.2 (2026-02-18): Resolved component extraction direction and marked Ready for Tasks
