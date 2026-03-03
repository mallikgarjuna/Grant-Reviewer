# WF-0045 — Base Review Pipeline v1.0 (call-agnostic core) PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-03

## 0. User Stories (MVP)

- US1: As a workflow owner, I want a locked six-stage base pipeline contract with explicit entry/exit invariants, so that every call runs on one deterministic call-agnostic core.
- US2: As a reviewer-engine maintainer, I want deterministic failure semantics and stage-boundary rules, so that compatibility behavior stays stable and auditable.
- US3: As a product maintainer, I want a strict in-core vs out-of-core boundary, so that optional competitive analysis and other extensions do not change core semantics.
- US4: As a researcher consuming outputs, I want deterministic aggregated diagnostics with compatibility-safe mapping, so that outputs stay traceable to evaluation criteria/elements.

## Deferred Stories (Not in MVP)

- DS1: Competitive analysis extension architecture and execution path.
- DS2: Detailed agency/call-specific policy framework beyond existing call-config constraints.
- DS3: Performance/scoring strategy expansion and optimization.

## 1. In Scope

- Define and freeze six required core stages: structural validation, compliance gate, expectation-level evaluation, cross-node alignment, risk audit, output aggregation. (US1)
- Define stage-level entry/exit invariants and failure-class semantics (`contract-failure` vs `execution-failure`). (US1, US2)
- Preserve deterministic diagnostic ordering and compatibility mapping behavior as mandatory base output semantics. (US2, US4)
- Enforce call-agnostic governance: no engine branching by call/funder/program in core stage logic. (US1, US3)
- Freeze explicit non-goals and deferred list to prevent optional analysis from entering core path in v1.0. (US3)

## 2. Out of Scope

- Implementing competitive analysis in the core pipeline. (DS1)
- Redesigning scoring models, rankers, or performance-oriented execution architecture. (DS3)
- Broad internal refactor not required to satisfy locked stage invariants. (DS2)
- Introducing new core stages beyond the locked six-stage contract. (DS2)

## 3. User / System Flow

- Happy path:
1. System receives a review request with resolvable call configuration and subject scope; structural validation confirms contract-valid request shape. (US1, US2)
2. Compliance gate executes deterministic checks and emits explicit compliance outcomes. (US1, US2)
3. Expectation-level evaluation resolves active expectations from call config and produces assessed/not-assessable outcomes per expectation. (US1, US4)
4. Cross-node alignment evaluates declared dependency context and emits deterministic alignment findings or explicit not-assessable reasons. (US1, US4)
5. Risk audit derives deterministic risk findings from prior stage outputs using core taxonomy. (US2, US4)
6. Output aggregation emits stable ordered diagnostics and compatibility-safe aggregation output for downstream surfaces. (US2, US4)

- Failure path A (contract invalid at stage boundary):
1. A stage receives input that violates its required entry invariant. (US2)
2. Stage emits `contract-failure`; aggregation preserves failure class and returns deterministic failure semantics with no silent drop. (US2, US4)

- Failure path B (runtime execution failure):
1. A stage receives valid contract input but fails at runtime. (US2)
2. Stage emits `execution-failure`; aggregation preserves class and exposes deterministic failure outcome. (US2, US4)

- Failure path C (scope creep attempt):
1. A change proposal introduces optional competitive analysis into core-stage behavior. (US3)
2. Governance gate rejects proposal as out-of-core for v1.0 and keeps base contract unchanged. (US1, US3)

## 4. Functional Requirements

- FR1 (US1): The PRD must lock exactly six core stages for base pipeline v1.0.
- FR2 (US1, US2): Each stage must define explicit entry and exit invariants.
- FR3 (US2): Each stage must classify failures as either `contract-failure` or `execution-failure`.
- FR4 (US2, US4): Output aggregation must preserve deterministic propagation of failure class with no silent drops.
- FR5 (US1, US3): Core behavior must remain call-agnostic; variability must come from call configuration only.
- FR6 (US3): Optional competitive analysis must be explicitly out-of-core and must not mutate base-stage contracts.
- FR7 (US2, US4): Base output must preserve deterministic diagnostic ordering.
- FR8 (US2, US4): Base output must preserve compatibility mapping semantics for downstream compatibility surfaces.
- FR9 (US1, US2): Any proposed internal refactor must be justified by a specific locked stage invariant.
- FR10 (US1, US3): No additional core stage may be introduced unless explicitly justified as cross-call mandatory in a new workflow.

## 5. Data & API Contracts

