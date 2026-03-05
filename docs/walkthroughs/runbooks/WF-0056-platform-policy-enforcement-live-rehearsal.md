# WF-0056 Runbook — Platform Policy Enforcement Live Rehearsal

Artifact: runbook
Version: v1.0
Status: Active
Last Updated: 2026-03-05

## Purpose
Run a live rehearsal chain for `verify -> apply -> rollback` with deterministic evidence on `main` (verify) and `policy-rehearsal` (mutation).

## Preflight
- Confirm branch targets:
  - `verify` uses `main`
  - `apply` and `rollback` use `policy-rehearsal`
- Confirm token scope allows read/mutate policy endpoints.
- Confirm expected policy file exists: `config/platform_policy/main_policy.yaml`.
- Confirm evidence directory exists: `docs/walkthroughs/evidence/WF-0056/`.

## Command Sequence
- Verify live policy drift on `main`:
  - `cd backend && uv run python -m tools.gh_policy.cli verify --repo <owner/repo> --branch main --verify-only --evidence-path ../docs/walkthroughs/evidence/WF-0056/tracer_verify_evidence.json`
- Apply expected policy on `policy-rehearsal`:
  - `cd backend && uv run python -m tools.gh_policy.cli apply --repo <owner/repo> --branch policy-rehearsal --apply-intent --evidence-path ../docs/walkthroughs/evidence/WF-0056/apply_evidence.json --snapshot-dir ../docs/walkthroughs/evidence/WF-0056/snapshots`
- Roll back using explicit snapshot-path input:
  - `cd backend && uv run python -m tools.gh_policy.cli rollback --repo <owner/repo> --branch policy-rehearsal --snapshot-path ../docs/walkthroughs/evidence/WF-0056/snapshots/<snapshot.json> --evidence-path ../docs/walkthroughs/evidence/WF-0056/rollback_evidence.json`

## Failure Handling by `error.kind`
- `permission_denied`: token/actor lacks required permission; stop mutation and rotate token/permissions.
- `plan_gated`: endpoint unavailable for repository/account plan; do not retry mutation blindly.
- `missing_required_checks`: preflight discovered missing check contexts; fix CI context surface first.
- `api_failure`: transient or hard API/runtime fault; inspect endpoint and retry only after diagnosis.
- `post_apply_mismatch`: apply completed but parity check failed; inspect diff and prepare rollback.
- `restore_mismatch`: rollback restore parity check failed; escalate and avoid further mutation.

## Evidence Requirements
Each verify/apply/rollback evidence file must include:
- `evidence_sha256`
- `workflow_run_id`
- `commit_sha`
- `linked_artifacts`
- `error.kind`
