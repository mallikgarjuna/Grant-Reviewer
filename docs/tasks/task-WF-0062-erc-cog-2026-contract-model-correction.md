<!-- docs/tasks/task-WF-0062-erc-cog-2026-contract-model-correction.md -->
# WF-0062 — ERC CoG 2026 Contract Model Correction

Artifact: task
Version: v0.1
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

## Changelog

- v0.1 (2026-03-07): Backfilled after implementation to match the actual WF-0062 branch scope and verification evidence.
