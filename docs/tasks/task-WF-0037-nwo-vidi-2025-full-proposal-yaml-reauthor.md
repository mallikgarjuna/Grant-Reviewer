# WF-0037 — NWO Vidi 2025 full proposal call definition (official sources)

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-28

## Task Breakdown (Sequential Order)

### [x] Task 1 — Align Vidi YAML With PRD Decisions (Remove AES-only Evaluation)

Goal:
Ensure the canonical Vidi YAML does not encode AES-only evaluation semantics that would be evaluated for all submissions (no domain gating yet).
Slice: tracer-bullet
User Stories: US1
PRD Requirements: FR1, FR2, FR4, FR7, FR8
Depends on: none
Enables: Task 2
Parallelizable: no
Files to modify:
- `backend/data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`
- `backend/data/calls/sources/nwo_vidi_2025_full_proposal.sources.md`
Acceptance Criteria:
- `elem_aes_user_committee` is removed from `evaluation_elements` and is not referenced anywhere (no AES-only criterion is evaluated without a domain signal).
- `node_expectations` no longer reference `elem_aes_user_committee`.
- `sources.md` records that the AES-only clause is deferred pending domain gating (with a pointer to WF-0037 PRD decision).
- YAML validates via schema-only validation command.
- `ingest_call.py ... --dry-run` succeeds.
TDD Plan: N/A (data-only; verification via validation + ingest commands).
Verification Steps:
- `cd backend && PYTHONPATH=. uv run python -c "from app.schemas.call_definitions_v2 import CallDefinitionV2; import yaml, pathlib; p=pathlib.Path('data/calls/nwo/nwo_vidi_2025_full_proposal.yaml'); CallDefinitionV2.model_validate(yaml.safe_load(p.read_text())); print('ok')"`
- `cd backend && PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/nwo/nwo_vidi_2025_full_proposal.yaml --dry-run`
Risks (if any):
- Over-correcting and deleting generally applicable impact elements; ensure only AES-specific clause is removed/deferred.
- If this reveals a schema gap (domain gating / non-evaluable guidance separation), stop and promote a follow-on WF (per PRD Out of Scope).

### [ ] Task 2 — Re-run DB/API Preflight and Update Walkthrough Evidence

Goal:
Prove the updated canonical YAML ingests into a test DB and serves consistent shapes via existing endpoints.
Slice: verification
User Stories: US1
PRD Requirements: FR8
Depends on: Task 1
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0037-nwo-vidi-2025-full-proposal-yaml-reauthor.md`
Acceptance Criteria:
- Ingest into test DB succeeds.
- `/calls`, `/calls/{id}/nodes` (flat/tree), `/api/public/.../config`, `/api/public/.../nodes/metadata` all return 200.
- Metadata returns `unknown_node_logical_ids` empty/absent.
TDD Plan: N/A (verification via scripted smoke-test).
Verification Steps:
- `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && ./scripts/reset_test_db.sh`
- `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && PYTHONPATH=. uv run python scripts/ingest_call.py data/calls/nwo/nwo_vidi_2025_full_proposal.yaml`
- `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && export LLM_MODE=stub && PYTHONPATH=. uv run python - <<'PY'\nfrom fastapi.testclient import TestClient\nfrom main import app\n\nc = TestClient(app)\ncode = \"nwo_vidi_2025_full_proposal\"\n\ncalls = c.get(\"/calls\")\nassert calls.status_code == 200, calls.text\ncall_id = next(x[\"id\"] for x in calls.json()[\"calls\"] if x[\"code\"] == code)\n\nassert c.get(f\"/calls/{call_id}/nodes\").status_code == 200\nassert c.get(f\"/calls/{call_id}/nodes?view=tree\").status_code == 200\nassert c.get(f\"/api/public/calls/{code}/config\").status_code == 200\nmeta = c.get(f\"/api/public/calls/{code}/nodes/metadata\")\nassert meta.status_code == 200\nassert meta.json().get(\"unknown_node_logical_ids\") in (None, []), meta.json()\nprint(\"ok\", code, call_id)\nPY`
Risks (if any):
- If domain gating becomes required to represent constraints correctly, stop and promote a follow-on WF (per PRD).

## Changelog

- v0.1 (2026-02-28): Initial task breakdown from PRD.
- v0.2 (2026-02-28): Applied Phase 2.2 review edits (tightened Task 1 acceptance criteria; marked ready for implementation).
