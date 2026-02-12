# PRD 8.0C: MVP Deployment Wiring (Vercel + Clerk + BFF, Render FastAPI, Render Postgres)

**Status**: Draft (v0.1 - Initial)  
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

**Acceptance Criteria**
- A single “max duration” budget is explicitly chosen and documented:
  - Vercel route handler max duration (and runtime type)
  - FastAPI `REVIEW_TIMEOUT_SECONDS`
- Deploy verification includes one end-to-end submit that completes within the budget.

**MVP fallback if platform budget is too low**
- Reduce `REVIEW_TIMEOUT_SECONDS` for production until it fits, and/or
- Temporarily run deploy verification in `LLM_MODE=stub` to validate wiring without external latency/cost.

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

### R2: Postgres support in backend (no SQLite-only assumptions)

**Acceptance Criteria**
- Backend uses `DATABASE_URL` when present; does not require local filesystem paths to exist.
- Backend starts cleanly against managed Postgres and creates tables (`create_all`) on startup.

### R3: Health checks (liveness + DB readiness)

**Acceptance Criteria**
- `GET /health` stays a fast liveness check.
- A DB readiness check exists (either `GET /health/db` or enriched `/health`) that:
  - performs a fast “can connect” query
  - times out quickly
  - returns `{ok:true}` only when DB is reachable

### R4: Bootstrap runbook (manual seed is OK, undocumented seed is not)

**Acceptance Criteria**
- A documented runbook exists for seeding at least one call YAML into prod DB.
- Verification steps confirm calls exist post-ingest (via API and/or DB query).

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

## Non-Goals (Explicit)

- Preview environment parity (Vercel previews + Clerk + backend)
- IaC (Terraform/Pulumi), CI/CD automation
- Alembic migrations
- Full observability stack (Sentry/OTel/metrics) beyond provider logs
- Custom backend domain (`api.<domain>`)

---

## Revision History

- **v0.1** (2026-02-12): Initial PRD for MVP deployment wiring (providers/env mapping, Postgres requirement, timeout alignment, health checks, bootstrap runbook, deploy verification checklist).

