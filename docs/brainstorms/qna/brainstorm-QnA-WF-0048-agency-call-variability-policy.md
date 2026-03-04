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

---

## Section 3 — Target User / Actor (Q&A)

**Q1: Primary contract consumer we optimize for (first-class docs/tests)?**
- A) Frontend BFF route handlers. (Recommended)
- B) Backend service layer (`structured_reviewer_service`) only.
- C) Both equally.
> Recommendation: A — This is where “guessing API shapes” manifests most directly; optimizing docs/tests for BFF consumers ensures the contract prevents inference and drift at the integration boundary.
> Why not B: Backend-only optimization can still leave BFF guessing and coding around ambiguity.
> Why not C: “Both” can be true, but prioritizing A reduces scope creep and sharpens examples.
> **Selected: A**

**Q2: What is the “API shape guessing” we most want to eliminate first?**
- A) Snapshot/request payload shape guessing. (Recommended)
- B) Review results shape guessing (cards/findings/telemetry).
- C) Both simultaneously.
> Recommendation: A — The snapshot boundary is the variability injection point; strictness here prevents downstream shape drift and allows result-contract cleanup to be a follow-up.
> Why not B: It does not stop variability leakage at the source.
> Why not C: Bundling both increases scope and may exceed the 3-file tracer-bullet slice.
> **Selected: A**

**Q3: Who owns building the activated snapshot (producer responsibility)?**
- A) Backend service layer assembles it from call-definition + stage + submitted nodes; engine only consumes strict snapshot. (Recommended)
- B) Frontend/BFF assembles it and sends to backend.
- C) Engine assembles it internally from DB.
> Recommendation: A — Keeps BFF simple and call-agnostic; keeps engine call-agnostic by consuming only a declared snapshot; avoids coupling core execution to persistence/DB.
> Why not B: Encourages guesswork and per-call branching in BFF.
> Why not C: Increases engine coupling to storage and makes determinism/migration harder.
> **Selected: A**

**Q4: What is the allowed “call variability input” for the producer?**
- A) Call-definition config + stage_ref + submitted nodes only. (Recommended)
- B) Also allow agency/call_code hints to influence behavior.
- C) Allow arbitrary per-call runtime switches.
> Recommendation: A — This enforces call-agnostic core execution while still allowing variability via declared config; identity hints are effectively branching inputs.
> Why not B: Violates the “no call identity branching” requirement in practice.
> Why not C: Makes the system non-auditable and non-deterministic.
> **Selected: A**

**Q5: What is the minimum documentation target in Phase 1 (after brainstorm)?**
- A) A single strict schema doc for `ActivatedCallConfigSnapshotV1` with examples + rejection cases. (Recommended)
- B) A full integration guide for all endpoints.
- C) Only code-level docstrings.
> Recommendation: A — Highest leverage for stopping guessing: one authoritative schema with acceptance/rejection examples.
> Why not B: Too broad for the tracer-bullet.
> Why not C: Too implicit; encourages inference rather than explicit contract.
> **Selected: A**

---

## Section 4 — Rough Idea Exploration (Q&A)

**Q1: What is the core “tracer-bullet” implementation direction?**
- A) Introduce strict `ActivatedCallConfigSnapshotV1` model + validate it at the request boundary; engine consumes only typed snapshot. (Recommended)
- B) Add more ad-hoc validators around existing dict usage.
- C) Push strictness into pipeline stages (late).
> Recommendation: A — It establishes the contract boundary cleanly and prevents drift with minimal surface area.
> Why not B: Validators without a typed model remain incomplete and grow brittle over time.
> Why not C: Too late; variability already leaks and behavior can diverge by stage.
> **Selected: A**

**Q2: How do we represent “allowed variability” without identity branching?**
- A) Explicit, named config/activation surfaces in the snapshot (stage gating, hierarchy/nesting, evaluation criteria/elements, compliance rules, reviewer-policy, prompt knobs). (Recommended)
- B) Generic `extensions: dict` bag.
- C) Per-call code paths.
> Recommendation: A — Makes variability auditable, testable, and contract-driven.
> Why not B: Becomes a shadow API.
> Why not C: Violates the hard requirement.
> **Selected: A**

