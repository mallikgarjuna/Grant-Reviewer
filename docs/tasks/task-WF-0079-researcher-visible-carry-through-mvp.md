<!-- docs/tasks/task-WF-0079-researcher-visible-carry-through-mvp.md -->
# WF-0079 — Researcher-Visible Carry-Through MVP

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-13

Type: feature

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Add nullable companion storage with legacy-null compatibility

Goal:
Lock the smallest persisted card contract for WF-0079 by adding one nullable stored companion field on `ReviewCard` plus migration coverage that proves legacy reviews/cards remain valid without backfill.
Slice: storage-contract
User Stories: US1, US2, US3
PRD Requirements: FR1, FR3, FR4, FR5, FR10, FR12
Depends on: none
Enables: 2, 3, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/models/domain.py`
- `backend/migrations/versions/<new_revision>_wf0079_review_card_companion_text.py`
- `backend/tests/test_api.py`
May touch files:
- `none`
Out of scope: write-path orchestration, backend detail response assembly, BFF normalization, detail-page rendering, copy/export wording
Stop if: the storage seam needs more than one new public card field, requires mutating deterministic `feedback_text`, or cannot stay backward compatible with null legacy rows
Session boundary after: no
Acceptance Criteria:
- A targeted failing regression such as `test_wf0079_contract_review_card_storage_allows_null_companion_text` proves the current model/schema lacks the nullable persisted companion field or does not round-trip it safely for legacy-null rows.
- After the change, the same regression passes by proving `ReviewCard` storage supports exactly one nullable `synthesized_companion_text` field and still reads/writes cards with `null` companion data without warning or backfill.
- Migration coverage proves existing deterministic-only rows remain valid after schema upgrade.
- The task does not change any repository, service, API, BFF, or frontend behavior yet.
TDD Plan:
- RED: add `test_wf0079_contract_review_card_storage_allows_null_companion_text` in `backend/tests/test_api.py` to fail on the missing nullable persisted field and legacy-null round-trip expectation.
- GREEN: add the minimal `ReviewCard` field and one migration revision that introduces a nullable companion column without touching deterministic columns.
- REFACTOR: skip unless the migration or model name needs a tiny clarity-only cleanup.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0079_contract_review_card_storage_allows_null_companion_text"`
- `cd backend && rg -n "synthesized_companion_text|ReviewCard" app/models/domain.py migrations/versions tests/test_api.py`
Risks (if any): If the storage contract grows beyond one nullable field here, later API/frontend slices can overexpose synthesis state prematurely.

### [ ] Task 2 — Tracer bullet: persist one accepted ERC-2026-PoC companion on review creation

Goal:
Prove the structured-review write path can persist one accepted additive companion for an eligible `ERC-2026-PoC` card while leaving deterministic `feedback_text` unchanged and preventing writes for non-targeted calls/cards.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR1, FR2, FR3, FR4, FR8, FR11, FR12
Depends on: 1
Enables: 3, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/repositories/review_repository.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `none`
Out of scope: backend detail response assembly, API schema changes, BFF normalization, page rendering, copy/export behavior
Stop if: persisting the accepted companion requires read-time synthesis, widening beyond these three files, or storing the additive text inside deterministic `feedback_text`
Session boundary after: yes
Acceptance Criteria:
- A targeted failing regression such as `test_wf0079_contract_erc_poc_persists_accepted_companion_text` proves the current structured-review path does not yet persist accepted companion text for an in-scope card.
- After the change, the same regression passes by proving one representative `ERC-2026-PoC` assessed card persists accepted `synthesized_companion_text` during review generation and leaves `feedback_text` equal to the deterministic baseline.
- A paired regression such as `test_wf0079_contract_non_targeted_calls_do_not_persist_companion_text` proves non-`ERC-2026-PoC` calls/cards do not write the new field accidentally.
- Card-level fail-closed behavior is preserved: rejected or absent synthesis leaves the stored companion field null for only that card.
TDD Plan:
- RED: add `test_wf0079_contract_erc_poc_persists_accepted_companion_text` and `test_wf0079_contract_non_targeted_calls_do_not_persist_companion_text` in `backend/tests/test_structured_reviewer_service.py`; run them before changing the write path so they fail.
- GREEN: add the smallest repository/service write-path change that stores accepted companion text for eligible cards only and preserves deterministic fallback semantics.
- REFACTOR: extract a tiny typed payload/argument helper only if repository call signatures become unclear; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0079_contract_erc_poc_persists_accepted_companion_text or wf0079_contract_non_targeted_calls_do_not_persist_companion_text"`
- `cd backend && rg -n "wf0079_contract_(erc_poc_persists_accepted_companion_text|non_targeted_calls_do_not_persist_companion_text)|synthesized_companion_text|ERC-2026-PoC" app/services/structured_reviewer_service.py app/repositories/review_repository.py tests/test_structured_reviewer_service.py`
Risks (if any): If scope gating is too loose, additive data could leak into other calls; if too strict, accepted in-scope companions may never persist.

