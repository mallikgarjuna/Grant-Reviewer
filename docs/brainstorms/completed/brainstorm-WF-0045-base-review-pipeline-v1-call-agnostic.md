# WF-0045 — Base Review Pipeline v1.0 (call-agnostic core)

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-03

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md`

---

## Contract Safety (SSOT)

- This brainstorm is SSOT for contracts/decisions; the Q&A transcript is rationale only.
- Base pipeline v1.0 must preserve deterministic diagnostics and compatibility mapping semantics.
- Phase 1 must state persistence side-effect boundaries explicitly (no new core persistence coupling by default).
- Any deviation from existing compatibility semantics requires explicit rationale and acceptance criteria.

## 0. Preflight Intake (Narrative Locked)

Problem narrative approved by user (as-is):
- We need a call-agnostic base review pipeline v1.0 that is reusable across calls and avoids funder/program overfitting.
- The core pain is absence of a tightly bounded universal pipeline contract with explicit stage boundaries and deterministic IO.
- Required core stages: structural validation, compliance gate, expectation-level evaluation, cross-node alignment, risk audit, output aggregation.
- Optional competitive analysis must stay out of the v1.0 core pipeline path.
- Success means deterministic, traceable outputs grounded in evaluation criteria/elements, with explicit in-core vs out-of-core boundaries.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Preflight Step 1)

## Repo Reality Snapshot (Read-Only) (2026-03-03)

- A universal engine baseline already exists from WF-0038 (`backend/app/engine/`) with two-pass contracts and `DiagnosticFinding v1` compatibility mapping.
- Current pipeline v1 implementation emphasizes deterministic finding generation + mapping, but the requested 6-stage “base pipeline v1.0” contract is not yet captured as a single explicit product-level stage model.
- Call-config activation/order and expectation semantics are implemented; universality is partially encoded in code/tests, not yet framed as a minimal core-vs-optional governance artifact.
- Traceability and criteria/elements grounding already exist in contracts/docs; this WF should avoid re-inventing them and instead tighten stage boundaries and scope guardrails.
- Competitive/adjacent analysis concerns are discussed in docs, but not explicitly separated from core pipeline as a formal non-goal contract for this WF.

Open questions from snapshot:
- Should “base pipeline v1.0” be a governance/spec contract over existing engine modules, or include code-path restructuring in the same WF?
- Where exactly should cross-node alignment and risk-audit semantics live: evaluator stage internals vs explicit post-evaluation stage contracts?
- What is the minimum acceptable output aggregation contract for v1.0: findings-only, ReviewCard compatibility, or both?
- How strict should phase-1 scope be in forbidding optional extensions (competitive analysis, scoring variants, extra orchestration)?

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Preflight Step 2)

---

## 1. Problem Statement (Section 1)

### Decisions (selected)

- Primary artifact for this WF is a pipeline contract/spec over existing engine behavior (not a full rewrite).
- Core failure mode to eliminate first is scope creep from optional analyses entering the core path.
- Optional competitive analysis is explicitly out-of-core for v1.0 (kept deferred from the base pipeline).
- Call-agnostic baseline remains strict: same core stages/contracts for all calls; variability comes from call configuration.
- Minimal required output contract for base core includes deterministic diagnostics and current compatibility mapping.

Contract Notes / Non-obvious constraints:
- “Out-of-core” means optional analysis may exist later but cannot mutate base-stage contracts or core pass/fail semantics.
- Compatibility mapping stays in scope to protect downstream behavior while we tighten core boundaries.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 1)

---

## 2. Desired Outcome (Section 2)

### Decisions (selected)

- Primary success metric is core-stage contract completeness plus deterministic acceptance-test pass.
- Phase 1 readiness bar is frozen in-core stage boundaries with explicit non-goals/deferred list.
- Expected behavior change: extensions plug into stable core contracts without redefining core stages.
- Universality-without-bloat rule: no new core stage unless cross-call justified and contract-noted.
- Required packaging for this phase: brainstorm content that is PRD-ready with stage-level guardrails.

Contract Notes / Non-obvious constraints:
- “Deterministic acceptance” includes both stage ordering and invariant output/compatibility behavior.
- Any proposal to add a core stage must include explicit multi-call justification and deferred alternative analysis.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 2)

---

## 3. Target User / Actor (Section 3)

### Decisions (selected)

- Primary actor is internal product/engineering workflow owners defining and maintaining core boundaries.
- Secondary protected actor is researchers consuming compatibility-safe outputs.
- Agency/call-specific variability is owned by call configuration + activation rules, not engine branches.
- First pain to reduce is implementation ambiguity on core-vs-optional scope.
- Phase artifact audience priority is cross-phase clarity (brainstorm → PRD → tasks).

Contract Notes / Non-obvious constraints:
- “Primary actor internal” does not reduce end-user quality requirements; it raises the burden on deterministic compatibility guarantees.
- Variability ownership in call config implies core contracts must remain call-invariant and extension-safe.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 3)

---

## 4. Rough Idea (Unstructured Thinking) (Section 4)

### Decisions (selected)

- Implementation direction is contract-first over existing modules (no rewrite-first or parallel prototype).
- Existing two-pass internals remain; the six stages are a governance contract mapped onto/around current execution seams.
- Cross-node alignment and risk audit are mandatory core stage contracts.
- Output aggregation minimum includes deterministic finding ordering and compatibility mapping behavior.
- Competitive analysis exclusion is enforced as explicit non-goal + deferred module boundary with no core dependency.

Contract Notes / Non-obvious constraints:
- Six-stage governance does not imply six runtime passes; it defines required stage responsibilities and invariants.
- Mandatory alignment/risk stages must be objectively testable to avoid fallback into narrative-only interpretation.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 4)

---

## 5. Constraints (Section 5)

### Decisions (selected)

- Primary technical constraint is preserving existing deterministic/compatibility contracts while defining core-stage governance.
- Conditional allowance: limited model/data-shape changes are acceptable only if they reduce complexity (no broad data-model expansion).
- Time/scope constraint is tight Phase 0/1 contract clarity, not broad execution refactor.
- Dependency constraint: align to existing pipeline-v1 SSOT and compatibility assumptions.
- Agency/call-specific constraint: no engine branching; variability remains in call configuration activation/expectation data.
- Output-quality constraint: every core stage must have entry/exit invariants and PRD-level testability hooks.

Contract Notes / Non-obvious constraints:
- “Complexity reduction” is valid only when it lowers core coupling; it cannot expand core scope.
- Any schema/model adjustment must remain subordinate to the contract-first objective.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 5)

---

## 6. Risks / Unknowns (Section 6)

### Decisions (selected)

- Highest-risk ambiguity is loose interpretation of “call-agnostic” that permits hidden call-specific core behavior.
- Earliest validation needed: the six-stage governance model maps cleanly to existing two-pass internals without rewrite pressure.
- Biggest scope-creep risk is optional competitive analysis leaking into core contracts.
- Key downstream risk is breaking compatibility outputs while tightening core stages.
- Explicit deferred unknown remains agency/call-specific requirement handling policy detail beyond current boundary rules.

Contract Notes / Non-obvious constraints:
- “Hidden call-specific behavior” includes implicit defaults or exceptional paths not declared in call config.
- Compatibility safety is a first-class risk gate, not a post-hoc cleanup.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 6)

---

## 7. MVP Definition (Section 7)

### Decisions (selected)

- MVP planning must freeze the 6-stage core contract, in-core/out-of-core boundary, and PRD-ready invariants.
- Deferred to later phases/WFs: detailed agency/call-specific policy design beyond the current call-config constraint boundary.
- Must not include optional competitive analysis in core or performance/scoring expansion scope.
- Phase 1 handoff minimum is stage-by-stage entry/exit criteria with traceability to existing contracts/tests.
- Engine internals default to no-change unless required to satisfy frozen core invariants.

Contract Notes / Non-obvious constraints:
- Deferred policy detail is intentional, not omission; current constraints still prohibit core call-specific branching.
- “No-change default” protects determinism/compatibility and forces explicit justification for any refactor.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 7)

---

## 8. Explicit Non-Goals (Section 8)

### Decisions (selected)

- No optional competitive analysis in core pipeline v1.0.
- No new core stages beyond the locked six in this WF.
- No broad pipeline-internal refactor and no schema/model expansion unless complexity-reducing and contract-required.
- Detailed agency/call-specific handling policy remains out of current scope (deferred).
- Performance optimization, scoring strategy, and competitive-analysis module design are postponed to future WFs.

Contract Notes / Non-obvious constraints:
- Deferred policy design does not weaken existing “no engine branching” constraint.
- Non-goals are hard scope boundaries for Phase 1 and may be promoted only via new parked items/WFs.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0045-base-review-pipeline-v1-call-agnostic.md` (Section 8)

