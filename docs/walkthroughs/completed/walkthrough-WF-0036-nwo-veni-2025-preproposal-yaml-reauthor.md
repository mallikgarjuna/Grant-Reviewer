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
PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run
```

Expected: exits 0; prints the ingested call payload (no DB writes).

2. Schema-only validation:

```bash
cd backend
PYTHONPATH=. uv run python -c "from app.schemas.call_definitions_v2 import CallDefinitionV2; import yaml, pathlib; p=pathlib.Path('data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml'); CallDefinitionV2.model_validate(yaml.safe_load(p.read_text())); print('ok')"
```

Expected: prints `ok`.

---

## DB/API Preflight Smoke-Test (Executed Later) (2026-02-28)

This is a lightweight runtime smoke-test to confirm DB ingest and the public call-config/metadata endpoints are consistent for the canonical Veni call definition.

```bash
cd backend
export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable"
./scripts/reset_test_db.sh
PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml

export LLM_MODE=stub
PYTHONPATH=. uv run python - <<'PY'
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
code = "nwo_veni_2025_preproposal"

calls = c.get("/calls")
assert calls.status_code == 200, calls.text
call_id = next(x["id"] for x in calls.json()["calls"] if x["code"] == code)

flat = c.get(f"/calls/{call_id}/nodes")
assert flat.status_code == 200, flat.text
assert all(n.get("parent_node_id") is None for n in flat.json().get("nodes", [])), "expected flat nodes only"

assert c.get(f"/calls/{call_id}/nodes?view=tree").status_code == 200
assert c.get(f"/api/public/calls/{code}/config").status_code == 200
assert c.get(f"/api/public/calls/{code}/nodes/metadata").status_code == 200
print("ok", code, call_id)
PY
```

Observed: flat call (no `parent_node_id` links), and `/api/public/...` endpoints returned `structured_nodes` config and complete metadata.

## What Shipped

- Canonical call YAML: `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`
- Archived legacy YAML: `backend/data/calls/legacy/nwo/nwo_veni_2025_preproposal_legacy.yaml`
- Source manifest: `backend/data/calls/sources/nwo_veni_2025_preproposal.sources.md`
