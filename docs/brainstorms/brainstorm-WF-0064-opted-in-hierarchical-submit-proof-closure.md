<!-- docs/brainstorms/brainstorm-WF-0064-opted-in-hierarchical-submit-proof-closure.md -->
# WF-0064 — Opted-In Hierarchical Submit Proof Closure

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-08

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0064-opted-in-hierarchical-submit-proof-closure.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts and scope decisions in WF-0064.
- The Q&A transcript is rationale only; it must not introduce new contracts.
- If later Q&A changes scope or contract claims, promote the change here and log it in `docs/logs/decisions.md`.

---

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0064-opted-in-hierarchical-submit-proof-closure.md` (Kickoff + Preflight)

- The old backlog framing is stale: the renderer no longer universally hard-blocks hierarchical calls.
- Opted-in hierarchical calls already render through the split visibility/reviewability path, with structural containers hidden from editability and `PRIMARY`/`SUPPORTING` nodes distinguished.
- The remaining real gap is end-to-end proof integrity for one opted-in hierarchical path: supporting nodes are editable in the submit UI, but current compliance and submit payloads intentionally drop them, the backend rejects them on the primary path, successful submit clears the entire draft, and review detail reports `Supporting context: None`.
- That means the MSCA proof path is structurally visible but not yet defensible as a user flow if a researcher enters text into supporting sections.

Contract Notes / Non-obvious constraints:

- This WF is not "build nested support from scratch"; it starts from the already-landed split-path contract. See WF-0063 decisions and parity tests.
- The remaining defect is not just frontend rendering. It is a product/contract/UX mismatch across submit UI, request boundary, persistence semantics, and review detail.

## 2. Desired Outcome

- One real opted-in hierarchical call already in the repo is defensible end-to-end.
- A researcher should not be invited to enter text that silently disappears or is misrepresented after submit.
- The product contract should state clearly whether supporting nodes are read-only structure/context in this path, separately persisted as non-reviewed context, or intentionally excluded with explicit UX and no data-loss trap.
- Backlog framing should describe the real remaining gap accurately so future work does not restart from the removed nested-node blocker.

Section 2 decisions:

- Success is one proof path that is honest and safe for users, not a broader capability claim.
- The preferred MVP outcome is fail-closed UX on the current primary-review path rather than adding supporting-context persistence by default.
- Review detail should say visible supporting nodes were not part of the review unless the WF explicitly persists and traces them.

## 3. Target User / Actor

- Primary actor: a researcher using universal submit on an opted-in hierarchical call.
- Proof actor: the existing `MSCA-PF-2025` split-visibility path, because it is the only current repo proof call explicitly opted into the WF-0063 contract.
- Secondary actor: maintainers relying on backlog/docs to understand what remains broken after WF-0063.

Section 3 decisions:

- The workflow optimizes for researcher-facing truthfulness first.
- The proof call is locked to `MSCA-PF-2025` only.
- Maintainers are a secondary audience through clearer backlog and workflow artifacts, not an excuse to make this docs-only.

## 4. Rough Idea (Unstructured Thinking)

## Repo Reality Snapshot (Read-Only)

- `frontend/src/lib/submit/renderModel.ts` no longer universally rejects nested calls. It rejects nested calls only when split visibility is disabled and the legacy path sees nested editable nodes without structural-container semantics.
- `frontend/src/components/submit/UniversalSubmitForm.tsx` renders supporting nodes for opted-in calls, but `buildNodesPayload()` and compliance payload generation include only stage-eligible `PRIMARY` nodes.
- `backend/main.py` explicitly rejects supporting nodes on both `/api/check-compliance` and `/api/structured-review` for the primary path.
- `backend/tests/test_api.py` and frontend tests already prove WF-0063 parity for `MSCA-PF-2025`, but that proof currently ends at "supporting nodes stay visible while primary path remains primary-only," not "supporting-node user input is handled defensibly."
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` currently builds coverage labels from `has_expectations` leaves, so supporting nodes such as `abstract` are omitted from coverage summary even when they were visible in the submit UI.

Open questions suggested by repo snapshot:

