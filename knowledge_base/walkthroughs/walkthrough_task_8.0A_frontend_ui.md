# Walkthrough: Task 8.0A Frontend UI Slice

**Date**: 2026-02-10  
**Task ID**: 8.0A  
**Pipeline Phase**: Phase 3 (Implementation + Verify)  
**Status**: In Progress (v0.1 - Implementation complete, manual verify pending)
**Related PRD**: `tasks/prd-8.0A-frontend-ui.md`  
**Related Task Plan**: `tasks/task-8.0A-frontend-ui.md`

---

## What was implemented

- `8.0A.4` Clerk auth wiring:
  - Clerk provider in root layout
  - Clerk middleware protecting `/app/*` and `/api/bff/*`
  - sign-in route scaffold
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

## Verification gaps / blockers

- Full manual UI happy-path (`/app` submit -> `/app/reviews/[id]`) was **not** executed in this Codex sandbox.
  - Reason: npm registry access is blocked here (`ENOTFOUND registry.npmjs.org`), so new frontend dependencies cannot be installed in this environment.
- Backend smoke command using `uv` from this sandbox also hit a cache permission restriction outside writable roots.

## Local follow-up to finalize Verify-Local

Run locally (outside this sandbox):

1. `source ~/.nvm/nvm.sh && nvm use v22.17.0`
2. `cd frontend && npm install`
3. Configure Clerk and BFF env vars (`FASTAPI_BASE_URL`, `BFF_SHARED_SECRET`, Clerk keys)
4. Start backend in stub mode and frontend dev server
5. Execute manual checklist in `tasks/task-8.0A-frontend-ui.md` section `8.0A.12`

## Revision History

- **v0.1** (2026-02-10): Initial implementation walkthrough with executed verification commands and explicit remaining manual verification items.