## Core Stage Contract Matrix (v1.0)

| Stage | Entry Invariant | Exit Invariant |
|---|---|---|
| Structural Validation | Request/config shape resolvable for target subject | Deterministic validity result and normalized subject scope |
| Compliance Gate | Structural validation complete | Deterministic compliance outcomes with explicit checks |
| Expectation-Level Evaluation | Active expectations resolved from call config | Per-expectation assessed/not-assessable outcomes |
| Cross-Node Alignment | Declared dependency context available/flagged missing | Deterministic alignment findings or explicit not-assessable reasons |
| Risk Audit | Expectation/alignment outputs available | Deterministic risk findings scoped to core taxonomy |
| Output Aggregation | All prior stage outputs finalized | Stable ordered diagnostics and compatibility-safe aggregation output |

## Phase 1 Handoff Guardrails

- No-behavior-change-first posture for existing deterministic compatibility surfaces.
- Define parity assertions for core outputs before/after any proposed contract tightening.
- Any internal refactor must be justified by a specific core-stage invariant, not general cleanup.
- Governance-only rule for Phase 1: no planned restructuring scope; restructuring is allowed only if a specific frozen invariant cannot be satisfied otherwise, and must be explicitly justified.

## Stage-to-Seam Mapping (Current Baseline, No New Seams by Default)

