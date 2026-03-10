<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0070-erc-structured-review-step-gating.md -->
# WF-0070 — ERC Structured Review: Enforce Step 1 vs Step 2 Evaluation Gating

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-09

---

## Preflight Step 1 — Long-Form Problem Intake

- User narrative:
  - Fix the mission-level trust gap where ERC can still evaluate the wrong proposal surfaces for the wrong official stage.
  - Add explicit ERC stage selection/routing for Step 1 vs Step 2.
  - Enforce fail-closed validation when submitted nodes do not match the chosen stage.
  - Ensure execution is stage-scoped, not just UI-scoped.
  - Preserve the call-agnostic core unless a narrowly justified extension seam is required.
  - Keep this as one coherent WF, not a frontend-only slice.
  - Do not widen scope into prompt tuning, assisted extraction, new agencies, or supporting-context semantics.

## Preflight Step 2 — Repo Reality Snapshot

- Read-only findings:
  - Canonical ERC YAML stores evaluation-element stage metadata, but node-level review stage is still derived from mixed element stages.
  - Current derived metadata marks `b2_part2_scientific_proposal` as effectively Step 1-eligible (`BOTH`) even though the official process treats B2 as Step 2-only.
  - Frontend visibility/filtering trusts that derived node metadata.
  - Backend node/stage mismatch checks run before execution, but only at node granularity.
  - Runtime execution does not stage-activate expectations before pipeline evaluation.
  - BFF invalid-stage handling silently coerces to `STEP_1`.

## Preflight Step 3 — Open Questions to Resolve in Brainstorm

- Where stage truth should be authored and enforced so node visibility and expectation execution cannot drift.
- Whether the shared execution core can absorb stage activation cleanly without widening unrelated call behavior.
- Whether compliance and review-detail surfaces need explicit stage-scoped evidence in the same WF.

## Section 1 — Problem Statement

**Q1: What exact problem should WF-0070 treat as the primary defect?**
- A) ERC Step 1/Step 2 stage truth is broken across UI, API, and runtime, causing wrong-surface/wrong-element evaluation.
- B) The main problem is only UI clarity around which fields belong to each stage.
- C) The main problem is a broader multi-call stage framework gap that should be solved generically now.
> Recommendation: A — This matches the repo reality and the mission-level trust risk. B is too narrow because the backend/runtime can still evaluate the wrong ERC surface. C widens scope before the ERC defect is closed and would violate the parking-lot boundary.
> **Selected: A**

**Q2: What must count as the authoritative stage boundary for this WF?**
- A) Proposal surfaces allowed per stage and expectations evaluated per stage must both be enforced.
- B) Only proposal-node submission eligibility must be enforced; expectation-level gating can wait.
- C) Only expectation activation must be enforced; surface visibility/routing can stay as-is.
> Recommendation: A — The trust gap is only closed if both the visible/submittable surfaces and the executed evaluation scope agree. B leaves runtime leakage. C leaves UX/request trust ambiguous.
> **Selected: A**

**Q3: When submitted ERC nodes do not match the chosen stage, what is the fail-closed behavior?**
- A) Reject the request before execution with explicit offending node ids and no silent dropping.
- B) Silently discard out-of-stage nodes and continue on the rest.
- C) Allow submission but downgrade to warnings.
> Recommendation: A — Silent dropping or warnings would make the reviewed evidence set unverifiable and would weaken traceability. Explicit rejection keeps the contract defensible.
> **Selected: A**

**Q4: What proof bar should this WF satisfy before we consider the trust gap closed?**
- A) Submit UX, BFF, backend structured-review execution, and review evidence must all agree on stage scope.
- B) UX plus backend request validation is enough even if review output does not expose the executed stage scope.
- C) Backend runtime correctness is enough even if the submit UX stays potentially misleading.
> Recommendation: A — Mission trust depends on aligned end-to-end truth, not isolated correctness. B and C leave researchers unable to verify what was actually evaluated.
> **Selected: A**

