# WF-0021 — NWO Veni 2025 preproposal (WF-2): DB logical IDs + V2 ingest

Artifact: spec
Version: v0.2
Status: Ready for PRD
Last Updated: 2026-02-21

## 1. Purpose

Make call-definition persistence robust to schema evolution by introducing a canonical call-definition document store (JSONB) while maintaining a stable relational projection for review/query flows and traceability via stable `logical_id`s.

## 2. User / System Context

This capability is primarily used by internal developers/admins who run the ingestion pipeline to maintain call definitions. It also serves backend developers building review and compliance features, who need stable references (`logical_id`) and access to evolving configuration rules without schema drift forcing DB migrations or API rewrites.

## 3. Core Behavior

The ingestion process is a two-phase, single-transaction operation:
1. **Document Storage**: Validate and persist the call definition as a canonical JSONB document, recording its `schema_version` and computing a semantic `checksum` (using a deterministic hashing algorithm like SHA-256 over the canonicalized JSON).
2. **Relational Projection**: Idempotently upsert the core review graph (nodes, criteria, elements, expectations, `guidance_text`) keyed by the stable `logical_id`.

At runtime, an internal read service fetches the canonical JSONB document once per call and hydrates per-node configuration (like constraints, rules, notes) in-memory, avoiding N+1 JSON parsing.

## 4. In Scope

- Canonical call-definition document storage (JSONB + `schema_version` + `checksum` + `source_path`).
- Stable relational projection of the core graph (nodes, evaluation criteria, evaluation elements, expectations) keyed by `logical_id`.
- Transactional, idempotent ingestion (insert/update based on `logical_id`).
- Orphan handling strategy: soft-delete (using an `archived_at` timestamp column) for nodes/criteria/elements that are omitted in a re-ingested call definition. Node expectations are deterministically replaced.
- V2 YAML schemas must explicitly define `logical_id`s for core entities; ingestion will fast-fail if omitted.
- Internal read service for single-read hydration of node configs from JSONB.
- DB round-trip verification, idempotent re-ingest tests, and V1 regression tests.
- Preserving V1 ingestion behavior and existing fixtures (with canonical storage for V1 if feasible).

## 5. Out of Scope

- Frontend UI changes or structured configuration endpoints (planned for WF-3).
- Compliance engine implementation (planned for WF-4).
- Normalizing all constraints and rules into relational tables (they stay in JSONB).
- Broadening scope to ingest other funder schemas beyond the current NWO V2 requirements.
- External or paid API calls (e.g., OpenAI) during the ingestion process.

## 6. Data & Dependencies

- **Database**: PostgreSQL with `JSONB` support.
- **Schema Changes**:
  - New table/columns for the canonical document.
  - New `logical_id` string columns on projection tables (unique per call).
  - Soft-delete archivation columns (e.g., `archived_at` timestamp).
- **Dependencies**: Uses existing Pydantic models for validation and SQLAlchemy for transaction management.

## 7. Edge Considerations

- **Migrations/Backfill**: Existing V1 DB rows lack `logical_id`s. We must either allow `logical_id` to be nullable for legacy data or provide a deterministic backfill script (e.g., slugified names) to safely enforce `logical_id` presence going forward. New V2 schemas mandate `logical_id` explicitly.
- **Semantic Checksum**: The checksum must be computed over the canonicalized JSON representation (stable key ordering, no whitespace/comments) to avoid redundant updates if only YAML formatting changes.

## Changelog

- v0.1 (2026-02-21): Initial spec from brainstorm
- v0.2 (2026-02-21): Applied review edits (enforce logical_id for V2, use archived_at for orphans, specify SHA-256 for checksum)
