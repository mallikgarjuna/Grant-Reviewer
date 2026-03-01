# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-01

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: prove v1-only routing contract

Goal:
- Prove end-to-end that `POST /api/structured-review` can run in enforced v1-only mode without API contract drift.
Slice: tracer-bullet-v1-only
User Stories: US1, US3
PRD Requirements: FR3, FR6
Depends on: none
Enables: Task 2, Task 3
Parallelizable: no
Files to modify:
- `backend/main.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Route-level selection for structured review is v1-only in retirement mode.
- Existing request/response contract behavior remains unchanged for covered test cases.
TDD Plan:
- RED: add/adjust failing API test in `backend/tests/test_api.py` asserting v1-only route selection and unchanged contract behavior.
- GREEN: apply minimal routing change in `backend/main.py` to satisfy the test.
- REFACTOR: remove duplicated route-selection condition branches.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t1.db uv run pytest -q tests/test_api.py -k "structured_review and (pipeline_v1 or v1_only)"`
Risks (if any):
- Hidden runtime assumptions may still rely on legacy path in uncovered payload shapes.

### [ ] Task 2 — Lock API invariant coverage for retirement

Goal:
- Ensure retirement keeps idempotency, validation ordering, and error semantics stable.
Slice: contract-invariants
User Stories: US2, US3
PRD Requirements: FR8
Depends on: Task 1
Enables: Task 4
Parallelizable: no
Files to modify:
- `backend/tests/test_api.py`
- `backend/tests/test_review_engine_pipeline_v1.py`
- `backend/app/services/structured_reviewer_service.py`
Acceptance Criteria:
- Automated tests explicitly cover invariant behaviors listed in PRD Section 5.
- Any required code changes are minimal and preserve current API semantics.
TDD Plan:
- RED: add failing invariant tests for digest mismatch, expectation resolution errors, timeout classification, and validation ordering.
- GREEN: patch service behavior only where tests expose drift.
- REFACTOR: deduplicate invariant test fixtures and helper setup.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t2.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py -k "idempotency or digest or expectation or timeout or validation"`
Risks (if any):
- Overly strict assertions may accidentally lock non-contract internals.

### [ ] Task 3 — Codify deletion-gate health thresholds in tooling

Goal:
- Encode PRD gate defaults (24h staging, 7d prod, min samples per call) in rollout-health evaluation output.
Slice: gate-tooling
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR10
Depends on: Task 1
Enables: Task 5
Parallelizable: no
Files to modify:
- `backend/scripts/evaluate_rollout_health.py`
- `backend/tests/test_rollout_health.py`
- `docs/walkthroughs/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
Acceptance Criteria:
- Health evaluator reports explicit pass/fail against retirement gate defaults.
- Walkthrough checklist references evaluator outputs as deletion precondition evidence.
TDD Plan:
- RED: add failing tests in `backend/tests/test_rollout_health.py` for threshold/sample-size gate evaluation.
- GREEN: implement minimal evaluator updates in `backend/scripts/evaluate_rollout_health.py`.
- REFACTOR: clean threshold constants and output formatting for operator readability.
Verification Steps:
- `cd backend && uv run pytest -q tests/test_rollout_health.py`
- `cd backend && uv run python scripts/evaluate_rollout_health.py --help`
Risks (if any):
- Historical artifact formats may require compatibility handling.

### [ ] Task 4 — Delete legacy execution entrypoints in service layer

Goal:
- Remove legacy structured-review execution methods once v1-only behavior and invariants are protected.
Slice: service-legacy-removal
User Stories: US1, US2
PRD Requirements: FR4
Depends on: Task 2
Enables: Task 5, Task 6
Parallelizable: no
Files to modify:
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_review_engine_pipeline_v1.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Legacy service entrypoints/helpers are deleted or made unreachable.
- API and pipeline tests continue to pass with v1-only assumptions.
TDD Plan:
- RED: add/update failing tests that still reference or depend on legacy execution entrypoints.
- GREEN: remove legacy entrypoints and align callers/tests to v1-only path.
- REFACTOR: simplify service interfaces and remove dead helpers.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t4.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py`
Risks (if any):
- Residual imports/references to deleted helpers can break unrelated test modules.

### [ ] Task 5 — Remove obsolete dual-routing env logic

Goal:
- Eliminate runtime config branches that only existed to support legacy/v1 dual routing.
Slice: route-config-cleanup
User Stories: US1, US2
PRD Requirements: FR5, FR9
Depends on: Task 3, Task 4
Enables: Task 6
Parallelizable: no
Files to modify:
- `backend/main.py`
- `backend/tests/test_api.py`
- `backend/README.md`
Acceptance Criteria:
- Runtime no longer exposes dual-engine routing toggles for structured review.
- Tests and backend operator docs reflect single-engine truth.
TDD Plan:
- RED: add/update tests that fail if legacy routing env branches remain reachable.
- GREEN: remove obsolete env-branch logic and update docs for supported runtime controls.
- REFACTOR: simplify route/config naming to single-engine semantics.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t5.db uv run pytest -q tests/test_api.py -k "structured_review and routing"`
- `cd backend && rg -n \"STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES|legacy route|dual-engine\" main.py README.md`
Risks (if any):
- Mis-scoped cleanup could remove still-needed non-retirement env behavior.

### [ ] Task 6 — Finalize operational readiness and evidence handoff

Goal:
- Finalize retirement runbook/checklist with concrete evidence links and owner sign-off capture.
Slice: ops-handoff
User Stories: US1, US2
PRD Requirements: FR1, FR7, FR9, FR10
Depends on: Task 5
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
- `backend/README.md`
- `docs/logs/decisions.md`
Acceptance Criteria:
- Walkthrough checklist includes completed evidence references and explicit approval record section.
- Backend runbook states pre-delete rollback posture and post-delete revert-deploy posture.
- Decision log references final gate default usage for deletion approval.
TDD Plan:
- N/A (documentation and operational artifact consolidation only).
Verification Steps:
- `rg -n \"Replay/parity artifact|Rollout health output|owner approval|revert-deploy|config-first rollback\" docs/walkthroughs/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md backend/README.md docs/logs/decisions.md`
Risks (if any):
- Missing evidence links can delay approval even if code changes are complete.

## Changelog

- v0.1 (2026-03-01): Initial sequential task plan for controlled deprecation and legacy path retirement.
- v0.2 (2026-03-01): Applied Phase 2 review revisions for atomicity, strict FR/US traceability, dependency DAG validity, and explicit TDD/verification per task.
