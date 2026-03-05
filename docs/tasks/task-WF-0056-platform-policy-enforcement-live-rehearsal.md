# WF-0056 — Platform Policy Enforcement Live Rehearsal

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-05

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: manual verify workflow emits durable evidence

Goal:
Create a minimal manual rehearsal workflow path that runs live `verify` on `main` and publishes one evidence artifact for audit traceability.
Slice: tracer-bullet
User Stories: US1, US4
PRD Requirements: FR1, FR2, FR10, FR12
Depends on: none
Enables: 2, 5
Parallelizable: no
Files to modify:
- `.github/workflows/platform-policy-live-rehearsal.yml` (new)
- `backend/tests/scripts/test_ci_policy_event_scope.py`
- `docs/walkthroughs/evidence/WF-0056/.gitkeep` (new)
Acceptance Criteria:
- A workflow-dispatch job exists for `verify-main` and calls `uv run python -m tools.gh_policy.cli verify` against `main`.
- Verify job uploads evidence artifact from `docs/walkthroughs/evidence/WF-0056/`.
- Deterministic CI policy test fails if `verify-main` job or expected command is removed/renamed.
TDD Plan:
- RED: add selector `wf0056_live_rehearsal_verify_tracer_contract` in `backend/tests/scripts/test_ci_policy_event_scope.py` expecting missing workflow job to fail.
- GREEN: add minimal `verify-main` job and artifact upload in `.github/workflows/platform-policy-live-rehearsal.yml`.
- REFACTOR: extract shared workflow loader helper usage for WF-0056 selectors.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0056_live_rehearsal_verify_tracer_contract"`
- `rg -n "workflow_dispatch|verify-main|upload-artifact|tools.gh_policy.cli verify" .github/workflows/platform-policy-live-rehearsal.yml`
Risks (if any): Workflow naming drift can break required-check context traceability.

### [x] Task 2 — CLI rehearsal targeting and WF-0056 evidence path contracts

Goal:
Harden CLI defaults and argument validation so live rehearsal targets `main` for verify and `policy-rehearsal` for mutation flows with WF-0056 evidence paths.
Slice: cli-safety-contract
User Stories: US1, US2, US3, US4
PRD Requirements: FR3, FR5, FR7, FR9
Depends on: 1
Enables: 3, 5, 6
Parallelizable: no
Files to modify:
- `backend/tools/gh_policy/cli.py`
- `backend/tests/tools/gh_policy/test_apply_command.py`
- `backend/tests/tools/gh_policy/test_rollback_command.py`
Acceptance Criteria:
- CLI help/defaults reference WF-0056 evidence directories instead of WF-0055 paths.
- `apply` rejects `--branch main` with deterministic non-zero exit and explicit error message.
- `rollback` validates snapshot path existence and preserves deterministic evidence path output.
TDD Plan:
- RED: add failing tests `test_apply_rejects_main_branch_for_live_rehearsal` and `test_rollback_requires_existing_snapshot_path`.
- GREEN: implement branch-target guard and updated WF-0056 default paths in `cli.py`.
- REFACTOR: centralize shared branch/evidence-path constants in CLI module.
Verification Steps:
- `cd backend && uv run pytest tests/tools/gh_policy/test_apply_command.py -k "rehearsal or main_branch"`
- `cd backend && uv run pytest tests/tools/gh_policy/test_rollback_command.py -k "snapshot_path"`
- `cd backend && uv run python -m tools.gh_policy.cli apply --help`
Risks (if any): Existing automation depending on WF-0055 defaults may require explicit override flags.

### [x] Task 3 — Live required-check discovery integration in apply preflight

Goal:
Replace static required-check assumptions with live check-context discovery before apply mutation.
Slice: apply-preflight-discovery
User Stories: US2, US4
PRD Requirements: FR4, FR6, FR11
Depends on: 2
Enables: 5
Parallelizable: no
Files to modify:
- `backend/tools/gh_policy/apply.py`
- `backend/tools/gh_policy/github_client.py`
- `backend/tests/tools/gh_policy/test_apply_preflight.py`
Acceptance Criteria:
- Apply preflight queries live check-run contexts through GitHub client boundary.
- Missing expected contexts fail-closed with `missing_required_checks` and no mutation call.
- Evidence payload includes discovered context summary and preflight decision fields.
TDD Plan:
- RED: add failing test `test_apply_preflight_uses_live_context_discovery_and_fails_closed`.
- GREEN: implement discovery hook + comparison in apply preflight flow.
- REFACTOR: extract context diff formatter for deterministic evidence payloads.
Verification Steps:
- `cd backend && uv run pytest tests/tools/gh_policy/test_apply_preflight.py -k "live_context or missing_required_checks"`
- `rg -n "missing_required_checks|available_check_contexts|preflight" backend/tools/gh_policy/apply.py backend/tools/gh_policy/github_client.py`
Risks (if any): Sparse check-run history can produce false negatives if discovery window is too narrow.

