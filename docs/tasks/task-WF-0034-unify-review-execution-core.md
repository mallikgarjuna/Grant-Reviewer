# WF-0034 — Unify review service execution core

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-26

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: structured path executes through shared core

Goal: Prove one end-to-end structured happy path can run via a new shared execution seam without changing endpoint contracts.
Slice: tracer-bullet
User Stories: US1, US2, US4
PRD Requirements: FR1, FR3, FR4, FR6, FR11
Files to modify:
- `backend/app/services/review_execution_core.py`
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_structured_reviewer_service.py`
Acceptance Criteria:
- New shared core exposes a single-node execution entry used by structured service for assessable nodes.
- Structured service continues returning existing `Review`/`ReviewCard` outcomes for happy path.
- No endpoint DTO or status semantics change.
TDD Plan:
- RED: add a failing structured-service test that asserts shared-core execution is invoked and cards persist with unchanged shape.
- GREEN: introduce `review_execution_core.py` and route structured assessable-node execution through it.
- REFACTOR: extract adapter mapping helpers in structured service (`skip` if no duplication appears).
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_structured_reviewer_service.py -k "test_structured_shared_core_tracer_happy_path"`
Risks (if any):
- Initial seam may accidentally absorb structured-only persistence responsibilities.

### [ ] Task 2 — Structured failure-path parity via shared core

Goal: Preserve structured timeout/LLM/validation failure semantics while using shared-core execution.
Slice: structured-failure-parity
User Stories: US2, US3, US4
PRD Requirements: FR3, FR6, FR8, FR9, FR10, FR11
Files to modify:
- `backend/app/services/review_execution_core.py`
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_structured_reviewer_service.py`
Acceptance Criteria:
- Timeout, LLM client failure, and parse/validation failures keep existing structured status/summary behavior.
- Structured service still returns already-persisted deterministic cards when a later node fails.
TDD Plan:
- RED: add failing structured-service tests for timeout and validation failure summaries/status after shared-core wiring.
- GREEN: map shared-core failure classifications back to existing structured error handling text and state transitions.
- REFACTOR: consolidate failure mapping into one adapter function.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_structured_reviewer_service.py -k "test_structured_shared_core_timeout_parity or test_structured_shared_core_validation_failure_parity or test_structured_shared_core_llm_failure_parity"`
Risks (if any):
- Failure classification drift could change externally observable summaries.

### [ ] Task 3 — Preserve deterministic structured NOT_ASSESSABLE semantics

Goal: Keep deterministic `NOT_ASSESSABLE` card generation endpoint-owned while shared core handles only assessable execution.
Slice: structured-not-assessable
User Stories: US2, US3
PRD Requirements: FR4, FR6, FR8, FR9
Files to modify:
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_structured_reviewer_service.py`
Acceptance Criteria:
- Missing cross-node context still creates deterministic `NOT_ASSESSABLE` cards with existing reason text and status.
- Shared core is not called for expectations classified as not assessable.
TDD Plan:
- RED: add failing test asserting not-assessable expectations persist deterministic cards and bypass shared-core call path.
- GREEN: enforce adapter boundary so shared core only receives assessable expectations.
- REFACTOR: simplify partition/execution loop for readability.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_structured_reviewer_service.py -k "test_structured_not_assessable_cards_remain_deterministic"`
Risks (if any):
- Boundary confusion may leak not-assessable logic into shared core.

### [ ] Task 4 — Single-node happy-path migration to shared core

Goal: Route single-node review execution through shared core while preserving existing single-node persistence behavior.
Slice: single-node-happy-path
User Stories: US1, US2, US4
PRD Requirements: FR1, FR3, FR4, FR5, FR8, FR11
Files to modify:
- `backend/app/services/review_execution_core.py`
- `backend/app/services/reviewer_service.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- `/reviews` continues to complete successfully with unchanged response payload and status.
- Single-node snippet/review persistence remains adapter-owned and unchanged.
TDD Plan:
- RED: add failing API parity test covering `/reviews` happy path after shared-core delegation.
- GREEN: wire `ReviewerService` to call shared core and map results back to current persistence flow.
- REFACTOR: isolate adapter-only persistence write block for clarity.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_api.py -k "test_create_review_shared_core_happy_path_parity"`
Risks (if any):
- Adapter migration may inadvertently change check ordering before execution.

### [ ] Task 5 — Single-node failure and idempotency parity lock

