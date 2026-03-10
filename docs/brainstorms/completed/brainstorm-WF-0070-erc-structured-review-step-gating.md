<!-- docs/brainstorms/brainstorm-WF-0070-erc-structured-review-step-gating.md -->
# WF-0070 — ERC Structured Review: Enforce Step 1 vs Step 2 Evaluation Gating

Artifact: brainstorm
Version: v0.4
Status: Draft Complete
Last Updated: 2026-03-09

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts/decisions for WF-0070.
- The Q&A transcript is rationale only; it must not introduce new contracts.
- If Phase 1 or later resolves a deferred stage-scope contract, verification bar, or proceed gate, promote that decision back into this brainstorm instead of leaving truth only in downstream artifacts.

## Preflight Step 1 — Long-Form Problem Intake

- User-selected WF target: close the mission-level trust gap where ERC can still evaluate the wrong proposal surfaces for the wrong official stage.
- Required outcome: explicit ERC stage selection/routing for Step 1 vs Step 2, fail-closed validation when submitted nodes do not match the chosen stage, and stage-scoped runtime execution.
- Required scope shape: one coherent WF spanning UX, API, and backend runtime. A frontend-only stage picker is explicitly unacceptable.
- Required architectural constraint: preserve the call-agnostic core unless a narrowly justified extension seam is necessary.
- Explicit non-goals from kickoff: no prompt-tuning WF, no assisted extraction, no new agencies, no supporting-context semantic expansion.

## Repo Reality Snapshot (Read-Only)

- The ERC canonical YAML encodes evaluation-element stage metadata, but the key B2 leaf `b2_part2_scientific_proposal` mixes `BOTH` and `STEP_2` elements, so derived node stage resolves to `BOTH` rather than a fail-closed Step 2-only surface.
- Frontend stage visibility is driven by node metadata (`review_stage`) via `isNodeEligibleForStage()`, so the current ERC metadata model would keep `b2_part2_scientific_proposal` visible in Step 1 even though official ERC process says B2 is Step 2 only.
- Backend `POST /api/structured-review` rejects explicit node/stage mismatches, but only at node granularity via `matches_review_stage()`; it does not activate expectations by stage before pipeline execution.
- Structured runtime execution builds request expectations directly from repository expectations on submitted nodes and never calls `activate_expectations_for_stage()`, so a submitted ERC B2 node can still evaluate Step 2-only elements during a Step 1 run.
- The BFF route normalizes invalid `review_stage` values to `STEP_1` instead of failing closed, which weakens trust and traceability at the boundary even before backend validation.
- Review-detail coverage already flows through persisted `structured_payload` fields such as `review_stage` and `submitted_leaf_ids`, and backend detail responses already expose explicit boundary buckets; Phase 1 should extend these existing seams rather than invent a disconnected second provenance path unless current seams prove insufficient.
- Current review-detail boundary metadata is not stage-aware: backend `visible_not_reviewed_node_logical_ids` derives from all expectation-bearing call nodes, and the current page consumes those fields directly, so an ERC Step 1 review can still imply that Step 2-only surfaces were merely “not reviewed” instead of out of scope.

### Repo Snapshot Open Questions

- Should ERC stage truth live at the proposal-node level, the evaluation-element level, or both with an explicit reconciliation contract?
- Is the cleanest fail-closed fix a generic stage-activation seam in the shared execution core, or an ERC-specific surface-selection seam layered above it?
- Must compliance checking become stage-aware in the same WF so pre-submit warnings/errors cannot reference hidden or disallowed Step 2 surfaces during Step 1?
- How should review detail/reporting expose stage-scoped coverage so researchers can verify what was and was not evaluated?
- How should existing persisted coverage (`review_stage`, `submitted_leaf_ids`) and review-detail boundary buckets be extended so Step 1 detail cannot imply Step 2-only surfaces were in scope?
- What is the narrowest acceptable extension seam if current call-agnostic contracts cannot represent “surface visible only in Step 2 while some linked elements remain BOTH”?

