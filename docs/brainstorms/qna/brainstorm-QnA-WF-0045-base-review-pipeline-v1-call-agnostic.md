# WF-0045 — Base Review Pipeline v1.0 (call-agnostic core)

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-03

---

## Preflight Step 1 — Long-Form Problem Intake

**Q1: How do you want to provide your narrative problem intake?**
- A) Full narrative (recommended): one long free-form write-up covering pain, actors, examples, constraints, and non-goals.
- B) Structured bullets: provide a template and fill each section briefly.
- C) Hybrid: short narrative first, then targeted gap probes.
> Recommendation: A — gives highest-fidelity Phase 0 signal with fewer interpretation gaps.
> **Selected: A**

User accepted the assistant-provided narrative draft as-is (`Approve as-is`).

## Preflight Step 2 — Repo Reality Snapshot (Read-Only)

Read-only grounding was performed against WF-0038 artifacts and current engine/tests to calibrate existing universal pipeline seams and avoid duplicate architecture invention.

---

## Section 1 — Problem Statement

**Q1: What is the primary artifact we are trying to define in this WF?**
- A) A pipeline contract/spec over existing engine behavior.
- B) A full new engine rewrite with new internals.
- C) A UI-facing process description only.
> Recommendation: A — maximizes leverage from WF-0038 baseline and avoids unnecessary rewrite risk.
> **Selected: A**

**Q2: What is the core failure mode this WF must eliminate first?**
- A) Inconsistent outputs across calls.
- B) Scope creep from optional analyses entering core.
- C) Slow runtime performance.
> Recommendation: B — directly enforces lean universality and prevents contract contamination.
> **Selected: B**

**Q3: What should be the strict boundary for optional competitive analysis?**
- A) Allowed in core as a low-priority stage.
- B) Separate module but same pipeline run.
- C) Explicitly out-of-core and deferred from v1.0 core.
> Recommendation: C — keeps the base pipeline minimal and avoids semantic drift.
> **Selected: C** (user note: park it if not already)

**Q4: For v1.0, what should “call-agnostic” strictly mean?**
- A) Same core stages + contracts for all calls; variability only from call config.
- B) Same codebase but call-specific exceptions allowed.
- C) Separate mini-pipelines per agency with shared helpers.
> Recommendation: A — strongest universality posture and lowest long-term maintenance burden.
> **Selected: A** (user note: park this question for later deeper handling of agency/call-specific requirements)

**Q5: What is the minimal required output contract from the base core pipeline?**
- A) Only internal diagnostics; no compatibility output.
- B) Deterministic diagnostics + current compatibility mapping contract.
- C) Human summary only.
> Recommendation: B — preserves downstream stability while the core contract is tightened.
> **Selected: B**

---

## Section 2 — Desired Outcome

**Q1: What is the primary measurable success indicator for this WF?**
- A) Core-stage contract completeness + deterministic acceptance tests pass.
- B) Faster runtime latency.
- C) More output verbosity.
> Recommendation: A — aligns directly to this WF’s universality contract objective.
> **Selected: A**

**Q2: What outcome best defines “good enough” for Phase 1 PRD readiness?**
- A) High-level ideas only.
- B) Frozen in-core stage boundaries + explicit non-goals/deferred list.
- C) Full implementation-level module plan.
> Recommendation: B — enables crisp downstream planning without premature over-design.
> **Selected: B**

**Q3: What behavior change do we want in future WFs using this pipeline?**
- A) Each WF can redefine core stages.
- B) Core stages stay stable; extensions plug in without modifying core contracts.
- C) Keep informal interpretation per workflow.
> Recommendation: B — preserves universality and lowers long-term maintenance entropy.
> **Selected: B**

**Q4: How should we evaluate “universality without bloat” in acceptance terms?**
- A) No new core stage unless required across multiple calls + justified in contract notes.
- B) Add stages freely, prune later.
- C) Permit call-specific core variants.
> Recommendation: A — imposes explicit discipline against scope inflation.
> **Selected: A**

**Q5: What is the required output packaging at this phase?**
- A) Brainstorm only.
- B) Brainstorm with clear PRD-ready acceptance/guardrail statements per stage.
- C) Immediate tasks list.
> Recommendation: B — keeps Phase 0 focused while preparing Phase 1 execution quality.
> **Selected: B**

---

## Section 3 — Target User / Actor

**Q1: Who is the primary actor for this WF’s deliverable?**
- A) Internal product/engineering workflow owners.
- B) End researchers directly.
- C) External auditors/regulators.
> Recommendation: A — this WF is primarily a contract-clarity and governance artifact.
> **Selected: A**

