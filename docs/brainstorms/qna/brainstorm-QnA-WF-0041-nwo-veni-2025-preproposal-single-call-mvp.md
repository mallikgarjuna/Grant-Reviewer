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

## Section 2 — Desired Outcome (Interactive)

**Brainstorming Q&A:**

**Q1: What’s the concrete MVP “success demo” for WF-0041?**
- A) Full happy-path in UI: select call → fill 3 nodes → compliance blocks/clears → submit → review detail shows section + evaluation element traceability
- B) Backend-only proof: ingest + compliance + structured-review returns call-aware results (UI can be rough)
- C) UI-only proof: submit UI is call-driven; review can be stubbed
  > Recommendation: A — This matches the P0 intent (“one real call works end-to-end”) and avoids shipping an MVP that’s only partially user-visible.
  > **Selected: A**

## Section 3 — Target User / Actor (Interactive)

**Brainstorming Q&A:**

**Q1: Who is the primary end-user persona for the single-call MVP?**
- A) Early-career researcher applying to Veni (self-serve)
- B) PI / senior researcher reviewing a junior’s draft (advisor)
- C) Research support office / grant officer (internal reviewer)
  > Recommendation: A — Aligns to the program and keeps product assumptions simple for MVP.
  > **Selected: A**

## Section 4 — Rough Idea Exploration (Interactive)

Repo grounding note (2026-03-01):
- Review detail page currently contains explicit Veni-only hardcoding: `VENI_NODE_LABELS` / `VENI_NODE_ORDER` in `frontend/src/app/app/reviews/[reviewId]/page.tsx`.
- Backend `GET /reviews/{review_id}` already returns per-card `node_title`, `criterion`, and `evaluation_element_name` (sufficient to render call-aware cards), but does not include call metadata needed to order sections without hardcoding.
- Domain options are currently hardcoded client-side: `frontend/src/lib/submit/domainOptions.ts`.

**Brainstorming Q&A:**

**Q1: Where is the “no hardcoding / universal” work most urgent for MVP credibility?**
- A) Review detail page: remove Veni hardcoded node labels/order; render cards grouped by `node_title` from backend
- B) Submit page: remove any remaining call-specific assumptions; ensure it renders any number of nodes purely from API data
- C) Domain: remove `DOMAIN_OPTIONS_BY_CALL` hardcoding and source domain options from call metadata/config
  > Recommendation: A (with C close behind) — Review detail has the most obvious hardcoding; domain options are also explicitly hardcoded today.
  > **Selected: A**

**Q2: What should drive node labeling and ordering in UI (both submit + review detail)?**
- A) DB node ordering + node titles from `/calls/{id}/nodes` and/or `/calls/{code}/metadata` (single source)
- B) Call YAML shipped to frontend (client-side parsing)
- C) A new backend “UI render model” endpoint tailored for frontend
  > Recommendation: A — Leverages existing contracts and keeps frontend thin.
  > **Selected: A**

**Q3: How should domain options be handled given “no hardcoding anywhere”?**
- A) Keep domain optional, but fetch options from backend metadata/config for the selected call (so non-domain calls show nothing)
- B) Keep frontend map for now; fix later (violates “no hardcoding”)
- C) Remove domain from MVP entirely
  > Recommendation: A — Universal behavior: only show domain UX when declared by the call.
  > **Selected: A**

**Q4: How should results be presented to emphasize criteria/elements grounding?**
- A) Default view groups cards by proposal section (`node_title`), each card shows evaluation element name + criterion
- B) Default view groups by criterion first
- C) No grouping; flat list
  > Recommendation: A — Matches the trust bar and aligns to applicant mental model (“which section is this about?”).
  > **Selected: A**
  > User note: verify current repo behavior; only implement if the UI is not already doing this.

**Q5: If we must add exactly one new backend capability to eliminate hardcoding, what should it be?**
- A) Return domain options (and active word-limit context) in call metadata/config for the selected call
- B) Return stable node display labels + order for review detail (explicitly)
- C) Return a single “review detail render model” that includes everything the UI needs
  > Recommendation: A — Node titles exist, but domain options are currently client-hardcoded. Also, domain should be call-specific and absent for calls that don’t use it.
  > **Selected: A**

## Section 5 — Constraints (Interactive)

**Brainstorming Q&A:**

**Q1: “Single-call MVP” vs “universal/no-hardcoding” — what’s the correct constraint?**
- A) We can change/add generic contracts/metadata so UI is call-driven; validate primarily using Veni, but nothing is Veni-specific
- B) No contract changes allowed; we accept temporary hardcoding to ship faster
- C) Add Veni-only shortcuts now and refactor later
  > Recommendation: A — Validating on one call is fine, but the implementation must remain universal and call-driven.
  > **Selected: A**

**Q2: What counts as “hardcoding” that is forbidden in WF-0041?**
- A) Only backend hardcoding is forbidden; frontend can have call-specific maps temporarily
- B) Any per-call branching/maps/constants in frontend or backend (e.g., `VENI_NODE_ORDER`, `DOMAIN_OPTIONS_BY_CALL`) are forbidden
- C) It’s OK to hardcode display labels/order as long as the review engine is universal
  > Recommendation: B — This is the only option that matches “no hardcoding anywhere.”
  > **Selected: B**

