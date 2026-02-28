# WF-0037 — Re-author NWO Vidi 2025 full proposal YAML (official sources)

Artifact: walkthrough
Version: v0.1
Status: Draft
Last Updated: 2026-02-28

---

## Verify (No DB Required)

1. Schema-only validation:

```bash
cd backend
PYTHONPATH=. uv run python -c "from app.schemas.call_definitions_v2 import CallDefinitionV2; import yaml, pathlib; p=pathlib.Path('data/calls/nwo/nwo_vidi_2025_full_proposal.yaml'); CallDefinitionV2.model_validate(yaml.safe_load(p.read_text())); print('ok')"
```

Expected: prints `ok`.

2. Dry-run ingest:

```bash
cd backend
PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/nwo/nwo_vidi_2025_full_proposal.yaml --dry-run
```

Expected: exits 0; prints a dry-run summary and canonical JSON (no DB writes).

## Shipped Files (WF-0037)

- Canonical YAML: `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`
- Source manifest: `backend/data/calls/sources/nwo_vidi_2025_full_proposal.sources.md`
