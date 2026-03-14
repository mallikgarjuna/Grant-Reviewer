<!-- docs/walkthroughs/walkthrough-WF-0080-production-mvp-launch-wedge.md -->
# WF-0080 — Production MVP Launch Wedge

Artifact: walkthrough
Version: v0.1
Status: Drafted (fail-closed usefulness gate)
Last Updated: 2026-03-14

## Summary

WF-0080 Part A scope is implemented through Tasks 1-8 on branch `wf/WF-0080-production-mvp-launch-wedge`.

- Locked launch wedge remains `ERC-2026-PoC` only.
- Submit fail-closed cohort gates now hold at both backend and BFF seams.
- Review detail remains backend-ranked and BFF-passthrough, with the action-first page rendering verified by exact selectors.
- Backend-owned support trace correlation is present on structured submit and backend detail, and the BFF preserves the submit-side trace header without inventing a second trace model.
- Ship remains blocked: the `Usefulness Evidence Log` has `0` attributable cohort sessions, so FR15/FR16 are not satisfied yet.

## Baseline And Scope Proof

- Baseline merge-base SHA for deferred-surface review: `363f8ce235dadecab7a6985a013adec557840e50`
- `git log --oneline main...HEAD` confirms the WF branch contains the expected WF-0080 artifact and task commits through Task 7 plus earlier planning commits.
- `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/'[reviewId]'/page.tsx frontend/src/app/api/bff/reviews/'[reviewId]'/route.ts` output:
  - `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/page.tsx frontend/src/app/api/bff/reviews/route.ts backend/app/repositories frontend/src/app/app/history` output: no files

Must-ship proof:

- Changed review surfaces remain inside the approved wedge detail page and detail BFF route only.
- Deferred surfaces called out in the PRD/tasks remain untouched in the current branch diff:
  - `frontend/src/app/app/reviews/page.tsx`
  - `frontend/src/app/api/bff/reviews/route.ts`
  - `backend/app/repositories/`
  - `frontend/src/app/app/history/`

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Happy-path submit-to-detail wedge proof | 1, 2, 3, 4, 5 | `test_wf0080_invited_submit_reaches_detail_projection`, `wf0080_bff_review_detail_preserves_backend_projection`, `wf0080_review_detail_renders_top_action_cards_first` | invited in-cohort researcher can submit, wait honestly, and open the bounded detail view | `pass` | `E1`, `E4`, `E5` | remains locked to `ERC-2026-PoC` |
| Backend cohort gate fail-closed proof | 1 | `test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation` | out-of-cohort direct signed users are rejected before review creation | `pass` | `E1` | reject path stayed header-additive only after Task 8 verification tightened the details payload back to Task 1 reality |
| BFF cohort gate fail-closed proof | 2 | `wf0080_bff_submit_blocks_out_of_cohort_before_proxy` | out-of-cohort users are rejected before proxying | `pass` | `E3` | zero downstream proxy side effects |
| Quota/reviews-disabled preservation proof | 1 | `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors` | existing quota and disable gates still behave truthfully for in-cohort users | `pass` | `E1` | cost/safety guard preserved |
| Review-detail projection proof | 3 | `test_wf0080_review_detail_emits_bounded_detail_projection`, `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker` | backend detail response exposes the exact bounded projection contract | `pass` | `E1` | backend remains the single ranking seam |
| BFF passthrough proof | 4 | `wf0080_bff_review_detail_preserves_backend_projection` | BFF preserves `detail_projection` without semantic rewrite | `pass` | `E4` | no frontend-local ranking |
| Top-action render proof | 5 | `wf0080_review_detail_renders_top_action_cards_first` | top 1-3 prioritized cards render above the fold in backend order | `pass` | `E5` | action-first read model holds |
| Positive-state proof | 5 | `wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success` | explicit positive headline appears only for the approved all-assessed note/success condition | `pass` | `E5` | no false reassurance |
| Evidence-collapse proof | 5 | `wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default` | supporting evidence stays collapsed by default with per-card expansion | `pass` | `E5` | first ranked card still explains itself above the fold |
| Timeout/degradation honesty proof | 5 | `wf0080_review_detail_handles_pending_timeout_and_failure_honestly` | pending, timeout, failed, and retry states remain explicit and truthful | `pass` | `E5` | no silent success implication |
| Export/copy truthfulness proof | 5 | `wf0080_review_detail_export_copy_stays_truthful_about_projection_scope` | page-local export/copy behavior is explicit about any excluded projection framing | `pass` | `E5` | same-page truthfulness only |
| Backend support trace proof | 6 | `test_wf0080_trace_correlation_is_present_on_submit_and_detail` | one disputed cohort session can be explained from bounded backend-owned support evidence | `pass` | `E2` | trace contract is deterministic and derived from existing review/request identifiers |
| BFF submit trace proof | 7 | `wf0080_bff_submit_preserves_trace_headers_for_support` | BFF submit path preserves the approved support trace correlation without reinterpretation | `pass` | `E3` | no second trace namespace |
| Privacy/retention proof | 6, 8 | `test_wf0080_trace_support_does_not_create_new_storage_surface`, walkthrough privacy section check | launch-session text remains only in approved review/support traces with limited access | `pass` | `E2`, `P1` | no new storage class introduced |
| Usefulness gate proof | 8 | walkthrough `Usefulness Evidence Log` | at least 5 attributable sessions are completed, rated useful, and name a next revision action | `fail` | `U1` | `0/5` minimum successful sessions logged; no ship recommendation allowed |
| Scope proof | 8 | `git merge-base main HEAD`, deferred-surface `git diff --name-only ...` checks | must-ship stays in wedge and deferred surfaces remain unchanged unless explicitly approved | `pass` | `S1`, `S2`, `S3` | fail-closed diff review completed against baseline SHA |

