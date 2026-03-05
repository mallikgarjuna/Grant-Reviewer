# WF-0055 — Platform Policy Enforcement

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-05

## Executive Summary
Implemented end-to-end platform policy tooling for verify/apply/rollback with deterministic evidence, policy schema validation, normalization + diff logic, and CI verify-only wiring.

## What Changed
- Added `backend/tools/gh_policy/` implementation modules:
  - `cli.py`, `evidence.py`, `policy_schema.py`, `github_client.py`
  - `normalizer.py`, `diff.py`, `verify.py`, `apply.py`, `snapshot.py`, `rollback.py`
- Added WF-0055 tests under `backend/tests/tools/gh_policy/`:
  - tracer verify evidence test
  - policy schema tests
  - live read/fallback/error mapping tests
  - normalization/diff parity tests
  - verify drift/non-mutation tests
  - apply preflight and post-apply verification tests
  - rollback restore mismatch evidence test
- Added PR verify-only workflow: `.github/workflows/verify-platform-policy.yml`
- Updated CI selector sweep to include WF-0055 policy checks:
  - `.github/workflows/ci.yml`
  - `backend/tests/scripts/test_ci_policy_event_scope.py`
- Added operations runbook:
  - `docs/walkthroughs/runbooks/WF-0055-platform-policy-enforcement.md`

## Verification Evidence
- Baseline preflight:
  - `cd backend && uv run pytest -m no_db` -> pass (`183 passed, 118 deselected`).
- Task-level verification:
  - `cd backend && uv run pytest tests/tools/gh_policy/test_verify_tracer.py -k "writes_evidence_json"` -> pass.
  - `cd backend && uv run pytest tests/tools/gh_policy/test_policy_schema.py` -> pass.
  - `cd backend && uv run pytest tests/tools/gh_policy/test_github_client_read.py` -> pass.
  - `cd backend && uv run pytest tests/tools/gh_policy/test_normalizer_diff.py` -> pass.
  - `cd backend && uv run pytest tests/tools/gh_policy/test_verify_command.py` -> pass.
  - `cd backend && uv run pytest tests/tools/gh_policy/test_apply_preflight.py` -> pass.
  - `cd backend && uv run pytest tests/tools/gh_policy/test_apply_command.py` -> pass.
  - `cd backend && uv run pytest tests/tools/gh_policy/test_rollback_command.py` -> pass.
  - `cd backend && uv run pytest tests/scripts/test_ci_policy_event_scope.py -k "platform_policy or wf0055"` -> pass.
- CLI entrypoint verification:
  - `cd backend && uv run python -m tools.gh_policy.cli verify --help` -> pass.
  - `cd backend && uv run python -m tools.gh_policy.cli apply --help` -> pass.
  - `cd backend && uv run python -m tools.gh_policy.cli rollback --help` -> pass.

## Risks and Follow-up Notes
- GitHub network/API integration is currently fixture-driven/offline in tests; live endpoint integration should be validated with an admin token before production enforcement.
- Evidence file naming in CLI defaults is deterministic and writable in repo context; CI artifact collection policy should retain these outputs for audit traceability.
