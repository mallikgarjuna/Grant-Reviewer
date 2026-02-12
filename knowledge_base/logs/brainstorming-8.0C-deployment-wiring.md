# Brainstorming 8.0C: MVP Deployment Wiring (Next.js + Clerk + BFF, FastAPI, Postgres)

**Date**: 2026-02-10  
**Task ID**: 8.0C  
**Pipeline Phase**: Phase 0 (Brainstorming)  
**Status**: Draft (v0.2 - Revised)  
**Last Updated**: 2026-02-12  

## Goal (MVP)

Wire up a *production-ish* deployment that is safe, low-ops, and fast to iterate:
- **Frontend**: Next.js (Vercel) + Clerk auth + BFF routes (browser never calls FastAPI directly).
- **Backend**: FastAPI service reachable from Vercel (but “private by contract” via BFF signatures).
- **DB**: managed Postgres for FastAPI persistence (replace SQLite drift risk).
- **Ops basics**: secrets/env mapping, domains + redirects, CORS posture, health checks, and a deploy verification checklist that is explicitly separate from local verification.

This task is *deployment wiring*, not feature expansion.

## Current Baseline (What Exists Today)

- Next.js expects (server-only) `FASTAPI_BASE_URL` + `BFF_SHARED_SECRET`; Clerk keys; BFF contract is already in place (Task 8.0B).
- FastAPI has `GET /health` liveness and uses SQLite via `backend/app/db.py` (hardcoded path today).
- Local verification split exists (see `scripts/verify_local_8_0A.sh`) and must remain explicit: sandbox/static vs local runtime.

## Critical Gaps / Risks (Senior Critique)

### R0: Vercel runtime timeouts vs synchronous reviews (risk: “deploy green, app broken”)
The BFF path is: browser → Next.js route handler → FastAPI `POST /reviews` (sync).
If Vercel request/compute limits are below the worst-case review time, users will see failures/timeouts even if FastAPI is healthy.

MVP requirement: explicitly align:
- Vercel route handler max duration (and runtime type)
- FastAPI `REVIEW_TIMEOUT_SECONDS`
- UI “still working” messaging (idempotency-based)

### R1: Provider decisions are still implicit (risk: thrash + broken redirects)
We have an earlier “Vercel + Render” direction in 8.0 notes, but 8.0C needs explicit closure because:
- Clerk redirect URLs/origins differ across prod vs preview vs local.
- API base URL, custom domains, and SSL assumptions differ per host.

### R2: Postgres is not “wiring only” — it forces code + dependency change
Backend DB is currently hardcoded SQLite and creates a local directory at import time.
Moving to managed Postgres implies:
- `DATABASE_URL` support (including SSL mode).
- a Postgres driver (e.g., `psycopg`) dependency.
- an environment-specific table creation/migration strategy.

If we pretend this is only “infra config”, we will lose time later.

### R3: Data bootstrapping is unsolved (risk: “empty prod”)
A new Postgres will be empty. The app needs:
- at least one ingested funding call YAML in prod DB, or
- a deterministic seed step at deploy time, or
- an admin workflow (non-goal for 8.0C, so we need a *minimal* bootstrap mechanism).

### R4: Secret alignment across services is a footgun (risk: silent auth failures)
`BFF_SHARED_SECRET` must match between Vercel and backend host. Missing/mismatched values manifest as generic `UNAUTHORIZED`.
We need a deliberate “secret rotation + verification” story (even if manual for MVP).

### R5: CORS is often over-configured (risk: weakening boundary)
With a BFF, browsers should not call FastAPI directly. Overly permissive CORS on FastAPI is unnecessary and increases abuse surface.
MVP should default to **no CORS** (or a tight dev-only allowlist if needed).

### R6: Health checks can be misleading (risk: green deploy, broken app)
`GET /health` is liveness only. For deployment we also need:
- a “can talk to DB” check (even if separate endpoint or optional query),
- and a BFF-to-backend connectivity smoke (from Vercel runtime).

## Clarifying Questions (Resolved for MVP Speed)

These were open questions in v0.1; for MVP velocity we choose defaults here and treat deviations as explicit follow-up tasks.