## 1. Problem Statement

- Current ERC stage handling is partially modeled but not end-to-end truthful.
- The most acute trust failure is that Step 1 can still expose or evaluate Step 2 proposal surfaces.
- This violates mission expectations for official-call grounding and defensible traceability.
- Primary defect for this WF: ERC Step 1/Step 2 stage truth is broken across UI, API, and runtime, causing wrong-surface and wrong-element evaluation.
- Authoritative stage boundary for this WF must cover both proposal surfaces allowed per stage and evaluation expectations executed per stage.
- Fail-closed behavior is mandatory: mismatched submitted ERC nodes must be rejected before execution with explicit offending node ids and no silent dropping.
- Closure bar for the trust gap requires submit UX, BFF, backend structured-review execution, and review evidence to agree on stage scope.
- Review detail must not label Step 2-only ERC surfaces as merely “not reviewed” on a Step 1 review; out-of-scope and in-scope-but-not-reviewed must remain distinct.
- If the current call-agnostic core cannot cleanly express ERC stage surfaces, the allowed fallback is one narrow ERC seam at the config/activation boundary, not evaluator-wide ERC branching.

Contract Notes / Non-obvious constraints:

- Stage truth must hold at execution time, not only in UI visibility rules.
- Fail-closed behavior is preferred over permissive fallback when stage metadata is ambiguous.
- Official ERC process semantics matter more than preserving current mixed-stage node derivation.
- Keep evaluator and pipeline core call-agnostic unless a narrow config/activation seam is proven necessary.
- Boundary fixes must preserve structured-review idempotency and payload-hash semantics; invalid stage input must fail before any coercion can change request meaning.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md` (Section 1)

## 2. Desired Outcome

- A researcher choosing ERC Step 1 cannot submit or review Step 2-only proposal surfaces, and the product makes that boundary legible.
- Structured-review runtime becomes stage-scoped so Step 1 cannot evaluate Step 2-only ERC surfaces or Step 2-only expectations.
- Persisted review data and review detail expose enough stage-scoped coverage to verify what was in scope.
- “Good enough” evidence for this WF is an explicit pass/fail verification matrix with targeted automated tests plus one representative ERC end-to-end proof across submit, validation, execution, and review detail.
- If adjacent gaps appear, fix only what is required to preserve ERC stage truth on the structured-review path and park the rest.

Contract Notes / Non-obvious constraints:

- Persisting `review_stage` alone is insufficient if the evaluated surface set remains implicit.
- Closure evidence must prove boundary truth, not just internal correctness.
- This WF is allowed to touch adjacent seams only when they directly affect the ERC structured-review trust claim.
- No proceed/ship recommendation is valid unless every blocking verification item in the chosen pass/fail matrix is explicitly marked passing with concrete evidence.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md` (Section 2)

## 3. Target User / Actor

- Primary actor: researchers submitting ERC Starting Grant material through the structured-review path.
- Immediate trust consumer: a researcher deciding whether Step 1 feedback is grounded only in officially reviewable Step 1 surfaces.
- Secondary actor: internal maintainers who need a stage contract that stays traceable and defensible across UI, BFF, backend, and review detail.
- Current bad behavior for the actor: they can be shown or allowed to submit ERC B2 material during Step 1, and the resulting review cannot prove the executed stage boundary cleanly.
- MVP target is not “all staged calls”; it is the locked ERC structured-review path with minimal spillover into the shared core.

Contract Notes / Non-obvious constraints:

