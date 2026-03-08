<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0064-opted-in-hierarchical-submit-proof-closure.md -->
# WF-0064 — Opted-In Hierarchical Submit Proof Closure

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

## Kickoff Context (User Narrative)

- User requested a new WF for the real remaining universal hierarchical submit gap.
- User explicitly rejected the framing "build nested support from scratch."
- User provided the free-form narrative problem statement directly in the kickoff message rather than as a separate follow-up answer.
- User required the audit to determine:
  - what is already working for opted-in hierarchical universal submit,
  - what is still broken,
  - and what is the smallest WF that makes one real hierarchical proof path defensible end-to-end.
- User anchored the audit on:
  - `frontend/src/lib/submit/renderModel.ts`
  - `frontend/src/components/submit/UniversalSubmitForm.tsx`
  - `backend/tests/test_api.py`
  - `docs/parking_lot.md`
  - `docs/logs/decisions.md` for WF-0060 to WF-0063
  - `docs/memory/tools/frontend.md`

## Preflight Repo Reality Snapshot

- `renderModel.ts` now allows opted-in hierarchical rendering via `splitVisibilityReviewabilityEnabled`; the old universal nested hard-block is no longer the main state of the repo.
- `UniversalSubmitForm.tsx` renders supporting nodes for opted-in calls, but both compliance and submit payload builders filter to `PRIMARY` nodes only.
- `backend/main.py` rejects supporting nodes on the primary review path for both compliance and structured review endpoints.
- WF-0063 tests prove the split-role MSCA path is wired, but they also prove `supporting_context_node_logical_ids` stays empty and review detail still labels supporting context as none.
- `ReviewDetailPage` derives coverage labels from `has_expectations` leaves, which hides supporting nodes from the coverage summary.

## Preflight Conclusions

- Proof call already present in repo: `MSCA-PF-2025`.
- Old backlog wording about removing the nested-node renderer block is stale.
- The remaining gap is a false-affordance/product-contract issue, not a missing hierarchy renderer.

## Section 1 Decision Batch

**Q1: What is the primary defect WF-0064 should claim?**
- A) False affordance: supporting nodes look like normal editable submit inputs even though they are not part of the primary review path.
- B) Missing persistence: supporting-node text should already be treated as real review context and saved.
- C) Mixed defect: both the false affordance and missing persistence must be fixed in the same WF.
  > Recommendation: A. This matches the audited repo state and keeps the WF narrow. B and C may become valid future directions, but they widen the contract into supporting-context persistence before the repo has chosen those semantics explicitly.
  > **Selected: A** (assistant recommendation approved by user for this and the rest of Phase 0).

**Q2: For the primary review path in this WF, what should happen to supporting nodes in the submit form?**
- A) Keep them visible but make them non-editable/read-only with explicit copy.
- B) Keep them editable and add explicit persistence as non-reviewed supporting context.
- C) Hide them again from the form until context semantics are built.
  > Recommendation: A. It preserves WF-0063 structural visibility while closing the current silent-drop trap. B broadens persistence semantics; C reintroduces structural incompleteness.
  > **Selected: A**.

**Q3: What should count as the one proof call for WF-0064?**
- A) `MSCA-PF-2025` only.
- B) `MSCA-PF-2025` plus one ERC path.
- C) Any opted-in call that currently passes parity tests.
  > Recommendation: A. `MSCA-PF-2025` is the explicit split-role proof call already grounded by WF-0063. Broader proof targets create avoidable scope spread.
  > **Selected: A**.

**Q4: What should review detail communicate for visible supporting nodes after this WF?**
- A) They should appear as visible but not part of this review, with no claim they were used as context.
- B) They should appear under supporting context even if no supporting payload was persisted.
- C) Review detail does not need to change if submit UI is corrected.
  > Recommendation: A. It is the most truthful label if supporting content still does not cross the request boundary in MVP. B would overclaim; C would leave a misleading coverage surface.
  > **Selected: A**.

**Q5: What is the maximum acceptable implementation scope for WF-0064?**
- A) UI affordance/copy + review-detail labeling/coverage fixes + tests, while keeping backend primary-only semantics.
- B) Add backend persistence for supporting-node drafts on the review record in the same WF.
- C) Full supporting-context contract across submit, persistence, prompt/runtime, and review detail.
  > Recommendation: A. This is the smallest defensible end-to-end closure for one real proof path. B and C are plausible future work but exceed the requested narrow WF.
  > **Selected: A**.
