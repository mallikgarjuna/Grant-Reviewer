# WF-0037 — Re-author NWO Vidi 2025 full proposal YAML (official sources)

Artifact: walkthrough
Version: v1.0
Status: Done
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

## DB/API Preflight (Executed, Test DB Only)

This is a smoke-test to catch runtime shape/mapping issues before any frontend work depends on the new call.

1. Reset local test DB (destructive to test DB only):

```bash
cd backend
export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable"
./scripts/reset_test_db.sh
```

2. Ingest into the test DB:

```bash
cd backend
export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable"
PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/nwo/nwo_vidi_2025_full_proposal.yaml
```

3. API preflight via FastAPI `TestClient` (no server process):

```bash
cd backend
export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable"
export LLM_MODE=stub
PYTHONPATH=. uv run python - <<'PY'
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
code = "nwo_vidi_2025_full_proposal"

calls = c.get("/calls")
assert calls.status_code == 200, calls.text
call_id = next(x["id"] for x in calls.json()["calls"] if x["code"] == code)

assert c.get(f"/calls/{call_id}/nodes").status_code == 200
assert c.get(f"/calls/{call_id}/nodes?view=tree").status_code == 200
assert c.get(f"/api/public/calls/{code}/config").status_code == 200
assert c.get(f"/api/public/calls/{code}/nodes/metadata").status_code == 200
print("ok", code, call_id)
PY
```

Expected: prints `ok nwo_vidi_2025_full_proposal <call_id>`.

Execution evidence (2026-02-28):
- Ingest result: `criteria_upserted=2`, `elements_upserted=14`, `nodes_upserted=4`, `expectations_replaced=17`.
- API preflight result:
  - `ok nwo_vidi_2025_full_proposal e863fa73-4f93-45e1-90d7-37ac12c29dba flat 4 tree_roots 4 expected_nodes 4 unknown None parent_links 0`
- Interpretation:
  - Call is served correctly across `/calls`, `/calls/{id}/nodes` (flat/tree), `/api/public/.../config`, and `/api/public/.../nodes/metadata`.
  - Vidi remains a flat-node call (`parent_links=0`), and metadata has no unknown logical IDs.

## Shipped Files (WF-0037)

- Canonical YAML: `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`
- Source manifest: `backend/data/calls/sources/nwo_vidi_2025_full_proposal.sources.md`
- Task outcome: removed AES-only `elem_aes_user_committee` from evaluable criteria and node mappings; deferred to future domain-gated modeling per WF-0037 PRD.
