<!-- docs/tasks/task-WF-0080-production-mvp-launch-wedge.md -->
# WF-0080 — Production MVP Launch Wedge

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-14

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: fail closed on direct backend structured-review submit before review creation

Goal:
Prove the narrowest launch-wedge access guard by rejecting out-of-cohort direct signed requests at `POST /api/structured-review` before review creation or downstream execution.
Slice: tracer-bullet-backend-gate
User Stories: US1, US3
PRD Requirements: FR1, FR3, FR4, FR16
Depends on: none
Enables: 2, 3, 6, 8
Parallelizable: no
Files to modify:
Must touch files:
- `backend/main.py`
- `backend/tests/test_api.py`
May touch files:
- `none`
Out of scope: BFF submit gating, review-detail ranking, detail-page rendering, support walkthrough evidence, generalized onboarding/admin tooling
Stop if: backend cohort gating cannot be enforced before review creation, requires widening beyond `ERC-2026-PoC`, or needs a new persistence/logging system to explain rejections
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions `test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation` and `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors` prove the current backend submit seam does not yet fail closed for launch-cohort access.
- After the change, invited in-cohort direct signed requests still reach the existing review creation path, while out-of-cohort direct signed requests return `COHORT_ACCESS_DENIED` before backend review creation side effects begin.
- Existing `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` behavior remains intact for in-cohort users and is not shadowed by the new gate.
- The task remains locked to the existing submit contract, idempotency behavior, and `ERC-2026-PoC` wedge only.
TDD Plan:
- RED: add `test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation` and `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors` in `backend/tests/test_api.py`; run them before changing the backend submit seam so they fail.
- GREEN: add the minimum backend cohort gate needed to reject out-of-cohort traffic before any review creation while preserving existing quota/review-disabled behavior.
- REFACTOR: extract one tiny backend gate helper only if the guard becomes unclear; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py::test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation tests/test_api.py::test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors`
- `cd backend && rg -n "COHORT_ACCESS_DENIED|REVIEWS_DISABLED|QUOTA_EXCEEDED|structured-review" main.py tests/test_api.py`
Risks (if any): If the reject path is not truly pre-side-effect, Phase 3 could accidentally create costly reviews for blocked users.

### [x] Task 2 — Fail closed on BFF structured-review submit before proxying

Goal:
Mirror the launch-cohort access guard at `/api/bff/structured-review` so out-of-cohort users are blocked before proxying to the backend.
Slice: bff-submit-gate
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR4, FR16
Depends on: 1
Enables: 3, 7, 8
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/structured-review/route.ts`
- `frontend/src/app/api/bff/structured-review/route.test.ts`
May touch files:
- `frontend/src/lib/bff/route-helpers.ts`
Out of scope: backend direct-submit gating, review-detail ranking, detail-page rendering, support walkthrough evidence, generalized onboarding/admin tooling
Stop if: the BFF gate needs a second identity source, a separate onboarding store, or any post-proxy rejection to work
Session boundary after: yes
Acceptance Criteria:
- A targeted failing regression `wf0080_bff_submit_blocks_out_of_cohort_before_proxy` proves the current BFF submit seam does not yet fail closed for launch-cohort access.
- After the change, invited in-cohort requests still proxy to the existing backend path, while out-of-cohort requests return `COHORT_ACCESS_DENIED` before proxying.
- Existing BFF request validation and idempotency-header requirements remain intact for in-cohort users.
- The task stays locked to the existing BFF submit contract and `ERC-2026-PoC` wedge only.
TDD Plan:
- RED: add `wf0080_bff_submit_blocks_out_of_cohort_before_proxy` in `frontend/src/app/api/bff/structured-review/route.test.ts`; run it before changing the BFF submit seam so it fails.
- GREEN: add the minimum BFF cohort gate needed to reject out-of-cohort traffic before proxying.
- REFACTOR: extract one tiny BFF gate helper only if the check becomes unclear; otherwise skip.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/structured-review/route.test.ts' -t '^wf0080_bff_submit_blocks_out_of_cohort_before_proxy$'`
- `cd frontend && rg -n "COHORT_ACCESS_DENIED|structured-review|Idempotency-Key" src/app/api/bff/structured-review/route.ts src/app/api/bff/structured-review/route.test.ts src/lib/bff/route-helpers.ts`
Risks (if any): If the BFF gate happens after proxying, blocked traffic can still create downstream cost or ambiguous audit trails.

