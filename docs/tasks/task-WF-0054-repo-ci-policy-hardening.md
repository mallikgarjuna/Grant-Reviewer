# WF-0054 — Repo-side CI Policy Hardening

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-05

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: governed-step inventory + PR-only scope assertion

Goal:
Establish a single governed-step inventory and prove one end-to-end PR-only governance invariant with deterministic CI-policy tests.
Slice: tracer-bullet
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR4, FR9
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
- `backend/scripts/ci_policy_inventory.py` (new)
- `backend/tests/scripts/test_ci_policy_event_scope.py` (new)
- `.github/workflows/ci.yml`
Acceptance Criteria:
- A governed-step inventory module defines stable governed check IDs and expected `event_scope` class for WF-0054.
- Deterministic test `wf0054_ci_policy_inventory_pr_only_tracer` fails when a governed PR-dependent check is missing or ungated.
- CI runs the tracer selector in backend lane so regressions fail pre-merge.
TDD Plan:
- RED: Add `wf0054_ci_policy_inventory_pr_only_tracer` in `backend/tests/scripts/test_ci_policy_event_scope.py` asserting one governed step is present and PR-only gated.
- GREEN: Add minimal inventory constants in `backend/scripts/ci_policy_inventory.py` and wire selector execution in `.github/workflows/ci.yml`.
- REFACTOR: Extract shared workflow-loading helper in the new test module for subsequent WF-0054 selectors.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_inventory_pr_only_tracer"`
- `rg -n "wf0054_ci_policy_inventory_pr_only_tracer|ci_policy_event_scope" .github/workflows/ci.yml`
Risks (if any): Existing CI naming drift may require precise governed-step ID normalization to avoid false negatives.

### [x] Task 2 — Deterministic policy matrix tests for pull_request vs push behavior

Goal:
Add deterministic positive and negative CI-policy assertions for PR-vs-push governance execution rules.
Slice: event-scope-matrix
User Stories: US1, US2
PRD Requirements: FR2, FR3, FR4, FR5, FR8, FR9
Depends on: 1
Enables: 3
Parallelizable: no
Files to modify:
- `backend/tests/scripts/test_ci_policy_event_scope.py`
- `backend/scripts/ci_policy_inventory.py`
Acceptance Criteria:
- Tests assert PR-dependent governed checks are executable only on `pull_request`.
- Tests assert push-safe checks are allowed on `push` and PR-dependent checks are not.
- Negative selector `wf0054_ci_policy_negative_removed_pr_guard_fails` proves deterministic fail behavior when PR guard is absent/simulated absent.
TDD Plan:
- RED: Add failing selectors for PR-positive, push-negative, and removed-guard-negative scenarios.
- GREEN: Extend inventory metadata/helpers to evaluate `if` expressions and event trigger context deterministically.
- REFACTOR: Consolidate event-expression predicate helpers to keep selector logic stable and explicit.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_event_scope_pr_positive or wf0054_ci_policy_event_scope_push_negative or wf0054_ci_policy_negative_removed_pr_guard_fails"`
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_"`
Risks (if any): Workflow expression variants may require normalization logic to keep AST-first checks robust.

### [x] Task 3 — Harden `.github/workflows/ci.yml` governance gating to satisfy policy contract

Goal:
Align CI workflow with explicit governance classes so push runs remain push-safe and PR-dependent checks are gated.
Slice: ci-gating-hardening
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR4, FR8
Depends on: 2
Enables: 4
Parallelizable: no
Files to modify:
- `.github/workflows/ci.yml`
- `backend/tests/scripts/test_ci_policy_event_scope.py`
- `backend/scripts/ci_policy_inventory.py`
Acceptance Criteria:
- Every governed PR-dependent check in inventory has explicit PR-only guard expression in CI YAML.
- Push-on-main execution excludes PR-dependent governed checks.
- Deterministic selectors from Task 2 pass without test skips or nondeterministic filtering.
TDD Plan:
- RED: Keep Task 2 selectors failing against current CI policy wiring until explicit guards are in place.
- GREEN: Apply minimal `.github/workflows/ci.yml` guard changes and inventory alignment to satisfy selectors.
- REFACTOR: Reduce duplicate conditional fragments in CI workflow while preserving behavior.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_"`
- `rg -n "if: github.event_name == 'pull_request'|Contract Boundary Governance Check|WF-0053 Negative Smoke" .github/workflows/ci.yml`
Risks (if any): Over-tightening guards could accidentally skip expected governance checks on pull requests.

### [ ] Task 4 — Add deterministic WF-0047 status-alignment selector

