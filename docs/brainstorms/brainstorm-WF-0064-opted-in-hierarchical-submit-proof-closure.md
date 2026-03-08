<!-- docs/brainstorms/brainstorm-WF-0064-opted-in-hierarchical-submit-proof-closure.md -->
# WF-0064 — Opted-In Hierarchical Submit Proof Closure

Artifact: brainstorm
Version: v0.1
Status: Draft
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

## 3. Target User / Actor

- Primary actor: a researcher using universal submit on an opted-in hierarchical call.
- Proof actor: the existing `MSCA-PF-2025` split-visibility path, because it is the only current repo proof call explicitly opted into the WF-0063 contract.
- Secondary actor: maintainers relying on backlog/docs to understand what remains broken after WF-0063.

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

## 6. Risks / Unknowns

- The current UI may be creating silent data loss for supporting-node text on successful submit.
- A docs-only rewrite would leave the product defect intact and make the repo claim more than the user flow actually supports.
- A persistence-heavy fix could broaden into the deferred supporting-context semantics work if the boundary is not kept narrow.
- Review-detail coverage may remain misleading even after submit-path changes if supporting nodes stay absent from coverage labeling.

## Open Questions / Deferred

- Whether supporting-node text should persist onto the review record in MVP, or whether the smaller fix is to make supporting nodes non-editable in the primary path.
- Whether `supporting_context_node_logical_ids` should remain empty in this WF or become a first-class persisted boundary for the proof path.
- Whether MSCA conditional sections need special handling in the proof slice beyond the current visible-role path.

## 7. MVP Definition

- Smallest functional slice:
  - use `MSCA-PF-2025` as the proof call,
  - remove the false-affordance or false-persistence defect on supporting nodes,
  - keep primary review submission semantics explicit and tested,
  - make review detail and user-facing copy accurately reflect what happened to visible hierarchical nodes.
- This WF succeeds only if one researcher-facing hierarchical path is defensible end-to-end, not merely renderable.

## 8. Explicit Non-Goals

- Generalized support for all hierarchical calls.
- Broad supporting-context engine semantics across calls.
- New scored review behavior for supporting nodes.
- Multi-call migration or broad refactors not directly required for the MSCA proof path.
