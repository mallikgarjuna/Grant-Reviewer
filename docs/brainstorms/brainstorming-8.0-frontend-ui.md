# Brainstorming 8.0: Frontend UI + Launch Architecture (Next.js + BFF)

**Date**: 2026-02-08  
**Task ID**: 8.0  
**Pipeline Phase**: Phase 0 (Brainstorming)  
**Status**: Draft (v0.3 - Revised)  
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

Related architectural decisions captured in `docs/logs/decisions.md` (AD 8.1–8.6).

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

### Enforcement (mechanical, MVP)
- Implement a single mandatory adapter module in the Next.js codebase (e.g., `src/lib/bff/*`) that:
  - is the **only** place that knows the FastAPI base URL
  - wraps all server-to-server calls
  - parses canonical errors and returns typed results
- Rule: UI components must not call FastAPI directly (no direct `fetch(FASTAPI_BASE_URL, ...)`).
  - UI components talk to Next route handlers/server actions, which talk to the BFF adapter.

### Error taxonomy (for UX consistency)
FastAPI errors should be classifiable by `error.code`:
- **User/actionable**: validation, snippet-too-long, no-expectations, node-not-in-call
- **Quota/billing**: quota exceeded / reviews disabled (kill switch)
- **Retryable infra**: upstream timeout / transient network / gateway failures (rare; BFF may suggest retry)
- **Non-retryable LLM**: invalid structured response (treat as failed; show “try again later” + support link)

Next.js should:
- render friendly messages for **user/actionable** and **quota/billing** codes
- avoid automatic retries that can multiply LLM cost

### Separate “errors” from “states” (clarification)
- **API errors** describe request rejection or infrastructure failures (canonical error shape).
- **Review status** (`PENDING`, `COMPLETED`, `FAILED`) describes lifecycle outcome once a review exists.
- `GET /reviews/{id}` should be safe to call repeatedly; once created, it should return `200` (subject to ownership checks), regardless of status.

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

MVP quota policy (explicit, temporary):
- Quota is consumed when an LLM execution attempt begins (i.e., when FastAPI accepts a new idempotency key for processing).
- Failures after acceptance do not refund quota in v1 (tradeoff: simpler + predictable billing model; can revisit later).

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

Additional constraints (MVP):
- **Payload mismatch rule**: same user + same idempotency key + different payload → `IDEMPOTENCY_PAYLOAD_MISMATCH` (hard error).
- **TTL**: idempotency keys expire after 24h (MVP default; configurable later).

Policy (MVP recommendation):
- Quota is consumed when FastAPI accepts a new idempotency key for processing (LLM attempt).
- Replays with the same key do not consume additional quota.

## Data Model Implications (DB)

Moving to Postgres enables:
- Durable user identity mapping (`clerk_user_id` → internal `User` row).
- Quota tracking (daily/monthly usage counts).
- Future Stripe subscription fields without schema contortions.

Avoid SQLite/Postgres split: use Postgres locally and in prod to prevent schema drift surprises.

## Review ownership & access control (MVP invariants)

- Reviews are private to the submitting user in v1.
- FastAPI must enforce ownership on all review reads:
  - `GET /reviews/{review_id}` must verify the caller identity (via BFF signature + external user id) and ensure the review belongs to that user.
- Next.js must not rely on “unguessable IDs” for security.

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

## Postgres + connection pooling (MVP note)

- With BFF, Next.js does **not** connect to Postgres; only FastAPI does. This limits connection pressure.
- MVP assumption: low concurrency. Prefer a small number of FastAPI workers and conservative SQLAlchemy pool sizing.
- If Render Postgres connection limits become an issue, introduce pooling (e.g., pgBouncer) as a later hardening step.

## Minimal analytics (MVP placeholder)

Track just enough to learn what converts:
- marketing/blog page views
- CTA clicks (“Try it”, “Sign in”, “Run review”)
- review submit started/succeeded/failed (by error code category)

## Open Questions / Risks

- Quota semantics: per-day reviews vs per-month; per-char caps; what happens on failures (still consumes quota?).
- Latency UX: loading states, request timeouts, and user guidance on retrying (idempotency required).
- Deployment secrets: coordinating `FASTAPI_BASE_URL`, `BFF_SHARED_SECRET`, and Clerk keys across Vercel/Render.
- Postgres plan: local dev Postgres setup + whether to introduce Alembic now vs later.

## Suggested sequencing (reduce scope thrash)

Enforce execution order to reduce rework and cost risk:
1) **8.0B Contracts**: BFF adapter, error/state separation, idempotency, quota errors + kill switch.
2) **8.0A UX Slice**: pages + components + MDX + basic app flow (calls → nodes → submit → results).
3) **8.0C Deployment**: secrets, environments, Vercel/Render wiring, Postgres provisioning.

## Revision History

- **v0.1** (2026-02-08): Initial Phase 0 brainstorming draft.
- **v0.2** (2026-02-08): Tightened BFF contract; clarified quota/idempotency/lifecycle, SEO rules, kill switch, and Postgres-local guidance.
- **v0.3** (2026-02-08): Added mechanical BFF adapter enforcement, ownership invariants, idempotency mismatch + TTL, explicit MVP quota policy, pooling note, and minimal analytics placeholder.
