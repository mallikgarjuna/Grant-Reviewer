# Brainstorming 8.0: Frontend UI + Launch Architecture (Next.js + BFF)

**Date**: 2026-02-08  
**Task ID**: 8.0  
**Pipeline Phase**: Phase 0 (Brainstorming)  
**Status**: Draft (v0.2 - Revised)  
**Last Updated**: 2026-02-08  

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
- **DB**: **Managed Postgres** (provider: Render Postgres currently preferred for MVP; revisit if constraints emerge).
- **Hosting (split)**: Next.js on Vercel; FastAPI + Postgres on Render.

Related architectural decisions captured in `knowledge_base/logs/decisions.md` (AD 8.1–8.6).

## Why BFF for this app

- Avoids cross-origin cookie/CORS complexity between Vercel and Render.
- Keeps FastAPI off the public browser surface (reduced abuse surface).
- Central place (Next) to implement session checks, UX-specific caching, and request shaping.
- Sets up future mobile/public API as an intentional, separate choice.

## Explicit BFF Contract (Must-Haves)

### Responsibility split (hard rule)
- **FastAPI decides and returns domain facts only**:
  - validates invariants (`CALL_NOT_FOUND`, `NODE_NOT_IN_CALL`, etc.)
  - enforces quotas
  - performs LLM execution
  - persists immutable review snapshots + cards
  - returns canonical errors `{error:{code,message,details}}` and structured review results
- **Next.js decides UX**:
  - auth gating, redirects, and post-login routing
  - loading/timeout UX, retries (only via idempotency)
  - mapping canonical errors → user-facing copy + CTA
  - normalizing responses for UI components (a small “BFF normalization” layer)

### Error taxonomy (for UX consistency)
FastAPI errors should be classifiable by `error.code`:
- **User/actionable**: validation, snippet-too-long, no-expectations, node-not-in-call
- **Quota/billing**: quota exceeded / reviews disabled (kill switch)
- **Retryable infra**: upstream timeout / transient network / gateway failures (rare; BFF may suggest retry)
- **Non-retryable LLM**: invalid structured response (treat as failed; show “try again later” + support link)

Next.js should:
- render friendly messages for **user/actionable** and **quota/billing** codes
- avoid automatic retries that can multiply LLM cost

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
- **FastAPI is the source of truth** for quota allow/deny decisions keyed by `clerk_user_id`.
- Next.js owns the **user-facing UX** (remaining quota messaging, upgrade CTA later).
- Optional: add coarse IP-based rate limiting on the backend edge as a second line of defense.

Quota contract (desired):
- On deny: `QUOTA_EXCEEDED` with `details` like `{limit, remaining, reset_at}`.
- On allow: proceed; idempotent replays must not consume quota again.

### Service-to-service request signing
To prevent direct abuse against FastAPI (bypassing Next/Clerk), add a lightweight “BFF signature”:
- Next adds `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature` (HMAC) on calls to FastAPI.
- FastAPI validates signature + timestamp and rejects missing/invalid signatures.

This keeps FastAPI “private by contract” even if the URL is discovered.

### Global cost kill switch (must-have)
- Add env kill switch in FastAPI: `REVIEWS_ENABLED=false` returns `REVIEWS_DISABLED` (maintenance/circuit-breaker).
- Next.js should show a dedicated maintenance state when disabled (no confusing “something went wrong”).

## Review Lifecycle + Idempotency (must-have before great UX)

### Lifecycle states
Current domain has `Review.status` (`PENDING`, `COMPLETED`, `FAILED`) and should remain the canonical backend state.
UI also has ephemeral client states:
- `draft` (not submitted)
- `submitting/processing` (request in flight)
- `completed` / `failed` (from backend)

### Idempotency for `POST /reviews`
To support safe retries/timeouts and prevent accidental double-charges:
- Next.js generates an idempotency key per user submission attempt.
- Next.js sends it to FastAPI (e.g., `Idempotency-Key` header).
- FastAPI guarantees: **same user + same idempotency key + same payload → same review**.

Policy (MVP recommendation):
- Quota is consumed when FastAPI accepts a new idempotency key for processing (LLM attempt).
- Replays with the same key do not consume additional quota.

## Data Model Implications (DB)

Moving to Postgres enables:
- Durable user identity mapping (`clerk_user_id` → internal `User` row).
- Quota tracking (daily/monthly usage counts).
- Future Stripe subscription fields without schema contortions.

Avoid SQLite/Postgres split: use Postgres locally and in prod to prevent schema drift surprises.

## SEO / Content Plan (MDX)

MDX articles live in-repo for fast iteration:
- topic clusters (e.g., “ERC Consolidator Grant proposal tips”, “rubric-grounded grant writing”)
- internal linking: article → relevant app entry point
- clear CTAs: “Try the rubric review”

## SEO + Auth + Sharing (MVP decisions)

- **Marketing/blog routes are indexable**.
- **App routes are not indexable**:
  - add `X-Robots-Tag: noindex` on `/app/*`
  - ensure `robots.txt` disallows `/app/`
- **Post-login redirect**: preserve intended destination (e.g., `/app/reviews/[review_id]`) so shared/internal links remain meaningful after auth.
- **Sharing model (MVP)**: reviews are private to the submitting user (no public share links in v1).
  - future option: share tokens / “shareable link” objects with explicit access control

## Open Questions / Risks

- Quota semantics: per-day reviews vs per-month; per-char caps; what happens on failures (still consumes quota?).
- Latency UX: loading states, request timeouts, and user guidance on retrying (idempotency required).
- Deployment secrets: coordinating `FASTAPI_BASE_URL`, `BFF_SHARED_SECRET`, and Clerk keys across Vercel/Render.
- Postgres plan: local dev Postgres setup + whether to introduce Alembic now vs later.

## Suggested sequencing (reduce scope thrash)

Split Phase 1/2 thinking into three “tracks” (can still be one Task 8.0 if desired):
- **8.0A UX Slice**: pages + components + MDX + basic app flow (calls → nodes → submit → results).
- **8.0B Contracts**: BFF normalization, idempotency, quota error semantics, kill switch.
- **8.0C Deployment**: secrets, environments, Vercel/Render wiring, Postgres provisioning.

## Revision History

- **v0.1** (2026-02-08): Initial Phase 0 brainstorming draft.
- **v0.2** (2026-02-08): Tightened BFF contract; clarified quota/idempotency/lifecycle, SEO rules, kill switch, and Postgres-local guidance.
