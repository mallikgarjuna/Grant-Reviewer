<!-- docs/brainstorms/brainstorm-WF-0065-cross-call-contract-hardening-base-review-semantics.md -->
# WF-0065 — Cross-Call Contract Hardening of Base Review Semantics

Artifact: brainstorm
Version: v0.5
Status: Draft Complete
Last Updated: 2026-03-08

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts/decisions (what we will implement).
- The Q&A transcript is rationale only; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, promote the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1-3 Contract Notes / Non-obvious constraints bullets and link to the relevant Q&A section header.

---

## 0. Preflight Intake (Narrative Locked)

Problem narrative approved by user (as-is):
- PeerLens helps researchers improve grant proposals before submission with feedback grounded in official call requirements, aligned to evaluation criteria/elements, and traceable enough to trust.
- WF-0063 and WF-0064 closed the `MSCA-PF-2025` proof-path gaps around opted-in hierarchical visibility/submit behavior; the blocker is no longer hierarchical submit behavior itself.
- The remaining mission-critical gap is insufficient deterministic evidence that the same base review contract semantics hold consistently across supported calls and failure modes.
- The target failure modes called out explicitly for this WF are `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`, with fail-closed behavior required at the contract boundary.
- Scope must stay tight: trust-surface hardening only, no broad product redesign, no supporting-context expansion, no speculative onboarding, no unrelated refactors.

---

## Repo Reality Snapshot (Read-Only) (2026-03-08)

- The base review pipeline already exists in `backend/app/engine/pipeline_v1.py` with the six-stage WF-0045 contract and deterministic failure-class mapping (`CONTRACT_FAILURE` vs `EXECUTION_FAILURE`).
- Deterministic call-agnostic pipeline tests already exist, but the cross-call stress harness is still thin: the MSCA archetype is synthetic and the current matrix asserts only severity outcomes, not broader contract-boundary semantics.
- Supported canonical calls with real repo artifacts currently include NWO Veni 2025, NWO Vidi 2025, ERC StG 2026, ERC CoG 2026, and MSCA-PF-2025; backlog rationale says the remaining promised-program breadth gap should stay after this hardening WF.
- API-level tests already assert `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`, but those assertions are still generic/seeded rather than explicitly proven across multiple supported calls and both review entry surfaces; real-call API helpers currently exist for ERC CoG, ERC StG, and MSCA-PF-2025.
- Repo reality splits the review runtime into two service paths: `POST /reviews` flows through `ReviewerService.generate_review`, while `POST /api/structured-review` flows through `StructuredReviewerService.generate_structured_review_pipeline_v1` and then `pipeline_v1`; the named gates live in the API endpoints before either service path is entered.
- WF-0063/WF-0064 hardened the MSCA proof path and preserved fail-closed supporting-node rejection, which means this WF should target broader base-review consistency rather than reopen supporting-context or hierarchical-submit semantics.

Open questions from snapshot:
- Which boundary is the true MVP proof target for this WF: engine contract only, API/service contract only, or paired engine-plus-API parity?
- Which supported calls count as the minimum credible cross-call set for mission trust: one NWO, one ERC, and MSCA, or all currently supported real calls?
- Should `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` be proven only at API entrypoints, or also through service-level invariants that confirm no fail-open execution occurs underneath?
- Is the main trust gap insufficient test breadth, or are there still unproven semantic differences between real call snapshots at the call-config boundary?
- What explicit evidence threshold is strong enough to say “dependable across calls” without broadening into new-call onboarding?

---

## 1. Problem Statement

### Decisions (selected)

- The primary defect is that the base review contract is not yet proven consistent at the contract boundary across supported calls and failure gates.
- WF-0065 MVP proof set is exactly one real supported call from each active family: NWO, ERC, and MSCA.
- Fail-closed consistency must be proven at the paired boundary for each real runtime path: `POST /reviews` with `ReviewerService.generate_review`, and `POST /api/structured-review` with `StructuredReviewerService.generate_structured_review_pipeline_v1`, plus the underlying `pipeline_v1` execution seam on the structured path where fail-open drift could hide.
- Blocking drift includes any mismatch in status/error semantics, gating behavior, or review-contract outcomes for the same boundary case across calls.
- The problem statement explicitly excludes supporting-context semantics, new-call onboarding, and broad pipeline redesign.
- Phase 1 must name the exact representative call code per family before PRD sign-off; if the default family representative lacks a stable real-call proof seam, the artifact must either switch to another already supported real call in that family or log a blocker before widening scope.

Contract Notes / Non-obvious constraints:
- “Cross-call” here means the locked 3-call proof set unless Phase 1 documents a blocker showing family-level variance still leaves a material semantic gap.
- API-only evidence is not enough if internal execution could still fail open before the boundary response is formed.
- The shared proof target is semantic parity, not DTO unification; `/reviews` and `/api/structured-review` may keep different request shapes as long as overlapping status/error/idempotency/persistence semantics stay consistent and explicit.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 1)

