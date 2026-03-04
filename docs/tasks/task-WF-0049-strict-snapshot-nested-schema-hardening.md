# WF-0049 — Strict Snapshot Nested Schema Hardening

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: nested unknown-field rejection with schema-first precedence
Goal:
Prove one end-to-end request-boundary path rejects undeclared nested snapshot keys deterministically and suppresses digest mismatch when schema is invalid.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR2, FR4, FR6
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- A payload containing an unknown key under an in-scope nested surface fails with `MALFORMED_REVIEW_REQUEST`.
- Returned `details.field_errors[]` includes a nested JSON Pointer path for the offending field.
- When payload is schema-invalid and digest is wrong, response remains schema failure only (no digest mismatch emission).
TDD Plan:
- RED: Add failing selectors `wf0049_contract_tracer_nested_unknown_rejected` and `wf0049_contract_tracer_schema_precedes_digest` in `backend/tests/engine/test_review_request_contracts.py`.
- GREEN: Implement minimal validator changes to enforce deterministic nested unknown-field failure and schema-before-digest precedence.
- REFACTOR: Extract shared malformed-request assertion helper for nested-path checks.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0049_contract_tracer_nested_unknown_rejected or wf0049_contract_tracer_schema_precedes_digest"`
Risks (if any): Existing fixtures may assume permissive nested payload handling.

### [ ] Task 2 — Strict nested models for `evaluation_criteria` and `evaluation_elements`
Goal:
Replace loose nested dict/list surfaces for criteria/elements with explicit strict models at snapshot boundary typing.
Slice: nested-modeling-core
User Stories: US1
PRD Requirements: FR1, FR2, FR3
Depends on: 1
Enables: 4
Parallelizable: no
Files to modify:
- `backend/app/engine/contracts.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- `evaluation_criteria` and `evaluation_elements` no longer rely on `dict[str, object]` or `list[dict[str, object]]` in active snapshot contract paths.
- Unknown nested fields for these surfaces are rejected by strict model config.
- Existing valid fixture payload class for these surfaces still parses successfully.
TDD Plan:
- RED: Add failing selectors `wf0049_contract_criteria_surface_strict` and `wf0049_contract_elements_surface_strict`.
- GREEN: Add explicit nested Pydantic models and wire them into `ActivatedCallConfigSnapshotV1` for active surfaces.
- REFACTOR: Consolidate shared strict model base config for nested surfaces.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0049_contract_criteria_surface_strict or wf0049_contract_elements_surface_strict"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0049_contract_tracer_`
Risks (if any): Producer fixtures with legacy extra keys may begin failing and require explicit compatibility expectations.

### [ ] Task 3 — Strict nested models for `reviewer_policy` and `prompt_knobs`
Goal:
Apply the same strict nested boundary hardening to reviewer policy and prompt knob surfaces, keeping scope to active request schema only.
Slice: nested-modeling-policy-knobs
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3
Depends on: 1
Enables: 4
Parallelizable: no
Files to modify:
- `backend/app/engine/contracts.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- `reviewer_policy` and `prompt_knobs` are represented by explicit strict nested models.
- Unknown nested keys/types for these surfaces produce deterministic malformed-request failures.
- No permissive catch-all extension dict is introduced.
TDD Plan:
- RED: Add failing selectors `wf0049_contract_reviewer_policy_surface_strict` and `wf0049_contract_prompt_knobs_surface_strict`.
- GREEN: Introduce strict nested models and bind them into snapshot v1 contract.
- REFACTOR: Reuse common nested strictness helpers/constants to avoid duplicate model config.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0049_contract_reviewer_policy_surface_strict or wf0049_contract_prompt_knobs_surface_strict"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0049_contract_tracer_`
Risks (if any): Prompt knob defaults may require careful optional typing to avoid accidental required-field regressions.