- Should supporting nodes remain editable in this primary review path if the platform still refuses to submit or persist them?
- If supporting drafts remain editable, what is the smallest safe persistence boundary that prevents silent data loss without broadening review semantics?
- Should review detail surface visible supporting nodes as "not part of this review" even when no supporting context is persisted?
- Is the minimum defensible fix UI-only (fail-closed affordance correction) or does it require persistence plus review-detail contract updates?

## 5. Constraints

- Keep scope to one real proof call and the smallest end-to-end fix for that path.
- Do not broaden into generic multi-call hardening, extraction work, or a general supporting-context engine.
- Preserve the WF-0063 primary-path contract unless this WF explicitly changes it with tests and decision logging.
- Do not treat this as docs-only unless current code/tests prove the path is already defensible; current audit says they do not.
- Preserve current backend `/api/check-compliance` and `/api/structured-review` primary-path rejection semantics for supporting nodes, including their fail-closed request-boundary posture, unless this workflow explicitly re-contracts them.
- Preserve existing idempotency and primary review persistence semantics unless a narrower explicit change is proven necessary.
- Treat supporting-node persistence as a fallback only if the read-only/non-editable proof-path fix is proven insufficient during planning; it is not an equal default direction for MVP.
- Keep implementation proof-path-local to `MSCA-PF-2025`; do not introduce generic multi-call supporting-context infrastructure in this workflow.

Section 5 decisions:

- Maximum intended scope is submit-form affordance/copy plus review-detail coverage/label honesty plus bounded tests.
- Backend persistence expansion for supporting nodes is explicitly not the default plan for MVP.

## 6. Risks / Unknowns

- The current UI may be creating silent data loss for supporting-node text on successful submit.
- A docs-only rewrite would leave the product defect intact and make the repo claim more than the user flow actually supports.
- A persistence-heavy fix could broaden into the deferred supporting-context semantics work if the boundary is not kept narrow.
- Review-detail coverage may remain misleading even after submit-path changes if supporting nodes stay absent from coverage labeling.

Section 6 decisions:

- Primary fail-closed assumption: if the UI cannot safely persist supporting-node text in this WF, it should stop collecting it on the proof path.
- The main unknown to validate in planning is whether review-detail honesty can be fixed without introducing a new persisted supporting-context field.
- Successful primary review submission must not clear any supporting-node draft state unless the UI no longer allows editing it or the workflow explicitly persists that data by contract.

## Open Questions / Deferred

- Whether supporting-node text should persist onto the review record in MVP, or whether the smaller fix is to make supporting nodes non-editable in the primary path.
- Whether `supporting_context_node_logical_ids` should remain empty in this WF or become a first-class persisted boundary for the proof path.
- Whether MSCA conditional sections need special handling in the proof slice beyond the current visible-role path.
- Exact UI wording for non-editable supporting nodes and the exact review-detail wording for visible-but-not-reviewed supporting sections. Deferred to Phase 1.
- Whether review detail should list all visible supporting nodes or only the subset relevant to the selected review stage. Deferred to Phase 1.

## 7. MVP Definition

- Smallest functional slice:
  - use `MSCA-PF-2025` as the proof call,
  - remove the false-affordance or false-persistence defect on supporting nodes,
  - keep primary review submission semantics explicit and tested,
  - make review detail and user-facing copy accurately reflect what happened to visible hierarchical nodes.
- This WF succeeds only if one researcher-facing hierarchical path is defensible end-to-end, not merely renderable.

Section 7 decisions:

- Recommended MVP path: keep supporting nodes visible but non-editable in the primary path, and make review detail classify them as visible but not part of this review unless explicitly persisted later.
- Verification must prove:
  - supporting nodes are no longer silently collected then discarded,
  - primary-only submit/compliance semantics still hold,
  - review detail no longer implies invisible or missing coverage semantics for stage-eligible visible supporting nodes on the proof call,
  - proof-call behavior remains reversible through the existing opt-in seam and non-opted-in calls do not change behavior.

## 8. Explicit Non-Goals

- Generalized support for all hierarchical calls.
- Broad supporting-context engine semantics across calls.
- New scored review behavior for supporting nodes.
- Multi-call migration or broad refactors not directly required for the MSCA proof path.
- Re-contracting idempotency or review-create persistence for the general structured-review surface.
