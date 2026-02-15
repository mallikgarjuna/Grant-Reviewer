# WF-0010 — PeerLens Landing Design Refresh

Artifact: walkthrough  
Version: v0.1  
Status: Completed  
Last Updated: 2026-02-15

## What Was Implemented

- Updated brand guidelines to the approved Ink + Parchment direction in `docs/reference/brand_guidelines.md`.
- Applied landing token and typography alignment in `frontend/src/app/globals.css`.
- Reworked landing layout rhythm in `frontend/src/app/page.tsx` to reduce container clutter and improve scan flow.
- Refreshed high-impact copy (hero/support/CTA) to academic, non-hype language.
- Harmonized demo and FAQ shell presentation in:
  - `frontend/src/app/_components/landing/demo-tabs.tsx`
  - `frontend/src/app/_components/landing/faq-accordion.tsx`
- Added accessibility hardening on `/`:
  - skip link to main content
  - explicit main-content target
  - maintained visible focus styles and mobile readability emphasis

## Per-Task Commits

1. `2d0717b` — Task 1 — align brand guideline source
2. `b5d6929` — Task 2 — implement token/type alignment
3. `39bf1b8` — Task 3 — rework layout rhythm
4. `274634d` — Task 4 — refresh high-impact copy
5. `1c77e63` — Task 5 — harmonize demo and FAQ shell
6. `6659ff0` — Task 6 — harden accessibility and mobile readability

## How To Run

From repo root:

```bash
cd frontend
npm run dev
```

Open:
- `http://localhost:3000/`

## Verification Run

Executed:

```bash
cd frontend && npm run lint
cd frontend && npm run check:seo
cd frontend && npx next build --webpack
```

Observed:
- `lint`: pass
- `check:seo`: pass (`seo-guardrail-check: ok (static)`)
- `next build --webpack`: pass (successful compile + typecheck + route generation)

## Known Limitations

- Manual browser-only checks (keyboard traversal and mobile viewport walkthrough) were not fully executed in this sandboxed run and should be validated locally before production release.

## Changelog

- v0.1 (2026-02-15): Initial implementation walkthrough for WF-0010 Phase 4 tasks.
- v0.2 (2026-02-15): Post-implementation manual-pass polish added for small-screen header/hero resilience and long-text wrapping safety.
- v0.3 (2026-02-15): Copy lock update for supported funding line and FAQ usage prompt/answer.

## Follow-Up Polish (Post Task Run)

- Manual pass requested for `/` with keyboard-only and mobile widths.
- Applied tiny polish in:
  - `frontend/src/app/page.tsx`
  - `frontend/src/app/_components/landing/demo-tabs.tsx`
- Changes:
  - Reduced small-screen outer/hero spacing to improve fit.
  - Hardened long text wrapping (`overflow-wrap:anywhere`) on hero/demo content blocks.
  - Adjusted small-screen header behavior and hid top-right `Sign In` chrome button on very small widths (primary CTA in hero remains available).
- Verification rerun:
  - `cd frontend && npm run -s lint` (pass)
  - Mobile screenshot checks run against local branch-specific server (`http://localhost:3101/`) at `390x844` and `430x932`.

## Copy Lock Follow-Up

- Updated landing funding-line copy in `frontend/src/app/page.tsx`:
  - `Supported funding calls: NL (NWO, ZonMw), EU/Horizon-Europe (ERC, MSCA)`
- Updated FAQ usage copy in `frontend/src/app/_components/landing/faq-accordion.tsx`:
  - Question: `How should I use PeerLens?`
  - Answer: `Select the funding call, then a proposal application's section heading, then paste one draft section at a time (for example, methodology, impact, or work plan) so the feedback stays specific and actionable.`
