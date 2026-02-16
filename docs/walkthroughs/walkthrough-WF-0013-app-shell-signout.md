# WF-0013 — App Shell + Sign-Out Walkthrough

Artifact: walkthrough
Version: v1.0
Status: Done
Last Updated: 2026-02-16

---

## Summary

Added a persistent app shell header to all `/app/*` pages with PeerLens branding, navigation, and Clerk-powered sign-out. This was P0 #1 from the parking lot.

---

## Changes Made

### New File
- `frontend/src/app/app/layout.tsx` — Next.js nested layout with:
  - Sticky header (logo, "New Review" nav link, Clerk `UserButton`)
  - Active nav state via `usePathname()`
  - `afterSignOutUrl="/"` for clean sign-out redirect

### Modified Files
- `frontend/src/app/app/page.tsx` — Removed `min-h-screen` from `<main>` (1 instance)
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` — Removed `min-h-screen` from `<main>` (5 instances)

### Docs
- `docs/index.md` — WF-0013 row added, status → Done
- `docs/parking_lot.md` — P0 #1 promoted to WF-0013
- `docs/lessons.md` — Added L21, L22
- `GEMINI.md` — Added two behavioral lessons

---

## Verification

| Check | Result |
|---|---|
| `npm run build` | ✅ Passed (13 routes, exit 0) |
| Landing page unaffected | ✅ `/` uses its own inline header |
| No new dependencies | ✅ `@clerk/nextjs` was already installed |
| File count | ✅ 3 source files (1 new, 2 modified) |

---

## Commit History

| Commit | Description |
|---|---|
| `aef8893` | Phase 0.0: start workflow |
| `b10ae8e` | Phase 0.1: brainstorm complete |
| `e0c0c95` | Phase 1: spec v1.0 |
| `04e4177` | Phase 2: PRD v1.0 |
| `0a6dc42` | Phase 3: tasks v1.0 |
| `6641247` | Phase 4: implement T1-T3 |

---

## What Could Break

1. **Clerk `UserButton` styling** — If Clerk updates its component styles, the avatar size may change. Mitigated by constraining via `appearance.elements.avatarBox`.
2. **`afterSignOutUrl` deprecation** — Clerk may change this prop name in future versions. Low risk for current `@clerk/nextjs` version.

---

## Next 2 WF Ideas

1. **P0 #2: Add review history ("My Reviews")** — Add `GET /reviews` backend endpoint + `/app/reviews` list page. The app shell nav already has room for a second link.
2. **P0 #3: Upgrade review results UX** — Richer review cards with criterion headings and visual rating indicators.