- C1 (US1, FR1, FR2): Stage contract matrix is normative and includes six locked stages with required entry/exit invariants.
- C2 (US2, FR3): Failure classification contract permits only `contract-failure` or `execution-failure` at stage boundaries.
- C3 (US2, US4, FR4): Aggregation contract must pass failure class through deterministically and must not apply best-effort semantic mutation.
- C4 (US1, US3, FR5): Call-config contract remains the only variability surface for expectations/activation behavior in core.
- C5 (US3, FR6): Optional extension modules are out-of-core by default and cannot alter core pass/fail semantics.
- C6 (US2, US4, FR7, FR8): Compatibility output contract requires stable ordered diagnostics and compatibility-safe mapping behavior.
- C7 (US1, US2, FR9): Governance contract for refactor requests requires explicit invariant linkage and parity assertions.
- C8 (US1, US3, FR10): Core-stage growth policy is frozen for this WF; new stage proposals are deferred.

State transitions:
- `structural_validation_complete` -> `compliance_gate_complete` -> `expectation_evaluation_complete` -> `cross_node_alignment_complete` -> `risk_audit_complete` -> `aggregation_complete`.
- Any stage may transition to `failed_contract` or `failed_execution`; aggregation terminal state must preserve failure class.

Validation rules:
- Stage cannot run unless prior stage exit invariant is satisfied.
- Aggregation cannot emit success when upstream stage terminal state is `failed_contract` or `failed_execution`.
- Deterministic ordering is required for all emitted diagnostics.

## 6. Components / Modules

- `backend/app/engine/` (existing runtime seam)
  - Responsibility: host execution boundaries where six-stage governance maps onto current internals. (FR1, FR2, FR5)
- Stage governance contract artifact (this PRD -> Phase 2 task artifact)
  - Responsibility: define normative boundaries, failure semantics, and non-goals. (FR2, FR3, FR6, FR10)
- Compatibility mapping surface (existing compatibility adapter behavior)
  - Responsibility: preserve downstream-compatible output semantics while core contracts are tightened. (FR7, FR8)
- Call configuration surfaces (`backend/data/calls/...`)
  - Responsibility: provide call-specific variability inputs without core branching. (FR5)

Design tree (dependencies + ordering):
1. Freeze stage and failure contracts in PRD. (FR1-FR4)
2. Map contracts to existing engine seams and parity assertions. (FR5, FR7-FR9)
3. Lock non-goals/deferred boundaries for optional modules. (FR6, FR10)

Deep modules:
- Core stage governance should expose small stable boundaries with hidden implementation detail.
- Compatibility mapping remains an adapter seam, not a core semantics owner.

Suggested file paths (coarse):
- `docs/prds/prd-WF-0045-base-review-pipeline-v1-call-agnostic.md`
- `docs/tasks/task-WF-0045-base-review-pipeline-v1-call-agnostic.md`
- `backend/app/engine/` (only if Phase 3 implementation tasks require invariant-backed edits)

## 7. Edge Cases

- E1 (US1, US2): Missing dependency context at alignment stage must yield explicit not-assessable reasoning, not silent omission.
- E2 (US2, US4): Mixed upstream failures across stages must still result in deterministic failure-class propagation in aggregation.
- E3 (US3): Optional module flags present in request must not alter core-stage ordering or core pass/fail logic.
- E4 (US1, US3): Call config with unusual expectation topology must still run through the same six locked stages.
- E5 (US2): Runtime timeout at one stage with otherwise valid input must classify as `execution-failure` only.

## 8. Testing Decisions (TDD)

- Seam S1 (US1, US2; FR1-FR4): Stage-boundary contract tests.
  - Verify entry/exit invariants and failure classification behavior.
  - Boundary mocking only at external runtime dependencies; do not mock core contract checks.
- Seam S2 (US1, US3; FR5, FR6, FR10): Governance tests for call-agnostic behavior and out-of-core exclusion.
  - Verify no call-specific core branching and no optional-competitive-analysis injection into core path.
- Seam S3 (US2, US4; FR7, FR8): Deterministic compatibility-output parity tests.
  - Verify stable ordering and compatibility mapping semantics remain unchanged for representative payloads.
- Seam S4 (US2; FR9): Refactor-justification tests/documentation checks.
  - Verify any behavior-affecting change references a specific stage invariant and parity assertion.

## 9. Telemetry (Minimal)

- Emit stage transition and terminal state (`success`, `failed_contract`, `failed_execution`) with stable stage identifiers.
- Emit deterministic counters for failure class by stage.
- Avoid adding optional-module telemetry to core stage signals in v1.0.

## 10. Deferred / Not in MVP

- Competitive analysis extension architecture and execution contract.
- Detailed agency/call policy design beyond current call-config boundary constraints.
- Performance/scoring redesign and broader orchestration optimizations.

## 11. Open Questions (if any)

- None blocking for MVP PRD v0.1.
- Deferred item remains open: how to design optional competitive-analysis extension contract without altering core semantics.

## 12. Changelog

- v0.1 (2026-03-03): Initial PRD from brainstorm.
