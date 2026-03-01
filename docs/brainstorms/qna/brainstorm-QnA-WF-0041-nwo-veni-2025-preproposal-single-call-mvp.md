# WF-0041 — NWO Veni 2025 (Preproposal) Single-Call MVP

Artifact: brainstorm-qna
Version: v0.1
Status: In progress
Last Updated: 2026-03-01

---

## Preflight Step 1 — Long-Form Narrative Intake (User Narrative)

The user provided the following narrative as the baseline intent for WF-0041:

We need one call to be fully usable end-to-end: `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml` (NWO Veni 2025 preproposal). The goal is a single-call MVP that proves the product works for a real applicant workflow using the universal engine (no multi-agency abstractions, no generalization beyond what this call forces).

Who experiences the problem / why now: Right now, we have pieces of universal structured submit + pipeline-v1 review, but the experience is not yet “one real call works as promised.” A researcher trying to use the app for this call can’t reliably go from selecting the call → entering the required proposal parts → being blocked on non-compliant inputs → running review → seeing results that are clearly tied back to the call’s evaluation criteria/elements and proposal structure. We need this because it’s the minimum trust-building slice: without a fully working single call, everything else is speculative.

The exact happy path (what “done” means):
1) Operator/dev can ingest + activate this call from the canonical YAML so it appears as an available call in the app.
2) A user can pick this call and see a call-driven submit UI with nodes/sections derived from the call definition.
3) User can paste text into each required node and submit.
4) Compliance runs on submission and blocks when enforceable constraints are violated, with clear failure UX.
5) When compliant, the universal engine runs the review using pipeline-v1 and returns results.
6) Results are call-aware: findings trace to the right proposal node(s) and the right evaluation criteria/elements.

What’s currently broken/missing (concrete failures):
- Call ingestion/activation for this YAML is unreliable or too manual.
- The submit UI is still partially hardcoded / not fully driven by the call-definition nodes.
- Compliance checks don’t run, don’t block when they should, or block incorrectly without clear UX messaging.
- Review execution succeeds but results aren’t mapped cleanly back to proposal nodes / criteria/elements (or are too generic).
- Edge conditions cause confusing errors even in the happy path (hardening mostly deferred to P0 #2).

Constraints / non-goals:
- Single call only; universal engine only; no multi-agency abstractions.
- No broad refactors unless they directly unblock the single-call happy path.
- Keep tasks atomic (<=3 files per task).
- Optimize for “one real call works” over “framework for many calls.”

Acceptance signal: end-to-end flow is demoable repeatedly without manual fixes between runs.

## Preflight Step 2 — Repo Reality Snapshot (Read-Only, Timeboxed)

Snapshot bullets (2026-03-01):
- The single call YAML is already authored (v2) with proposal nodes, evaluation criteria/elements, node expectations, reviewer policy, and domain-limited word limits: `backend/data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml`.
- Ingestion exists: `backend/scripts/ingest_call.py` (v1/v2 detection + DB upsert).
- Universal submit UI exists and loads calls + nodes + optional per-call domain options: `frontend/src/components/submit/UniversalSubmitForm.tsx`.
- Deterministic compliance exists: `backend/app/services/compliance_engine.py` and `POST /api/check-compliance` in `backend/main.py`.
- Structured review execution exists: `POST /api/structured-review`; reviewer-policy violations can block based on forbidden terms in LLM output: `backend/app/services/review_execution_core.py`.

Open questions suggested by this snapshot:
- Is it acceptable that review-detail UI is still Veni-hardcoded labeling/order (since we’re single-call), or do we want call-aware labels sourced from call metadata even for this one call?
- Should the ENW/Science pilot domain selector be optional defaulting to “none”, or require explicit selection to avoid accidental wrong word limits?
- What’s the minimum “call-aware results” bar: explicit references to evaluation criteria/elements, vs section grouping only?
- If reviewer-policy blocking triggers, what UX behavior is acceptable for MVP?

## Section 1 — Problem Statement (Interactive)

**Brainstorming Q&A:**

**Q1: Who is the primary “MVP must satisfy” actor for WF-0041?**
- A) Applicant/researcher end-user (submit + results trust is the core)
- B) Operator/dev (ingest/activate + demo pipeline is the core)
- C) Both equally (we won’t ship unless both are smooth)
  > Recommendation: A — If the applicant flow works, operator friction is typically fixable without redefining the product. B risks optimizing for “it runs” without the user trust bar. C increases scope and slows the MVP.
  > **Selected: A**

