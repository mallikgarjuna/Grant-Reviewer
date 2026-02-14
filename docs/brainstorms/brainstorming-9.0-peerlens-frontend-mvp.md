# Brainstorming 9.0: PeerLens Frontend MVP (Ship-Fast UX + Static Demo)

**Date**: 2026-02-14  
**Task ID**: 9.0  
**Pipeline Phase**: Phase 0 (Brainstorming)  
**Status**: Draft (v0.1)  
**Last Updated**: 2026-02-14  

## Goal (MVP)

Ship a credible, calm, researcher-friendly PeerLens web UI that drives:
1) trust on the landing page, and
2) a tight conversion into the authenticated “submit → results → copy” loop.

Constraints (MVP):
- Login required for real review generation.
- Landing demo is static (no backend calls).
- Keep pages thin; avoid scope creep.

## Decisions Locked (MVP)

These are decision closures for fast implementation with minimal churn:

- Product name in UI: **PeerLens** (repo/internal name can remain “Grant Reviewer”).
- Minimal routes to ship:
  - `/` landing with static demo switcher
  - `/privacy` minimal privacy page
  - `/blog` optional (keep to 1 post max)
  - `/sign-in` (Clerk)
  - `/app` single-page submit wizard (call → section → snippet → submit)
  - `/app/reviews/[review_id]` results
  - `/app/reviews` recent review links (device-only local storage)
- Signed-out demo:
  - Pre-generated examples; no user text input; no calls to `POST /reviews`.
  - Demo scenarios: `NWO-Veni`, `ERC-Starting`, `MSCA-PF`.
- Privacy + retention:
  - “No training on snippets” claim in `/privacy` and in-product reassurance.
  - “Retained until you delete” with self-serve deletion.
  - Minimal operational logs/backups retained up to **30 days**.
- Delete review semantics:
  - Hard-delete `Review`, `ReviewCard`s, and associated proposal snippet text.
  - No quota refund.
  - No “rerun from results” after delete (return to `/app`).
- Results scan UX:
  - No interactive filter chips in MVP.
  - Still scan-first: severity-forward presentation and ordering.

## UX Concepts (MVP)

### Landing: “Show, don’t ask”

- Static demo switcher builds credibility without cost risk.
- Clear CTA to authenticated app: “Try with your text”.
- Calm authority tone: rubric-grounded, expectation-linked feedback (not generic writing tips).

### App: single-page wizard

- One primary action per state.
- Clear context line for the selected call/section (dense, not verbose).
- Disable submit while in-flight; show “refresh safely” guidance around timeouts.

### Results: decisive, scannable, exportable

- Put the “what’s most urgent” signal above the fold.
- Make “Copy all feedback” and “Copy summary” the default next action.
- Show a simple, explicit “Delete review” action with confirmation.

## Demo Content Drafts (Landing; static)

Note: These are intentionally “demo-only” and do not need to correspond to ingested call YAML yet.

### Demo 1 — NWO Veni (Example)

- **Who it’s for**: Early-career PI/Postdoc
- **What you paste**: A short “Approach / Methods” paragraph
- **What PeerLens highlights** (sample output):
  - **CRITICAL**: “Methods are described at a high level; add concrete steps, feasibility checks, and a minimal validation plan.”
  - **WARNING**: “Objectives are stated but not measurable; add 1–2 quantitative milestones.”
  - **SUCCESS**: “The motivation is clearly tied to a gap in the field.”
- **Why it feels rubric-grounded**: Each point references an “expectation” label (demo-only) like “Feasibility”, “Measurable objectives”, “Novelty positioning”.

### Demo 2 — ERC Starting Grant (Example)

- **Who it’s for**: PI writing an extended synopsis
- **What you paste**: A “Synopsis / Vision” paragraph
- **What PeerLens highlights** (sample output):
  - **CRITICAL**: “Breakthrough claim is asserted but not justified; add 1–2 lines contrasting with state-of-the-art.”
  - **WARNING**: “Risk mitigation is missing; add at least one fallback strategy.”
  - **SUCCESS**: “The expected impact is stated clearly and linked to outcomes.”
- **Why it feels rubric-grounded**: expectation labels (demo-only) like “State-of-the-art contrast”, “Risk mitigation”, “Impact clarity”.

### Demo 3 — MSCA Postdoctoral Fellowship (Example)

- **Who it’s for**: Postdoc drafting training + mobility narrative
- **What you paste**: A “Training / Career development” paragraph
- **What PeerLens highlights** (sample output):
  - **CRITICAL**: “Training plan is generic; specify named skills + supervision structure + measurable outputs.”
  - **WARNING**: “Host fit is implied but not evidenced; add 1–2 specifics on infrastructure or mentorship.”
  - **SUCCESS**: “Career trajectory is coherent and plausible.”
- **Why it feels rubric-grounded**: expectation labels (demo-only) like “Training specificity”, “Host fit evidence”, “Career path coherence”.

## Risks / Watch-outs

- “Retained until you delete” requires real deletion semantics; do not ship a cosmetic-only delete.
- `/app/reviews` must be labeled device-only to avoid cross-device expectations.
- Static demo content must not imply the system reviewed their text; keep it clearly “example”.
- Avoid expanding traceability in MVP unless backend returns expectation metadata (otherwise it’s a promise gap).

## Next Phase Gate

If approved, Phase 1 PRD should lock:
- Exact minimal UI copy for demo + privacy statements.
- Delete-review UX (confirmations, success states).
- Exact “device-only library” behavior and labeling.
- Success criteria for MVP (activation + retention).

## Revision History

- **v0.1** (2026-02-14): Initial ship-fast Phase 0 decisions + demo draft content.

