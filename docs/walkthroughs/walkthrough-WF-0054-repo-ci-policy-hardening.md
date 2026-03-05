# WF-0054 — Repo-side CI Policy Hardening

Artifact: walkthrough
Version: v1.0
Status: Draft
Last Updated: 2026-03-05

## Scope Boundary
This workflow is repo-only and intentionally excludes GitHub branch protection admin configuration changes.
Branch protection enforcement ownership is handed off to a dedicated follow-on workflow.

## Branch Protection Handoff Mapping
| check_name | event_scope | enforcement_recommendation | notes |
| :--- | :--- | :--- | :--- |
| Contract Boundary Governance Check | pull_request_only | Required check on `pull_request` in follow-on branch protection WF | PR-dependent governance check; intentionally skipped on push-to-main |
| WF-0053 Negative Smoke (Expected Fail-Closed) | pull_request_only | Optional informational check in follow-on WF; keep non-blocking unless policy mandates | Fail-closed validation step designed for PR governance surface only |
| Contract Gate (Marker) | push_safe | Required on both `pull_request` and `push` where required-check policy allows | Push-safe contract marker can be enforced consistently across events |
| Test (Pytest no_db) | push_safe | Required on both `pull_request` and `push` in branch protection policy | Deterministic no-DB test lane suitable for broad enforcement |

## Follow-on Ownership
A separate workflow (new WF, outside WF-0054 scope) must execute GitHub admin branch protection updates using this mapping.
