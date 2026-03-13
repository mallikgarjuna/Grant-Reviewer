<!-- docs/prds/completed/prd-WF-0077-structured-review-deterministic-researcher-guidance.md -->
# WF-0077 — Structured Review Deterministic Researcher Guidance

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-13

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher using the structured `/app` review flow for `ERC-2026-PoC`, I want assessed cards to tell me what to revise next in deterministic evaluation-criteria-grounded language, so that I can improve proposal text without decoding reviewer-question lists.
- US2: As a backend maintainer, I want the guidance rewrite to live only in `StructuredReviewerService`, so that the active structured-review path improves without mutating raw machine `reason`, evaluator semantics, or cross-call mapper behavior.
- US3: As a maintainer protecting scope and trust, I want the MVP locked to `ERC-2026-PoC` with fail-closed fallback behavior and service-level TDD proof, so that this WF does not widen into frontend polish, OpenAI synthesis, or broader call rollout.

## Deferred Stories (Not in MVP)

- As a researcher, I want the same deterministic guidance transform to apply to all structured-review calls immediately.
- As a maintainer, I want frontend grouping/copy updates that further polish how cards render after backend guidance improves.
- As a maintainer, I want OpenAI-backed coaching or synthesized revision advice layered on top of deterministic guidance primitives.

## 1. In Scope

- Improve researcher-facing `feedback_text` for assessed `ERC-2026-PoC` structured-review cards so the output reads as concise revision guidance rather than subordinate-prompt question lists. `(US1) (US3)`
- Keep the implementation at the existing presentation seam in `backend/app/services/structured_reviewer_service.py`, specifically the feedback-resolution path that already contains WF-0069 and WF-0076 logic. `(US2) (US3)`
- Reuse only existing deterministic inputs already available on the structured path: evaluation element labels, canonical subordinate-prompt text, and the machine outcome already produced by the active backend flow. `(US1) (US2)`
- Preserve raw machine `reason` for audit and traceability, with researcher-facing guidance remaining an additive presentation transform rather than a replacement for stored machine signal. `(US2) (US3)`
- Prefer a backend-only MVP with regression proof in `backend/tests/test_structured_reviewer_service.py`; only plan frontend work later if backend proof reveals a remaining rendering mismatch. `(US2) (US3)`
- Require deterministic fallback behavior that preserves existing WF-0076-style prompt rendering when canonical subordinate-prompt text is missing, unresolved, duplicated into an unusable surface, or otherwise too weak to support an honest imperative rewrite. `(US1) (US3)`

## 2. Out of Scope

- Any OpenAI or other LLM call, synthesis layer, or prompt-engine redesign. `(US3)`
- Changes to `backend/app/engine/findings/evaluator.py`, `backend/app/engine/compat/review_card_mapper.py`, or the legacy `ReviewerService` path as the primary MVP seam. `(US2) (US3)`
- Frontend-first rewriting, formatting, or grouping changes unless a later phase proves the backend contract alone is insufficient. `(US3)`
- Broadening the deterministic guidance transform beyond `ERC-2026-PoC` during MVP. `(US3)`
- Reworking WF-0074, WF-0075, or WF-0076 contracts around canonical call fidelity, fail-closed engine boundaries, or subordinate-prompt traceability. `(US2) (US3)`

## 3. User / System Flow

- Happy path
  - A researcher opens an `ERC-2026-PoC` structured review in `/app`, and the backend reaches the existing `StructuredReviewerService` presentation seam after deterministic review execution completes. `(US1) (US2)`
  - For an assessed card with usable `ERC-2026-PoC` subordinate-prompt text, the service resolves evaluation-element-grounded imperative guidance such as clarifying what to strengthen, evidence to add, or the gap to close, instead of returning a raw question list. `(US1) (US2)`
  - The structured-review response still carries the original machine `reason` for audit while `feedback_text` becomes researcher-facing deterministic guidance. `(US1) (US2) (US3)`
  - Existing frontend rendering continues to display `card.feedback_text` directly, so the backend-only contract change is sufficient for MVP. `(US1) (US3)`
