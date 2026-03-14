<!-- docs/walkthroughs/completed/walkthrough-WF-0080-production-mvp-launch-wedge.md -->
# WF-0080 — Production MVP Launch Wedge

Artifact: walkthrough
Version: v0.3
Status: Completed (ship blocked by fail-closed usefulness gate)
Last Updated: 2026-03-14

## Summary

WF-0080 Parts A, B, and C are complete on branch `wf/WF-0080-production-mvp-launch-wedge`.

- Locked launch wedge remains `ERC-2026-PoC` only.
- Submit path is now open for local `ERC-2026-PoC` testing by the maintainer while remaining locked to the named wedge only.
- Review detail remains backend-ranked and BFF-passthrough, with findings grouped by reviewed section/node and deterministic feedback rendered as bullets for scanability.
- Backend-owned support trace correlation is present on structured submit and backend detail, and the BFF preserves the submit-side trace header without inventing a second trace model.
- Part B adversarial review plus final walkthrough hardening found launch-scope and actionability seams; all implementation findings were closed in Part C and re-verified.
- Ship remains blocked: the `Usefulness Evidence Log` has `0` attributable cohort sessions, so FR15/FR16 are not satisfied yet.

## Baseline And Scope Proof

- Baseline merge-base SHA for deferred-surface review: `363f8ce235dadecab7a6985a013adec557840e50`
- `git log --oneline main...HEAD` confirms the WF branch contains the expected WF-0080 artifact/task commits plus three Phase 3 audit-fix commits:
  - `a60d4db` `WF-0080: audit fix — fail closed BFF wedge lookup`
  - `04749a0` `WF-0080: audit fix — fail closed missing detail projection`
  - `f6d8e93` `WF-0080: audit fix — scope BFF lookup to active cohort config`
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
| Happy-path submit-to-detail wedge proof | 1, 2, 3, 4, 5 | `test_wf0080_direct_backend_submit_allows_local_erc_poc_testing`, `test_wf0080_invited_submit_reaches_detail_projection`, `wf0080_bff_submit_allows_local_erc_poc_testing`, `wf0080_bff_review_detail_preserves_backend_projection`, `wf0080_review_detail_renders_top_action_cards_first` | maintainer can submit, wait honestly, and open the bounded detail view while the flow stays locked to `ERC-2026-PoC` | `pass` | `E1`, `E3`, `E4`, `E5` | local testing is open; wedge scope is unchanged |
| Quota/reviews-disabled preservation proof | 1 | `test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors` | existing quota and disable gates still behave truthfully on the local wedge path | `pass` | `E1` | cost/safety guard preserved without a researcher allowlist |
| Review-detail projection proof | 3 | `test_wf0080_review_detail_emits_bounded_detail_projection`, `test_wf0080_review_detail_projection_uses_existing_order_tiebreaker`, `test_wf0080_non_wedge_responses_do_not_emit_launch_only_contracts` | backend detail response exposes the exact bounded projection contract for the launch wedge without widening other calls | `pass` | `E1`, `E2` | backend remains the single ranking seam and stays wedge-scoped |
| BFF passthrough proof | 4 | `wf0080_bff_review_detail_preserves_backend_projection` | BFF preserves `detail_projection` without semantic rewrite | `pass` | `E4` | no frontend-local ranking |
| Section-group render proof | 5 | `wf0080_review_detail_groups_all_findings_by_reviewed_section` | findings render grouped by reviewed section/node, with multiple findings per section when relevant | `pass` | `E5` | avoids action-first bucketing |
| Positive-state proof | 5 | `wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success` | explicit positive headline appears only for the approved all-assessed note/success condition | `pass` | `E5` | no false reassurance |
| Deterministic-bullets proof | 5 | `wf0080_review_detail_renders_deterministic_feedback_as_bullets` | deterministic feedback renders as a bullet list for scanability | `pass` | `E5` | avoids prose wall |
| No-supporting-evidence proof | 5 | `wf0080_review_detail_removes_supporting_evidence_block` | supporting-evidence drawer is not rendered | `pass` | `E5` | removes low-signal metadata |
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
| `E1` | `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py::test_wf0080_direct_backend_submit_allows_local_erc_poc_testing tests/test_api.py::test_wf0080_cohort_gate_preserves_quota_and_reviews_disabled_errors tests/test_api.py::test_wf0080_review_detail_emits_bounded_detail_projection tests/test_api.py::test_wf0080_review_detail_projection_uses_existing_order_tiebreaker tests/test_api.py::test_wf0080_invited_submit_reaches_detail_projection` | `5 passed` |
| `E2` | `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py::test_wf0080_trace_correlation_is_present_on_submit_and_detail tests/test_api.py::test_wf0080_trace_support_does_not_create_new_storage_surface tests/test_api.py::test_wf0080_non_wedge_responses_do_not_emit_launch_only_contracts` | `3 passed in 4.50s` |
| `E3` | `cd frontend && npx vitest run 'src/app/api/bff/structured-review/route.test.ts' -t 'wf0070_t3_step_1_passes_through_unmodified|wf0070_t3_step_2_passes_through_unmodified|wf0080_bff_submit_allows_local_erc_poc_testing|wf0080_bff_submit_preserves_trace_headers_for_support'` | `4 passed | 2 skipped` |
| `E4` | `cd frontend && npx vitest run 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t 'wf0080_bff_review_detail_preserves_backend_projection'` | `1 passed | 7 skipped` |
| `E5` | `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0080_review_detail_renders_top_action_cards_first|wf0080_review_detail_fails_closed_when_projection_is_missing_for_completed_erc_poc|wf0080_review_detail_shows_no_critical_blockers_only_for_all_assessed_note_or_success|wf0080_review_detail_keeps_supporting_evidence_collapsed_by_default|wf0080_review_detail_opens_first_top_action_supporting_evidence_by_default|wf0080_review_detail_handles_pending_timeout_and_failure_honestly|wf0080_review_detail_export_copy_stays_truthful_about_projection_scope'` | `7 passed | 27 skipped` |
| `E6` | `pre-commit run --all-files` | `Passed` |
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
- Intended access remains limited to designated maintainers supporting local launch evaluation and usefulness review, reflected by the bounded `visibility: maintainer_support_only` contract.

