# WF-0010 — PeerLens Landing Design Refresh Spec

Artifact: spec
Version: v0.1
Status: Draft
Last Updated: 2026-02-15

## 1. Purpose

Improve the existing PeerLens landing page so it reads as academically credible and institutionally trustworthy, increasing confident clicks to `/sign-in` without changing product functionality.

## 2. User / System Context

- Primary user: individual researchers drafting grant proposals.
- Secondary audience: senior PIs/funders scanning for credibility cues.
- Current behavior: users self-edit and gather informal peer feedback before submission.
- Situation: users evaluate the landing page quickly and decide whether to trust PeerLens with proposal text review.

## 3. Core Behavior

- Landing communicates a calm, specific value proposition for proposal review readiness.
- Visual language shifts from startup-like to journal/institutional:
  - coherent token usage
  - restrained typography
  - reduced card density, stronger whitespace rhythm
- Copy is tightened to remove hype and increase academic clarity.
- Primary CTA remains sign-in oriented.
- Existing trust cues remain lightweight and text-based.

## 4. In Scope

- Update `docs/reference/brand_guidelines.md` to match WF-0010 visual direction.
- Refresh landing visual system on `/`:
  - token consistency and palette usage
  - typography hierarchy adjustments
  - spacing/layout rhythm improvements
- Targeted copy rewrite for high-impact sections:
  - hero
  - trust/support context line
  - demo presentation shell text
  - final CTA area
- Preserve and validate accessibility quality:
  - WCAG AA contrast
  - visible keyboard focus states
  - mobile readability

## 5. Out of Scope

- No backend/API/auth changes.
- No `/app/*` flow or interaction changes.
- No route restructuring (`/`, `/sign-in`, `/privacy` remain unchanged).
- No new dependencies.
- No analytics instrumentation, A/B testing, or SEO/content expansion.
- No testimonial/logo/case-study system additions.

## 6. Data & Dependencies

- Inputs:
  - `docs/brainstorms/brainstorm-WF-0010-peerlens-landing-design-refresh.md`
  - `docs/reference/brand_guidelines.md`
  - current landing implementation under `frontend/src/app/*`
- Files expected to change in implementation phase:
  - `frontend/src/app/page.tsx`
  - `frontend/src/app/globals.css`
  - existing landing component files under `frontend/src/app/_components/landing/`
  - `docs/reference/brand_guidelines.md`
- Verification dependencies:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run check:seo`
  - `cd frontend && npx next build --webpack`
  - manual keyboard/mobile pass on `/`

## 7. Edge Considerations

- Risk of style-token drift between documentation and CSS implementation.
- Risk of over-design (too much churn) vs under-design (insufficient trust improvement).
- Ensure trust language stays specific and non-promissory.
- Maintain readability and hierarchy on small screens when reducing container usage.

## 8. Desktop Wireframe (ASCII)

```text
+-------------------------------------------------------------------+
| PeerLens                         Privacy                [Sign In] |
+-------------------------------------------------------------------+
|                                                                   |
|  Sharpen your proposal before you submit                          |
|  Structured feedback aligned to grant review expectations.        |
|                                                                   |
|  [ Check My Draft Now ]                                           |
|  Supported calls: NWO Veni · ERC Starting · MSCA PF               |
|                                                                   |
+-------------------------------------------------------------------+
|  Why researchers use PeerLens                                     |
|  - clearer fit to evaluator expectations                          |
|  - focused suggestions, not generic writing advice                |
|  - privacy details are explicit                                   |
+-------------------------------------------------------------------+
|  Demo (examples only)                                             |
|  [ NWO Veni ] [ ERC Starting ] [ MSCA PF ]                        |
|                                                                   |
|  Snippet preview                                                   |
|  Key findings + suggested fixes                                   |
|  Example readiness score                                           |
|  "Examples only. Sign in to get feedback on your proposal text."  |
|  "Export your review. Delete your data anytime. See Privacy."     |
+-------------------------------------------------------------------+
|  Final CTA                                                         |
|  Ready to pressure-test your draft before submission?              |
|  [ Check My Draft Now ]                                            |
+-------------------------------------------------------------------+
| PeerLens · Privacy                                                 |
+-------------------------------------------------------------------+
```

## Changelog

- v0.1 (2026-02-15): Initial spec from brainstorm.
