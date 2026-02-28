# WF-0020 — NWO Veni 2025 preproposal (WF-1): V2 call YAML dry-run loader

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-02-21

## Summary

WF-0020 implements dry-run-only support for NWO-style CallDefinition V2 YAML while preserving V1 behavior.

Delivered:
- New strict V2 schema model: `backend/app/schemas/call_definitions_v2.py`.
- Ingest script V1/V2 detection via `funding_agency` discriminants.
- DB-free dry-run path (no `DATABASE_URL` needed for dry-run).
- Deterministic, self-describing dry-run JSON summary.
- Improved YAML syntax error messages with line/column and local context.
- Regression test to ensure V1 and V2 dry-run both work without DB config.

## Files Implemented

- `backend/app/schemas/call_definitions_v2.py`
- `backend/scripts/ingest_call.py`
- `backend/tests/test_ingest_call_dry_run.py`

## How To Run

From repo root:

```bash
cd backend
env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run
```

V1 dry-run compatibility check:

```bash
cd backend
env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/legacy/erc/erc_cog_2026_full_official.yaml --dry-run
```

Targeted regression test:

```bash
cd backend
uv run pytest tests/test_ingest_call_dry_run.py
```

## Verification Log (Executed)

Task 1:
- `cd backend && uv run python -c "from app.schemas.call_definitions_v2 import CallDefinitionV2; import yaml, pathlib; p=pathlib.Path('data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml'); CallDefinitionV2.model_validate(yaml.safe_load(p.read_text())); print('ok')"`
- Result: pass (`ok`)

Task 2:
- `cd backend && env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run`
- Result: pass (schema_version=v2, summary returned)
- `cd backend && env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/legacy/erc/erc_cog_2026_full_official.yaml --dry-run`
- Result: pass (schema_version=v1, summary returned)

Task 3:
- `cd backend && env -u DATABASE_URL uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run 2>&1 | rg '"schema_version"'`
- Result: pass (detected `"schema_version": "v2"`)

Task 4:
- malformed YAML temp-file dry-run command (non-committed temp file)
- Result: expected failure with YAML syntax message including line/column/context

Task 5:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py`
- Result: pass (`1 passed`)

## Known Limitations

- V2 ingestion is intentionally dry-run only in this WF. Persisting V2 to DB is deferred to WF-2.
- V1/V2 detection currently depends on `funding_agency.short_name` vs `funding_agency.id` rather than an explicit `schema_version` key.
- Deterministic summary is logged through the script logger; consumers should parse the JSON block from logs.

## Changelog

- v1.0 (2026-02-21): Added implementation walkthrough, execution commands, verification log, and limitations.