**Q2: What is the single biggest current blocker to “one call works”?**
- A) Call doesn’t reliably ingest/activate/show up (availability)
- B) Submit UI isn’t truly call-driven for the required nodes (input capture)
- C) Review runs but results aren’t clearly tied to proposal sections + evaluation criteria/elements (trust/interpretability)
  > Recommendation: C — “Works” for users is primarily about traceability and interpretability; A/B are necessary plumbing but don’t satisfy the product promise alone.
  > **Selected: C**

**Q3: When you say “call-aware results,” what’s the minimum bar for MVP?**
- A) Each finding/card is tied to a proposal section and explicitly references the relevant evaluation element(s)
- B) Findings/cards are grouped by proposal section labels only (criteria/elements not shown)
- C) Only an overall summary is acceptable for MVP; section-level traceability can wait
  > Recommendation: A — This aligns with the “evaluation criteria/elements grounded” promise and reduces “generic AI feedback” risk. B/C defer the core trust signal.
  > **Selected: A**

**Q4: How should the ENW/Science pilot domain be handled in the applicant flow?**
- A) Optional domain selector; default is “none” (100-word research idea limit) unless user chooses ENW/Science (500)
- B) Domain must be explicitly selected before submit to prevent accidental wrong limit
- C) Hide domain entirely for MVP; always apply default (100)
  > Recommendation: A — Minimal friction while still supporting the real pilot behavior. B is safer but adds gating UX; C breaks a real call behavior.
  > **Selected: A**

**Q5: What’s the problem framing we should optimize for (the “why now”)?**
- A) Demo credibility: “one real call works end-to-end repeatedly”
- B) User trust: “outputs are traceable to evaluable structure + evaluation criteria/elements”
- C) Operational confidence: “deterministic checks prevent obviously invalid submissions”
  > Recommendation: B (with A as the proof) — Trust is the core; repeatable demo is the evidence. C matters but is supportive, not primary.
  > **Selected: B**

## Preflight Open Questions — Decisions (Interactive)

**Brainstorming Q&A:**

**Q1: Review detail page labeling/order (single-call MVP)**
- A) Keep the current hardcoded Veni labels/order for WF-0041; defer call-aware mapping to P1 #2
- B) Make it call-aware now (use call metadata / node labels) even though we’re single-call, to reduce “hardcoded trust” risk
- C) Hide ordering/labels entirely in detail view for MVP; show flat cards only
  > Recommendation: A — Fastest path to single-call MVP; avoids broadening scope.
  > **Selected: B**
  > User constraint override: no hardcoding anywhere; even single-call MVP should use universal/call-driven behavior.

**Q2: Domain selection safety for ENW/Science pilot**
- A) Optional selector with default “none” (100-word limit) and clear helper text
- B) Require explicit domain choice before enabling submit (forces correctness)
- C) Auto-detect domain from content (risky/implicit)
  > Recommendation: A — Minimal friction; correctness remains user-controlled.
  > **Selected: A**

**Q3: “Call-aware results” display contract for MVP**
- A) UI surfaces evaluation element identifiers/names per finding/card (explicit criteria/elements traceability)
- B) UI groups by proposal section only; criteria/elements exist only inside the prompt/back-end but aren’t shown
- C) Only overall summary + generic feedback; no structured traceability in UI
  > Recommendation: A — Matches the trust bar set in Section 1.
  > **Selected: A**

**Q4: Reviewer-policy blocking failure UX (if it triggers)**
- A) Fail the review with a clear error + one-click retry
- B) Auto-retry once server-side with a stricter system instruction, then fail if still blocked
- C) Never hard-block on policy for MVP (downgrade blocking to warning)
  > Recommendation: B — Preserves the policy contract while keeping the happy path resilient.
  > **Selected: B**
