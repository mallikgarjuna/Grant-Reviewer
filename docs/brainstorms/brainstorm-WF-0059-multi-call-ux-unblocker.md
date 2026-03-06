<!-- docs/brainstorms/brainstorm-WF-0059-multi-call-ux-unblocker.md -->
# WF-0059 — Multi-call UX Unblocker

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-06

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1-3 "Contract Notes / Non-obvious constraints" bullets and link to the relevant Q&A section header.

---

## Preflight Checklist

### Step 1 — Long-Form Problem Intake

- PeerLens is currently usable only along a Veni-shaped happy path, which blocks trust in the product beyond one flat call shape.
- The immediate user pain is that hierarchical or nested calls can be selected and partially rendered, but the review-creation flow does not complete when the call structure contains nested sections.
- Review detail also must be trustworthy for non-Veni calls: labels, grouping, ordering, and traceability must come from call data rather than Veni-shaped assumptions.
- The success bar for this WF is one real ERC-like hierarchical happy path that can be submitted and reviewed end-to-end; if the workflow still only proves Veni, it failed.
- Scope must stay focused on the UX/runtime unblocker, preserve working Veni behavior, and avoid turning this WF into a broad universal-call redesign.

### Repo Reality Snapshot (Read-Only) (2026-03-06)

- The submit renderer still hard-blocks nested calls today: `frontend/src/lib/submit/renderModel.ts` returns `unsupported` with reason `nested_nodes`.
- The universal submit UI surfaces that blocker directly in the product path: `frontend/src/components/submit/UniversalSubmitForm.tsx` prevents submission when render state is unsupported.
- Review detail is no longer purely Veni-hardcoded: `frontend/src/app/app/reviews/[reviewId]/page.tsx` already uses `call_id`, `/calls/{call_id}/nodes`, and `order_index` when metadata is available.
- The review detail contract already carries call-awareness fields (`call_id`, `call_code`, `ordering_source`, `unmapped_node_logical_ids`) in `backend/app/schemas/api.py`, so part of the earlier generic contract work is already in place.
- Backend/API support for hierarchy already exists at least at the node-contract level (`GET /calls/{call_id}/nodes?view=tree`, `NodeTreeNode`, `node_tree_service.py`), which means the main platform gap is the applicant submit UX/runtime path rather than raw hierarchy storage.

### Open Questions Suggested by Repo Snapshot

- Does WF-0059 need to unblock nested rendering only in the frontend, or is there still a downstream review-create/runtime contract gap once nested payloads are allowed through?
- What exact proof artifact will count as "one ERC-like happy path works end-to-end": automated tests only, manual walkthrough evidence, or both?
- Should the review detail scope focus on closing remaining fallback paths for mixed-version payloads, or is "call-aware when metadata exists" already good enough for MVP?
- Which concrete hierarchical call should be the proof target: existing ERC data already in repo, or another non-Veni call with nested structure that is easier to exercise?

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md` (Section 1)

- Primary product defect: the platform cannot complete one real non-Veni hierarchical applicant happy path because nested-call submit is blocked.
- The required success proof is one concrete ERC-like hierarchical call that can be selected, completed, submitted, and reviewed end-to-end.
- First-order bottleneck: nested-call submit unblock. Second-order bottleneck: review detail hardening needed to make the proof trustworthy.
- "Review detail fully call-aware" means section grouping, labels, ordering, and coverage/traceability come from call-linked metadata or stored call-linked payloads, with any legacy fallback explicitly scoped.
- Scope boundary: WF-0059 fixes the unblocker and proves one non-Veni hierarchical call; it does not promise universal support for every future call shape.

Contract notes / non-obvious constraints:
- A UX-only removal of the unsupported nested-call message is insufficient; the proof bar includes successful review creation and trustworthy review detail rendering.
- Review-detail success is defined by call-linked rendering behavior, not merely by deleting Veni-specific constants.
- Universal support for every future call shape is explicitly parked to prevent Phase 0 from turning into a platform rewrite.

## 2. Desired Outcome

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md` (Section 2)

- Success is measured by at least one hierarchical call that previously hit the nested-node unsupported state now producing a completed review with call-aware detail rendering.
- Desired user-visible behavior: a researcher can complete and submit one real hierarchical call flow without structural blockers, and the resulting review detail reflects the call's actual structure.
- Minimum acceptable proof requires both automated coverage for the unblocker path and a concrete end-to-end proof artifact for one hierarchical call.
- Review-detail success threshold: it must be call-aware for the proof call, and any remaining legacy fallback must be explicit rather than silently Veni-shaped.
- "Good enough" means unblocking nested submit and proving one hierarchical call while preserving current Veni behavior and deferring broader multi-call hardening.

Contract notes / non-obvious constraints:
- Removing the frontend unsupported state alone does not satisfy the workflow; review creation and review-detail rendering must also succeed.
- The proof artifact must be tied to one concrete hierarchical call rather than a generic capability claim.
- Legacy fallback behavior is allowed only if it is explicit and scoped to old payloads, not silently used for the proof path.

