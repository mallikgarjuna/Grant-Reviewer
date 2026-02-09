# Task 8.0A: Frontend UI Slice (Phase 2 Plan)

**Date**: 2026-02-09
**Task ID**: 8.0A
**Pipeline Phase**: Phase 2 (Task breakdown)
**Status**: Draft (v0.6 - Revised)
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

## Decisions Locked In This Plan (MVP, ship-fast)

- **Next.js app location**: create a dedicated `frontend/` directory at repo root.
  - Rationale: isolates Node tooling from `backend/` and keeps Python tooling clean.
- **BFF surface**: use Next route handlers under `frontend/src/app/api/bff/*` as the browser-facing BFF.
  - UI calls same-origin `/api/bff/*`; route handlers call FastAPI via the adapter.
  - Rationale: debuggable, cacheable, clear separation (components do not call FastAPI).
- **Auth protection**: use Clerk middleware to protect both:
  - `/app/*` pages
  - `/api/bff/*` route handlers
  - Rationale: one place to enforce auth; consistent deep-link behavior.
- **Verification split**:
  - “Verify-Local” in 8.0A uses stub backend + scripts.
  - “Verify-Deploy” (Vercel/Render wiring) is deferred to 8.0C.

## Dependencies / Inputs

- Backend contracts already shipped (8.0B):
  - Signed headers required for protected routes (`X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`)
  - `Idempotency-Key` required for `POST /reviews`
  - canonical errors and review states (`FAILED` returned as a state)
- Secrets alignment needed:
  - Next server has `BFF_SHARED_SECRET` matching FastAPI
  - Next server has `FASTAPI_BASE_URL` (server-only)
- Clerk configured for Next.js (sign-in, redirect back to intended `/app/*` route)

## 8.0A.0 Scaffolding (Hard Prereq, Split Into Reviewable Commits)

### 8.0A.0-pre Tooling preflight (commit)

- [ ] Confirm Node/npm available for `frontend/` work (Node `22.17.0` recommended).
- [ ] If Node tooling is not available in the current execution environment:
  - scaffold `frontend/` locally
  - commit the generated files
  - continue subsequent implementation in-repo as usual

### 8.0A.0a Project scaffold (commit)

- [ ] Create Next.js app scaffold in `frontend/` (App Router, TS).
- [ ] Add Tailwind and shadcn/ui baseline.
- [ ] Add minimal dev scripts (how to run frontend locally) in repo README if needed.

### 8.0A.0a2 MVP style guide checkpoint (commit)

- [ ] Lock a minimal MVP style guide (documented decision):
  - typography: 1 font choice + heading scale
  - color: primary + neutrals + semantic colors (error/success)
  - spacing: consistent form/layout spacing
  - primitives: `Button`, `Input`, `Card` (shadcn variants)
- [ ] Document the choices in `tasks/prd-8.0A-frontend-ui.md` so later UI work stays consistent.

Optional guardrails (run locally if you have Node/npm):
- If you use `nvm`, activate the expected Node version first: `nvm use v22.17.0`.
- Skill search:
  - `npx skills find vercel react nextjs`
  - `npx skills find ui accessibility web design`
  - `npx skills find tailwind shadcn nextjs`
- Recommended MVP installs (low churn, high leverage):
  - `npx skills add vercel-labs/agent-skills@vercel-react-best-practices -g -y`
  - `npx skills add https://github.com/addyosmani/web-quality-skills --skill accessibility -g -y`
- Optional (only if you want shadcn bootstrapping help):
  - `npx skills add shipshitdev/library@shadcn-setup -g -y`

### 8.0A.0b Clerk auth + route protection (commit)

- [ ] Add Clerk to Next.js.
- [ ] Protect `/app/*` via Clerk middleware.
- [ ] Preserve intended redirect path (deep link support).

### 8.0A.0c BFF adapter core (commit)

- [ ] Enforce “server-only env” immediately:
  - `FASTAPI_BASE_URL` must not be exposed via `NEXT_PUBLIC_*`.
  - Only server code can read it.
- [ ] Implement adapter module `frontend/src/lib/bff/*` (single owner of FastAPI calls):
  - typed `Result<T>` and `ApiError`
  - canonical error parsing (`{error:{code,message,details}}`)
  - signing logic (HMAC; sign exact bytes sent)
  - payload normalization + `payload_sha256`
  - adapter functions (as locked in PRD): `listCalls`, `listNodes`, `createReview`, `getReview`
