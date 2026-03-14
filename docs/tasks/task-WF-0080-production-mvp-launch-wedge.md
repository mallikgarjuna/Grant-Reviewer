<!-- docs/tasks/task-WF-0080-production-mvp-launch-wedge.md -->
# WF-0080 — Production MVP Launch Wedge

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-14

Type: feature

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: lock fail-closed cohort submit gating on both entrypoints

Goal:
Prove the smallest production-wedge submit path for `ERC-2026-PoC` stays fail-closed by rejecting out-of-cohort traffic at both `/api/bff/structured-review` and `POST /api/structured-review` before review creation or downstream execution.
Slice: tracer-bullet
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR3, FR4, FR16
Depends on: none
Enables: 2, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/structured-review/route.ts`
- `backend/main.py`
- `backend/tests/test_api.py`
May touch files:
- `frontend/src/app/api/bff/structured-review/route.test.ts`
Out of scope: review-detail ranking, detail-page rendering, support walkthrough evidence, generalized onboarding/admin tooling
Stop if: cohort gating cannot be enforced before review creation on both entrypoints, requires widening beyond `ERC-2026-PoC`, or needs a second persistence/logging system to explain rejections
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions such as `test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation`, `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors`, and `wf0080_bff_submit_blocks_out_of_cohort_before_proxy` prove the current submit seam does not yet fail closed for launch-cohort access.
- After the change, invited in-cohort requests still reach the existing review creation path, while out-of-cohort requests return `COHORT_ACCESS_DENIED` before proxying or backend review creation side effects begin.
- Existing `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` behavior remains intact for in-cohort users and is not shadowed by the new gate.
- The task remains locked to the existing submit contract, idempotency behavior, and `ERC-2026-PoC` wedge only.
TDD Plan:
- RED: add `test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation` and `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors` in `backend/tests/test_api.py`, plus `wf0080_bff_submit_blocks_out_of_cohort_before_proxy` in `frontend/src/app/api/bff/structured-review/route.test.ts`, and run them before changing the submit seams so they fail.
- GREEN: add the minimum BFF and backend cohort gate checks needed to reject out-of-cohort traffic before any downstream review creation or proxying while preserving existing quota/review-disabled behavior.
- REFACTOR: extract one tiny shared gate helper only if the BFF/backend checks become unclear; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation or wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors"`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/structured-review/route.test.ts' -t 'wf0080_bff_submit_blocks_out_of_cohort_before_proxy'`
- `cd backend && rg -n "COHORT_ACCESS_DENIED|REVIEWS_DISABLED|QUOTA_EXCEEDED|structured-review" main.py tests/test_api.py`
Risks (if any): If the reject path is not truly pre-side-effect, Phase 3 could accidentally create costly reviews for blocked users.

### [ ] Task 2 — Add the bounded review-detail projection seam in backend detail assembly

Goal:
Create the one approved read-model seam by computing `detail_projection` inside `GET /reviews/{review_id}` from persisted `ReviewCard` truth and existing call/node order only.
Slice: backend-detail-projection
User Stories: US1, US2, US3
PRD Requirements: FR6, FR7, FR8, FR10, FR11, FR16
Depends on: 1
Enables: 3, 4, 5
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
- Targeted failing regressions such as `test_wf0080_review_detail_emits_bounded_detail_projection` and `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker` prove the current response lacks the approved projection contract and ranking semantics.
- After the change, `ReviewDetailResponse.detail_projection` exposes exactly `version`, `headline_state`, `ordered_card_ids`, `top_action_card_ids`, and `ranking_basis`, with `top_action_card_ids` bounded to at most 3 cards.
- Ranking is derived only from `assessment_status`, then rating order `CRITICAL -> WARNING -> NOTE -> SUCCESS`, then existing call/node order; no BFF or frontend recomputation is required.
- `headline_state` becomes `no_critical_blockers` only when every card is `ASSESSED` and every rating is `NOTE` or `SUCCESS`; any `NOT_ASSESSABLE`, `CRITICAL`, or `WARNING` keeps `action_required`.
TDD Plan:
- RED: add `test_wf0080_review_detail_emits_bounded_detail_projection` and `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker` in `backend/tests/test_api.py`; run them before backend contract changes so they fail.
- GREEN: add the minimal schema and response-assembly logic required to emit the additive `detail_projection` object directly from persisted card truth.
- REFACTOR: extract one tiny ranking helper only if response assembly becomes hard to read; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0080_review_detail_emits_bounded_detail_projection or wf0080_review_detail_projection_uses_existing_order_tiebreaker"`
- `cd backend && rg -n "detail_projection|top_action_card_ids|ranking_basis|no_critical_blockers" app/schemas/api.py main.py tests/test_api.py`
Risks (if any): If ranking semantics leak outside this seam, the wedge can drift into hidden coupling across backend, BFF, and UI.