**Q5: If the current call-agnostic core cannot cleanly express ERC stage surfaces, what extension policy should we adopt?**
- A) Allow one narrow ERC stage-surface seam at the config/activation boundary while keeping evaluator/pipeline core call-agnostic.
- B) Force a universal multi-call stage redesign now, even if it broadens scope.
- C) Add ERC-specific conditionals wherever needed across the stack.
> Recommendation: A — This preserves the call-agnostic core while allowing a bounded seam if the existing contract is too weak. B is premature universalization. C creates trust and maintenance drift across layers.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: What is the minimum user-visible outcome that proves this WF succeeded?**
- A) A researcher choosing ERC Step 1 cannot submit or review Step 2-only surfaces, and the system clearly shows that boundary.
- B) A researcher sees a clearer stage selector, even if some backend edge cases remain.
- C) Only backend correctness matters; the submit experience can stay mostly opaque.
> Recommendation: A — This matches the mission trust requirement. B is only a UX improvement. C leaves the researcher unable to trust the boundary.
> **Selected: A**

**Q2: What is the minimum runtime outcome that proves this WF succeeded?**
- A) Structured review execution must be stage-scoped so Step 1 cannot evaluate Step 2-only ERC expectations or surfaces.
- B) Request validation may block some bad payloads, but runtime can still trust submitted nodes after that.
- C) Only metadata derivation needs to change; runtime execution can remain unchanged.
> Recommendation: A — The defect is runtime trust, not only request hygiene. B and C would leave the core mission failure partially open.
> **Selected: A**

**Q3: What traceability outcome is required in review results or persisted review state?**
- A) The resulting review must make the selected stage and evaluated surface set explicit enough to verify what was in scope.
- B) Persisting `review_stage` alone is enough, even if reviewed surface coverage is not explicit.
- C) No additional evidence is needed if tests prove backend behavior.
> Recommendation: A — Researcher trust requires inspectable evidence, not hidden correctness. B and C are insufficient for mission-level defensibility.
> **Selected: A**

**Q4: What is “good enough” for this WF’s launch-bar evidence?**
- A) Targeted tests plus one representative ERC end-to-end proof across submit, validation, execution, and review detail.
- B) Unit tests only.
- C) Frontend integration tests only.
> Recommendation: A — This is the smallest evidence set that proves end-to-end truth without widening into a full wedge E2E program. B and C are too narrow.
> **Selected: A**

**Q5: If we discover adjacent gaps in compliance or single-node review behavior while doing this WF, how should we treat them?**
- A) Fix only what is necessary to preserve ERC stage truth on the structured-review path; park the rest.
- B) Expand the WF to close every stage-related gap across all review paths now.
- C) Ignore them even if they would undermine the structured ERC trust claim.
> Recommendation: A — This keeps the WF coherent and bounded. B widens scope prematurely. C would risk a false trust-closure claim.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary actor for this WF?**
- A) Researchers using the ERC structured-review submission path.
- B) Internal developers trying to standardize stage semantics across all calls.
- C) Review-detail readers only, after a review already exists.
> Recommendation: A — The mission is researcher trust before submission. B is secondary. C is downstream of the primary failure.
> **Selected: A**

**Q2: What is the main actor harm today?**
- A) They can be shown or allowed to submit wrong-stage ERC surfaces and cannot fully trust the resulting review scope.
- B) They mostly suffer from visual clutter in the form.
- C) They mainly suffer from slow reviews.
> Recommendation: A — This is the concrete trust break observed in code. B and C are different problems.
> **Selected: A**

**Q3: What audience should shape the wording and evidence standard?**
- A) Researchers making revision decisions based on evaluation-criteria-grounded feedback.
- B) Engineers maintaining the pipeline.
- C) Future multi-agency product planning.
> Recommendation: A — The evidence standard should be optimized for the researcher-facing trust promise. B and C are important but secondary.
> **Selected: A**

**Q4: How broad should the actor scope be for this WF?**
- A) ERC structured-review actor only, with maintainers as secondary consumers of the contract.
- B) All staged-call actors across the product.
- C) All review actors including legacy single-node mode.
> Recommendation: A — This keeps scope honest and aligned to the parked item. B and C broaden the WF without evidence.
> **Selected: A**