### Q1: Providers
**Decision (MVP)**: Vercel (Next.js) + Render (FastAPI) + Render Postgres.
- Why: matches current direction, minimizes bespoke infra, good “one team, two services” wiring story.

### Q2: Preview environments
**Decision (MVP)**: prod-only wiring first; preview environments are non-goal for 8.0C.
- Why: Clerk + cross-service previews tends to eat days. We can add it later once prod is stable.

### Q3: Domains / URLs
**Decision (MVP)**:
- Frontend can use a custom domain (optional).
- Backend stays on its provider URL for now (no `api.<domain>` requirement).
- Why: the browser should not talk to FastAPI directly; a custom backend domain doesn’t buy MVP value and adds TLS/DNS + Clerk surface area.

### Q4: FastAPI `/docs` exposure
**Decision (MVP)**: keep `/docs` public.
- Guardrail: protected endpoints still require valid BFF signatures; docs visibility should not imply access.

### Q5: Migrations
**Decision (MVP)**: no Alembic yet; use `SQLModel.metadata.create_all()` while schema is still moving fast.
- Explicit risk acceptance: schema changes later may require manual migration steps until Alembic is added.

### Q6: Bootstrap / seeding
**Decision (MVP)**: start with empty Postgres and perform a one-time manual ingest into prod.
- Requirement: document the exact runbook + verification steps (no tribal knowledge).

### Q7: Secrets policy
**Decision (MVP)**: separate secrets per environment (local vs prod), even if we skip preview envs.
- Practical minimum: prod `BFF_SHARED_SECRET` is not the same as `dev`.

### Q8: Secrets management constraints
**Decision (MVP)**: use provider secret stores (Vercel env vars + Render env vars). No `.env` in deployed artifacts.

## Decisions Locked Now (MVP)

### D1: Hosting split
- **Next.js** on **Vercel**.
- **FastAPI** on **Render Web Service**.
- **Postgres** on **Render Postgres**.

Rationale: matches existing architectural direction, minimizes bespoke infra work, and keeps DB close to backend.

### D2: Domain model (MVP-fast)
- Frontend:
  - Option A: custom domain on Vercel (recommended if you already have one)
  - Option B: keep `*.vercel.app` until later
- Backend: keep Render service URL (no custom `api.<domain>` for MVP).
- Clerk: configure only the production frontend domain + local dev origins; skip previews.

### D3: FastAPI exposure + security posture
- Backend remains *publicly reachable* but:
  - protected endpoints require BFF signatures (`BFF_SHARED_SECRET`) and user id headers.
  - CORS stays **disabled** (or a minimal dev-only allowlist).

### D4: Timeout alignment (must-have)
- Choose a single end-to-end budget for synchronous reviews and enforce it:
  - Vercel route handler max duration ≥ backend review timeout + overhead
  - FastAPI `REVIEW_TIMEOUT_SECONDS` set accordingly
- Deploy verification must include one real end-to-end call through the BFF path that stays within this budget.

### D5: Health endpoints (liveness + readiness)
- Keep `GET /health` as liveness.
- Add a DB readiness check (either `GET /health/db` or enrich `/health`):
  - Runs a fast “can connect” query (e.g., `SELECT 1`)
  - Uses a small timeout
  - Returns `{ok:true}` only when the DB is reachable

### D6: Postgres bootstrap strategy
MVP-fast option:
- “Create tables on startup” for now (no migrations).
- Run a **one-time manual ingest** to populate calls (documented runbook).

## Environment / Secrets Mapping (Concrete, MVP)

### Frontend (Vercel env vars)

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (public; client-visible)
- `CLERK_SECRET_KEY` (secret; server-only)
- `FASTAPI_BASE_URL` (server-only; points to the Render FastAPI service URL for MVP)
- `BFF_SHARED_SECRET` (secret; server-only; must match backend)

Notes:
- Keep `FASTAPI_BASE_URL` **not** prefixed with `NEXT_PUBLIC_` to avoid accidental browser access.
- Keep separate values for **Development / Production** in Vercel (preview is out-of-scope for MVP).

### Backend (FastAPI service env vars)

Existing:
- `BFF_SHARED_SECRET` (required for protected endpoints)
- `OPENAI_API_KEY` (prod only if using real LLM)
- `LLM_MODE` (`stub` vs `openai`)
- `REVIEWS_ENABLED`, `FREE_DAILY_REVIEW_LIMIT`, `REVIEW_TIMEOUT_SECONDS`