**Q3: How should the UI learn whether domain selection applies (and what the options are)?**
- A) Backend exposes domain options in call metadata/config; frontend shows selector only when present
- B) Frontend infers domain options by parsing node constraints (e.g., keys in `word_limit_by_domain`)
- C) Always show a domain selector for every call
  > Recommendation: A — Keeps frontend universal and ensures “domain applies only when the call defines it.”
  > **Selected: A**

**Q4: What’s the constraint on review runs/history given “single-pass MVP UX”?**
- A) Keep current persistence: each submit creates a Review record and it appears in `/app/reviews`; idempotency prevents accidental duplicates
- B) Don’t persist reviews for MVP; only show immediate results
- C) Persist only the latest review per call (overwrite)
  > Recommendation: A — Preserves current product behavior and avoids breaking review history.
  > **Selected: A**

**Q5: What’s the constraint on ordering/grouping in review detail once we remove hardcoding?**
- A) Ordering must be call-driven (DB node `order_index`); if unavailable in current review detail payload, we extend contracts to enable it
- B) Ordering doesn’t matter for MVP; any stable order is fine
- C) Use alphabetical ordering by section title as a universal fallback
  > Recommendation: A — Otherwise we’ll reintroduce implicit per-call behavior via arbitrary ordering.
  > **Selected: A**

**Q2: What “job-to-be-done” should the UI optimize for in this MVP?**
- A) “I need to validate compliance fast before I submit”
- B) “I need criteria/elements-grounded feedback to revise”
- C) “I need both equally; neither can be weak”
  > Recommendation: B — This is the core product promise; compliance is necessary but supportive.
  > **Selected: B**

**Q3: What’s the expected usage pattern for the MVP?**
- A) Single pass: paste once, get feedback, done
- B) Iterative loop: paste → fix → resubmit multiple times
- C) Collaborative: multiple people contribute text to different nodes
  > Recommendation: B — Most real users iterate.
  > **Selected: A**
  > Constraint note: although UX is “single pass” for MVP, each run should still persist as a Review and appear in `/app/reviews` (current behavior); iteration UX can be a follow-up.

**Q4: What’s the MVP stance on authentication friction?**
- A) Sign-in required before submit/review (current pattern)
- B) Allow one anonymous run then require sign-in
- C) Fully anonymous MVP
  > Recommendation: A — Keeps abuse/rate-limit controls and current flow intact.
  > **Selected: A**

**Q5: What’s the minimum “trust posture” we should communicate to the user?**
- A) “This is structured feedback aligned to evaluation criteria/elements; still use judgement”
- B) “This is a compliance checker; review feedback is secondary”
- C) “This is an AI reviewer; treat it as authoritative”
  > Recommendation: A — Honest positioning supports trust without overclaiming.
  > **Selected: A**
  > Constraint note: although Veni currently has 3 nodes, the UI must support an arbitrary number of call-defined nodes without per-call hardcoding.

**Q2: What’s the minimum acceptable “call-aware” evidence in the review detail UI?**
- A) Each card shows proposal section title + evaluation element name (and stable IDs available via an “info” affordance)
- B) Cards show section title only; evaluation element name can be omitted
- C) Cards show evaluation element only; section grouping can be omitted
  > Recommendation: A — Visible element names are the trust signal; IDs can be present but should not be required to interpret feedback.
  > **Selected: A**
  > User note: verify whether backend already provides these fields; if missing, improve the existing contract to reach this bar.

**Q3: What’s the minimum acceptable compliance behavior for MVP (honest + enforceable)?**
- A) Enforce mandatory presence + min/max word limits (domain-aware), block on errors, warnings shown but don’t block
- B) Enforce only mandatory presence; word limits are informational
- C) No blocking; only informational messages
  > Recommendation: A — Blocking on enforceable constraints is required for “usable” and prevents false trust.
  > **Selected: A**

**Q4: What’s the MVP stance on domain (ENW/Science pilot) correctness?**
- A) Optional domain selector; if unset, we apply default limits and clearly show the active limit in the Research Idea UI + compliance output
- B) Require explicit domain choice before enabling submit
- C) Remove domain from UI; always treat as default
  > Recommendation: A — Minimal friction while still supporting real call behavior.
  > **Selected: A**
  > Scope note: treat domain behavior as call-specific; do not assume it applies to ERC/MSCA unless their call definition introduces it.

**Q5: What must be true to say “no hardcoding anywhere” is satisfied for this MVP?**
- A) No hardcoded per-call node labels/order/domain options in frontend; everything comes from call metadata/config
- B) Frontend can have call-specific constants as long as backend is universal
- C) It’s enough that the backend is universal; frontend hardcoding is acceptable temporarily
  > Recommendation: A — This prevents “Veni-shaped MVP” and keeps the product aligned to universal call support.
  > **Selected: A**
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
