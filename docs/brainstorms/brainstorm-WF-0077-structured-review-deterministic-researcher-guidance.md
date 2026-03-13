<!-- docs/brainstorms/brainstorm-WF-0077-structured-review-deterministic-researcher-guidance.md -->
# WF-0077 — Structured Review Deterministic Researcher Guidance

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-13

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for scope, boundaries, and implementation direction for WF-0077.
- The Q&A transcript is rationale only; it must not become the only place where seam choice, task split, or non-goals live.
- Raw machine `reason` remains preserved for audit and traceability; this WF is only about improving researcher-facing deterministic presentation.
- WF-0074, WF-0075, and WF-0076 boundaries remain prior truth: no rework to canonical call fidelity, no rework to fail-closed engine contracts, and no regression of subordinate-prompt traceability.

## Long-Form Problem Intake

The active researcher-facing `/app` review flow is the structured path: `/app` calls `/api/bff/structured-review`, which reaches backend `/api/structured-review`, `StructuredReviewerService`, and `pipeline_v1`. That path is deterministic and does not call OpenAI today. The product issue is therefore not “the LLM is weak”; it is that the deterministic structured path currently exposes an internal evaluation scaffold rather than strong revision guidance.

WF-0076 improved this by replacing raw machine signal like `content_evaluated;subordinate_prompt_ids=...` with readable subordinate-prompt text for ERC-2026-PoC. That was the right seam for trust and readability, but it still leaves the user experience at the level of “these are the review questions.” For a researcher trying to improve proposal text, that is still not good enough. The user needs concise deterministic guidance that says what to revise, what evidence to strengthen, and what gap to close, while remaining grounded in the same evaluation criteria/elements and canonical subordinate prompts already present in the structured path.

This workflow must stay narrow. It should not add OpenAI-backed synthesis, widen into the legacy `ReviewerService` path, or move traceability logic into the UI. The smallest honest product claim is that the structured deterministic path can generate better researcher-facing revision guidance at the existing service seam without changing the core fail-closed engine contract.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Preflight Step 1)

Contract Notes / Non-obvious constraints:
- The problem is not lack of canonical source data; the relevant evaluation criteria/elements and subordinate prompts already exist.
- The problem is not lack of machine traceability; raw `reason` must remain unchanged and preserved.
- The product promise for this WF must stay bounded to deterministic guidance transformation, not researcher-specific synthesis.

## Repo Reality Snapshot (Read-Only)