- Failure path 1
  - The service can resolve subordinate prompts, but the rewritten text still reads mainly as reviewer questions rather than revision guidance, so MVP remains incomplete because the product outcome did not change materially. `(US1) (US3)`
- Failure path 2
  - The required source prompt surface is missing, unresolved, or too weak to support an honest rewrite, so the service must keep the WF-0076 prompt-list fallback instead of fabricating stronger advice. `(US1) (US3)`
- Failure path 3
  - Implementation planning pulls evaluator, mapper, legacy review, frontend, or cross-call rollout into the first slice, so the workflow fails closed for scope drift beyond the approved seam. `(US2) (US3)`

## 4. Functional Requirements

- FR1 (US1) (US2): `StructuredReviewerService` must transform assessed `ERC-2026-PoC` subordinate-prompt/question surfaces into concise deterministic revision guidance in `feedback_text`.
- FR2 (US1) (US2): The guidance transform must stay grounded in existing evaluation element labels plus canonical subordinate-prompt text already available to the structured path; it must not invent new semantic claims not supported by those sources.
- FR3 (US2) (US3): Raw machine `reason` must remain preserved for audit and traceability and must not be mutated, suppressed, or repurposed as the only researcher-facing output.
- FR4 (US2) (US3): MVP implementation must stay in `backend/app/services/structured_reviewer_service.py` and must not move the primary guidance rewrite into evaluator, compatibility mapper, legacy review service, or frontend.
- FR5 (US3): MVP scope is `ERC-2026-PoC` only; non-targeted calls must keep their existing deterministic behavior unless a later artifact explicitly re-approves widening.
- FR6 (US1) (US3): If the subordinate-prompt surface is missing, unresolved, duplicated into an unusable surface, or too weak to support an imperative rewrite without invention, the service must preserve existing WF-0076 fallback output instead of fabricating stronger guidance.
- FR7 (US2) (US3): Phase 3 must start with a failing regression in `backend/tests/test_structured_reviewer_service.py` proving the current `ERC-2026-PoC` output is still question-shaped or prompt-list-shaped before implementation begins.
- FR8 (US1) (US2): Service-level regression tests must prove the new `feedback_text` is actionable revision guidance for targeted `ERC-2026-PoC` cards rather than raw machine text or raw prompt lists.
- FR9 (US2) (US3): Service-level regression tests must prove raw machine `reason` preservation alongside the new researcher-facing `feedback_text`.
- FR10 (US3): Service-level regression tests must prove non-targeted calls remain unchanged by the `ERC-2026-PoC`-specific transform.
- FR11 (US1) (US3): Service-level regression tests must prove fallback honesty when subordinate-prompt surfaces are unusable, preserving WF-0076-style output rather than invented guidance.
- FR12 (US2) (US3): Phase 2 task planning must keep the first implementation slice bounded to `StructuredReviewerService` plus `backend/tests/test_structured_reviewer_service.py`, with each task preferring no more than three touched files and any broader work split into dependent follow-on tasks instead of one wide slice.
- FR13 (US3): The optional frontend necessity check may close as an explicit skip only if Phase 2 cites the current direct `card.feedback_text` render path and no backend proof shows a remaining UI truthfulness gap.
- FR14 (US3): No proceed or implementation-ready claim is valid unless the final proof set includes an explicit fail-closed verification matrix and an audit-disposition record closing every blocking finding and closing or justifying every non-blocking finding.

## 5. Data & API Contracts

- Structured-review response contract `(US1) (US2) (FR1) (FR3) (FR8) (FR9)`
  - Target seam: `backend/app/services/structured_reviewer_service.py`
  - Required behavior:
    - `card.feedback_text` may change for targeted `ERC-2026-PoC` assessed cards;
    - researcher-facing text must become deterministic revision guidance;
    - raw machine `reason` remains preserved on the underlying review artifact for audit/traceability;
    - no new public API field is required for MVP if the current response already returns `feedback_text`.
- Guidance-source contract `(US1) (US2) (FR2) (FR6)`
  - Required behavior:
    - guidance must derive from already-available evaluation element labels and canonical subordinate-prompt text;
    - the transform may reshape that source into imperative revision guidance;
    - the transform must fail closed to existing WF-0076 prompt rendering when those source surfaces are unusable for honest rewrite.