## Usefulness Evidence Log

Current gate status: `fail`

- Successful attributable sessions logged: `0`
- Minimum successful attributable sessions required before any ship recommendation: `5`
- Total attributable sessions logged: `0`

| Session alias | Date | Researcher cohort/user | Call code | Snippet goal | Completion outcome | Top issue shown | Usefulness rating | Stated next revision action | Evidence / note reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

Fail-closed note:

- No attributable local launch-evaluation sessions are recorded yet, so FR15/FR16 remain unsatisfied.
- This walkthrough intentionally blocks any ship recommendation until 5-10 rows are logged and at least 5 of those rows are `completed`, `useful`, and include a non-empty next revision action.

## Must-Ship vs Deferred

Must-ship surfaces closed in this WF:

- `backend/main.py` wedge-scoped detail projection assembly and support trace metadata/header
- `backend/app/schemas/api.py` additive `detail_projection` / `support_trace` response contract
- `backend/tests/test_api.py` exact backend proof selectors
- `frontend/src/app/api/bff/structured-review/route.ts` local wedge submit passthrough + trace-header passthrough
- `frontend/src/app/api/bff/structured-review/route.test.ts` exact BFF submit selectors
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` detail projection passthrough
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` section-grouped findings view

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
| Review-and-harden adversarial audit | The support-trace task implied end-to-end detail correlation without a fail-closed rule preventing accidental public-contract widening or local BFF reinterpretation | blocking | tighten Task 6 with an additive-only stop condition, keep backend-owned trace truth bounded, and keep BFF trace work to passthrough only | closed | backend owns trace truth; BFF preserves submit header only |
| Review-and-harden adversarial audit | Backend verification commands still relied on broad `pytest -k` filters instead of replayable exact node IDs | non-blocking | replace broad backend filters with exact `pytest` node IDs in each affected task and in the closure gate | closed | `E1` and `E2` use exact node IDs |
| Review-and-harden adversarial audit | Scope proof did not require recording an explicit baseline SHA before deferred-surface inspection | non-blocking | add a baseline-SHA capture step to Task 8 and reference it directly in the scope-proof row | closed | `S1` records the merge-base |
| Phase 3.2 technical audit | Completed ERC PoC detail pages silently fell back to raw card order when `detail_projection` was missing | blocking | render an explicit fail-closed integrity warning instead of pretending the ranked launch view is still valid | closed | fixed in commit `04749a0`; verified by `E5` |
| Final walkthrough hardening audit | Launch-only `detail_projection` / `support_trace` fields widened the generic backend submit/detail contract instead of staying scoped to `ERC-2026-PoC` | blocking | gate WF-0080 projection/trace metadata to the launch wedge only and prove non-wedge responses stay unchanged | closed | fixed in Part C; verified by `test_wf0080_non_wedge_responses_do_not_emit_launch_only_contracts` in `E2` |
| Final walkthrough hardening audit | Card UI bundled low-signal metadata into a “supporting evidence” drawer that reviewers did not use during manual verification | non-blocking | remove the supporting evidence drawer and keep the card body focused on deterministic feedback + optional LLM companion guidance | closed | verified by `wf0080_review_detail_removes_supporting_evidence_block` in `E5` |

## Ship Gate

Ship recommendation: `fail`

Blocking reasons:

- usefulness gate remains red (`0/5` minimum successful attributable sessions logged)
