# WF-0054 — Repo-side CI Policy Hardening

Artifact: walkthrough
Version: v1.1
Status: Completed
Last Updated: 2026-03-05

## Executive Summary
Implemented deterministic repo-side CI-policy governance checks for pull_request vs push behavior, added WF-0047 artifact-status alignment enforcement, and prepared explicit handoff mapping for branch protection admin enforcement in a separate workflow.

## Scope Boundary
This workflow is repo-only and intentionally excludes GitHub branch protection admin configuration changes.
Branch protection enforcement ownership is handed off to a dedicated follow-on workflow.

## What Changed
- Added governed-step inventory and deterministic evaluator in `backend/scripts/ci_policy_inventory.py`.
- Added deterministic WF-0054 selector tests in `backend/tests/scripts/test_ci_policy_event_scope.py`:
  - `wf0054_ci_policy_inventory_pr_only_tracer`
  - `wf0054_ci_policy_event_scope_pr_positive`
  - `wf0054_ci_policy_event_scope_push_negative`
  - `wf0054_ci_policy_negative_removed_pr_guard_fails`
  - `wf0054_ci_policy_wf0047_status_alignment`
- Hardened CI backend lane to run deterministic WF-0054 selector sweep via:
  - `uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_"`
- Normalized WF-0047 status semantics across task/walkthrough/index artifacts.

## Verification Evidence
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_"` -> pass (all WF-0054 selectors).
- `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "wf0054_ci_policy_wf0047_status_alignment"` -> pass after WF-0047 status cleanup.
- `rg -n "if: github.event_name == 'pull_request'|Contract Boundary Governance Check|WF-0053 Negative Smoke" .github/workflows/ci.yml` -> confirms explicit PR guards on PR-dependent governed checks.
- `rg -n "wf0054_ci_policy_|repo-only|branch protection" .github/workflows/ci.yml docs/walkthroughs/walkthrough-WF-0054-repo-ci-policy-hardening.md` -> confirms CI selector wiring and repo-only branch-protection handoff language.

## Branch Protection Handoff Mapping
| check_name | event_scope | enforcement_recommendation | notes |
| :--- | :--- | :--- | :--- |
| Contract Boundary Governance Check | pull_request_only | Required check on `pull_request` in follow-on branch protection WF | PR-dependent governance check; intentionally skipped on push-to-main |
| WF-0053 Negative Smoke (Expected Fail-Closed) | pull_request_only | Optional informational check in follow-on WF; keep non-blocking unless policy mandates | Fail-closed validation step designed for PR governance surface only |
| Contract Gate (Marker) | push_safe | Required on both `pull_request` and `push` where required-check policy allows | Push-safe contract marker can be enforced consistently across events |
| Test (Pytest no_db) | push_safe | Required on both `pull_request` and `push` in branch protection policy | Deterministic no-DB test lane suitable for broad enforcement |

## Follow-on Ownership
A separate workflow (new WF, outside WF-0054 scope) must execute GitHub admin branch protection updates using this mapping.
