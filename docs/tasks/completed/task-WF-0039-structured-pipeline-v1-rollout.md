# WF-0039 — Structured Pipeline v1 Rollout

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-01

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: deterministic canary routing decision

Goal:
- Prove the backend structured-review route deterministically selects legacy vs `pipeline_v1` by env + call code allowlist.
Slice: tracer-bullet
User Stories: US1, US3
PRD Requirements: FR1, FR3, FR10
Depends on: none
Enables: Task 2, Task 3
Parallelizable: no
Files to modify:
- `backend/tests/test_api.py`
Acceptance Criteria:
- Route-level test proves allowlisted canary call routes to `pipeline_v1`.
- Route-level test proves non-allowlisted call routes to legacy path.
- No request/response contract behavior changes.
TDD Plan:
- RED: add failing tests in `backend/tests/test_api.py` for allowlisted and non-allowlisted path selection.
- GREEN: adjust only minimal routing seam usage to satisfy tests if needed.
- REFACTOR: consolidate duplicated structured-review test setup helpers (`skip` if none).
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_phase2a.db uv run pytest -q tests/test_api.py -k "structured_review and pipeline_v1 and allowlist"`
Risks (if any):
- Existing test fixtures may not expose path selection cleanly; keep assertions focused on service call target.

### [x] Task 2 — Production guardrail: fail-closed on empty allowlist

Goal:
- Enforce production-safe behavior when global flag is on and allowlist is empty.
Slice: prod-guardrail
User Stories: US1, US2
PRD Requirements: FR2, FR8, FR10
Depends on: Task 1
Enables: Task 6
Parallelizable: no
Files to modify:
- `backend/main.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- When `APP_ENV=prod`, `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1`, and empty allowlist, requests route to legacy path (fail-closed).
- Guardrail emits an operator-visible warning/error log marker.
- Non-prod behavior remains unchanged.
TDD Plan:
- RED: add failing API test covering prod empty-allowlist fail-closed behavior.
- GREEN: implement guardrail logic in routing helper.
- REFACTOR: normalize environment parsing helper for readability (`skip` if none).
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_phase2b.db uv run pytest -q tests/test_api.py -k "prod and allowlist and fail_closed"`
Risks (if any):
- Environment detection drift; keep `APP_ENV` contract explicit and tested.

### [x] Task 3 — Engine-path telemetry tagging for structured-review requests

Goal:
- Ensure rollout observability includes engine-path attribution per request.
Slice: telemetry-tagging
User Stories: US2, US4
PRD Requirements: FR9
Depends on: Task 1
Enables: Task 6
Parallelizable: yes (planning-only)
Files to modify:
- `backend/main.py`
- `backend/tests/test_api.py`
- `backend/tests/test_engine_telemetry.py`
Acceptance Criteria:
- Structured-review execution emits telemetry/log metadata including `engine_path` (`legacy` or `pipeline_v1`).
- Tests validate engine-path tag presence on both paths.
TDD Plan:
- RED: add failing tests for telemetry tag emission on legacy and v1.
- GREEN: emit engine-path telemetry at route/service seam.
- REFACTOR: deduplicate telemetry payload builder (`skip` if none).
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_phase2c.db uv run pytest -q tests/test_engine_telemetry.py tests/test_api.py -k "engine_path or structured_review"`
Risks (if any):
- Over-coupling tests to logging text; assert on structured fields, not strings.

### [x] Task 4 — Replay comparator contract: structural parity + status/error stability

Goal:
- Implement deterministic replay comparator logic for rollout evidence gate.
Slice: replay-comparator
User Stories: US3, US4
PRD Requirements: FR4, FR5, FR6
Depends on: Task 1
Enables: Task 5
Parallelizable: no
Files to modify:
- `backend/scripts/replay_structured_rollout.py` (new)
- `backend/tests/test_rollout_replay.py` (new)
Acceptance Criteria:
- Comparator evaluates two runs (legacy vs v1) for:
  - card count/order/rating structural parity,
  - status/error-code stability.
- Comparator output is deterministic JSON.
TDD Plan:
- RED: add failing test in `backend/tests/test_rollout_replay.py` for comparator mismatch detection and deterministic output shape.
- GREEN: implement minimal comparator in script/module.
- REFACTOR: extract parity-check helpers if duplicated (`skip` if none).
Verification Steps:
- `cd backend && uv run pytest -q tests/test_rollout_replay.py -k "parity or comparator"`
Risks (if any):
- Comparator may accidentally include text parity; keep scope strictly structural.

