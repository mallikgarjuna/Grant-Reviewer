# WF-0010 — PeerLens Landing Design Refresh

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-15

## 1. In Scope

- Refresh landing page `/` to strengthen academic/institutional trust and improve sign-in intent.
- Align visual system across landing:
  - token usage consistency
  - restrained typography hierarchy
  - clearer spacing rhythm and reduced container clutter
- Targeted copy updates in high-impact sections:
  - hero
  - trust/support context line
  - demo shell labels
  - final CTA area
- Preserve current demo behavior and static data contract (presentation-only refresh).
- Update `docs/reference/brand_guidelines.md` to match finalized landing visual direction.
- Preserve accessibility and mobile quality (contrast, keyboard focus, readability).

## 2. Out of Scope

- No backend/API/auth changes.
- No `/app/*` flow or interaction changes.
- No routing changes for `/`, `/sign-in`, `/privacy`.
- No new dependencies.
- No analytics instrumentation or A/B test tooling.
- No SEO/content expansion, testimonial system, logo system, or case-study expansion.

## 3. User / System Flow

### Happy Path

1. User lands on `/`.
2. User immediately reads a clear, academically credible value proposition.
3. User scans trust/support context and demo shell copy.
4. User clicks primary CTA and reaches `/sign-in`.

### Failure Paths

- **FP1: Trust mismatch persists**
  Visual or copy tone still feels generic/startup-like; user exits without clicking CTA.
- **FP2: CTA path regressions**
  CTA or top-nav sign-in link points incorrectly; conversion path breaks.
- **FP3: A11y/mobile regressions**
  Focus visibility, contrast, or mobile readability degrades after layout changes.

## 4. Functional Requirements

- **FR1: Route and intent stability**
  - Keep `/` as the landing route.
  - Preserve CTA destination to `/sign-in`.
  - Keep privacy route `/privacy` accessible from landing.
- **FR2: Visual system coherence**
  - Apply a single, consistent token set for background/surface/border/muted/primary text and controls.
  - Remove token mismatches currently causing inconsistent muted text and borders.
- **FR3: Layout rhythm improvement**
  - Reduce excessive bordered containers where not required.
  - Increase whitespace and line-length discipline to improve scanning.
- **FR4: Copy tone refresh**
  - Replace SaaS/hype phrasing with precise, academically credible wording.
  - Keep claims conservative and aligned with current product capabilities.
  - Use locked copy:
    - `Supported funding calls: NL (NWO, ZonMw), EU/Horizon-Europe (ERC, MSCA)`
    - FAQ question: `How should I use PeerLens?`
- **FR5: Accessibility and responsive quality**
  - Maintain WCAG AA contrast targets.
  - Maintain visible keyboard focus states.
  - Preserve readability and interaction clarity on mobile layouts.
- **FR6: Verification gate (must pass before implementation close)**
  - `cd frontend && npm run lint`
  - `cd frontend && npm run check:seo`
  - `cd frontend && npx next build --webpack`
  - Manual keyboard + mobile readability pass on `/`

## 5. Data & API Contracts

- **Landing data contracts**
  - No new data models or backend contracts.
  - Existing static demo content contract remains unchanged (no new tabs or API-driven demo behavior).
- **Validation rules**
  - No claims that imply unsupported product behavior.
  - CTA/link destinations must remain valid (`/sign-in`, `/privacy`).
- **State transitions**
  - Existing landing interactions remain client-local.
  - No new cross-route state or backend round-trip introduced by this PRD.

## 6. Components / Modules

- `frontend/src/app/page.tsx`
  - main landing structure, hero, trust text, CTA placement/copy
- `frontend/src/app/globals.css`
  - token and typographic usage alignment
- `frontend/src/app/_components/landing/demo-tabs.tsx`
  - adjust presentation shell styling/copy only (no behavior expansion)
- `frontend/src/app/_components/landing/faq-accordion.tsx`
  - styling/tone consistency updates only if needed
- `docs/reference/brand_guidelines.md`
  - source-of-truth alignment for chosen palette/type/usage rules

## 7. Edge Cases

- Extremely narrow mobile widths must not produce horizontal overflow in hero/demo blocks.
- Updated muted text colors must remain readable against all used surfaces.
- Reduced card count/border usage must not remove critical grouping cues.
- Existing CTA and navigation affordances must remain obvious after visual simplification.

## 8. Telemetry (Minimal)

- No new analytics integrations in this phase.
- Preserve existing stable attributes/hooks if already present.
- Keep existing `data-*` hooks unchanged to avoid breaking future instrumentation work.

## Deferred / Not in MVP

- Conversion instrumentation and A/B experimentation.
- Expanded proof assets (institution logos, testimonials, case snippets).
- Broader content/SEO expansion outside current landing scope.
- Any app-level UX or backend behavior changes.

## Open Questions (if any)

- None blocking for this PRD phase.

## Ready-for-Tasks Checklist

- Scope remains landing-only (`/`, supporting landing components/styles, brand guideline updates).
- No backend/API/auth or `/app/*` behavior changes are introduced.
- Existing CTA/link destinations remain stable (`/sign-in`, `/privacy`).
- Token/copy/layout changes are specific enough for sequential task generation.
- Verification gate is explicit and executable.

## Changelog

- v0.1 (2026-02-15): Initial PRD from spec.
- v0.2 (2026-02-15): Applied risk-audit edits, added readiness checklist/verification gate, and marked Ready for Tasks.
- v0.3 (2026-02-15): Added locked funding-line and FAQ usage copy requirements.
