# WF-0052 — Producer Compatibility Stress (Real Snapshots)

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-04

## Task 1 Implementation
- Added real-snapshot compatibility matrix fixture:
  - `backend/tests/fixtures/wf_0052_real_snapshot_compat_matrix.yaml`
- Added deterministic WF-0052 contract compatibility tests:
  - `wf0052_contract_compat_happy_valid_payload_real_snapshot`
  - `wf0052_contract_compat_legacy_extra_nested_key_real_snapshot`
  - `wf0052_contract_compat_nested_type_mismatch_real_snapshot`
  - `wf0052_contract_compat_omitted_optional_default_equivalence_real_snapshot`
- Added grounding assertions per case:
  - each matrix case includes `source_call_path` and `grounding_element_ids`
  - tests verify grounding IDs exist in the source call `evaluation_criteria/evaluation_elements` before validating request-boundary behavior.

## Verification Evidence
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0052_contract_compat_ -q` -> pass (`4 passed, 31 deselected`)
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -m contract_gate -q` -> pass (`35 passed`)
- `cd backend && uv run ruff check tests/engine/test_review_request_contracts.py` -> pass

## Task 2 Implementation
- Added real-snapshot digest determinism tests:
  - `wf0052_contract_digest_validated_projection_equivalence_real_snapshot`
  - `wf0052_contract_digest_raw_snapshot_mismatch_real_snapshot`
- Proven behavior:
  - canonical digests computed from schema-validated projections are equivalent for omitted-vs-explicit defaults.
  - raw snapshot JSON digesting (without schema projection) is rejected deterministically as `CALL_CONFIG_DIGEST_MISMATCH`.

## Task 3 Implementation
- Hardened CI marker gate command:
  - `pytest tests/engine/test_review_request_contracts.py -m contract_gate --strict-markers -q`
- Kept WF-0052 inclusion fail-closed through module-level `contract_gate` marker on contract suites.

## Residual Work
- None for Phase 3 implementation tasks.

## Final Verification Gate (Phase 3.3 C2)
- `uv run pre-commit run --all-files` -> pass
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -m contract_gate --strict-markers -q` -> pass (`37 passed`)
- `cd backend && uv run pytest -m no_db -q` -> pass (`163 passed, 116 deselected`)
