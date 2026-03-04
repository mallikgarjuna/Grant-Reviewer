# WF-0049 — Strict Snapshot Nested Schema Hardening

Artifact: walkthrough
Version: v1.0
Status: Done
Last Updated: 2026-03-04

## Scope Completed

- Request-boundary snapshot v1 now uses explicit strict nested models for:
  - `evaluation_criteria`
  - `evaluation_elements` (both criterion-nested and root surface)
  - `reviewer_policy`
  - `prompt_knobs`
- Unknown nested keys are rejected deterministically as `MALFORMED_REVIEW_REQUEST`.
- Nested error normalization is stable and sorted by `path`, `kind`, `message`.
- `field_errors.kind` behavior is frozen to:
  - `unknown_field`
  - `missing_field`
  - `type_error`
  - `value_error`
- Digest comparison runs only after schema success and is computed from schema-validated canonical projection.
- Scope guards confirm no call-identity branching and stable pipeline semantics for schema-valid requests.

## Compatibility Matrix Gate

- Added fixture-backed compatibility matrix: `backend/tests/fixtures/wf_0049_nested_schema_compat_matrix.yaml`.
- Required class coverage locked to:
  - `happy_valid_payload`
  - `legacy_extra_nested_key`
  - `nested_type_mismatch`
  - `omitted_optional_default_equivalence`
- CI-selectable selectors:
  - `wf0049_contract_compat_happy_valid_payload`
  - `wf0049_contract_compat_legacy_extra_nested_key`
  - `wf0049_contract_compat_nested_type_mismatch`
  - `wf0049_contract_compat_omitted_optional_default_equivalence`

## Release Readiness Policy

- Rollout gate is fail-closed: missing required matrix classes or unexpected outcomes block release readiness.
- Validation remains request-boundary-only and deterministic (`path`, `kind`, `message`) for malformed cases.

## Verification Evidence

- Baseline preflight before Task 1:
  - `cd backend && uv run pytest -m no_db` -> pass.
- WF task-level selectors executed during implementation:
  - tracer strictness/digest precedence (`wf0049_contract_tracer_*`) -> pass.
  - strict surfaces for criteria/elements/policy/knobs -> pass.
  - nested error normalization selectors -> pass.
  - digest determinism selectors -> pass.
  - compatibility matrix selectors -> pass.
  - scope guard selectors -> pass.
- Final Phase 3 verify gate:
  - `pre-commit run --all-files` -> pass.
  - `cd backend && uv run pytest -m no_db` -> pass (`152 passed, 116 deselected`).

## Adversarial Review Revision

- Part B adversarial pass identified one blocking gap:
  - root `call_config_snapshot.evaluation_elements` remained loose (`list[dict]`) instead of strict nested model.
- Applied Part C1 fix:
  - switched root `evaluation_elements` to strict `ActivatedEvaluationElementV1`.
  - added selector `wf0049_contract_elements_root_surface_strict`.
  - reran targeted selectors and full no-db suite to green.

## Remaining Risks

- Producers that still hash raw snapshot payload bytes (instead of validated canonical projection) will fail digest checks until aligned.
- Future Pydantic error-type taxonomy changes could require updates to error-kind mapping, guarded by WF-0049 kind/message stability selectors.
