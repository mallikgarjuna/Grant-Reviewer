# WF-0055 — Platform Policy Enforcement

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-05

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: verify path emits deterministic evidence

Goal:
Stand up a minimal verify-only command path that reads a fixture-backed live policy, compares to expected policy, and writes one evidence JSON artifact.
Slice: tracer-bullet
User Stories: US2
PRD Requirements: FR2, FR4, FR5, FR7, FR11
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
- `tools/gh_policy/cli.py` (new)
- `tools/gh_policy/evidence.py` (new)
- `tests/tools/gh_policy/test_verify_tracer.py` (new)
Acceptance Criteria:
- A verify command exists and supports explicit verify-only mode.
- Verify writes one evidence JSON file with `drift`, `mechanism`, and `evidence_sha256`.
- A deterministic tracer test fails when evidence output is absent or malformed.
TDD Plan:
- RED: add `test_verify_tracer_writes_evidence_json` in `tests/tools/gh_policy/test_verify_tracer.py`.
- GREEN: implement minimal `verify` CLI path and evidence writer.
- REFACTOR: extract shared evidence payload builder into `tools/gh_policy/evidence.py`.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_verify_tracer.py -k "writes_evidence_json"`
- `uv run python -m tools.gh_policy.cli verify --help`
Risks (if any): CLI entrypoint wiring may differ from repo conventions and require import-path adjustments.

### [x] Task 2 — Expected policy contract loader and schema validation

Goal:
Define and validate the in-repo expected policy contract for `main` including exact required checks and toggle surface.
Slice: policy-contract
User Stories: US1, US2, US3
PRD Requirements: FR1, FR9, FR10
Depends on: 1
Enables: 4, 5
Parallelizable: no
Files to modify:
- `tools/gh_policy/policy_schema.py` (new)
- `config/platform_policy/main_policy.yaml` (new)
- `tests/tools/gh_policy/test_policy_schema.py` (new)
Acceptance Criteria:
- Expected policy file contains `schema_version`, `target_branch`, 6 required checks, and full toggle surface from PRD.
- Loader validates malformed or incomplete policy with deterministic error messages.
- Schema test covers success and one required-field failure case.
TDD Plan:
- RED: add failing schema tests in `tests/tools/gh_policy/test_policy_schema.py`.
- GREEN: implement strict loader/validator and baseline `main_policy.yaml`.
- REFACTOR: centralize default toggle normalization helper in `policy_schema.py`.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_policy_schema.py`
- `rg -n "required_checks|enforce_admins|strict_required_status_checks" config/platform_policy/main_policy.yaml`
Risks (if any): Strict validation may require explicit ordering rules for required checks.

### [x] Task 3 — GitHub live policy reader with rulesets-first fallback

Goal:
Implement read-only GitHub client logic that tries rulesets first and falls back to branch protection with deterministic plan/permission error mapping.
Slice: live-read
User Stories: US2, US3
PRD Requirements: FR2, FR11
Depends on: 1
Enables: 4, 6
Parallelizable: no
Files to modify:
- `tools/gh_policy/github_client.py` (new)
- `tests/tools/gh_policy/test_github_client_read.py` (new)
- `tests/tools/gh_policy/fixtures/rulesets_plan_gated.json` (new)
Acceptance Criteria:
- Read path selects `rulesets` when available and uses branch protection fallback when rulesets are unavailable.
- Plan-gated and permission-denied responses map to explicit error kinds (`plan_gated`, `permission_denied`).
- Tests cover rulesets success, fallback success, and one deterministic plan-gated failure.
TDD Plan:
- RED: add failing read-path tests in `tests/tools/gh_policy/test_github_client_read.py`.
- GREEN: implement `GitHubPolicyClient.read_live_policy()` with endpoint-selection logic.
- REFACTOR: extract response-to-error classifier helper.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_github_client_read.py`
- `rg -n "plan_gated|permission_denied|branch_protection" tools/gh_policy/github_client.py`
Risks (if any): GitHub API variant payloads may require robust response normalization.

### [x] Task 4 — Policy normalization and drift diff engine

Goal:
Normalize rulesets/branch-protection payloads into one stable contract and produce minimal field-level drift diffs.
Slice: normalize-diff
User Stories: US2
PRD Requirements: FR3, FR4, FR9, FR10
Depends on: 2, 3
Enables: 5, 6, 7
Parallelizable: no
Files to modify:
- `tools/gh_policy/normalizer.py` (new)
- `tools/gh_policy/diff.py` (new)
- `tests/tools/gh_policy/test_normalizer_diff.py` (new)
Acceptance Criteria:
- Normalizer outputs stable ordering and full canonical toggle surface.
- Diff engine returns deterministic minimal changes keyed by canonical field names.
- Tests validate both rulesets and branch-protection normalization into equivalent canonical structures.
TDD Plan:
- RED: add failing canonical-equivalence and minimal-diff tests.
- GREEN: implement normalization and diff helpers.
- REFACTOR: deduplicate canonical field mapping constants.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_normalizer_diff.py`
- `uv run pytest tests/tools/gh_policy/test_verify_tracer.py -k "drift"`
Risks (if any): Missing default handling can create noisy false-positive drift.

