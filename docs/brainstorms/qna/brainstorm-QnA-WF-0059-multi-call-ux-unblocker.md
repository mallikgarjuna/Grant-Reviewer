<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md -->
# WF-0059 — Multi-call UX Unblocker

Artifact: brainstorm-qna
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-06

Type: feature

## Preflight Checklist

### Step 1 — Long-Form Problem Intake

- PeerLens is currently usable only along a Veni-shaped happy path, and that is now the main product bottleneck.
- Hierarchical or nested calls can exist in the system, but the real user flow still breaks when the call contains nested sections because review submission does not complete for that structure.
- Review detail must become trustworthy for non-Veni calls by sourcing labels, grouping, ordering, and traceability from call metadata rather than call-specific assumptions.
- Success requires one real ERC-like hierarchical call to submit and review end-to-end; if the result still only works for Veni-shaped calls, the workflow failed.
- The workflow must stay focused on the unblocker, preserve current Veni behavior, and avoid broad speculative platform redesign.

### Step 2 — Repo Reality Snapshot (Read-Only) (2026-03-06)

- `frontend/src/lib/submit/renderModel.ts` explicitly rejects nested nodes with `reason: "nested_nodes"`.
- `frontend/src/components/submit/UniversalSubmitForm.tsx` surfaces that unsupported state and blocks the structured submit path.
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` already uses `call_id` and fetched call nodes to drive ordering/labels when metadata is available.
- `backend/app/schemas/api.py` already exposes `call_id`, `call_code`, `ordering_source`, and tree-capable node response models.
- Hierarchy support exists in backend services/contracts, so the clearest product bottleneck is end-user nested submit usability plus proof on a real non-Veni path.

## Brainstorming Q&A

### Section 1 — Problem Statement

**Q1: What is the primary product defect WF-0059 is actually solving?**
- A) Generic "multi-call support" across the whole platform.
- B) The platform cannot complete one real non-Veni hierarchical applicant happy path because nested-call submit is blocked.
- C) Review detail labels/order are cosmetically inconsistent across calls.
  > Recommendation: B — This is the concrete product failure. A is too broad for MVP, and C matters only insofar as it prevents a trustworthy end-to-end proof.
  > **Selected: B**

**Q2: What should count as the core success proof for this WF?**
- A) One concrete ERC-like hierarchical call can be selected, completed, submitted, and reviewed end-to-end with call-aware review detail.
- B) Nested calls no longer show an unsupported message in submit UI.
- C) Review detail works for arbitrary calls, even if no real hierarchical call is proven end-to-end.
  > Recommendation: A — The workflow explicitly fails without a real ERC-like happy path. B and C can both produce false confidence if runtime behavior still breaks later in the flow.
  > **Selected: A**

**Q3: Which current bottleneck should this WF treat as first-order and which as second-order?**
- A) First-order: review detail call-awareness. Second-order: nested submit.
- B) First-order: hierarchical backend ingestion. Second-order: frontend UX.
- C) First-order: nested-call submit unblock. Second-order: review detail hardening needed to make the proof trustworthy.
  > Recommendation: C — The repo already supports hierarchy and some review-detail call-awareness, while nested submit is still explicitly blocked in the user path.
  > **Selected: C**

**Q4: How should we define "review detail fully call-aware" for Phase 0 scope?**
- A) It only needs to stop using Veni constants in code.
- B) It must render section grouping, labels, ordering, and coverage/traceability from call-linked metadata or stored call-linked payloads, with legacy fallback explicitly scoped.
- C) It must become a fully generic explorer for every possible hierarchical depth and future call variation.
  > Recommendation: B — This is strong enough to prevent a fake pass while keeping scope below a full universal explorer. A is too weak; C is broader than the unblocker.
  > **Selected: B**

**Q5: What should be the explicit problem boundary to avoid scope creep?**
- A) WF-0059 fixes the unblocker and proves one non-Veni hierarchical call; it does not promise universal support for every future call shape.
- B) WF-0059 should solve nested submit, review detail, import/export, review history, and future multi-step evaluation in one pass.
- C) WF-0059 should re-architect call handling across backend and frontend before proving any real call.
  > Recommendation: A — It preserves the forcing-function proof without letting the workflow expand into a platform rewrite.
  > **Selected: A**

### Parked Scope Creep

- "Universal support for every future call shape" is explicitly parked beyond WF-0059.

### Section 2 — Desired Outcome

**Q1: What measurable change best defines success for WF-0059?**
- A) At least one hierarchical call that previously hit the nested-node unsupported state can now produce a completed review with call-aware detail rendering.
- B) Nested nodes render in the submit form without considering submission or review detail.
- C) The codebase contains no nested-node guardrails.
  > Recommendation: A — This measures the end-to-end behavior the workflow exists to restore. B and C are implementation artifacts, not product outcomes.
  > **Selected: A**

**Q2: What behavior change should the user experience after this WF?**
- A) They can start a hierarchical call, but only flat leaf nodes are actually reviewed.
- B) They can complete and submit one real hierarchical call flow without hitting structural blockers, and the resulting review detail reflects the call's actual structure.
- C) They can use any call in the system with equal confidence.
  > Recommendation: B — It matches the stated proof bar without overclaiming universal readiness. A is too weak; C is broader than the workflow.
  > **Selected: B**

**Q3: What is the minimum acceptable proof artifact for "happy path works end-to-end"?**
- A) A few passing unit tests around the nested render model.
- B) Manual local spot-check only.
- C) Both automated coverage for the unblocker path and a concrete end-to-end proof artifact for one hierarchical call.
  > Recommendation: C — This workflow exists to avoid a fake pass. Tests alone can miss integrated seams; manual evidence alone is too weak and decays.
  > **Selected: C**

**Q4: How should we define the review-detail success threshold for MVP?**
- A) It must be call-aware for the proof call and any remaining legacy fallback must be explicit rather than silently Veni-shaped.
- B) It must remove all fallback behavior from the product, including mixed-version legacy reviews.
- C) It only needs to show cards somehow after submit.
  > Recommendation: A — It protects user trust on the proof call while containing scope. B is broader than necessary; C is not credible.
  > **Selected: A**

**Q5: What should count as "good enough" for Phase 0 MVP framing?**
- A) Unblock nested submit and prove the path on one hierarchical call, while preserving existing Veni behavior and deferring broader multi-call hardening.
- B) Support all existing nested and flat calls equally before closing the WF.
- C) Ship a new abstraction layer for all future funding-call structures before proof.
  > Recommendation: A — It is the tightest falsifiable outcome aligned to the proposal and avoids architecture-first drift.
  > **Selected: A**

### Section 3 — Target User / Actor

**Q1: Who is the primary actor for WF-0059?**
- A) Any user across every funding-call shape.
- B) A researcher/applicant using a real hierarchical funding call, with ERC-like structure as the proof target.
- C) Internal engineering only.
  > Recommendation: B — The workflow is product-facing and judged by a real applicant path, not by abstract platform readiness.
  > **Selected: B**

**Q2: Who is the most important secondary actor affected by this WF?**
- A) Internal product/demo owner who needs one trustworthy non-Veni path to validate broader usability claims.
- B) Procurement or billing admin.
- C) Anonymous landing-page visitor.
  > Recommendation: A — This workflow unblocks product credibility, but only through a real end-user path.
  > **Selected: A**

**Q3: What is the actor's primary job-to-be-done in this workflow?**
- A) Explore every possible call shape in a generalized interface.
- B) Submit proposal text across a hierarchical call structure and receive review output traceable to actual sections and evaluation criteria/elements.
- C) Manage call ingestion metadata.
  > Recommendation: B — It keeps the workflow anchored to the applicant path and the product's core value.
  > **Selected: B**

**Q4: What level of persona coverage is required?**
- A) One concrete happy-path persona is enough for this WF.
- B) Multiple personas across applicant, reviewer, and admin must all be optimized now.
- C) Internal-only persona coverage is enough.
  > Recommendation: A — The proof bar is one real usable path, not a full persona matrix.
  > **Selected: A**

**Q5: What trust signal must the actor receive to believe the path is valid?**
- A) Only that the submit button no longer errors.
- B) Clear evidence in review detail that labels, grouping, ordering, and traceability come from the selected call's structure rather than Veni-shaped assumptions.
- C) A generic "multi-call supported" badge.
  > Recommendation: B — The WF fails if the proof is not trustworthy to the user.
  > **Selected: B**

### Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction?**
- A) Remove the nested-node submit guardrail by making the existing submit experience operable for one real hierarchical call rather than rewriting the whole platform first.
- B) Build a universal abstraction layer for all future call shapes before proving anything.
- C) Add a hierarchical-call-only parallel UI path.
  > Recommendation: A — The fastest credible path is to deepen the existing generic seams only where the proof call forces it.
  > **Selected: A**

**Q2: How should the proof call influence scope?**
- A) It is just an example; we should design mainly for unknown future calls.
- B) It should be the forcing function for any required contract or UX changes, and anything not required by that path stays out.
- C) Avoid choosing a concrete proof call until implementation.
  > Recommendation: B — A concrete forcing function prevents speculative universalization.
  > **Selected: B**

**Q3: How should review detail get the data it needs?**
- A) Use call-linked metadata or stored call-linked payload structure to render grouping, labels, ordering, and coverage for the proof path.
- B) Reintroduce temporary call-specific maps for the proof call.
- C) Ignore grouping/coverage and just list cards in payload order.
  > Recommendation: A — The repo already has generic call-awareness seams; this workflow should rely on and deepen them, not backslide to call maps.
  > **Selected: A**

**Q4: How should flat-call compatibility be handled?**
- A) Preserve existing Veni/flat-call behavior while adding the minimum hierarchical handling needed for the proof call.
- B) Break current flat behavior if necessary to move faster on hierarchy.
- C) Freeze all flat-call paths and work only on hierarchy in isolation.
  > Recommendation: A — Preserving Veni behavior is an explicit constraint and a release guardrail.
  > **Selected: A**

**Q5: What architecture stance should this WF take?**
- A) Prefer deepening existing generic seams already present in contracts and review detail instead of introducing new parallel pathways.
- B) Pause to redesign backend and frontend call handling wholesale before proof.
- C) Add one-off logic for the proof call and clean it up later.
  > Recommendation: A — This avoids both rewrite drift and proof-only hacks.
  > **Selected: A**

### Section 5 — Constraints

**Q1: What is the top scope constraint?**
- A) Keep the WF focused on the bundled UX/runtime unblocker and one real hierarchical proof path.
- B) Use this opportunity to solve all multi-call debt at once.
- C) Expand into adjacent submission and review UX redesigns.
  > Recommendation: A — It protects delivery and keeps the workflow falsifiable.
  > **Selected: A**

**Q2: What compatibility constraint must remain explicit?**
- A) Preserve current Veni/flat-call behavior while unblocking the hierarchical path.
- B) Hierarchical support can replace flat support if needed.
- C) Compatibility can be decided later.
  > Recommendation: A — Preserving Veni behavior is a release constraint, not an optional nice-to-have.
  > **Selected: A**

**Q3: What class of work is explicitly out of scope even if tempting?**
- A) Full universal-call redesign, future-call generalization, and adjacent UX rewrites like import/export or review-history redesign.
- B) All tests and evidence work.
- C) Any contract changes whatsoever.
  > Recommendation: A — These are the main scope magnets that would replace the unblocker outcome with platform cleanup.
  > **Selected: A**

**Q4: What proof constraint must guide implementation?**
- A) Success requires a concrete proof artifact, not only code changes or compatibility claims.
- B) A merged PR without evidence is enough.
- C) Passing lint and unit tests is enough.
  > Recommendation: A — The workflow explicitly fails without a real ERC-like happy path.
  > **Selected: A**

**Q5: How should fallback behavior be treated?**
- A) Any remaining fallback behavior must be explicit and non-silent for legacy or mixed-version cases.
- B) Silent fallback is acceptable if the UI still renders.
- C) All fallback must be removed from the product immediately.
  > Recommendation: A — Silent fallback hides trust defects; full fallback removal is broader than required.
  > **Selected: A**

### Section 6 — Risks / Unknowns

**Q1: What is the most fragile assumption right now?**
- A) Removing the frontend nested-node guardrail may still expose a downstream runtime or contract mismatch during review creation or review-detail fetch/render.
- B) The product name may confuse users.
- C) The main risk is only CSS layout.
  > Recommendation: A — The integrated path is the highest-risk seam, and the repo snapshot already suggests multiple layers are involved.
  > **Selected: A**

**Q2: What must be validated earliest?**
- A) One concrete hierarchical call path should be proven end-to-end as early as possible rather than trusting partial unit-level progress.
- B) Only the submit form visuals.
- C) Future universal-call abstractions.
  > Recommendation: A — Early end-to-end proof is the fastest way to expose hidden blockers and avoid fake progress.
  > **Selected: A**

**Q3: What is the main source of likely rework?**
- A) Existing review-detail call-awareness may still rely on flat assumptions for coverage or grouping once a genuinely hierarchical payload is exercised.
- B) The landing page copy.
- C) Removing all fallback behavior immediately.
  > Recommendation: A — The proof path could still break on subtle flat-shape assumptions even if submit starts working.
  > **Selected: A**

**Q4: What other planning risk could blur success criteria?**
- A) Choosing a proof call whose structure is not actually runnable with current data/contracts, making it unclear whether the blocker is UX/runtime or call readiness.
- B) Picking too many font variants.
- C) Adding too much telemetry.
  > Recommendation: A — The proof target itself must be concrete and runnable enough to serve as a valid forcing function.
  > **Selected: A**

**Q5: What residual risk is acceptable for this WF?**
- A) Broader future-call generalization can remain unresolved as long as the proof path and explicit non-goals stay clear.
- B) The proof path can remain ambiguous if the docs sound confident.
- C) Veni regressions are acceptable.
  > Recommendation: A — This workflow is intentionally narrow; unresolved broader generalization is acceptable if clearly deferred.
  > **Selected: A**

### Section 7 — MVP Definition

**Q1: If limited to a short implementation window, what must exist?**
- A) One real hierarchical call can move from submit UI through review creation to call-aware review detail without structural blockers.
- B) Every hierarchical call in the repo works equally well.
- C) A full architecture rewrite is complete.
  > Recommendation: A — This is the smallest slice that still satisfies the workflow's falsifiable proof obligation.
  > **Selected: A**

**Q2: What submit behavior must be eliminated?**
- A) The nested-node unsupported gate must be replaced by a functional path for the proof call rather than a silent fallback or cosmetic state change.
- B) Only the wording of the unsupported message must change.
- C) The user can be redirected away from unsupported calls without further work.
  > Recommendation: A — A cosmetic or silent workaround would fail the workflow's core objective.
  > **Selected: A**

**Q3: What review-detail behavior is non-negotiable for MVP?**
- A) It must use call-linked grouping, labels, ordering, and explicit coverage/traceability behavior for the proof path.
- B) It only needs to show a summary and raw cards.
- C) It can rely on Veni-like defaults if the proof call mostly looks right.
  > Recommendation: A — Trustworthy call-awareness is part of the success definition, not optional polish.
  > **Selected: A**

**Q4: What compatibility requirement remains part of MVP?**
- A) Existing Veni flow must remain working.
- B) Flat-call behavior can regress temporarily.
- C) Compatibility is outside MVP.
  > Recommendation: A — Preserving the current working path is part of the acceptance boundary.
  > **Selected: A**

**Q5: What evidence requirement is part of the MVP itself?**
- A) Automated coverage plus one concrete proof artifact are required to close the WF.
- B) Evidence can be added after closure if someone asks.
- C) Only manual confidence is needed.
  > Recommendation: A — The proof artifact is part of the deliverable, not optional documentation.
  > **Selected: A**

### Section 8 — Explicit Non-Goals

**Q1: What broad promise must explicitly be postponed?**
- A) Full universal support for every future call shape.
- B) Any support for hierarchical calls at all.
- C) All generic contract changes.
  > Recommendation: A — This is the main scope-creep magnet already identified and parked.
  > **Selected: A**

**Q2: What product surface is explicitly not being redesigned here?**
- A) Product-wide redesign of review detail, review history, or submission UX outside what the proof path forces.
- B) The exact proof-path surfaces touched by the unblocker.
- C) Any user-visible change.
  > Recommendation: A — This keeps the workflow centered on the unblocker rather than adjacent UX ambition.
  > **Selected: A**

**Q3: What adjacent capability stays out of scope?**
- A) New import/export pipelines, document parsing, or broad workflow changes unrelated to nested submit plus call-aware review detail.
- B) All evidence work.
- C) Call selection.
  > Recommendation: A — These are tempting but not necessary for the proof obligation.
  > **Selected: A**

**Q4: What call-specific future capability is deferred?**
- A) Multi-step evaluation logic and other future call-specific capabilities not required for one hierarchical happy path.
- B) Any criteria/elements traceability.
- C) The proof call itself.
  > Recommendation: A — It avoids pulling in future call semantics that are unrelated to the immediate unblocker.
  > **Selected: A**

**Q5: What engineering stance is explicitly out of bounds?**
- A) Architecture-first refactors not necessary to unblock and prove the selected hierarchical call.
- B) Minimal generic changes forced by the proof path.
- C) Preserving current Veni behavior.
  > Recommendation: A — This prevents the workflow from turning into an abstract cleanup effort.
  > **Selected: A**
