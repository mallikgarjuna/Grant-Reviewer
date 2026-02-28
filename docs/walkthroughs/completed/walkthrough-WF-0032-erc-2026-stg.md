# WF-0032 — ERC Starting Grant 2026 Walkthrough

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-02-26

## 1. Goal Overview
Deliver hierarchical proposal-node ingestion for V2 call definitions and author a source-grounded ERC StG 2026 full-call YAML with enforceable reviewer-policy metadata.

## 2. What Changed
- Added V2 schema support for hierarchical authoring and evaluation metadata (`parent_logical_id`, `max_pages`, stage metadata on evaluation elements).
- Refactored ingestion graph handling to validate duplicates/missing parents/self-parent/cycles and persist deterministic preorder with `parent_node_id` linking.
- Added/updated DB and API tests to verify end-to-end hierarchy persistence and flat-node API parent links.
- Authored ERC StG full-call YAML from provided official sources and added a traceability source manifest.
- Hardened reviewer-policy runtime behavior and aligned ERC call artifact layout under `backend/data/calls/erc/` plus `backend/data/calls/sources/`.
- Updated docs/commands to use new ERC paths and parked follow-up re-authoring work for ERC CoG in `docs/parking_lot.md`.

## 3. Verification Evidence
- `pre-commit run --all-files` passed.
- `cd backend && docker compose -f docker-compose.test.yml up -d`
- `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && uv run pytest -q` → `92 passed`.
- `cd backend && uv run python scripts/ingest_call.py data/calls/erc/erc_stg_2026_full.yaml --dry-run` passed.
- `cd backend && uv run python scripts/ingest_call.py data/calls/erc/erc_cog_2026_full_official.yaml --dry-run` passed.

## 3.1 DB/API Preflight Smoke-Test (Executed Later) (2026-02-28)

This is a lightweight runtime smoke-test (in addition to automated tests) to confirm the public call-config and metadata endpoints are consistent after DB ingest.

```bash
cd backend
export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable"
./scripts/reset_test_db.sh
PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/erc/erc_stg_2026_full.yaml

export LLM_MODE=stub
PYTHONPATH=. uv run python - <<'PY'
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
code = "erc_stg_2026_full"

calls = c.get("/calls")
assert calls.status_code == 200, calls.text
call_id = next(x["id"] for x in calls.json()["calls"] if x["code"] == code)

flat = c.get(f"/calls/{call_id}/nodes")
assert flat.status_code == 200, flat.text
assert any(n.get("parent_node_id") for n in flat.json().get("nodes", [])), "expected nested parent_node_id links"

tree = c.get(f"/calls/{call_id}/nodes?view=tree")
assert tree.status_code == 200, tree.text
assert any(n.get("children") for n in tree.json().get("nodes", [])), "expected children in tree view"

assert c.get(f"/api/public/calls/{code}/config").status_code == 200
assert c.get(f"/api/public/calls/{code}/nodes/metadata").status_code == 200
print("ok", code, call_id)
PY
```

Observed: `/calls/{id}/nodes` contained non-null `parent_node_id` links and tree view returned `children[]` (nested call).

## 4. Notable Decisions
- Kept `GET /calls/{id}/nodes` flat with correct `parent_node_id` for MVP stability.
- Stored source traceability next to call artifacts (`backend/data/calls/sources/`) instead of `docs/reference/`.
- Preserved separate `/reviews` and `/api/structured-review` endpoints; shared-core refactor remains parked.

## 5. Next Steps
- Execute shipping flow for this branch (`ship it`).
- Start the parked workflow to re-author ERC CoG from official sources (P2 #23).