- Researcher-facing trust is the primary optimization target, not generic stage abstraction.
- This WF should not widen to legacy single-snippet UX unless the structured-review trust claim depends on it.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md` (Section 3)

## 4. Rough Idea (Unstructured Thinking)

- Establish one authoritative ERC stage-scope contract that can drive node metadata, request validation, runtime expectation activation, and review evidence consistently.
- Prefer fixing stage truth at the boundary where authored call config becomes runtime-active scope, rather than scattering ERC-specific conditionals across UI, BFF, route, service, and evaluator layers.
- Keep the evaluator/pipeline core call-agnostic; if ERC needs a special rule, place it in a narrow config/activation seam that produces a stage-scoped runtime snapshot before execution.
- Treat BFF invalid-stage coercion as a contract defect and fail closed at the boundary.
- Ensure review detail/persisted coverage can prove which ERC surfaces were actually in scope for the chosen stage.

Contract Notes / Non-obvious constraints:

- “Stage-scoped execution” means more than blocking a bad node id at the API route; the activated expectation set must also respect stage truth.
- The cleanest architecture is likely pre-execution activation plus explicit coverage evidence, not prompt-only stage hints.
- Phase 1 must choose one authoritative source of ERC stage truth for structured review; node metadata, request validation, runtime activation, and review evidence must all derive from that source rather than acting as peer-authoritative mappings.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md` (Section 4)

## 5. Constraints

- Must remain one coherent WF across UX, BFF, backend validation, runtime execution, and review evidence.
- Must preserve the call-agnostic evaluator/pipeline core unless a narrowly justified extension seam is necessary.
- Must not widen into prompt tuning, extraction flows, new agencies, supporting-context semantics, or generalized stage-framework redesign.
- Must fail closed on ambiguity; permissive fallback behavior is not acceptable for stage truth.
- Must use current repo state as truth and explicitly call out any doc/code disagreement.
- Must preserve structured-review boundary semantics already relied on elsewhere: `Idempotency-Key` behavior, payload-hash mismatch behavior, and validation-order guarantees must remain deterministic when invalid or mismatched `review_stage` is introduced.

Contract Notes / Non-obvious constraints:

- Existing tests and mocks already disagree about ERC B2 stage truth, so artifact updates must resolve that split-brain explicitly.
- A UI-only fix is invalid even if it appears to hide the immediate symptom.
- Stage mismatch and invalid-stage errors must preserve existing validation-order invariants; this WF must not reintroduce silent fallback or post-persistence failure behavior.
- Review-detail proof is part of the trust claim, so stage-aware boundary metadata cannot be treated as optional polish or deferred silently behind runtime fixes.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md` (Section 5)

## 6. Risks / Unknowns

- Highest-risk unknown: the current mixed ERC node/element stage model may be too weak to express official stage surfaces without a new authored seam.
- Architectural risk: stage truth could be “fixed” in metadata/UI while runtime expectation execution still leaks Step 2 evaluation.
- Regression risk: tightening ERC stage truth could break current tests or review detail assumptions that were built around `BOTH` metadata for B2.
- Evidence risk: even a correct runtime fix may still leave researchers unable to verify scope if review detail does not expose stage-scoped coverage explicitly.
- Scope risk: adjacent compliance or legacy-review issues may tempt expansion beyond the structured ERC trust closure target.

Contract Notes / Non-obvious constraints:

- Any change that relies on implicit knowledge of submitted nodes without explicit review evidence leaves the mission-level trust gap partially open.
- If fail-closed stage truth cannot be represented cleanly, Phase 1 must stop and resolve the contract before tasks are generated.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md` (Section 6)

## Open Questions / Deferred

- Whether compliance warnings/errors need explicit stage labeling in the user-facing response, beyond stage-correct node filtering. Deferred to Phase 1 if not required for trust closure.

## Authoritative Stage Truth (Must Resolve in Phase 1)

- Phase 1 chooses the authored proposal-surface stage-scope contract in canonical ERC call configuration as the one authoritative source of ERC stage truth for structured review.
- Any secondary representation, such as node metadata or execution snapshots, must be derived from that source and must not become a peer-authoritative mapping.
- The selected contract must resolve the current code-vs-doc disagreement around `b2_part2_scientific_proposal` explicitly rather than inheriting the current `BOTH` drift silently.

## Minimum Traceability Evidence (Must Resolve in Phase 1)