### [x] Task 3 — Tracer bullet: prove one invited submit-to-detail wedge through backend detail projection

Goal:
Prove one invited `ERC-2026-PoC` researcher can complete the locked submit-to-detail happy path by keeping the backend projection seam additive at `GET /reviews/{review_id}` and fetchable after review creation.
Slice: tracer-bullet-detail-projection
User Stories: US1, US2, US3
PRD Requirements: FR6, FR7, FR8, FR10, FR11, FR16
Depends on: 1, 2
Enables: 4, 5, 6, 8
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/api.py`
- `backend/main.py`
- `backend/tests/test_api.py`
May touch files:
- `none`
Out of scope: BFF/frontend-local ranking, new persistence tables, whole-review synthesized summaries, export/copy wording
Stop if: the projection cannot stay additive at `GET /reviews/{review_id}`, requires new persisted ranking state, or needs ranking logic outside backend response assembly
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions `test_wf0080_review_detail_emits_bounded_detail_projection` and `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker` prove the current response lacks the approved projection contract and ranking semantics.
- A targeted failing regression `test_wf0080_invited_submit_reaches_detail_projection` proves one in-cohort `ERC-2026-PoC` submit can create a review and later fetch the approved `detail_projection` without widening beyond the existing submit/detail path.
- After the change, `ReviewDetailResponse.detail_projection` exposes exactly `version`, `headline_state`, `ordered_card_ids`, `top_action_card_ids`, and `ranking_basis`, with `top_action_card_ids` bounded to at most 3 cards.
- Ranking is derived only from `assessment_status`, then rating order `CRITICAL -> WARNING -> NOTE -> SUCCESS`, then existing call/node order; no BFF or frontend recomputation is required.
- `headline_state` becomes `no_critical_blockers` only when every card is `ASSESSED` and every rating is `NOTE` or `SUCCESS`; any `NOT_ASSESSABLE`, `CRITICAL`, or `WARNING` keeps `action_required`.
TDD Plan:
- RED: add `test_wf0080_review_detail_emits_bounded_detail_projection`, `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker`, and `test_wf0080_invited_submit_reaches_detail_projection` in `backend/tests/test_api.py`; run them before backend contract changes so they fail.
- GREEN: add the minimal schema and response-assembly logic required to emit the additive `detail_projection` object directly from persisted card truth.
- REFACTOR: extract one tiny ranking helper only if response assembly becomes hard to read; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py::test_wf0080_review_detail_emits_bounded_detail_projection tests/test_api.py::test_wf0080_review_detail_projection_uses_existing_order_tiebreaker tests/test_api.py::test_wf0080_invited_submit_reaches_detail_projection`
- `cd backend && rg -n "detail_projection|top_action_card_ids|ranking_basis|no_critical_blockers" app/schemas/api.py main.py tests/test_api.py`
Risks (if any): If ranking semantics leak outside this seam, the wedge can drift into hidden coupling across backend, BFF, and UI.

### [x] Task 4 — Preserve `detail_projection` across the BFF detail contract without reinterpretation

