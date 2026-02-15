# WF-0010 — PeerLens Landing Design Refresh

Artifact: brainstorm  
Version: v0.1  
Status: Draft  
Last Updated: 2026-02-15

## Goal

Make `/` look professional and credible for academics/researchers/funders while staying MVP-fast.

## Non-Goals

- No new product features, dependencies, or redesign of `/app/*` flows.
- No analytics vendor integration.

## Decisions to Carry Forward

- Visual direction: “clean journal / institutional”
- Palette: Ink + Parchment (see `docs/logs/decisions.md`)
- We can tweak copy as part of this WF.
- We will update `docs/reference/brand_guidelines.md` to match the new palette and typography.

## Problems Observed

- Token mismatch causes inconsistent muted text/colors on `/`.
- Too many bordered boxes (“card soup”), weak layout rhythm.
- Typography feels heavy/techy vs academic.

## Proposed Changes (MVP scope)

1. Update `docs/reference/brand_guidelines.md` with the new palette + restrained type weights.
2. Implement palette via CSS tokens in `frontend/src/app/globals.css`.
3. Rework landing layout for rhythm:
   - fewer boxed sections, more whitespace, clear max line-length
   - hero + trust line + demo presentation refinements
4. Copy refresh for academic tone:
   - remove SaaS-y phrasing, tighten claims, increase clarity
5. A11y pass:
   - confirm contrast, focus styles, tab/accordion behavior

## Acceptance Criteria

- Landing looks “institutional” (less startup SaaS).
- Consistent muted text + borders + surfaces (no token gaps).
- Mobile remains clean; keyboard navigation remains correct.
- No new dependencies.
