<!-- docs/brainstorms/brainstorm-WF-0081-atomic-findings-structured-review.md -->
# WF-0081 — Atomic Findings Structured Review

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-14

Type: feature

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0081-atomic-findings-structured-review.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for scope, boundaries, and implementation direction for WF-0081.
- The helper plan at `docs/plans/plan-WF-0081-v0.1.md` is intent input only; canonical decisions must live here.
- The current engine already produces atomic diagnostic findings before collapsing them into `ReviewCard`; this workflow re-exposes that truth to persistence/API/frontend rather than inventing a new evaluation engine.
- Legacy reviews must continue to read and render from `ReviewCard`.
- New structured reviews in scope for WF-0081 must read and render from `findings` grouped under reviewed nodes.
- Researcher-facing terminology must remain `evaluation criteria` / `evaluation elements`.

## Long-Form Problem Intake

The current structured-review product surface still centers on persisted `ReviewCard` output. That compatibility surface works for legacy review rendering, but it compresses too much structure for the newer structured-review path. A single card can hide multiple evaluation-element issues, flatten the evidence basis, and obscure which evaluation element actually triggered the guidance. It also makes positive pass states less visible because the card model optimizes for rolled-up feedback rather than atomic evaluation-element traceability.

Repo history already tells us the engine truth is more granular. WF-0038 locked `DiagnosticFinding v1` as engine SSOT, with `DiagnosticFinding v1 -> ReviewCard` as a compatibility adapter. The current engine therefore already produces diagnostic findings before they are collapsed into `ReviewCard`. WF-0081 should treat that as the main reality anchor: we are not trying to replace the review engine first. We are trying to promote atomic findings to a first-class persisted and researcher-visible structured-review detail surface.

This must not be treated as a UI-only redesign. To make the output truthful and durable, the workflow has to plan the full path: persistence/model changes, review-generation output changes, review-detail API changes, frontend rendering, and a compatibility strategy that keeps legacy `ReviewCard` reviews stable while allowing new reviews to return a reviewed-node-plus-findings detail shape.

## Repo Reality Snapshot (Read-Only)

- `pipeline_v1` and the findings/evaluator path already produce diagnostic findings before the compatibility mapper collapses them into persisted/user-visible `ReviewCard` rows.
- The current structured-review persistence and detail surfaces still center on `ReviewCard`, `ReviewCardSummary`, and review-detail card arrays.
- Existing structured-review UX groups cards by reviewed section/node, which is a useful bridge for WF-0081 because the new shape should stay grouped by reviewed nodes rather than becoming a flat cross-review findings list.
- Existing structured review semantics already distinguish `ASSESSED` and `NOT_ASSESSABLE`; WF-0081 must preserve those semantics and add an explicit positive `REQUIREMENTS_MET` state for the new findings-based path.
- Existing subordinate prompts and deterministic guidance already provide grounding context that can be reused when generating element-level actionable findings.

## 1. Problem Statement

- `ReviewCard` is too coarse to serve as the primary output unit for new structured reviews that need evaluation-element-level traceability.
- Researchers need each visible finding to anchor to one reviewed node and one evaluation element, with clear issue summary, evidence basis, and actionable guidance.
- The current pipeline already has finer-grained findings internally, but the persisted/API/frontend contract still collapses them before researchers can see them.
- A truthful rollout therefore requires an end-to-end contract change, not just a render change.
- Backward compatibility is mandatory: legacy reviews keep the current `ReviewCard` contract; only new atomic-flow reviews adopt the `findings`-based detail shape.

## 2. Desired Outcome

- New structured reviews expose a first-class `ReviewFinding` persistence contract anchored to one proposal node and one evaluation element.
- New review detail responses return `reviewed_nodes[]`, each with `findings[]`, so the researcher reads feedback in section context.
- Each finding carries explicit fields for severity, assessment status, issue summary, evidence basis, and actionable feedback instead of one collapsed `feedback_text` blob.
- A reviewed node with no issues can still surface a positive `REQUIREMENTS_MET` state explicitly rather than disappearing into silence.
- Legacy reviews continue to read/render through `ReviewCard` without migration-driven breakage.

## 3. Target User / Actor

- The primary user is a researcher reading structured review output to improve proposal text against evaluation criteria and evaluation elements.
- The maintainer/operator is a secondary actor who needs durable persistence and API contracts that truthfully represent what the engine produced.
- The frontend consumer needs a dual-path render contract: legacy `cards[]` for old reviews and `reviewed_nodes[].findings[]` for new atomic reviews.

## 4. Rough Idea (Unstructured Thinking)

- Persist a new `ReviewFinding` model for atomic findings rather than widening `ReviewCard` until it becomes a hidden second findings table.
- Keep `ReviewCard` as a compatibility surface for legacy reviews and possibly legacy reads only; do not require backfill of existing reviews into `ReviewFinding`.
- Generate new findings output from existing diagnostic finding flow plus bounded new synthesis/persistence behavior where the current collapse to `ReviewCard` loses researcher-visible structure.
- Expose one dual-mode review-detail response that can safely carry either legacy cards or reviewed-node findings without forcing all clients to migrate at once.
- Render new reviews as section-grouped finding lists, with explicit positive states when requirements are met.

