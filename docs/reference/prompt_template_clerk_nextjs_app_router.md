# Prompt Template: Clerk + Next.js (App Router) for Grant Reviewer

**Date**: 2026-02-10
**Scope**: `frontend/` (Next.js App Router)
**Status**: Draft (v0.1)

Use this prompt when asking an LLM to help with Clerk integration for this repo.

## Notes (repo-specific)

- Next.js (current) prefers the `proxy.ts` convention over `middleware.ts`.
  - For this repo: `frontend/src/proxy.ts`.
- MVP UX decisions (locked):
  - Dedicated `/sign-in` route only (no global header auth buttons).
  - Marketing (`/`) and blog (`/blog/*`) are public.
  - Only `/app/*` and `/api/bff/*` are protected.
- Secrets policy:
  - Real keys go only in `frontend/.env.local` (gitignored).
  - Placeholder examples may exist in tracked `frontend/.env.local.example`.

## Prompt (paste into LLM)

```text
Integrate Clerk into this Next.js App Router app located in `frontend/` with App Router under `frontend/src/app`.

Hard requirements:
- Use Next.js proxy at `frontend/src/proxy.ts` (NOT middleware.ts).
- Protect ONLY:
  - `/app/*`
  - `/api/bff/*`
  Marketing `/` and `/blog/*` must remain public.
- Wrap the app with `<ClerkProvider>` in `frontend/src/app/layout.tsx`.
- Use a dedicated sign-in route only:
  - `frontend/src/app/sign-in/[[...sign-in]]/page.tsx` with `<SignIn />`.
  Do NOT add global header auth buttons on marketing/blog in MVP.
- Server-side code should use Clerk userId from `@clerk/nextjs/server` (`auth()`) and treat it as the external user id for BFF calls.
- Never print/write real keys into tracked files. Real keys go only in `frontend/.env.local` (gitignored). Keep placeholders in `frontend/.env.local.example`.

Use imports only from:
- `@clerk/nextjs`
- `@clerk/nextjs/server`
```
