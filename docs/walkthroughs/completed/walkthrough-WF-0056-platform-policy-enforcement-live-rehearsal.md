# WF-0056 — Platform Policy Enforcement Live Rehearsal

Artifact: walkthrough
Version: v1.2
Status: Done (Waiver-backed)
Last Updated: 2026-03-06

## Summary
Implemented live rehearsal workflow coverage and safety contracts for verify/apply/rollback flows, with deterministic evidence schema/linkage and CI regression selectors.

## Evidence Chain (verify -> apply -> rollback)
| Operation | Evidence Link | Evidence Checksums | Snapshot Checksums | workflow_run_id | run URL | commit_sha | linked_artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| verify-main | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#verify-main` | `evidence_sha256=0de58e3d9bd6ecc0b05e85a565b70559ebb4231bf158b87941cbb7fa167d098c` | N/A | `22751018925` | `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925` | `97aab2008c4c5aa33da016af87c333fc7c541145` | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#verify-main` |
| apply-rehearsal | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#apply-rehearsal` | `evidence_sha256=5a7b47ecb17fba138fba3598036a7522c4dedc16725c8e3975b8f04b9ca4ef20` | `snapshot_sha256=dc40036c1f884fb2ab2b29495acfd4c18df2f3b191eb894a57e6c0fdce16aeef` | `22751018925` | `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925` | `97aab2008c4c5aa33da016af87c333fc7c541145` | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#apply-rehearsal` |
| rollback-rehearsal | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#rollback-rehearsal` | `evidence_sha256=7910bd5a97fdc96182efd66aac053fdee3f278566d2800920368cdac63173748` | `source snapshot checksum=dc40036c1f884fb2ab2b29495acfd4c18df2f3b191eb894a57e6c0fdce16aeef` | `22751018925` | `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925` | `97aab2008c4c5aa33da016af87c333fc7c541145` | `docs/walkthroughs/evidence/WF-0056/live-run-index.md#rollback-rehearsal` |

## Stub Evidence Policy
Static or stub evidence is invalid for WF-0056 completion. Final completion requires live-generated verify/apply/rollback artifacts with real `workflow_run_id`, run URL, and `commit_sha` fields.

## Rollback Waiver Record (2026-03-06)

- waived gate: rollback artifact retrieval and upload proof chain for the rehearsal rollback job.
- constraint: rollback snapshot artifact download failed in the live run context (`Artifact not found for name: wf-0056-apply-snapshot`), so rollback evidence file upload path did not resolve.
- residual risk: rollback execution evidence remains failure-state metadata only; replayable success-path rollback artifact proof is still missing.
- owner sign-off: repo owner (chat approval), dated `2026-03-06`.
- source: `docs/walkthroughs/evidence/WF-0056/live-run-index.md#rollback-rehearsal`.

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
