# WF-0009 — PeerLens Landing Page

Artifact: brainstorm  
Version: v0.19  
Status: Draft  
Last Updated: 2026-02-14

---

## 1. Problem Statement (Complete)

- Primary audience: new researchers/PIs drafting grant proposals.
- Core pain: unclear reviewer expectations; existing feedback feels generic (not rubric-grounded).
- When pain is most acute (priority order): early ideation/outline → mid-draft concreteness → late polish.
- Current workaround (priority order): peers/mentors/internal review (slow/inconsistent) → old successful proposals/checklists (hard to adapt) → generic LLMs (not expectation-linked).
- Why now (priority order): increased competitiveness/criteria-fit pressure → trust gap with generic AI unless it’s grounded.

### Problem Definition (Working)

New researchers/PIs need a fast, trustworthy way to understand “what reviewers expect” and get expectation-linked feedback; current feedback channels are often generic, slow, or inconsistent.

---

## 2. Desired Outcome (Complete)

- Primary landing KPI (priority order): click-through to “Try with your text” / sign-in → demo engagement → contact/waitlist conversion.
- Intended behavior change: “I trust this enough to try it with my text (login) now.”
- “Good enough” MVP landing: clear hero + 3 benefits + static example demo + CTA + brief trust/privacy reassurance.
- Core positioning takeaway: “PeerLens gives rubric-grounded, expectation-linked feedback — not generic writing tips.”
- Biggest trust blocker to address (priority order): grounded-in-expectations vs generic AI → accuracy/trustworthiness (avoid overclaiming) → privacy/training concerns.

---

## 3. Target User / Actor (Complete)

- Primary segment (priority order): early-career PI / first major grant → postdoc / fellowship applicant → any academic researcher.
- Primary context (priority order): drafting from scratch → revising after internal feedback → final-week polish.
- Primary unit of value (priority order): one section/paragraph snippet → 2–3 page narrative → entire proposal.
- Primary acquisition channel: search / “grant review / feedback” intent.
- Primary fear to defuse (priority order): “generic / not aligned to reviewer expectations” → “confidently wrong” → “homogenized proposal.”

---

## 4. Rough Idea Exploration (Complete)

- Demo should primarily demonstrate: expectation-linked feedback feels meaningfully different from generic advice.
  - Secondary emphasis (priority order): safety/ethics posture → speed/iteration.
- Simplest credible demo format (priority order): 3 scenario tabs with pre-written snippet + pre-written feedback cards → short “tour” steps.
- “Rubric-grounded” phrasing (priority order): be explicit and define it in 1–2 lines + show it in the demo → if needed, simplify wording to “reviewer expectations” without losing meaning.
- CTA style: direct (“Try with your text” / “Get feedback”).
- Trust-protecting avoid list (priority order): over-promising outcomes → too many features/pricing details → unsupported privacy/training claims.

### Rough Direction (Working)

Landing should quickly define “expectation-linked feedback,” show it via a few concrete examples (tabs), and funnel into an authenticated “try with your text” flow, without making outcome promises.

### Landing Structure (Blueprint-Guided; Refinement)

- Framework: Product-led (Framework A).
- MVP section order (target): Nav+Hero → Benefits → Static Demo Tabs → How It Works → FAQ (objections) → Final CTA+Footer.
- Social proof in MVP: omit logos/testimonials; earn trust via clarity + conservative claims.
- Primary CTA destination (priority order): “Try with your text” → `/sign-in` (primary) → `/app` (fallback/secondary).
- Objections to address (priority order): “Is this generic (or expectation-linked)?” → privacy/training reassurance → “Will this homogenize my proposal?” → “Can I try without logging in?” → “What do I actually get back?”

---

## Landing Page Content (Copy + Sections; Refinement)

- Hero headline direction (priority order; avoid “AI” wording):
  - “Expectation-linked feedback for your grant writing.”
  - “Find what reviewers expect — fast.”
- Hero subheadline direction:
  - Explain mechanism: expectation-linked feedback on a single snippet → faster iteration → better criteria fit (no outcome promises).