### [x] Task 5 — Verify command: drift failure semantics and CI-safe behavior

Goal:
Harden verify behavior so CI is strictly mutation-free, emits evidence on every run, and exits non-zero when drift exists.
Slice: verify-command
User Stories: US2
PRD Requirements: FR4, FR5, FR7, FR11
Depends on: 2, 4
Enables: 9
Parallelizable: no
Files to modify:
- `tools/gh_policy/verify.py` (new)
- `tests/tools/gh_policy/test_verify_command.py` (new)
- `tools/gh_policy/cli.py`
Acceptance Criteria:
- Verify command never performs mutation calls.
- Drifted policy yields non-zero exit and minimal diff in output/evidence.
- Tests prove no mutation path is invoked during verify execution.
TDD Plan:
- RED: add failing `test_verify_drift_returns_nonzero_and_no_mutation`.
- GREEN: implement verify orchestration using read + normalize + diff + evidence.
- REFACTOR: consolidate CLI-to-command argument parsing.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_verify_command.py`
- `uv run python -m tools.gh_policy.cli verify --repo owner/repo --branch main`
Risks (if any): Exit-code handling can drift if CLI wrapper swallows command errors.

### [x] Task 6 — Apply preflight and rollback snapshot capture

Goal:
Implement controlled apply preflight checks (intent, permissions, required contexts) and deterministic snapshot capture before mutation.
Slice: apply-preflight
User Stories: US1, US3, US4
PRD Requirements: FR6, FR11, FR12, FR13
Depends on: 2, 3, 4
Enables: 7, 8
Parallelizable: no
Files to modify:
- `tools/gh_policy/apply.py` (new)
- `tests/tools/gh_policy/test_apply_preflight.py` (new)
- `tools/gh_policy/snapshot.py` (new)
Acceptance Criteria:
- Apply requires explicit apply intent; otherwise exits without mutation.
- Preflight fails with deterministic `missing_required_checks` or `permission_denied` errors when applicable.
- Snapshot artifact is written before any mutation call and includes `snapshot_sha256`.
- Snapshot file path follows `docs/walkthroughs/evidence/WF-0055/snapshots/snapshot_<repo>_<branch>_<utc-timestamp>.json`.
TDD Plan:
- RED: add failing tests for missing apply intent and missing required check contexts.
- GREEN: implement preflight and snapshot capture path.
- REFACTOR: extract required-check-context comparison helper.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_apply_preflight.py`
- `rg -n "missing_required_checks|snapshot_sha256|apply intent" tools/gh_policy/apply.py tools/gh_policy/snapshot.py`
Risks (if any): Context-existence checks can be brittle if CI job naming conventions are inconsistent.

### [ ] Task 7 — Apply mutation and post-apply verification evidence

