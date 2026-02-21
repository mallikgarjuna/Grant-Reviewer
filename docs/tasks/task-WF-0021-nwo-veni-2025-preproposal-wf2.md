# WF-0021 — NWO Veni 2025 preproposal (WF-2): DB logical IDs + V2 ingest Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-21

## Task Breakdown (Sequential Order)

### Task 1 — Database Schema & Alembic Migration
**Goal:** Introduce the `CallDefinition` table and new metadata columns to the core graph.
**Files to modify:** `backend/app/models/domain.py`, `backend/alembic/versions/*`
**Acceptance Criteria:**
- `CallDefinition` model is created with a 1:1 FK to `FundingCall`, plus `schema_version`, `checksum`, `raw_yaml`, `canonical_json`, and `source_path`.
- `ProposalNode`, `EvaluationCriterion`, and `EvaluationElement` get `logical_id` (String, unique within call) and `archived_at` (DateTime, nullable).
- Alembic migration generated and successfully applied to local Postgres.
**Verification Steps:** Run `alembic upgrade head`. Check DB schema in psql to ensure columns exist.
**Risks (if any):** Migration issues if `logical_id` uniqueness constraint conflicts with existing V1 data (make sure uniqueness constraint handles NULLs or is scoped properly).

### Task 2 — Hardening Application Read Queries
**Goal:** Ensure all existing queries filter out soft-deleted entities before we introduce soft-deletion mechanics.
**Files to modify:** `backend/app/services/*.py`, `backend/app/api/endpoints/*.py` (wherever queries on nodes/criteria/elements are made).
**Acceptance Criteria:**
- All `select()` statements for `ProposalNode`, `EvaluationCriterion`, and `EvaluationElement` explicitly add `.where(Model.archived_at.is_(None))`.
**Verification Steps:** Run existing pytest suite (`make test` or `pytest`) to ensure no DB queries break and V1 flows remain green.
**Risks (if any):** Missing a query could resurrect deleted nodes in the AI prompts or UI.

### Task 3 — Canonical Document Storage & Checksum Logic
**Goal:** Handle the first phase of V2 ingestion: parsing, canonicalizing, validating, and storing the JSONB representation.
**Files to modify:** `backend/scripts/ingest_call.py` (or new ingestion service module).
**Acceptance Criteria:**
- Parse V2 YAML and canonicalize to a stable JSON string (sorted keys, no comments).
- Compute SHA-256 semantic checksum.
- Skip ingestion if the stored checksum matches the incoming checksum for the same `FundingCall`.
- Persist `CallDefinition`.
**Verification Steps:** Run dry-run ingestion on V2 YAML fixture. Ensure it correctly reports the deterministic JSON summary and checksum.
**Risks (if any):** Determinism failures if dictionary ordering varies during checksum computation.

### Task 4 — Idempotent Projection Upsert & Orphan Handling
**Goal:** Handle the second phase of V2 ingestion: upserting the relational graph and soft-deleting orphans.
**Files to modify:** `backend/scripts/ingest_call.py` (or new ingestion service module).
**Acceptance Criteria:**
- Upsert Nodes, Criteria, and Elements using `logical_id` as the merge key.
- Deterministically replace `NodeExpectation` records.
- For any existing DB entities belonging to the `FundingCall` that are NOT in the active ingested YAML, set `archived_at = func.now()`.
- Wrap Task 3 and Task 4 in a single DB transaction.
**Verification Steps:** Run ingestion script twice. The second run should report "skipped" (checksum match) or 0 newly inserted rows. Remove a section from YAML and re-ingest: DB should show `archived_at` populated for that section.
**Risks (if any):** Complex SQLAlchemy merge logic; transaction rollback edge cases.

### Task 5 — Single-Read Hydration Service
**Goal:** Provide an internal read interface that fetches the node graph and hydrates configs from the stored JSONB.
**Files to modify:** `backend/app/services/call_definition_service.py` (new).
**Acceptance Criteria:**
- Service queries the projection (filtered by `archived_at IS NULL`).
- Service queries `CallDefinition` once.
- Merges JSONB constraints/rules into the loaded nodes in-memory via `(call_id, logical_id)`.
**Verification Steps:** Write a unit test that provisions a mock `CallDefinition` and `ProposalNode` and verifies the returned object has the hydrated config.
**Risks (if any):** Potential N+1 query traps if not loaded eagerly.

### Task 6 — V1 Compatibility & Full Verification
**Goal:** Ensure V1 ingestion still works perfectly and the entire V2 flow operates end-to-end.
**Files to modify:** `tests/test_ingestion*.py` (or similar test files).
**Acceptance Criteria:**
- Run V1 existing ingest fixtures; they must ingest successfully (with nullable `logical_id`), preserving exact prior behavior.
- Validate V1 vs V2 detection based on `funding_agency`.
- End-to-end DB round trip tests pass.
**Verification Steps:** Run the full test suite.
**Risks (if any):** Regressions in V1 behavior that block users of legacy calls.

## Changelog
- v0.1 (2026-02-21): Initial tasks from PRD.
- v0.2 (2026-02-21): Applied review edits (made explicit that Task 2 handles the query hardening before ingestion changes; grouped JSON/Checksum and Upsert into separate logical tasks).