Goal:
Keep the backend read-model authoritative by passing `detail_projection` through the BFF detail route and frontend types unchanged.
Slice: bff-detail-contract
User Stories: US1, US2
PRD Requirements: FR10, FR11, FR16
Depends on: 3
Enables: 5, 8
Parallelizable: yes
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts`
- `frontend/src/lib/bff/types.ts`
May touch files:
- `none`
Out of scope: submit gating, detail-page rendering, export/copy behavior, alternate ranking helpers
Stop if: the BFF must recompute ranking or headline semantics locally to keep the page working, because that would violate the bounded backend seam
Session boundary after: no
Acceptance Criteria:
- A targeted failing regression such as `wf0080_bff_review_detail_preserves_backend_projection` proves the current BFF route drops or rewrites the new projection object.
- After the change, the BFF returns `detail_projection` verbatim, including `ordered_card_ids`, `top_action_card_ids`, and `headline_state`, and frontend types model the additive object without local ranking helpers.
- The BFF task does not alter submit routing, review list/history surfaces, or any deferred review-detail reinterpretation.
TDD Plan:
- RED: add `wf0080_bff_review_detail_preserves_backend_projection` in `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts` and run it before changing the route/types so it fails.
- GREEN: make the smallest BFF normalization and type updates needed to preserve the backend projection object unchanged.
- REFACTOR: skip unless a tiny typed normalizer is needed to avoid duplicated optional-field plumbing.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t '^wf0080_bff_review_detail_preserves_backend_projection$'`
- `cd frontend && rg -n "detail_projection|top_action_card_ids|headline_state|ranking_basis" src/app/api/bff/reviews/'[reviewId]'/route.ts src/app/api/bff/reviews/'[reviewId]'/route.test.ts src/lib/bff/types.ts`
Risks (if any): A local BFF rewrite would make Phase 3 verification ambiguous and break the PRD’s single-seam constraint.

### [x] Task 5 — Render the action-first detail page with honest pending, failure, and export truthfulness

Goal:
Implement the one approved researcher reading flow on `/app/reviews/[reviewId]`: top 1-3 prioritized cards above the fold, expandable evidence, honest pending/timeout/failure states, and explicit copy/export truthfulness.
Slice: detail-page-flow
User Stories: US1, US2
PRD Requirements: FR5, FR6, FR8, FR9, FR12, FR16
Depends on: 3, 4
Enables: 8
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/components/review/ReviewCard.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `none`
Out of scope: reviews list/history redesign, generalized export redesign, backend/BFF ranking changes, multi-call rollout
Stop if: the page needs new persistence fields, cross-page navigation changes, or frontend-local ranking logic to present the approved flow honestly
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions such as `wf0080_review_detail_renders_top_action_cards_first`, `wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success`, `wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default`, and `wf0080_review_detail_handles_pending_timeout_and_failure_honestly` prove the current page does not yet satisfy the approved reading model.
- A targeted failing regression such as `wf0080_review_detail_export_copy_stays_truthful_about_projection_scope` proves the current page-local copy/export behavior can overclaim what the projection framing includes.
- After the change, only the backend-provided `top_action_card_ids` render above the fold by default, the first ranked card exposes enough summary context to justify rank, and supporting evidence stays collapsed until expanded per card.
- The page renders `no critical blockers found` only when the backend projection indicates `no_critical_blockers`; otherwise it stays action-oriented without implying success.
- Pending, timeout, failed, retry, and return-later states remain explicit and truthful, and page-local copy/export wording states any projection-only framing it excludes.
TDD Plan:
- RED: add `wf0080_review_detail_renders_top_action_cards_first`, `wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success`, `wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default`, `wf0080_review_detail_handles_pending_timeout_and_failure_honestly`, and `wf0080_review_detail_export_copy_stays_truthful_about_projection_scope` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`; run them before UI changes so they fail.
- GREEN: make the minimum page/component changes needed to consume `detail_projection`, render the top-action-first layout, and keep degraded states and copy/export messaging honest.
- REFACTOR: extract a tiny ordering/headline presentational helper only if the page diff becomes repetitive; otherwise skip.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t '^(wf0080_review_detail_renders_top_action_cards_first|wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success|wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default|wf0080_review_detail_handles_pending_timeout_and_failure_honestly|wf0080_review_detail_export_copy_stays_truthful_about_projection_scope)$'`
- `cd frontend && rg -n "top_action_card_ids|no critical blockers found|return later|still processing|supporting evidence" src/app/app/reviews/'[reviewId]'/page.tsx src/components/review/ReviewCard.tsx src/app/app/reviews/'[reviewId]'/page.test.tsx`
Risks (if any): If the page overstates completion or hides degraded states, the production wedge could mislead researchers during the launch cohort.

