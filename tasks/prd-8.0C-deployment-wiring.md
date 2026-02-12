# PRD 8.0C: MVP Deployment Wiring (Vercel + Clerk + BFF, Render FastAPI, Render Postgres)

**Status**: Draft (v0.3 - Revised)  
**Date**: 2026-02-12  
**Phase**: Phase 1 (PRD)  
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-8.0C-deployment-wiring.md`  

---

## Goal (MVP)

Deploy a production-ish environment that supports the existing end-to-end flow (8.0A + 8.0B):
- Public marketing/blog routes on Next.js (Vercel)
- Authenticated `/app/*` routes behind Clerk
- Browser → Next.js BFF → FastAPI server-to-server only (no direct browser → FastAPI dependency)
- FastAPI persisted state on managed Postgres (no SQLite drift)

This task is deployment wiring and operational correctness, not new product features.

---

## Decisions Locked (MVP-fast)

- **Hosting**: Vercel (Next.js) + Render (FastAPI) + Render Postgres
- **Environments**: prod-only for 8.0C (no preview parity requirement)
- **Domains**:
  - frontend: custom domain optional; `*.vercel.app` acceptable for MVP
  - backend: keep Render service URL (no custom `api.<domain>` for MVP)
- **CORS**: disabled on FastAPI (BFF makes browser CORS unnecessary)
- **Docs**: FastAPI `/docs` can be public; protected endpoints still require BFF signature
- **Migrations**: no Alembic yet; use `SQLModel.metadata.create_all()` for MVP speed
- **Bootstrap**: one-time manual ingest into prod DB is acceptable (documented runbook required)

---

## Critical Requirement: Timeout Alignment (Must-Have)

The BFF request path must not exceed the platform runtime budget:
browser → Vercel route handler `POST /api/bff/reviews` → FastAPI `POST /reviews` (sync).

### Concrete MVP defaults (lock now)

- **Vercel**: set the BFF create route handler to Node runtime with a long max duration:
  - file: `frontend/src/app/api/bff/reviews/route.ts`
  - config: `runtime="nodejs"`, `maxDuration=60`
- **FastAPI**: set production `REVIEW_TIMEOUT_SECONDS=25` (buffer for network + auth + serialization overhead).

### Acceptance Criteria

- The timeout budget is explicitly documented as:
  - Vercel `maxDuration` for `POST /api/bff/reviews`
  - FastAPI `REVIEW_TIMEOUT_SECONDS`
- Deploy verification includes one end-to-end submit that completes within the budget (stub first; openai after wiring proof).

**MVP fallback if platform budget is too low**
- Reduce `REVIEW_TIMEOUT_SECONDS` for production until it fits, and/or
- Temporarily run deploy verification in `LLM_MODE=stub` to validate wiring without external latency/cost.
- If the Vercel plan cannot support a duration compatible with synchronous LLM reviews, treat async execution (jobs + polling) as a follow-up task (explicitly out-of-scope for 8.0C).

---

## Requirements

### R1: Secrets and env mapping (no secrets in repo)

**Frontend (Vercel env vars)**
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `FASTAPI_BASE_URL` (server-only; Render service URL)
- `BFF_SHARED_SECRET` (server-only; must match backend)

**Backend (Render env vars)**
- `DATABASE_URL` (Postgres; include SSL requirements explicitly)
- `BFF_SHARED_SECRET` (must match frontend)
- `OPENAI_API_KEY` (only when running real LLM)
- `LLM_MODE` (`stub` or `openai`)
- `REVIEWS_ENABLED`, `FREE_DAILY_REVIEW_LIMIT`, `REVIEW_TIMEOUT_SECONDS`

**Acceptance Criteria**
- `BFF_SHARED_SECRET` is different between local dev and prod.
- FastAPI rejects protected calls when `BFF_SHARED_SECRET` is missing/mismatched.

### R2: Render deployment mechanics are explicit (avoid “guess the platform”)

**Decision (MVP)**: use Render’s native Python runtime first (no Docker/IaC in 8.0C).

**Acceptance Criteria**
- Render FastAPI service has explicit settings documented (root dir, build, start).
- Backend binds `0.0.0.0:$PORT` (Render requirement).
- Backend runs as a single instance initially.

### R2: Postgres support in backend (no SQLite-only assumptions)

**Acceptance Criteria**
- Backend uses `DATABASE_URL` when present; does not require local filesystem paths to exist.
- Backend starts cleanly against managed Postgres and creates tables (`create_all`) on startup.
- Backend accepts Render-provided DB URLs:
  - supports `postgres://...` by normalizing to a SQLAlchemy-compatible scheme (e.g., `postgresql+psycopg://...`)
  - SSL requirements are explicit (`sslmode=require`)

### R3: Health checks (liveness + DB readiness)

**Acceptance Criteria**
- `GET /health` stays a fast liveness check.
- A DB readiness check exists (either `GET /health/db` or enriched `/health`) that:
  - performs a fast “can connect” query
  - times out quickly
  - returns `{ok:true}` only when DB is reachable

### R4: Bootstrap runbook (manual seed is OK, undocumented seed is not)

The backend currently requires:
- at least 1 call + nodes + expectations (so `/app` is usable)
- at least 1 active `PromptTemplate` (otherwise `POST /reviews` fails)

**Acceptance Criteria**
- A documented runbook exists for:
  - ensuring an active `PromptTemplate` exists
  - ingesting at least one call YAML into prod DB
- Verification steps confirm:
  - `GET /calls` returns at least 1 call
  - `GET /calls/{call_id}/nodes` returns nodes
  - an end-to-end submit via `/api/bff/reviews` succeeds in stub mode

---

## Deploy Verification Checklist (Separate From Local Verification)

**Backend**
- `GET <fastapi-base-url>/health` returns `{ok:true}`
- DB readiness check passes
- Direct (unsigned) requests to protected endpoints fail

**Frontend**
- `GET <frontend-base-url>/` renders
- `/app` redirects to Clerk sign-in when logged out
- After sign-in, can run one review end-to-end via BFF

**Timeout**
- End-to-end `/api/bff/reviews` submit completes within the documented budget

Local verification remains `scripts/verify_local_8_0A.sh` and is not replaced by deploy verification.

---

## MVP Rollout Staging (Recommended)

To ship faster and reduce cost/latency noise while wiring infra:

1) **Wiring proof (stub)**: deploy with `LLM_MODE=stub` and complete deploy verification end-to-end.
2) **Real service (openai)**: set `LLM_MODE=openai` + `OPENAI_API_KEY` and run one real end-to-end review to confirm timeouts and quotas behave in prod.

Notes:
- OpenAI mode incurs cost; keep the kill switch (`REVIEWS_ENABLED=false`) ready if needed.
- This staging does not change the product contract; it’s an operational safety step.

---

## Operational Constraints (MVP)

- Run the backend as a **single Render instance** for initial launch.
- Rationale: we are using `create_all()` (no migrations) and want to avoid DDL races and unknown connection pressure until the system is stable.

---

## Bootstrap Runbook (Manual Seed Required)

Manual seed is acceptable for MVP, but it must be written down and repeatable.

**Runbook must include**
- The exact command to ingest at least one YAML call definition into prod DB.
- Where the command is executed (e.g., a Render shell / one-off exec against the deployed code).
- Verification steps:
  - `GET /calls` returns at least 1 call
  - `GET /calls/{call_id}/nodes` returns nodes
  - an active `PromptTemplate` exists (required by backend)

---

## Non-Goals (Explicit)

- Preview environment parity (Vercel previews + Clerk + backend)
- IaC (Terraform/Pulumi), CI/CD automation
- Alembic migrations
- Full observability stack (Sentry/OTel/metrics) beyond provider logs
- Custom backend domain (`api.<domain>`)
- Async execution (background jobs + polling)
- Docker-based deployment and Render blueprints (`render.yaml`) (follow-up if native build is unreliable)

---

## Revision History

- **v0.1** (2026-02-12): Initial PRD for MVP deployment wiring (providers/env mapping, Postgres requirement, timeout alignment, health checks, bootstrap runbook, deploy verification checklist).
- **v0.2** (2026-02-12): Locked concrete timeout defaults (`maxDuration=60`, `REVIEW_TIMEOUT_SECONDS=25`), added staged rollout (stub → openai), clarified MVP operational constraint (single backend instance), and tightened the manual seed runbook requirements.
- **v0.3** (2026-02-12): Added explicit Render deployment mechanics requirement and corrected bootstrap definition to include the required `PromptTemplate` (not just YAML ingest). Added Postgres URL normalization + SSL expectations.
