# WF-0036 — Re-author NWO Veni 2025 preproposal YAML (official sources)

Artifact: walkthrough
Version: v1.0
Status: Done
Last Updated: 2026-02-26

---

## Verify (No DB Required)

1. Dry-run ingest:

```bash
cd backend
PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/nwo/nwo_veni_2025_preproposal.yaml --dry-run
```

Expected: exits 0; prints the ingested call payload (no DB writes).

2. Schema-only validation:

```bash
cd backend
PYTHONPATH=. uv run python -c "from app.schemas.call_definitions_v2 import CallDefinitionV2; import yaml, pathlib; p=pathlib.Path('data/calls/nwo/nwo_veni_2025_preproposal.yaml'); CallDefinitionV2.model_validate(yaml.safe_load(p.read_text())); print('ok')"
```

Expected: prints `ok`.

## What Shipped

- Canonical call YAML: `backend/data/calls/nwo/nwo_veni_2025_preproposal.yaml`
- Archived legacy YAML: `backend/data/calls/nwo/nwo_veni_2025_preproposal_legacy.yaml`
- Source manifest: `backend/data/calls/sources/nwo_veni_2025_preproposal.sources.md`
