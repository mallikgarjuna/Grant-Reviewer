# WF-0052 — Producer Compatibility Stress (Real Snapshots)

Artifact: task
Version: v0.4
Status: Completed
Last Updated: 2026-03-04

## Task Breakdown

### [x] Task 1 — Real snapshot matrix coverage
Files:
- `backend/tests/fixtures/wf_0052_real_snapshot_compat_matrix.yaml`
- `backend/tests/engine/test_review_request_contracts.py`
- `docs/walkthroughs/walkthrough-WF-0052-producer-compatibility-stress-real-snapshots.md`
Verification:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0052_contract_compat_`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -m contract_gate`

### [x] Task 2 — Digest determinism on real snapshot classes
Files:
- `backend/tests/engine/test_review_request_contracts.py`
- `backend/app/engine/review_request_validator.py`
- `docs/walkthroughs/walkthrough-WF-0052-producer-compatibility-stress-real-snapshots.md`
Verification:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0052_contract_digest_ or wf0052_contract_compat_omitted_optional_default_equivalence_real_snapshot"`
- `cd backend && uv run pytest -m no_db`

### [x] Task 3 — CI contract-gate inclusion for WF-0052 selectors
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

## Changelog
- v0.1 (2026-03-04): Initial task artifact.
- v0.2 (2026-03-04): Completed Task 1 with real-snapshot matrix fixture, deterministic WF-0052 contract compatibility tests, and walkthrough evidence.
- v0.3 (2026-03-04): Completed Task 2 with real-snapshot digest determinism tests and walkthrough evidence.
- v0.4 (2026-03-04): Completed Task 3 with strict-marker CI contract gate and verification evidence.