## Verification Evidence

| Evidence ID | Command / artifact | Outcome |
| :--- | :--- | :--- |
| `E1` | `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py::test_wf0080_cohort_gate_blocks_direct_backend_submit_before_review_creation tests/test_api.py::test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors tests/test_api.py::test_wf0080_review_detail_emits_bounded_detail_projection tests/test_api.py::test_wf0080_review_detail_projection_uses_existing_order_tiebreaker tests/test_api.py::test_wf0080_invited_submit_reaches_detail_projection` | `5 passed in 3.68s` |
| `E2` | `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py::test_wf0080_trace_correlation_is_present_on_submit_and_detail tests/test_api.py::test_wf0080_trace_support_does_not_create_new_storage_surface` | `2 passed in 2.66s` |
| `E3` | `cd frontend && npx vitest run 'src/app/api/bff/structured-review/route.test.ts' -t 'wf0080_bff_submit_blocks_out_of_cohort_before_proxy|wf0080_bff_submit_preserves_trace_headers_for_support'` | `2 passed | 4 skipped` |
| `E4` | `cd frontend && npx vitest run 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t 'wf0080_bff_review_detail_preserves_backend_projection'` | `1 passed | 7 skipped` |
| `E5` | `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0080_review_detail_renders_top_action_cards_first|wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success|wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default|wf0080_review_detail_handles_pending_timeout_and_failure_honestly|wf0080_review_detail_export_copy_stays_truthful_about_projection_scope'` | `5 passed | 27 skipped` |
| `S1` | `git merge-base main HEAD` | `363f8ce235dadecab7a6985a013adec557840e50` |
| `S2` | `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/'[reviewId]'/page.tsx frontend/src/app/api/bff/reviews/'[reviewId]'/route.ts` | only the approved wedge detail page and detail BFF route differ |
| `S3` | `git diff --name-only main...HEAD -- frontend/src/app/app/reviews/page.tsx frontend/src/app/api/bff/reviews/route.ts backend/app/repositories frontend/src/app/app/history` | no output |
| `P1` | code + test reading from Task 6 | `support_trace` is response/header-only metadata; `test_wf0080_trace_support_does_not_create_new_storage_surface` proves no `support_trace` fields are persisted into structured payload storage |
| `U1` | walkthrough `Usefulness Evidence Log` | fail-closed: no attributable launch cohort sessions logged yet |

## Privacy / Retention

- Launch-session inputs and outputs remain in existing review storage only.
- The added `support_trace` metadata is bounded to:
  - `contract`
  - `trace_id`
  - `visibility`
- The support trace is derived from existing review/request identifiers; it does not persist new launch-session text or create a new storage class.
- Intended access remains limited to designated maintainers supporting the launch cohort and usefulness review, reflected by the bounded `visibility: maintainer_support_only` contract.

