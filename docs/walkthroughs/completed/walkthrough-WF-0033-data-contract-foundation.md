# WF-0033 — Data Contract Foundation Walkthrough

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-02-26

---

## 1. Goal Overview

Deliver the backend data-contract foundation for hierarchical grant calls by adding tree-shaped node responses, a public node metadata DTO endpoint, and deterministic mismatch/cycle safety behavior aligned to V2 call-definition structure.

## 2. What Changed

- Extended `GET /calls/{call_id}/nodes` to support `view=flat|tree` with backward-compatible flat default.
- Added `logical_id` to flat node DTOs and introduced recursive tree DTOs (`NodeTreeNode`, `NodesTreeResponse`).
- Implemented canonical tree construction from V2 `proposal_nodes[].id + parent_logical_id` via `NodeTreeService`.
- Added strict failure handling for canonical/DB mismatches and canonical cycles with explicit API codes:
  - `CALL_DEFINITION_NODE_MISMATCH` (409)
  - `CALL_DEFINITION_CYCLE` (409)
- Added `GET /api/public/calls/{call_logical_id}/nodes/metadata` returning UI-oriented metadata DTOs.
- Implemented metadata filtering via repeated `node_logical_ids` query params and partial-success unknown reporting (`unknown_node_logical_ids`).
- Refactored metadata projection logic into `NodeMetadataService` and kept route handler thin.
- Updated error-code consistency test to include newly introduced metadata/tree contract error codes.

## 3. Verification Evidence

- `cd backend && export DATABASE_URL='postgresql+psycopg://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' && pre-commit run --all-files` passed.
- `cd backend && export DATABASE_URL='postgresql+psycopg://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' && PYTHONPATH=. uv run pytest -q` -> `101 passed`.
- Targeted contract tests added and passing:
  - `backend/tests/test_call_nodes_tree_api.py`
  - `backend/tests/test_node_tree_service.py`
  - `backend/tests/test_call_nodes_metadata_api.py`

## 4. Notable Decisions

- Kept `/calls/{call_id}/nodes` as the canonical endpoint and introduced shape switching through `view` instead of creating a second tree endpoint.
- Used V2 canonical JSON as tree source-of-truth when valid; retained DB adjacency fallback for legacy/no-definition cases.
- For metadata filtering, chose partial success (`200`) with explicit unknown IDs rather than hard-fail on mixed requests.

## 5. Commit Trail (Phase 3)

- `03a124c` Task 1: tree view tracer bullet + flat `logical_id`.
- `8b55955` Task 2: canonical parent-based tree service integration.
- `a6f048d` Task 3: deterministic 409 mismatch/cycle handling.
- `0378711` Task 4: metadata endpoint tracer.
- `843abe6` Task 5: metadata filtering + unknown IDs response.
- `7223587` Task 6: metadata service refactor.
- `aa5a486` Part B verification fix: error-code mapping test alignment.

## 6. Next Steps

- Execute `ship it` flow for the WF branch.
- Start the next workflow from `docs/parking_lot.md` if there is no follow-up for WF-0033.