- [ ] Add minimal invariant self-check script (no new deps):
  - verifies payload normalization stability
  - verifies signature changes when bytes change

MVP gate:
- Do not start building `/app` pages until this step passes locally (prevents brittle auth/idempotency failures from surfacing late).

### 8.0A.0d BFF route handlers (commit)

- [ ] Implement `frontend/src/app/api/bff/*` route handlers:
  - browser -> `/api/bff/*`
  - handlers call adapter -> FastAPI
- [ ] Protect `/api/bff/*` via Clerk middleware.
- [ ] Ensure `X-GR-User-Id` uses Clerk user id, and `Idempotency-Key` is set on create.

### 8.0A.0e SEO privacy guardrails + verify script (commit)

- [ ] Add `robots.txt` disallowing `/app/`.
- [ ] Add `X-Robots-Tag: noindex` on `/app/*` (middleware or headers).
- [ ] Add lightweight verification script:
  - asserts `robots.txt` contains `Disallow: /app/`
  - asserts `/app` response contains `X-Robots-Tag: noindex`

## 8.0A.1 App Vertical Slice

### 8.0A.1a `/app` submit flow (commit)

- [ ] `/app` submission page:
  - auth required (redirect to Clerk sign-in, then back)
  - call selector (via `/api/bff/*`)
  - node selector (via `/api/bff/*`)
  - snippet textarea with char count (aligned to backend max)
  - submit button:
    - disabled while in-flight
    - uses current attempt idempotency key
    - navigates to `/app/reviews/[review_id]` on success
  - timeout UX:
    - after ~40s show “still working, refresh safely” message
    - no auto-retry

### 8.0A.1b `/app/reviews/[review_id]` results + error mapping (commit)

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

## 8.0A.2 Marketing + MDX (Minimum)

### 8.0A.2a Marketing landing (commit)

- [ ] Marketing landing (`/`) with CTA to `/app` (auth will gate).

### 8.0A.2b Blog route + one MDX article (commit)

- [ ] Blog route (`/blog/*`) backed by MDX with one placeholder article.
- [ ] Ensure marketing/blog are indexable while `/app/*` stays `noindex`.

## 8.0A.9 Verify (Required)

### Verify-Local (8.0A)

- [ ] Manual happy-path (stub mode backend):
  - load `/app` -> submit -> results
  - refresh and resubmit unchanged draft -> reuse idempotency key (no duplicate spend)
  - FAILED retry -> new key
  - deep link results route works after login
- [ ] SEO guardrail verification script passes.
- [ ] Adapter invariant self-check passes.
- [ ] Document verification results in a walkthrough:
  - `knowledge_base/walkthroughs/walkthrough_task_8.0A_frontend_ui.md`

### Verify-Deploy (defer to 8.0C)

- [ ] Confirm same behaviors on deployed environment (auth redirects, noindex headers, BFF-to-FastAPI wiring).

## Non-Scope Ideas (Backlog)

- Cross-tab idempotency coordination.
- Automatic retries/backoff.
- Proactive quota introspection endpoint and UI.
- Paid tiers, teams, sharing links.
- CI enforcement for SEO guardrail script (run manually first).

## Revision History

- **v0.1** (2026-02-09): Initial Phase 2 plan split into 8.0A.0 scaffolding, 8.0A.1 app slice, 8.0A.2 marketing/MDX, plus explicit verify step.
- **v0.2** (2026-02-09): Locked `frontend/` location and BFF route-handler approach; split 8.0A.0/8.0A.1 into smaller commit-sized subtasks; made adapter invariants and SEO guardrail verification concrete; separated Verify-Local vs deferred Verify-Deploy.
- **v0.3** (2026-02-09): Added an explicit MVP style guide checkpoint right after scaffolding and documented optional local skill-install commands (Node/npm required).
- **v0.4** (2026-02-09): Locked recommended skill installs for MVP guardrails (Vercel React/Next best practices + web accessibility).
- **v0.5** (2026-02-09): Updated accessibility skill reference to match installed `web-quality-skills` accessibility skill.
- **v0.6** (2026-02-09): Added explicit Node/tooling preflight + local scaffold fallback, and made adapter invariants a hard gate before UI pages.