### [ ] Task 3 — Preserve `detail_projection` across the BFF detail contract without reinterpretation

Goal:
Keep the backend read-model authoritative by passing `detail_projection` through the BFF detail route and frontend types unchanged.
Slice: bff-detail-contract
User Stories: US1, US2
PRD Requirements: FR10, FR11, FR16
Depends on: 2
Enables: 4, 5
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
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t 'wf0080_bff_review_detail_preserves_backend_projection'`
- `cd frontend && rg -n "detail_projection|top_action_card_ids|headline_state|ranking_basis" src/app/api/bff/reviews/'[reviewId]'/route.ts src/app/api/bff/reviews/'[reviewId]'/route.test.ts src/lib/bff/types.ts`
Risks (if any): A local BFF rewrite would make Phase 3 verification ambiguous and break the PRD’s single-seam constraint.

### [ ] Task 4 — Render the action-first detail page with honest pending, failure, and export truthfulness

Goal:
Implement the one approved researcher reading flow on `/app/reviews/[reviewId]`: top 1-3 prioritized cards above the fold, expandable evidence, honest pending/timeout/failure states, and explicit copy/export truthfulness.
Slice: detail-page-flow
User Stories: US1, US2
PRD Requirements: FR5, FR6, FR8, FR9, FR12, FR16
Depends on: 2, 3
Enables: 5
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
- After the change, only the backend-provided `top_action_card_ids` render above the fold by default, the first ranked card exposes enough summary context to justify rank, and supporting evidence stays collapsed until expanded per card.
- The page renders `no critical blockers found` only when the backend projection indicates `no_critical_blockers`; otherwise it stays action-oriented without implying success.
- Pending, timeout, failed, retry, and return-later states remain explicit and truthful, and page-local copy/export wording states any projection-only framing it excludes.
TDD Plan:
- RED: add `wf0080_review_detail_renders_top_action_cards_first`, `wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success`, `wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default`, and `wf0080_review_detail_handles_pending_timeout_and_failure_honestly` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`; run them before UI changes so they fail.
- GREEN: make the minimum page/component changes needed to consume `detail_projection`, render the top-action-first layout, and keep degraded states and copy/export messaging honest.
- REFACTOR: extract a tiny ordering/headline presentational helper only if the page diff becomes repetitive; otherwise skip.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0080_review_detail_renders_top_action_cards_first|wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success|wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default|wf0080_review_detail_handles_pending_timeout_and_failure_honestly'`
- `cd frontend && rg -n "top_action_card_ids|no critical blockers found|return later|still processing|supporting evidence" src/app/app/reviews/'[reviewId]'/page.tsx src/components/review/ReviewCard.tsx src/app/app/reviews/'[reviewId]'/page.test.tsx`
Risks (if any): If the page overstates completion or hides degraded states, the production wedge could mislead researchers during the launch cohort.

### [ ] Task 5 — Add bounded trace correlation and launch privacy guardrails for one disputed session

