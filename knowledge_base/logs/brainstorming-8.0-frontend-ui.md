# Brainstorming 8.0: Frontend UI + Launch Architecture (Next.js + BFF)

**Date**: 2026-02-08  
**Task ID**: 8.0  
**Pipeline Phase**: Phase 0 (Brainstorming)  

## Goal

Ship a v1 web experience that:
- Drives discovery via SEO (marketing pages + MDX articles).
- Converts readers into users who can run snippet reviews.
- Controls LLM cost/abuse via login + quotas from day 1.

## Proposed v1 Architecture (Decision Direction)

- **Frontend**: Next.js (App Router) + TypeScript/React + Tailwind + shadcn/ui + **MDX** for articles.
- **Auth**: **Clerk** (magic link), login required to submit reviews.
- **Backend**: existing FastAPI service remains the LLM execution API.
- **Pattern**: **BFF** — browser calls Next.js routes; Next.js calls FastAPI server-to-server.
- **DB**: **Managed Postgres** (Render Postgres for production).
- **Hosting (split)**: Next.js on Vercel; FastAPI + Postgres on Render.

Related architectural decisions captured in `knowledge_base/logs/decisions.md` (AD 8.1–8.6).

## Why BFF for this app

- Avoids cross-origin cookie/CORS complexity between Vercel and Render.
- Keeps FastAPI off the public browser surface (reduced abuse surface).
- Central place (Next) to implement session checks, UX-specific caching, and request shaping.
- Sets up future mobile/public API as an intentional, separate choice.

## MVP UX (first end-to-end slice)

### Primary user flow
1) Land on marketing page / article.
2) Click “Try it” → auth gate (Clerk).
3) In app:
   - select **funding call**
   - select **proposal section**
   - paste **snippet text**
   - submit review
4) View results:
   - overall summary + rating
   - ordered review cards (stable order)

### Pages (initial)
- `/` marketing (SEO)
- `/blog/*` MDX articles (SEO)
- `/app` main flow (auth required)
- `/app/reviews/[review_id]` results deep link (auth required)

## Backend API usage (existing)

FastAPI endpoints already exist:
- `GET /calls`
- `GET /calls/{call_id}/nodes`
- `POST /reviews`
- `GET /reviews/{review_id}`

Next.js creates BFF route handlers that call these endpoints server-to-server:
- `GET /bff/calls` → FastAPI `GET /calls`
- `GET /bff/calls/{call_id}/nodes` → FastAPI `GET /calls/{call_id}/nodes`
- `POST /bff/reviews` → FastAPI `POST /reviews`
- `GET /bff/reviews/{review_id}` → FastAPI `GET /reviews/{review_id}`

## Auth & Abuse Control (MVP)

### Login required
- Blog + marketing pages are public.
- App submit endpoints require Clerk-authenticated session.

### Quotas-first
- Enforce free-tier quotas in backend (source of truth) keyed by `clerk_user_id`.
- Optional: add coarse IP-based rate limiting on the backend edge as a second line of defense.

### Service-to-service request signing
To prevent direct abuse against FastAPI (bypassing Next/Clerk), add a lightweight “BFF signature”:
- Next adds `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature` (HMAC) on calls to FastAPI.
- FastAPI validates signature + timestamp and rejects missing/invalid signatures.

This keeps FastAPI “private by contract” even if the URL is discovered.

## Data Model Implications (DB)

Moving to Postgres enables:
- Durable user identity mapping (`clerk_user_id` → internal `User` row).
- Quota tracking (daily/monthly usage counts).
- Future Stripe subscription fields without schema contortions.

Local dev can keep SQLite initially, but production should use Postgres.

## SEO / Content Plan (MDX)

MDX articles live in-repo for fast iteration:
- topic clusters (e.g., “ERC Consolidator Grant proposal tips”, “rubric-grounded grant writing”)
- internal linking: article → relevant app entry point
- clear CTAs: “Try the rubric review”

## Open Questions / Risks

- Quota semantics: per-day reviews vs per-month; per-char caps; retry policy on failures.
- Latency UX: loading states, request timeouts, and error messaging for LLM failures.
- Deployment secrets: coordinating `FASTAPI_BASE_URL`, `BFF_SHARED_SECRET`, and Clerk keys across Vercel/Render.
- DB migration plan: switching SQLModel engine/config from SQLite to Postgres cleanly (and whether to introduce Alembic now vs later).

