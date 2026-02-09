# Task 8.0A: Frontend UI Slice (Phase 2 Plan)

**Date**: 2026-02-09
**Task ID**: 8.0A
**Pipeline Phase**: Phase 2 (Task breakdown)
**Status**: Draft (v0.1)
**Last Updated**: 2026-02-09
**PRD**: `tasks/prd-8.0A-frontend-ui.md`
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-8.0A-frontend-ui.md`

---

## Scope Guardrails (MVP)

- No payments, no org/team accounts, no sharing links.
- No background jobs, streaming, or polling. `POST /reviews` stays synchronous.
- No repo-wide lint cleanup (Task 8.1+).
- Keep analytics as a placeholder only.

## Deliverable Separation (Execution Order)

- **8.0A.0** Scaffolding (must land first): Next.js scaffold + Clerk + BFF adapter + SEO noindex guardrail.
- **8.0A.1** App slice: `/app` submit flow and `/app/reviews/[review_id]` results page.
- **8.0A.2** Marketing/MDX: minimum landing + blog route to support SEO discovery.

## Dependencies / Inputs

- Backend contracts already shipped (8.0B):
  - Signed headers required for protected routes (`X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`)
  - `Idempotency-Key` required for `POST /reviews`
  - canonical errors and review states (`FAILED` returned as a state)
- Secrets alignment needed:
  - Next server has `BFF_SHARED_SECRET` matching FastAPI
  - Next server has `FASTAPI_BASE_URL` (server-only)
- Clerk configured for Next.js (sign-in, redirect back to intended `/app/*` route)

## 8.0A.0 Scaffolding (Hard Prereq)

- [ ] Create Next.js app scaffold (App Router, TS, Tailwind, shadcn/ui baseline).
- [ ] Add Clerk to Next.js (server-side auth available in route handlers).
- [ ] Enforce “server-only env” immediately:
  - `FASTAPI_BASE_URL` must not be exposed via `NEXT_PUBLIC_*`.
  - Only server code can read it.
- [ ] Implement BFF adapter module (single owner of FastAPI calls):
  - `src/lib/bff/*` with:
    - typed `Result<T>` and `ApiError`
    - canonical error parsing (`{error:{code,message,details}}`)
    - signing logic (HMAC; sign exact bytes sent)
    - idempotency utilities (payload normalization + sha256)
  - Adapter functions (as locked in PRD):
    - `listCalls`
    - `listNodes`
    - `createReview`
    - `getReview`
- [ ] Implement attempt persistence (tab-scoped) in `sessionStorage`:
  - store draft + `{idempotency_key,payload_sha256,created_at_ms}`
  - reuse key on unchanged payload; new key on changed payload
  - FAILED retry always generates a new key
- [ ] Add SEO privacy guardrails:
  - `robots.txt` disallow `/app/`
  - `X-Robots-Tag: noindex` on `/app/*`
- [ ] Add lightweight verification guardrail (script/test):
  - asserts `robots.txt` contains `Disallow: /app/`
  - asserts `/app` includes `X-Robots-Tag: noindex`

Commit checkpoint (Phase 3): one commit after 8.0A.0 is complete.

## 8.0A.1 App Vertical Slice

- [ ] `/app` submission page:
  - auth required (redirect to Clerk sign-in, then back)
  - call selector (via adapter)
  - node selector (via adapter)
  - snippet textarea with char count (aligned to backend max)
  - submit button:
    - disabled while in-flight
    - uses current attempt idempotency key
    - navigates to `/app/reviews/[review_id]` on success
  - timeout UX:
    - after ~40s show “still working, refresh safely” message
    - no auto-retry
- [ ] `/app/reviews/[review_id]` results page:
  - deep link supported
  - render `COMPLETED` results (summary + cards)
  - render `FAILED` state with retry CTA (prefill inputs; new idempotency key)
  - render not-found state for masked 404
- [ ] Error UX mapping by `error.code` (no branching on HTTP status):
  - `UNAUTHORIZED` -> sign-in flow
  - `QUOTA_EXCEEDED` -> limit reached message + reset time (if provided)
  - `REVIEWS_DISABLED` -> maintenance banner/state
  - validation/snippet-too-long/no-expectations -> inline form errors

Commit checkpoint (Phase 3): one commit after 8.0A.1 is complete.

## 8.0A.2 Marketing + MDX (Minimum)

- [ ] Marketing landing (`/`) with CTA to `/app` (auth will gate).
- [ ] Blog route (`/blog/*`) backed by MDX with one placeholder article.
- [ ] Ensure marketing/blog are indexable while `/app/*` stays `noindex`.

Commit checkpoint (Phase 3): one commit after 8.0A.2 is complete.

## 8.0A.9 Verify (Required)

- [ ] Manual happy-path (stub mode backend):
  - load `/app` -> submit -> results
  - refresh and resubmit unchanged draft -> reuse idempotency key (no duplicate spend)
  - FAILED retry -> new key
  - deep link results route works after login
- [ ] SEO guardrail verification script passes.
- [ ] Document verification results in a walkthrough:
  - `knowledge_base/walkthroughs/walkthrough_task_8.0A_frontend_ui.md`

## Non-Scope Ideas (Backlog)

- Cross-tab idempotency coordination.
- Automatic retries/backoff.
- Proactive quota introspection endpoint and UI.
- Paid tiers, teams, sharing links.
- CI enforcement for SEO guardrail script (run manually first).

## Revision History

- **v0.1** (2026-02-09): Initial Phase 2 plan split into 8.0A.0 scaffolding, 8.0A.1 app slice, 8.0A.2 marketing/MDX, plus explicit verify step.

