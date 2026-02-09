# Brainstorming 8.0A: Frontend UI Slice (Next.js App + MDX + BFF Adapter)

**Date**: 2026-02-09
**Task ID**: 8.0A
**Pipeline Phase**: Phase 0 (Brainstorming)
**Status**: Draft (v0.1)
**Last Updated**: 2026-02-09

## Goal (MVP)

Ship the first usable web UI that:
- Lets an authenticated user run a snippet review end-to-end (calls -> nodes -> submit -> results).
- Keeps FastAPI private behind the BFF boundary (browser never calls FastAPI directly).
- Supports SEO discovery via marketing + MDX content, while keeping `/app/*` private and non-indexed.

This task builds on contracts already implemented in 8.0B (BFF signature headers, ownership checks, required `Idempotency-Key`, quotas, kill switch, canonical errors).

## What’s Already Locked (From 8.0 / 8.0B)

- Frontend stack direction: Next.js (App Router) + TS/React + Tailwind + shadcn/ui + MDX.
- Auth: Clerk; login required for app usage.
- Pattern: browser -> Next.js (BFF routes) -> FastAPI (server-to-server).
- FastAPI requirements that UI/BFF must satisfy:
  - Signed headers: `X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature` (HMAC with `BFF_SHARED_SECRET`)
  - `Idempotency-Key` header on `POST /reviews`
  - Quota and kill switch failures are canonical errors (`QUOTA_EXCEEDED`, `REVIEWS_DISABLED`)

## 8.0A Scope (MVP)

- Next.js scaffold (App Router) + basic layout, routing, and auth gating.
- Marketing pages + MDX blog routes for SEO.
- App pages for the vertical slice:
  - `/app` (call picker, node picker, snippet input, submit)
  - `/app/reviews/[review_id]` (results)
- BFF adapter layer (deferred item from 8.0B.7) implemented early as “8.0A.0 scaffolding”:
  - `src/lib/bff/*` owns FastAPI calling, signing, and canonical error parsing
  - UI never knows FastAPI base URL
- Minimal, predictable error UX based on `error.code`:
  - auth required
  - quota exceeded
  - reviews disabled
  - validation/snippet too long
  - review FAILED state displayed as a state (not a red “500” error)

## Non-Goals (Explicitly Deferred)

- Payments (Stripe), paid tiers, subscription management.
- Org/team accounts or sharing reviews between users.
- Async/background jobs, streaming responses, realtime progress.
- “Quota remaining” preflight endpoint (`GET /quota`) and proactive quota UI.
- Full lint debt cleanup (tracked separately as Task 8.1+).

## Key Risks (MVP-Focused)

- BFF boundary erosion (UI calling FastAPI directly over time).
- Mis-handling idempotency (accidental double submits causing extra quota/LLM cost).
- Confusing UX for quota/disabled/errors without overbuilding UI state machines.
- SEO and private app route indexing (must be explicit).

## Decisions To Make In 8.0A (Prefer MVP Defaults)

### D1: Execution model UX (sync request)
MVP assumption: `POST /reviews` is synchronous; user waits on submit.
- UX: show spinner state with “This can take up to ~30s”.
- Retry: manual-only; if the user retries, reuse the same idempotency key if they haven’t changed inputs.

### D2: Where the “BFF adapter” lives (mechanical enforcement)
Put all FastAPI calls in one adapter module and make it the only place that can read `FASTAPI_BASE_URL`.
- MVP enforcement: “server-only” env var + adapter-only rule documented.
- Lint enforcement: staged (warn first, hard error later) to preserve early velocity.

### D3: Minimal analytics (optional placeholder)
MVP: add a placeholder section in README for future analytics; do not wire vendors yet unless it’s trivial.

## Proposed File/Module Structure (Next.js)

This is intentionally small and enforcement-oriented:
- `src/lib/bff/client.ts` (Fetch wrapper + signing + error parsing)
- `src/lib/bff/endpoints.ts` (typed functions: `listCalls`, `listNodes`, `createReview`, `getReview`)
- `src/lib/bff/types.ts` (`ApiError`, `Result<T>`)
- `src/app/(marketing)/*` (public)
- `src/app/(app)/*` (auth required)

## BFF Adapter Contract (UI-Safe)

UI should never branch on HTTP status; it should branch on a typed error:
- `UNAUTHORIZED` -> redirect to sign-in
- `QUOTA_EXCEEDED` -> show “limit reached” with reset time (from `details.reset_at`)
- `REVIEWS_DISABLED` -> maintenance banner
- `VALIDATION_ERROR`, `SNIPPET_TOO_LONG`, etc. -> inline form errors

## Vertical Slice UX (MVP)

### `/app` (submit)
- Call select (populate from BFF)
- Node select (depends on call)
- Snippet textarea (char count, hard cap aligned to backend)
- Submit button:
  - Generates `Idempotency-Key` on first submit
  - Disables button while in-flight
  - On success: navigate to `/app/reviews/[review_id]`

### `/app/reviews/[review_id]` (results)
- Fetch review detail via BFF
- Render:
  - Overall rating + summary (if present)
  - Cards list (stable order)
  - If `FAILED`: show “Review failed” state with manual retry CTA (back to `/app` with inputs preserved if possible)

## SEO + Private App Routes (MVP)

- Marketing and blog routes are indexable.
- `/app/*` is not indexable:
  - `robots.txt` disallow `/app/`
  - add `X-Robots-Tag: noindex` for app routes (middleware or headers)

## Deferred Ideas (Keep For Later)

- Public sharing links with share tokens.
- Pre-submit “remaining quota” UI.
- Background jobs + polling (if synchronous proves too slow).
- Strict ESLint rules that hard-block direct FastAPI access outside adapter (once UI stabilizes).
- Playwright E2E tests (after the slice stabilizes).

## Immediate Next Step After Phase 0

Phase 1 PRD 8.0A should lock:
- Exact page list and UI acceptance criteria.
- Exact adapter surface and error mapping behavior.
- “8.0A.0 scaffolding” as the first implementation subtask (adapter + env setup + staged lint).

## Revision History

- **v0.1** (2026-02-09): Initial Phase 0 brainstorming for the 8.0A UI slice; explicitly includes deferred 8.0A.0 adapter/lint scaffolding from 8.0B.

