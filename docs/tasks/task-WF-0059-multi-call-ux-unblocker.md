<!-- docs/tasks/task-WF-0059-multi-call-ux-unblocker.md -->
# WF-0059 — Multi-call UX Unblocker

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-06

Type: feature

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Proof-call parity plumbing and guard selectors

Goal:
Lock the ERC proof target into deterministic frontend/backend guard coverage before behavior changes land, so later slices can prove parity and scope control without broad exploratory edits.
Slice: parity-plumbing
User Stories: US1, US2, US3
PRD Requirements: FR1, FR7, FR8, FR11, FR13
Depends on: none
Enables: 2, 3, 5, 7
Parallelizable: no
Files to modify:
- `frontend/src/lib/submit/renderModel.test.ts`
- `backend/tests/test_api.py`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
Acceptance Criteria:
- Deterministic WF-0059 test coverage exists for the locked proof target `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`.
- Guard coverage proves current Veni/flat-call behavior remains the control path while the proof-call path is extended.
- Task-level selectors are added for nested submit blocking, structured-review contract entry, and review-detail fallback boundaries touched by later tasks.
TDD Plan:
- RED: add `wf0059_render_model_proof_target_guard`, `wf0059_structured_review_proof_target_contract_guard`, and `wf0059_review_detail_fallback_guard` cases that fail until the seams are explicitly wired for the proof call.
- GREEN: add the minimal fixture/helper plumbing in the touched tests so later slices can target the proof call deterministically without widening scope.
- REFACTOR: skip unless shared proof-call fixture setup becomes repetitive across the three tests.
Verification Steps:
- `cd frontend && npx vitest run src/lib/submit/renderModel.test.ts -t "wf0059_render_model_proof_target_guard"`
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0059_review_detail_fallback_guard"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0059_structured_review_proof_target_contract_guard"`
Risks (if any): Overly broad selectors would weaken later proof obligations, so case names must stay WF-specific.

### [ ] Task 2 — Tracer bullet: hierarchical proof-call submit reaches structured-review

Goal:
Replace the proof-call nested-node blocker with the thinnest functional hierarchical submit path that reaches `/api/bff/structured-review` in executable order.
Slice: tracer-bullet
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR3, FR8, FR11
Depends on: 1
Enables: 3, 7
Parallelizable: no
Files to modify:
- `frontend/src/lib/submit/renderModel.ts`
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
Acceptance Criteria:
- The ERC proof call no longer resolves to the `nested_nodes` unsupported state in the submit renderer.
- Submit UI renders the proof-call hierarchy in the intended execution order and collects text for required nodes.
- Submitting the proof path posts a structured-review request carrying the proof-call node logical IDs needed downstream.
TDD Plan:
- RED: add `wf0059_submit_tracer_erc_proof_call_reaches_structured_review` in `frontend/src/components/submit/UniversalSubmitForm.test.tsx`.
- GREEN: implement the minimum `renderModel` and submit-form changes to support the proof-call hierarchy without widening support claims beyond the locked proof target.
- REFACTOR: extract a small helper for proof-call node flattening only if `UniversalSubmitForm.tsx` becomes harder to read.
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0059_submit_tracer_erc_proof_call_reaches_structured_review"`
- `cd frontend && npm run test:ui`
Risks (if any): It is easy to accidentally generalize all nested calls instead of the single proof target.

### [ ] Task 3 — Structured-review hierarchical payload parity