### [x] Task 6 — Add bounded backend trace correlation and no-new-storage proof for one disputed session

Goal:
Make one failed or disputed cohort session explainable on backend-owned seams by adding narrow trace correlation across direct submit, review creation, and detail retrieval without widening storage or inventing a new public read model.
Slice: backend-support-trace
User Stories: US3, US4
PRD Requirements: FR13, FR14, FR16
Depends on: 1, 3
Enables: 7, 8
Parallelizable: no
Files to modify:
Must touch files:
- `backend/main.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_api.py`
May touch files:
- `none`
Out of scope: analytics dashboards, admin consoles, replay tooling, new retention stores
Stop if: traceability requires a new data store, broad observability platform work, storing launch-session text outside existing review storage and bounded support traces, or a new public detail payload contract beyond bounded additive support metadata already justified by FR13/FR14
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions `test_wf0080_trace_correlation_is_present_on_submit_and_detail` and `test_wf0080_trace_support_does_not_create_new_storage_surface` prove the current backend seams cannot yet explain one disputed session without widening storage/access.
- After the change, one bounded trace identifier or correlation tuple is emitted on backend-owned submit rejection or creation paths and is tieable to later detail retrieval/support investigation without introducing a new storage class for researcher text.
- Any additive support metadata exposed on backend responses remains minimal and bounded to supportability; if later BFF/page work needs more than passthrough, execution must stop and split rather than reinterpret backend truth.
- Verification proves the trace path does not widen access to review inputs/outputs beyond designated maintainers and existing review/support trace surfaces.
- The task stays limited to supportability for the launch wedge and does not introduce generalized telemetry or cohort-management products.
TDD Plan:
- RED: add `test_wf0080_trace_correlation_is_present_on_submit_and_detail` and `test_wf0080_trace_support_does_not_create_new_storage_surface` in `backend/tests/test_api.py`; run them before changing backend trace seams so they fail.
- GREEN: add the minimal backend trace correlation plumbing needed to connect submit and detail support evidence on existing surfaces only.
- REFACTOR: skip unless one tiny helper is needed to keep correlation-id naming consistent across the backend seams.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py::test_wf0080_trace_correlation_is_present_on_submit_and_detail tests/test_api.py::test_wf0080_trace_support_does_not_create_new_storage_surface`
- `cd backend && rg -n "trace|correlation|support" app/schemas/api.py main.py tests/test_api.py`
Risks (if any): If backend trace evidence is too weak, operators will have to infer failures from unrelated logs and the wedge will not be honestly supportable.

### [ ] Task 7 — Preserve submit-side support trace correlation at the BFF boundary

Goal:
Keep the BFF submit seam aligned with the backend trace contract by preserving the bounded support trace identifier/header without creating a second trace model or local reinterpretation.
Slice: bff-support-trace
User Stories: US3, US4
PRD Requirements: FR13, FR14, FR16
Depends on: 2, 6
Enables: 8
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/structured-review/route.ts`
- `frontend/src/app/api/bff/structured-review/route.test.ts`
May touch files:
- `frontend/src/lib/bff/route-helpers.ts`
Out of scope: backend trace generation, detail-page rendering, analytics dashboards, admin consoles, replay tooling, new retention stores
Stop if: the BFF needs its own persisted trace store, needs to recompute backend support metadata locally, or needs a second trace identifier distinct from the backend contract
Session boundary after: yes
Acceptance Criteria:
- A targeted failing regression `wf0080_bff_submit_preserves_trace_headers_for_support` proves the current BFF submit seam does not yet preserve the bounded support trace correlation required for one disputed-session investigation.
- After the change, the BFF preserves the approved trace identifier/header contract on submit without inventing local ranking, local support metadata, or a second trace namespace.
- Verification proves the trace path does not widen access to review inputs/outputs beyond the approved BFF/backend support surfaces.
- The task stays limited to submit-side supportability for the launch wedge and does not introduce generalized telemetry or cohort-management products.
TDD Plan:
- RED: add `wf0080_bff_submit_preserves_trace_headers_for_support` in `frontend/src/app/api/bff/structured-review/route.test.ts`; run it before changing the BFF submit seam so it fails.
- GREEN: add the minimum BFF trace-header preservation needed to keep the backend trace contract observable on the submit path.
- REFACTOR: skip unless one tiny helper is needed to keep header naming consistent.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/structured-review/route.test.ts' -t '^wf0080_bff_submit_preserves_trace_headers_for_support$'`
- `cd frontend && rg -n "trace|correlation|support" src/app/api/bff/structured-review/route.ts src/app/api/bff/structured-review/route.test.ts src/lib/bff/route-helpers.ts`
Risks (if any): If submit-side BFF trace correlation drifts from the backend contract, support evidence will become ambiguous even when backend logging is correct.

