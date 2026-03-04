# WF-0048 — Agency/Call Variability Policy Contract

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-04

## Executive Summary
Phase 3 implemented a strict, deterministic engine request-boundary contract for call variability.
`ReviewRequestV1.call_config_snapshot` is now a strict typed `ActivatedCallConfigSnapshotV1` model with schema-first validation, stable malformed-request field errors, and deterministic digest-precedence behavior.

## What Changed
- Introduced strict snapshot/request contracts in `backend/app/engine/contracts.py`.
- Reworked validator flow in `backend/app/engine/review_request_validator.py` to enforce:
  - schema validation before digest check,
  - deterministic `MALFORMED_REVIEW_REQUEST` field-error normalization,
  - stable digest mismatch behavior (`CALL_CONFIG_DIGEST_MISMATCH`) only post-schema.
- Added WF-0048 contract suite in `backend/tests/engine/test_review_request_contracts.py` with deterministic selectors for:
  - strict happy-path acceptance,
  - unknown/missing/type/value malformed semantics,
  - schema-before-digest precedence,
  - replay byte-stability,
  - no call-identity branching at request boundary.
- Aligned existing validator/pipeline/error/stress tests to strict `schema_version: "v1"` snapshot shape.

## Part B Adversarial Findings and Resolutions
- Blocking finding: `expectations` was accidentally optional in strict snapshot model.
  - Fix: made `expectations` required.
- Blocking finding: legacy `required` expectation semantics were dropped, causing severity regressions.
  - Fix: restored `required: bool = False` in `ActivatedExpectationV1` and added WF-0048 contract test proving `required: true` drives `ERROR` severity.
- Blocking finding: digest mismatches caused by default-field normalization drift.
  - Fix: digest now canonicalizes schema-validated snapshot projection with `exclude_unset=True` to preserve producer intent while keeping deterministic behavior.

## Verification Evidence
- Focused WF-0048 contract suite:
  - `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -q`
  - Result: `10 passed`
- Stress/legacy compatibility checks:
  - `cd backend && uv run pytest tests/test_review_engine_stress_matrix.py -q`
  - Result: `3 passed`
- Full no-DB backend verification:
  - `cd backend && uv run pytest -m no_db`
  - Result: `135 passed, 116 deselected`
- Repository gate:
  - `pre-commit run --all-files`
  - Result: passed

## Remainder Risks
- Optional extension-point sub-surfaces (`stage_gating`, `hierarchy`, `nesting`, etc.) remain coarse typed containers; deeper strict nested schemas for those sub-surfaces are deferred and should be addressed in a follow-up WF if strict nested invariants become required.

## Next Steps
- User-gated: `ship it` for push/PR/merge.
- Start next workflow for v1 extension-surface schema hardening if needed.