### [ ] Task 4 — Deterministic nested field error contract normalization
Goal:
Normalize nested validation errors into stable `{path, kind, message}` entries sorted deterministically and aligned to frozen kind enum.
Slice: error-contract-stability
User Stories: US2
PRD Requirements: FR4, FR5, FR5a
Depends on: 2, 3
Enables: 5
Parallelizable: no
Files to modify:
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- Nested field errors are emitted with stable JSON Pointer `path`, stable `kind`, and stable message template wording.
- `kind` values are limited to `unknown_field`, `missing_field`, `type_error`, `value_error`.
- Error list ordering is deterministic by `path`, then `kind`, then `message`.
TDD Plan:
- RED: Add failing selectors `wf0049_contract_nested_field_error_sort`, `wf0049_contract_kind_enum_frozen`, and `wf0049_contract_message_template_stable`.
- GREEN: Implement deterministic nested error normalization/sorting and explicit `kind` mapping.
- REFACTOR: Extract dedicated error-normalization helper to isolate validator-library differences.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0049_contract_nested_field_error_sort or wf0049_contract_kind_enum_frozen or wf0049_contract_message_template_stable"`
Risks (if any): Raw validator error structures may change across dependency upgrades if not fully normalized.

### [ ] Task 5 — Digest canonicalization determinism for omitted/default nested fields
Goal:
Ensure digest computation uses schema-validated projection and remains stable for omitted optional nested defaults versus explicit default equivalents.
Slice: digest-determinism
User Stories: US3
PRD Requirements: FR7, FR8
Depends on: 4
Enables: 6
Parallelizable: no
Files to modify:
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- Digest input is derived only from schema-validated projection.
- Equivalent semantic payloads (omitted optional nested defaults vs explicit defaults) produce stable digest behavior.
- Digest mismatch is checked only after schema success (regression guard maintained).
TDD Plan:
- RED: Add failing selectors `wf0049_contract_digest_omitted_default_equivalence` and `wf0049_contract_digest_projection_from_validated_schema`.
- GREEN: Implement minimal canonicalization updates for deterministic nested default handling.
- REFACTOR: Centralize canonical projection builder used by digest logic.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0049_contract_digest_omitted_default_equivalence or wf0049_contract_digest_projection_from_validated_schema"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0049_contract_tracer_schema_precedes_digest`
Risks (if any): Canonicalization changes can alter historical digest fixtures if equivalence rules are not tightly bounded.

### [ ] Task 6 — Producer compatibility matrix and fail-closed rollout gate
Goal:
Add fixture-backed compatibility evidence for required payload classes and enforce fail-closed readiness expectations for strict nested hardening.
Slice: producer-compatibility-gate
User Stories: US4
PRD Requirements: FR9, FR10, FR10a
Depends on: 5
Enables: none
Parallelizable: no
Files to modify:
- `backend/tests/engine/test_review_request_contracts.py`
- `backend/tests/fixtures/wf_0049_nested_schema_compat_matrix.yaml`
- `docs/walkthroughs/walkthrough-WF-0049-strict-snapshot-nested-schema-hardening.md`
Acceptance Criteria:
- Compatibility matrix includes required classes: `happy_valid_payload`, `legacy_extra_nested_key`, `nested_type_mismatch`, `omitted_optional_default_equivalence`.
- Matrix assertions are deterministic and CI-selectable for WF-0049 selectors.
- Walkthrough documents matrix expectations and fail-closed gate rationale for release readiness.
TDD Plan:
- RED: Add failing matrix-driven selector coverage under `wf0049_contract_compat_*` in `test_review_request_contracts.py`.
- GREEN: Add minimal fixture matrix + test wiring for required class expectations.
- REFACTOR: Normalize matrix loader/helper to keep fixture schema stable.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0049_contract_compat_`
- `cd backend && uv run pytest -k wf0049_contract_`
- `rg -n "wf0049_contract_compat_|fail-closed" docs/walkthroughs/walkthrough-WF-0049-strict-snapshot-nested-schema-hardening.md`
Risks (if any): Matrix fixture schema drift can hide rollout blockers unless selector coverage remains explicit.

## Changelog

- v0.1 (2026-03-04): Initial task breakdown from PRD
