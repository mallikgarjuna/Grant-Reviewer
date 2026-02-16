# WF-0013 — App Shell + Sign-Out Brainstorm

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-02-16

---

## 1. Problem Statement

**What problem?** Authenticated `/app/*` pages have no persistent header, no branding, no navigation, and no sign-out button. Users who sign in have no way to sign out or orient themselves.

**Who?** Every authenticated researcher using the review workbench.

**Why now?** This is a P0 blocker — must be fixed before any real user touches the app.

---

## 2. Desired Outcome

- A persistent header bar on all `/app/*` pages with PeerLens logo, navigation links, and a user menu with sign-out.
- Users can sign out with one click.
- The authenticated area feels like a coherent app, not a bare form.

---

## 3. Target User / Actor

**Who:** All authenticated users (researchers).
**Current behavior:** Users land on `/app` after sign-in and see a floating form with no chrome. They cannot sign out without clearing cookies.
**Frustration:** Feeling lost, no way to navigate, no way to sign out.

---

## 4. Rough Idea

Add a Next.js nested layout (`/app/layout.tsx`) that wraps all `/app/*` pages. The layout renders a sticky header with:
- PeerLens logo (link to `/`)
- Nav link: "New Review" (`/app`)
- Clerk `<UserButton>` component (provides sign-out + account menu for free)

The landing page (`/`) and public pages are unaffected — they live outside the `/app` route group.

---

## 5. Constraints

- Must use existing Clerk integration (already installed and configured).
- Must use existing design tokens (Ink+Parchment palette CSS variables).
- Must not change the landing page header.
- Maximum 3 files changed.

---

## 6. Risks / Unknowns

- **Low risk**: Clerk `<UserButton>` is well-documented and works out of the box with `ClerkProvider`.
- **Assumption**: `afterSignOutUrl` prop handles post-sign-out redirect correctly.
- **No unknowns**: The scope is clear and uses existing patterns.

---

## 7. MVP Definition

**Must exist:** Persistent header with logo + nav + UserButton on all `/app/*` pages.
**Excluded:** Footer, sidebar, breadcrumbs, "My Reviews" page (separate P0 #2 item).

---

## 8. Explicit Non-Goals

- No "My Reviews" page (P0 #2)
- No mobile hamburger menu (P1)
- No dark mode toggle
- No footer in the app shell
