<!-- docs/tasks/completed/task-WF-0062-erc-cog-2026-contract-model-correction.md -->
# WF-0062 — ERC CoG 2026 Contract Model Correction

Artifact: task
Version: v0.2
Status: Complete
Last Updated: 2026-03-07

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Re-author canonical CoG contract from uploaded sources

Goal:
Bring canonical CoG into line with the official 2026 CoG form and the corrected StG-era container/leaf semantics.
Slice: canonical-contract
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR4
Files modified:
- `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml`
- `backend/data/calls/sources/erc_cog_2026_full.sources.md`
- `docs/memory/domain/yaml_definitions.md`
Verification:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k erc_cog_2026_full`
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml --dry-run`

### [x] Task 2 — Verify real ingest/API path and align stale proof seams

Goal:
Prove the corrected CoG contract survives DB/API use and replace stale proof seams that still target old CoG node IDs.
Slice: verification-proof
User Stories: US3
PRD Requirements: FR5
Files modified:
- `backend/tests/test_api.py`
Verification:
- `cd backend && export DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' && uv run pytest tests/test_ingest_call_v2_db.py -k erc_cog_2026_full`
- `cd backend && export DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' && export LLM_MODE=stub && uv run pytest tests/test_api.py -k "structured_review_erc_cog_2026_full_happy_path or structured_review_wf0044_policy_structured_api_modes"`

### [x] Task 3 — Close ship-gate compatibility and read-surface gaps

Goal:
Close the Phase 3 audit findings so CoG review-detail compatibility and corrected read surfaces are explicitly proven before merge.
Slice: audit-closure
User Stories: US3
PRD Requirements: FR5, FR6, FR7
Files modified:
- `backend/app/repositories/review_repository.py`
- `backend/tests/test_api.py`
- `backend/tests/test_call_nodes_tree_api.py`
- `backend/tests/test_call_nodes_metadata_api.py`
- `backend/data/calls/canonical/erc/erc_cog_2026_full.yaml`
- `docs/memory/domain/yaml_definitions.md`
Verification:
- `cd backend && ./scripts/reset_test_db.sh`
- `cd backend && DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' LLM_MODE=stub uv run pytest tests/test_api.py::test_wf0062_review_detail_maps_legacy_cog_leaf_ids_to_corrected_leaf_coverage tests/test_api.py::test_structured_review_erc_cog_2026_full_happy_path tests/test_api.py::test_structured_review_erc_cog_2026_full_rejects_legacy_leaf_ids tests/test_api.py::test_structured_review_wf0044_policy_structured_api_modes tests/test_call_nodes_tree_api.py::test_wf0060_erc_tree_models_structural_containers_without_review_surfaces tests/test_call_nodes_tree_api.py::test_wf0062_erc_cog_tree_models_structural_containers_without_review_surfaces tests/test_call_nodes_metadata_api.py::test_wf0060_erc_metadata_moves_resources_under_budget_without_changing_leaf_identity tests/test_call_nodes_metadata_api.py::test_wf0062_erc_cog_metadata_exposes_corrected_hierarchy_and_leaf_review_stages tests/test_ingest_call_v2_db.py::test_v2_ingest_supports_erc_cog_2026_full`

## Changelog

- v0.1 (2026-03-07): Backfilled after implementation to match the actual WF-0062 branch scope and verification evidence.
- v0.2 (2026-03-07): Added explicit audit-closure task for legacy CoG compatibility mapping and CoG tree/metadata proof coverage before ship.
