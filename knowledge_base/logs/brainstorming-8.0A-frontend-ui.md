# Brainstorming 8.0A: Frontend UI Slice (Next.js App + MDX + BFF Adapter)

**Date**: 2026-02-09
**Task ID**: 8.0A
**Pipeline Phase**: Phase 0 (Brainstorming)
**Status**: Draft (v0.7 - Revised)
**Last Updated**: 2026-02-09

## Goal (MVP)

Ship the first usable web UI that:
- Lets an authenticated user run a snippet review end-to-end (calls -> nodes -> submit -> results).
- Keeps FastAPI private behind the BFF boundary (browser never calls FastAPI directly).
- Supports SEO discovery via marketing + MDX content, while keeping `/app/*` private and non-indexed.

This task builds on contracts already implemented in 8.0B (BFF signature headers, ownership checks, required `Idempotency-Key`, quotas, kill switch, canonical errors).

## MVP Decisions Locked Now (To Remove Footguns)

These are the “decision closures” needed before Phase 1 PRD so UI work doesn’t drift.

### Idempotency key persistence (submit + refresh safety)

MVP choice: persist the current submission attempt in `sessionStorage` (draft + attempt metadata) until a new submission is started.
- Store:
  - draft: `{call_id, node_id, snippet_text}`
  - `idempotency_key`
  - `payload_sha256` (hash of `{call_id,node_id,snippet_text}`)
  - `created_at_ms`
- On submit:
  - If payload hash matches the stored hash, reuse the stored key.
  - Otherwise generate a new key and overwrite the stored attempt.
- On refresh/navigation:
  - The user can safely resubmit; if inputs are unchanged in this browser session, the key is reused and FastAPI replay prevents duplicate spend.

This is intentionally session-scoped (not long-lived); deep sharing of “draft submits” is non-goal.

### Payload normalization for `payload_sha256` (avoid accidental “new attempt”)

MVP choice: normalize the payload before hashing to reduce churn from trivial edits.
- `snippet_text` normalization:
  - normalize newlines (`\r\n` -> `\n`)
  - trim leading/trailing whitespace
- Hash the normalized JSON payload of `{call_id,node_id,snippet_text}`.

This improves safety (fewer accidental new keys) at low complexity. The adapter owns this normalization so UI stays consistent.

### FAILED retry semantics (simple mental model)

MVP choice:
- Retrying after `FAILED` always creates a new attempt (new `Idempotency-Key`).
- Inputs are prefilled for convenience, but the retry is explicitly a new run.

### Client timeout messaging (sync UX hardening without async infra)

MVP choice:
- Keep `POST /reviews` synchronous.
- After ~40s of waiting, show a message:
  - “Still working. You can refresh safely. Don’t spam submit.”
- Do not auto-retry. If the user clicks submit again with unchanged inputs, the stored idempotency key is reused.
- While a submit is in-flight, keep submit disabled. After the timeout message appears, keep the button disabled and offer: “Edit inputs to start a new attempt.”

### Deep links to results

MVP choice:
- `/app/reviews/[review_id]` must support direct entry (deep link) and render:
  - unauthenticated -> Clerk sign-in, then redirect back
  - authenticated but not owned -> “Not found” (404 masked by backend)
  - authenticated and owned -> render `COMPLETED` or `FAILED` state

### BFF enforcement (remove easy footguns now)

MVP choice:
- `FASTAPI_BASE_URL` is server-only immediately (no `NEXT_PUBLIC_*` usage).
- Only the adapter module can read it.
- ESLint hard enforcement is staged, but env visibility is locked from day 1 to prevent accidental browser calls.

### Signing rule (avoid brittle auth failures)

MVP choice:
- The adapter must sign the exact request bytes it sends to FastAPI.
- Build body bytes once, then:
  - compute signature over `sha256(body_bytes)`
  - send those same `body_bytes` in the request

This prevents “same JSON, different bytes” failures due to re-serialization differences.

### Optional skill guardrails (MVP-friendly)

If you want additional implementation guardrails (without expanding scope), install these skills locally:
- `vercel-labs/agent-skills@vercel-react-best-practices` (Next.js/React guardrails)
- `addyosmani/web-quality-skills --skill accessibility` (accessibility baseline)

We treat them as guidance, not as requirements or new dependencies.

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
- Frontend tooling availability (Node/npm) can block execution in some environments; keep a “scaffold locally, commit generated files” fallback.

MVP mitigation: treat adapter correctness as the “hard gate” before building UI pages (sign exact bytes, canonical error parsing, idempotency helpers + invariant self-checks).

Tooling note (MVP):
- Before any `frontend/` work, run `nvm use v22.17.0` so `npm/npx` are available (when `nvm` exists in the environment).
- If `nvm` is not available in the current environment, scaffold/build locally and commit `frontend/` outputs to keep the repo moving.

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
  - If `FAILED`: show “Review failed” state with manual retry CTA (prefill inputs; retry uses a new idempotency key)

## SEO + Private App Routes (MVP)

- Marketing and blog routes are indexable.
- `/app/*` is not indexable:
  - `robots.txt` disallow `/app/`
  - add `X-Robots-Tag: noindex` for app routes (middleware or headers)

MVP guardrail:
- Add one explicit verification step (script/test) that asserts `/app/*` responses include `X-Robots-Tag: noindex` and `robots.txt` contains the disallow rule. Keep it lightweight (no full E2E suite yet).

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
- **v0.2** (2026-02-09): Locked MVP decisions for idempotency key storage, FAILED retry semantics, sync-timeout messaging, deep-link behavior, and immediate server-only env enforcement for the BFF boundary.
- **v0.3** (2026-02-09): Added draft persistence, payload normalization rules, “sign exact bytes” requirement, in-flight submit lock policy, and a lightweight SEO noindex verification guardrail.
- **v0.4** (2026-02-09): Added optional skill guardrails recommendations for MVP implementation (Next/React best practices and accessibility).
- **v0.5** (2026-02-09): Updated skill guardrails to match installed skills (Vercel best practices + web-quality accessibility).
- **v0.6** (2026-02-09): Added explicit execution/tooling risk and locked “adapter invariants first” as the MVP mitigation before UI work.
- **v0.7** (2026-02-09): Added explicit `nvm use v22.17.0` tooling note for Phase 3 frontend work, plus fallback if `nvm` is unavailable.
