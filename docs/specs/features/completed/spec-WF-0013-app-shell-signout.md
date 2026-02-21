# WF-0013 — App Shell + Sign-Out Spec

Artifact: spec
Version: v1.0
Status: Ready for PRD
Last Updated: 2026-02-16

---

## Feature Summary

Add a persistent app shell header to all authenticated `/app/*` pages. The header provides branding, navigation, and account management (including sign-out).

---

## User Stories

### US-1: Persistent Header
**As** an authenticated researcher,
**I want** a persistent header bar on every `/app/*` page,
**so that** I can orient myself within the application.

**Acceptance Criteria:**
- A sticky header appears at the top of all `/app/*` pages.
- Header contains: PeerLens logo (links to `/`), navigation links, and user avatar/menu.
- Header does NOT appear on public pages (`/`, `/privacy`, `/blog`, `/sign-in`).

### US-2: Sign-Out Capability
**As** an authenticated researcher,
**I want** to sign out from within the application,
**so that** I can end my session securely.

**Acceptance Criteria:**
- Clerk `UserButton` component renders in the header.
- Clicking the avatar opens a dropdown with sign-out option.
- After sign-out, user is redirected to `/`.

### US-3: Navigation Links
**As** an authenticated researcher,
**I want** navigation links in the header,
**so that** I can access key app areas quickly.

**Acceptance Criteria:**
- "New Review" link navigates to `/app`.
- Active link is visually distinguished from inactive links.

---

## UI Sketch

```
┌──────────────────────────────────────────────────────┐
│  [Logo]     New Review                    [Avatar ▾] │
│─────────────────────────────────────────────────────-│
│                                                      │
│              {page content here}                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Technical Approach

- Use Next.js nested layout: `frontend/src/app/app/layout.tsx`.
- `UserButton` from `@clerk/nextjs` (requires `"use client"`).
- Leverage existing CSS custom properties for styling.
- No new dependencies.

---

## Out of Scope

- "My Reviews" page (P0 #2, separate WF)
- Mobile hamburger menu
- Footer in app shell
- Dark mode toggle

---

## Changelog

- v0.1 (2026-02-16): Initial spec generated from brainstorm.
- v1.0 (2026-02-16): Self-reviewed, no blocking issues found. Marked Ready for PRD.
