<!-- docs/walkthroughs/walkthrough-WF-0062-erc-cog-2026-contract-model-correction.md -->
# WF-0062 Walkthrough — ERC CoG 2026 Contract Model Correction

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-07

## Scope

Implemented a narrow CoG correction workflow: canonical contract re-authoring, source-manifest refresh, generalized memory note, and alignment of stale CoG API proof seams.

## What Changed

1. Re-authored [erc_cog_2026_full.yaml](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/canonical/erc/erc_cog_2026_full.yaml) to the corrected container/leaf structure:
   - `part_a -> budget -> resources_time_commitment`
   - `part_b -> b1 -> proposal_summary / b1_part1_scientific_proposal / b1_cv_track_record`
   - `part_b -> b2 -> b2_part2_scientific_proposal`
2. Removed the old CoG split-node shape that treated `b1`/`b2` as expectation-bearing surfaces.
3. Preserved CoG-specific nuance in guidance/runtime notes:
   - PI independence / consolidation expectation
   - 40% PI time commitment on the ERC-funded project
4. Refreshed [erc_cog_2026_full.sources.md](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/data/calls/sources/erc_cog_2026_full.sources.md) to the explicit 3-document source set accepted for this run.
5. Recorded the generalized CoG/StG shared-structure rule in [yaml_definitions.md](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/memory/domain/yaml_definitions.md).
6. Fixed stale CoG API proof seams in [test_api.py](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/tests/test_api.py) that still referenced the old node ID `b1_part1_state_of_knowledge`; they now use `b1_part1_scientific_proposal`.
7. Closed the Phase 3 audit gaps:
   - normalized legacy persisted CoG leaf IDs onto corrected leaf coverage in review detail
   - removed stale `b1` container scoping from CoG reviewer policy
   - added deterministic CoG tree and metadata proofs for the corrected hierarchy
   - added explicit API rejection proof for submitting old CoG leaf IDs after the correction

## Verification Evidence

- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k erc_cog_2026_full`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml --dry-run`
- `cd backend && export DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' && ./scripts/reset_test_db.sh`
- `cd backend && export DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' && uv run pytest tests/test_ingest_call_v2_db.py -k erc_cog_2026_full`
- `cd backend && export DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' && export LLM_MODE=stub && uv run pytest tests/test_api.py -k "structured_review_erc_cog_2026_full_happy_path or structured_review_wf0044_policy_structured_api_modes"`
- `cd backend && ./scripts/reset_test_db.sh`
- `cd backend && DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' LLM_MODE=stub uv run pytest tests/test_api.py::test_wf0062_review_detail_maps_legacy_cog_leaf_ids_to_corrected_leaf_coverage tests/test_api.py::test_structured_review_erc_cog_2026_full_happy_path tests/test_api.py::test_structured_review_erc_cog_2026_full_rejects_legacy_leaf_ids tests/test_api.py::test_structured_review_wf0044_policy_structured_api_modes tests/test_call_nodes_tree_api.py::test_wf0060_erc_tree_models_structural_containers_without_review_surfaces tests/test_call_nodes_tree_api.py::test_wf0062_erc_cog_tree_models_structural_containers_without_review_surfaces tests/test_call_nodes_metadata_api.py::test_wf0060_erc_metadata_moves_resources_under_budget_without_changing_leaf_identity tests/test_call_nodes_metadata_api.py::test_wf0062_erc_cog_metadata_exposes_corrected_hierarchy_and_leaf_review_stages tests/test_ingest_call_v2_db.py::test_v2_ingest_supports_erc_cog_2026_full`

## Outcome

WF-0062 is completed and ship-gated: canonical CoG is now source-grounded, structurally aligned with the corrected ERC 2026 form family, and backed by passing dry-run, DB-ingest, API, review-detail compatibility, and read-surface proofs.