### [ ] Task 3 — Carry the optional companion through the backend detail contract

Goal:
Expose the persisted nullable companion field on `GET /reviews/{review_id}` so backend detail responses can return deterministic-only, companion-present, and mixed-card reviews without semantic drift.
Slice: backend-detail-contract
User Stories: US1, US2, US3
PRD Requirements: FR5, FR6, FR7, FR8, FR10, FR12
Depends on: 1, 2
Enables: 4, 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/api.py`
- `backend/main.py`
- `backend/tests/test_api.py`
May touch files:
- `none`
Out of scope: BFF normalization, frontend type updates, detail-page UI changes, copy/export copy changes
Stop if: exposing the field requires a second public state marker, whole-review synthesis logic, or frontend-side semantic rewriting to stay correct
Session boundary after: yes
Acceptance Criteria:
- A targeted failing regression such as `test_wf0079_contract_review_detail_response_carries_optional_companion_text` proves the current backend detail response drops the persisted field.
- After the change, the same regression passes by proving `ReviewDetailResponse.cards[*].synthesized_companion_text` is nullable, per-card, and present only on cards that actually persisted accepted companion text.
- A paired regression such as `test_wf0079_contract_review_detail_response_supports_mixed_card_companion_states` proves one card in a review can expose companion text while a sibling card stays deterministic-only.
- Legacy deterministic-only reviews still deserialize and return `null` companion values without empty placeholder state.
TDD Plan:
- RED: add `test_wf0079_contract_review_detail_response_carries_optional_companion_text` and `test_wf0079_contract_review_detail_response_supports_mixed_card_companion_states` in `backend/tests/test_api.py`; run them before backend response changes so they fail.
- GREEN: add the nullable backend response field and the minimal response assembly logic needed to return it verbatim per card.
- REFACTOR: skip unless response assembly needs a tiny helper to keep per-card mapping readable.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0079_contract_review_detail_response_carries_optional_companion_text or wf0079_contract_review_detail_response_supports_mixed_card_companion_states"`
- `cd backend && rg -n "synthesized_companion_text|ReviewCardSummary|ReviewDetailResponse" app/schemas/api.py main.py tests/test_api.py`
Risks (if any): If the backend invents a synthesized state beyond the nullable field, BFF and UI tasks can inherit unnecessary coupling.

### [ ] Task 4 — Preserve the companion field across the BFF/type boundary

Goal:
Keep the review-detail BFF contract additive and truthful by passing the backend companion field through unchanged and declaring it in the frontend review-detail types.
Slice: bff-contract
User Stories: US1, US2
PRD Requirements: FR6, FR10, FR12
Depends on: 3
Enables: 5, 6
Parallelizable: yes
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts`
- `frontend/src/lib/bff/types.ts`
May touch files:
- `none`
Out of scope: detail-page rendering, copy/export UI behavior, reviews-list changes, backend schema changes
Stop if: the BFF must synthesize or rename the backend field to keep the page working, because the contract should stay pass-through and additive
Session boundary after: no
Acceptance Criteria:
- A targeted failing regression such as `wf0079_bff_review_detail_preserves_optional_companion_text` proves the current BFF/type boundary does not yet model or preserve the optional per-card field.
- After the change, the same regression passes by proving the BFF returns `synthesized_companion_text` verbatim when present and preserves `null`/absence for deterministic-only cards.
- The frontend `ReviewCardSummary`/`ReviewDetailResponse` types accept the optional field without forcing companion presence.
- The BFF task does not change copy/export behavior or page rendering semantics.
TDD Plan:
- RED: add `wf0079_bff_review_detail_preserves_optional_companion_text` in `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts`; run it before changing the route/types so it fails.
- GREEN: make the minimum BFF normalization and type updates needed to preserve the backend field verbatim.
- REFACTOR: skip unless a tiny card normalizer helper is needed to avoid repeated optional-field handling.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts'`
- `cd frontend && rg -n "synthesized_companion_text|ReviewCardSummary|ReviewDetailResponse" src/app/api/bff/reviews/'[reviewId]'/route.ts src/app/api/bff/reviews/'[reviewId]'/route.test.ts src/lib/bff/types.ts`
Risks (if any): If the BFF rewrites semantics instead of passing the field through, the detail page can drift from backend truth.

