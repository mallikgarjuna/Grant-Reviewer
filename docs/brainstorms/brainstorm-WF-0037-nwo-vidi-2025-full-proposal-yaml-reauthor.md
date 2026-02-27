# WF-0037 — Re-author NWO Vidi 2025 full proposal YAML (official sources)

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-02-27

---

## Preflight Step 1: Narrative Intake (Interactive)

Current intent:

- Primary goal (now): prove the universal call YAML authoring pipeline works for a second real NWO call (eventually also supports researcher-facing use).
- Stage: full proposal (not pre-proposal), single-stage evaluation (per user; must confirm against official docs).
- Scope boundary: encode evaluable proposal structure (nodes), evaluation criteria/elements, and enforceable content constraints only; include reviewer-relevant guidance only when it directly supports evaluation and is grounded in the official sources.

**Brainstorming Q&A:**

**Q1: What is the primary “pain” WF-0037 is fixing?**
- A) Our call YAML for NWO Vidi full proposal doesn’t exist (or is outdated), so we can’t ingest/evaluate it reliably.
- B) The YAML exists but doesn’t follow updated authoring conventions (sources manifest, reviewer_policy), risking drift and poor traceability.
- C) The YAML is fine; the real issue is frontend or API behavior.
> Recommendation: A — This is the cleanest, falsifiable deliverable and keeps scope in call-definition maintenance rather than product changes.
> **Selected: A**

**Q2: Who is the primary “customer” of this WF output?**
- A) Researchers/applicants using the app to get evaluation-criteria-grounded feedback.
- B) Internal us, to prove the universal YAML authoring pipeline works across calls.
- C) Reviewers/committee members (model reviewer instructions heavily).
> Recommendation: B — Optimizes for creating a second robust, source-grounded call definition under the universal conventions; researcher UX benefits later.
> **Selected: B (then eventually A)**

**Q3: What “stage model” should the YAML encode for Vidi?**
- A) Single stage only, unless the official docs clearly define multiple steps.
- B) Always encode STEP_1 + STEP_2 for future-proofing.
- C) No stages; treat stage as app-level only.
> Recommendation: A — Don’t invent stages. Encode what the funder defines, and keep runtime honest.
> **Selected: A (single-stage full proposal; must confirm in sources)**

**Q4: What is your strict scope boundary for what goes into the call YAML?**
- A) Only: proposal structure (nodes), evaluation criteria/elements, and enforceable content constraints.
- B) Include lots of help text/guidelines even if not enforceable.
- C) Encode everything in the docs (process/eligibility/deadlines/budget rules).
> Recommendation: A — Matches repo scope rules and keeps YAML legally/operationally defensible.
> **Selected: A (plus reviewer-relevant, source-grounded guidance that directly supports evaluation)**

**Q5: Definition of “done” for WF-0037 Phase 0 output?**
- A) Source-gated: official docs uploaded, clear plan for YAML + reviewer_policy, and a verification plan (dry-run ingest + DB/API preflight).
- B) A complete YAML fully authored and merged.
- C) A brainstorm only, no verification plan.
> Recommendation: A — Prevents authoring from memory and sets up a deterministic verification loop.
> **Selected: A**

## Preflight Step 2: Repo Reality Snapshot (Read-Only) (2026-02-27)

- No existing NWO Vidi call YAML is present in `backend/data/calls/nwo/`; only Veni preproposal exists (canonical + legacy archive).
- The repo has an explicit authoring SSOT: `docs/workflow/call-yaml-authoring-workflow.md` with gated steps (source confirmation, nodes, criteria/elements, mapping, guidance/compliance, then generation).
- Source traceability manifests live in `backend/data/calls/sources/` and are already used for ERC StG 2026 and NWO Veni 2025 preproposal; we should follow the same pattern for Vidi.
- V2 schema supports `reviewer_policy` with deterministic enforcement modes (`PROMPT_ONLY`, `POST_CHECK`, `BLOCKING`) and validates `forbidden_terms` when enforcement is post-check/blocking.
- Universal form work (WF-0035) has an explicit acceptance gate: “Veni + 1 additional official flat-supported structured call” (Vidi selected as the candidate), so we should preserve flat-only feasibility when authoring Vidi nodes.

Key open questions this snapshot suggests:

- What is the exact canonical call code + filename that matches `{agency}_{program}_{year}_{stage}.yaml` without leaking brittle numbering?
- What are the official sources for: (1) proposal structure (application form/template) and (2) evaluation criteria/procedure (reviewer guidance / criteria chapter)?
- Are there domain/pilot variants that introduce per-domain word limits or node differences (like Veni `science_enw`)?
- Does Vidi explicitly prohibit bibliometrics/venue-prestige language (needs `reviewer_policy` parity), and where is it stated?
- Are there hard word limits / item limits per section that are actually enforceable with current compliance engine capabilities?