**Q2: Who is the secondary actor we must not break?**
- A) Research users consuming ReviewCard-compatible outputs.
- B) Only backend developers.
- C) Marketing/content stakeholders.
> Recommendation: A — protects external experience while internal contracts evolve.
> **Selected: A**

**Q3: For agency/call-specific requirements, who should own expression of variability?**
- A) Engine code branches.
- B) Call configuration artifacts + activation rules.
- C) Manual per-call overrides in each WF.
> Recommendation: B — preserves call-agnostic engine semantics and maintainability.
> **Selected: B**

**Q4: What actor pain should this WF reduce first?**
- A) Ambiguity for implementation teams about what belongs in core vs optional.
- B) UI styling inconsistency.
- C) Data ingestion speed only.
> Recommendation: A — ambiguity at contract level is the highest rework multiplier.
> **Selected: A**

**Q5: For this phase, what audience should the artifacts optimize for?**
- A) Immediate coding convenience.
- B) Cross-phase decision clarity (brainstorm → PRD → tasks).
- C) External presentation polish.
> Recommendation: B — maximizes workflow leverage and reduces downstream contradictions.
> **Selected: B**

---

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction for this WF?**
- A) Contract-first: define the 6-stage core pipeline spec + invariants over existing modules.
- B) Refactor code first, document later.
- C) New parallel engine prototype.
> Recommendation: A — highest leverage, lowest regression risk, preserves existing tested baseline.
> **Selected: A**

**Q2: How should we model the six stages against the current two-pass engine reality?**
- A) Replace two-pass with six-pass execution.
- B) Keep two-pass internals; define six logical governance stages that map onto/around existing passes.
- C) Ignore current engine and define abstract stages only.
> Recommendation: B — avoids unnecessary churn while still freezing core stage contracts.
> **Selected: B**

**Q3: Where should cross-node alignment and risk audit live in v1.0 design?**
- A) In optional extension layer.
- B) As mandatory core stage contracts with deterministic output conditions.
- C) As free-form narrative guidance only.
> Recommendation: B — these are central to review trust and must not be optional in base core.
> **Selected: B**

**Q4: What should “output aggregation” include at v1.0 minimum?**
- A) Deterministic finding ordering + compatibility mapping surface.
- B) Only human-readable summary text.
- C) Scoring/ranking bundle.
> Recommendation: A — preserves downstream interoperability while remaining lean.
> **Selected: A**

**Q5: How should we enforce “optional competitive analysis out of core” technically in planning?**
- A) Explicit non-goal + deferred module boundary + no core contract dependency.
- B) Mentioned informally in prose only.
- C) Keep as low-priority core hook.
> Recommendation: A — gives enforceable scope discipline and prevents accidental coupling.
> **Selected: A**

---

## Section 5 — Constraints

**Q1: What is the top technical constraint for this WF?**
- A) Preserve existing deterministic contracts and compatibility behavior while defining core-stage governance.
- B) Introduce new data model tables first.
- C) Replace existing engine interfaces.
> Recommendation: A — keeps risk low and leverages existing proven contracts.
> **Selected: A** (with user caveat: “and B if needed to avoid complexity”)

**Q2: What is the time/scope constraint for Phase 0/1?**
- A) Broad redesign across all related WFs.
- B) Tight scope: contract/governance clarity only, no broad execution refactor.
- C) Skip constraints; decide later.
> Recommendation: B — enforces lean progress and avoids design sprawl.
> **Selected: B**

**Q3: What dependency constraint must be explicit?**
- A) This WF can ignore existing WF-0038/0040 contracts.
- B) Must align with existing pipeline-v1 SSOT and not break current stage/compatibility assumptions.
- C) Depend on future unknown architecture changes.
> Recommendation: B — prevents regressions and duplicate architecture tracks.
> **Selected: B**

**Q4: What constraint do we impose on agency/call-specific logic?**
- A) No engine branching; variability only via call config activation/expectation data.
- B) Allow small hardcoded agency exceptions in core.
- C) Defer all agency handling without any rule.
> Recommendation: A — required to preserve call-agnostic core integrity.
> **Selected: A**

**Q5: What output-quality constraint should be explicit now?**
- A) Each core stage must have entry/exit invariant statements and testability hooks in PRD language.
- B) Keep stage descriptions conceptual only.
- C) Focus only on prose readability.
> Recommendation: A — makes Phase 1 executable and reviewable.
> **Selected: A**

---

## Section 6 — Risks / Unknowns

