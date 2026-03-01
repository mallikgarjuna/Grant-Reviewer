# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: task
Version: v0.1
Status: Ready for Implementation
Last Updated: 2026-03-01

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Baseline retirement readiness audit

Goal:
- Produce a concrete go/no-go checklist from current production/staging evidence.
Slice: readiness-audit
User Stories: US1, US2
PRD Requirements: FR1, FR2
Depends on: none
Enables: Task 2
Parallelizable: no
Files to modify:
- `backend/README.md`
- `docs/walkthroughs/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md` (new)
Acceptance Criteria:
- Checklist defines required replay/health evidence and observation windows.
- Checklist has explicit go/no-go decision points.
TDD Plan:
- RED: add checklist assertions as failing test placeholders where automation exists.
- GREEN: wire checklist references to existing scripts/artifacts.
- REFACTOR: tighten wording and remove duplicate steps.
Verification Steps:
- `cd backend && uv run python scripts/replay_structured_rollout.py --help`
- `cd backend && uv run python scripts/evaluate_rollout_health.py --help`
Risks (if any):
- Checklist can drift from real runtime behavior if not tied to scripts.

### [ ] Task 2 — Enforce v1-only routing mode (pre-delete safe state)

Goal:
- Route all structured-review execution to `pipeline_v1` while legacy code remains temporarily for rollback.
Slice: v1-only-runtime
User Stories: US1, US3
PRD Requirements: FR3, FR6
Depends on: Task 1
Enables: Task 3
Parallelizable: no
Files to modify:
- `backend/main.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Dual-path runtime routing is disabled; v1 path is always selected for structured review.
- API behavior and idempotency semantics remain unchanged.
TDD Plan:
- RED: failing tests for forced v1-only routing and contract stability.
- GREEN: minimal routing changes to satisfy tests.
- REFACTOR: remove dead condition branches where safe.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t2.db uv run pytest -q tests/test_api.py -k "structured_review and pipeline_v1"`
Risks (if any):
- Hidden reliance on legacy branch behavior for edge cases.

### [ ] Task 3 — Harden v1-only regression safety net

Goal:
- Add/adjust tests to cover v1-only edge cases formerly covered indirectly by legacy fallback.
Slice: regression-hardening
User Stories: US2, US3
PRD Requirements: FR2, FR6
Depends on: Task 2
Enables: Task 4
Parallelizable: no
Files to modify:
- `backend/tests/test_review_engine_pipeline_v1.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Explicit coverage exists for malformed payloads, missing config paths, and stable error codes in v1-only mode.
- Replay and rollout-health scripts still pass on representative fixtures.
TDD Plan:
- RED: add failing edge-case tests.
- GREEN: implement smallest fixes needed in v1 path.
- REFACTOR: consolidate test fixtures.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t3.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py`
- `cd backend && uv run pytest -q tests/test_rollout_replay.py tests/test_rollout_health.py`
Risks (if any):
- Overly brittle tests if assertions are tied to non-contract text.

### [ ] Task 4 — Delete legacy execution path and obsolete env routing logic

Goal:
- Remove legacy structured-review execution code and dead routing toggles.
Slice: code-removal
User Stories: US1, US2
PRD Requirements: FR4, FR5
Depends on: Task 3
Enables: Task 5
Parallelizable: no
Files to modify:
- `backend/main.py`
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/` (targeted files)
Acceptance Criteria:
- Legacy execution entrypoints are removed.
- Obsolete dual-routing env logic is removed.
- Test suite passes with v1-only assumptions.
TDD Plan:
- RED: tests fail when legacy references remain or contracts break.
- GREEN: delete legacy code and update tests.
- REFACTOR: simplify naming/comments to single-engine terminology.
Verification Steps:
- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t4.db uv run pytest -q`
Risks (if any):
- Incomplete removal can leave dead code or broken imports.

### [ ] Task 5 — Operational documentation and release cutover finalization

Goal:
- Finalize operator docs, rollout/runbook, and release notes for post-legacy world.
Slice: ops-finalization
User Stories: US1, US2
PRD Requirements: FR7
Depends on: Task 4
Enables: none
Parallelizable: no
Files to modify:
- `backend/README.md`
- `docs/guides/engineering-standards.md`
- `docs/walkthroughs/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
Acceptance Criteria:
- Docs no longer instruct dual-engine operations.
- Rollback policy reflects post-delete code rollback model.
- Release checklist includes post-ship monitoring tasks.
TDD Plan:
- RED: identify stale dual-engine doc references.
- GREEN: update docs and commands.
- REFACTOR: reduce duplicate operational guidance across docs.
Verification Steps:
- `rg -n "STRUCTURED_REVIEW_PIPELINE_V1_ENABLED|legacy structured|allowlist" backend/README.md docs/guides/engineering-standards.md docs/walkthroughs/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
Risks (if any):
- Doc drift can cause incorrect operator actions during incidents.

## Changelog

- v0.1 (2026-03-01): Initial sequential task plan for controlled deprecation and legacy path retirement.
