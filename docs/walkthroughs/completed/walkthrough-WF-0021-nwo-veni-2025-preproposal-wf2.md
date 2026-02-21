# WF-0021 — NWO Veni 2025 preproposal (WF-2): DB logical IDs + V2 ingest

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-02-21

## Summary

Implemented Phase 3 for WF-0021 end-to-end:
- Added database support for canonical call-definition storage and logical IDs.
- Hardened active read queries to exclude archived projection rows.
- Implemented transactional V2 ingestion with deterministic canonical JSON checksum, idempotent skip behavior, upsert-by-logical-id projection updates, and orphan soft-deletion.
- Added a single-read hydration service that merges active projection nodes with canonical JSON configuration.
- Added regression tests covering V1 compatibility and V2 end-to-end behavior.

## Task Execution Record

### Task 1 — Database Schema & Alembic Migration
- Added `CallDefinition` model in `backend/app/models/domain.py`.
- Added `logical_id` + `archived_at` to `ProposalNode`, `EvaluationCriterion`, and `EvaluationElement`.
- Added migration `backend/migrations/versions/1c4d8f7a9c23_wf_0021_call_definition_logical_id_.py`.
- Verification:
  - `cd backend && uv run alembic upgrade head`
  - DB schema check via SQL query for added tables/columns.

### Task 2 — Hardening Application Read Queries
- Updated query paths to enforce `archived_at IS NULL` where nodes/criteria/elements are read:
  - `backend/app/repositories/review_repository.py`
  - `backend/scripts/ingest_call.py`
  - `backend/scripts/seed.py`
- Verification:
  - `cd backend && uv run pytest`

### Task 3 — Canonical Document Storage & Checksum Logic
- Extended ingestion pipeline in `backend/scripts/ingest_call.py` to:
  - Build deterministic canonical JSON (`sort_keys=True`, compact separators).
  - Compute SHA-256 checksum.
  - Persist/update `CallDefinition` record.
  - Skip re-ingest on checksum match.
- Verification:
  - Dry-run deterministic checksum assertions in tests.

### Task 4 — Idempotent Projection Upsert & Orphan Handling
- Implemented V2 projection upsert by `logical_id` for nodes/criteria/elements.
- Implemented deterministic `NodeExpectation` replacement per node.
- Implemented orphan handling via `archived_at` soft-delete for missing projection rows.
- Wrapped V2 persistence + projection updates inside one transaction.
- Verification:
  - Re-ingest same YAML => skipped.
  - Remove a node from YAML and re-ingest => archived row asserted in DB.

### Task 5 — Single-Read Hydration Service
- Added `backend/app/services/call_definition_service.py` with `CallDefinitionService.get_hydrated_nodes(call_id)`.
- Service performs one active projection read + one `CallDefinition` read and merges config by `logical_id`.
- Verification:
  - Hydration unit test validates merged `content_constraints` and `compliance_rules`.

### Task 6 — V1 Compatibility & Full Verification
- Added `backend/tests/test_ingest_call_v2_db.py` for:
  - V2 deterministic dry-run checksum.
  - V1 ingest compatibility with nullable logical IDs.
  - V2 idempotency + orphan soft-delete behavior.
  - Hydration merge behavior.
- Verification:
  - `cd backend && uv run pytest` => all tests passing.

## Verification Evidence

- `pre-commit run --all-files` -> Passed.
- `cd backend && uv run pytest` -> 32 passed.

## Commits (Phase 3)

- `e6322f3` — Task 1
- `5524a64` — Task 2
- `9b95378` — Task 3
- `6281478` — Task 4
- `87d3e7b` — Task 5
- `3e2021b` — Task 6

## Notes

- No push/PR/merge performed in this phase.