### [ ] Task 5 — Render additive companions on the detail page and keep copy/export deterministic-only

Goal:
Render deterministic feedback as the primary card body on `/app/reviews/[reviewId]`, add a clearly labeled companion block only when present, and align the page-local copy/download wording and behavior to stay deterministic-only in MVP.
Slice: detail-page-render
User Stories: US1, US3, US4
PRD Requirements: FR7, FR8, FR9, FR10, FR12
Depends on: 4
Enables: 6
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/components/review/ReviewCard.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `none`
Out of scope: reviews-list/history rollout, legacy `/reviews` redesign, whole-review export redesign, backend/BFF contract changes
Stop if: truthful rendering requires whole-page AI summary logic, more than these three files, or a change to the deterministic-first baseline contract
Session boundary after: yes
Acceptance Criteria:
- A targeted failing regression such as `wf0079_review_detail_renders_optional_companion_block` proves the current page does not yet show additive companion text when present.
- After the change, the same regression passes by proving deterministic `feedback_text` remains the primary rendered feedback and a labeled additive companion block appears only on cards with `synthesized_companion_text`.
- A paired regression such as `wf0079_review_detail_copy_and_download_remain_deterministic_only` proves the page-local copy/download output still includes deterministic feedback only and the visible wording no longer implies additive carry-through in copied/exported text.
- Another regression such as `wf0079_review_detail_legacy_and_mixed_cards_hide_empty_companion_shells` proves legacy-null and mixed-card pages render cleanly with no empty headings or misleading placeholder blocks.
TDD Plan:
- RED: add `wf0079_review_detail_renders_optional_companion_block`, `wf0079_review_detail_copy_and_download_remain_deterministic_only`, and `wf0079_review_detail_legacy_and_mixed_cards_hide_empty_companion_shells` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`; run them before the UI change so they fail.
- GREEN: add the smallest detail-page and card-render changes needed to show the optional additive block, preserve deterministic-first rendering, and keep copy/download deterministic-only with aligned wording.
- REFACTOR: extract a tiny companion-render helper or copy-label constant only if the page/component diff becomes repetitive; otherwise skip.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx'`
- `cd frontend && rg -n "synthesized_companion_text|deterministic-only|Copy as text|Download \\.txt|additive" src/components/review/ReviewCard.tsx src/app/app/reviews/'[reviewId]'/page.tsx src/app/app/reviews/'[reviewId]'/page.test.tsx`
Risks (if any): If the labels are vague, researchers could assume copied/exported text contains the additive companion when it does not.

### [ ] Task 6 — Close the scope lock and fail-closed verification gate

