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

## 1. Problem Statement (Refined)

### Primary Audience
- Mixed academic users: early-career researchers, experienced PIs, and research support staff.

### Core Problem
- The landing page has a trust deficit for academic users: it feels too startup-like rather than scholarly/institutional.

### First-10-Second Failure Point
- Visual language mismatch is the biggest issue (color/typography/layout do not immediately signal research-grade credibility).
- Copy tone and hierarchy are secondary contributors and should be corrected in the same workflow.

### Why This Matters Now
- Current presentation likely suppresses sign-in conversion among qualified academic users.
- This is a pre-launch blocker for market-facing credibility.

### Scope Boundary for Problem Statement
- No product flow or feature changes in `/app/*`.
- No backend/auth/infra changes.
- Focus only on landing UI presentation, content tone, and token consistency.

## 2. Desired Outcome (Refined)

### Primary Success Signal
- Increase landing-to-sign-in click-through rate from `/` primary CTA.

### Target Behavior Change (First 30 Seconds)
- Visitors quickly understand the value proposition and click the sign-in CTA with confidence.

### Perception Shift
- Visitors should feel: “This is academically credible and serious.”

### MVP “Good Enough” Definition
- Cohesive palette + typography + layout rhythm.
- Clear, restrained value narrative aligned to research audiences.
- No new product features required.

### Explicitly De-Prioritized in This WF
- SEO/content expansion work (new content surfaces beyond current scope).
- Conversion instrumentation/analytics tooling.

## 3. Target User / Actor (Refined)

### Primary User
- Individual researchers drafting grant proposals themselves.

### Current Behavior
- Self-editing in documents plus informal peer feedback.

### Core Frustration
- Uncertainty about whether draft text aligns with evaluator expectations.

### Highest-Value Trust Cue
- Institutional visual tone and precise, non-hyped language.

### Secondary Audience (Consider, Not Optimize For)
- Senior PIs/funders scanning for credibility signals.

## 4. Rough Idea Exploration (Refined)

### Preferred Direction
- Moderate layout rewrite of existing landing sections while keeping content scope and route scope unchanged.

### Hero Strategy
- Use a calm, specific value claim with a concrete primary CTA.
- Remove hype phrasing and sales-heavy language.

### Trust/Proof Strategy (MVP)
- Keep proof text-based and lightweight:
  - supported call context
  - explicit scope/positioning
  - privacy link

### Layout Strategy
- Reduce “card soup” by using whitespace and typographic hierarchy as the primary organizer.
- Keep containers only where they materially improve scannability.

### Copy Strategy
- Targeted rewrite of high-impact sections only (hero, supporting value bullets/labels, CTA language).

## 5. Constraints (Refined)

### Implementation Boundary
- Docs and frontend landing surface only:
  - `frontend/src/app/page.tsx`
  - landing components/styles
  - `frontend/src/app/globals.css`
  - `docs/reference/brand_guidelines.md`

### Dependency Constraint
- No new npm or Python dependencies.

### Timeline Constraint
- One focused MVP-fast implementation slice with verification in a single pass.

### Compatibility Constraint
- Preserve existing route structure and CTA destinations (`/sign-in`, `/privacy`).

### Non-Negotiable Quality Constraint
- Maintain WCAG AA contrast, keyboard/focus correctness, and mobile readability.

## 6. Risks / Unknowns (Refined)

### Most Fragile Assumption
- A more institutional visual tone will improve trust and conversion without requiring heavy social-proof assets.

### Earliest Validation Target
- Confirm revised hero/copy clarity and immediate comprehensibility for academic users.

### Rework Risks
- Risk of over-designing beyond MVP.
- Risk of under-shooting with changes too subtle to materially improve trust.

### Primary Operational Risk
- Token/style drift between brand guideline intent and implemented CSS.

### Required Mitigation
- Use explicit acceptance-criteria checklists with required a11y/mobile verification.

## 7. MVP Definition (Refined)

### Must Exist in 2–3 Days
- Updated `docs/reference/brand_guidelines.md` aligned with WF-0010 direction.
- Landing token/style alignment on `/`.
- Targeted layout + copy refresh across high-impact sections.
- Accessibility/mobile verification pass.

### High-Impact Sections to Touch
- Hero
- Trust/supporting context line
- Demo presentation shell
- Final CTA area

### Explicitly Deferred
- Analytics instrumentation.
- SEO/content expansion work.
- A/B testing.

### Explicitly Excluded
- Backend/API/auth changes.
- `/app/*` interaction or flow changes.

### Minimum Verification Bundle
- `cd frontend && npm run lint`
- `cd frontend && npm run check:seo`
- `cd frontend && npx next build --webpack`
- Manual keyboard + mobile readability pass on `/`

## 8. Explicit Non-Goals (Refined)

### Tempting Enhancements Postponed
- Rich testimonial/case-study system.

### Technical Non-Goal
- No design-system overhaul outside landing scope.

### Product Non-Goal
- No change to review generation flow, quota behavior, or auth/sign-in requirements.

### Content Non-Goal
- No long-form feature matrix or deep technical documentation expansion on landing.

### Declared Follow-Up WF Candidates
- Conversion instrumentation + experiment plan.
- Expanded proof assets (logos/testimonials/case snippets), if needed post-MVP.
