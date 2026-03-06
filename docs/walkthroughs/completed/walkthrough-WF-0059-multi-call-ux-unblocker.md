<!-- docs/walkthroughs/walkthrough-WF-0059-multi-call-ux-unblocker.md -->
# WF-0059 — Multi-call UX Unblocker

Artifact: walkthrough
Version: v0.3
Status: Completed
Last Updated: 2026-03-06

Type: feature

## Summary

- Unblocked the locked ERC proof call `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml` through the existing structured-review submit path without widening generic nested-call support.
- Preserved structured-review validation ordering and idempotency mismatch behavior across the proof path after the later WF-0060 ERC contract correction.
- Moved proof-path review detail coverage and ordering onto persisted leaf coverage plus call-linked metadata, with explicit state handling for legacy fallback and proof-path unmapped linkage.

## What Changed

- Frontend submit:
  - Allowed only `erc_stg_2026_full` to traverse grouped nested structure without hitting the `nested_nodes` unsupported state.
  - After WF-0060 reconciliation, submit remains leaf-only for ERC StG 2026 while preserving grouped rendering.
  - Kept flat-call/Veni submit behavior unchanged.
- Backend structured review:
  - Accepted recursive hierarchical request payloads and flattened them deterministically at the contract boundary.
  - Persisted downstream coverage in the merged branch via `submitted_leaf_ids`, while preserving `submitted_node_logical_ids` compatibility for older review payloads.
- Review detail:
  - Exposed explicit `detail_state`, `submitted_leaf_ids`, compatibility metadata, and retained `submitted_node_logical_ids` compatibility on the review-detail contract.
  - Derived proof-path reviewed/not-reviewed sections from persisted review-linked coverage plus call metadata instead of `submitted_nodes` query params.
  - Added explicit UI states for legacy fallback vs proof-path unmapped linkage.

## Verification

- Backend baseline:
  - `cd backend && uv run pytest -m no_db`
- Post-WF-0060 isolated Postgres verification:
  - `cd backend && ./scripts/verify_tests_postgres.sh tests/test_api.py -k 'wf0059_ or wf0060_ or structured_review_validation_error_precedes_idempotency_mismatch'`
  - `cd backend && RESET_DB=0 ./scripts/verify_tests_postgres.sh tests/test_structured_reviewer_service.py -k 'wf0059_structured_payload_normalization_contract or wf0060_structured_review_rejects_erc_container_submission_ids'`
- Frontend targeted checks:
  - `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0059_submit_tracer_erc_proof_call_reaches_structured_review"`
  - `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0059_submit_tracer_preserves_veni_flat_path"`
  - `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0059_review_detail_proof_path_uses_call_linked_ordering"`
  - `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0059_review_detail_explicit_legacy_fallback_and_unmapped_state"`
  - `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0059_review_detail_proof_path_blocks_query_param_fallback"`
  - `cd frontend && npm run test:ui`
- Repo-wide gate:
  - `pre-commit run --all-files`
- Agentic browser validation:
  - Loaded `http://127.0.0.1:3000/` and confirmed landing page renders with the expected PeerLens hero and navigation.
  - Loaded `http://127.0.0.1:3000/app` and confirmed redirect to `http://127.0.0.1:3000/sign-in?redirect_url=%2Fapp`.
  - Confirmed the Clerk sign-in shell renders without browser console errors on the protected route boundary.

## Part B Audit

- Re-ran the adversarial `main...HEAD` technical audit after the Part C1 fix.
- Cleared the only prior blocker: backend `/reviews/{id}` now emits `detail_state` directly, and the direct API contract regression covers both `legacy_fallback` and proof-path unmapped state.
- During the later post-WF-0060 merge reconciliation, stale WF-0059 container-era tests were re-based onto the corrected leaf-only ERC contract before verification.
- Remaining risks are non-blocking:
  - route-level BFF normalization still lacks a direct unit test
  - frontend retains defensive `detail_state` inference in addition to the backend contract

## Proof Artifact

- Submit artifact: `docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_submit.json`
- Review-detail artifact: `docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_review_detail.json`
- Both artifacts are tied to review `bb5b6f57-6f16-4a20-a5b0-eab71cf91d69`.
- The review-detail artifact shows:
  - `call_code = erc_stg_2026_full`
  - `submitted_leaf_ids = ["b1_part1_scientific_proposal", "b1_cv_track_record"]`
  - `ordering_source = call_nodes`
  - review cards ordered and labeled from call-linked metadata
- The evidence harness used deterministic API-level stubs for request validation/pipeline output so the artifact could prove submit + persisted coverage + call-aware detail ordering against the locked ERC proof call in one repeatable run.

## Risks

- ERC proof-path evidence currently depends on a deterministic harness for the validator/pipeline seam, not a fully native proof-call pipeline success path.
- Review-detail explicit-state inference exists in both the BFF route and the page fallback path; future state additions should keep those branches aligned or consolidate them behind the backend contract.
