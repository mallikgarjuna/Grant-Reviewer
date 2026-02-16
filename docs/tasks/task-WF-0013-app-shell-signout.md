# WF-0013 — App Shell + Sign-Out Tasks

Artifact: task
Version: v1.0
Status: Ready for Implementation
Last Updated: 2026-02-16

Derived from: [prd-WF-0013-app-shell-signout.md](../prds/prd-WF-0013-app-shell-signout.md)

---

## Tasks

### T1: Create app layout with persistent header
- [ ] Create `frontend/src/app/app/layout.tsx`
- [ ] Add `"use client"` directive
- [ ] Import `UserButton` from `@clerk/nextjs`
- [ ] Import `Image`, `Link` from Next.js
- [ ] Import `usePathname` for active nav state
- [ ] Implement `NavLink` component with active state styling
- [ ] Implement sticky `<header>` with:
  - PeerLens logo linking to `/`
  - `<nav>` with "New Review" link to `/app`
  - `<UserButton afterSignOutUrl="/" />`
- [ ] Render `{children}` below header
- [ ] Use existing CSS custom properties for design consistency

### T2: Update submit page layout compatibility
- [ ] Remove `min-h-screen` from `<main>` in `frontend/src/app/app/page.tsx`

### T3: Update review detail page layout compatibility
- [ ] Remove `min-h-screen` from all `<main>` wrappers in `frontend/src/app/app/reviews/[reviewId]/page.tsx`

### T4: Verify
- [ ] `npm run build` succeeds
- [ ] Browser: `/app` shows persistent header
- [ ] Browser: `UserButton` dropdown shows sign-out
- [ ] Browser: `/` landing page is unaffected
- [ ] Update walkthrough artifact

---

## Changelog

- v0.1 (2026-02-16): Initial task breakdown from PRD.
- v1.0 (2026-02-16): Self-reviewed, no blocking sequencing issues. Ready for Implementation.