- Scope contract `(US2) (US3) (FR4) (FR5)`
  - Required behavior:
    - the primary behavior change must stay inside `StructuredReviewerService`;
    - no evaluator, mapper, legacy review, or frontend contract widening is required for MVP;
    - non-targeted calls must continue to receive their current deterministic `feedback_text`.
- Planning-slice contract `(US2) (US3) (FR12) (FR13)`
  - Required behavior:
    - the first Phase 2 implementation slice must stay backend-only unless proof later forces a frontend follow-on;
    - task decomposition must prefer no more than three touched files per task;
    - the default first task should stay inside `backend/app/services/structured_reviewer_service.py` and `backend/tests/test_structured_reviewer_service.py`;
    - any frontend work must be planned as a separate conditional task only after backend proof demonstrates necessity.
- State transitions `(US3) (FR14)`
  - `Draft`: PRD captures the bounded deterministic-guidance contract but has not yet absorbed audit hardening.
  - `Ready for Tasks`: PRD locks the `ERC-2026-PoC`-only service seam, fail-closed fallback rules, TDD seams, and explicit verification matrix strongly enough for atomic task planning.

## 6. Components / Modules

- Primary MVP seam
  - `backend/app/services/structured_reviewer_service.py`
  - Responsibility: own the call-scoped presentation transform from machine-oriented structured-review feedback into researcher-facing deterministic guidance for `ERC-2026-PoC`.
- Primary regression seam
  - `backend/tests/test_structured_reviewer_service.py`
  - Responsibility: prove the current question-shaped baseline, the targeted guidance rewrite, raw machine `reason` preservation, non-targeted-call safety, and fallback honesty.
