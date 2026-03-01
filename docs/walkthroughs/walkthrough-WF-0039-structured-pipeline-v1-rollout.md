# WF-0039 — Structured Pipeline v1 Rollout

Artifact: walkthrough
Version: v0.0
Status: Not started
Last Updated: 2026-03-01

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
