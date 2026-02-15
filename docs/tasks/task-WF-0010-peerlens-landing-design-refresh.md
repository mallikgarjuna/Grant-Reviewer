# WF-0010 — PeerLens Landing Design Refresh

Artifact: task  
Version: v0.2  
Status: Ready for Implementation  
Last Updated: 2026-02-15

## Task Breakdown (Sequential Order)

Execution order is strict: complete Tasks 1->7 in sequence.

### Task 1 — Align brand guideline source of truth

Goal:
Update `docs/reference/brand_guidelines.md` so implementation tokens/typography guidance matches WF-0010 PRD decisions.

Files to modify:
- `docs/reference/brand_guidelines.md`

Acceptance Criteria:
- Landing palette/typography direction is explicitly documented for WF-0010.
- Guidance clearly preserves route/behavior stability and MVP scope boundaries.

Verification Steps:
- Manual content review against `docs/prds/prd-WF-0010-peerlens-landing-design-refresh.md`.

Risks (if any):
- Guideline drift if implementation changes are made before this update.

### Task 2 — Implement landing token and type alignment

Goal:
Apply the approved token/typography adjustments in global styles without changing non-landing behavior.

Files to modify:
- `frontend/src/app/globals.css`

Acceptance Criteria:
- Landing token usage is coherent (background/surface/border/muted/primary).
- Typography hierarchy is restrained and readable for academic tone.
- No new CSS frameworks/dependencies introduced.

Verification Steps:
- `cd frontend && npm run lint`
- Manual spot-check of `/sign-in`, `/privacy`, and `/app` visual sanity after token changes.

Risks (if any):
- Global style changes could unintentionally affect non-landing routes.

### Task 3 — Rework landing layout rhythm and hierarchy

Goal:
Improve structure/scannability on `/` by reducing container clutter and strengthening whitespace/line-length rhythm.

Files to modify:
- `frontend/src/app/page.tsx`

Acceptance Criteria:
- Card density is reduced where non-essential.
- Hero/support/demo/CTA sections read clearly in top-to-bottom flow.
- CTA and nav sign-in affordance remain prominent and unchanged in destination.

Verification Steps:
- `cd frontend && npm run lint`
- Manual keyboard check for tab/accordion focus and activation behavior.
- Manual visual check on desktop + mobile widths.

Risks (if any):
- Over-simplification may remove helpful grouping cues.

### Task 4 — Refresh high-impact copy to academic tone

Goal:
Rewrite hero/support/demo/CTA copy with precise, non-hype language aligned to current product capability.

Files to modify:
- `frontend/src/app/page.tsx`

Acceptance Criteria:
- SaaS-heavy phrasing is removed from high-impact areas.
- Claims remain conservative and truthful.
- CTA still routes to `/sign-in`; privacy references still route to `/privacy`.

Verification Steps:
- Manual copy review against PRD scope.
- `cd frontend && npm run check:seo`

Risks (if any):
- Copy edits may accidentally imply unsupported outcomes.

### Task 5 — Ensure demo/FAQ shell consistency (presentation-only)

Goal:
Adjust landing component presentation for visual consistency while preserving current behavior and data contracts.

Files to modify:
- `frontend/src/app/_components/landing/demo-tabs.tsx`
- `frontend/src/app/_components/landing/faq-accordion.tsx`

Acceptance Criteria:
- Component visuals align with refreshed landing style.
- No behavioral expansion (no API calls, no new interaction flows).
- Existing accessibility semantics remain intact.

Verification Steps:
- `cd frontend && npm run lint`

Risks (if any):
- Presentation edits could degrade existing focus/keyboard behavior if done carelessly.

### Task 6 — Accessibility + mobile hardening pass

Goal:
Run a targeted pass for contrast, focus visibility, and small-screen readability after UI updates.

Files to modify:
- `frontend/src/app/page.tsx` (if needed)
- `frontend/src/app/globals.css` (if needed)
- `frontend/src/app/_components/landing/demo-tabs.tsx` (if needed)
- `frontend/src/app/_components/landing/faq-accordion.tsx` (if needed)

Acceptance Criteria:
- WCAG AA contrast maintained for landing text/controls.
- Keyboard focus-visible states are clear.
- No horizontal overflow or unreadable sections on mobile.

Verification Steps:
- Manual keyboard traversal on `/`.
- Manual mobile viewport checks.

Risks (if any):
- Last-mile tweaks may cause minor style regressions if not rechecked holistically.

### Task 7 — Verification gate and readiness sign-off

Goal:
Execute the PRD verification bundle and confirm landing refresh readiness for implementation completion.

Files to modify:
- None (verification-only), unless fixes are required from failed checks.

Acceptance Criteria:
- Required checks pass:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run check:seo`
  - `cd frontend && npx next build --webpack`
- Manual keyboard + mobile pass on `/` completed and noted.

Verification Steps:
- Run all required commands and record outcomes in walkthrough/implementation notes.
- Record final results in `docs/walkthroughs/walkthrough-WF-0010-peerlens-landing-design-refresh.md`.

Risks (if any):
- Build/runtime discrepancies between local and sandboxed environments.

## Changelog

- v0.1 (2026-02-15): Initial tasks from PRD.
- v0.2 (2026-02-15): Applied review edits (sequencing + verification clarity) and marked Ready for Implementation.