Goal: Maintain `/reviews` timeout/error/idempotency semantics after shared-core migration.
Slice: single-node-parity-guards
User Stories: US2, US3
PRD Requirements: FR5, FR7, FR8, FR9, FR10
Files to modify:
- `backend/app/services/reviewer_service.py`
- `backend/tests/test_api.py`
- `backend/tests/test_reviewer_policy.py`
Acceptance Criteria:
- Existing idempotency mismatch behavior and exposed error semantics for `/reviews` remain unchanged.
- Timeout and policy-blocking outcomes remain baseline-compatible.
TDD Plan:
- RED: add failing tests for idempotency mismatch and timeout/policy-blocking responses in single-node flow.
- GREEN: restore parity by adjusting adapter-side mapping/order without changing API contract.
- REFACTOR: remove duplicated failure summary formatting code.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_api.py -k "test_create_review_idempotency_mismatch_parity or test_create_review_timeout_parity"`
- `cd backend && PYTHONPATH=. uv run pytest tests/test_reviewer_policy.py -k "test_policy_blocking_violation_classification"`
Risks (if any):
- Route/service validation ordering can regress and change returned error priority.

### [ ] Task 6 — Shared-core service tests with deterministic stubs

Goal: Add focused shared-core seam tests for policy injection, parse/validation, and post-check outcomes.
Slice: core-seam-tests
User Stories: US1, US3
PRD Requirements: FR2, FR3, FR4, FR10
Files to modify:
- `backend/app/services/review_execution_core.py`
- `backend/tests/test_review_execution_core.py`
Acceptance Criteria:
- Shared core has deterministic tests for success, timeout/failure classification, and blocking/warning policy post-checks.
- Tests stub only external LLM boundary and keep business logic real.
TDD Plan:
- RED: create failing `test_review_execution_core.py` cases for success/failure/policy classifications.
- GREEN: implement minimal typed execution result and behavior required by tests.
- REFACTOR: tighten internal helper names and type hints.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_review_execution_core.py -k "test_core_success_result or test_core_timeout_classification or test_core_policy_postcheck_classification"`
Risks (if any):
- Over-mocking could hide regressions that adapters depend on.

### [ ] Task 7 — Introduce no-op telemetry seam at execution boundaries

Goal: Add standardized, non-invasive telemetry hooks around shared-core execution.
Slice: telemetry-seam
User Stories: US1, US3
PRD Requirements: FR12
Files to modify:
- `backend/app/services/review_execution_core.py`
- `backend/tests/test_review_execution_core.py`
- `backend/tests/test_structured_reviewer_service.py`
Acceptance Criteria:
- Shared core emits start/completion and failure-category hook calls through a no-op-safe interface.
- Hook behavior does not alter endpoint-visible outputs.
TDD Plan:
- RED: add failing tests asserting telemetry hook invocation counts/labels for success and failure flows.
- GREEN: implement no-op telemetry interface and invoke it at execution boundaries.
- REFACTOR: centralize telemetry payload construction.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_review_execution_core.py -k "test_core_emits_telemetry_start_complete or test_core_emits_telemetry_failure_category"`
- `cd backend && PYTHONPATH=. uv run pytest tests/test_structured_reviewer_service.py -k "test_structured_path_telemetry_is_non_invasive"`
Risks (if any):
- Hook placement could accidentally mutate control flow if not strictly side-effect free.

### [ ] Task 8 — Endpoint contract parity guard for both create endpoints

Goal: Add explicit parity regression checks proving external contracts remain stable after both migrations.
Slice: endpoint-parity
User Stories: US2, US3, US4
PRD Requirements: FR5, FR6, FR7, FR8, FR9, FR11
Files to modify:
- `backend/tests/test_api.py`
- `backend/tests/test_structured_reviewer_service.py`
Acceptance Criteria:
- Regression tests explicitly assert unchanged request/response semantics for `/reviews` and `/api/structured-review`.
- Tests cover incremental migration invariant: changing one adapter path does not regress the other endpoint behavior.
TDD Plan:
- RED: add failing parity assertions for both endpoints around response shape, status codes, and idempotency mismatch behavior.
- GREEN: keep this task test-only; if parity fails, update the owning prior migration task instead of adding new behavior here.
- REFACTOR: consolidate duplicated parity fixtures/helpers.
Verification Steps:
- `cd backend && PYTHONPATH=. uv run pytest tests/test_api.py -k "test_create_review_contract_parity or test_structured_review_contract_parity"`
- `cd backend && PYTHONPATH=. uv run pytest tests/test_structured_reviewer_service.py -k "test_incremental_migration_does_not_cross_regress"`
Risks (if any):
- Broad parity tests can become brittle if fixture setup is not isolated.

## Changelog

- v0.1 (2026-02-26): Initial task breakdown from PRD
- v0.2 (2026-02-26): Applied Phase 2.2 review tightenings (precise verification commands, clarified test-only parity task) and marked Ready for Implementation
