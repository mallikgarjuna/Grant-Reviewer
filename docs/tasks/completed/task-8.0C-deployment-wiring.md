# Task 8.0C: Deployment Wiring (Phase 2 Plan)

**Date**: 2026-02-12
**Task ID**: 8.0C
**Pipeline Phase**: Phase 2 (Task breakdown)
**Status**: In Progress (v0.8 - deploy wiring verified; stub-default active)
**Last Updated**: 2026-02-12
**PRD**: `docs/prds/prd-8.0C-deployment-wiring.md`
**Phase 0 Notes**: `docs/brainstorms/brainstorming-8.0C-deployment-wiring.md`

---

## Scope Guardrails (MVP)

- Prod-only wiring for 8.0C (no preview parity requirements).
- No async execution, streaming, background jobs, or polling.
- No Alembic migrations yet (we accept `create_all()` MVP risk).
- No custom backend domain (`api.<domain>`) for MVP.
- No IaC / CI-CD automation in 8.0C.
- Keep FastAPI CORS disabled (BFF boundary means browsers should not call FastAPI directly).

## Subtask Verification Rule (Mandatory)

- For every Phase 3 subtask commit, run at least one targeted verification for that subtask before committing.
- Verification can be test, lint/build check, or reliable manual repro depending on the subtask.
- Record what was run (and outcome) in the 8.0C walkthrough.

## Decisions Locked In This Plan (MVP, ship-fast)

- Providers: Vercel (Next.js) + Render (FastAPI) + Neon Postgres.
- Render backend deploy mechanics (MVP-fast default):
  - Render Web Service **Root Directory**: `backend`
  - Render Web Service **Python version**: 3.12
  - Render Web Service **Build Command**: `python -m pip install --upgrade pip && python -m pip install uv && uv sync --frozen`
  - Render Web Service **Start Command**: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
- Timeout defaults:
  - Next BFF create route (`frontend/src/app/api/bff/reviews/route.ts`): `runtime="nodejs"`, `maxDuration=60`.
  - FastAPI production: `REVIEW_TIMEOUT_SECONDS=25`.
- Rollout staging:
  - Stage 1: deploy/verify with `LLM_MODE=stub` (wiring proof, no cost noise).
  - Stage 2: flip to `LLM_MODE=openai` + `OPENAI_API_KEY` and run one real end-to-end review.
- Operational constraint: single backend instance for initial launch.
- Bootstrap: one-time manual ingest into prod DB with a written runbook.

Note: `DATABASE_URL` normalization/SSL defaults were originally driven by Render Postgres URLs; they remain valid for Neon (Neon enforces SSL; `postgres://...` is still normalized).

## Dependencies / Inputs

- Backend contracts are already shipped (8.0B): signatures, idempotency, quotas, kill switch, ownership.
- Frontend BFF routes already exist (8.0A): `frontend/src/app/api/bff/*`.
- Local verification exists (8.0A): `scripts/verify_local_8_0A.sh`.

## Next-Round Decisions (MVP, ship-fast)

- Execute provider/env wiring first (`8.0C.1`) before further backend hardening or real LLM deploy checks.
- Keep deploy verification strictly separate from local verification (`scripts/verify_local_8_0A.sh` remains a local-only gate).
- Add a lightweight readiness hardening step: DB-unreachable readiness should fail explicitly as `503` (instead of generic uncaught failure) before deploy-stage verification.
- Preserve staged rollout discipline:
  - Stage 1 deploy verification uses `LLM_MODE=stub`.
  - Stage 2 runs exactly one real `LLM_MODE=openai` review after Stage 1 passes.

---

## 8.0C.1 Provider + env wiring (commit)

Goal: get Vercel ↔ Render connectivity and secrets wiring correct before touching DB internals.

- [x] Create/confirm Render FastAPI service deploys from `backend/`:
  - [x] Root Directory: `backend`
  - [x] Python: 3.12
  - [x] Build: `python -m pip install --upgrade pip && python -m pip install uv && uv sync --frozen`
  - [x] Start: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
- [x] Create/confirm Vercel frontend deploys from `frontend/`.
- [x] Configure Clerk for production frontend URL.
- [x] Set Vercel env vars:
  - [x] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - [x] `CLERK_SECRET_KEY`
  - [x] `FASTAPI_BASE_URL=https://grant-reviewer.onrender.com` (**no trailing slash**)
  - [x] `BFF_SHARED_SECRET` (prod secret, not `dev`)
- [x] Set Render env vars (minimum to boot):
  - [x] `BFF_SHARED_SECRET` (must match Vercel)
  - [x] `LLM_MODE=stub`
  - [x] `REVIEWS_ENABLED=true`
  - [x] `REVIEW_TIMEOUT_SECONDS=25`
  - [x] `DATABASE_URL` (Neon direct URL; avoid `-pooler` for MVP stability)

