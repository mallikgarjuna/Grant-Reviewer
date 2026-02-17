# WF-0009 — PeerLens Landing Page PRD

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-02-14

## 1. In Scope

- Public landing page route: `/`
  - Nav: PeerLens wordmark, `Privacy` link, `Sign In` link/button
  - Hero: headline + subhead + primary CTA “Check My Draft Now” → `/sign-in`
  - “Supported calls” (text-only): `NWO Veni · ERC Starting · MSCA PF`
  - Problem/Agitation section (“Reviewer #2” anxiety)
  - Solution/Demo: 3 static tabs (NWO Veni / ERC Starting / MSCA PF)
    - Each tab shows: snippet (80–120 words), 4 feedback cards, example readiness score (0–100)
    - Feedback card includes: Criterion, Finding, Suggested fix, Micro-rewrite (Example)
    - Demo label includes the exact copy from spec:
      - “Examples only. Sign in to get feedback on your proposal text.”
      - “Export your review. Delete your data anytime. See Privacy.”
  - Benefits: Readiness Score, Compliance Check, Time Saved
  - How it works: Sign in → select call/section + paste snippet → get review
  - Social proof (text-only): supported calls ticker/list (no funder logos; no implication of endorsement)
  - FAQ (accordion): generic AI, why sign in, what to paste, data handling (links to `/privacy`), deletion
  - Footer: Privacy link only + copyright
- Privacy page route: `/privacy` (minimal, content-driven page) including:
  - PeerLens does not use proposal snippets to train its models
  - Proposal snippets are retained until the user deletes them (self-serve deletion)
  - Minimal operational logs/backups may be retained for up to 30 days

## 2. Out of Scope

- Any signed-out “run a real review” flow (no user text input on landing; no `POST /reviews`)
- Pricing, blog/content hub, testimonials, funder logos, dark mode
- Dashboard/app functionality (covered by other specs/WFs)

## 3. User / System Flow

### Happy path

1. User lands on `/`.
2. User reads hero + supported calls, scans trust line, scrolls to demo.
3. User switches between static demo tabs to understand “review-criteria-aligned” feedback.
4. User clicks “Check My Draft Now” → `/sign-in`.
5. User optionally visits `/privacy` for reassurance, then returns to CTA.

### Failure paths (2–3)

- **FP1: `/privacy` missing or broken link** → user trust drops; user bounces.
- **FP2: `/sign-in` route misconfigured** → CTA leads to 404; conversion fails.
- **FP3: Demo content overflows on mobile** → user cannot read snippet/cards; perceived quality drops.

## 4. Functional Requirements

- **Routing**
  - Primary CTA routes to `/sign-in`.
  - Privacy link routes to `/privacy`.
- **Demo**
  - Demo is static-only (no backend calls, no user input, no network dependency).
  - 3 tabs exactly: NWO Veni, ERC Starting, MSCA PF.
  - Each tab includes: 1 snippet (80–120 words), 4 cards, 1 readiness score (0–100).
  - Demo includes an “Examples only…” label and a privacy link near the demo/CTAs.
  - Readiness score is explicitly presented as an example visualization, not a computed metric on landing.
- **Copy safety**
  - No outcome promises (no “increase acceptance chances”, no success-rate claims).
  - Do not use “rubric” terminology on `/` (use “review criteria” / “review-criteria-aligned”).
  - “Export your review” and “Delete your data anytime” appear only as demo label copy (as in spec).
- **Accessibility**
  - Tab UI is keyboard-navigable (focus-visible, Enter/Space activates).
  - Accordions are keyboard and screen-reader friendly (button semantics + ARIA).
  - Color contrast and focus rings meet the existing tokenized style.
- **Performance**
  - Landing uses lightweight components; no heavy media; assets are optimized.
  - No client-side data fetching required for initial render.

## 5. Data & API Contracts

### Landing demo data

- Static demo content lives in code as a typed constant (no CMS in MVP).
- Proposed shape:

```ts
type LandingDemoTabId = "nwo_veni" | "erc_starting" | "msca_pf";

type LandingDemoCard = {
  criterion: string;
  finding: string;
  suggestedFix: string;
  microRewriteExample: string;
};

type LandingDemoTab = {
  id: LandingDemoTabId;
  label: string;
  snippet: string;
  cards: LandingDemoCard[]; // length === 4
  readinessScore: number; // 0..100 (example only)
};
```

### State transitions

- Default tab selected on load (e.g., NWO Veni).
- User changes active tab; no URL state required in MVP.

### API calls

- None for the landing page MVP (no backend fetches).

### Preconditions (Must Be True Before Landing Ships)

The landing page includes the demo label copy promising export + deletion. To keep this truthful at launch:

- **Export**: The signed-in review experience must provide an “Export your review” action that produces a user-copyable artifact of the review.
  - MVP acceptable outputs: “Copy as text” and/or “Download .txt”.
  - Not required for MVP: PDF export.
- **Delete**: The signed-in review experience must provide a “Delete review” action that hard-deletes the review, its cards, and the associated snippet text (per existing deletion decisions).
- **Privacy**: `/privacy` must exist and contain the specific statements listed in §1.

## 6. Components / Modules

- `frontend/src/app/page.tsx`: PeerLens landing page UI
- `frontend/src/app/privacy/page.tsx`: minimal privacy content
- `frontend/src/lib/landing-demo.ts`: static demo tabs data + types
- `frontend/src/app/_components/landing/demo-tabs.tsx`: `use client` tab switcher (minimal JS; no third-party deps)
- (Optional) `frontend/src/app/_components/landing/*`: extracted UI components (cards, FAQ) if `page.tsx` gets too large

## 7. Edge Cases

- Very small screens: demo stacks vertically; snippet and cards remain readable without horizontal scrolling.
- Reduced motion: no essential animation; respects `prefers-reduced-motion`.
- Long translated strings / copy edits: layout should wrap without overlap.

## 8. Telemetry (Minimal)

- MVP baseline: no analytics vendor integration required.
- Add stable `data-*` attributes to key elements for later instrumentation:
  - `data-pl="cta-primary"`
  - `data-pl="demo-tab"`
  - `data-pl="faq-toggle"`

## Deferred / Not in MVP

- Funder logos, testimonials, pricing page, blog, video demo
- A/B testing, heatmaps, conversion analytics vendor integration

## Open Questions (if any)

- None (spec is locked to static demo content and routes).

## Changelog

- v0.1 (2026-02-14): Initial PRD from spec.
- v0.2 (2026-02-14): Applied risk audit edits; locked privacy page content; marked Ready for Tasks.
- v0.3 (2026-02-14): Define MVP export/delete preconditions; add landing copy guardrail (“no rubric”).