Goal:
Execute controlled policy apply from CLI, then re-read and assert live policy matches expected before marking success.
Slice: apply-mutate-verify
User Stories: US1, US3
PRD Requirements: FR2, FR5, FR6, FR10, FR11
Depends on: 6
Enables: 8, 9
Parallelizable: no
Files to modify:
- `tools/gh_policy/apply.py`
- `tests/tools/gh_policy/test_apply_command.py` (new)
- `tools/gh_policy/cli.py`
Acceptance Criteria:
- Apply performs mutation through selected mechanism and then re-reads live policy.
- Apply success is contingent on post-apply normalized parity with expected policy.
- Evidence artifact is emitted for success and failure paths.
- CLI exposes an explicit apply command that requires explicit apply intent.
TDD Plan:
- RED: add failing tests for post-apply mismatch and no-evidence-on-failure regression.
- GREEN: implement mutate + post-verify orchestration with deterministic exits.
- REFACTOR: extract shared read-normalize-compare helper for verify/apply parity.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_apply_command.py`
- `uv run pytest tests/tools/gh_policy/test_apply_command.py -k "post_apply"`
- `uv run python -m tools.gh_policy.cli apply --help`
Risks (if any): Divergent rulesets vs branch-protection mutation semantics can cause false success if parity checks are incomplete.

### [ ] Task 8 — Rollback command restores snapshot deterministically

Goal:
Add rollback flow that restores a selected snapshot and emits rollback evidence after verification.
Slice: rollback
User Stories: US4
PRD Requirements: FR8, FR11, FR12, FR14
Depends on: 7
Enables: 10
Parallelizable: no
Files to modify:
- `tools/gh_policy/rollback.py` (new)
- `tests/tools/gh_policy/test_rollback_command.py` (new)
- `tools/gh_policy/cli.py`
Acceptance Criteria:
- Rollback accepts a snapshot artifact and restores through the recorded mechanism path.
- Rollback re-reads policy and verifies restoration before success exit.
- Rollback writes evidence with populated `error` surface on restore failure.
TDD Plan:
- RED: add failing test for restore mismatch after rollback attempt.
- GREEN: implement rollback command + verification + evidence path.
- REFACTOR: share snapshot-loading validation logic between apply and rollback.
Verification Steps:
- `uv run pytest tests/tools/gh_policy/test_rollback_command.py`
- `uv run python -m tools.gh_policy.cli rollback --help`
Risks (if any): Snapshot schema drift can break deterministic restore if versioning is not validated.

### [ ] Task 9 — CI wiring for verify-only enforcement context

Goal:
Wire verify-only policy drift detection into GitHub Actions and ensure required check context naming is enforceable for branch policy.
Slice: ci-wiring
User Stories: US1, US2
PRD Requirements: FR7, FR9, FR13
Depends on: 5
Enables: 10
Parallelizable: no
Files to modify:
- `.github/workflows/verify-platform-policy.yml` (new)
- `.github/workflows/ci.yml`
- `backend/tests/scripts/test_ci_policy_event_scope.py`
Acceptance Criteria:
- A dedicated verify workflow runs in PR context and invokes verify-only command.
- Workflow/job naming is aligned so required check contexts are emitted exactly as contracted.
- Deterministic CI policy selector fails if verify workflow context is renamed or ungated.
TDD Plan:
- RED: add/extend CI policy selector test asserting expected verify context emission.
- GREEN: add verify workflow and minimal CI updates to satisfy selector.
- REFACTOR: trim duplicate workflow condition fragments while preserving event safety.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "platform_policy or wf0055"`
- `rg -n "verify-platform-policy|Contract Boundary Governance Check|WF-0054 CI Policy Regression Sweep|Contract Gate \\(Marker\\)|Test \\(Pytest no_db\\)|frontend / Lint|frontend / Build" .github/workflows`
Risks (if any): Existing workflow naming conventions may conflict with exact required-check string contracts.

### [ ] Task 10 — Runbook and walkthrough evidence documentation

Goal:
Document operational verify/apply/rollback flows, prerequisites, and failure modes with evidence path contracts.
Slice: operations-docs
User Stories: US3, US4
PRD Requirements: FR5, FR8, FR11, FR12, FR14
Depends on: 8, 9
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/runbooks/WF-0055-platform-policy-enforcement.md` (new)
- `docs/walkthroughs/walkthrough-WF-0055-platform-policy-enforcement.md`
Acceptance Criteria:
- Runbook includes prerequisite matrix, verify/apply/rollback commands, and deterministic failure interpretation.
- Documentation includes evidence and snapshot file locations/patterns from the PRD contract.
- Walkthrough records final verification evidence references for WF-0055 completion.
TDD Plan: N/A (documentation and operational handoff)
Verification Steps:
- `rg -n "verify|apply|rollback|evidence|snapshot|plan_gated|permission_denied|missing_required_checks" docs/walkthroughs/runbooks/WF-0055-platform-policy-enforcement.md docs/walkthroughs/walkthrough-WF-0055-platform-policy-enforcement.md`
Risks (if any): Runbook drift can mislead operators if command flags diverge from CLI implementation.

## Changelog

- v0.1 (2026-03-05): Initial task breakdown from PRD
- v0.2 (2026-03-05): Applied Part B review edits (dependency correction for apply preflight, CI-task decoupling from apply path, verification command fix, and explicit snapshot path contract); marked Ready for Implementation
- v0.3 (2026-03-05): Adversarial Part B pass cleared final blocker by adding explicit CLI apply-entrypoint coverage in Task 7; readiness retained
