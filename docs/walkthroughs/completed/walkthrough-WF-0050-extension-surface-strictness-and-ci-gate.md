# WF-0050 — Extension Surface Strictness + CI Contract Gate

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-04

## What Changed
- Added strict nested models for remaining snapshot extension surfaces:
  - `compliance_rules`
  - `stage_gating`
  - `hierarchy`
  - `nesting`
- Added WF-0050 contract selectors validating strict unknown-key rejection and valid parse behavior.
- Added explicit CI contract-gate step:
  - `pytest tests/engine/test_review_request_contracts.py -k "wf0048_contract_ or wf0049_contract_"`
- Updated backend CI test lane to:
  - `pytest -m no_db`

## Verification Evidence
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0050_contract_ or wf0049_contract_ or wf0048_contract_"` -> pass
- `cd backend && uv run pytest -m no_db` -> pass (`157 passed, 116 deselected`)
- `pre-commit` on touched files -> pass

## Risks
- New strictness may reject legacy payloads that relied on undeclared keys under the newly hardened extension surfaces.