**Q1: What is the highest-risk ambiguity if left unresolved?**
- A) “Call-agnostic” interpreted loosely, allowing hidden call-specific core behavior.
- B) Naming style differences only.
- C) Minor documentation drift.
> Recommendation: A — this directly threatens universality and causes architectural backsliding.
> **Selected: A**

**Q2: What must be validated earliest to prevent rework?**
- A) Whether the 6-stage governance model maps cleanly to current two-pass internals without forced rewrites.
- B) UI copy tone.
- C) Future scoring strategy.
> Recommendation: A — this is the structural hinge for a lean Phase 1.
> **Selected: A**

**Q3: What is the biggest scope-creep risk in this WF?**
- A) Expanding into performance optimization.
- B) Pulling optional competitive analysis into core contracts.
- C) Adding more examples in docs.
> Recommendation: B — it dilutes base-contract purpose and increases coupling.
> **Selected: B**

**Q4: What downstream risk should we guard against explicitly?**
- A) Breaking compatibility outputs while tightening core stages.
- B) Having too few open questions.
- C) Not using enough diagrams.
> Recommendation: A — compatibility regressions would negate the value of core-contract cleanup.
> **Selected: A**

**Q5: Which unknown should remain explicitly deferred (not resolved now)?**
- A) Agency/call-specific requirement handling detail policy beyond current constraint boundary.
- B) Whether core should include competitive analysis.
- C) Whether to keep deterministic behavior.
> Recommendation: A — consistent with user request to park this for later focused decision-making.
> **Selected: A**

---

## Section 7 — MVP Definition

**Q1: If limited to 2–3 days equivalent planning depth, what must exist?**
- A) Frozen core-stage contract (6 stages), in-core/out-of-core boundary, and PRD-ready invariants.
- B) Full task decomposition.
- C) Prototype refactor.
> Recommendation: A — strongest signal-to-noise for Phase 1 quality.
> **Selected: A**

**Q2: What can explicitly wait until later WF/phases?**
- A) All agency/call-specific detailed policy design beyond current constraints.
- B) Deterministic invariant definitions.
- C) Compatibility guarantees.
> Recommendation: A — preserves lean scope while maintaining current safety boundaries.
> **Selected: A** (user note: park/defer this item)

**Q3: What must NOT be included in this MVP definition?**
- A) Optional competitive analysis in core.
- B) Performance tuning and scoring design.
- C) Both A and B.
> Recommendation: C — both are scope creep vectors for this Phase 0/1 objective.
> **Selected: C**

**Q4: What is the minimum acceptance shape for Phase 1 handoff?**
- A) Stage-by-stage entry/exit criteria + traceability to existing contracts/tests.
- B) Narrative only.
- C) Open-ended principles.
> Recommendation: A — ensures PRD can be audited and executed without ambiguity.
> **Selected: A**

**Q5: How strict should we be about changes to existing engine internals in this MVP definition?**
- A) Default no-internal-change unless required to satisfy frozen core invariants.
- B) Encourage broad internals cleanup now.
- C) Leave unconstrained.
> Recommendation: A — minimizes regression surface while defining governance clearly.
> **Selected: A**

---

## Section 8 — Explicit Non-Goals

**Q1: Which non-goal is most important to state explicitly?**
- A) No optional competitive analysis in core pipeline v1.0.
- B) No docs updates.
- C) No tests later.
> Recommendation: A — this is the primary anti-bloat boundary for this WF.
> **Selected: A**

**Q2: Which additional non-goal protects against architecture bloat?**
- A) No new core stages beyond the locked six in this WF.
- B) No use of existing engine modules.
- C) No PRD in next phase.
> Recommendation: A — prevents uncontrolled expansion of the core contract.
> **Selected: A**

**Q3: Which implementation non-goal should be explicit for Phase 0/1?**
- A) No broad refactor of pipeline internals.
- B) No schema/model expansion unless complexity-reducing and contract-required.
- C) Both A and B.
> Recommendation: C — this provides the strongest anti-bloat guardrail.
> **Selected: C**

**Q4: Which decision should remain out of scope now (deferred)?**
- A) Detailed agency/call-specific handling policy beyond current constraints.
- B) Whether deterministic behavior matters.
- C) Whether compatibility mapping should exist.
> Recommendation: A — aligns with earlier deferred decision and keeps Phase 0/1 focused.
> **Selected: A**

**Q5: What should we explicitly postpone to future WF(s)?**
- A) Performance optimization/scoring/competitive-analysis module design.
- B) Stage invariants.
- C) Core boundary definition.
> Recommendation: A — these are valid follow-ons but not base-contract essentials now.
> **Selected: A**
