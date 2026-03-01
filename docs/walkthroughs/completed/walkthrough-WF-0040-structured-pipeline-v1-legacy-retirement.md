# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-03-01

---

## Legacy Retirement Readiness Checklist (SSOT)

Use this checklist as the gate before deleting legacy execution-path code.

- [x] Scope boundary confirmed: WF-0040 covers only legacy engine execution for `POST /api/structured-review`.
- [x] API contract invariants listed in PRD Section 5 are covered by tests and passing.
- [ ] Replay/parity evidence artifact exists and is linked.
- [ ] Rollout health output exists and is linked.
- [ ] Staging observation window passed:
  - [ ] `pipeline_v1` only routing active.
  - [ ] 24 consecutive green hours.
- [ ] Production observation window passed:
  - [ ] `pipeline_v1` only routing active.
  - [ ] 7 consecutive green days.
  - [ ] Minimum 50 completed requests per currently-supported call code.
- [x] No contract-semantic regression in invariant errors (`CALL_CONFIG_DIGEST_MISMATCH`, `EXPECTATION_REF_UNRESOLVABLE`, timeout classification, validation ordering behavior).
- [x] Rollback runbook validated in pre-delete posture (config-first while legacy code exists).
- [ ] Explicit owner approval recorded (tech lead/repo owner sign-off).

## Evidence Links

- Replay/parity artifact: `backend/artifacts/rollout/replay_canary.json` (existing rollout artifact; refresh before deletion decision).
- Rollout health output: run `cd backend && uv run python scripts/evaluate_rollout_health.py --input artifacts/rollout/replay_canary.json` and archive JSON output with required checks (`staging_window_ok`, `prod_window_ok`, `prod_sample_size_ok`, `overall.recommended_action`).
- API contract test run:
  - `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t2.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py -k "idempotency or digest or expectation or timeout or validation"` (pass in this phase).
  - `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t6.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py tests/test_rollout_health.py` (pass in this phase).
  - `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_c2.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py tests/test_rollout_health.py tests/test_structured_reviewer_service.py` (pass: `92 passed`).
- Implementation commits:
  - `b86b6de` Task 1 (v1-only routing tracer bullet).
  - `9e27515` Task 2 (API invariant coverage + timeout message stability).
  - `78e2382` Task 3 (retirement-gate thresholds in rollout health evaluator).
  - `5022b0a` Task 4 (legacy execution entrypoint removal).
  - `ed382cf` Task 5 (dual-routing env logic removal + runbook update).
  - `8d61957` Task 6 (operational readiness and evidence handoff).
  - `346e38b` Phase 2 delta closure (aggregate verification gate in task plan).
  - `b89083a` Phase 1 delta closure (gate defaults and checklist baseline).
  - `42cc983` Phase 2 atomic task-plan finalization.

## Implementation Summary

- Runtime path for `POST /api/structured-review` is now v1-only; dual-engine route selection branches were removed.
- Legacy execution entrypoint `StructuredReviewerService.generate_structured_review` was removed; API tests now guard against reintroduction.
- API contract-invariant coverage was expanded for digest mismatch, expectation unresolvable, timeout classification, and validation-order behavior.
- Rollout-health evaluator now supports retirement gate checks (`24h` staging, `7d` production, `>=50` completed requests per supported call).
- Backend operator docs were updated to pre-delete config-first rollback posture and post-delete revert-deploy-only posture.

## Part B Audit Fixes (Phase 3.3 C1)

- Blocking audit finding addressed: `tests/test_structured_reviewer_service.py` still referenced removed legacy entrypoint and failed.
- File was revised to pipeline_v1-only service tests aligned to WF-0040 scope and contracts.
- Post-fix regression evidence: `92 passed` in combined API + pipeline + rollout + structured service test run.

## Remaining Risks

- Deletion approval remains blocked until staging/prod observation windows and per-call production sample thresholds are recorded with fresh artifacts.
- Tech lead/repo owner sign-off is still pending in Approval Record.

## Approval Record

- Owner (tech lead/repo owner): TODO
- Decision: TODO (`approve deletion gate` / `hold`)
- Date: TODO
- Notes: TODO