### [x] Task 4 — Deterministic error-kind and linkage fields for shared evidence contract

Goal:
Ensure the shared evidence builder used by verify/apply/rollback emits stable error kinds and cross-artifact linkage fields.
Slice: evidence-contract
User Stories: US1, US2, US3, US4
PRD Requirements: FR2, FR11, FR12
Depends on: 2
Enables: 5, 6
Parallelizable: no
Files to modify:
- `backend/tools/gh_policy/evidence.py`
- `backend/tests/tools/gh_policy/test_verify_command.py`
- `backend/tests/tools/gh_policy/test_apply_command.py`
Acceptance Criteria:
- Evidence schema always includes `error.kind`, `workflow_run_id`, `commit_sha`, and `linked_artifacts` keys (nullable when unavailable).
- Error classifier maps permission, plan, API, and required-check failures to stable kinds.
- Verify and apply tests assert presence and determinism of these fields on both pass/fail paths.
TDD Plan:
- RED: add failing tests for missing linkage keys and unstable error kind mapping in verify/apply flows.
- GREEN: extend evidence builder/classifier and wire fields in verify/apply paths.
- REFACTOR: deduplicate error-kind mapping table into one helper.
Verification Steps:
- `cd backend && uv run pytest tests/tools/gh_policy/test_verify_command.py -k "error_kind or linked_artifacts"`
- `cd backend && uv run pytest tests/tools/gh_policy/test_apply_command.py -k "error_kind or linked_artifacts"`
Risks (if any): Over-strict schema enforcement may require coordinated fixture updates.

### [x] Task 5 — Apply rehearsal job with permissions preflight, snapshot, and artifact upload

Goal:
Implement the live apply rehearsal workflow job for `policy-rehearsal` with deterministic preflight gating and snapshot/evidence publication.
Slice: live-apply-workflow
User Stories: US2, US4
PRD Requirements: FR3, FR4, FR5, FR6, FR9
Depends on: 1, 3, 4
Enables: 6, 7
Parallelizable: no
Files to modify:
- `.github/workflows/platform-policy-live-rehearsal.yml`
- `backend/tests/scripts/test_ci_policy_event_scope.py`
- `backend/tools/gh_policy/cli.py`
Acceptance Criteria:
- `apply-rehearsal` workflow job only allows branch target `policy-rehearsal`.
- Job executes apply with explicit intent flag and uploads both apply evidence and snapshot artifacts.
- Deterministic CI selector fails when preflight flags/artifact uploads are missing.
TDD Plan:
- RED: add selector `wf0056_live_rehearsal_apply_contract` expecting failure before apply job wiring.
- GREEN: wire apply job steps, required env, and artifact uploads.
- REFACTOR: extract shared workflow env/paths into reusable anchors or constants where possible.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0056_live_rehearsal_apply_contract"`
- `rg -n "apply-rehearsal|policy-rehearsal|--apply-intent|snapshot|upload-artifact" .github/workflows/platform-policy-live-rehearsal.yml`
- `cd backend && uv run python -m tools.gh_policy.cli apply --help`
Risks (if any): Insufficient token scopes in Actions may block live mutation even when logic is correct.

### [x] Task 6 — Rollback rehearsal job with snapshot restore verification

Goal:
Add rollback workflow execution that consumes a selected snapshot artifact, restores policy state, and publishes rollback evidence.
Slice: live-rollback-workflow
User Stories: US3, US4
PRD Requirements: FR7, FR8, FR9, FR12
Depends on: 2, 4, 5
Enables: 7, 8
Parallelizable: no
Files to modify:
- `.github/workflows/platform-policy-live-rehearsal.yml`
- `backend/tools/gh_policy/rollback.py`
- `backend/tests/tools/gh_policy/test_rollback_command.py`
Acceptance Criteria:
- Workflow exposes rollback path that requires explicit snapshot input.
- Rollback verifies restored policy parity and emits rollback evidence with source snapshot linkage.
- Rollback job uploads evidence artifact even on failure.
TDD Plan:
- RED: add failing test `test_rollback_evidence_includes_source_snapshot_linkage`.
- GREEN: implement linkage + restore verification updates and workflow rollback step wiring.
- REFACTOR: isolate rollback evidence payload assembly from command orchestration.
Verification Steps:
- `cd backend && uv run pytest tests/tools/gh_policy/test_rollback_command.py -k "source_snapshot or rollback"`
- `rg -n "rollback-rehearsal|snapshot-path|rollback_evidence|upload-artifact" .github/workflows/platform-policy-live-rehearsal.yml`
Risks (if any): Snapshot handoff across workflow steps can fail if artifact naming conventions are unstable.