## 3. Target User / Actor

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md` (Section 3)

- Primary actor: a researcher/applicant using a real hierarchical funding call, with ERC-like structure as the proof target.
- Secondary actor: the internal product/demo owner who needs one trustworthy non-Veni path to validate the platform's broader usability claim.
- Primary user job: submit proposal text across a hierarchical call structure and receive review output that stays traceable to the call's actual sections and evaluation criteria/elements.
- The workflow optimizes for a single concrete happy path, not for broad multi-persona UX coverage.
- Trust requirement: the actor must be able to see that the review detail is derived from the selected call's structure, not from Veni-shaped assumptions.

Contract notes / non-obvious constraints:
- The proof actor is still an end-user in the applicant flow; this WF is not an internal admin-only infrastructure exercise.
- Internal/demo confidence matters, but only insofar as it reflects a real end-user path that works.
- The actor definition excludes "all users/all calls" scope for this WF.

## 4. Rough Idea (Unstructured Thinking)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md` (Section 4)

- Simplest direction: remove the nested-node submit guardrail by making the submit experience operable for one real hierarchical call, rather than building a broad abstraction-first rewrite.
- Treat the proof call as the forcing function for any required frontend/runtime contract changes; only generic changes strictly required for that path are in scope.
- Review detail should consume call-linked metadata or stored call-linked payload structure to render grouping, labels, ordering, and coverage for the proof path.
- Preserve existing flat-call/Veni behavior while adding the minimum hierarchical handling needed for the proof call.
- Prefer deepening the existing generic seams already present in contracts and review detail instead of introducing new parallel pathways.

Contract notes / non-obvious constraints:
- Any contract change introduced here must remain generic, but it only needs to cover what the proof call forces.
- The workflow should not fork into separate Veni-specific and hierarchical-specific product experiences unless the fallback is explicitly legacy-only.
- The proof call is the correctness driver; architecture work not required by that path is out of scope.

## 5. Constraints

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md` (Section 5)

- Hard scope constraint: keep the WF focused on the bundled UX/runtime unblocker and one real hierarchical proof path.
- Preserve current Veni/flat-call behavior while unblocking the hierarchical path.
- Avoid a full universal-call redesign, future-call generalization pass, or adjacent UX rewrites such as import/export and review-history redesign.
- Success requires a concrete proof artifact, not only code changes or compatibility claims.
- Any remaining fallback behavior must be explicit and non-silent for legacy or mixed-version cases.

Contract notes / non-obvious constraints:
- "Generic where required" is allowed; "generic everywhere" is not required in this WF.
- Scope exclusions are binding because adjacent product debts could easily swallow the unblocker outcome.
- Preserving Veni behavior is a release constraint, not a nice-to-have.

## 6. Risks / Unknowns

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md` (Section 6)

- Most fragile assumption: removing the frontend nested-node guardrail may still expose a downstream runtime or contract mismatch during review creation or review-detail fetch/render.
- Early validation target: prove one concrete hierarchical call path end-to-end as soon as possible rather than trusting partial unit-level progress.
- Rework risk: the existing review-detail call-awareness may still rely on flat assumptions for coverage or grouping once a genuinely hierarchical payload is exercised.
- Another rework risk is choosing a proof call whose structure is not actually runnable with current data/contracts, which would blur whether the blocker is UX/runtime or call readiness.
- Residual risk accepted for Phase 0: this WF may leave broader future-call generalization unresolved, as long as the proof path and explicit non-goals stay clear.

Contract notes / non-obvious constraints:
- A "works in tests, fails in the integrated flow" outcome is the main failure mode this WF must defend against.
- Hidden flat-shape assumptions in coverage summaries or payload storage count as blocker-class risk for the proof path.
- The proof target itself must be concrete enough in planning to prevent ambiguous success claims.

## Open Questions / Deferred

- Open questions to resolve in planning:
- Which exact hierarchical call in repo will be the proof target, and what evidence path will validate it end-to-end?
- What minimum submit/runtime contract changes are required once nested nodes are allowed through the current unsupported guardrail?
- Does review-detail coverage need to move fully off `submitted_nodes` query-param assumptions for the proof path?
- What automated test seam best proves the end-to-end unblocker without overfitting to one implementation detail?

- Deferred / parked:
- "Universal support for every future call shape" is explicitly deferred beyond WF-0059.
- Broader multi-call hardening beyond the proof path is deferred.
- Import/export, review-history redesign, and multi-step evaluation flows remain out of scope.

## 7. MVP Definition

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0059-multi-call-ux-unblocker.md` (Section 7)

- If limited to a short implementation window, the must-have slice is: one real hierarchical call can move from submit UI through review creation to call-aware review detail without structural blockers.
- The nested-node unsupported gate must be replaced by a functional path for the proof call rather than a silent fallback or cosmetic state change.
- Review detail for the proof path must use call-linked grouping, labels, ordering, and explicit coverage/traceability behavior.
- Existing Veni flow must remain working.
- Automated coverage plus one concrete proof artifact are required to close the WF.

Contract notes / non-obvious constraints:
- MVP is defined by end-to-end usability of one hierarchical call, not by the number of generalized utilities introduced.
- Preserving the flat-call path is part of MVP acceptance.
- The proof artifact is part of the deliverable, not post-hoc documentation.

## 8. Explicit Non-Goals

- Full universal support for every future call shape.
- Product-wide redesign of review detail, review history, or submission UX outside what the proof path forces.
- New import/export pipelines, document parsing, or broad workflow changes unrelated to nested submit + call-aware review detail.
- Multi-step evaluation logic and other call-specific future capabilities that are not required for one hierarchical happy path.
- Architecture-first refactors that are not necessary to unblock and prove the selected hierarchical call.

Contract notes / non-obvious constraints:
- These non-goals exist to stop "platform cleanup" from replacing the actual proof obligation.
- Generic changes are acceptable only when they are the minimal way to satisfy the proof path.
