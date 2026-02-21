# WF-0020 — NWO Veni 2025 preproposal (WF-1): V2 call YAML dry-run loader

Artifact: spec
Version: v0.1
Status: Draft
Last Updated: 2026-02-21

## 1. Purpose

Enable offline validation of the NWO Veni 2025 preproposal call definition YAML by adding a CallDefinition V2 schema/loader and supporting `scripts/ingest_call.py --dry-run` for V2 YAML files.

This unblocks authoring and iterating on “evaluation criteria” / “evaluation elements” definitions and proposal node structure without touching the database or the product UI.

## 2. User / System Context

- Primary user: developer/admin maintaining call definition YAML files.
- Context: running the ingestion CLI locally to validate call definition files during authoring.
- Target input files:
  - V2 (NWO): `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`
  - V1 (existing fixture): `backend/data/calls/erc_cog_2026_full.yaml` (must remain supported)
- Current limitation: existing schema/loader (`backend/app/schemas/call_definitions.py`) only supports the V1 shape and cannot validate the NWO V2 YAML structure.

## 3. Core Behavior

When running:

- `uv run python scripts/ingest_call.py backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml --dry-run`

The system must:

1. Load YAML.
2. Detect whether the YAML is V1 or V2 (deterministic rule).
3. Validate against the correct schema (V1 or V2).
4. In dry-run mode: print/log a deterministic summary and exit 0, without requiring DB connectivity and without writing anything to DB.

Dry-run summary minimum content (V2):
- Funding call metadata (title/stage/year/code if present).
- Proposal nodes list (IDs/labels) and key constraints summary (e.g., word limits, max items).
- Evaluation criteria count + evaluation elements count (and per-criterion counts).
- Compliance rules count (by severity) and runtime notes count, if present.

Failure behavior:
- YAML syntax errors: show actionable location info (line/column) when available.
- Schema validation errors: show failing field path(s) and a concise message per error.

## 4. In Scope

- Define a CallDefinition V2 schema that matches the concrete NWO Veni YAML shape (including:
  `funding_agency.id/country`, `funding_call.title/stage/language/deadlines/domain_notes`,
  `evaluation_criteria[].weight_percent`, `evaluation_elements[].source_hint`,
  `proposal_nodes[].id/label/node_type: narrative`, `content_constraints`, `compliance_rules`, `runtime_notes`).
- Implement a V2 loader / validator path used by `scripts/ingest_call.py`.
- Add V1/V2 detection logic and route to the correct validator.
- Extend or adjust `--dry-run` behavior so V2 dry-run:
  - does not initialize DB
  - does not require `DATABASE_URL`
  - prints/logs a stable summary (not a raw dump)
- Preserve existing V1 behavior (ERC YAML still validates and ingests as before; V1 dry-run still works).

## 5. Out of Scope

- No DB schema changes, migrations, or new tables/columns.
- No new API endpoints (FastAPI or otherwise).
- No frontend/UI changes.
- No persistence of V2 YAML into DB (that is WF-2).
- No implementation of compliance engine, alignment engine, assisted extraction, or NOT_ASSESSABLE logic (future WFs).

## 6. Data & Dependencies

- YAML parsing: `yaml.safe_load` (PyYAML).
- Validation: Pydantic models (current repo uses Pydantic-based ingestion schemas).
- CLI entry point: `backend/scripts/ingest_call.py`.
- V1 schema: `backend/app/schemas/call_definitions.py` (must remain supported).
- V2 schema: new Pydantic models co-located under `backend/app/schemas/` (exact file path TBD during implementation, but must be importable by the script).

## 7. Edge Considerations

- **Version detection**: NWO V2 YAML currently does not declare an explicit version field; detection must be via a stable discriminant (e.g., presence of `funding_agency.id` vs `funding_agency.short_name`, `proposal_nodes[].id` vs `proposal_nodes[].title`, etc.). The rule must be documented in code.
- **Terminology**: any user-facing output should prefer “evaluation criteria / evaluation elements” (avoid “rubric” in CLI copy).
- **Strictness vs brittleness**: schema should be strict enough to catch mistakes, but must not reject valid YAML due to harmless extra keys unless that’s intentional (decision to be made during implementation).
- **Deterministic summary**: ordering should be stable across runs (avoid unordered dict/set output).
- **Non-DB dry-run**: ensure dry-run does not import/initialize DB session paths that require `DATABASE_URL`.

## Changelog

- v0.1 (2026-02-21): Initial spec from brainstorm.