**Verify (deploy)**
- [x] `GET https://grant-reviewer.onrender.com/health` returns `{ok:true}`
- [x] Frontend landing renders at `https://grant-reviewer.vercel.app/`
- [x] Logged-out `/app` redirects to sign-in

---

## 8.0C.2 Postgres support + DB readiness check (commit)

Goal: switch backend persistence to managed Postgres without breaking local dev.

- [x] Backend supports `DATABASE_URL`:
  - [x] Uses `DATABASE_URL` when set; otherwise defaults to local SQLite for dev.
  - [x] Avoid SQLite-only filesystem side effects when Postgres is used.
- [x] Add Postgres driver dependency (`psycopg[binary]`) and verify import/runtime.
- [x] Normalize Render DB URLs for SQLAlchemy:
  - [x] Accept `postgres://...` and rewrite to `postgresql+psycopg://...` (preserve user/pass/host/db + query string).
  - [x] Ensure SSL requirements are explicit (`sslmode=require`), either via `DATABASE_URL` or documented env.
- [x] Add DB readiness endpoint (`/health/db` or enrich `/health`) that:
  - [x] performs a fast `SELECT 1` (or equivalent)
  - [x] times out quickly
  - [x] returns `{ok:true}` only when DB is reachable

**Verify (local/sandbox where possible)**
- [x] `uv run pytest tests/test_api.py -q` (SQLite mode still passes)

**Verify (deploy)**
- [x] Neon Postgres provisioned and `DATABASE_URL` set
- [x] DB readiness check passes in deployed environment

---

## 8.0C.3 Bootstrap runbook (commit)

Goal: a repeatable “seed prod DB” procedure (manual is OK, undocumented is not).

- [x] Document the exact one-time seed steps (where + command + verification).
- [x] Ensure prod bootstrap covers *all* prerequisites for “submit review”:
  - [x] At least 1 active call + nodes + expectations (YAML ingest)
  - [x] At least 1 active `PromptTemplate` row (required by backend; otherwise `POST /reviews` fails)
- [x] Required verification steps:
  - [x] `GET /calls` returns at least 1 call
  - [x] `GET /calls/{call_id}/nodes` returns nodes

Implementation options (pick the simplest that works on Render):
- **Decision (MVP)**: avoid `scripts/seed.py` in production (it creates sample calls); use explicit bootstrap commands instead.
- Option A (preferred): Render shell / one-off exec runs:
  - `uv run python scripts/ensure_prompt_template.py`
  - `uv run python scripts/ingest_call.py data/calls/legacy/erc/erc_cog_2026_full_official.yaml`
- Option B: extend `scripts/ingest_call.py` to ensure an active prompt template exists (acceptable, but mixes concerns).
- Option C: temporary admin-only route (defer unless absolutely necessary; increases attack surface).

---

## 8.0C.4 Frontend BFF route runtime config (commit)

Goal: ensure Vercel runtime settings won’t prematurely time out review creation.

- [x] Update `frontend/src/app/api/bff/reviews/route.ts`:
  - [x] `export const runtime = "nodejs"`
  - [x] `export const maxDuration = 60`

**Verify (local)**
- [x] `npm run check:bff` (adapter/BFF invariants).
- [ ] `scripts/verify_local_8_0A.sh` full pass (still needed outside sandbox; backend smoke hangs in this environment).

---

## 8.0C.5 Deploy verification (Required)

Run deploy verification in two stages:

- [x] Stage 1 (stub): `LLM_MODE=stub`
  - [x] `/api/bff/calls` returns at least 1 call (seed completed)
  - [x] End-to-end submit works via `/api/bff/reviews`
  - [x] Unsigned direct calls to FastAPI protected endpoints fail (`401 UNAUTHORIZED` without signature headers)
- [x] Stage 2 (openai): `LLM_MODE=openai`
  - [x] One real end-to-end review completes within the timeout budget

Record results (including exact URLs and env toggles used) in the 8.0C walkthrough.

---

## 8.0C.6 Readiness failure semantics hardening (commit)

Goal: make DB readiness behavior deterministic and operator-friendly for deployment probes.

- [x] Update backend DB readiness behavior so DB-unreachable checks return explicit HTTP `503` with stable error payload.
- [x] Keep `GET /health` as pure liveness (`200` when app process is alive).
- [x] Add targeted API tests covering:
  - [x] healthy DB path (`200`, `{ok:true}`)
  - [x] forced DB failure path (`503`, stable error body)
- [x] Update backend docs to state liveness vs readiness semantics clearly.

**Verify (local/sandbox where possible)**
- [x] `uv run pytest tests/test_api.py -q -k "healthcheck_db or error_code_status_mapping"` (readiness + mapping focus)
- [x] `uv run pytest tests/test_api.py -q` (full API regression)