- Conditional-only downstream seam
  - `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Responsibility: remain untouched for MVP unless backend proof shows the UI no longer renders the improved `feedback_text` truthfully.
- Excluded primary seams
  - `backend/app/engine/findings/evaluator.py`
  - `backend/app/engine/compat/review_card_mapper.py`
  - `backend/app/services/reviewer_service.py`
  - Responsibility: preserve current machine/audit and broader compatibility behavior; Phase 2 must not treat these as default MVP edit targets.
- Design tree (dependencies + ordering)
  - 1. Prove the current `ERC-2026-PoC` service output is still prompt-list/question-shaped. `(FR7)`
  - 2. Add the smallest deterministic guidance transform inside `StructuredReviewerService`. `(FR1) (FR2) (FR4)`
  - 3. Prove raw machine `reason` remains preserved and non-targeted calls remain unchanged. `(FR3) (FR5) (FR9) (FR10)`
  - 4. Prove fallback honesty when subordinate-prompt surfaces are unusable. `(FR6) (FR11)`
  - 5. Keep Phase 2 tasks bounded to no more than three touched files, with backend-only service plus service-test slices first. `(FR12)`
  - 6. Check whether frontend work is still unnecessary after backend proof; if yes, skip it explicitly with cited render-path evidence. `(FR5) (FR13) (FR14)`
- Deep module guidance
  - Keep the public change small: one service-level presentation transform and one existing response field (`feedback_text`) carrying improved guidance.
  - Hide rewrite heuristics inside the service seam rather than introducing new cross-layer contracts for MVP.

## 7. Edge Cases

- A targeted assessed card has subordinate-prompt text, but the transform would need to invent evidence or unsupported priorities to produce imperative guidance; the service must preserve prompt-style fallback instead. `(US1) (US3)`
- Multiple subordinate prompts resolve to duplicated or unusable text surfaces for one targeted card; the service must not manufacture sharper advice from ambiguous input. `(US1) (US3)`
- A card is not part of the approved `ERC-2026-PoC` slice; the new guidance transform must not silently affect it. `(US3)`
- The improved backend text is correct, but the existing frontend still fails to show it because of an unexpected render assumption; frontend work becomes a conditional follow-on, not implicit MVP scope. `(US1) (US3)`
- A future engineer mistakes readable guidance for a reason to drop raw machine `reason`; that change is invalid because audit traceability remains mandatory. `(US2) (US3)`

## 8. Testing Decisions (TDD)

- RED first
  - Add a failing service-level regression in `backend/tests/test_structured_reviewer_service.py` proving targeted `ERC-2026-PoC` assessed cards still emit prompt-list/question-shaped `feedback_text`. `(US1) (US3) (FR7)`
- GREEN scope
  - Add the smallest service change in `backend/app/services/structured_reviewer_service.py` needed to make targeted `ERC-2026-PoC` `feedback_text` read as deterministic revision guidance. `(US1) (US2) (FR1) (FR2) (FR4) (FR8)`
- Required regression coverage
  - Prove raw machine `reason` is still preserved after the presentation rewrite. `(FR3) (FR9)`
  - Prove non-targeted calls keep existing deterministic behavior. `(FR5) (FR10)`
  - Prove fallback honesty when subordinate-prompt surfaces are missing or unusable. `(FR6) (FR11)`
- Test seams
  - `StructuredReviewerService.generate_structured_review_pipeline_v1`
  - Internal service feedback-resolution helpers only through public service behavior
- What to mock
  - Mock only outer boundaries needed to build deterministic service fixtures; do not mock the feedback-resolution logic being changed.
- Minimal test types
  - Service-level regressions are sufficient for MVP unless backend proof shows a real downstream render mismatch that justifies one additional frontend assertion later.

## 9. Telemetry (Minimal)

- No new product telemetry is required for MVP.
- Deterministic service-test evidence is the primary proof surface for this workflow.

## 10. Deferred / Not in MVP

- Generic multi-call rollout of deterministic guidance transforms.
- Frontend copy, formatting, grouping, or card-layout changes unless backend-only proof exposes a real mismatch.
- LLM-backed synthesis, coaching, or researcher-specific narrative advice.
- Reworking evaluator, compatibility mapper, or legacy review paths to own presentation logic.

## 11. Open Questions (if any)

- none

## 12. Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Current-seam baseline proof | targeted `StructuredReviewerService` test | `fail` (default until executed) | required | must prove targeted `ERC-2026-PoC` output is still prompt-list/question-shaped before implementation |
| Narrow seam proof | service-level regression plus code review | `fail` (default until executed) | required | must prove the behavior change lives in `StructuredReviewerService`, not evaluator/mapper/frontend-first |
| Raw machine reason preservation | targeted service/assertion test | `fail` (default until executed) | required | must prove raw `reason` remains available for audit/traceability |
| Deterministic guidance proof | targeted service test for researcher-facing `feedback_text` | `fail` (default until executed) | required | must prove cards emit concise deterministic revision guidance |
| Non-targeted call regression proof | targeted service regression for unaffected calls | `fail` (default until executed) | required | must prove the transform stays bounded to `ERC-2026-PoC` |
| Fallback honesty proof | targeted service regression for unresolved/missing/unusable subordinate-prompt surfaces | `fail` (default until executed) | required | must prove the service keeps WF-0076-style prompt/fallback output when stronger guidance would require invention |
| Boundary preservation | `main...HEAD` review plus artifact citations | `fail` (default until executed) | required | must prove no widening into legacy review path, OpenAI calls, or WF-0074/75/76 contract changes |
| Optional frontend necessity check | targeted UI assertion or explicit skip rationale | `fail` (default until executed) | required | acceptable closure is an explicit skip rationale if backend `feedback_text` proof is sufficient and the page still renders it directly |
| Atomic task-slice proof | finalized Phase 2 task artifact review | `fail` (default until executed) | required | must prove the first implementation slice stays within the approved backend-only seam and each task prefers no more than three touched files |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close all blocking findings and either close or justify non-blocking findings |

- Proceed recommendation remains blocked unless every required row above is `pass`, or explicitly `skipped` with accepted rationale during review.

## 13. Changelog

- v0.1 (2026-03-13): Initial PRD from brainstorm.
- v0.2 (2026-03-13): Applied audit hardening by making the 3-file task-slice limit explicit, locking the backend-first Phase 2 seam, and tightening the conditional frontend skip rule before marking the PRD ready for Tasks.
