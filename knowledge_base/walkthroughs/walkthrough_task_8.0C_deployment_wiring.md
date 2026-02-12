# Walkthrough: Task 8.0C Deployment Wiring (Phase 3)

**Date**: 2026-02-12  
**Task ID**: 8.0C  
**Status**: In Progress (v0.2 - 8.0C.6 complete; deploy execution pending)  

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
- No real deploy operations were executed from this environment (no Render/Vercel provisioning actions).

## Remaining Open Subtasks

- `8.0C.1` Provider + env wiring (deploy platform configuration, Clerk production URLs, secret setup).
- `8.0C.7` Deploy execution Stage 1 (`LLM_MODE=stub` wiring proof in deployed environment).
- `8.0C.8` Deploy execution Stage 2 (`LLM_MODE=openai` one-shot real review verification).

## Revision History

- **v0.1** (2026-02-12): Initial Phase 3 walkthrough with completed local implementation/verification and explicit deploy-only remaining steps.
- **v0.2** (2026-02-12): Added `8.0C.6` readiness hardening outcomes, including explicit `503` failure semantics and targeted/full API verification results.