---

## 8.0C.7 Deploy execution - Stage 1 (stub) (commit)

Goal: prove end-to-end deployed wiring with minimal cost/latency noise.

- [x] Complete `8.0C.1` provider/env wiring in deployed services.
- [x] Provision Neon Postgres + set backend `DATABASE_URL`.
- [x] Run production bootstrap commands against the deployed DB:
  - [x] `uv run python scripts/ensure_prompt_template.py` (ran locally with `DATABASE_URL` targeting Neon; Render free has no shell)
  - [x] `uv run python scripts/ingest_call.py data/calls/legacy/erc/erc_cog_2026_full_official.yaml` (ran locally with `DATABASE_URL` targeting Neon)
- [x] Verify deployed backend:
  - [x] `GET /health` returns `{ok:true}`
  - [x] DB readiness endpoint returns healthy signal
  - [x] `GET /calls` returns at least 1 call
- [x] Verify deployed frontend/BFF:
  - [x] `/api/bff/calls` returns at least one call
  - [x] one end-to-end submit via `/api/bff/reviews` succeeds with `LLM_MODE=stub`
  - [x] unsigned direct calls to protected FastAPI endpoints fail (`401 UNAUTHORIZED` without signature headers)
- [x] Record exact URLs + env toggles + outcomes in walkthrough.

---

## 8.0C.8 Deploy execution - Stage 2 (openai) (commit)

Goal: confirm one real production review within runtime budget after stub wiring proof.

- [x] Flip backend to `LLM_MODE=openai` and set `OPENAI_API_KEY`.
- [x] Run exactly one real end-to-end review through frontend BFF.
- [x] Capture observed request latency and compare with timeout budget (`maxDuration=60`, `REVIEW_TIMEOUT_SECONDS=25`).
- [x] If Stage 2 fails due to timeout/instability, revert to `LLM_MODE=stub`, log findings, and open follow-up task (do not block MVP wiring completion).
- [x] Reverted production default to `LLM_MODE=stub` after verification; confirmed UI returns stub feedback post-redeploy.

---

## Walkthrough (Phase 3 requirement)

- Create `docs/walkthroughs/walkthrough_task_8.0C_deployment_wiring.md` with:
  - what was deployed (providers, URLs)
  - what was verified (commands + results)
  - what remains deferred (explicitly)

---

## Non-Scope Ideas (Backlog)

- Preview environment parity (Vercel previews + Clerk + backend).
- Custom backend domain (`api.<domain>`).
- Alembic migrations + schema evolution automation.
- Async execution (jobs + polling) if runtime limits force it.
- IaC / CI-CD automation.
- Full observability stack (Sentry/OTel/metrics) beyond provider logs.
- Dockerfile / containerization for backend deploy (only if native Render build proves unreliable).
- Render blueprint (`render.yaml`) until the manual wiring path is stable.
- DB pooling/connection tuning (including PgBouncer) before real load exists.
- Health endpoint auth/rate-limit hardening beyond current MVP probe requirements.
- Automated bootstrap admin endpoint/job (manual runbook remains preferred for 8.0C).

---

## Revision History

- **v0.1** (2026-02-12): Initial Phase 2 plan with MVP sequencing (env wiring → Postgres support → bootstrap runbook → runtime config → deploy verification).
- **v0.2** (2026-02-12): Added explicit Render build/start mechanics, tightened Postgres URL/SSL requirements, and fixed bootstrap runbook to include the required `PromptTemplate` (avoid sample seed data in prod).
- **v0.3** (2026-02-12): Phase 3 progress update: completed 8.0C.2 backend DB wiring, 8.0C.3 bootstrap script/runbook, and 8.0C.4 BFF route runtime config; deploy-bound subtasks remain open.
- **v0.4** (2026-02-12): Incorporated critical Phase 3 review feedback by adding next-round execution decisions, a dedicated readiness-failure hardening subtask (`8.0C.6`), and explicit staged deploy execution subtasks (`8.0C.7` stub, `8.0C.8` openai).
- **v0.5** (2026-02-12): Completed `8.0C.6` readiness hardening: `/health/db` now returns explicit `503` canonical error on DB-unavailable checks, with targeted + full API test verification.
- **v0.6** (2026-02-12): Locked DB provider change to Neon Postgres (Render still hosts FastAPI; `DATABASE_URL` now sourced from Neon).
- **v0.7** (2026-02-12): Completed Stage 2 deploy verification in `LLM_MODE=openai` (one real end-to-end review succeeded within runtime budget).
- **v0.8** (2026-02-12): Confirmed rollback to `LLM_MODE=stub` as production default after Stage 2 verification.
