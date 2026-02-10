# Task 8.0A: Frontend UI Slice (Phase 2 Plan)

**Date**: 2026-02-09
**Task ID**: 8.0A
**Pipeline Phase**: Phase 2 (Task breakdown)
**Status**: Completed (v1.0 - Verify-Local complete; Verify-Deploy deferred to 8.0C)
**Last Updated**: 2026-02-10
**PRD**: `tasks/prd-8.0A-frontend-ui.md`
**Phase 0 Notes**: `knowledge_base/logs/brainstorming-8.0A-frontend-ui.md`

---

## Scope Guardrails (MVP)

- No payments, no org/team accounts, no sharing links.
- No background jobs, streaming, or polling. `POST /reviews` stays synchronous.
- No repo-wide lint cleanup (Task 8.1+).
- Keep analytics as a placeholder only.

## Subtask Verification Rule (Mandatory)

- For every Phase 3 subtask commit, run at least one targeted verification for that subtask before committing.
- Verification can be test, lint/build check, or reliable manual repro, depending on what the subtask changes.
- Record what was run (and outcome) in task notes and/or walkthrough logs.

## Deliverable Separation (Execution Order)

- **8.0A.1-8.0A.7** Scaffolding (must land first): preflight + Next scaffold + Clerk + BFF adapter + SEO noindex guardrail.
- **8.0A.8-8.0A.9** App slice: `/app` submit flow and `/app/reviews/[review_id]` results page.
- **8.0A.10-8.0A.11** Marketing/MDX: minimum landing + blog route to support SEO discovery.
- **8.0A.12** Verify checklist.

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

## 8.0A.1 Tooling preflight (commit)

- [x] Confirm Node/npm available for `frontend/` work (Node `22.17.0` recommended).
- [x] If the environment uses `nvm`, run `nvm use v22.17.0` to ensure `npm/npx` are available.
- If scaffold commands cannot run in the current execution environment (tooling or network restrictions):
  - scaffold `frontend/` locally
  - commit the generated files
  - continue subsequent implementation in-repo as usual

Execution note:
- In this Codex environment, `nvm` works but npm registry access is blocked (`ENOTFOUND registry.npmjs.org`), so `create-next-app` cannot be downloaded here. Use the local-scaffold fallback and commit `frontend/` before continuing.

## 8.0A.2 Project scaffold (commit)

- [x] Create Next.js app scaffold in `frontend/` (App Router, TS).
- [x] Add Tailwind and shadcn/ui baseline.
- [x] Add minimal dev scripts (how to run frontend locally) in repo README if needed.

## 8.0A.3 MVP style guide checkpoint (commit)

- [x] Lock a minimal MVP style guide (documented decision):
  - primary color: `#2563EB`
  - neutral palette: slate / blue-gray
  - font: Inter (headings + body)
  - border radius: medium-rounded (`12px` to `16px`)
  - spacing density: comfortable -> slightly airy
  - theme mode: light-only (MVP)
  - primitives: `Button`, `Input`, `Card` (shadcn variants)
- [x] Lock interaction principles in implementation notes:
  - clarity over cleverness
  - trust/calm surfaces and restrained color
  - short micro-animations, no heavy effects
  - one primary action per screen
- [x] Document the choices in `tasks/prd-8.0A-frontend-ui.md` so later UI work stays consistent.

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

## 8.0A.4 Clerk auth + route protection (commit)

- [x] Add Clerk to Next.js.
- [x] Protect `/app/*` via Clerk middleware.
- [x] Preserve intended redirect path (deep link support).
- [x] Verify this subtask before commit (targeted auth route protection check).

## 8.0A.5 BFF adapter core (commit)

- [x] Enforce “server-only env” immediately:
  - `FASTAPI_BASE_URL` must not be exposed via `NEXT_PUBLIC_*`.
  - Only server code can read it.
- [x] Implement adapter module `frontend/src/lib/bff/*` (single owner of FastAPI calls):
  - typed `Result<T>` and `ApiError`
  - canonical error parsing (`{error:{code,message,details}}`)
  - signing logic (HMAC; sign exact bytes sent)
  - payload normalization + `payload_sha256`
  - adapter functions (as locked in PRD): `listCalls`, `listNodes`, `createReview`, `getReview`
- [x] Add minimal invariant self-check script (no new deps):
  - verifies payload normalization stability
  - verifies signature changes when bytes change
- [x] Verify this subtask before commit (run adapter invariant self-check).

MVP gate:
- Do not start building `/app` pages until this step passes locally (prevents brittle auth/idempotency failures from surfacing late).

## 8.0A.6 BFF route handlers (commit)

- [x] Implement `frontend/src/app/api/bff/*` route handlers:
  - browser -> `/api/bff/*`
  - handlers call adapter -> FastAPI