## 5. Constraints

- WF-0081 is a new workflow and must not be treated as an extension of the shipped WF-0080 launch wedge.
- The workflow must plan backend, persistence, API, and frontend changes together.
- The implementation plan must respect the repo’s atomic-task discipline, with sequential slices that prefer touching no more than three files each.
- Python slices in later phases must use the `python-best-practices` skill.
- Researcher-facing copy must use `evaluation criteria/elements`, not `rubric`.

## 6. Key Risks / Unknowns

- The largest hidden-coupling risk is introducing `ReviewFinding` without a clean review-generation ownership seam, which could create duplicate truths between findings and cards.
- A second risk is overrelying on current in-memory diagnostic findings without proving which fields are already stable enough to persist directly versus which must be regenerated or synthesized.
- A third risk is contract drift in the review-detail API if the dual legacy/new shape is not explicit and version-safe.
- A fourth risk is frontend overreach: if the page assumes all reviews are findings-based, legacy review detail could break.
- A fifth risk is scope creep into engine redesign. WF-0081 should consume existing engine findings truth where possible, not reopen engine semantics wholesale.

## 7. MVP Definition

- Must ship in WF-0081:
  - persisted `ReviewFinding` model and migration strategy for new atomic reviews;
  - review-generation/output path that creates atomic findings for new structured reviews;
  - review-detail API shape for `reviewed_nodes[].findings[]`;
  - frontend rendering for findings grouped under reviewed nodes;
  - explicit compatibility behavior for legacy `ReviewCard` reviews;
  - explicit statement of what derives from existing diagnostic findings versus what requires new persistence/generation behavior.
- Deferred after WF-0081:
  - backfilling historical legacy reviews into `ReviewFinding`;
  - removing `ReviewCard` entirely;
  - redesigning review history/list surfaces beyond what is required for honest detail rendering;
  - generalized cross-surface export/reporting changes unless Phase 1/2 prove they are required for truthful launch of this contract.

## 8. Smallest Implementation Slices

- Slice 1 — Persistence/model seam:
  - Add `ReviewFinding` persistence contract and the minimum review linkage/snapshot fields needed for historical renderability.
  - Keep legacy `ReviewCard` storage untouched for old reviews.
- Slice 2 — Backend generation/output seam:
  - Create new findings write-path behavior for new structured reviews, reusing existing diagnostic findings where possible and adding only the missing issue/evidence/actionable persistence mapping.
- Slice 3 — Review-detail API seam:
  - Add a dual-path detail response that returns either legacy cards or findings grouped by reviewed node for atomic reviews.
- Slice 4 — Frontend rendering seam:
  - Render findings-based review detail grouped by reviewed nodes while preserving legacy `ReviewCard` rendering.
- Slice 5 — Compatibility/migration seam:
  - Gate new reviews onto the findings-based path without forcing legacy backfill; keep explicit fallback behavior and mixed-data safety.

## 9. Derived vs New Behavior

- Can derive from existing pipeline findings:
  - proposal-node anchoring already present in diagnostic finding flow;
  - evaluation-element grounding and subordinate-prompt context already available in the current engine/call definition path;
  - severity/assessment semantics already partly present through findings plus current `ReviewCard` status/rating behavior;
  - the architectural fact that engine truth exists before `ReviewCard` collapse.
- Requires new generation/persistence behavior:
  - durable `ReviewFinding` storage;
  - explicit persisted `issue_summary`, `evidence_basis`, and `actionable_feedback` fields;
  - explicit `REQUIREMENTS_MET` positive-state persistence/response behavior;
  - dual-shape review-detail API contract and frontend consumer support;
  - migration/gating rules deciding which reviews remain legacy-card reads versus new findings-based reads.

## 10. Explicit Non-Goals

- Replacing engine SSOT or redesigning `pipeline_v1` from scratch.
- Breaking or rewriting legacy `ReviewCard` review reads.
- Treating the problem as a frontend-only refactor.
- Reopening WF-0080 launch-wedge scope or coupling this workflow to a single-call launch wedge.

## 11. Verification / Proceed Gate

- No Phase 1 recommendation is valid unless the PRD keeps legacy `ReviewCard` compatibility explicit and names one canonical owner for new `ReviewFinding` writes.
- No implementation-ready plan is valid unless the task file splits work into sequential slices that prefer touching no more than three files each.
- No ship recommendation is valid unless the implementation proves both paths work: legacy `ReviewCard` reads still render and new findings-based reviews render grouped under reviewed nodes.

## Changelog

- v0.1 (2026-03-14): Created the canonical Phase 0 brainstorm for WF-0081, locking the new workflow around evaluation-element-level atomic findings with legacy `ReviewCard` compatibility.