To add for Postgres:
- `DATABASE_URL` (Render/managed Postgres connection string; ensure SSL expectations are explicit)

## Deploy Verification vs Local Verification (Keep Separate On Purpose)

### Local verification (unchanged; developer machine)
- Use `scripts/verify_local_8_0A.sh` for:
  - static checks (lint/SEO/contract checks)
  - backend smoke via `TestClient` with signed headers (stub mode)
  - required manual browser checklist for auth + UX flow

### Deploy verification (new; production/preview environment)
Minimum deploy checks should be explicitly documented and repeatable:
- Backend:
  - `GET <fastapi-base-url>/health` returns `{ok:true}`
  - DB connectivity check passes (`/health/db` or equivalent)
- Frontend:
  - `GET <frontend-base-url>/` renders
  - `/app` redirects to Clerk sign-in when logged out
  - after sign-in, can run one review end-to-end (stub mode if configured; openai mode if opted-in)
- Security posture:
  - direct browser requests to protected FastAPI endpoints fail without signature headers
  - CORS is not wildcard-open on FastAPI
- Timeout alignment:
  - the end-to-end “submit review” path through Next.js does not exceed the Vercel runtime budget

Important: deploy verification is *not* a substitute for local browser-flow verification; it’s a separate checklist.

## Recommended Sequencing (Keep “Wiring” Shippable)

This is still one task (8.0C), but the execution should be split into small, independently verifiable slices:

1) **8.0C.1 Provider + env wiring (no Postgres yet)**: Vercel env vars + Render service + basic deploy smoke.
2) **8.0C.2 Postgres support**: backend `DATABASE_URL` support + driver + readiness check.
3) **8.0C.3 Bootstrap runbook**: one-time ingest steps + verification query/endpoints.
4) **8.0C.4 Deploy verification checklist**: explicit “prod checklist” separate from local verification, includes timeout proof.

If any slice grows unexpectedly (e.g., migrations become necessary), split it into a follow-up task rather than stalling the deploy.

## Non-Scope Backlog (Explicitly Deferred)

- CI/CD pipelines, GitHub Actions deployments, or IaC (Terraform/Pulumi).
- Automated DB migrations (Alembic) if we choose “create_all” for MVP.
- Observability stack (Sentry/OTel/metrics) beyond basic provider logs.
- Rate limiting/WAF beyond current signature boundary + quotas.
- Multi-tenant/org accounts, billing/Stripe, user management UI.
- Zero-downtime deploys and advanced rollout strategies.
- Preview environment parity (Vercel previews + Clerk + backend) until prod is stable.
- Custom backend domain (`api.<domain>`) until it provides concrete value.

## Phase 1 PRD Readiness Criteria (Definition of “Ready to Spec”)

Phase 1 PRD can be written once we have unambiguous answers/choices for:

1) **Provider lock**: Vercel + (Render or alternative) is confirmed, including preview environment expectations.
2) **Domain plan**: exact URLs for frontend + backend + Clerk allowed origins/redirect URLs.
3) **DB approach**: migrations vs `create_all`, and the concrete `DATABASE_URL` format/SSL expectation.
4) **Bootstrap plan**: how prod DB gets initial call definitions (manual one-off vs automated seed job).
5) **Env matrix**: final list of env vars per environment (local/dev/preview/prod) for both services, including secret-rotation expectations.
6) **Health checks**: which endpoints exist and what “green” means (liveness vs readiness/DB).
7) **Verification split**: a written deploy verification checklist that is separate from local verification.
8) **Timeout budget**: explicit Vercel runtime max + FastAPI timeout + “submit review” p95 target.

## Revision History

- **v0.1** (2026-02-10): Initial Phase 0 brainstorming for MVP deployment wiring (providers, env mapping, domains/CORS, health checks, Postgres/seed risks, and PRD readiness gates).
- **v0.2** (2026-02-12): Incorporated senior critique; added Vercel timeout alignment as a first-class risk/decision, resolved clarification questions with MVP-fast defaults (prod-only, backend provider URL, no Alembic, manual seed runbook), and added recommended sequencing slices to keep deployment shippable.
