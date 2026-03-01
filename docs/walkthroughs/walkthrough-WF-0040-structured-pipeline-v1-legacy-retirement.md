# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: walkthrough
Version: v0.1
Status: In progress
Last Updated: 2026-03-01

---

## Legacy Retirement Readiness Checklist (SSOT)

Use this checklist as the gate before deleting legacy execution-path code.

- [ ] Scope boundary confirmed: WF-0040 covers only legacy engine execution for `POST /api/structured-review`.
- [ ] API contract invariants listed in PRD Section 5 are covered by tests and passing.
- [ ] Replay/parity evidence artifact exists and is linked.
- [ ] Rollout health output exists and is linked.
- [ ] Staging observation window passed:
  - [ ] `pipeline_v1` only routing active.
  - [ ] 24 consecutive green hours.
- [ ] Production observation window passed:
  - [ ] `pipeline_v1` only routing active.
  - [ ] 7 consecutive green days.
  - [ ] Minimum 50 completed requests per currently-supported call code.
- [ ] No contract-semantic regression in invariant errors (`CALL_CONFIG_DIGEST_MISMATCH`, `EXPECTATION_REF_UNRESOLVABLE`, timeout classification, validation ordering behavior).
- [ ] Rollback runbook validated in pre-delete posture (config-first while legacy code exists).
- [ ] Explicit owner approval recorded (tech lead/repo owner sign-off).

## Evidence Links

- Replay/parity artifact: TODO
- Rollout health output: TODO
- API contract test run: TODO
- Approval record: TODO
