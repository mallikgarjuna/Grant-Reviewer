# WF-0045 — Base Review Pipeline v1.0 (call-agnostic core)

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-03

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: deterministic six-stage happy path

Goal:
Prove one end-to-end request executes the locked six stages in order and returns deterministic success envelope + compatibility output.
Slice: tracer-bullet
User Stories: US1, US2, US4
PRD Requirements: FR1, FR2, FR7, FR8, FR13
Depends on: none
Enables: Task 2, Task 3
Parallelizable: no
Files to modify:
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_review_engine_pipeline_v1.py`
- `backend/tests/test_engine_telemetry.py`
Acceptance Criteria:
- Pipeline run includes explicit stage transition evidence for all six core stages.
- Success response carries deterministic envelope fields (`request_id`, `pipeline_status`, `failure_code`, `diagnostics`, `compatibility_output`).
- Running the same payload twice yields byte-identical serialized results.
TDD Plan: RED: add `wf0045_contract_tracer_happy_path` failing assertions in `test_review_engine_pipeline_v1.py`; GREEN: implement minimal stage transition and response-envelope wiring in `pipeline_v1.py`; REFACTOR: centralize stage name constants used by pipeline + telemetry tests.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k wf0045_contract_tracer_happy_path`
- `cd backend && uv run pytest tests/test_engine_telemetry.py -k wf0045_contract_tracer_happy_path`
Risks (if any):
- Existing pipeline payload format may require compatibility-preserving adapter fields.

### [x] Task 2 — Failure contract taxonomy and stable code mapping

Goal:
Introduce explicit contract vs execution failure classes with stable WF-0045 codes and deterministic response mapping.
Slice: failure-contract
User Stories: US2, US4
PRD Requirements: FR3, FR4, FR11, FR13
Depends on: Task 1
Enables: Task 8
Parallelizable: no
Files to modify:
- `backend/app/engine/errors.py`
- `backend/app/engine/contracts.py`
- `backend/tests/test_review_engine_error_contracts.py`
Acceptance Criteria:
- Error contract includes class-safe mapping for `contract-failure` and `execution-failure`.
- Response envelope uses only stable mapped failure codes (`CONTRACT_FAILURE`, `EXECUTION_FAILURE`).
- Unknown error paths map deterministically to execution-failure classification.
TDD Plan: RED: add failing selector `wf0045_contract_failure_code_mapping` in `test_review_engine_error_contracts.py`; GREEN: extend error/code enums + contract fields; REFACTOR: deduplicate error mapping helper usage.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_engine_error_contracts.py -k wf0045_contract_failure_code_mapping`
Risks (if any):
- Legacy engine error codes may need compatibility aliasing to avoid regressions.

### [x] Task 3 — Structural validation and compliance gate invariants

Goal:
Enforce stage entry/exit invariants for structural validation and compliance gate before expectation evaluation.
Slice: precondition-gates
User Stories: US1, US2
PRD Requirements: FR2, FR3, FR4, FR12
Depends on: Task 1
Enables: Task 4
Parallelizable: no
Files to modify:
- `backend/app/engine/review_request_validator.py`
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_review_request_validator.py`
Acceptance Criteria:
- Invalid request envelope/call-config boundary violations terminate as `contract-failure`.
- Compliance gate produces deterministic check outcomes and blocks downstream stages on contract-invalid input.
- Validator errors remain deterministic for same malformed payload.
TDD Plan: RED: add failing selectors `wf0045_contract_structural_gate_rejects_invalid` and `wf0045_contract_compliance_gate_blocks_downstream`; GREEN: implement invariant checks + stage short-circuiting; REFACTOR: normalize validator error construction helpers.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_request_validator.py -k wf0045_contract_`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k wf0045_contract_compliance_gate_blocks_downstream`
Risks (if any):
- Tightened validation may expose previously tolerated malformed fixtures.

### [x] Task 4 — Expectation-level evaluation contract (assessed/not-assessable)

