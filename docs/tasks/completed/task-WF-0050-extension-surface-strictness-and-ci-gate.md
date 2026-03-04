# WF-0050 — Extension Surface Strictness + CI Contract Gate

Artifact: task
Version: v1.0
Status: Completed
Last Updated: 2026-03-04

## Task Breakdown

### [x] Task 1 — Strict `compliance_rules` + explicit CI contract gate
Files:
- `backend/app/engine/contracts.py`
- `backend/tests/engine/test_review_request_contracts.py`
- `.github/workflows/ci.yml`
Verification:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0050_contract_compliance_rules_surface_strict or wf0050_contract_producer_stress_fixture_requests_validate"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0048_contract_ or wf0049_contract_"`
- `cd backend && uv run pytest -m no_db`

### [x] Task 2 — Strict `stage_gating`, `hierarchy`, `nesting`
Files:
- `backend/app/engine/contracts.py`
- `backend/tests/engine/test_review_request_contracts.py`
Verification:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0050_contract_stage_gating_surface_strict or wf0050_contract_hierarchy_surface_strict or wf0050_contract_nesting_surface_strict"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0050_contract_ or wf0049_contract_ or wf0048_contract_"`
- `cd backend && uv run pytest -m no_db`

## Commits
- `8bbf236` — strict `compliance_rules` + explicit CI contract gate
- `5ef09b8` — strict `stage_gating`/`hierarchy`/`nesting`
