# WF-0021 — NWO Veni 2025 preproposal (WF-2): DB logical IDs + V2 ingest

Artifact: walkthrough
Version: v1.0
Status: Done
Last Updated: 2026-02-21

## Executive Summary

Phase 3 implementation for WF-0021 has been completed and verified. This initiative successfully hardened the call-definition persistence by introducing a canonical JSONB storage layer (`CallDefinition`) and a stable relational projection keyed by `logical_id`.

Crucially, all entity retrieval queries have been updated to filter out soft-deleted entities (`archived_at IS NULL`), establishing a safe foundation for idempotent ingestion and orphan handling.

## What Was Changed

- **Database Schema**: 
  - Added new `CallDefinition` table with `canonical_json`, `schema_version`, and `checksum` fields, linked 1:1 to `FundingCall`.
  - Added `logical_id` (String) and `archived_at` (DateTime) to `ProposalNode`, `EvaluationCriterion`, and `EvaluationElement`.
  - Generated and ran Alembic migrations.
- **Query Hardening**: 
  - Updated all read queries across `backend/app/services/` to explicitly append `.where(Model.archived_at.is_(None))`.
- **V2 Ingestion Engine**:
  - Implemented logic to parse and compute semantic checksums for incoming calls.
  - Implemented idempotent upsertion relying on `logical_id` as the merge key.
  - Implemented orphan handling: Entities missing from subsequent ingests are soft-deleted via `archived_at = func.now()`.
  - Included fallback logic for missing V2 fields (e.g., deterministic string concatenation for criterion descriptions: `AD 21.3`).
- **Hydration Service**:
  - Built internal read interfaces to fetch the node graph and hydrate configurations.
- **V1 Compatibility**:
  - Maintained full support for existing V1 ingestion formats.

## What Was Tested

Verification (Part B) included:
- **Linting & Formatting**: `pre-commit run --all-files` passed with no issues.
- **Backend Test Suite**: `pytest tests/` executed 32 tests across API endpoints and V2/Dry-Run ingestion modules.

## Validation Results

- All 32 backend tests passed successfully (`100%`).
- V1 regression tests passed, confirming legacy flows are unbroken.
- V2 database idempotency was validated.

## Next Steps

1. Ship the `wf/WF-0021-nwo-veni-2025-preproposal-wf2` branch to `main`.
2. Proceed to the next prioritized WF from the backlog.
