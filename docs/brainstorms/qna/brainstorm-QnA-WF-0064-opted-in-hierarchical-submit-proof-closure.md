<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0064-opted-in-hierarchical-submit-proof-closure.md -->
# WF-0064 — Opted-In Hierarchical Submit Proof Closure

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

## Kickoff Context (User Narrative)

- User requested a new WF for the real remaining universal hierarchical submit gap.
- User explicitly rejected the framing "build nested support from scratch."
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