Goal:
Produce deterministic per-expectation outcomes with explicit assessed vs not-assessable semantics from call-config expectations.
Slice: expectation-evaluation
User Stories: US1, US4
PRD Requirements: FR2, FR5, FR7, FR13
Depends on: Task 3
Enables: Task 5, Task 7
Parallelizable: no
Files to modify:
- `backend/app/engine/findings/evaluator.py`
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_finding_evaluator.py`
Acceptance Criteria:
- Each active expectation yields exactly one deterministic result classification.
- Missing context cases emit `NOT_ASSESSABLE` with explicit reason text.
- Evaluation remains call-agnostic and driven only by call-config snapshot content.
TDD Plan: RED: add failing selectors `wf0045_contract_expectation_assessed` and `wf0045_contract_expectation_not_assessable`; GREEN: implement expectation outcome mapping in evaluator + pipeline integration; REFACTOR: extract expectation iteration helper for deterministic ordering.
Verification Steps:
- `cd backend && uv run pytest tests/test_finding_evaluator.py -k wf0045_contract_expectation_`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k wf0045_contract_expectation_not_assessable`
Risks (if any):
- Existing evaluator assumptions may conflate missing content with not-assessable context.

### [x] Task 5 — Cross-node alignment stage with explicit dependency-context handling

Goal:
Add deterministic cross-node alignment stage outputs, including explicit not-assessable reasons when dependency context is absent.
Slice: cross-node-alignment
User Stories: US1, US4
PRD Requirements: FR1, FR2, FR7
Depends on: Task 4
Enables: Task 6, Task 8
Parallelizable: no
Files to modify:
- `backend/app/engine/observations/extractor.py`
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_observation_extractor.py`
Acceptance Criteria:
- Alignment stage consumes declared dependency context or explicitly records absence.
- Stage output is deterministic for identical payloads.
- Missing dependency context never silently drops alignment evaluation.
TDD Plan: RED: add failing selectors `wf0045_contract_alignment_with_context` and `wf0045_contract_alignment_not_assessable`; GREEN: implement alignment-stage extraction and pipeline wiring; REFACTOR: isolate alignment reason constants.
Verification Steps:
- `cd backend && uv run pytest tests/test_observation_extractor.py -k wf0045_contract_alignment_`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k wf0045_contract_alignment_not_assessable`
Risks (if any):
- Context sourcing format differences between fixtures may require adapter normalization.

### [x] Task 6 — Risk audit deterministic taxonomy pass

Goal:
Derive risk findings deterministically from expectation/alignment outputs using a fixed taxonomy.
Slice: risk-audit
User Stories: US2, US4
PRD Requirements: FR1, FR2, FR7
Depends on: Task 5
Enables: Task 8
Parallelizable: no
Files to modify:
- `backend/app/engine/findings/check_catalog.py`
- `backend/app/engine/findings/aggregator.py`
- `backend/tests/test_finding_aggregation.py`
Acceptance Criteria:
- Risk audit emits deterministic risk findings for same inputs.
- Taxonomy categories are stable and do not vary by call identity.
- Upstream not-assessable signals are represented without mutation.
TDD Plan: RED: add failing selector `wf0045_contract_risk_taxonomy_deterministic`; GREEN: implement taxonomy-driven risk derivation + aggregation integration; REFACTOR: consolidate severity precedence constants.
Verification Steps:
- `cd backend && uv run pytest tests/test_finding_aggregation.py -k wf0045_contract_risk_taxonomy_deterministic`
Risks (if any):
- Aggregator sort precedence changes can alter downstream card ordering.

### [ ] Task 7 — Call-agnostic governance guardrail tests