Goal:
Make one failed or disputed cohort session explainable end to end by adding narrow trace correlation across submit, review creation, and detail retrieval while preserving the PRD’s no-new-storage privacy rule.
Slice: support-trace
User Stories: US3, US4
PRD Requirements: FR13, FR14, FR16
Depends on: 1, 2, 3, 4
Enables: 6
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/structured-review/route.ts`
- `backend/main.py`
- `backend/tests/test_api.py`
May touch files:
- `frontend/src/app/api/bff/structured-review/route.test.ts`
Out of scope: analytics dashboards, admin consoles, replay tooling, new retention stores
Stop if: traceability requires a new data store, broad observability platform work, or storing launch-session text outside existing review storage and bounded support traces
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions such as `test_wf0080_trace_correlation_is_present_on_submit_and_detail` and `wf0080_bff_submit_preserves_trace_headers_for_support` prove the current wedge cannot yet explain one disputed session across BFF and backend seams.
- After the change, one bounded trace identifier or correlation tuple is emitted/preserved across submit rejection or creation paths and can be tied to later detail retrieval/support investigation without introducing a new storage class for researcher text.
- Verification proves the trace path does not widen access to review inputs/outputs beyond designated maintainers and existing review/support trace surfaces.
- The task stays limited to supportability for the launch wedge and does not introduce generalized telemetry or cohort-management products.
TDD Plan:
- RED: add `test_wf0080_trace_correlation_is_present_on_submit_and_detail` in `backend/tests/test_api.py` and `wf0080_bff_submit_preserves_trace_headers_for_support` in `frontend/src/app/api/bff/structured-review/route.test.ts`; run them before changing trace seams so they fail.
- GREEN: add the minimal trace correlation plumbing needed to connect submit and detail support evidence on existing surfaces only.
- REFACTOR: skip unless one tiny helper is needed to keep correlation-id naming consistent across the two seams.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0080_trace_correlation_is_present_on_submit_and_detail"`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/structured-review/route.test.ts' -t 'wf0080_bff_submit_preserves_trace_headers_for_support'`
- `cd backend && rg -n "trace|correlation|support" main.py tests/test_api.py`
Risks (if any): If trace evidence is too weak, operators will have to infer failures from unrelated logs and the wedge will not be honestly supportable.

### [ ] Task 6 — Close the must-ship gate with usefulness evidence, scope proof, and fail-closed verification rows