## Usefulness Evidence Log

Current gate status: `fail`

- Successful attributable sessions logged: `0`
- Minimum successful attributable sessions required before any ship recommendation: `5`
- Total attributable sessions logged: `0`

| Session alias | Date | Researcher cohort/user | Call code | Snippet goal | Completion outcome | Top issue shown | Usefulness rating | Stated next revision action | Evidence / note reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

Fail-closed note:

- No attributable launch-cohort sessions are recorded yet, so FR15/FR16 remain unsatisfied.
- This walkthrough intentionally blocks any ship recommendation until 5-10 rows are logged and at least 5 of those rows are `completed`, `useful`, and include a non-empty next revision action.

## Must-Ship vs Deferred

Must-ship surfaces closed in this WF:

- `backend/main.py` cohort gate, detail projection assembly, and support trace metadata/header
- `backend/app/schemas/api.py` additive `detail_projection` / `support_trace` response contract
- `backend/tests/test_api.py` exact backend proof selectors
- `frontend/src/app/api/bff/structured-review/route.ts` fail-closed submit gate + trace-header passthrough
- `frontend/src/app/api/bff/structured-review/route.test.ts` exact BFF submit selectors
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` detail projection passthrough
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` action-first detail read model

Deferred surfaces still out of scope for WF-0080:

- review list/history redesign
- generalized export redesign
- multi-call rollout beyond `ERC-2026-PoC`
- admin/onboarding/replay products
- new review persistence hierarchies or frontend/BFF-local ranking semantics

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Verification-matrix rows for happy-path, export/copy, privacy, and scope proof used narrative placeholders instead of exact selectors or commands | non-blocking | replace every vague proof row with replayable test IDs or shell commands and mirror them in the closure-gate verification steps | closed | completed in task plan and reflected in `E1`-`E5`, `S1`-`S3` |
| Phase 2.2 task review | The early tracer bullet did not explicitly prove one invited submit-to-detail story on its own | non-blocking | promote the backend detail-projection slice into an explicit invited submit-to-detail tracer bullet and add one targeted backend selector for it | closed | covered by `test_wf0080_invited_submit_reaches_detail_projection` in `E1` |
| Phase 2.2 task review | The supportability/privacy slice mixed trace intent with no concrete no-new-storage proof or additive-only contract statement | non-blocking | add a dedicated privacy/no-new-storage selector and state that trace metadata is additive-only to the approved public contract | closed | covered by `E2` and Privacy / Retention |
| Review-and-harden adversarial audit | The cohort-access and support-trace slices crossed backend+BFF code and test seams, which would force Phase 3 to violate the repo’s atomic `<=3`-file task rule | blocking | split the backend and BFF gate/trace work into separate sequential tasks so each slice stays independently testable and verifiable | closed | Tasks 1/2 and 6/7 stayed atomic |
| Review-and-harden adversarial audit | The support-trace task implied end-to-end detail correlation without a fail-closed rule preventing accidental public-contract widening or local BFF reinterpretation | blocking | tighten Task 6 with an additive-only stop condition, keep backend-owned trace truth bounded, and keep BFF trace work to passthrough only | closed | backend owns trace truth; BFF preserves submit header only |
| Review-and-harden adversarial audit | Backend verification commands still relied on broad `pytest -k` filters instead of replayable exact node IDs | non-blocking | replace broad backend filters with exact `pytest` node IDs in each affected task and in the closure gate | closed | `E1` and `E2` use exact node IDs |
| Review-and-harden adversarial audit | Scope proof did not require recording an explicit baseline SHA before deferred-surface inspection | non-blocking | add a baseline-SHA capture step to Task 8 and reference it directly in the scope-proof row | closed | `S1` records the merge-base |
| Task 8 verification sweep | Initial Task 6 trace implementation widened the Task 1 rejection `details` payload and broke the exact backend cohort-gate selector | blocking | keep rejection support trace on the submit header only and preserve the prior error `details` contract | closed | fixed before final verification; `E1` and `E2` both pass together |

## Ship Gate

Ship recommendation: `fail`

Blocking reasons:

- usefulness gate remains red (`0/5` minimum successful attributable sessions logged)
- Part B technical audit review gate has not run yet
- Part C revise/verify/ship sequence is not complete yet
