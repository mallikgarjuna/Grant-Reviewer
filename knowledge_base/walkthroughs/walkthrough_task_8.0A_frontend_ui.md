# Walkthrough: Task 8.0A Frontend UI Slice

**Date**: 2026-02-10  
**Task ID**: 8.0A  
**Pipeline Phase**: Phase 3 (Implementation + Verify)  
**Status**: Completed (v1.0 - Verify-Local complete; Verify-Deploy deferred to 8.0C)
**Related PRD**: `tasks/prd-8.0A-frontend-ui.md`  
**Related Task Plan**: `tasks/task-8.0A-frontend-ui.md`

---

## What was implemented

- `8.0A.4` Clerk auth wiring:
  - Clerk provider in root layout
  - Clerk middleware protecting `/app/*` and `/api/bff/*`
  - sign-in route scaffold (MVP: dedicated `/sign-in` route only)
- `8.0A.5` BFF adapter core:
  - server-only env boundary for `FASTAPI_BASE_URL` and `BFF_SHARED_SECRET`
  - signed server-to-server request flow
  - canonical error parsing + typed `Result<T>`
  - payload normalization/hash helpers + invariant check script
- `8.0A.6` Next BFF route handlers:
  - `/api/bff/calls`
  - `/api/bff/calls/[callId]/nodes`
  - `/api/bff/reviews` (POST)
  - `/api/bff/reviews/[reviewId]`
- `8.0A.7` SEO/privacy guardrails:
  - `/app/*` noindex header
  - robots disallow for `/app/`
  - guardrail check script
- `8.0A.8` App submit flow:
  - auth-gated `/app` UI
  - call/node selector + snippet limits
  - idempotency attempt persistence in `sessionStorage`
  - 40s slow-request hint + no auto-retry
- `8.0A.9` Results flow:
  - deep-link review page
  - completed/pending/failed state rendering
  - failed retry path with new idempotency key
  - error-code-based UX mapping
- `8.0A.10` Marketing landing page (`/`)
- `8.0A.11` Blog route + one article (`/blog`, `/blog/writing-better-grant-snippets`)

## Verification executed

From `frontend/` with Node `v22.17.0`:

- `npm run check:bff` -> pass
- `npm run check:seo` -> pass (static mode)
- `npm run lint` -> pass

## Verification completion

- Automated checks were run locally from `frontend/` and passed:
  - `npm run check:bff`
  - `npm run check:seo`
  - `npm run lint`
- Manual browser checklist for `8.0A.12` was completed locally:
  - open `/app` while signed out -> redirect to sign-in
  - sign in and submit review flow from `/app`
  - deep-link `/app/reviews/[review_id]` after auth
- Deploy-environment verification remains intentionally deferred to Task `8.0C`.

## Why local verification script exists

- Codex sandbox is reliable for static checks (`lint`, invariant scripts) but not for runtime browser/E2E flows (port binding, auth redirects, full `/app` journey).
- To make verification repeatable and explicit, use a single local command that runs automated checks first and then prints the required manual browser checklist.
- Script: `scripts/verify_local_8_0A.sh`

## Local follow-up for Verify-Deploy (8.0C)

Run locally (outside this sandbox):

1. `source ~/.nvm/nvm.sh && nvm use v22.17.0`
2. `cd frontend && npm install`
3. Configure Clerk and BFF env vars (`FASTAPI_BASE_URL`, `BFF_SHARED_SECRET`, Clerk keys)
4. Validate `/app` and `/api/bff/*` behavior on deployed frontend/backend
5. Confirm `X-Robots-Tag: noindex` still applies to `/app/*` in deployment
6. Record deployment verification results under Task `8.0C`

MVP UX constraints (locked):
- Marketing + blog are accessible while signed out.
- Only `/app/*` and `/api/bff/*` require login.
- Auth UI is via the dedicated `/sign-in` route (no global header auth buttons in MVP).

Implementation note (Clerk):
- Next.js (current) prefers the `proxy.ts` convention over `middleware.ts`.
  - For this repo: `frontend/src/proxy.ts`.

Implementation note (MDX):
- If using `@next/mdx`, ensure `@mdx-js/loader` is installed (required by the Next MDX loader).

Implementation note (BFF signing):
- If `Generate Review` returns `UNAUTHORIZED` / “Authentication signature verification failed”, the backend usually does **not** have `BFF_SHARED_SECRET` set (or it does not match frontend).
  - Ensure backend is started with `BFF_SHARED_SECRET` matching `frontend/.env.local` `BFF_SHARED_SECRET`.

If you hit npm home-dir permission issues in restricted environments, use a project-local cache/logs:

```bash
cd frontend
mkdir -p .npm-cache .npm-logs
NPM_CONFIG_CACHE=$PWD/.npm-cache NPM_CONFIG_LOGS_DIR=$PWD/.npm-logs npm install
```

## Revision History

- **v0.1** (2026-02-10): Initial implementation walkthrough with executed verification commands and explicit remaining manual verification items.
- **v0.2** (2026-02-10): Added explicit rationale for local verification vs sandbox verification and documented `scripts/verify_local_8_0A.sh` as the standard verification entrypoint.
- **v1.0** (2026-02-10): Marked local automated and manual verification complete, set walkthrough status to completed, and moved deployment checks to Task `8.0C`.