Goal:
Verify the final implementation remains limited to the approved detail-page slice, keeps deferred surfaces deterministic-only, and records explicit proof rows for the fail-closed proceed gate before any implementation-ready claim.
Slice: closure-gate
User Stories: US2, US3, US4
PRD Requirements: FR11, FR12
Depends on: 1, 2, 3, 4, 5
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `none`
May touch files:
- `none`
Out of scope: opportunistic UI cleanup, reviews-list/history feature work, legacy `/reviews` redesign, extra analytics
Stop if: any proof requires widening into history/list surfaces or a second workflow approval to close honestly
Session boundary after: yes
Acceptance Criteria:
- Phase 3 records explicit `pass`, `fail`, or approved `skipped` evidence for each verification-matrix row below before claiming the plan is closed.
- Verification proves non-targeted calls/cards remain deterministic-only, review history/list and legacy `/reviews` surfaces stay unchanged, and no read-time synthesis or deterministic-field overloading was introduced.
- Verification uses deterministic structural assertions and fixture/stubbed companion values rather than brittle exact-string expectations against live-model output.
- If any required proof fails, Phase 3 stops instead of soft-closing the workflow.
TDD Plan:
- N/A for the gate itself; this task consumes the RED/GREEN proofs produced by Tasks 1-5 and fails closed if they are incomplete.
Verification Steps:
- `git diff --name-only main...HEAD`
- `rg -n "synthesized_companion_text|feedback_text|Copy as text|Download \\.txt|My reviews" backend/app frontend/src/app/app/reviews frontend/src/components/review`
- `cd backend && uv run pytest tests/test_api.py -k "wf0079_contract_" && uv run pytest tests/test_structured_reviewer_service.py -k "wf0079_contract_"`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' 'src/app/app/reviews/[reviewId]/page.test.tsx'`
Risks (if any): Without an explicit closure gate, Phase 3 could overclaim researcher-visible rollout while deferred surfaces or scope-gates remain unproved.

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Deterministic SSOT boundary proof | 2, 5 | `wf0079_contract_erc_poc_persists_accepted_companion_text`, `wf0079_review_detail_renders_optional_companion_block` | deterministic `feedback_text` remains primary and additive text never replaces it | `fail` (default until executed) | required | must not mutate deterministic baseline |
| Write-path persistence proof | 2 | `wf0079_contract_erc_poc_persists_accepted_companion_text` | accepted in-scope companion text persists during review generation | `fail` (default until executed) | required | no read-time synthesis |
| Legacy review compatibility proof | 1, 3, 5 | `wf0079_contract_review_card_storage_allows_null_companion_text`, `wf0079_review_detail_legacy_and_mixed_cards_hide_empty_companion_shells` | null legacy rows stay valid from storage through render | `fail` (default until executed) | required | no backfill requirement |
| Eligibility scope-gate proof | 2, 6 | `wf0079_contract_non_targeted_calls_do_not_persist_companion_text` | non-`ERC-2026-PoC` calls/cards do not persist or expose companion text | `fail` (default until executed) | required | protects narrow rollout |
| Detail read/API carry-through proof | 3 | `wf0079_contract_review_detail_response_carries_optional_companion_text` | backend detail response returns the nullable per-card field without semantic drift | `fail` (default until executed) | required | per-card optionality only |
| BFF carry-through proof | 4 | `wf0079_bff_review_detail_preserves_optional_companion_text` | BFF/type boundary passes the backend field through unchanged | `fail` (default until executed) | required | no semantic rewrite |
| Mixed-card fail-closed proof | 3, 5 | `wf0079_contract_review_detail_response_supports_mixed_card_companion_states`, `wf0079_review_detail_legacy_and_mixed_cards_hide_empty_companion_shells` | one card can show companion text while another remains deterministic-only | `fail` (default until executed) | required | per-card degradation only |
| Detail-page render proof | 5 | `wf0079_review_detail_renders_optional_companion_block` | page renders additive companion only when present and labeled as additive guidance | `fail` (default until executed) | required | deterministic text stays primary |
| Page-local copy/export proof | 5 | `wf0079_review_detail_copy_and_download_remain_deterministic_only` | copy/download remain deterministic-only with aligned wording | `fail` (default until executed) | required | no implied additive export |
| Out-of-scope surface proof | 6 | `git diff --name-only main...HEAD` plus targeted `rg` check | reviews list/history and legacy `/reviews` remain unchanged and deterministic-only | `fail` (default until executed) | required | defer widened rollout |
| Honest non-determinism test strategy | 6 | task-level selectors plus fixture/stubbed companion values | proofs avoid brittle exact-string assertions against live-model output | `fail` (default until executed) | required | structural assertions only |
| Audit disposition proof | 6 | task artifact + Part B/C ledger | all blocking findings closed; non-blocking findings closed or explicitly rejected with rationale | `fail` (default until executed) | required | no implicit approval |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| none yet | none | n/a | n/a | open | populated during Part B / Part C |

## Changelog

- v0.1 (2026-03-13): Initial task breakdown from PRD.