**Q5: What internal actor need must still be preserved?**
- A) Maintainers need one traceable stage contract across metadata, validation, execution, and review evidence.
- B) Maintainers need maximum short-term patch speed, even if stage logic is duplicated.
- C) Maintainers mainly need a UI-only workaround until later.
> Recommendation: A — Duplicated stage logic is the drift risk to avoid. B and C would increase future trust regressions.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction?**
- A) Define one authoritative stage-scope contract that drives metadata, validation, runtime activation, and review evidence consistently.
- B) Patch the UI selector and backend route separately without a shared contract.
- C) Rewrite the evaluator into a stage-specialized engine for ERC.
> Recommendation: A — This is the smallest coherent path to trust closure. B risks more drift. C over-specializes the core.
> **Selected: A**

**Q2: Where should the narrow extension seam live if needed?**
- A) At config/activation boundary where authored call truth becomes runtime-active scope.
- B) Inside evaluator/pipeline internals.
- C) In ad hoc BFF/UI conditionals.
> Recommendation: A — Boundary activation is the cleanest place to localize ERC-specific truth without corrupting the core evaluator.
> **Selected: A**

**Q3: How should invalid BFF stage input behave?**
- A) Fail closed and surface an explicit validation error.
- B) Continue coercing invalid input to `STEP_1`.
- C) Silently omit the field and let backend default.
> Recommendation: A — Boundary coercion is incompatible with the selected trust standard. B and C hide defects.
> **Selected: A**

**Q4: How should runtime treat stage scope?**
- A) As an activated execution boundary, not merely a prompt hint or UI filter.
- B) As a prompt hint while keeping the same expectation set.
- C) As a reporting label only.
> Recommendation: A — The user explicitly required stage-scoped execution. B and C do not close the defect.
> **Selected: A**

**Q5: How should review evidence be handled?**
- A) Explicitly expose enough stage-scoped coverage to verify what surfaces were evaluated.
- B) Keep evidence implicit to avoid touching review detail.
- C) Skip evidence changes and rely on backend logs/tests.
> Recommendation: A — Trust requires inspectable user-facing or persisted evidence. B and C leave the closure unverifiable.
> **Selected: A**

## Section 5 — Constraints

**Q1: What is the most important architectural constraint?**
- A) Preserve the call-agnostic evaluator/pipeline core unless a narrow seam is unavoidable.
- B) Generalize all staged-call behavior now.
- C) Optimize for the fewest touched files regardless of design quality.
> Recommendation: A — This follows the WF target and existing architecture constraints. B widens scope. C is not a sound design rule.
> **Selected: A**

**Q2: What scope constraint should dominate planning?**
- A) Keep the WF coherent around ERC structured-review trust closure only.
- B) Absorb adjacent trust work while we are already in the area.
- C) Use this as the start of a broader stage-framework initiative.
> Recommendation: A — Coherence matters more than opportunistic expansion. B and C risk rework and diluted closure.
> **Selected: A**

**Q3: What product constraint is mandatory?**
- A) A stage picker without backend/runtime enforcement is unacceptable.
- B) A stage picker is sufficient if UX is clear enough.
- C) Runtime-only change is sufficient even if UI stays confusing.
> Recommendation: A — This is explicitly stated by the user and the parking-lot dependency note.
> **Selected: A**

**Q4: How should ambiguity be handled?**
- A) Fail closed and surface ambiguity as a contract defect to resolve.
- B) Default permissively to Step 1 behavior.
- C) Leave behavior undocumented if current tests pass.
> Recommendation: A — This is the trust bar chosen in Section 1. B and C would institutionalize drift.
> **Selected: A**

**Q5: How should code-vs-doc disagreement be treated?**
- A) Call it out explicitly and plan to resolve it in the WF artifacts/tests.
- B) Prefer docs silently.
- C) Prefer code silently.
> Recommendation: A — Silent preference hides split-brain risk. The disagreement itself is evidence for the WF.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the most fragile assumption right now?**
- A) The existing mixed node/element stage model can cleanly express ERC’s official Step 1 vs Step 2 surfaces.
- B) The frontend can hide all trust issues by filtering fields.
- C) Review detail can stay unchanged without harming trust.
> Recommendation: A — This is the exact architectural pressure point exposed by the repo snapshot. B and C are already contradicted by the mission goal.
> **Selected: A**

**Q2: What must be validated earliest?**
- A) That runtime expectation activation and surface-stage truth can align without broad evaluator specialization.
- B) That the selector copy is understandable.
- C) That this can be generalized to all future agencies.
> Recommendation: A — If this fails, the WF architecture is wrong. B and C are secondary.
> **Selected: A**