- Planning chooses an inspectable evidence surface by extending current persisted structured payload coverage with one derived review-time stage-scope snapshot field and projecting stage-aware review-detail boundaries from that persisted evidence.
- Persisted `review_stage` alone is not sufficient.
- The chosen evidence surface must let a researcher or reviewer verify what ERC surfaces were in scope for the completed review.
- Do not invent a disconnected provenance system if the existing persisted/review-detail seams can carry the proof honestly.
- Any proceed/phase-advance recommendation for this WF must include both:
  - an explicit pass/fail verification ledger covering every blocking proof item in the locked matrix,
  - a baseline-SHA or explicit commit-range-anchored scope proof plus an audit-disposition ledger closing every blocking finding and either closing or explicitly rejecting each justified non-blocking finding with rationale.

## Structured-Path Scope Boundary (Resolved in Phase 1)

- The structured ERC trust claim for this WF remains anchored to `POST /api/structured-review`, its stage-aware submit flow, its runtime activation seam, and its persisted/review-detail evidence path.
- `POST /api/reviews` remains deferred because it runs through a different service seam and does not participate in the structured payload/review-detail trust path that this WF is closing.
- Phase 2 must treat any required changes to `POST /api/reviews` as an explicit blocker or follow-on decision, not as silent implementation spillover.
- No readiness/proceed recommendation is valid if implementation work touches the single-node path without first proving that dependency is necessary to keep the structured ERC trust claim honest.

## 7. MVP Definition

- Smallest acceptable slice: ERC structured-review path enforces explicit Step 1 vs Step 2 selection/routing, rejects out-of-stage submitted nodes fail-closed, stage-scopes runtime execution, and exposes review evidence proving scope.
- Required technical closure: no silent stage coercion at BFF, no Step 1 evaluation of Step 2-only ERC surfaces, and no runtime reliance on UI-only filtering.
- Required artifact closure: tests and docs align on the authoritative ERC stage truth for affected nodes/surfaces.
- Minimum proof matrix for planning/tests: Step 1 happy path, Step 1 with Step 2 node mismatch, Step 1 review-detail boundary proof that Step 2-only ERC surfaces are out of scope rather than “not reviewed”, Step 2 happy path, invalid-stage fail-closed proof at the BFF/backend boundary, idempotency/payload-hash parity proof for the tightened boundary, and explicit review-evidence verification for scope.
- Proceed/phase-advance proof must be fail-closed: every blocking proof item is marked pass/fail with explicit evidence, and closure records the scope proof plus final disposition of every justified finding.
- Explicitly excluded from MVP: prompt-quality improvements, extraction, new agencies, generalized supporting-context semantics, and broad multi-call stage redesign.
- If a narrow ERC-specific seam is required, it must stay localized to config/activation rather than spreading across the evaluator core.

Contract Notes / Non-obvious constraints:

- The MVP is a trust-closure slice, not a convenience slice.
- A successful demo must prove both prevention and evidence, not only prevention.

## Stop Conditions

- Stop planning if the chosen seam cannot keep evaluator/pipeline core call-agnostic.
- Stop planning if authoritative stage truth still requires duplicate ambiguous peer-authoritative mappings across node metadata and runtime activation.
- Stop planning if no inspectable evidence surface can prove executed ERC stage scope honestly.
- Stop planning if invalid-stage fail-closed behavior would require weakening current idempotency or payload-hash guarantees at the structured-review boundary.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md` (Section 7)

## 8. Explicit Non-Goals

- Do not tune prompts or broaden reviewer-policy semantics as part of this WF.
- Do not add new agencies or generalize staged-review support beyond what is necessary for the locked ERC path.
- Do not expand supporting-context behavior or revisit opted-in hierarchical submit semantics except where current structured ERC trust depends on them.
- Do not reopen assisted extraction, file parsing, or hierarchy-navigation work.
- Do not solve every stage-related issue in every review path unless Phase 1 proves the structured ERC trust closure cannot be made honestly without it.

Contract Notes / Non-obvious constraints:

- “Preserve call-agnostic core” is a hard non-goal on broad evaluator specialization.
- Any adjacent issue not necessary for ERC structured-review truth should be parked, not absorbed.
