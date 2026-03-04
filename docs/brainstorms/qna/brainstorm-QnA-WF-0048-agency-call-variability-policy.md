# WF-0048 — Agency/Call Variability Policy Contract

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

---

## Section 1 — Problem Statement (Q&A)

**Q1: What is the primary “who is harmed” actor for this problem?**
- A) Frontend/BFF developers integrating review submission. (Recommended)
- B) Backend engineers maintaining the engine.
- C) Both equally.
> Recommendation: A — This WF’s stated goal is to stop UI/BFF guessing API shapes by enforcing strict contracts at boundaries. Backend benefits too, but choosing A keeps the MVP scoped to the integration contract and avoids expanding into broader refactors.
> Why not B: Backend-only framing risks “internal cleanup” without guaranteeing external contract clarity.
> Why not C: “Both” is true but dilutes prioritization and can bloat scope.
> **Selected: A**

**Q2: Where is the single canonical contract boundary we enforce first?**
- A) `validate_review_request_payload()` strict-parse of `call_config_snapshot`. (Recommended)
- B) Earlier: call-definition ingestion/activation pipeline.
- C) Later: inside pipeline stages.
> Recommendation: A — It is the smallest tracer-bullet that immediately stops drift and makes failures deterministic, without requiring changes across ingestion, DB, or UI.
> Why not B: Stronger long-term, but larger scope and higher coupling; risks breaking existing flows before we have tests.
> Why not C: Too late; variability would already have leaked and behavior could differ by stage.
> **Selected: A**

**Q3: What is the core invariant we’re protecting?**
- A) Engine is call-agnostic; variability only via declared snapshot surfaces. (Recommended)
- B) Engine can branch but only in one place.
- C) Engine remains flexible; accept unknown fields for forward-compat.
> Recommendation: A — This matches the hard requirement: no call identity branching, and variability is expressed only through declared config/activation surfaces.
> Why not B: Still violates the “no call identity branching” requirement (even if centralized).
> Why not C: Conflicts with “reject unknown fields” and reintroduces guessing and drift.
> **Selected: A**

**Q4: What is the failure mode we want on contract violations?**
- A) Deterministic contract-failure with stable code + field-path details; reject unknown fields. (Recommended)
- B) Best-effort ignore unknowns, log warning.
- C) Generic 500 execution failure.
> Recommendation: A — Deterministic failures are necessary to keep the pipeline call-agnostic while still allowing per-call variability; errors must be actionable and compatible with WF-0045 semantics.
> Why not B: Silent ignore means consumers will keep guessing; misconfigurations become latent bugs.
> Why not C: 500s conflate contract issues with runtime failures; breaks debuggability and compatibility expectations.
> **Selected: A**

**Q5: What is the minimum “activated snapshot” content that must be modeled in v1 (even if optional at first)?**
- A) `expectations[]` + explicit extension points for stage gating, evaluation criteria/elements, compliance rules, reviewer-policy, prompt knobs. (Recommended)
- B) Only `expectations[]`.
- C) Full call-definition.
> Recommendation: A — Modeling explicit extension points is how we stay call-agnostic without adding identity branching; it also prevents ad-hoc fields from becoming de-facto APIs.
> Why not B: Recreates today’s drift risk; pushes variability into undefined/unvalidated fields.
> Why not C: Too large for an “activated snapshot”; increases coupling to ingestion and storage details.
> **Selected: A**