---

## 2. Desired Outcome

### Decisions (selected)

- Success means deterministic evidence that the same base review semantics hold across representative NWO, ERC, and MSCA calls at the paired engine-plus-API boundary.
- “Good enough” for MVP is a narrow evidence bundle of deterministic contract tests proving consistent success, fail-closed gating, and failure-mode behavior without broadening scope.
- Expected behavior change is increased release confidence: supported calls stop relying on proof slices and instead share an explicit cross-call trust baseline.
- Required failure-mode outcome includes explicit deterministic coverage for `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` at the API entry boundary, with proof that neither downstream service path executes and that no engine execution or partial persistence occurs beyond the gate.
- The desired outcome is evidence-first, not architecture-first: tests and invariant proof count more than prose expansion.
- Preserved external semantics include current HTTP/error-code behavior, idempotency replay behavior, idempotency payload-mismatch rejection, and validation-before-idempotency ordering on each in-scope endpoint.

Contract Notes / Non-obvious constraints:
- Passing evidence must be concrete enough to support the product claim “traceable enough to trust,” not just “works in representative demos.”
- Failure-mode proof must show returned semantics plus explicit absence of downstream review creation, pipeline execution, and partial persisted review state for blocked gate outcomes.
- “Consistent semantics” means more than matching severity labels: it includes review status class, stable error codes/details shape, ordering of gate evaluation, and whether persistence/execution happens at all.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 2)

---

## 3. Target User / Actor

### Decisions (selected)

- Primary actor is the internal product/engineering/release owner deciding whether the base review surface is trustworthy enough to support launch claims.
- Secondary protected actor is the researcher, who depends on review behavior being consistent and traceable across supported calls even if they never see the internal contract tests.
- The key frustration is not missing features; it is uncertainty about whether the same semantics really hold once the call changes or failure gates trigger.
- The artifact audience for this WF is downstream planning and implementation owners who need an unambiguous trust-hardening scope.
- This WF prioritizes contract-boundary reliability over UX expansion, content expansion, or architectural cleanup.

Contract Notes / Non-obvious constraints:
- Internal actor priority raises the evidence bar: “trustworthy” must be proven before more onboarding or surface expansion.
- Researcher trust is an outcome constraint, even though the direct workflow audience is internal.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 3)

---

## 4. Rough Idea (Unstructured Thinking)

### Decisions (selected)

- The simplest direction is a contract-hardening WF centered on deterministic cross-call tests at the engine and API/service seams, not a redesign of the pipeline.
- Representative calls should come from real supported families already in-repo, with no speculative onboarding unless current representatives cannot expose the required semantics.
- The WF should harden both happy-path and failure-gate semantics under one trust story, while keeping the proof surfaces explicit: review execution cases use paired path-specific service-plus-API parity; quota/policy gates use API-entry fail-closed assertions plus downstream non-invocation proof.
- Existing WF-0045 stage contracts and WF-0063/WF-0064 fail-closed proof behavior are baseline inputs, not subjects for reinvention.
- The implementation direction should prefer extending existing deterministic fixtures/selectors over inventing new broad harnesses unless current seams are inadequate.
- Shared-core extraction, if needed, must stop at semantic seams such as gating order, pipeline invocation, persistence guards, telemetry hooks, and deterministic request normalization; it must not force endpoint DTO convergence or a broad repository/service rewrite.

Contract Notes / Non-obvious constraints:
- The WF is allowed to expose missing seams if existing tests cannot prove the contract, but only as minimal implementation work in service of evidence.
- “Cross-call hardening” does not mean each call gets unique semantics; it means the same semantics are asserted against varied real call shapes.
- The current repo already has mixed test surfaces (synthetic seeded API/service paths plus some real-call helpers), so Phase 1 should prefer upgrading those seams to real-call parity before creating new harnesses.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 4)

---

## 5. Constraints

### Decisions (selected)

- Scope is tightly limited to trust-surface hardening for base review semantics across supported calls and named failure modes.
- The WF must stay fail-closed and preserve existing contract boundaries unless a specific deterministic proof gap requires a minimal correction.
- Supported-call breadth is constrained to current active families already represented in-repo; no new onboarding unless lack of a real representative becomes a documented blocker.
- The workflow should prefer deterministic tests and contract evidence over architectural prose, broad refactors, or speculative cleanup.
- Any implementation changes must remain subordinate to evidence goals and avoid unrelated UI, supporting-context, or onboarding work.
- No endpoint routing flip, DTO redesign, or persistence-model rewrite is in scope for MVP; if a new shared seam is required, it must land under no-behavior-change parity tests first and remain reversible without changing public endpoint contracts.

