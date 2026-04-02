<!-- docs/walkthroughs/walkthrough-WF-0081-atomic-findings-structured-review.md -->
# WF-0081 — Atomic Findings Structured Review

Artifact: walkthrough
Version: v0.1
Status: Ready for Technical Audit
Last Updated: 2026-04-02

Type: feature

---

## Summary

WF-0081 adds an explicit mixed-rollout review-detail contract:

- legacy reviews keep reading and rendering from `ReviewCard` with `detail_mode="legacy_cards"`
- new atomic reviews use `reviewed_nodes[].findings[]` with `detail_mode="reviewed_node_findings"`
- researcher-facing copy uses evaluation criteria/elements terminology throughout the review detail page

## Baseline and Commit Range

- Merge-base SHA versus `main`: `1c7df35406658e9a62277c8eb93def9c0d425b25`
- Resume baseline SHA for this Part A continuation: `60c2a9c`
- Current implementation SHA at Task 7 closure gate: `418a622328ea5a7a0cef90dd86080fdd75c89fbe`
- WF commit range in `main...HEAD` at Task 7 closure:
  - `697e0c1` Task 1
  - `6ba6563` Task 2
  - `8708414` Task 3
  - `60c2a9c` Task 4
  - `4074413` baseline repair for explicit `detail_mode` in a no-db contract test
  - `4e940cb` Task 5
  - `418a622` Task 6

## Scope Closure