Goal:
Allow the proof-call hierarchical payload through the existing structured-review contract while preserving validation ordering, idempotency replay, and mismatch semantics.
Slice: contract-parity
User Stories: US1, US3
PRD Requirements: FR3, FR4, FR8, FR9, FR11, FR13
Depends on: 1, 2
Enables: 4, 7
Parallelizable: no
Files to modify:
- `backend/app/schemas/structured_review.py`
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Structured-review accepts the proof-call hierarchical payload through the existing request boundary.
- Validation failures still precede idempotency mismatch handling for malformed hierarchical payloads.
- Replay with the same idempotency key and payload remains stable; same key plus different payload still returns the existing mismatch/error behavior.
TDD Plan:
- RED: add `wf0059_contract_hierarchical_submit_validation_and_idempotency` in `backend/tests/test_api.py` and `wf0059_structured_payload_normalization_contract` in `backend/tests/test_structured_reviewer_service.py`.
- GREEN: implement the smallest schema/service changes needed to translate the proof-path payload without changing existing persistence side effects.
- REFACTOR: extract nested-node normalization logic only if both schema and service need the same transform.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0059_contract_hierarchical_submit_validation_and_idempotency"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0059_structured_payload_normalization_contract"`
Risks (if any): Validation-order regressions can hide behind a passing happy-path test if mismatch coverage is not kept in the same slice.

### [ ] Task 4 — Persist submitted-node coverage for proof-path reviews

Goal:
Persist a review-linked submitted-node coverage source so proof-call review detail can account for reviewed nodes even when they emit zero cards.
Slice: persisted-coverage
User Stories: US2, US3
PRD Requirements: FR5, FR10, FR12, FR14
Depends on: 3
Enables: 5, 6, 7
Parallelizable: no
Files to modify:
- `backend/app/repositories/review_repository.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_api.py`
Acceptance Criteria:
- Successful proof-path review creation persists submitted node logical IDs, or an equivalent persisted review-linked coverage source, on the review detail contract.
- Coverage accounting includes proof-call nodes that were submitted but emitted zero review cards.
- The persisted coverage source is review-linked and does not depend on URL query parameters.
TDD Plan:
- RED: add `wf0059_contract_persisted_submitted_node_coverage` in `backend/tests/test_api.py`.
- GREEN: implement the minimal repository/detail-contract changes needed to expose persisted coverage for proof-call reviews.
- REFACTOR: extract review-detail coverage serialization if repository and API assembly start duplicating mapping logic.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0059_contract_persisted_submitted_node_coverage"`
- `cd backend && rg -n "submitted_node|coverage" app/repositories/review_repository.py app/schemas/api.py`
Risks (if any): Card-derived coverage shortcuts would silently violate the persisted-node invariant for zero-card nodes.

### [ ] Task 5 — Review detail flips to call-linked ordering for the proof path

Goal:
Render proof-call review detail from stored review linkage plus fetched call metadata, never from `submitted_nodes` query-param ordering.
Slice: review-detail-call-aware
User Stories: US2, US3
PRD Requirements: FR5, FR6, FR10, FR14
Depends on: 1, 4
Enables: 6, 7
Parallelizable: no
Files to modify:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
Acceptance Criteria:
- Proof-call review detail derives grouping, ordering, labels, and coverage from persisted review-linked data plus call metadata.
- Proof-call rendering does not use `submitted_nodes` query params as its source of truth.
- Traceability in review detail reflects the proof call's actual sections and evaluation criteria/elements.
TDD Plan:
- RED: add `wf0059_review_detail_proof_path_uses_call_linked_ordering` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`.
- GREEN: implement the minimal BFF/page changes needed to consume the persisted coverage source and call-node metadata for the proof path.
- REFACTOR: extract ordering/coverage derivation into a small local helper if page composition becomes difficult to follow.
Verification Steps:
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0059_review_detail_proof_path_uses_call_linked_ordering"`
- `cd frontend && npm run test:ui`
Risks (if any): Silent fallback to review-payload ordering would look correct in happy-path snapshots while still violating the proof-path source-of-truth contract.

### [ ] Task 6 — Explicit fallback and unmapped proof-call state

