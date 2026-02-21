# WF-0021 — NWO Veni 2025 preproposal (WF-2): DB logical IDs + V2 ingest PRD

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-02-21

## 1. In Scope
- Canonical call-definition document storage (JSONB + `schema_version` + `checksum` + `source_path`).
- Stable relational projection of the core graph (nodes, evaluation criteria, evaluation elements, expectations) keyed by `logical_id`.
- Transactional, idempotent ingestion (insert/update based on `logical_id`).
- Orphan handling strategy: soft-delete (`archived_at` timestamp) for nodes/criteria/elements omitted in re-ingest. Node expectations are deterministically replaced.
- **CRITICAL**: Update all existing DB read paths (queries) to filter out soft-deleted entities (`archived_at IS NULL`).
- Internal read service for single-read hydration of node configs from JSONB.
- DB round-trip verification, idempotent re-ingest tests, and V1 regression tests.
- V1 compatibility preservation.

## 2. Out of Scope
- Frontend UI changes.
- Structured configuration endpoints (WF-3).
- Compliance engine implementation (WF-4).
- Normalizing all constraints and rules into relational tables.
- Ingesting other funder schemas beyond NWO V2.
- External or paid API calls (e.g., OpenAI) during ingestion.

## 3. User / System Flow
- **Happy path**: Admin runs V2 ingestion script -> validated YAML is converted to JSONB -> semantic checksum computed -> stored in new doc table (linking to `FundingCall` 1:1) -> core graph is upserted into projection tables using `logical_id` -> success.
- **Failure paths**:
  - Missing `logical_id` in V2 YAML: ingestion fails fast with a validation error.
  - DB transaction fails: canonical document and projection changes are completely rolled back.
  - Invalid YAML schema: ingestion fails before DB transaction begins.

## 4. Functional Requirements
- System must compute a deterministic SHA-256 semantic checksum of the call definition to skip redundant DB updates.
- System must softly delete (`archived_at`) projection rows (nodes, criteria, elements) that are missing from a re-ingested call definition.
- System must assign or handle nullable `logical_id`s for V1 legacy ingest correctly, while enforcing `logical_id` on V2.
- Internal read component must fetch the canonical JSONB document and merge it with relational data without N+1 queries.
- All application queries accessing Nodes, EvaluationCriteria, and EvaluationElements must omit rows where `archived_at IS NOT NULL`.

## 5. Data & API Contracts
- No external API changes.
- **Data Model**:
  - `CallDefinition` (new model): 1:1 with `FundingCall`. Columns: `id`, `funding_call_id` (FK), `schema_version`, `checksum`, `raw_yaml` (optional), `canonical_json` (JSONB), `source_path`.
  - Added `logical_id` (String, unique within call) to `ProposalNode`, `EvaluationCriterion`, `EvaluationElement`.
  - Added `archived_at` (DateTime, nullable) to `ProposalNode`, `EvaluationCriterion`, `EvaluationElement`.

## 6. Components / Modules
- **Ingestion Pipeline**: `scripts/ingest_call.py` or new domain logic for transaction.
- **Data Models**: Additions to `models/domain.py`.
- **Read Service**: Internal service inside `services/` for merging DB projection with JSONB.

## 7. Edge Cases
- V1 database rows backfill: legacy rows without `logical_id` must not block V2 queries.
- Schema version coexistence: the system must recognize and handle V1 vs V2 correctly during ingest and read.
- Queries failing to filter `archived_at` will cause duplicate/zombie nodes to appear in prompts or UI. This is the highest risk edge case.

## 8. Telemetry (Minimal)
- Minimal logging on successful ingest (checksum match vs updated) and validation errors.

## Deferred / Not in MVP
- Endpoint exposure of full JSONB configuration.

## Open Questions (if any)
- None.

## Changelog
- v0.1 (2026-02-21): Initial PRD from spec.
- v0.2 (2026-02-21): Applied risk audit edits. Enforced `archived_at IS NULL` query requirement explicitly. Clarified 1:1 linking of JSONB store with `FundingCall`.