- Benefits (top 3):
  - Expectation-linked findings
  - Scannable severity
  - Copy-ready next steps
- How-it-works (MVP steps):
  - Choose call/section → paste snippet (in app) → get expectation-linked feedback + copy
- FAQ (MVP 5 objections; A + B prioritized; C secondary):
  - “Is this generic (or is it expectation-linked)?”
  - “Do you train on my text?”
  - “Why do I need to sign in?”
  - “What should I paste?”
  - “Can I delete my review/snippet?”
  - Secondary candidates (not in MVP 5): supported funders, time-to-results, export/copy, compliance, homogenization, accuracy.

---

## Hero + CTA + Footer (Microcopy; Refinement)

- Public terminology: use “review criteria” (avoid internal “expectation” DB term).
- Hero headline (current preference):
  - “Review-criteria-aligned feedback for your grant writing — find what reviewers look for, fast.”
- Hero subheadline direction (combined):
  - “Get review-criteria-aligned feedback and concrete next steps on a single snippet.”
- Primary CTA label (current preference):
  - “Get feedback on your proposal text”.
- How-it-works steps:
  - “Select funding call & section → Paste a snippet → Get review-criteria-aligned feedback”.
- Footer: include CTA + `Privacy` + explicit “Delete your data” mention (linking into `/privacy`).

### Copy Decisions (Locked)

- How-it-works Step 1 label: “Select funder call & section”.
- Preferred phrasing: “review-criteria-aligned feedback” (over “criteria-linked feedback”).
- Hero/subheadline/CTA consistency: prefer “proposal text” wording.
  - “Call” term in copy: “funding call”.
  - Step 1 final wording: “Select funding call & section”.
  - Subheadline final: “Get review-criteria-aligned feedback and concrete next steps on a single snippet.”

### Trust + FAQ Decisions (Locked)

- Trust line format: split into 2 short lines + 1 link (near demo).
- Export wording: “Export your review”.
- Deletion promise: “Delete your data anytime”.
- “Generic” objection phrasing (no “AI” wording): “Is this aligned to review criteria, or generic feedback?”
- Primary CTA destination: `/sign-in`.
  - Trust line (exact, 2 lines):
    - Line 1: “Examples only. Sign in to get feedback on your proposal text.”
    - Line 2: “Export your review. Delete your data anytime. No training on your text.”
  - FAQ ordering: criteria-aligned vs generic → what to paste → why sign in → no training → delete data.
  - FAQ answer depth: 1–2 sentences each + link to `/privacy` where relevant.

---

## Static Demo (MVP; Refinement)

- Demo scenarios (3 tabs):
  - NWO Veni
  - ERC Starting Grant
  - MSCA Postdoctoral Fellowship (PF)
- Tab labels: use the program names (“NWO Veni” / “ERC Starting” / “MSCA PF”).
- Per-scenario content (minimum):
  - Snippet text + 3–5 feedback cards + “review-criterion tags”
- Snippet length: ~120–180 words (one paragraph).
- Snippet source guidance: primarily fictional/generic grant-like text, lightly flavored by real-call patterns (credible without implying a real call/rubric).
- Feedback card anatomy:
  - Severity → Finding → Review criterion tag → Concrete next step
- Cards per scenario (MVP): 4 cards.
- “Concrete next step” length: 2–3 sentences.
- Tag wording: plain-language, criteria-oriented tag using prefix “Review criterion: …” (avoid strong “rubric traceability” claims).
- Trust reassurance placement:
  - Short trust line near the demo + link to `/privacy` (avoid burying it; avoid leading with it in hero).
- Trust line (exact, 2 lines + link):
  - Line 1: “Examples only. Sign in to get feedback on your proposal text.”
  - Line 2: “Export your review. Delete your data anytime. No training on your text.”
  - Link: `Privacy`
- MVP nav:
  - Logo + “Privacy” link + primary CTA button

---

## 5. Constraints (Complete)

- Time constraint (priority order): 2–3 days → 1 week (more polished).
- Signed-out demo: 100% static examples; no user text input; no real review run.
- Required supporting pages/links: include `/privacy` (minimal) + basic footer links.
- Allowed claims: conservative, verifiable claims only; avoid outcome promises.
- Quality bar (MVP): mobile-first + fast load + accessibility basics.

