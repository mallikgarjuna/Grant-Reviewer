# WF-0048 — Agency/Call Variability Policy Contract

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-04

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: strict snapshot contract accepted on happy path
Goal:
Prove one end-to-end contract request succeeds only when `call_config_snapshot` matches strict `ActivatedCallConfigSnapshotV1` with deterministic digest validation.
Slice: tracer-bullet
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR4, FR8, FR9
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
- `backend/app/engine/contracts.py`
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- `ReviewRequestV1.call_config_snapshot` is typed as `ActivatedCallConfigSnapshotV1`, not a loose dict.
- `schema_version` is required and only accepts `"v1"`.
- A valid payload with matching digest reaches validator success deterministically.
TDD Plan:
- RED: Add failing selector `wf0048_contract_tracer_valid_snapshot_digest_ok` in `backend/tests/engine/test_review_request_contracts.py`.
- GREEN: Implement strict request/snapshot model binding and minimal schema+digest success path.
- REFACTOR: Deduplicate snapshot fixture builder for reuse in later tasks.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0048_contract_tracer_valid_snapshot_digest_ok`
Risks (if any): Existing fixtures may rely on loose snapshot dict behavior and require updates.

### [ ] Task 2 — Deterministic malformed-request contract semantics
Goal:
Enforce deterministic `MALFORMED_REVIEW_REQUEST` behavior for unknown/missing/type/value errors with stable JSON Pointer paths and stable sort order.
Slice: contract-failure-semantics
User Stories: US2
PRD Requirements: FR2, FR5, FR6, FR7, FR14
Depends on: 1
Enables: 3, 4
Parallelizable: no
Files to modify:
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- Unknown fields are rejected for top-level request and all snapshot nested models.
- `details.field_errors[]` contains deterministic `{path, kind, message}` entries.
- Field errors are sorted by `path`, then `kind`, then `message`.
- Message templates are stable and not raw validator-native text.
TDD Plan:
- RED: Add failing selectors `wf0048_contract_unknown_field_stable_pointer`, `wf0048_contract_field_error_sort_order`, `wf0048_contract_kind_message_templates`.
- GREEN: Implement deterministic error normalization, `kind` mapping, pointer formatting, and stable message templates.
- REFACTOR: Extract reusable field-error sorter/helper to keep ordering logic centralized.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0048_contract_unknown_field_stable_pointer or wf0048_contract_field_error_sort_order or wf0048_contract_kind_message_templates"`
Risks (if any): Pydantic/native validation detail ordering may vary unless fully normalized in validator.

### [ ] Task 3 — Schema-before-digest precedence with deterministic mismatch failure
Goal:
Lock validation precedence so schema validation runs first and digest mismatch is emitted only after schema success.
Slice: precedence-and-digest
User Stories: US2
PRD Requirements: FR8, FR9, FR11
Depends on: 1, 2
Enables: 4
Parallelizable: no
Files to modify:
- `backend/app/engine/review_request_validator.py`
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- Requests with schema violations + wrong digest return only `MALFORMED_REVIEW_REQUEST`.
- Requests that pass schema but fail digest return `CALL_CONFIG_DIGEST_MISMATCH` deterministically.
- No nondeterministic branch in failure code selection for the same payload.
TDD Plan:
- RED: Add failing selectors `wf0048_contract_schema_precedes_digest` and `wf0048_contract_digest_mismatch_post_schema`.
- GREEN: Enforce ordered validation flow and deterministic mismatch response contract.
- REFACTOR: Consolidate digest-check invocation point to a single post-schema path.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0048_contract_schema_precedes_digest or wf0048_contract_digest_mismatch_post_schema"`
Risks (if any): Existing validator call sites may assume digest check can occur before full schema normalization.

### [ ] Task 4 — Deterministic replay contract for success serialization
Goal:
Prove deterministic contract behavior for success path and guard against call-identity branching regressions within this scope.
Slice: deterministic-replay-proof
User Stories: US1, US3
PRD Requirements: FR10, FR12
Depends on: 2, 3
Enables: none
Parallelizable: no
Files to modify:
- `backend/tests/engine/test_review_request_contracts.py`
Acceptance Criteria:
- Identical validated payload replay yields byte-identical canonical JSON from `PipelineResult.to_dict()`.
- Contract test coverage includes no call-identity branching assumption in request-boundary behavior.
TDD Plan:
- RED: Add failing selectors `wf0048_contract_replay_byte_stable_success` and `wf0048_contract_snapshot_driven_not_identity_driven`.
- GREEN: Apply minimal implementation updates in `backend/app/engine/review_request_validator.py` only if replay/branching assertions fail.
- REFACTOR: Normalize shared canonical JSON assertion helper for deterministic comparisons.
Verification Steps:
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "wf0048_contract_replay_byte_stable_success or wf0048_contract_snapshot_driven_not_identity_driven"`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0048_contract_replay_byte_stable_success && uv run pytest tests/engine/test_review_request_contracts.py -k wf0048_contract_replay_byte_stable_success`
- `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k wf0048_contract_`
Risks (if any): Existing success payload may include unstable fields requiring explicit exclusion from contract assertions.

## Changelog

- v0.1 (2026-03-04): Initial task breakdown from PRD
- v0.2 (2026-03-04): Applied Part B review edits (tightened deterministic replay verification command; clarified minimal GREEN touchpoint); marked Ready for Implementation
