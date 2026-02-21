# WF-0020 — NWO Veni 2025 preproposal (WF-1): V2 call YAML dry-run loader

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-21

## 1. In Scope

- Add CallDefinition V2 validation support for the NWO Veni 2025 preproposal YAML shape.
- Support `backend/scripts/ingest_call.py --dry-run` for V2 YAML:
  - validate only (no DB writes)
  - no DB connectivity required (`DATABASE_URL` must not be required for dry-run)
  - deterministic summary output suitable for iterating on call YAML authoring
- Preserve existing CallDefinition V1 behavior (existing ERC YAML continues to validate/ingest; V1 dry-run still works).
- Provide actionable validation failures:
  - YAML syntax errors with location when available
  - schema errors with field paths

## 2. Out of Scope

- No DB schema changes, migrations, or new tables/columns.
- No persistence of V2 YAML into DB (WF-2).
- No new API endpoints.
- No frontend changes.
- No compliance engine / alignment engine runtime implementation (only parse/validate/summarize call definition).

## 3. User / System Flow

### Happy path (V2)

1. Developer runs:
   - `cd backend && uv run python scripts/ingest_call.py data/calls/nwo/nwo_veni_2025_preproposal.yaml --dry-run`
2. Script loads YAML, detects it is V2, validates against V2 schema.
3. Script prints a deterministic summary including:
   - funding call metadata (title/stage/year; IDs/codes when present)
   - proposal node list (IDs/labels) and key constraints summary
   - evaluation criteria count + evaluation elements counts (per criterion)
   - compliance rules counts (by severity) and runtime notes count (if present)
4. Script exits 0 without importing/initializing DB connectivity code.

### Failure path 1: YAML syntax error

1. Developer runs dry-run with a malformed YAML file.
2. Script fails fast with:
   - clear message
   - file path
   - line/column and brief context (when available from the YAML parser)
3. Exits non-zero.

### Failure path 2: Schema validation error (shape mismatch / missing keys)

1. Developer runs dry-run with YAML that parses but violates V2 schema.
2. Script fails fast with:
   - schema path(s) to offending field(s)
   - concise per-error messages (avoid huge dumps)
3. Exits non-zero.

### Failure path 3: Ambiguous V1/V2 detection

1. Developer runs dry-run on a YAML that lacks the discriminant keys (or contains both).
2. Script fails with an explicit message explaining:
   - how V1 vs V2 detection works
   - what key(s) must be present to disambiguate

## 4. Functional Requirements

### FR1 — V1/V2 detection and routing

- Implement deterministic detection:
  - V1 if `funding_agency.short_name` exists
  - V2 if `funding_agency.id` exists
  - otherwise: fail with a clear error
- Route validation to the correct schema (existing V1 models; new V2 models).

### FR2 — V2 schema coverage (minimum for the current NWO YAML)

- V2 must accept the current NWO YAML fields used by:
  - `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`
- At minimum, model and validate:
  - `funding_agency` (including `id`, `name`, `country`)
  - `funding_call` (including `id`, `code`, `title`, `year`, `stage`, `language`, `deadlines`, `domain_notes`)
  - `evaluation_criteria` with:
    - `id`, `name`, `stage`, `weight_percent`
    - `evaluation_elements` with `id`, `name`, `description`, `source_hint`
  - `proposal_nodes` with:
    - `id`, `label`, `node_type` (as-is from YAML, e.g. `narrative`)
    - `source_section`, `guidance_text`
    - `content_constraints` (including word limits and max items, as structured in YAML)
    - `compliance_rules` entries (with `id`, `severity`, `rule_type`, `description`)
    - `node_expectations` (including `evaluation_element_id`, `expectation_strength`, `evaluation_intent`, `guidance_note`)
  - `runtime_notes` (id + description)

### FR3 — Dry-run must not require DB

- Dry-run must not import/initialize modules that raise when `DATABASE_URL` is missing.
- Dry-run must not create engine/session, create tables, or attempt inserts/updates.

### FR4 — Deterministic summary output (dry-run)

- Output must be deterministic across runs:
  - stable ordering for lists
  - avoid unordered set/dict representations
- Preferred format:
  - single JSON object (pretty-printed) with `sort_keys=True`, plus a short human-readable headline.

### FR5 — Compatibility with existing V1 ingestion

- Non-dry-run behavior for V1 remains unchanged.
- V1 `--dry-run` behavior remains supported.
- Existing fixture `erc_cog_2026_full.yaml` must still validate under V1.

## 5. Data & API Contracts

### CLI contract (existing)

- Command: `backend/scripts/ingest_call.py <yaml_path> [--dry-run]`
- Exit codes:
  - `0` on success (including dry-run validation)
  - non-zero on parse/validation errors

### Validation rules

- V1 uses existing Pydantic models: `backend/app/schemas/call_definitions.py`.
- V2 uses new Pydantic models under `backend/app/schemas/` (exact filenames are implementation detail).

### Dry-run summary shape (proposed)

- Keys (minimum):
  - `dry_run` (bool)
  - `schema_version` (`"v1"` | `"v2"`)
  - `funding_agency` (id/short_name + name)
  - `funding_call` (code/title/year/stage)
  - `proposal_nodes` (count + list of ids/labels)
  - `evaluation_criteria` (count + element counts)
  - `compliance_rules` (counts by severity, when present)
  - `runtime_notes` (count, when present)

## 6. Components / Modules

Suggested minimal boundaries (no refactors):

- `backend/app/schemas/call_definitions.py`
  - Keep existing V1 models unchanged where possible.
- `backend/app/schemas/call_definitions_v2.py` (new)
  - V2 Pydantic models aligned to the NWO YAML structure.
- `backend/scripts/ingest_call.py`
  - Add V1/V2 detection
  - Ensure dry-run code path avoids DB imports/initialization
  - Implement summary formatting for V2 dry-run

## 7. Edge Cases

- YAML parses but includes unknown keys:
  - V2 should fail by default (catch authoring mistakes early).
- Evaluation element IDs referenced by `node_expectations`:
  - V2 schema should enforce referential integrity (unknown `evaluation_element_id` fails validation).
- Node ordering / stable output:
  - Summary should preserve YAML order for nodes/criteria where possible.

## 8. Telemetry (Minimal)

- None for MVP (CLI-only workflow).

## Deferred / Not in MVP

- DB persistence for V2 YAML (WF-2).
- Logical ID columns in DB + stable mapping (WF-2).
- API endpoints for structured config/reviews.
- Compliance finding generation and persistence.
- Assisted extraction support.

## Open Questions (if any)

- None (defaults chosen per spec: strict V2, deterministic dry-run summary, explicit detection rule).

## Changelog

- v0.1 (2026-02-21): Initial PRD from spec.
