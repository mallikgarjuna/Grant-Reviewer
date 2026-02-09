# PRD 8.0A: Frontend UI Slice (Next.js App + MDX + BFF Adapter)

**Date**: 2026-02-09
**Task ID**: 8.0A
**Pipeline Phase**: Phase 1 (PRD)
**Status**: Draft (v0.1)
**Last Updated**: 2026-02-09

## Summary

Build the first end-to-end web UI for Grant Reviewer using Next.js (App Router) with a strict BFF boundary to the existing FastAPI backend. The MVP delivers:
- Public marketing + MDX blog for SEO discovery.
- Authenticated app flow to run snippet reviews.
- A BFF adapter layer that signs requests to FastAPI, enforces idempotency requirements, and maps canonical backend errors into UI-safe results.

This PRD is intentionally scoped to the minimum that enables Task 8.0A Phase 3 implementation and a usable MVP slice.

## Background / Context

- Backend contracts are already implemented (Task 8.0B): signed request headers, ownership checks, required `Idempotency-Key`, quota enforcement, kill switch, canonical errors.
- This task focuses on building the UI and the minimal Next-side plumbing required to consume those contracts safely.

Related artifacts:
- Phase 0 notes: `knowledge_base/logs/brainstorming-8.0A-frontend-ui.md`
- Contract PRD: `tasks/prd-8.0B-bff-contracts.md`

## Goals (MVP)

- Ship an authenticated app that can create and view reviews:
  - calls -> nodes -> snippet -> submit -> results
- Ensure browser never calls FastAPI directly; Next server routes act as BFF.
- Ensure resubmits and refreshes are safe (idempotency key persistence) and do not accidentally multiply cost.
- Keep `/app/*` private and not indexed, while marketing/blog are indexable.

## Non-Goals (Explicitly Deferred)

- Payments, subscriptions, paid tiers, org accounts, sharing links.
- Background jobs, polling, streaming responses.
- Repo-wide lint debt cleanup (tracked as Task 8.1+).
- Full analytics integration (vendor wiring); keep placeholder only.
- E2E suite (Playwright) beyond minimal guardrails.

## Users / Primary Use Cases

- Public visitor reads a marketing page or blog post and clicks “Try it”.
- Authenticated user runs a snippet review and sees results.
- Authenticated user opens a deep link to an existing review and sees results (or “not found” if not owned).

## UX Scope

### Public (SEO)
- `/` marketing landing page
- `/blog/*` MDX articles

### App (auth required)
- `/app` submission flow (call picker, node picker, snippet input, submit)
- `/app/reviews/[review_id]` results page

Auth behavior:
- Unauthenticated user hitting `/app/*` is redirected to Clerk sign-in and returned to the intended destination after login.

## Technical Scope

### BFF boundary (hard requirement)

- Browser talks only to Next.js routes/actions.
- Next.js server code calls FastAPI server-to-server.
- FastAPI base URL is server-only; no `NEXT_PUBLIC_*` exposure.

### Adapter layer (first-class deliverable)

Implement a single adapter module that is the only place that knows:
- `FASTAPI_BASE_URL`
- how to sign requests (HMAC with `BFF_SHARED_SECRET`)
- how to parse canonical errors (`{error:{code,message,details}}`)

The adapter returns UI-safe types:
- `Ok<T>` for success
- `Err<ApiError>` for canonical errors

### Signing (locked decision)

The adapter signs the exact request bytes it sends to FastAPI:
- Build body bytes once.
- Compute signature over `sha256(body_bytes)`.
- Send those same `body_bytes` in the request.

### Idempotency (locked decision)

FastAPI requires `Idempotency-Key` for `POST /reviews`. Next must implement:
- Attempt persistence in `sessionStorage`:
  - draft: `{call_id,node_id,snippet_text}`
  - `idempotency_key`, `payload_sha256`, `created_at_ms`
- Payload hashing normalization:
  - normalize newlines (`\r\n` -> `\n`)
  - trim leading/trailing whitespace
- Reuse rule:
  - unchanged payload -> reuse stored key (safe retry/refresh)
  - changed payload -> generate new key (new attempt)
- FAILED retry rule:
  - always generate a new key
  - prefill inputs for convenience

### Synchronous submission UX (MVP)

- `POST /reviews` is synchronous.
- UI shows an in-flight state and disables submit while in-flight.
- After ~40s show a “still working, refresh safely” message.
- No automatic retries.

### SEO privacy guardrails (MVP)

- `/app/*` should not be indexed:
  - `robots.txt` disallows `/app/`
  - `X-Robots-Tag: noindex` for `/app/*`
- Add a lightweight verification guardrail (script/test) that asserts:
  - `robots.txt` contains the disallow rule
  - `/app/*` responses include `X-Robots-Tag: noindex`

## Error Handling Requirements (UI)

UI should branch on canonical `error.code`, not HTTP status.

Required UX handling:
- `UNAUTHORIZED`: redirect to sign-in (or show sign-in CTA).
- `QUOTA_EXCEEDED`: show limit reached and reset time if present in `details.reset_at`.
- `REVIEWS_DISABLED`: show maintenance state.
- `VALIDATION_ERROR`, `SNIPPET_TOO_LONG`, `NO_EXPECTATIONS`, etc.: show inline form errors.
- `REVIEW_NOT_FOUND`: show “Not found”.

Review states:
- `FAILED` is rendered as a state (with retry CTA), not as an exception screen.

## Acceptance Criteria

### A. App flow
- User can load `/app`, select call and node, paste snippet, submit, and navigate to results.
- User can open `/app/reviews/[review_id]` directly and see the same result.
- Cross-user review access results in “Not found” (backend returns masked 404).

### B. Cost/abuse safety
- UI never calls FastAPI directly from the browser.
- All FastAPI calls are signed through the adapter.
- `POST /reviews` always includes `Idempotency-Key`.
- Refresh + resubmit with unchanged draft reuses the same key (no duplicate spend).
- FAILED retry uses a new key.

### C. SEO/privacy
- Marketing/blog routes are indexable.
- `/app/*` is not indexable via both `robots.txt` and `X-Robots-Tag: noindex`.
- A lightweight verification step exists for the above.

### D. UX resilience (sync)
- Submit is disabled during in-flight.
- After ~40s, user sees a clear “still working / refresh safely” message.
- No automatic retry behavior exists.

## Dependencies

- Clerk configuration for Next.js (sign-in, callbacks, and redirect preservation).
- Backend env shared secret alignment:
  - `BFF_SHARED_SECRET` in FastAPI
  - same secret available to Next server-side code

## Out of Scope Ideas (Backlog)

- Public share links, org/team accounts, paid tiers.
- Background job processing with polling/streaming.
- Proactive quota introspection endpoint and UI.
- Strict ESLint rules that hard-block non-adapter FastAPI calls (after first slice is stable).

## Verification Plan (Phase 3)

- Manual smoke:
  - submit review once -> results
  - refresh `/app` with same draft -> resubmit uses same idempotency key
  - FAILED retry -> new key (verify new review id)
  - deep link `/app/reviews/[id]` without prior submit
- Lightweight SEO check:
  - confirm `/robots.txt` and `/app/*` `X-Robots-Tag` behavior

## Revision History

- **v0.1** (2026-02-09): Initial PRD for the 8.0A UI slice; incorporates locked Phase 0 decisions on idempotency persistence, signing exact bytes, sync UX, and SEO noindex guardrails.

