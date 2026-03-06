# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: walkthrough
Version: v1.4
Status: Complete (Waived Gate Closure)
Last Updated: 2026-03-06

---

## Legacy Retirement Readiness Checklist (SSOT)

Use this checklist as the gate before deleting legacy execution-path code.

- [x] Scope boundary confirmed: WF-0040 covers only legacy engine execution for `POST /api/structured-review`.
- [x] API contract invariants listed in PRD Section 5 are covered by tests and passing.
- [x] Replay/parity evidence artifact exists and is linked.
- [x] Rollout health output exists and is linked.
- [ ] Staging observation window passed:
  - [ ] `pipeline_v1` only routing active.
  - [ ] 24 consecutive green hours.
- [ ] Production observation window passed:
  - [ ] `pipeline_v1` only routing active.
  - [ ] 7 consecutive green days.
  - [ ] Minimum 50 completed requests per currently supported call code.
- [x] No contract-semantic regression in invariant errors (`CALL_CONFIG_DIGEST_MISMATCH`, `EXPECTATION_REF_UNRESOLVABLE`, timeout classification, validation ordering behavior).
- [x] Rollback runbook validated in pre-delete posture (config-first while legacy code exists).
- [ ] Explicit owner approval recorded (tech lead/repo owner sign-off).
- [x] Waiver-based closure recorded with explicit residual risks and follow-up backlog item.

## Evidence Links

- Replay/parity artifact: `backend/artifacts/rollout/wf0040_replay_canary_2026-03-01.json` (fresh local replay artifact generated in corrective pass).
- Rollout health output: `backend/artifacts/rollout/wf0040_rollout_health_2026-03-01.json` from `cd backend && uv run python scripts/evaluate_rollout_health.py --input artifacts/rollout/wf0040_health_input_2026-03-01.json --require-retirement-gate`.
- API contract test run:
  - `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t2.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py -k "idempotency or digest or expectation or timeout or validation"` (pass in this phase).
  - `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_t6.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py tests/test_rollout_health.py` (pass in this phase).
  - `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_c2.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py tests/test_rollout_health.py tests/test_structured_reviewer_service.py` (pass: `92 passed`).
  - `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_wf0040_fixfull.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py tests/test_rollout_health.py tests/test_structured_reviewer_service.py` (adversarial-fix pass: `93 passed`).
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

## Adversarial Corrective Pass (Post-Phase-3)

- Restored stable `check_id` taxonomy (`check.presence`) for pipeline expectations and fixed validator identity semantics so same `check_id` across different expectations is valid.
- Re-opened WF status from `Done` to `Phase 3 (Gate Pending)` and moved WF artifacts back to active paths to match unchecked approval/evidence gates.
- Removed stale call-level routing toggle references in call-yaml runtime docs.

## Gate Closure Mode

- WF-0040 is closed via documented waiver because required staging/production observation evidence and per call production counts are unavailable in the current environment.
- This closure confirms implementation completion and verification evidence only; it does **not** claim production observation-window validation.
- A follow-up backlog item is required before public-launch hardening/scale commitments.

## WF-0057 Closure Path Decision (Owner-Gated)

- Chosen path: `waiver refresh` (not runtime evidence backfill).
- Decision date: `2026-03-06`.
- Owner sign-off location: `docs/logs/decisions.md` (Date: `2026-03-06`, WF-0057 entry `AD 57.3`).
- Why runtime backfill was not used in this run:
  - no deterministic access to staging/production telemetry windows in this execution environment,
  - no reproducible per call production count extracts available from repo-local artifacts alone.

## Waiver Refresh Record (2026-03-06)

- waived gate 1: staging runtime window (`24` consecutive green hours on `pipeline_v1`).
- waived gate 2: production runtime window (`7` consecutive green days on `pipeline_v1`).
- waived gate 3: minimum production volume (`50` completed requests per currently supported call code).
- constraint: this repo-only run cannot access deterministic staging/production telemetry or queryable production event counts.
- residual risk: runtime routing incidents could remain undetected until external telemetry backfill is completed.
- owner sign-off: repo owner (chat approval), dated `2026-03-06`.

## Remaining Risks

- Staging/prod observation windows and per call production sample thresholds remain unproven and must be backfilled in a follow-up WF.
- Current replay/health artifacts are local simulated evidence; they are not substitutes for real environment evidence.
- If runtime incidents occur, fallback is operational rollback posture documented in backend runbook updates from this WF.

## Workflow Status Clarification

- WF-0040 implementation tasks are complete and workflow closure is recorded as waiver-based.
- `docs/index.md` now tracks this WF as `Done` with artifacts archived under `completed/`.

## Approval Record

- Owner (tech lead/repo owner): Repo owner (chat approval)
- Decision: `waive-gate-close` (accept residual risk, close WF artifacts, track evidence backfill as follow-up)
- Date: 2026-03-01
- Notes: Missing staging/prod observation-window evidence + per call production counts acknowledged; closure allowed for MVP momentum with explicit follow-up backlog item.
