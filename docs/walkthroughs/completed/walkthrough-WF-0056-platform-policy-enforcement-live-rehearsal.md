# WF-0056 — Platform Policy Enforcement Live Rehearsal

Artifact: walkthrough
Version: v1.1
Status: Done
Last Updated: 2026-03-05

## Summary
Implemented live rehearsal workflow coverage and safety contracts for verify/apply/rollback flows, with deterministic evidence schema/linkage and CI regression selectors.

## Evidence Chain (verify -> apply -> rollback)
| Operation | Evidence Link | Evidence Checksums | Snapshot Checksums | workflow_run_id | run URL | commit_sha | linked_artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| verify-main | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#verify-main` | `evidence_sha256=4300ab4c1d431a47c34a1e5011aed542f276480becfd8af3431199ed431bdc80` | N/A | `22751018925` | `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925` | `97aab2008c4c5aa33da016af87c333fc7c541145` | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#verify-main` |
| apply-rehearsal | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#apply-rehearsal` | `evidence_sha256=c38e899015690a0e6f2ee67d32f4ce0861701910b41c1019642eba06c5f6faf0` | `snapshot_sha256=dc40036c1f884fb2ab2b29495acfd4c18df2f3b191eb894a57e6c0fdce16aeef` | `22751018925` | `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925` | `97aab2008c4c5aa33da016af87c333fc7c541145` | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#apply-rehearsal` |
| rollback-rehearsal | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#rollback-rehearsal` | `evidence_sha256=fa3b0b1f5f10546ad565c3af2cda0bd05e3306f8a0e8c56c3982b427d794b182` | `source snapshot checksum=dc40036c1f884fb2ab2b29495acfd4c18df2f3b191eb894a57e6c0fdce16aeef` | `22751018925` | `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925` | `97aab2008c4c5aa33da016af87c333fc7c541145` | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#rollback-rehearsal` |

## Stub Evidence Policy
Static or stub evidence is invalid for WF-0056 completion. Final completion requires live-generated verify/apply/rollback artifacts with real `workflow_run_id`, run URL, and `commit_sha` fields.

## Runbook
- `docs/walkthroughs/runbooks/WF-0056-platform-policy-enforcement-live-rehearsal.md`

## Verification Notes
- Workflow selectors cover:
  - `wf0056_live_rehearsal_verify_tracer_contract`
  - `wf0056_live_rehearsal_apply_contract`
  - `wf0056_live_rehearsal_safety_gates`
- CI backend lane executes WF-0056 selector gate via `tests/scripts/test_ci_policy_event_scope.py`.
- Final verify gate (Part C2):
  - `pre-commit run --all-files` -> pass
  - `cd backend && uv run pytest -m no_db` -> pass (`214 passed, 118 deselected`)
