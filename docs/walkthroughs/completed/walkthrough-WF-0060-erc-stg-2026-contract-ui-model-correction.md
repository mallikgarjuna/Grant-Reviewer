<!-- docs/walkthroughs/walkthrough-WF-0060-erc-stg-2026-contract-ui-model-correction.md -->
# WF-0060 Walkthrough — ERC StG 2026 Contract/UI Model Correction

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-03-06

## Scope

Implemented WF-0060 end-to-end across canonical call contract, submit-flow stage awareness, backend stage gating, structured review contract compliance, persisted coverage compatibility, and review-detail ordering/compatibility notes.

## What Changed

1. Corrected ERC canonical hierarchy to leaf/container model (`resources_time_commitment` under `part_a -> budget`; container nodes non-submittable).
2. Enforced leaf-only submit boundaries on frontend and backend.
3. Added stage-aware submit flow and metadata stage projection (`STEP_1`, `STEP_2`, `BOTH`).
4. Fixed backend structured review request contract shape/digest handling to prevent `MALFORMED_REVIEW_REQUEST`.
5. Persisted submitted leaf coverage and compatibility metadata for review detail.
6. Switched review detail grouping/ordering to call metadata + persisted coverage.
7. Added explicit mixed-version compatibility notes for deprecated/moved legacy evidence.
8. Added closure regression selectors for container blocking and zero-card leaf visibility.
9. Hardened multi-call review stage UX:
   - Step 2 hidden for single-stage calls unless explicit `STEP_2` metadata exists.
   - Fail-closed reset to Step 1 on call switch/metadata failure.
10. Relaxed default daily quota in dev-like `APP_ENV` when `FREE_DAILY_REVIEW_LIMIT` is unset.

## Verification Evidence

- Frontend:
  - `npm run test:ui -- src/components/submit/UniversalSubmitForm.test.tsx`
  - `npm run test:ui -- src/app/app/reviews/[reviewId]/page.test.tsx` (covered in suite invocation)
- Backend:
  - `DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_call_nodes_metadata_api.py -q`
  - `DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_structured_reviewer_service.py::test_structured_pipeline_v1_happy_path tests/test_structured_reviewer_service.py::test_structured_pipeline_v1_review_request_snapshot_stays_contract_compliant tests/test_structured_reviewer_service.py::test_wf0060_structured_review_rejects_erc_container_submission_ids -q`
  - `DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py::test_create_structured_review_stage_mismatch_returns_422 tests/test_api.py::test_review_stage_node_mismatch_returns_422 tests/test_api.py::test_create_structured_review_success_persists_structured_fields -q`
  - `uv run pytest tests/test_reviewer_policy.py -q`
  - `DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py::test_quota_exceeded_returns_429_with_details tests/test_api.py::test_quota_relaxed_in_dev_mode_when_limit_unset -q`

## Risks / Notes

- Metadata ingestion freshness still matters for local runtime correctness; stale DB call definitions can produce apparent UI/backend mismatches.
- Quota relaxation remains env-driven and explicit env values take precedence.

## Outcome

WF-0060 implementation and review-and-harden fixes are complete and ready for ship-gate approval.