### [ ] Task 7 — Rehearsal safety and non-main-mutation regression gates

Goal:
Lock in execution safety guarantees that live rehearsal never mutates `main` and always fails closed on invalid target/mechanism conditions.
Slice: safety-regression-gates
User Stories: US2, US3
PRD Requirements: FR3, FR6, FR11
Depends on: 5, 6
Enables: 8
Parallelizable: no
Files to modify:
- `backend/tests/tools/gh_policy/test_apply_command.py`
- `backend/tests/scripts/test_ci_policy_event_scope.py`
- `.github/workflows/ci.yml`
Acceptance Criteria:
- Regression tests assert mutation path aborts when target branch resolves to `main`.
- CI includes deterministic WF-0056 safety selector execution in backend lane.
- Failure messages clearly classify `permission_denied`, `plan_gated`, and `api_failure` categories for operators.
TDD Plan:
- RED: add failing selectors/tests for main-target mutation attempts and missing `wf0056_live_rehearsal_safety_gates` execution in CI.
- GREEN: wire safety selectors in CI and implement/adjust guard behavior to satisfy tests.
- REFACTOR: reduce duplicated test fixtures for error-kind assertions.
Verification Steps:
- `cd backend && uv run pytest tests/tools/gh_policy/test_apply_command.py -k "rejects_main_branch or error_kind"`
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0056_live_rehearsal_safety_gates"`
- `rg -n "wf0056|policy-live-rehearsal|ci_policy_event_scope" .github/workflows/ci.yml`
Risks (if any): Overlapping selectors from prior WFs can hide WF-0056-specific regressions if naming is ambiguous.

### [ ] Task 8 — Runbook and walkthrough with full verify->apply->rollback evidence chain

Goal:
Document reproducible live rehearsal operations and record final evidence chain with checksum traceability.
Slice: ops-documentation
User Stories: US4
PRD Requirements: FR9, FR10, FR12
Depends on: 6, 7
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/runbooks/WF-0056-platform-policy-enforcement-live-rehearsal.md` (new)
- `docs/walkthroughs/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md`
- `docs/walkthroughs/evidence/WF-0056/README.md` (new)
Acceptance Criteria:
- Runbook defines preflight prerequisites, live command sequence, and failure handling by `error.kind`.
- Walkthrough captures artifact references and checksums for verify/apply/rollback outputs.
- Walkthrough captures explicit live-proof fields (`workflow_run_id`, run URL, commit SHA) for each operation; static stub evidence is called out as invalid for completion.
- Evidence README defines fallback storage layout and checksum generation command(s).
TDD Plan: N/A (documentation artifact)
Verification Steps:
- `rg -n "verify|apply|rollback|evidence_sha256|snapshot_sha256|workflow_run_id|linked_artifacts|commit_sha|run(_| )URL|stub evidence" docs/walkthroughs/runbooks/WF-0056-platform-policy-enforcement-live-rehearsal.md docs/walkthroughs/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md docs/walkthroughs/evidence/WF-0056/README.md`
- `test -f docs/walkthroughs/runbooks/WF-0056-platform-policy-enforcement-live-rehearsal.md && test -f docs/walkthroughs/evidence/WF-0056/README.md`
Risks (if any): Documentation can drift from actual workflow inputs if dispatch parameters are renamed.

## Changelog

- v0.1 (2026-03-05): Initial task breakdown from PRD
- v0.2 (2026-03-05): Applied Phase 2.2 review refinements (apply-path evidence coverage, explicit WF-0056 safety selector contract, stronger live-proof documentation criteria); marked Ready for Implementation
- v0.3 (2026-03-05): Adversarial Part B pass confirmed blocker-free plan; tightened Task 4 evidence-contract scope/FR mapping and hardened docs verification pattern