Goal:
Add deterministic test coverage that enforces semantic status alignment across WF-0047 task/walkthrough/index artifacts.
Slice: wf0047-status-alignment-test
User Stories: US3
PRD Requirements: FR6
Depends on: 3
Enables: 5
Parallelizable: no
Files to modify:
- `backend/tests/scripts/test_ci_policy_event_scope.py`
Acceptance Criteria:
- Selector `wf0054_ci_policy_wf0047_status_alignment` deterministically validates WF-0047 task/walkthrough/index status semantics.
- Assertion output identifies which WF-0047 artifact field is mismatched.
TDD Plan:
- RED: Add `wf0054_ci_policy_wf0047_status_alignment` expecting failure against current WF-0047 status mismatch.
- GREEN: Implement minimal artifact-status parser/assertion helper in the test module to render deterministic mismatch diagnostics.
- REFACTOR: Centralize accepted completed-status semantics in one helper constant.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_wf0047_status_alignment"`
Risks (if any): Loose status parsing can mask drift if semantic equivalence rules are not explicit.

### [ ] Task 5 — WF-0047 artifact status consistency cleanup

Goal:
Normalize WF-0047 task/walkthrough/index statuses to consistent completed semantics required by WF-0054.
Slice: wf0047-status-alignment-fix
User Stories: US3
PRD Requirements: FR6
Depends on: 4
Enables: 6
Parallelizable: no
Files to modify:
- `docs/tasks/completed/task-WF-0047-git-hooks-rule-enforcement.md`
- `docs/walkthroughs/completed/walkthrough-WF-0047-git-hooks-rule-enforcement.md`
- `docs/index.md`
Acceptance Criteria:
- WF-0047 task artifact header status reflects completed semantics and matches walkthrough/index status intent.
- WF-0047 walkthrough header remains/updates to matching completed semantics.
- `docs/index.md` WF-0047 row status text remains semantically aligned with both artifacts.
TDD Plan:
- RED: Run `wf0054_ci_policy_wf0047_status_alignment` and confirm failure against pre-fix artifact state.
- GREEN: Update WF-0047 status fields and index row to satisfy the selector.
- REFACTOR: skip
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_wf0047_status_alignment"`
- `rg -n "WF-0047|Status: Completed|Status: Done" docs/tasks/completed/task-WF-0047-git-hooks-rule-enforcement.md docs/walkthroughs/completed/walkthrough-WF-0047-git-hooks-rule-enforcement.md docs/index.md`
Risks (if any): Historical status wording conventions may conflict with strict equality checks if not explicitly normalized.

### [ ] Task 6 — Branch-protection enforcement handoff mapping artifact

Goal:
Produce the explicit check mapping needed for a follow-on WF that handles GitHub branch protection enforcement.
Slice: branch-protection-handoff
User Stories: US4
PRD Requirements: FR7
Depends on: 5
Enables: 7
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0054-repo-ci-policy-hardening.md`
Acceptance Criteria:
- WF-0054 walkthrough includes a dedicated branch-protection mapping section.
- Mapping rows include `check_name`, `event_scope`, `enforcement_recommendation`, and `notes`.
- Mapping explicitly calls out repo-only boundary and references separate follow-on WF ownership for admin enforcement.
TDD Plan: N/A (documentation handoff contract)
Verification Steps:
- `rg -n "Branch Protection Handoff Mapping|check_name|event_scope|enforcement_recommendation|repo-only" docs/walkthroughs/walkthrough-WF-0054-repo-ci-policy-hardening.md`
Risks (if any): Missing event-scope caveats in mapping can cause incorrect required-check setup in the follow-on WF.

### [ ] Task 7 — Final governance regression sweep and walkthrough evidence

Goal:
Freeze deterministic verification evidence for repo-side policy hardening without expanding to admin settings.
Slice: verification-and-evidence
User Stories: US1, US2, US3, US4
PRD Requirements: FR4, FR5, FR6, FR7, FR8, FR9
Depends on: 6
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0054-repo-ci-policy-hardening.md`
- `.github/workflows/ci.yml`
Acceptance Criteria:
- CI backend lane runs deterministic WF-0054 selectors with explicit command(s) and stable failure text.
- Walkthrough records verification evidence for PR-vs-push tests, WF-0047 status alignment check, and branch-protection handoff completion.
- No GitHub branch protection admin/config changes are introduced in this WF.
TDD Plan:
- RED: Add/keep failing WF-0054 regression selector invocation until missing selectors are wired in CI.
- GREEN: Wire deterministic selector command(s) in CI and record resulting evidence in walkthrough.
- REFACTOR: Trim duplicate CI test command fragments while preserving clear WF-0054 scope visibility.
Verification Steps:
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_"`
- `rg -n "wf0054_ci_policy_|repo-only|branch protection" .github/workflows/ci.yml docs/walkthroughs/walkthrough-WF-0054-repo-ci-policy-hardening.md`
Risks (if any): Broad selector patterns could hide missing-case coverage if not kept WF-specific.

## Changelog

- v0.1 (2026-03-05): Initial task breakdown from PRD
- v0.2 (2026-03-05): Applied review edits by splitting WF-0047 test-vs-doc alignment into separate atomic tasks, removing self-editing task coupling, and marking plan Ready for Implementation
- v0.3 (2026-03-05): Adversarial Part B re-audit completed; confirmed blocker-free plan and retained task structure