Goal:
Keep legacy fallback scoped to older or mixed-version reviews and surface explicit unmapped state when proof-call linkage is incomplete.
Slice: fallback-explicitness
User Stories: US2, US3
PRD Requirements: FR6, FR7, FR10, FR13, FR14
Depends on: 4, 5
Enables: 7
Parallelizable: no
Files to modify:
- `backend/app/schemas/api.py`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
Acceptance Criteria:
- Older or mixed-version reviews without required call-linked metadata take an explicit legacy fallback path.
- Partially mapped proof-call reviews render visible unmapped state instead of silently degrading to Veni-shaped ordering.
- Proof-call tests prove legacy fallback does not leak into the locked proof target.
TDD Plan:
- RED: add `wf0059_review_detail_explicit_legacy_fallback_and_unmapped_state` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`.
- GREEN: implement the smallest schema/page updates needed to distinguish legacy fallback from proof-path unmapped state.
- REFACTOR: deduplicate any fallback-note rendering branches once the explicit states are proven.
Verification Steps:
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0059_review_detail_explicit_legacy_fallback_and_unmapped_state"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0059_contract_persisted_submitted_node_coverage"`
Risks (if any): Mixing legacy and proof-path states in one flag can cause false-positive parity on older reviews while masking proof-call defects.

### [ ] Task 7 — Scope guard: proof-path closure regressions and Veni parity

Goal:
Close the implementation plan with deterministic automated regressions that prove Veni parity, no fallback leakage, and persisted submitted-node coverage for the proof path.
Slice: scope-guard
User Stories: US1, US2, US3
PRD Requirements: FR7, FR8, FR12, FR13, FR14
Depends on: 2, 3, 4, 5, 6
Enables: 8
Parallelizable: no
Files to modify:
- `backend/tests/test_api.py`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
Acceptance Criteria:
- Deterministic automated coverage proves proof-call hierarchical submit, proof-call review-detail ordering/coverage, and Veni/flat-call regression parity.
- Deterministic automated coverage proves legacy fallback does not leak into proof-call reviews and zero-card submitted nodes still surface as reviewed from persisted coverage.
- The closure regressions remain WF-specific and do not rely on broad namespace filters.
TDD Plan:
- RED: add `wf0059_submit_tracer_preserves_veni_flat_path`, `wf0059_review_detail_proof_path_blocks_query_param_fallback`, and `wf0059_zero_card_node_remains_reviewed_from_persisted_coverage`.
- GREEN: add the smallest final regression assertions after Tasks 2 through 6 are green.
- REFACTOR: trim duplicated setup between frontend/backend closure assertions if the selectors become noisy.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0059_zero_card_node_remains_reviewed_from_persisted_coverage"`
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0059_submit_tracer_preserves_veni_flat_path"`
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0059_review_detail_proof_path_blocks_query_param_fallback"`
Risks (if any): If the regression selectors stay broad, Phase 3 can claim closure while still missing the persisted-coverage invariant.

### [ ] Task 8 — Concrete ERC proof artifact and walkthrough handoff

Goal:
Capture the required end-to-end proof artifact for `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml` after the automated scope guards are green.
Slice: proof-evidence
User Stories: US1, US2, US3
PRD Requirements: FR1, FR10, FR12, FR14
Depends on: 7
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0059-multi-call-ux-unblocker.md`
- `docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_submit.json`
- `docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_review_detail.json`
Acceptance Criteria:
- One concrete proof artifact is captured for the locked ERC proof target and tied to the same created review across submit and review-detail evidence.
- Evidence shows selected proof-call identity, successful submit/review-create result, and review-detail grouping/ordering/coverage traceability.
- Walkthrough text makes explicit that proof-call review detail used persisted submitted-node coverage plus call-linked metadata rather than `submitted_nodes` query params.
TDD Plan:
- N/A: evidence capture task after automated gates are already green.
Verification Steps:
- `rg -n "erc_stg_2026_full|persisted submitted-node coverage|call-linked metadata|submitted_nodes" docs/walkthroughs/walkthrough-WF-0059-multi-call-ux-unblocker.md`
- `test -f docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_submit.json`
- `test -f docs/walkthroughs/evidence/WF-0059/erc_stg_2026_full_review_detail.json`
Risks (if any): Evidence gathered before Task 7 passes could memorialize a path that still violates parity or fallback invariants.

## Changelog

- v0.1 (2026-03-06): Initial task breakdown from PRD.
- v0.2 (2026-03-06): Applied review edits by splitting closure proof from evidence capture and tightening task-level verification selectors.
