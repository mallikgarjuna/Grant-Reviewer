# WF-0054 — Repo-side CI Policy Hardening

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-05

## 0. User Stories (MVP)

- US1: As a maintainer, I want CI governance checks to run only in valid event contexts, so that merges are gated correctly without false failures on `push`.
- US2: As a maintainer, I want deterministic CI-policy tests for `pull_request` vs `push`, so that policy regressions are caught immediately.
- US3: As a maintainer, I want WF-0047 artifact status fields aligned across task/walkthrough/index, so that human and automation status interpretation is consistent.
- US4: As a maintainer, I want a clear handoff contract for a separate branch-protection WF, so that repo policy and GitHub admin enforcement are cleanly separated.

## Deferred Stories (Not in MVP)

- DS1: As a maintainer, I want automated GitHub branch protection settings enforcement, so that required checks are centrally managed.

## 1. In Scope

- Repo-side CI policy hardening only (no GitHub admin/branch protection changes). (US1, US2, US4)
- Deterministic tests validating PR-vs-push governance behavior for `.github/workflows/ci.yml`. (US1, US2)
- Explicit governance classification: PR-dependent vs push-safe checks. (US1, US2)
- WF-0047 artifact status consistency cleanup in `docs/index.md`, task artifact, and walkthrough artifact. (US3)
- Branch-protection handoff mapping artifact for follow-on WF. (US4)

## 2. Out of Scope

- Editing GitHub repository branch protection settings or required checks. (DS1)
- Large CI architecture redesign beyond governance event-scoping hardening. (US1)
- General historical WF status normalization outside WF-0047. (US3)

## 3. User / System Flow

Happy path:
1. Maintainer opens PR that changes governance-sensitive surfaces; CI runs on `pull_request`. (US1)
2. PR-dependent governance checks run only for `pull_request` and produce deterministic pass/fail outcomes. (US1, US2)
3. CI policy tests validate event-scoping invariants and fail if PR-only checks can run on `push`. (US2)
4. Maintainer merges PR; `push` CI on `main` runs only push-safe checks. (US1)
5. WF-0047 status artifacts show consistent completed state. (US3)
6. Maintainer uses branch-protection handoff mapping to open follow-on enforcement WF. (US4)

Failure paths:
- FP1: A PR-dependent governance step loses PR-only guard; CI-policy tests fail before merge. (US1, US2)
- FP2: A contributor modifies CI and unintentionally scopes governance to `push`; deterministic negative test fails. (US2)
- FP3: WF-0047 status mismatch persists after update; status consistency verification fails and blocks completion. (US3)

## 4. Functional Requirements

- FR1 (US1): CI policy must explicitly classify governance checks as PR-dependent or push-safe.
- FR2 (US1, US2): PR-dependent governance checks must be gated to `pull_request` only.
- FR3 (US1): `push` to `main` CI execution must exclude PR-dependent governance checks.
- FR4 (US2): Deterministic CI-policy tests must assert `pull_request` vs `push` behavior for governance checks.
- FR5 (US2): CI-policy tests must include at least one negative regression assertion proving fail behavior when PR-only gating is removed.
- FR6 (US3): WF-0047 task, walkthrough, and `docs/index.md` status values must be aligned to completed/done semantics.
- FR7 (US4): Workflow artifacts must include a branch-protection handoff mapping of relied-on checks to future required-check configuration targets.
- FR8 (US1, US2): CI-policy tests must avoid dependence on live GitHub admin settings and remain repo-deterministic.
- FR9 (US2): Governed CI step identities under policy must be explicit and stable so tests fail on missing/renamed governed steps.

## 5. Data & API Contracts

- CI policy contract representation (US1, US2) (FR1, FR2, FR3):
  - Source of truth: `.github/workflows/ci.yml` with explicit `if` event guards for PR-dependent checks.
  - Contract dimensions:
    - `event_scope`: `pull_request` or `push`
    - `governance_class`: `pr_dependent` or `push_safe`
    - `required_guard`: expression proving PR-only gating for PR-dependent checks
- CI-policy test assertions (US2) (FR4, FR5, FR8):
  - Deterministic parser/assertion logic over workflow YAML structure (AST-first; avoid brittle string-only matching).
  - Stable check identifiers for governed steps to avoid brittle name drift.
  - Negative assertion must fail if PR-dependent step is executable on `push`.
- Governed step identity contract (US2) (FR9):
  - PRD/tasks must define a single governed-step inventory for this WF, referenced by tests.
  - Inventory updates are explicit and reviewed; missing inventory IDs in CI YAML must fail tests.