---

## 6. Risks / Unknowns (Complete)

- Most fragile assumption (priority order): “expectation-linked” messaging feels credible without real user input → search-intent visitors trust a new brand enough to click through.
- Validate earliest (priority order): demo scenarios + copy make people say “this is different” → CTA wording/placement converts.
- Biggest rework risk (priority order): over-promising “rubric-grounded” before backend traceability supports it → needing extra pages unexpectedly (FAQ/pricing/blog).
- Stall risk (priority order): unclear product narrative / copy disagreements → SEO/content rabbit holes → waiting on auth/provider setup.
- Unknown affecting scope: final set of demo scenarios/snippets/outputs to ship.

---

## 7. MVP Definition (Complete)

- 3-day “shipped” must-have: landing (`/`) with hero + benefits + static demo tabs + primary CTA to sign-in/app.
- Minimum demo content: 3 scenarios (each: snippet + 3–5 feedback cards).
- Explicitly OK to defer: testimonials/logos, pricing, detailed FAQ, SEO tuning beyond basics, and visual polish beyond “clean and credible.”
  - Blog: defer `/blog` entirely in this WF.
- Must NOT include: signed-out “run a real review” flow; any text upload on landing.
- Copy safety bar (priority order): conservative wording; no outcome promises; clear “example/demo” labeling → (secondary) keep SEO/content scope tight.

---

## 8. Explicit Non-Goals (Complete)

- Postpone (tempting feature) (priority order): signed-out “paste your text” demo → pricing page.
- Explicitly not solving: improving review quality/LLM prompting/back-end evaluation logic.
- Avoid committing publicly (priority order): “rubric-grounded” traceability details we can’t reliably show yet → acceptance probability / success-rate claims.
- Belongs in a future WF: SEO/content program (blog, posts, lead magnets).
- Design scope boundary: landing page UI only; no full design system overhaul.

---

## Revision History

- v0.1 (2026-02-14): Captured initial Problem Statement + Desired Outcome decisions.
- v0.2 (2026-02-14): Captured Target User / Actor decisions.
- v0.3 (2026-02-14): Captured Rough Idea Exploration decisions.
- v0.4 (2026-02-14): Captured Constraints decisions.
- v0.5 (2026-02-14): Captured Risks / Unknowns decisions.
- v0.6 (2026-02-14): Captured MVP Definition decisions (blog pending).
- v0.7 (2026-02-14): Finalized MVP Definition decision to defer `/blog` in this WF.
- v0.8 (2026-02-14): Captured Explicit Non-Goals decisions.
- v0.9 (2026-02-14): Refined landing page section structure using landing page blueprint (Framework A).
- v0.10 (2026-02-14): Refined hero/benefits/how-it-works/FAQ set (avoid “AI” wording in hero).
- v0.11 (2026-02-14): Refined static demo scenarios + card anatomy + trust reassurance placement.
- v0.12 (2026-02-14): Refined demo tab labels, snippet length, expectation-tag wording, and trust-line microcopy.
- v0.13 (2026-02-14): Refined hero/subheadline/CTA/footer microcopy; aligned away from internal “expectation” term.
- v0.14 (2026-02-14): Locked “review criteria” terminology and updated CTA + demo tag wording.
- v0.15 (2026-02-14): Locked how-it-works phrasing + “proposal text” consistency; expanded trust line to include export + deletion.
- v0.16 (2026-02-14): Locked trust-line format (2 lines + link), export/delete wording, and FAQ objection phrasing.
- v0.17 (2026-02-14): Locked “funding call” wording, final how-it-works label, final subheadline, trust-line exact text, and FAQ ordering.
- v0.18 (2026-02-14): Harmonized landing copy to “review-criteria-aligned” and synced demo card terminology + trust line.
- v0.19 (2026-02-14): Finalized demo + FAQ depth (4 cards/scenario, 2–3 sentence next steps, short FAQ answers).

## Notes

- Brainstorming is being done in batches (up to 5 questions per section) for speed.
