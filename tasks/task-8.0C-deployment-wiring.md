# Task 8.0C: Deployment Wiring (Phase 2 Plan)

**Date**: 2026-02-12  
**Task ID**: 8.0C  
**Pipeline Phase**: Phase 2 (Task breakdown)  
**Status**: In Progress (v0.3 - 8.0C.2/8.0C.3/8.0C.4 complete)  
**Last Updated**: 2026-02-12  
**PRD**: `tasks/prd-8.0C-deployment-wiring.md`  
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-8.0C-deployment-wiring.md`  

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

- Providers: Vercel (Next.js) + Render (FastAPI) + Render Postgres.
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

## Dependencies / Inputs

- Backend contracts are already shipped (8.0B): signatures, idempotency, quotas, kill switch, ownership.
- Frontend BFF routes already exist (8.0A): `frontend/src/app/api/bff/*`.
- Local verification exists (8.0A): `scripts/verify_local_8_0A.sh`.

---

## 8.0C.1 Provider + env wiring (commit)

Goal: get Vercel ↔ Render connectivity and secrets wiring correct before touching DB internals.

- [ ] Create/confirm Render FastAPI service deploys from `backend/`:
  - [ ] Root Directory: `backend`
  - [ ] Python: 3.12
  - [ ] Build: `python -m pip install --upgrade pip && python -m pip install uv && uv sync --frozen`
  - [ ] Start: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Create/confirm Vercel frontend deploys from `frontend/`.
- [ ] Configure Clerk for production frontend URL (and local dev origins remain intact).
- [ ] Set Vercel env vars:
  - [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - [ ] `CLERK_SECRET_KEY`
  - [ ] `FASTAPI_BASE_URL` (Render service URL; **no trailing slash**)
  - [ ] `BFF_SHARED_SECRET` (prod secret, not `dev`)
- [ ] Set Render env vars (minimum to boot):
  - [ ] `BFF_SHARED_SECRET` (must match Vercel)
  - [ ] `LLM_MODE=stub`
  - [ ] `REVIEWS_ENABLED=true`
  - [ ] `REVIEW_TIMEOUT_SECONDS=25`

**Verify (deploy)**
- [ ] `GET <fastapi-base-url>/health` returns `{ok:true}`
- [ ] Frontend landing renders at `<frontend-base-url>/`
- [ ] Logged-out `/app` redirects to sign-in

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
- [ ] Render Postgres provisioned and `DATABASE_URL` set
- [ ] DB readiness check passes in deployed environment

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
  - `uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml`
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

- [ ] Stage 1 (stub): `LLM_MODE=stub`
  - [ ] `/api/bff/calls` returns at least 1 call (seed completed)
  - [ ] End-to-end submit works via `/api/bff/reviews`
  - [ ] Unsigned direct calls to FastAPI protected endpoints fail
- [ ] Stage 2 (openai): `LLM_MODE=openai`
  - [ ] One real end-to-end review completes within the timeout budget

Record results (including exact URLs and env toggles used) in the 8.0C walkthrough.

---

## Walkthrough (Phase 3 requirement)

- Create `knowledge_base/walkthroughs/walkthrough_task_8.0C_deployment_wiring.md` with:
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

---

## Revision History

- **v0.1** (2026-02-12): Initial Phase 2 plan with MVP sequencing (env wiring → Postgres support → bootstrap runbook → runtime config → deploy verification).
- **v0.2** (2026-02-12): Added explicit Render build/start mechanics, tightened Postgres URL/SSL requirements, and fixed bootstrap runbook to include the required `PromptTemplate` (avoid sample seed data in prod).
- **v0.3** (2026-02-12): Phase 3 progress update: completed 8.0C.2 backend DB wiring, 8.0C.3 bootstrap script/runbook, and 8.0C.4 BFF route runtime config; deploy-bound subtasks remain open.