- [x] Protect `/api/bff/*` via Clerk middleware.
- [x] Ensure `X-GR-User-Id` uses Clerk user id, and `Idempotency-Key` is set on create.
- [x] Verify this subtask before commit (manual BFF route smoke check).

## 8.0A.7 SEO privacy guardrails + verify script (commit)

- [x] Add `robots.txt` disallowing `/app/`.
- [x] Add `X-Robots-Tag: noindex` on `/app/*` (middleware or headers).
- [x] Add lightweight verification script:
  - asserts `robots.txt` contains `Disallow: /app/`
  - asserts `/app` response contains `X-Robots-Tag: noindex`
- [x] Verify this subtask before commit (run SEO guardrail script).

## 8.0A.8 `/app` submit flow (commit)

- [x] `/app` submission page:
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
- [x] Verify this subtask before commit (manual `/app` flow check).

## 8.0A.9 `/app/reviews/[review_id]` results + error mapping (commit)

- [x] `/app/reviews/[review_id]` results page:
  - deep link supported
  - render `COMPLETED` results (summary + cards)
  - render `FAILED` state with retry CTA (prefill inputs; new idempotency key)
  - render not-found state for masked 404
- [x] Error UX mapping by `error.code` (no branching on HTTP status):
  - `UNAUTHORIZED` -> sign-in flow
  - `QUOTA_EXCEEDED` -> limit reached message + reset time (if provided)
  - `REVIEWS_DISABLED` -> maintenance banner/state
  - validation/snippet-too-long/no-expectations -> inline form errors
- [x] Verify this subtask before commit (manual deep-link + error mapping check).

## 8.0A.10 Marketing landing (commit)

- [x] Marketing landing (`/`) with CTA to `/app` (auth will gate).
- [x] Verify this subtask before commit (manual landing route check).

## 8.0A.11 Blog route + one MDX article (commit)

- [x] Blog route (`/blog/*`) backed by MDX with one placeholder article.
- [x] Ensure marketing/blog are indexable while `/app/*` stays `noindex`.
- [x] Verify this subtask before commit (manual blog route + noindex boundary check).

## 8.0A.12 Verify (Required)

Verification purpose (explicit):
- We use a local verification script because Codex sandbox checks are reliable for static checks, but not for long-running web-server runtime flows (`next dev`, browser redirects, sign-in UX).
- The script separates:
  - automated contract/lint checks (repeatable and fast)
  - manual browser UX checks (auth redirect and end-to-end app behavior)

### Verify-Local (8.0A)

- [x] Run `scripts/verify_local_8_0A.sh` and save the output in your PR/notes.
- [x] Manual happy-path (stub mode backend):
  - load `/app` -> submit -> results
  - refresh and resubmit unchanged draft -> reuse idempotency key (no duplicate spend)
  - FAILED retry -> new key
  - deep link results route works after login
- [x] SEO guardrail verification script passes.
- [x] Adapter invariant self-check passes.
- [x] Document verification results in a walkthrough:
  - `knowledge_base/walkthroughs/walkthrough_task_8.0A_frontend_ui.md`

### Verify-Deploy (defer to 8.0C)

- [x] Deferred to Task `8.0C`: confirm same behaviors on deployed environment (auth redirects, noindex headers, BFF-to-FastAPI wiring).

Closure note:
- `8.0A` is closed based on completed Verify-Local and user-run manual browser verification in local environment.
- Verify-Deploy remains explicitly deferred to Task `8.0C` and is not a blocker for closing `8.0A`.

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
- **v0.7** (2026-02-09): Added explicit `nvm use v22.17.0` step to the tooling preflight (when `nvm` is present).
- **v0.8** (2026-02-09): Locked concrete MVP visual style choices and interaction principles (now tracked as `8.0A.3` after renumbering).
- **v0.9** (2026-02-09): Added mandatory per-subtask “verify before commit” checkpoints across remaining Phase 3 subtasks.
- **v0.10** (2026-02-09): Renumbered Phase 3 subtasks to a strict sequential series (`8.0A.1` through `8.0A.12`) for clearer tracking.
- **v0.11** (2026-02-10): Phase 3 subtasks `8.0A.4` through `8.0A.11` implemented and committed; local verification scripts passed (`check:bff`, `check:seo`, `lint`); manual happy-path verification remains pending local dependency installation.
- **v0.12** (2026-02-10): Added `scripts/verify_local_8_0A.sh` and explicit verification-purpose guidance to separate sandbox-static checks from local runtime/browser verification.
- **v1.0** (2026-02-10): Marked Verify-Local complete (script + manual browser checklist) and closed Task `8.0A`; Verify-Deploy remains deferred to `8.0C`.
- **v1.1** (2026-02-10): Marked Verify-Deploy item as explicitly deferred-and-tracked in `8.0C` so `8.0A.12` checklist is fully closed without ambiguity.
