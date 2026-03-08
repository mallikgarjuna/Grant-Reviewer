<!-- docs/walkthroughs/completed/walkthrough-WF-0067-review-trust-surface-closure.md -->
# WF-0067 — Review Trust Surface Closure

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-08

## Part A — Implementation Summary

WF-0067 implementation shipped the launch-blocking trust surfaces across backend seam, BFF seam, and review-detail rendering seam:

- Backend now exposes per-card source basis (`source_basis_label`, `source_basis_state`) with precedence `evaluation element source_hint` -> `criterion source_hint` -> explicit unavailable, plus boundary buckets for `visible_not_reviewed_node_logical_ids` and `no_generated_cards_node_logical_ids`.
- BFF review-detail route preserves trust fields and boundary arrays without local source-basis synthesis.
- Review-detail page and review cards now render criterion/element, reviewed section context, official source basis or explicit unavailable/legacy limitation copy, and distinct visible-not-reviewed vs no-generated-card surfaces.

## Part B — Adversarial Audit Closure (Phase 3.2 -> 3.3)

Audit profile: `execution`
Primary range used for gate: `main...HEAD`

Closed findings:

1. Blocking: explicit empty boundary arrays were treated as absent and could re-enable inference fallback on opted-in calls.
   - Fix: treat boundary arrays as authoritative when present, even when empty.
   - Evidence:
     - `frontend/src/app/app/reviews/[reviewId]/page.tsx`
     - `frontend/src/app/app/reviews/[reviewId]/page.test.tsx` test `wf0067_review_detail_boundary_explicit_empty_buckets_do_not_fallback_to_inference`
2. Non-blocking: BFF recomputed `detail_state` instead of preserving backend-supplied state.
   - Fix: preserve backend `detail_state` verbatim when provided, fallback inference only when absent.
   - Evidence:
     - `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
     - `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts` test `wf0067_bff_review_detail_preserves_backend_detail_state_verbatim`

## Part C — Verification Evidence

Automated verification:

- `cd frontend && npx vitest run 'src/app/api/bff/reviews/[reviewId]/route.test.ts' 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0067_'`
  - Result: pass (`16 passed`, `14 skipped`)
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py -k "wf0067_backend_source_basis_contract_ or wf0067_backend_boundary_contract_"`
  - Result: pass (`8 passed`)

Browser-based visual validation:

- Backend and frontend dev servers run locally with `AUTH_MODE=test_bypass`.
- Browser validation executed against:
  - `/app/reviews`
  - `/app/reviews/7bc977f3-676c-4e16-9b67-6656ebf8629a`
- Validated in rendered UI:
  - coverage summary visible,
  - reviewed section context visible on cards,
  - official source-basis line visible,
  - visible-but-not-reviewed section rendering present when provided,
  - no mobile horizontal overflow on 390x844 viewport.

## Part D — Scope & Risk Notes

- Scope stayed inside WF-0067 launch-blocking trust surfaces and seam-level proof closure.
- Remaining work is non-WF product polish only; no blocking trust-surface defects remain after the audit closure fixes.
