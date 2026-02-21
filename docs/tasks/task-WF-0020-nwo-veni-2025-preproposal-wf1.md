# WF-0020 — NWO Veni 2025 preproposal (WF-1): V2 call YAML dry-run loader

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-02-21

## Task Breakdown (Sequential Order)

### Task 1 — Add CallDefinition V2 Pydantic schema

Goal:
Define a strict CallDefinition V2 schema that matches the concrete NWO Veni YAML shape (including nested sub-structures) and enforces referential integrity for `evaluation_element_id` references.

Files to modify:
- `backend/app/schemas/call_definitions_v2.py` (new)
- Potentially `backend/app/schemas/__init__.py` (only if needed for imports)

Acceptance Criteria:
- V2 schema validates `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml` with no code changes to the YAML.
- V2 schema rejects unknown keys by default (strict).
- V2 schema fails if a `node_expectations[].evaluation_element_id` references a non-existent evaluation element ID.

Verification Steps:
- `cd backend && uv run python -c "from app.schemas.call_definitions_v2 import CallDefinitionV2; import yaml, pathlib; p=pathlib.Path('data/calls/nwo/nwo_veni_2025_preproposal.yaml'); CallDefinitionV2.model_validate(yaml.safe_load(p.read_text())); print('ok')"`

Risks (if any):
- Pydantic strictness may require explicitly modeling optional fields exactly as used in the YAML; keep scope to the current file’s fields only.

### Task 2 — Add V1/V2 detection + routing in ingest script (no DB for dry-run)

Goal:
Update `backend/scripts/ingest_call.py` to:
1) detect V1 vs V2 deterministically via `funding_agency.short_name` vs `funding_agency.id`
2) validate with the correct schema
3) ensure `--dry-run` runs without `DATABASE_URL` by avoiding DB imports/initialization before the dry-run early return

Files to modify:
- `backend/scripts/ingest_call.py`

Acceptance Criteria:
- V1 path unchanged for non-dry-run ingest (existing behavior preserved).
- V1 `--dry-run` continues to work.
- V2 `--dry-run` validates the NWO V2 YAML and returns a summary without requiring `DATABASE_URL`.
- If both discriminant keys exist (or neither), dry-run fails with a clear error.

Verification Steps:
- V2 dry-run with no DB env:
  - `cd backend && env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/nwo/nwo_veni_2025_preproposal.yaml --dry-run`
- V1 dry-run still works:
  - `cd backend && env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml --dry-run`

Risks (if any):
- Current script imports DB modules at import time; restructuring must be minimal but sufficient to defer DB imports until needed.

### Task 3 — Implement deterministic dry-run summary output (V2)

Goal:
Produce a deterministic, self-describing JSON summary for V2 dry-run mode (include `schema_version` and `source_path`) without dumping the full YAML.

Files to modify:
- `backend/scripts/ingest_call.py`

Acceptance Criteria:
- Dry-run prints (or logs) a JSON object with stable key ordering and stable list ordering.
- Summary includes:
  - `dry_run`, `schema_version`, `source_path`
  - funding agency (id/name)
  - funding call (code/title/year/stage)
  - proposal nodes (count + list of ids/labels)
  - evaluation criteria (count + per-criterion element counts)
  - compliance rules counts by severity (when present)
  - runtime notes count (when present)

Verification Steps:
- `cd backend && env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/nwo/nwo_veni_2025_preproposal.yaml --dry-run | rg '\"schema_version\"'`

Risks (if any):
- Ensure output remains deterministic (avoid `set` in summary construction).

### Task 4 — Improve YAML parse error messaging (syntax errors)

Goal:
Ensure YAML syntax errors produce actionable messages (file + line/column when available + brief context) while keeping schema errors concise and path-oriented.

Files to modify:
- `backend/scripts/ingest_call.py`

Acceptance Criteria:
- Malformed YAML fails with a clear message including a line/column when available.
- Schema validation errors do not claim to have line/column; they include schema paths and concise messages.

Verification Steps:
- Create a tiny malformed YAML in a temp location and run dry-run to confirm error formatting (do not commit the temp file).

Risks (if any):
- YAML parser exception types differ by loader; handle the PyYAML exceptions used by `yaml.safe_load`.

### Task 5 — Add minimal targeted regression check (script-level)

Goal:
Add a lightweight “smoke” verification step (no DB) that can be run locally/CI to ensure V1 and V2 dry-run both validate.

Files to modify:
- Prefer adding a small test under existing test framework if present (otherwise document a command-only check in the walkthrough during Phase 4).

Acceptance Criteria:
- There is a repeatable command that validates:
  - V1 fixture dry-run succeeds
  - NWO V2 YAML dry-run succeeds
  - V2 dry-run succeeds without `DATABASE_URL`

Verification Steps:
- Run the chosen command(s) and record them in `docs/walkthroughs/walkthrough-WF-0020-nwo-veni-2025-preproposal-wf1.md` during Phase 4.

Risks (if any):
- Don’t introduce new dependencies or DB requirements; keep it pure-Python + existing tooling.

## Changelog

- v0.1 (2026-02-21): Initial task breakdown from PRD.