### [ ] Task 8 — Close the must-ship gate with usefulness evidence, scope proof, and fail-closed verification rows

Goal:
Make the Phase 3 handoff executable and honest by turning the walkthrough into the required closure artifact for usefulness evidence, must-ship versus deferred proof, and row-level pass/fail verification.
Slice: closure-gate
User Stories: US3, US4
PRD Requirements: FR15, FR16
Depends on: 1, 2, 3, 4, 5, 6, 7
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0080-production-mvp-launch-wedge.md`
May touch files:
- `docs/index.md`
Out of scope: post-launch analytics interpretation, expanding to new calls, re-opening deferred surfaces, hand-wavy evidence summaries without replayable proof
Stop if: any required verification row lacks executable evidence, the usefulness threshold cannot be recorded with attributable session rows, or the branch diff shows unapproved changes on deferred surfaces
Session boundary after: yes
Acceptance Criteria:
- The walkthrough becomes the single closure artifact for the `Usefulness Evidence Log`, verification matrix evidence pointers, audit disposition ledger, and must-ship versus deferred scope proof.
- The `Usefulness Evidence Log` format records at least the PRD-approved row fields and fails closed unless 5-10 attributable sessions are logged, with at least 5 rows meeting the success threshold before any ship recommendation.
- Closure proof records the exact baseline SHA used for scope review, then names exact deferred surfaces to inspect, including `frontend/src/app/app/reviews/page.tsx`, `frontend/src/app/api/bff/reviews/route.ts`, and any other branch-touched review surfaces outside the approved wedge.
- Every verification row remains explicit `pass`, `fail`, or approved `skipped` with a concrete evidence pointer; no row may be silently inferred from narrative prose.
TDD Plan:
- N/A for the gate itself; this task consumes the RED/GREEN proofs from Tasks 1-7 and fails closed if any required evidence remains missing or inconclusive.
Verification Steps:
- `git log --oneline main...HEAD`
- `git merge-base main HEAD`
- `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/page.tsx frontend/src/app/api/bff/reviews/route.ts frontend/src/app/app/reviews/'[reviewId]'/page.tsx frontend/src/app/api/bff/reviews/'[reviewId]'/route.ts`
- `cd backend && uv run pytest tests/test_api.py::test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation tests/test_api.py::test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors tests/test_api.py::test_wf0080_review_detail_emits_bounded_detail_projection tests/test_api.py::test_wf0080_review_detail_projection_uses_existing_order_tiebreaker tests/test_api.py::test_wf0080_invited_submit_reaches_detail_projection`
- `cd backend && uv run pytest tests/test_api.py::test_wf0080_trace_correlation_is_present_on_submit_and_detail tests/test_api.py::test_wf0080_trace_support_does_not_create_new_storage_surface`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/structured-review/route.test.ts' -t '^(wf0080_bff_submit_blocks_out_of_cohort_before_proxy|wf0080_bff_submit_preserves_trace_headers_for_support)$'`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t '^wf0080_bff_review_detail_preserves_backend_projection$'`
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t '^(wf0080_review_detail_renders_top_action_cards_first|wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success|wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default|wf0080_review_detail_handles_pending_timeout_and_failure_honestly|wf0080_review_detail_export_copy_stays_truthful_about_projection_scope)$'`
- `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/page.tsx frontend/src/app/api/bff/reviews/route.ts backend/app/repositories frontend/src/app/app/history`
- `cd docs && rg -n "Usefulness Evidence Log|Verification Matrix|Audit Disposition Ledger|must-ship|deferred|pass|fail|skipped" walkthroughs/walkthrough-WF-0080-production-mvp-launch-wedge.md`
Risks (if any): Without an explicit closure artifact, Phase 3 could claim launch readiness while usefulness evidence, scope proof, or fail-closed verification is still aspirational.

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Happy-path submit-to-detail wedge proof | 1, 2, 3, 4, 5 | `test_wf0080_invited_submit_reaches_detail_projection`, `wf0080_bff_review_detail_preserves_backend_projection`, `wf0080_review_detail_renders_top_action_cards_first` | invited in-cohort researcher can submit, wait honestly, and open the bounded detail view | `fail` (default until executed) | required | must stay locked to `ERC-2026-PoC` |
| Backend cohort gate fail-closed proof | 1 | `test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation` | out-of-cohort direct signed users are rejected before review creation | `fail` (default until executed) | required | zero-side-effect rejection on backend seam |
| BFF cohort gate fail-closed proof | 2 | `wf0080_bff_submit_blocks_out_of_cohort_before_proxy` | out-of-cohort users are rejected before proxying | `fail` (default until executed) | required | zero-side-effect rejection on BFF seam |
| Quota/reviews-disabled preservation proof | 1 | `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors` | existing quota and disable gates still behave truthfully for in-cohort users | `fail` (default until executed) | required | cost/safety guard stays intact |
| Review-detail projection proof | 3 | `test_wf0080_review_detail_emits_bounded_detail_projection`, `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker` | backend detail response exposes the exact bounded projection contract | `fail` (default until executed) | required | backend is single ranking seam |
| BFF passthrough proof | 4 | `wf0080_bff_review_detail_preserves_backend_projection` | BFF preserves `detail_projection` without semantic rewrite | `fail` (default until executed) | required | no frontend-local ranking |
| Top-action render proof | 5 | `wf0080_review_detail_renders_top_action_cards_first` | top 1-3 prioritized cards render above the fold in backend order | `fail` (default until executed) | required | one action-first reading model only |
| Positive-state proof | 5 | `wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success` | explicit positive headline appears only for the approved all-assessed note/success condition | `fail` (default until executed) | required | no false reassurance |
| Evidence-collapse proof | 5 | `wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default` | supporting evidence stays collapsed by default with per-card expansion | `fail` (default until executed) | required | first card still explains rank |
| Timeout/degradation honesty proof | 5 | `wf0080_review_detail_handles_pending_timeout_and_failure_honestly` | pending, timeout, failed, and retry states remain explicit and truthful | `fail` (default until executed) | required | no silent success implication |
| Export/copy truthfulness proof | 5 | `wf0080_review_detail_export_copy_stays_truthful_about_projection_scope` | page-local export/copy behavior is explicit about any excluded projection framing | `fail` (default until executed) | required | same-page truthfulness only |
| Backend support trace proof | 6 | `test_wf0080_trace_correlation_is_present_on_submit_and_detail` | one disputed cohort session can be explained from bounded backend-owned support evidence | `fail` (default until executed) | required | no new telemetry product |
| BFF submit trace proof | 7 | `wf0080_bff_submit_preserves_trace_headers_for_support` | BFF submit path preserves the approved support trace correlation without reinterpretation | `fail` (default until executed) | required | no second trace namespace |
| Privacy/retention proof | 6, 8 | `test_wf0080_trace_support_does_not_create_new_storage_surface`, walkthrough privacy section check | launch-session text remains only in approved review/support traces with limited access | `fail` (default until executed) | required | no new storage class |
| Usefulness gate proof | 8 | walkthrough `Usefulness Evidence Log` | at least 5 attributable sessions are completed, rated useful, and name a next revision action | `fail` (default until executed) | required | 5-10 rows total required |
| Scope proof | 8 | `git merge-base main HEAD`, `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/page.tsx frontend/src/app/api/bff/reviews/route.ts backend/app/repositories frontend/src/app/app/history`, walkthrough deferred-surface check | must-ship stays in wedge and deferred surfaces remain unchanged unless explicitly approved | `fail` (default until executed) | required | fail closed on scope drift with recorded baseline SHA |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Verification-matrix rows for happy-path, export/copy, privacy, and scope proof used narrative placeholders instead of exact selectors or commands | non-blocking | replace every vague proof row with replayable test IDs or shell commands and mirror them in the closure-gate verification steps | closed | keeps all must-ship rows Phase 3 executable |
| Phase 2.2 task review | The early tracer bullet did not explicitly prove one invited submit-to-detail story on its own | non-blocking | promote the backend detail-projection slice into an explicit invited submit-to-detail tracer bullet and add one targeted backend selector for it | closed | Task 3 now carries the early end-to-end story proof without widening scope |
| Phase 2.2 task review | The supportability/privacy slice mixed trace intent with no concrete no-new-storage proof or additive-only contract statement | non-blocking | add a dedicated privacy/no-new-storage selector and state that trace metadata is additive-only to the approved public contract | closed | reduces hidden coupling between support traces and wedge scope |
| Review-and-harden adversarial audit | The cohort-access and support-trace slices crossed backend+BFF code and test seams, which would force Phase 3 to violate the repo’s atomic `<=3`-file task rule | blocking | split the backend and BFF gate/trace work into separate sequential tasks so each slice stays independently testable and verifiable | closed | Tasks 1/2 and 6/7 now preserve the gate/trace contracts without multi-surface task spillover |
| Review-and-harden adversarial audit | The support-trace task implied end-to-end detail correlation without a fail-closed rule preventing accidental public-contract widening or local BFF reinterpretation | blocking | tighten Task 6 with an additive-only stop condition, keep backend-owned trace truth bounded, and keep BFF trace work to passthrough only | closed | prevents Phase 3 from inventing a second trace model or widening the detail payload casually |
| Review-and-harden adversarial audit | Backend verification commands still relied on broad `pytest -k` filters instead of replayable exact node IDs | non-blocking | replace broad backend filters with exact `pytest` node IDs in each affected task and in the closure gate | closed | keeps row-level proof deterministic as the test file grows |
| Review-and-harden adversarial audit | Scope proof did not require recording an explicit baseline SHA before deferred-surface inspection | non-blocking | add a baseline-SHA capture step to Task 8 and reference it directly in the scope-proof row | closed | makes later scope review auditable even after multiple implementation commits |

## Changelog

- v0.1 (2026-03-14): Initial task breakdown from PRD.
- v0.2 (2026-03-14): Applied Part B feedback by promoting Task 2 into the explicit invited submit-to-detail tracer bullet, replacing vague verification rows with exact selectors/commands, and tightening Task 5/Task 6 fail-closed privacy and scope proof.
- v0.3 (2026-03-14): Applied review-and-harden findings by splitting cross-surface gate/trace work into atomic tasks, tightening backend-versus-BFF trace ownership, replacing broad backend test filters with exact node IDs, and requiring an explicit baseline SHA for scope proof.