| Stage | Baseline seam (current runtime boundary) | Mapping rule |
|---|---|---|
| Structural Validation | Request validation + call-config activation boundary | Reuse existing validation/activation seams; no new core validator path by default |
| Compliance Gate | Deterministic compliance check boundary | Keep deterministic check posture; no call-specific branching hooks |
| Expectation-Level Evaluation | Pass-level expectation evaluation boundary | Stay on existing expectation-driven evaluation seam |
| Cross-Node Alignment | Dependency-context handling boundary | Use declared dependency context only; no implicit cross-node heuristics |
| Risk Audit | Finding classification/governance boundary | Risk signals must remain deterministic and call-agnostic |
| Output Aggregation | Finding ordering + compatibility mapping boundary | Preserve deterministic ordering and compatibility mapping semantics |

## Stage Failure Semantics (Locked for Phase 1)

- Each stage must classify failures as either:
  - `contract-failure` (input/config/identity/integrity violations), or
  - `execution-failure` (runtime processing failure despite valid contract input).
- Aggregation boundary must preserve deterministic failure propagation:
  - no silent drops,
  - no best-effort mutation of core semantics,
  - explicit pass-through of failure class to downstream compatibility surfaces.

## Open Questions / Deferred

- Deferred policy design: agency/call-specific requirement handling details beyond current call-config-only boundary.
- Deferred optional-module design: competitive analysis extension architecture (kept out of core pipeline v1.0).
- Phase 1 gating for deferred agency/call policy: Phase 1 may proceed only under existing constraints (`no engine branching` + `call-config activation/expectation variability`). Additional policy assumptions are prohibited until the deferred item is promoted and resolved.