Contract Notes / Non-obvious constraints:
- Tight scope means some superficially related items remain deferred even if encountered during analysis.
- A missing proof seam may justify a narrow code change, but not a “while we are here” redesign.
- For `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`, fail-closed means no review creation, no pipeline run, and no partial persisted review state.
- For `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`, fail-closed proof must attach to the API gate and explicitly show neither `ReviewerService.generate_review` nor `StructuredReviewerService.generate_structured_review_pipeline_v1` was entered.
- For idempotency-related cases, fail-closed also means replay preserves the original review without creating a second row, while payload mismatch returns the existing conflict semantics without mutating persisted state.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 5)

---

## 6. Risks / Unknowns

### Decisions (selected)

- Highest risk is that current evidence overstates universality because the contract is only deeply proven on slices, not across representative real calls and failure modes.
- Another key risk is boundary-only success masking internal fail-open behavior, especially around gating outcomes like quota or review disabling.
- The most likely scope-creep trap is slipping into new-call onboarding, supporting-context semantics, or generalized pipeline cleanup.
- A real unknown is whether one representative call per family is sufficient, or whether ERC/NWO family variance still exposes material contract differences that require broader proof.
- The first validation target is identifying the exact unproven semantic invariants that still matter for launch trust, not merely adding more tests indiscriminately.

Contract Notes / Non-obvious constraints:
- More tests are not automatically better if they do not prove the boundary invariants that the mission claim depends on.
- If representative-family coverage proves insufficient, rescoping must be explicit and justified, not implicit through task creep.
- A “green” engine-only result does not close launch risk if endpoint-specific ordering or idempotency semantics can still drift.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 6)

---

## Open Questions / Deferred

- Phase 1 decision gate: if the locked 3-call proof set proves insufficient to expose material semantic variance, document the blocker and rationale before widening call coverage.
- Deferred: remaining promised-program breadth gap (for example ZonMw-equivalent expansion) stays out of this WF unless current supported-call coverage proves insufficient to validate the contract.
- Deferred: explicit supporting-context semantics beyond the WF-0063/WF-0064 proof-call MVP remain out of scope.
- Deferred: broad pipeline redesign, performance optimization, and optional extension boundary redesign remain outside this WF.

---

## 7. MVP Definition

### Decisions (selected)

- The smallest acceptable slice is a deterministic proof bundle showing that representative NWO, ERC, and MSCA calls preserve the same core base-review contract semantics across the real endpoint, service, and structured-engine boundaries that exist today.
- MVP must explicitly cover `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` as API-entry fail-closed contract outcomes with no execution or persistence side effects.
- MVP should prefer existing real call snapshots and current runtime seams over creating synthetic abstractions, unless synthetic coverage is only needed to isolate a boundary invariant.
- The minimum acceptable output is evidence strong enough to decide whether the current review behavior is dependable across calls and failure modes.
- Anything not required to reach that decision is excluded from MVP.
- Required proof seams are explicit: direct service tests for `ReviewerService.generate_review` and `StructuredReviewerService.generate_structured_review_pipeline_v1`, direct execution tests for `pipeline_v1`, and endpoint tests for both `POST /reviews` and `POST /api/structured-review` wherever the contract surface exists.
- Required parity assertions are explicit: success-path review status behavior, stable error semantics, validation/gating order, idempotency replay and mismatch behavior, and no-persistence/no-execution guarantees for blocked paths.

Contract Notes / Non-obvious constraints:
- “Dependable” in MVP terms means proven stable semantics, not perfect feature completeness across the product.
- A planning artifact alone is insufficient; the later phases must be structured toward executable deterministic evidence.
- If the locked 3-call proof set proves insufficient, widening call coverage requires an explicit Phase 1 blocker note rather than silent scope expansion.
- “No behavior change first” is enforceable here: if Phase 1 introduces a new shared seam, parity tests must prove the current endpoint behavior before any semantic correction is attempted.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 7)

---

## 8. Explicit Non-Goals

### Decisions (selected)

- No new call onboarding unless a documented blocker shows the current supported-call set cannot prove the contract.
- No supporting-context semantic expansion beyond the existing WF-0063/WF-0064 proof-call boundary.
- No broad pipeline redesign, architecture rewrite, or unrelated refactor work.
- No product-surface expansion whose primary value is UX/content breadth rather than trust-surface hardening.
- No speculative features or adjacent planning work outside the base review contract boundary.

Contract Notes / Non-obvious constraints:
- This WF is about proving or falsifying trust claims on the current surface, not increasing the size of that surface.
- Non-goals are hard guards for Phase 1 and should be preserved unless a blocker is documented and accepted explicitly.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md` (Section 8)
