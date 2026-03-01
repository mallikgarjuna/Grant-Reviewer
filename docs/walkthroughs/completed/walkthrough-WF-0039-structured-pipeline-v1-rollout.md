# WF-0039 — Structured Pipeline v1 Rollout

Artifact: walkthrough
Version: v0.1
Status: Complete
Last Updated: 2026-03-01

## Overview

WF-0039 implemented rollout-safety controls for `pipeline_v1` on structured reviews. The scope stayed operational:
- deterministic call-level routing checks,
- production fail-closed guardrail for empty allowlist,
- engine-path telemetry visibility,
- replay artifact generation and rollout-health evaluation scripts,
- staging-simulated canary verification matrix.

No schema changes, no public API contract changes, and no frontend UX changes were introduced.

## What Changed

1. Routing and guardrails:
- Added production guardrail logic so `APP_ENV=prod` + global v1 enabled + empty allowlist fails closed to legacy routing.
- Added explicit warning logging for this misconfiguration path.

2. Observability:
- Added `engine_path` metadata into pipeline telemetry run metadata.
- Added route-level log marker `structured_review.engine_path=<legacy|pipeline_v1>`.

3. Replay and health tooling:
- Added `backend/scripts/replay_structured_rollout.py` comparator + replay artifact writer (`--replays`, `--output`).
- Added `backend/scripts/evaluate_rollout_health.py` threshold evaluator with fail-safe rollback recommendation on insufficient data.
- Added deterministic replay artifact sample at `backend/artifacts/rollout/replay_canary.json`.

4. Tests:
- Added `backend/tests/test_rollout_replay.py`.
- Added `backend/tests/test_rollout_health.py`.
- Extended API and pipeline tests for canary routing matrix, fail-closed behavior, and health decision flow.

## Verification Evidence

- Baseline preflight (before Task 1):
  `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_phase3_preflight.db uv run pytest -q tests/test_api.py -k "structured_review and pipeline_v1 and allowlist"`
  Result: pass.

- Task-level verification commands executed and passing:
  - Task 2: prod fail-closed route test.
  - Task 3: engine-path telemetry/log tagging tests.
  - Task 4/5: replay comparator + artifact schema tests and CLI run.
  - Task 6: rollout health threshold tests and CLI run.
  - Task 7: canary/fail-closed integrated matrix test.

- Final Part A regression sweep:
  `DATABASE_URL=sqlite:////tmp/grant_reviewer_test_phase3_parta.db backend/scripts/verify_tests_sqlite.sh -q tests/test_api.py tests/test_engine_telemetry.py tests/test_rollout_replay.py tests/test_rollout_health.py tests/test_review_engine_pipeline_v1.py`
  Result: `81 passed`.

## Remaining Risks

- Current replay artifact sample uses deterministic demo payload defaults unless explicit input payloads are provided; operators should run with real captured payloads for release decisions.
- Guardrail warning currently logs per affected request; this is acceptable for MVP but may be noisy under sustained misconfiguration.
- Threshold constants are fixed in script for now; future tuning should be data-driven after initial canary rollout.

## Staging-Simulated Canary Verification Checklist

1. Enable canary routing for one call:
   - `APP_ENV=staging`
   - `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1`
   - `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES=nwo_veni_2025_preproposal`
2. Submit structured review request and confirm route logs include:
   - `structured_review.engine_path=pipeline_v1`
3. Simulate production misconfiguration:
   - `APP_ENV=prod`
   - `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1`
   - `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` unset/empty
4. Confirm fail-closed behavior:
   - request still succeeds
   - route logs show legacy path and warning for empty prod allowlist
5. Generate replay artifact evidence:
   - `cd backend && uv run python scripts/replay_structured_rollout.py --replays 20 --output artifacts/rollout/replay_canary.json`
6. Evaluate rollout health decision:
   - `cd backend && uv run python scripts/evaluate_rollout_health.py --input artifacts/rollout/replay_canary.json`
   - expected with missing metrics: `recommended_action=rollback` and reason `insufficient_data`

## Expected Automated Verification

- `cd backend && DATABASE_URL=sqlite:////tmp/grant_reviewer_test_phase2e.db uv run pytest -q tests/test_api.py tests/test_review_engine_pipeline_v1.py -k "canary or rollout or fail_closed"`