- WF artifact status contract (US3) (FR6):
  - WF-0047 task status header value must represent completed state.
  - WF-0047 walkthrough status and index row must agree with task status semantics.
- Branch-protection handoff contract (US4) (FR7):
  - Target location: `docs/walkthroughs/walkthrough-WF-0054-repo-ci-policy-hardening.md` under a dedicated section for branch-protection mapping.
  - Mapping schema:
    - `check_name`
    - `event_scope`
    - `enforcement_recommendation` (future required-check candidate)
    - `notes`

## 6. Components / Modules

- `.github/workflows/ci.yml`
  - Holds event triggers and per-step `if` conditions.
  - Primary policy target for scope hardening.
- `scripts/check_contract_boundary_governance.py` (or adjacent policy-check script surface)
  - Maintains governance check logic used in CI.
  - Must preserve PR-only assumptions for PR-dependent paths.
- CI-policy tests (existing or new tests module under repo test suite)
  - Validates event-scoping invariants deterministically.
  - Includes explicit negative regression test case(s).
- WF documentation artifacts:
  - `docs/index.md`
  - `docs/tasks/completed/task-WF-0047-git-hooks-rule-enforcement.md`
  - `docs/walkthroughs/completed/walkthrough-WF-0047-git-hooks-rule-enforcement.md`
  - Enforce status consistency contract for WF-0047.
- Branch-protection handoff artifact
  - Produced in WF-0054 walkthrough/tasks output as explicit mapping for follow-on WF.

Design tree (dependencies + ordering):
1. Define policy contract + event-scope invariants.
2. Add deterministic CI-policy tests.
3. Harden CI workflow gating to satisfy tests.
4. Align WF-0047 artifact statuses.
5. Produce branch-protection handoff mapping.

## 7. Edge Cases

- EC1: Governance step renamed in CI YAML; tests should detect missing expected governed step IDs instead of silently passing. (US2)
- EC2: Workflow has mixed `if` conditions with reusable expressions; parser must still determine effective PR-only gating. (US2)
- EC3: `push` trigger changes from `main` to broader patterns; tests must remain explicit about allowed behavior per trigger. (US1, US2)
- EC4: WF-0047 status word variants (`Done` vs `Completed`) differ by artifact; validation must enforce semantic alignment for that WF. (US3)
- EC5: Branch-protection handoff includes a check that is push-only; mapping must indicate event-scope caveat for future required-check configuration. (US4)

## 8. Testing Decisions (TDD)

- TDD scope:
  - Behavior changes to CI policy gating and WF-0047 status consistency must be test-first where practical.
- Test seams (public interfaces):
  - Workflow-policy assertion helpers against `.github/workflows/ci.yml`.
  - Governance script invocation contract for PR-vs-push assumptions.
  - Artifact-status consistency check for WF-0047 docs alignment.
- Boundary mocking:
  - No live GitHub API or branch protection admin dependencies.
  - Use static fixtures or checked-in workflow/doc files for deterministic tests.
- Minimum tests per requirement:
  - FR2/FR3/FR4: positive event-scope assertions for PR-only governance and push-safe execution.
  - FR5: negative regression test proving failure when PR guard is removed/missing.
  - FR6: status alignment assertion over WF-0047 task/walkthrough/index artifacts.
  - FR7: handoff mapping presence/shape validation in produced artifact.
  - FR9: missing/renamed governed step ID assertion fails deterministically.
  - Deterministic selector convention for WF-0054 CI policy tests: `wf0054_ci_policy_<surface>_<case_id>`.

## 9. Telemetry (Minimal)

- CI logs include clear pass/fail reason for each policy invariant check.
- Deterministic error text for event-scope violations (step ID + expected scope).
- Status-alignment check output points to mismatched artifact field(s).

## 10. Deferred / Not in MVP

- GitHub branch protection settings enforcement automation (separate WF).
- Repo-wide historical status normalization beyond WF-0047.
- Generic CI policy framework reusable across repositories.

## 11. Open Questions (if any)

- OQ1: Should any currently PR-dependent governance check be duplicated as a reduced push-safe variant in future iterations?

## 12. Changelog

- v0.1 (2026-03-05): Initial PRD from brainstorm
- v0.2 (2026-03-05): Applied risk-audit revisions (stable governed-step IDs, AST-first test contract, explicit handoff artifact location); marked Ready for Tasks
