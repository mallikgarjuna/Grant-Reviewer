<!-- docs/walkthroughs/walkthrough-WF-0079-researcher-visible-carry-through-mvp.md -->
# WF-0079 — Researcher-Visible Carry-Through MVP

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-14

Type: feature

## Summary

WF-0079 is closed as the narrow researcher-visible carry-through for `ERC-2026-PoC`.
Deterministic `feedback_text` remains the primary persisted and exported surface.
One nullable additive field, `synthesized_companion_text`, now carries accepted same-card companion guidance from storage through backend detail, BFF, and `/app/reviews/[reviewId]` rendering without changing review history/list surfaces.

## Commit Range

- Baseline SHA: `5a2d9c41456043e64b80119d515fa7f66749a2f3` (`main`)
- Head SHA: `62a852bdbbcd775e9c641742bdaf3a261df1ae72` (pre-hardening audit head)
- Branch diff: `main...HEAD`

## What Changed

- Added nullable `ReviewCard.synthesized_companion_text` storage plus migration coverage for legacy-null rows.
- Persisted accepted additive companion text only for in-scope `ERC-2026-PoC` cards while leaving deterministic `feedback_text` unchanged and non-targeted calls/cards null.
- Carried the optional field through `GET /reviews/{review_id}` and the review-detail BFF/type boundary without renaming or synthesizing extra public state.
- Rendered additive companion guidance on `/app/reviews/[reviewId]` only when present.
- Kept page-local copy/download deterministic-only and labeled those actions accordingly.

## Part B Audit Findings

- Blocking: `backend/app/services/structured_reviewer_service.py` widened persisted card payloads to six values at runtime but left local tuple annotations on the old five-value shape. `mypy` failed and the service contract drifted from `ReviewRepository.create_review_cards_batch(...)`.
- Blocking: this walkthrough remained a placeholder (`v0.0`, `Not started`) even though Phase 3 implementation commits existed, so Task 6's required closure artifact and fail-closed evidence surface were still missing.
- Non-blocking: `docs/index.md` still showed WF-0079 as `Phase 2 (Ready)`, which no longer matched the implemented branch state and made closure status non-auditable.

## Part C Revisions

- Fixed the persisted card payload typing in `backend/app/services/structured_reviewer_service.py` and guarded `element_logical_id` before using it in synthesis-context lookup so the static contract matches runtime behavior.
- Replaced the walkthrough placeholder with this closure artifact and recorded the audit outcome plus replayable verification evidence.
- Updated the WF registry status in `docs/index.md` to match the completed Phase 3 state on this branch.

## Verification

- `cd backend && ./scripts/verify_tests_postgres.sh tests/test_api.py -k 'wf0079_contract_review_card_storage_allows_null_companion_text or wf0079_contract_migration_preserves_legacy_null_companion_text or wf0079_contract_review_detail_response_carries_optional_companion_text or wf0079_contract_review_detail_response_supports_mixed_card_companion_states'` -> `4 passed, 149 deselected`
- `cd backend && ./scripts/verify_tests_postgres.sh tests/test_structured_reviewer_service.py -k 'wf0079_contract_erc_poc_persists_accepted_companion_text or wf0079_contract_non_targeted_calls_do_not_persist_companion_text'` -> pass
- `cd backend && uv run mypy app/services/structured_reviewer_service.py app/models/domain.py app/schemas/api.py main.py` -> pass after hardening fix
- `cd backend && uv run ruff check app/services/structured_reviewer_service.py app/models/domain.py app/schemas/api.py main.py` -> pass after import-order fix
- `cd frontend && npx vitest run 'src/app/api/bff/reviews/[reviewId]/route.test.ts' 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0079_bff_review_detail_preserves_optional_companion_text|wf0079_review_detail_renders_optional_companion_block|wf0079_review_detail_copy_and_download_remain_deterministic_only|wf0079_review_detail_legacy_and_mixed_cards_hide_empty_companion_shells'` -> `4 passed`
- `git diff --name-only main...HEAD -- 'frontend/src/app/app/reviews/page.tsx' 'frontend/src/app/api/bff/reviews/route.ts'` -> no output

## Outcome

- Blocking issues remaining: none
- Non-blocking deltas remaining: none known on the implemented Phase 3 surface
- Proceed recommendation: yes, this artifact is solid enough to proceed past Phase 3 closeout

## Remaining Risks

- Researcher-visible additive guidance remains intentionally scoped to review detail only; any expansion into review history/list or exported artifacts needs its own explicit workflow approval.
