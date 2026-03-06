<!-- docs/walkthroughs/walkthrough-WF-0059-multi-call-ux-unblocker.md -->
# WF-0059 — Multi-call UX Unblocker

Artifact: walkthrough
Version: v0.1
Status: Drafted
Last Updated: 2026-03-06

Type: feature

## Summary

- Unblocked the locked ERC proof call `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml` through the existing structured-review submit path without widening generic nested-call support.
- Preserved structured-review validation ordering and idempotency mismatch behavior while accepting hierarchical proof-call payloads.
- Moved proof-path review detail coverage and ordering onto persisted submitted-node coverage plus call-linked metadata, with explicit state handling for legacy fallback and proof-path unmapped linkage.

## What Changed

- Frontend submit:
  - Allowed only `erc_stg_2026_full` to traverse hierarchical nodes in execution order.
  - Kept flat-call/Veni submit behavior unchanged.
- Backend structured review:
  - Accepted recursive hierarchical request payloads and flattened them deterministically at the contract boundary.
  - Persisted `submitted_node_logical_ids` on structured reviews for downstream review-detail coverage.
- Review detail:
  - Exposed `submitted_node_logical_ids` on the review-detail contract.
  - Derived proof-path reviewed/not-reviewed sections from persisted submitted-node coverage plus call metadata instead of `submitted_nodes` query params.
  - Added explicit UI states for legacy fallback vs proof-path unmapped linkage.

## Verification

- Backend baseline:
  - `cd backend && uv run pytest -m no_db`
- Task-targeted backend checks:
  - `DATABASE_URL='sqlite:////tmp/grant_reviewer_wf0059_test.db' uv run pytest tests/test_api.py -k "wf0059_contract_hierarchical_submit_validation_and_idempotency"`
  - `DATABASE_URL='sqlite:////tmp/grant_reviewer_wf0059_test.db' uv run pytest tests/test_structured_reviewer_service.py -k "wf0059_structured_payload_normalization_contract"`
  - `DATABASE_URL='sqlite:////tmp/grant_reviewer_wf0059_task4_test.db' uv run pytest tests/test_api.py -k "wf0059_contract_persisted_submitted_node_coverage"`
  - `DATABASE_URL='sqlite:////tmp/grant_reviewer_wf0059_task7_test.db' uv run pytest tests/test_api.py -k "wf0059_zero_card_node_remains_reviewed_from_persisted_coverage"`
- Frontend targeted checks:
  - `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0059_submit_tracer_erc_proof_call_reaches_structured_review"`
  - `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0059_submit_tracer_preserves_veni_flat_path"`
  - `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0059_review_detail_proof_path_uses_call_linked_ordering"`
  - `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0059_review_detail_explicit_legacy_fallback_and_unmapped_state"`
  - `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0059_review_detail_proof_path_blocks_query_param_fallback"`
  - `cd frontend && npm run test:ui`

## Proof Artifact

- Submit artifact: `docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_submit.json`
- Review-detail artifact: `docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_review_detail.json`
- Both artifacts are tied to review `bb5b6f57-6f16-4a20-a5b0-eab71cf91d69`.
- The review-detail artifact shows:
  - `call_code = erc_stg_2026_full`
  - `submitted_node_logical_ids = ["b1_part1_scientific_proposal", "b1_cv_track_record"]`
  - `ordering_source = call_nodes`
  - review cards ordered and labeled from call-linked metadata
- The evidence harness used deterministic API-level stubs for request validation/pipeline output so the artifact could prove submit + persisted coverage + call-aware detail ordering against the locked ERC proof call in one repeatable run.

## Risks

- ERC proof-path evidence currently depends on a deterministic harness for the validator/pipeline seam, not a fully native proof-call pipeline success path.
- Review-detail explicit-state inference exists in both the BFF route and the page fallback path; future state additions should keep those branches aligned or consolidate them.
