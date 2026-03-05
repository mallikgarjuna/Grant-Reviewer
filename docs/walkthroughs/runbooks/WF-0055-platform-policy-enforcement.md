# WF-0055 Runbook — Platform Policy Enforcement

Artifact: runbook
Version: v1.0
Status: Active
Last Updated: 2026-03-05

## Purpose
Operate verify/apply/rollback flows for `main` platform policy enforcement with deterministic evidence.

## Prerequisites Matrix
| Operation | Required Inputs | Required Permission | Mutation |
| :--- | :--- | :--- | :--- |
| verify | repo, branch, expected policy file | `GITHUB_TOKEN` for live mode read access | no |
| apply | repo, branch, expected policy file, apply intent, check contexts present | admin mutation permission | yes |
| rollback | repo, branch, snapshot artifact | admin mutation permission | yes |

## Commands
- Verify (CI-safe, verify-only):
  - `cd backend && uv run python -m tools.gh_policy.cli verify --repo <owner/repo> --branch main --verify-only`
- Verify (local deterministic/offline mode):
  - `cd backend && uv run python -m tools.gh_policy.cli verify --repo <owner/repo> --branch main --verify-only --offline`
- Apply (explicit intent required):
  - `cd backend && uv run python -m tools.gh_policy.cli apply --repo <owner/repo> --branch main --apply-intent`
- Rollback (snapshot-driven restore):
  - `cd backend && uv run python -m tools.gh_policy.cli rollback --repo <owner/repo> --branch main --snapshot-path <snapshot.json>`

## Evidence and Snapshot Contracts
- Evidence JSON path pattern:
  - `docs/walkthroughs/evidence/WF-0055/branch-protection_<repo>_<branch>_<utc-timestamp>.json`
- Snapshot path pattern:
  - `docs/walkthroughs/evidence/WF-0055/snapshots/snapshot_<repo>_<branch>_<utc-timestamp>.json`
- Snapshot payload includes deterministic `snapshot_sha256`.
- Verify/apply/rollback evidence includes deterministic `evidence_sha256`.

## Deterministic Failure Interpretation
- `plan_gated`: GitHub plan does not permit rulesets/protection endpoint usage.
- `permission_denied`: token/actor lacks required policy mutation permissions.
- `missing_required_checks`: required check contexts are not all present in CI surface.
- `post_apply_mismatch`: mutation ran but post-apply verification still drifted.
- `restore_mismatch`: rollback restore did not match snapshot on post-read.
- `api_unreachable`: request/mutation path threw API/runtime error.

## Required Check Contexts (Contracted)
- `backend / Contract Boundary Governance Check`
- `backend / WF-0054 CI Policy Regression Sweep`
- `backend / Contract Gate (Marker)`
- `backend / Test (Pytest no_db)`
- `frontend / Lint`
- `frontend / Build`