- Approved mixed-rollout implementation surfaces in `main...HEAD`:
  - `backend/app/models/domain.py`
  - `backend/app/services/structured_reviewer_service.py`
  - `backend/main.py`
  - `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
  - `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- Deferred out-of-scope list/history surfaces checked during Task 7 and untouched in `main...HEAD`:
  - `frontend/src/app/app/reviews/page.tsx`
  - `frontend/src/app/api/bff/reviews/route.ts`

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Persisted detail-mode discriminator proof | 1 | `test_wf0081_contract_review_storage_supports_detail_mode_and_findings` | reviews store an explicit primary detail mode instead of relying on read-time inference | `pass` | `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py -k "wf0081_contract_review_storage_supports_detail_mode_and_findings or wf0081_contract_migration_preserves_legacy_review_cards or wf0081_contract_review_detail_exposes_explicit_detail_mode or wf0081_contract_atomic_review_detail_groups_findings_under_reviewed_nodes or wf0081_contract_review_detail_modes_are_mutually_exclusive or wf0081_contract_review_detail_records_detail_mode_usage"` -> `6 passed, 162 deselected in 10.79s` | protects mixed rollout |
| Legacy migration safety proof | 1 | `test_wf0081_contract_migration_preserves_legacy_review_cards` | existing reviews/cards remain valid without backfill | `pass` | same backend API command as above | legacy cards stay readable |
| Atomic findings write-path proof | 2 | `test_wf0081_contract_atomic_review_persists_review_findings` | new atomic reviews persist one finding per reviewed-node plus evaluation-element outcome | `pass` | `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0081_contract_atomic_review_persists_review_findings or wf0081_contract_legacy_review_card_path_remains_unchanged or wf0081_contract_unmappable_diagnostic_finding_fails_closed or wf0081_contract_unmappable_diagnostic_finding_records_bounded_failure"` -> `4 passed, 50 deselected in 4.88s` | verified after rerunning alone to avoid transient DB deadlock from concurrent test-db seeding |
| Legacy compatibility separation proof | 2 | `test_wf0081_contract_legacy_review_card_path_remains_unchanged` | legacy review generation/reads remain on `ReviewCard` and do not require `ReviewFinding` | `pass` | same structured reviewer service command as above | no competing truths |
| Fail-closed mapping proof | 2 | `test_wf0081_contract_unmappable_diagnostic_finding_fails_closed` | unmappable diagnostic findings raise/log a bounded failure instead of being dropped silently | `pass` | same structured reviewer service command as above | closes the PRD edge case |
| Write-path failure telemetry proof | 2 | `test_wf0081_contract_unmappable_diagnostic_finding_records_bounded_failure` | bounded write-path failures are recorded on the agreed telemetry/logging seam | `pass` | same structured reviewer service command as above | closes PRD telemetry 9.2 |
| Backend dual-mode detail proof | 3 | `test_wf0081_contract_review_detail_exposes_explicit_detail_mode` | `GET /reviews/{review_id}` returns explicit `detail_mode` for every review | `pass` | same backend API command as above | no heuristics |
| Reviewed-node grouping proof | 3 | `test_wf0081_contract_atomic_review_detail_groups_findings_under_reviewed_nodes` | atomic responses group findings beneath reviewed nodes rather than flattening them | `pass` | same backend API command as above | primary researcher reading model |
| Single-mode invariant proof | 3 | `test_wf0081_contract_review_detail_modes_are_mutually_exclusive` | each review exposes one primary detail mode without requiring the other shape | `pass` | same backend API command as above | prevents mixed-contract drift |
| Detail-mode telemetry proof | 3 | `test_wf0081_contract_review_detail_records_detail_mode_usage` | backend response assembly records `legacy_cards` vs `reviewed_node_findings` usage from the explicit contract | `pass` | same backend API command as above | closes PRD telemetry 9.1 |
| BFF contract carry-through proof | 4 | `wf0081_bff_review_detail_preserves_explicit_detail_mode`, `wf0081_bff_review_detail_preserves_reviewed_node_findings`, `wf0081_bff_review_detail_preserves_backend_detail_metadata_verbatim` | BFF/types preserve the backend dual-mode contract verbatim without inventing local atomic semantics | `pass` | `cd frontend && npm run test:ui -- --testNamePattern='wf0081_bff_review_detail_preserves_explicit_detail_mode|wf0081_bff_review_detail_preserves_reviewed_node_findings|wf0081_bff_review_detail_preserves_backend_detail_metadata_verbatim|wf0081_review_detail_renders_grouped_reviewed_node_findings|wf0081_review_detail_legacy_cards_still_render_without_findings|wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful|wf0081_review_detail_requirements_met_render_without_empty_issue_shells|wf0081_review_detail_legacy_copy_and_export_remain_card_based'` -> `5 passed, 75 skipped` | page+BFF combined proof command reused repo test runner `npm run test:ui` because `npm test` is not defined in `frontend/package.json` |
| Legacy render continuity proof | 5 | `wf0081_review_detail_legacy_cards_still_render_without_findings` | legacy reviews still render from `ReviewCard` without placeholder findings | `pass` | same frontend combined proof command as above | backward compatibility |
| Atomic findings render proof | 5 | `wf0081_review_detail_renders_grouped_reviewed_node_findings` | atomic reviews render grouped findings with evaluation criteria/elements terminology | `pass` | same frontend combined proof command as above | no `rubric` copy |
| Positive-state truthfulness proof | 6 | `wf0081_review_detail_requirements_met_render_without_empty_issue_shells` | `REQUIREMENTS_MET` renders bounded positive guidance without empty issue placeholders | `pass` | same frontend combined proof command as above | keeps positive cases honest |
| Copy/export truthfulness proof | 6 | `wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful` | same-page actions stay truthful to the active detail mode | `pass` | same frontend combined proof command as above | no legacy text leakage |
| Legacy export continuity proof | 6 | `wf0081_review_detail_legacy_copy_and_export_remain_card_based` | atomic-mode truthfulness changes do not rewrite legacy review export semantics | `pass` | same frontend combined proof command as above | guards backward compatibility |
| Render/copy limitation telemetry disposition | 7 | walkthrough closure note | any temporary limitation telemetry is recorded, or the row is explicitly `skipped` with rationale when no limitation ships | `skipped` | no temporary render/copy limitation shipped in Tasks 5-6, so no limitation telemetry seam was added | PRD telemetry 9.3 is conditionally not needed here |
| Mixed-rollout closure proof | 7 | walkthrough verification matrix + scoped diff/test commands | implementation-ready claim is blocked until legacy and atomic compatibility evidence is recorded | `pass` | this walkthrough section plus `git log --oneline main...HEAD`, scoped `git diff --name-only main...HEAD ...`, backend API proof, backend service proof, and frontend combined proof | fail-closed closure gate satisfied before Part B |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Task 6 needed an explicit legacy copy/export regression in addition to atomic truthfulness work | non-blocking | landed `wf0081_review_detail_legacy_copy_and_export_remain_card_based` in Task 6 | closed | protects backward compatibility |
| Phase 2.2 task review | Task 2 needed fail-closed coverage when a diagnostic finding cannot resolve required snapshot fields | non-blocking | landed fail-closed + bounded failure telemetry regressions in Task 2 | closed | prevents silent finding loss |
| Phase 2.2 task review | Task 3 needed an explicit per-review mutual-exclusivity proof between legacy cards and reviewed-node findings | non-blocking | landed `test_wf0081_contract_review_detail_modes_are_mutually_exclusive` in Task 3 | closed | keeps the API contract single-mode |
| Phase 2.2 task review | Task 7 needed to name deferred reviews list/history surfaces | non-blocking | closure proof names `frontend/src/app/app/reviews/page.tsx` and `frontend/src/app/api/bff/reviews/route.ts` explicitly | closed | improves hidden-coupling detection |
| 2026-03-14 fail-closed adversarial review | Task 3 leaked same-page truthfulness into a backend-only slice | blocking | same-page truthfulness work remained isolated to Tasks 6-7 | closed | keeps backend and UI responsibilities bounded |
| 2026-03-14 fail-closed adversarial review | PRD telemetry requirements for detail-mode usage and bounded write-path failures were missing from the task plan | blocking | telemetry proofs landed in Tasks 2, 3, and this closure matrix | closed | restores approved PRD scope |
| 2026-03-14 fail-closed adversarial review | Verification matrix used placeholder states instead of explicit fail-closed results | blocking | every row above now records `pass`, `fail`, or approved `skipped` evidence | closed | restores ship-gate semantics |
| 2026-03-14 fail-closed adversarial review | Task 4 needed proof that backend review-detail metadata stays authoritative across BFF normalization | non-blocking | landed `wf0081_bff_review_detail_preserves_backend_detail_metadata_verbatim` in Task 4 | closed | tightens hidden-coupling coverage |
| 2026-03-14 fail-closed adversarial review | Task 5 needed explicit clarification that `ReviewNodeFindings.tsx` is intentionally created in-slice | non-blocking | Task 5 implementation created the file as the atomic leaf renderer | closed | removes file-path ambiguity |

## Preflight and Notes

- Part A preflight:
  - initial broad backend suite run failed closed because `DATABASE_URL` pointed to `grant_reviewer_dev`
  - safe no-db preflight then passed via `cd backend && uv run pytest -m no_db` -> `316 passed, 252 deselected in 6.85s`
- Resume-only baseline repair:
  - [`backend/tests/test_review_detail_stage_aware_buckets.py`](/home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/backend/tests/test_review_detail_stage_aware_buckets.py) needed `detail_mode="legacy_cards"` after Tasks 1-4 made the field required
  - committed separately as `4074413` before Task 5 so the resumed branch returned to a green no-db baseline

## Remaining Risks Before Ship

- Part B technical audit has not run yet; this walkthrough records implementation closure evidence only.
- Part C verification still needs repo-wide `pre-commit run --all-files` plus the broader final verification gate.
- The frontend combined proof command verifies the review-detail page contract and page-local actions, but no manual browser validation has been performed yet.
