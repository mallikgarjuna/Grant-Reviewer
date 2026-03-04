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

---

## Section 2 — Desired Outcome (Q&A)

**Q1: What is the primary measurable “success signal” for WF-0048?**
- A) Engine rejects unknown fields + malformed variability with deterministic contract failures. (Recommended)
- B) Frontend/BFF no longer needs per-call parsing/branching.
- C) Both A+B as hard gates.
> Recommendation: A — It is directly testable at the engine boundary and is the minimal tracer-bullet that unblocks call-agnostic integration; B becomes a downstream consequence once the contract exists.
> Why not B: It depends on frontend changes and broader API cleanup beyond this WF’s first slice.
> Why not C: Valuable as a roadmap goal, but bundling both as hard gates risks scope creep and delays the strict contract foundation.
> **Selected: A**

**Q2: What is the v1 “activated snapshot” contract stance on forward-compat?**
- A) Strict-by-default: reject unknown fields everywhere; version bump for any new field. (Recommended)
- B) Allow `extensions` free-form dict for forward-compat.
- C) Allow unknown fields only under one reserved namespace.
> Recommendation: A — Unknown-field rejection is the core mechanism that stops drift and guessing; contract evolution should be explicit and versioned rather than opportunistic.
> Why not B: A free-form `extensions` bag becomes an unofficial API surface and reintroduces silent variability.
> Why not C: Better than B, but still risks “shadow contracts” unless heavily governed; v1 should start maximally strict.
> **Selected: A**

**Q3: Where do we pin determinism for “same payload ⇒ same serialized result”?**
- A) `PipelineResult.to_dict()` JSON stable ordering + stable IDs derived only from payload. (Recommended)
- B) Only guarantee same review_cards content, ignore telemetry.
- C) Determinism only for contract-failure cases.
> Recommendation: A — This is the cleanest contract: the serialized result is deterministic, full stop, so downstream systems (BFF, caching, audit) can rely on it.
> Why not B: It leaves ambiguity (telemetry is often used for debugging/audit) and creates “mostly deterministic” behavior that still breaks caching semantics.
> Why not C: Too weak; determinism is most valuable on success paths.
> **Selected: A**

**Q4: What is the boundary I/O contract we harden in v1?**
- A) `ReviewRequestV1` boundary only (call_config_snapshot + proposal_nodes + digest). (Recommended)
- B) Also harden BFF-facing API DTOs in the same WF slice.
- C) Harden call-definition ingestion outputs first.
> Recommendation: A — Smallest tracer-bullet with immediate value; keeps file-touch count low and avoids coupling this WF to UI/ingestion refactors.
> Why not B: Likely >3-file change and mixes responsibilities; better as a follow-up once snapshot is strict.
> Why not C: Larger, riskier scope; ingestion hardening is important but not the fastest route to stopping boundary drift.
> **Selected: A**

**Q5: What’s “good enough” for Phase 0 completion?**
- A) Clear contract surfaces + error semantics + testable invariants; implementation details deferred. (Recommended)
- B) Full draft PRD-level API schemas for all endpoints.
- C) Full implementation plan down to file-by-file changes.
> Recommendation: A — Phase 0 should converge on a tight, testable MVP contract without prematurely designing full architecture or broad endpoint refactors.
> Why not B: Too broad and not required to lock the engine boundary contract.
> Why not C: Premature specificity; we should validate the contract and error semantics first.
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