**Q3: What is the digest contract?**
- A) Digest computed from canonical JSON serialization of the validated snapshot only; mismatch is deterministic contract failure. (Recommended)
- B) Digest includes non-contract metadata (timestamps, etc.).
- C) No digest; accept any snapshot.
> Recommendation: A — Aligns with deterministic semantics and replayability; keeps the digest meaningful.
> Why not B: Breaks determinism and makes replay hard.
> Why not C: Loses tamper/consistency check.
> **Selected: A**

**Q4: How strict is “strict” for unknown fields?**
- A) Reject unknown fields everywhere in the snapshot (strict-by-default). (Recommended)
- B) Reject only at top-level, allow nested unknowns.
- C) Allow unknowns but ignore.
> Recommendation: A — Eliminates drift and guessing; forces explicit evolution.
> Why not B: Nested unknowns become the common loophole.
> Why not C: Reintroduces implicit contracts.
> **Selected: A**

**Q5: How do we prove “no call-identity branching required”?**
- A) Tests that build snapshots without any call identity fields and still cover variability via declared surfaces. (Recommended)
- B) Allow call_code but promise not to use it.
- C) Rely on code review only.
> Recommendation: A — Makes the constraint enforceable in an automated way.
> Why not B: Non-enforceable promise; becomes a latent dependency.
> Why not C: Too weak; regressions are likely.
> **Selected: A**

---

## Section 5 — Constraints (Q&A)

**Q1: What is the hard “no branching” constraint?**
- A) No `if agency == ...` / call-code branching in core execution; variability only via config/activation surfaces. (Recommended)
- B) Branching allowed if centralized.
- C) Branching allowed if feature-flagged.
> Recommendation: A — It is a stated hard requirement and the primary design driver.
> Why not B/C: Still identity-driven behavior; undermines call-agnostic core.
> **Selected: A**

**Q2: What is the contract strictness requirement at boundaries?**
- A) Pydantic strict models; reject unknown fields. (Recommended)
- B) Allow unknowns for forward-compat.
- C) Only validate minimally, rely on downstream defaults.
> Recommendation: A — Necessary to stop guessing and drift.
> Why not B/C: Reintroduce ambiguity.
> **Selected: A**

**Q3: What is the implementation-scope guardrail?**
- A) Keep changes within 3 files per task slice; split if needed. (Recommended)
- B) Allow broad refactor in one go.
- C) Delay strictness until later.
> Recommendation: A — Keeps risk low and progress incremental.
> Why not B: High regression risk.
> Why not C: Leaves drift unaddressed.
> **Selected: A**

**Q4: What is the behavior-change workflow?**
- A) TDD (RED/GREEN) for behavior changes with deterministic contract tests. (Recommended)
- B) Implement first, add tests later.
- C) Manual testing only.
> Recommendation: A — Contract enforcement must be proven and regression-resistant.
> Why not B/C: Too risky for boundary changes.
> **Selected: A**

**Q5: What is the canonical terminology constraint?**
- A) Use “evaluation criteria/elements” in researcher-facing text/contracts. (Recommended)
- B) Use “rubric” where convenient.
- C) Mix terms, clarify later.
> Recommendation: A — Consistency prevents misunderstandings and drift in docs/UI.
> Why not B/C: Creates split-brain terminology.
> **Selected: A**

---

## Section 6 — Risks / Unknowns (Q&A)

**Q1: What is the most fragile assumption?**
- A) We can tighten the snapshot contract without breaking current producers beyond a manageable migration. (Recommended)
- B) We can keep accepting unknowns safely.
- C) Determinism is optional.
> Recommendation: A — This is the key migration risk; we mitigate via incremental enforcement + tests.
> Why not B/C: Conflicts with strictness and determinism requirements.
> **Selected: A**

**Q2: What must be validated early?**
- A) Unknown-field rejection + deterministic error semantics at the boundary. (Recommended)
- B) Full ingestion pipeline refactor.
- C) UI refactor.
> Recommendation: A — It is the tracer-bullet that unlocks downstream work.
> **Selected: A**

