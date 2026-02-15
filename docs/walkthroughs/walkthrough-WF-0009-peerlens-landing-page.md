# WF-0009 — PeerLens Landing Page

Artifact: walkthrough  
Version: v1.1  
Status: Completed  
Last Updated: 2026-02-15

---

## Scope Delivered

- Replaced `/` with PeerLens landing page sections from PRD:
  - Nav, hero, problem framing, static demo, benefits, how-it-works, FAQ, final CTA, privacy-only footer
- Added static demo data source with 3 locked tabs (`NWO Veni`, `ERC Starting`, `MSCA PF`) and 4 cards each
- Added accessible landing components:
  - `demo-tabs` (keyboard support + ARIA tab semantics)
  - `faq-accordion` (button + `aria-expanded` + stable ids)
- Added `/privacy` route with required MVP statements
- Added review export actions on review detail page:
  - `Copy as text`
  - `Download .txt`
- Added backend hard-delete API and ownership checks:
  - `DELETE /reviews/{review_id}` -> `200 { "ok": true }`
  - hard-deletes review + cards + associated snippet
- Added BFF support and review UI deletion flow:
  - Next.js BFF `DELETE` handler
  - review detail “Delete review” confirmation and redirect to `/app`
- Added telemetry attributes on landing interactions:
  - `data-pl="cta-primary"`
  - `data-pl="demo-tab"`
  - `data-pl="faq-toggle"`

## Post-Completion Fixes (v1.1)

- Export payload/readability fix:
  - backend now returns `criterion` on review cards
  - review export now uses criterion names instead of expectation UUIDs
- Landing footer now includes privacy link + copyright
- Demo tabs keyboard interaction now uses roving focus on arrow/Home/End navigation
- Frontend font loading changed to local/system stack (`--font-inter`) to avoid external Google Fonts dependency during build

## How to Run

### Backend

```bash
cd backend
uv sync
uv run pytest -q
```

### Frontend

```bash
cd frontend
npm install
npm run lint
npm run check:bff
npm run check:seo
npm run dev
```

Open:

- `http://localhost:3000/`
- `http://localhost:3000/privacy`

## How to Verify

### Automated checks executed in this run

- `cd backend && uv run pytest -q` -> pass (`24 passed`)
- `cd frontend && npm run lint` -> pass
- `cd frontend && npm run check:bff` -> pass
- `cd frontend && npm run check:seo` -> pass
- `cd frontend && npx next build --webpack` -> compile succeeds; build fails at existing TypeScript error in `src/app/sign-in/[[...sign-in]]/page.tsx` generated type check

### Manual verification checklist

- Landing `/` shows required sections and copy
- CTA “Check My Draft Now” routes to `/sign-in`
- Demo label copy is present exactly:
  - “Examples only. Sign in to get feedback on your proposal text.”
  - “Export your review. Delete your data anytime. See Privacy.”
- Review detail page can:
  - copy export text
  - download `.txt`
  - delete review and redirect to `/app`
- Reloading deleted review URL shows not-found behavior

## Known Limitations

- `npm run build` cannot complete in this sandbox environment:
  - Turbopack fails with OS permission when spawning/binding
- `npx next build --webpack` now avoids font-fetch/network failure, but still fails on a pre-existing Next.js/TypeScript mismatch under sign-in route page props typing.
- Clerk-authenticated browser flows (`/sign-in`, `/app/*`) were not fully exercised in this sandbox and should be validated locally with real env vars.

## Revision History

- v0.0 (2026-02-14): placeholder
- v1.0 (2026-02-14): implementation complete, verification logged, limitations documented
- v1.1 (2026-02-15): post-implementation quality fixes (export criterion labels, tab focus behavior, local font stack, footer compliance)
