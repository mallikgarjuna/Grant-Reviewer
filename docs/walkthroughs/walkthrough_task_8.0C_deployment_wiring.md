# Walkthrough: Task 8.0C Deployment Wiring (Phase 3)

**Date**: 2026-02-12  
**Task ID**: 8.0C  
**Status**: In Progress (v0.6 - Stage 2 complete; stub-default locked)  

## Scope Completed In This Pass

- Completed `8.0C.2` backend DB wiring:
  - `backend/app/db.py` now supports `DATABASE_URL`, normalizes Render-style Postgres URLs (`postgres://` -> `postgresql+psycopg://`), and enforces default `sslmode=require` + `connect_timeout=3`.
  - Added DB readiness ping via `ping_database()` and exposed `GET /health/db` in `backend/main.py`.
  - Added tests for `/health/db` and URL normalization in `backend/tests/test_api.py`.
  - Added Postgres driver dependency in `backend/pyproject.toml` (`psycopg[binary]`).
- Completed `8.0C.3` bootstrap tooling:
  - Added `backend/scripts/ensure_prompt_template.py` (idempotent active-template bootstrap).
  - Updated `backend/README.md` with explicit manual production bootstrap runbook.
- Completed `8.0C.4` frontend runtime config:
  - Added `runtime="nodejs"` and `maxDuration=60` to `frontend/src/app/api/bff/reviews/route.ts`.
- Completed `8.0C.6` readiness failure semantics hardening:
  - `GET /health/db` now maps DB-unavailable checks to a canonical `503` (`DB_UNAVAILABLE`) instead of generic unhandled failures.
  - Added explicit failure-path API test coverage and updated backend endpoint docs for liveness vs readiness behavior.

## Verification Run (What Actually Ran)

### Backend targeted tests

Command:
`cd backend && uv run pytest tests/test_api.py -q`

Result:
- Passed (`22 passed`).

### Readiness semantics verification (8.0C.6)

Commands:
- `cd backend && uv run pytest tests/test_api.py -q -k "healthcheck_db or error_code_status_mapping"`
- `cd backend && uv run pytest tests/test_api.py -q`

Results:
- Focused readiness/mapping tests passed (`3 passed, 19 deselected`).
- Full API regression passed after readiness change (`22 passed`).

### Bootstrap script idempotency

Command:
`cd backend && uv run python scripts/ensure_prompt_template.py` (run twice)

Result:
- Both runs succeeded; script reported existing active template without mutation.

### Frontend BFF invariant check

Command:
`cd frontend && npm run check:bff`

Result:
- Passed (`bff-invariant-check: ok`).

## Verification Limits / Remaining Work

- `scripts/verify_local_8_0A.sh` full pass was attempted in this sandbox, but backend smoke stage hung and timed out. Partial output confirmed frontend checks (`check:bff`, `check:seo`, `lint`) reached pass points before timeout.
- Deploy operations were executed outside this sandbox (Render/Vercel/Neon).

## Deployed Environment (What Was Wired)

- **Backend (Render)**: `https://grant-reviewer.onrender.com`
  - `GET /health` → `200 {"ok":true}`
  - `GET /health/db` → `200 {"ok":true}` (Neon connectivity)
  - `GET /calls` → `200` with ≥ 1 call after bootstrap
- **Database (Neon)**:
  - `DATABASE_URL` uses **direct** connection (pooling OFF); `sslmode=require`.
  - Attempting Neon `-pooler` + `channel_binding=require` caused intermittent `psycopg.OperationalError` (`SSL connection has been closed unexpectedly`) on real queries; resolved by switching to direct and removing `channel_binding=require`.
- **Frontend (Vercel)**: `https://grant-reviewer.vercel.app`
  - Logged-out `/app` redirects to sign-in (`/sign-in?redirect_url=%2Fapp`).
  - End-to-end submit via BFF succeeds in `LLM_MODE=stub`.

## Production Bootstrap (No Render Shell)

Render free instances do not support shell access; bootstrap was run from a developer machine against the same Neon database used by Render.

Commands (run locally with `DATABASE_URL` set to the Neon **direct** URL used by Render):
- `cd backend && DATABASE_URL="..." uv run python scripts/ensure_prompt_template.py`
- `cd backend && DATABASE_URL="..." uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml`

Verification:
- `curl -i https://grant-reviewer.onrender.com/calls`

## Stage 1 (Stub) End-to-End Verification

- Vercel app submitted one review successfully in `LLM_MODE=stub`.
- Example review id: `a2c1ecb1-2e3f-4f94-8fb7-45f71c0cc32a` (UI showed “Review completed with 2 findings.”)
- Unsigned direct backend access fails as expected:
  - `curl -i https://grant-reviewer.onrender.com/reviews/a2c1ecb1-2e3f-4f94-8fb7-45f71c0cc32a` → `401 UNAUTHORIZED` (`Missing authentication signature headers.`)

## Remaining Open Subtasks

- Decide production default mode:
  - keep `LLM_MODE=stub` until launch day (lowest cost risk), or
  - keep `LLM_MODE=openai` enabled (ready for real users).
- Optional: record Vercel Network timing evidence screenshot for Stage 2 in a durable location (no secrets).

## Stage 2 (OpenAI) One-Shot Verification

- Backend set to `LLM_MODE=openai` with `OPENAI_API_KEY` present.
- One real end-to-end review submitted via Vercel BFF completed successfully.
  - Review id: `b3a9df0c-7c78-4a90-8ec8-51cf3fd5ce5e`
  - Observed wait time (Vercel request): ~11.41s
  - Status: `COMPLETED`

## Operational Decision (Post-Verification)

- Decision (AD 8.16): keep production default `LLM_MODE=stub` until launch day.
- Verified: Render env `LLM_MODE=stub` set and redeployed; UI submissions return “Stub feedback…” as expected.

## Revision History

- **v0.1** (2026-02-12): Initial Phase 3 walkthrough with completed local implementation/verification and explicit deploy-only remaining steps.
- **v0.2** (2026-02-12): Added `8.0C.6` readiness hardening outcomes, including explicit `503` failure semantics and targeted/full API verification results.
- **v0.3** (2026-02-12): Recorded deployed wiring (Vercel + Clerk, Render FastAPI, Neon direct Postgres) and Stage 1 stub end-to-end verification results; Stage 2 remains pending.
- **v0.4** (2026-02-12): Added explicit verification that unsigned `GET /reviews/{review_id}` returns `401 UNAUTHORIZED` (BFF boundary holds).
- **v0.5** (2026-02-12): Recorded Stage 2 `LLM_MODE=openai` one-shot end-to-end verification (completed review within runtime budget).
- **v0.6** (2026-02-12): Locked operational choice to keep production default `LLM_MODE=stub` until launch day (AD 8.16).
