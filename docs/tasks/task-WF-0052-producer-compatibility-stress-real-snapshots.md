# WF-0052 — Producer Compatibility Stress (Real Snapshots)

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## Task Breakdown

### [ ] Task 1 — Real snapshot matrix coverage
Files:
- `backend/tests/fixtures/wf_0052_real_snapshot_compat_matrix.yaml`
- `backend/tests/engine/test_review_request_contracts.py`
- `docs/walkthroughs/walkthrough-WF-0052-producer-compatibility-stress-real-snapshots.md`
Verification:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0052_contract_compat_`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -m contract_gate`

### [ ] Task 2 — Digest determinism on real snapshot classes
Files:
- `backend/tests/engine/test_review_request_contracts.py`
- `backend/app/engine/review_request_validator.py`
- `docs/walkthroughs/walkthrough-WF-0052-producer-compatibility-stress-real-snapshots.md`
Verification:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0052_contract_digest_ or wf0052_contract_compat_omitted_optional_default_equivalence_real_snapshot"`
- `cd backend && uv run pytest -m no_db`

### [ ] Task 3 — CI contract-gate inclusion for WF-0052 selectors
Files:
- `backend/tests/engine/test_review_request_contracts.py`
- `.github/workflows/ci.yml`
- `docs/walkthroughs/walkthrough-WF-0052-producer-compatibility-stress-real-snapshots.md`
Verification:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -m contract_gate`
- `cd backend && uv run pytest -m no_db`

## Notes
- Keep slices atomic and bounded to request-boundary contract behavior.
- Do not broaden scope into runtime pipeline behavior.
