# WF-0013 — App Shell + Sign-Out PRD

Artifact: prd
Version: v1.0
Status: Ready for Tasks
Last Updated: 2026-02-16

---

## Overview

This PRD defines the implementation requirements for adding a persistent app shell header to all authenticated `/app/*` pages. The header provides PeerLens branding, navigation, and Clerk-powered sign-out.

Derived from: [spec-WF-0013-app-shell-signout.md](../specs/features/spec-WF-0013-app-shell-signout.md)

---

## User Stories & Acceptance Criteria

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-1 | Persistent header on all `/app/*` pages | Sticky header with logo, nav, UserButton. Not on public pages. |
| US-2 | Sign-out capability | Clerk `UserButton` in header; sign-out redirects to `/`. |
| US-3 | Navigation links | "New Review" → `/app`; active state visually distinct. |

---

## Implementation Requirements

### IR-1: Create `/app/layout.tsx`
- File: `frontend/src/app/app/layout.tsx`
- Next.js nested layout wrapping all `/app/*` pages.
- Must use `"use client"` (required by `UserButton`).
- Renders `<header>` with:
  - PeerLens logo (`/logo.png`, links to `/`).
  - `<nav>` with "New Review" link (`/app`) with active state based on `usePathname()`.
  - Clerk `<UserButton afterSignOutUrl="/" />`.
- Header is sticky (`position: sticky; top: 0; z-index: 40`).
- Uses existing CSS custom properties for colors and borders.
- Renders `{children}` below header.

### IR-2: Modify submit page
- File: `frontend/src/app/app/page.tsx`
- Remove `min-h-screen` from the `<main>` wrapper (layout now controls height).
- No functional changes.

### IR-3: Modify review detail page
- File: `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- Remove `min-h-screen` from all `<main>` wrappers (5 return paths).
- No functional changes.

---

## Breaking Changes

None identified.

---

## Dependencies

- `@clerk/nextjs` — already installed (provides `UserButton`).
- No new dependencies.

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `UserButton` styling conflicts | Low | Use `appearance` prop to constrain avatar size |
| `afterSignOutUrl` not working | Low | Fallback exists in Clerk middleware redirect |

---

## Out of Scope

- "My Reviews" page (P0 #2)
- Mobile hamburger menu
- Footer, sidebar, breadcrumbs
- Dark mode toggle

---

## Verification Plan

1. `npm run build` must succeed.
2. Browser check: `/app` shows header with logo, nav, UserButton.
3. Browser check: UserButton dropdown shows sign-out.
4. Browser check: `/` (landing) shows its own header, not the app header.

---

## Changelog

- v0.1 (2026-02-16): Initial PRD generated from spec.
- v1.0 (2026-02-16): Self-audited (Part B), no blocking risks. Marked Ready for Tasks.