**Q3: What could cause major rework?**
- A) Ambiguous contract versioning/error taxonomy causing downstream incompatibility. (Recommended)
- B) Lack of any tests.
- C) Over-optimizing for one call.
> Recommendation: A — If versioning/error semantics aren’t pinned, we will churn across layers.
> **Selected: A**

**Q4: Determinism risk source?**
- A) Hidden nondeterminism (ordering, IDs, telemetry) leaking into serialized outputs. (Recommended)
- B) Python hash randomization only.
- C) Network timing.
> Recommendation: A — Determinism failures usually come from ordering/IDs and optional fields.
> **Selected: A**

**Q5: What is the best mitigation posture?**
- A) Deterministic contract tests that lock acceptance/rejection and serialization behavior. (Recommended)
- B) Rely on manual review.
- C) Add logging only.
> Recommendation: A — Makes the contract enforceable and prevents regressions.
> **Selected: A**

---

## Section 7 — MVP Definition (Q&A)

**Q1: If limited to 2–3 days, what must exist?**
- A) Strict activated snapshot model + boundary validation + deterministic contract tests. (Recommended)
- B) Full UI/BFF integration overhaul.
- C) Full ingestion hardening.
> Recommendation: A — Minimal tracer-bullet that enforces the variability policy contract.
> **Selected: A**

**Q2: What can explicitly wait?**
- A) Broader API DTO reshaping + UI refactors; ingestion hardening follow-ups. (Recommended)
- B) Contract tests.
- C) Deterministic error semantics.
> Recommendation: A — Tests and error semantics are core to the contract.
> **Selected: A**

**Q3: What must NOT be included?**
- A) Any call identity branching in core or “extensions dict” escape hatches. (Recommended)
- B) Adding more per-call special cases.
- C) Competitive analysis in core.
> Recommendation: A — These directly undermine the goal.
> **Selected: A**

**Q4: What is the minimal compatibility target?**
- A) Compatible contract-failure semantics with WF-0045 (stable codes/details). (Recommended)
- B) Allow breaking changes and fix later.
- C) No defined semantics.
> Recommendation: A — Prevents downstream churn.
> **Selected: A**

**Q5: What is the acceptance test posture?**
- A) Deterministic tests: unknown fields rejected; no identity needed; identical payload → identical output. (Recommended)
- B) Only unit tests for validators.
- C) Manual ad-hoc checks.
> Recommendation: A — Locks the contract end-to-end.
> **Selected: A**

---

## Section 8 — Explicit Non-Goals (Q&A)

**Q1: What tempting feature must be postponed?**
- A) Competitive analysis inside core pipeline; any such work remains out-of-core. (Recommended)
- B) Allowing unknown fields for convenience.
- C) Per-call branching “just for now”.
> Recommendation: A — Keeps scope tight and preserves the call-agnostic invariant.
> **Selected: A**

**Q2: What belongs to a future WF?**
- A) Broader API DTO harmonization + frontend/BFF refactors once snapshot is strict. (Recommended)
- B) Strict snapshot contract itself.
- C) Deterministic tests.
> Recommendation: A — Snapshot strictness is the foundation; broader work follows.
> **Selected: A**

**Q3: What is explicitly out-of-scope for v1?**
- A) Ingestion pipeline hardening and DB schema changes. (Recommended)
- B) Contract boundary enforcement.
- C) Error taxonomy.
> Recommendation: A — Keeps the tracer-bullet within the 3-file slice.
> **Selected: A**

**Q4: What is explicitly prohibited?**
- A) Any call identity branching in core execution. (Recommended)
- B) Using evaluation criteria/elements terminology.
- C) Rejecting unknown fields.
> Recommendation: A — It is a hard requirement.
> **Selected: A**

**Q5: What is our stance on “escape hatches”?**
- A) None in v1; explicit versioned evolution only. (Recommended)
- B) Add `extensions: dict`.
- C) Allow unknown nested fields.
> Recommendation: A — Prevents drift and guessing.
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