### [x] Task 5 — Replay evidence artifact writer (2 payloads x 20 replays)

Goal:
- Produce deterministic replay evidence artifacts committed on branch for canary decisions.
Slice: replay-artifacts
User Stories: US4
PRD Requirements: FR5, FR6
Depends on: Task 4
Enables: Task 6
Parallelizable: no
Files to modify:
- `backend/scripts/replay_structured_rollout.py`
- `backend/tests/test_rollout_replay.py`
- `docs/guides/engineering-standards.md`
Acceptance Criteria:
- Script supports running `2 payloads x 20 replays` and writes deterministic JSON artifact under a documented path.
- Docs include exact command and artifact location contract.
TDD Plan:
- RED: add failing test in `backend/tests/test_rollout_replay.py` for artifact schema and deterministic key ordering.
- GREEN: implement artifact writer and iteration loop.
- REFACTOR: isolate artifact-path resolver (`skip` if none).
Verification Steps:
- `cd backend && uv run pytest -q tests/test_rollout_replay.py -k "artifact or replay"`
- `cd backend && uv run python scripts/replay_structured_rollout.py --replays 20 --output artifacts/rollout/replay_canary.json`
Risks (if any):
- Runtime cost; keep defaults aligned to PRD while allowing CLI overrides for local dev.

### [x] Task 6 — Rollback trigger evaluator and operator runbook sync

Goal:
- Encode rollback threshold checks and align operator runbook with executable commands.
Slice: rollback-ops
User Stories: US2, US4
PRD Requirements: FR7, FR8, FR9
Depends on: Task 2, Task 3, Task 5
Enables: Task 7
Parallelizable: no
Files to modify:
- `backend/scripts/evaluate_rollout_health.py` (new)
- `backend/README.md`
- `backend/tests/test_rollout_health.py` (new)
Acceptance Criteria:
- Script evaluates thresholds (error-rate/latency/parity) using replay/telemetry inputs and returns pass/fail.
- Backend runbook documents rollback commands for global disable and call removal.
- Tests validate threshold evaluation edge behavior.
TDD Plan:
- RED: add failing tests in `backend/tests/test_rollout_health.py` for threshold breach and pass cases.
- GREEN: implement evaluator script and runbook updates.
- REFACTOR: centralize threshold constants (`skip` if none).
Verification Steps:
- `cd backend && uv run pytest -q tests/test_rollout_health.py`
- `cd backend && uv run python scripts/evaluate_rollout_health.py --input artifacts/rollout/replay_canary.json`
Risks (if any):
- Threshold inputs may be sparse; fail-safe output should recommend rollback when data is insufficient.

### [x] Task 7 — End-to-end canary workflow verification (staging-simulated)

Goal:
- Validate full canary workflow from gating to replay evidence to rollback decision in one automated verification sequence.
Slice: e2e-verification
User Stories: US1, US2, US3, US4
PRD Requirements: FR1, FR2, FR4, FR5, FR7, FR8, FR9, FR10
Depends on: Task 6
Enables: none
Parallelizable: no
Files to modify:
- `backend/tests/test_api.py`
- `backend/tests/test_review_engine_pipeline_v1.py`
- `docs/walkthroughs/walkthrough-WF-0039-structured-pipeline-v1-rollout.md`
Acceptance Criteria:
- Automated test flow verifies:
  - allowlist routing behavior,
  - prod guardrail fail-closed behavior,
  - replay evidence artifact generation,
  - rollback evaluator pass/fail behavior.
- Walkthrough includes staging-simulated execution checklist and expected outputs.
TDD Plan:
- RED: add failing integrated regression test matrix for canary flow.
- GREEN: wire minimal glue adjustments to satisfy test matrix.
- REFACTOR: prune duplicated setup fixtures between API and pipeline tests (`skip` if none).
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_phase2e.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py -k "canary or rollout or fail_closed"`
Risks (if any):
- Integration matrix can become brittle; keep assertions contract-focused and deterministic.

## Changelog

- v0.1 (2026-03-01): Initial task breakdown from PRD
- v0.2 (2026-03-01): Applied review edits (script-test boundary split, concrete replay/evaluator verification commands, readiness set to implementation)