Goal:
Make the Phase 3 handoff executable and honest by turning the walkthrough into the required closure artifact for usefulness evidence, must-ship versus deferred proof, and row-level pass/fail verification.
Slice: closure-gate
User Stories: US3, US4
PRD Requirements: FR15, FR16
Depends on: 1, 2, 3, 4, 5
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
- Closure proof names exact deferred surfaces to inspect, including `frontend/src/app/app/reviews/page.tsx`, `frontend/src/app/api/bff/reviews/route.ts`, and any other branch-touched review surfaces outside the approved wedge.
- Every verification row remains explicit `pass`, `fail`, or approved `skipped` with a concrete evidence pointer; no row may be silently inferred from narrative prose.
TDD Plan:
- N/A for the gate itself; this task consumes the RED/GREEN proofs from Tasks 1-5 and fails closed if any required evidence remains missing or inconclusive.
Verification Steps:
- `git log --oneline main...HEAD`
- `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/page.tsx frontend/src/app/api/bff/reviews/route.ts frontend/src/app/app/reviews/'[reviewId]'/page.tsx frontend/src/app/api/bff/reviews/'[reviewId]'/route.ts`
- `cd backend && uv run pytest tests/test_api.py -k "wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation or wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors or wf0080_review_detail_emits_bounded_detail_projection or wf0080_review_detail_projection_uses_existing_order_tiebreaker or wf0080_trace_correlation_is_present_on_submit_and_detail"`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/structured-review/route.test.ts' -t 'wf0080_bff_submit_blocks_out_of_cohort_before_proxy|wf0080_bff_submit_preserves_trace_headers_for_support'`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t 'wf0080_bff_review_detail_preserves_backend_projection'`
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0080_review_detail_renders_top_action_cards_first|wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success|wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default|wf0080_review_detail_handles_pending_timeout_and_failure_honestly'`
- `cd docs && rg -n "Usefulness Evidence Log|Verification Matrix|Audit Disposition Ledger|must-ship|deferred|pass|fail|skipped" walkthroughs/walkthrough-WF-0080-production-mvp-launch-wedge.md`
Risks (if any): Without an explicit closure artifact, Phase 3 could claim launch readiness while usefulness evidence, scope proof, or fail-closed verification is still aspirational.

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Happy-path submit-to-detail wedge proof | 1, 2, 3, 4 | targeted backend/frontend selectors plus walkthrough evidence | invited in-cohort researcher can submit, wait honestly, and open the bounded detail view | `fail` (default until executed) | required | must stay locked to `ERC-2026-PoC` |
| Cohort gate fail-closed proof | 1 | `test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation`, `wf0080_bff_submit_blocks_out_of_cohort_before_proxy` | out-of-cohort users are rejected before proxy/review creation on both entrypoints | `fail` (default until executed) | required | zero-side-effect rejection |
| Quota/reviews-disabled preservation proof | 1 | `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors` | existing quota and disable gates still behave truthfully for in-cohort users | `fail` (default until executed) | required | cost/safety guard stays intact |
| Review-detail projection proof | 2 | `test_wf0080_review_detail_emits_bounded_detail_projection`, `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker` | backend detail response exposes the exact bounded projection contract | `fail` (default until executed) | required | backend is single ranking seam |
| BFF passthrough proof | 3 | `wf0080_bff_review_detail_preserves_backend_projection` | BFF preserves `detail_projection` without semantic rewrite | `fail` (default until executed) | required | no frontend-local ranking |
| Top-action render proof | 4 | `wf0080_review_detail_renders_top_action_cards_first` | top 1-3 prioritized cards render above the fold in backend order | `fail` (default until executed) | required | one action-first reading model only |
| Positive-state proof | 4 | `wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success` | explicit positive headline appears only for the approved all-assessed note/success condition | `fail` (default until executed) | required | no false reassurance |
| Evidence-collapse proof | 4 | `wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default` | supporting evidence stays collapsed by default with per-card expansion | `fail` (default until executed) | required | first card still explains rank |
| Timeout/degradation honesty proof | 4 | `wf0080_review_detail_handles_pending_timeout_and_failure_honestly` | pending, timeout, failed, and retry states remain explicit and truthful | `fail` (default until executed) | required | no silent success implication |
| Export/copy truthfulness proof | 4 | detail-page selector plus walkthrough copy evidence | page-local export/copy behavior is explicit about any excluded projection framing | `fail` (default until executed) | required | same-page truthfulness only |
| Support trace proof | 5 | `test_wf0080_trace_correlation_is_present_on_submit_and_detail`, `wf0080_bff_submit_preserves_trace_headers_for_support` | one disputed cohort session can be explained from bounded support evidence | `fail` (default until executed) | required | no new telemetry product |
| Privacy/retention proof | 5, 6 | code/config evidence plus walkthrough privacy section | launch-session text remains only in approved review/support traces with limited access | `fail` (default until executed) | required | no new storage class |
| Usefulness gate proof | 6 | walkthrough `Usefulness Evidence Log` | at least 5 attributable sessions are completed, rated useful, and name a next revision action | `fail` (default until executed) | required | 5-10 rows total required |
| Scope proof | 6 | branch-diff inspection plus walkthrough deferred-surface check | must-ship stays in wedge and deferred surfaces remain unchanged unless explicitly approved | `fail` (default until executed) | required | fail closed on scope drift |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | none yet | `N/A` | pending | open | to be populated in Part C if review finds issues |

## Changelog

- v0.1 (2026-03-14): Initial task breakdown from PRD.