- `backend/app/engine/findings/evaluator.py` emits call-agnostic machine `reason` strings such as `content_evaluated` and `content_evaluated;subordinate_prompt_ids=...`; this is traceability-oriented output, not researcher-facing guidance.
- `backend/app/engine/compat/review_card_mapper.py` rolls finding reasons into `ReviewCard.feedback` in a generic compatibility layer; changing it would widen behavior across all calls and blur machine-signal preservation with presentation.
- `backend/app/services/structured_reviewer_service.py` already owns the call-scoped presentation seam. `_resolve_feedback_text_for_card` contains both the existing WF-0069 deterministic “Revise ...” guidance path for selected calls and the WF-0076 subordinate-prompt presentation transform for ERC-2026-PoC.
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` renders `card.feedback_text` directly; frontend-only edits would only restyle text after the backend contract is already decided and would not create a stronger deterministic review artifact.
- `backend/tests/test_structured_reviewer_service.py` already contains seam-specific regression tests for WF-0069 and WF-0076, which makes the service test file the narrowest TDD entry point for this behavior change.

## Open Questions / Deferred

- Approved default for MVP remains ERC-2026-PoC only; any reusable transform beyond that call requires explicit re-approval in a later phase artifact and must not be assumed by current tasks.
- Whether any frontend copy or grouping change is needed after backend guidance text improves, or whether improved `feedback_text` alone is sufficient for MVP.
- Whether later LLM-backed synthesis should consume these deterministic guidance primitives as inputs, which is explicitly deferred to a separate WF.

## 1. Problem Statement

- The structured review path currently produces readable but still question-shaped output, so the researcher sees reviewer concerns more than revision guidance.
- The primary actor is a researcher revising proposal text in `/app`; the maintainer-facing requirement is to improve that experience without adding non-deterministic synthesis.
- The narrow defect is presentation-contract weakness at the structured-review seam, not engine failure, not missing source fidelity, and not frontend rendering absence.
- The adversarial reading of current seams is:
  - evaluator is too low-level because it must keep machine `reason` stable for audit;
  - compatibility mapper is too broad because it is cross-call and reason-centric;
  - frontend is too late because it only formats already-chosen text;
  - structured-review service is the narrowest safe place because it already converts machine feedback into user-facing feedback for bounded call slices.
- This WF fails if it produces nicer-looking text that is no more actionable than the current prompt list.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Section 1)

Contract Notes / Non-obvious constraints:
- “Researcher-facing” here means revision guidance grounded in evaluation criteria/elements, not generic writing advice.
- The target artifact is still deterministic backend output, not a client-side rewrite.
- Audit traceability remains anchored in raw machine `reason`, not in the user-facing rewrite.

## 2. Desired Outcome

- Researchers should receive concise deterministic guidance that reads like “Revise this section to clarify X, strengthen evidence for Y, and address Z.”
- The guidance must stay grounded in the existing expectation, evaluation element, and canonical subordinate-prompt data already available to the structured path.
- The first implementation should prefer a deterministic transform that turns ERC-2026-PoC subordinate-prompt/question surfaces into imperative revision guidance, without inventing new semantics beyond what the structured path already knows.
- Success is defined by a behavior change at the service seam, proven with TDD, where assessed ERC-2026-PoC cards on the structured path contain actionable revision guidance instead of raw machine text or raw question lists.
- Raw machine `reason` storage, fail-closed behavior, and existing engine contracts remain unchanged.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Section 2)

## 3. Target User / Actor

- Primary user: researchers using the current `/app` structured review flow to improve proposal text.
- Secondary actor: maintainers protecting traceability, deterministic behavior, and bounded rollout.
- This WF is not primarily for internal admins, prompt engineers, or legacy OpenAI review users.
- The user’s current pain is that they must infer revision actions from reviewer questions; the desired change is for the product to state the revision action directly.
- The maintainer’s acceptance bar is higher than readability; the guidance must remain deterministic, testable, and source-grounded.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Section 3)

## 4. Rough Idea (Unstructured Thinking)

- Reuse the existing presentation seam in `StructuredReviewerService._resolve_feedback_text_for_card` and add a narrower deterministic guidance builder for the structured researcher-facing path.
- Prefer a transform that consumes the already-resolved evaluation element label plus canonical subordinate prompt text and emits short imperative guidance bullets or sentences.
- Do not move this logic into evaluator or mapper because those layers currently carry machine-oriented semantics used for compatibility and audit.
- Do not begin with frontend-only rewriting because that would create implicit presentation rules outside the backend review contract and would be harder to verify against audit invariants.
- Smallest safe new WF/task split recommendation:
  - Task 1: RED test at the service seam proving the targeted structured path still emits prompt-list/question-shaped guidance for ERC-2026-PoC.
  - Task 2: GREEN implementation in `StructuredReviewerService` plus the same service test file to transform prompt-list output into deterministic revision guidance while preserving raw machine `reason`.
  - Task 3: Only if needed after Task 2, add a narrow frontend assertion/update for label or formatting behavior; otherwise stop without frontend changes.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Section 4)

Contract Notes / Non-obvious constraints:
- Keep the initial implementation bounded to no more than three touched files in a task slice.
- Prefer backend-only MVP unless a frontend mismatch is proven.
- The deterministic guidance builder should be additive to existing seam logic, not a rewrite of pipeline semantics.
- If canonical subordinate-prompt text is missing, unresolved, duplicated into an unusable surface, or otherwise too weak to support an imperative rewrite without invention, the service must preserve the existing WF-0076 prompt rendering/fallback behavior instead of fabricating stronger guidance.

## 5. Constraints

- No OpenAI or other LLM call in this WF.
- Preserve raw machine `reason` for audit and traceability.
- Preserve fail-closed behavior and WF-0074/WF-0075/WF-0076 boundaries.
- Use researcher-facing terminology of evaluation criteria/elements, never “rubric.”
- For behavior change, use TDD: write the failing regression first, then implement the smallest backend seam change, then refactor only if needed.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Section 5)

## 6. Risks / Unknowns

- Guidance text could become deterministic but still too generic, producing cosmetically improved output that does not materially help revision.
- A mapper-level or evaluator-level implementation would create hidden coupling across unrelated calls and risk breaking traceability assumptions.
- A frontend-only implementation would create presentation drift where exported/contracted feedback remains weak while the UI looks better.
- Attempting to make this WF reusable for all structured calls immediately could exceed the evidence available from the current seams and violate the bounded-scope requirement.
- Future LLM synthesis work could be conflated with this WF unless the deterministic output contract and proof standard are stated separately now.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Section 6)

## 7. MVP Definition

- If limited to 2–3 days, MVP is one deterministic backend guidance transform on the structured service seam for the targeted structured path, backed by seam-specific regression tests.
- The minimum acceptable product effect is that targeted assessed cards no longer read as raw subordinate-prompt lists/questions and instead read as concise revision guidance tied to the relevant evaluation element.
- The first safe TDD seam is `backend/tests/test_structured_reviewer_service.py`, with implementation in `backend/app/services/structured_reviewer_service.py`, targeting ERC-2026-PoC first.
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` should stay out of MVP unless a verified formatting or wording issue remains after the backend contract improves.
- MVP must also prove that non-targeted calls keep their current deterministic behavior, so this WF does not silently widen beyond the approved ERC-2026-PoC slice.
- MVP must prove deterministic fallback behavior for unresolved or unusable subordinate-prompt surfaces so the service never replaces known WF-0076 traceability output with invented researcher guidance.
- This should be a separate WF from future LLM synthesis because deterministic guidance transformation and synthesized coaching have different dependencies, risk, verification methods, and rollback boundaries.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0077-structured-review-deterministic-researcher-guidance.md` (Section 7)

## Verification / Proceed Gate

- No proceed recommendation is valid if raw machine `reason` is mutated, suppressed, or repurposed as the only source of user-facing guidance.
- No proceed recommendation is valid if the chosen seam moves presentation logic into evaluator or compatibility mapper and thereby widens call-agnostic behavior without new approval.
- No proceed recommendation is valid if the behavior change is proven only with UI snapshots and not with a backend TDD regression at the service seam.
- No proceed recommendation is valid if the output still reads mainly as evaluation questions instead of revision guidance.
- No proceed recommendation is valid if the WF implicitly pulls in OpenAI-backed synthesis, legacy review-path changes, or broader prompt-engine redesign.

### Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Current-seam baseline proof | targeted `StructuredReviewerService` test | `fail` (default until executed) | required | must prove the targeted structured path still emits prompt-list/question-shaped feedback before implementation |
| Narrow seam proof | service-level regression plus code review | `fail` (default until executed) | required | must prove the change lives in the structured-review presentation seam rather than evaluator/mapper/frontend-first |
| Raw machine reason preservation | targeted service/assertion test | `fail` (default until executed) | required | must prove raw `reason` remains available for audit/traceability |
| Deterministic guidance proof | targeted service test for researcher-facing `feedback_text` | `fail` (default until executed) | required | must prove cards emit concise deterministic revision guidance |
| Non-targeted call regression proof | targeted service regression for unaffected calls | `fail` (default until executed) | required | must prove the new guidance transform stays bounded to the approved ERC-2026-PoC slice unless Phase 1 re-approves widening |
| Fallback honesty proof | targeted service regression for unresolved/missing subordinate-prompt surfaces | `fail` (default until executed) | required | must prove the service keeps WF-0076-style prompt/fallback output when deterministic guidance would otherwise require invention |
| Boundary preservation | `main...HEAD` review plus artifact citations | `fail` (default until executed) | required | must prove no widening into legacy review path, OpenAI calls, or WF-0074/75/76 contract changes |
| Optional frontend necessity check | targeted UI assertion or explicit skip rationale | `fail` (default until executed) | required | default acceptable closure is an explicit skip rationale if backend `feedback_text` proof is sufficient and `frontend/src/app/app/reviews/[reviewId]/page.tsx` still renders `card.feedback_text` directly without extra transform |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close all blocking findings and either close or justify non-blocking findings |

## 8. Explicit Non-Goals

- Adding OpenAI or any other LLM synthesis to structured reviews.
- Widening scope into `ReviewerService` or the legacy review path.
- Changing engine evaluator semantics, compatibility-mapper contracts, or raw machine-signal storage.
- Re-solving canonical call fidelity, subordinate-prompt runtime carriage, or fail-closed boundaries already handled in WF-0074, WF-0075, and WF-0076.
- Repositioning the UI through frontend-only prose rewriting if the backend contract can solve the problem directly.

## Changelog

- v0.1 (2026-03-13): Minted WF-0077, anchored the problem to the active structured-review path, completed an adversarial seam review, selected `StructuredReviewerService` as the narrowest deterministic guidance seam, and separated this deterministic guidance contract from any later LLM-synthesis workflow.
- v0.2 (2026-03-13): Tightened MVP proof to ERC-2026-PoC as the first approved slice and added an explicit non-targeted-call regression requirement so the seam cannot silently widen.
- v0.3 (2026-03-13): Closed review-gate gaps by making ERC-2026-PoC-only MVP scope explicit, requiring deterministic fallback-honesty proof for unresolved subordinate prompts, and clarifying when frontend work may be skipped.