**Q3: What regression risk is most likely?**
- A) Existing tests and review-detail assumptions currently built around ERC B2=`BOTH` may break and need contract correction.
- B) Styling regressions in the submit form.
- C) Prompt wording regressions.
> Recommendation: A — This is the real drift risk already visible in current tests.
> **Selected: A**

**Q4: What evidence risk matters most?**
- A) Fixing prevention without exposing stage-scoped review evidence would leave the trust claim unverifiable.
- B) Over-documenting the solution in artifacts.
- C) Spending too much time on test naming.
> Recommendation: A — The mission requires trust and traceability, not hidden correctness.
> **Selected: A**

**Q5: What should trigger a stop condition in later phases?**
- A) Discovering that fail-closed stage truth cannot be represented cleanly without unresolved contract ambiguity or broad core specialization.
- B) Any test failure anywhere in the repo.
- C) Any need to edit more than one layer.
> Recommendation: A — This isolates the meaningful architectural blocker. B and C are too blunt.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: If limited to a small launch-blocking slice, what must exist?**
- A) Explicit ERC stage selection/routing, fail-closed node mismatch rejection, stage-scoped runtime execution, and review evidence proving scope.
- B) Only a corrected stage selector.
- C) Only backend validation plus tests.
> Recommendation: A — This is the smallest honest trust-closure slice.
> **Selected: A**

**Q2: What must be explicitly excluded from the MVP?**
- A) Prompt tuning, extraction, new agencies, supporting-context semantics, and broad multi-call redesign.
- B) Review evidence changes.
- C) Backend runtime changes.
> Recommendation: A — The excluded items are adjacent but not required for the trust claim. B and C would remove required scope.
> **Selected: A**

**Q3: What is the minimum architectural allowance if the current contract is insufficient?**
- A) One narrow ERC-specific seam at config/activation boundary.
- B) ERC-specific branches throughout evaluator and route layers.
- C) Immediate universal redesign.
> Recommendation: A — This is the bounded exception already approved in Section 1.
> **Selected: A**

**Q4: What verification standard must the MVP meet?**
- A) Tests and one representative ERC proof covering submit, validation, execution, and review evidence.
- B) Unit tests only.
- C) Manual spot check only.
> Recommendation: A — This balances rigor and scope.
> **Selected: A**

**Q5: What would make the MVP not good enough even if some tests pass?**
- A) If Step 1 can still expose/evaluate Step 2-only ERC surfaces or the result cannot prove scope.
- B) If the UI copy is imperfect.
- C) If the implementation touches several layers.
> Recommendation: A — This is the actual mission-level bar. B and C are secondary concerns.
> **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: What tempting adjacent feature must be postponed?**
- A) Prompt-quality or reviewer-policy tuning unrelated to stage truth.
- B) Fail-closed validation.
- C) Review evidence clarity.
> Recommendation: A — Tuning is adjacent but not part of this closure slice. B and C are core.
> **Selected: A**

**Q2: What future initiative belongs to another WF?**
- A) General staged-review abstraction beyond what ERC trust closure strictly requires.
- B) BFF invalid-stage handling.
- C) Runtime expectation activation.
> Recommendation: A — Universalization is future work unless Phase 1 proves it unavoidable.
> **Selected: A**

**Q3: What user-facing area should stay out of scope here?**
- A) Assisted extraction and file parsing.
- B) ERC submit/review stage truth.
- C) Review detail evidence for scope.
> Recommendation: A — Extraction is explicitly out of scope. B and C are central to this WF.
> **Selected: A**

**Q4: What semantic area should stay parked unless directly required?**
- A) Supporting-context semantics and hierarchical reviewability expansion.
- B) Fail-closed mismatch behavior.
- C) Stage-scoped execution.
> Recommendation: A — Those semantics are separate work and explicitly excluded by the user.
> **Selected: A**

**Q5: What implementation anti-goal should be explicit?**
- A) Do not solve the problem by scattering ERC-specific conditionals across the stack.
- B) Do not add tests.
- C) Do not update artifacts if code changes.
> Recommendation: A — This preserves the architecture boundary and prevents hidden coupling.
> **Selected: A**