Goal:
Prevent core stage branching by call/funder/program and keep optional modules out of base pipeline semantics.
Slice: governance-guardrails
User Stories: US1, US3
PRD Requirements: FR5, FR6, FR9, FR10, FR12
Depends on: Task 4
Enables: Task 9
Parallelizable: no
Files to modify:
- `backend/app/services/review_execution_core.py`
- `backend/tests/test_review_execution_core.py`
- `backend/tests/test_rollout_replay.py`
Acceptance Criteria:
- Core execution path does not branch stage behavior on call identity.
- Optional extension flags do not alter base stage ordering or pass/fail semantics.
- Refactor touchpoints in this area are tied to explicit stage invariants in test naming/comments.
TDD Plan: RED: add failing selectors `wf0045_contract_call_agnostic_core` and `wf0045_contract_optional_extension_noop`; GREEN: apply minimal guardrails in execution core path; REFACTOR: remove duplicate branch-condition helpers.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_execution_core.py -k wf0045_contract_call_agnostic_core`
- `cd backend && uv run pytest tests/test_rollout_replay.py -k wf0045_contract_optional_extension_noop`
Risks (if any):
- Existing rollout fixtures may encode implicit call-specific assumptions.

### [ ] Task 8 — Output aggregation and compatibility-safe failure propagation

Goal:
Finalize aggregation contract so stable ordered diagnostics and compatibility output always preserve upstream failure class.
Slice: aggregation-compat
User Stories: US2, US4
PRD Requirements: FR4, FR7, FR8, FR11, FR13
Depends on: Task 2, Task 5, Task 6
Enables: Task 9
Parallelizable: no
Files to modify:
- `backend/app/engine/compat/review_card_mapper.py`
- `backend/app/engine/pipeline_v1.py`
- `backend/tests/test_review_card_mapper.py`
Acceptance Criteria:
- Diagnostic ordering remains deterministic for identical inputs.
- Compatibility output preserves failure class mapping without silent mutation.
- Contract-invalid and execution-failed paths emit distinct, stable final envelope states.
- Pipeline aggregation path includes risk-audit outcomes without call-specific branching.
TDD Plan: RED: add failing selectors `wf0045_contract_aggregation_failure_passthrough` and `wf0045_contract_diagnostic_ordering_stable`; GREEN: implement failure propagation + ordering guards across pipeline/mapper; REFACTOR: centralize compatibility output shaping.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_card_mapper.py -k wf0045_contract_`
- `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k wf0045_contract_diagnostic_ordering_stable`
Risks (if any):
- Card-mapper hard failures may need adaptation to emit envelope-safe failure payloads.

### [ ] Task 9 — WF-0045 contract matrix fixture and verification bundle

Goal:
Create WF-0045 contract matrix coverage and lock a repeatable verification command set for phase handoff.
Slice: contract-matrix-and-verification
User Stories: US1, US2, US3, US4
PRD Requirements: FR1, FR3, FR5, FR7, FR11, FR12, FR13
Depends on: Task 7, Task 8
Enables: none
Parallelizable: no
Files to modify:
- `backend/tests/fixtures/wf_0045_contract_matrix.yaml`
- `backend/tests/test_review_execution_core.py`
- `docs/walkthroughs/walkthrough-WF-0045-base-review-pipeline-v1-call-agnostic.md`
Acceptance Criteria:
- Matrix includes selectors covering happy path, contract-failure, execution-failure, ordering parity, and call-agnostic guardrails.
- Test harness runs WF-0045 selectors deterministically.
- Walkthrough captures verification commands and expected outcomes for implementation handoff.
TDD Plan: RED: add failing matrix-driven test selectors `wf0045_contract_*`; GREEN: add fixture cases and hook them into execution-core tests; REFACTOR: simplify matrix loader plumbing if duplicated.
Verification Steps:
- `cd backend && uv run pytest tests/test_review_execution_core.py -k wf0045_contract_`
- `cd backend && uv run pytest -k wf0045_contract_`
- `rg -n "wf0045_contract_" docs/walkthroughs/walkthrough-WF-0045-base-review-pipeline-v1-call-agnostic.md`
Risks (if any):
- New fixture selectors can collide with prior WF selector namespaces if naming is inconsistent.

## Changelog

- v0.1 (2026-03-03): Initial task breakdown from PRD.
- v0.2 (2026-03-03): Applied Phase 2.2 review refinements (risk-stage pipeline glue path, sequential metadata clarity, explicit walkthrough verification command); marked Ready for Implementation.
- v0.3 (2026-03-03): Adversarial Part B/C pass: tightened WF-0045 deterministic verification selectors, restored Task 6 atomicity (<=3 files), and clarified Task 8 risk-audit aggregation coverage.
