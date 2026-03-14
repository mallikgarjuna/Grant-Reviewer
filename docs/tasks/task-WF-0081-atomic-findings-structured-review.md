<!-- docs/tasks/task-WF-0081-atomic-findings-structured-review.md -->
# WF-0081 — Atomic Findings Structured Review

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-14

Type: feature

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Add the persisted findings contract and explicit detail-mode discriminator

Goal:
Introduce the minimum durable storage contract for atomic findings reviews by adding `ReviewFinding`, extending the assessment-status enum with `REQUIREMENTS_MET`, and persisting an explicit per-review `detail_mode` so legacy `ReviewCard` reads stay distinct from the new findings path.
Slice: storage-contract
User Stories: US1, US2, US3, US4
PRD Requirements: FR2, FR3, FR4, FR5, FR6, FR9, FR13
Depends on: none
Enables: 2, 3, 7
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/models/domain.py`
- `backend/migrations/versions/<new_revision>_wf0081_review_findings_detail_mode.py`
- `backend/tests/test_api.py`
May touch files:
- `none`
Out of scope: structured-review write-path orchestration, API response assembly, BFF normalization, detail-page rendering, historical backfill
Stop if: the persisted discriminator cannot stay per-review, `ReviewFinding` needs denormalized data beyond the PRD snapshot fields to render safely, or the schema change would force legacy reviews off `ReviewCard`
Session boundary after: no
Acceptance Criteria:
- Targeted failing regressions such as `test_wf0081_contract_review_storage_supports_detail_mode_and_findings` and `test_wf0081_contract_migration_preserves_legacy_review_cards` prove the current schema lacks the findings table, the explicit detail-mode discriminator, or the `REQUIREMENTS_MET` assessment state.
- After the change, the same regressions pass by proving legacy reviews remain readable through `ReviewCard`, new atomic reviews can persist `reviewed_node_findings` mode plus `ReviewFinding` rows, and the persisted contract carries the proposal-node and evaluation criteria/element snapshot fields required by the PRD.
- Migration coverage proves pre-WF-0081 reviews default to the legacy-card detail mode without backfill and continue to round-trip existing `ReviewCard` rows unchanged.
- The task does not yet change structured-review generation behavior or the `GET /reviews/{review_id}` response shape.
TDD Plan:
- RED: add `test_wf0081_contract_review_storage_supports_detail_mode_and_findings` and `test_wf0081_contract_migration_preserves_legacy_review_cards` in `backend/tests/test_api.py`; run them before adding the schema changes so they fail on the missing table, discriminator, and enum support.
- GREEN: add the minimal model and migration changes for `ReviewFinding`, `review.detail_mode`, and `AssessmentStatus.REQUIREMENTS_MET` while keeping legacy card persistence intact.
- REFACTOR: extract a tiny typed enum/helper only if the new detail-mode or assessment-state declarations become repetitive; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0081_contract_review_storage_supports_detail_mode_and_findings or wf0081_contract_migration_preserves_legacy_review_cards"`
- `cd backend && rg -n "ReviewFinding|detail_mode|REQUIREMENTS_MET" app/models/domain.py migrations/versions tests/test_api.py`
Risks (if any): If the persisted discriminator is implicit instead of stored, later API and frontend slices can fall back to heuristic mode detection.

### [ ] Task 2 — Tracer bullet: persist one atomic findings review from the current diagnostic engine output

Goal:
Prove the structured-review write path can map existing diagnostic findings into persisted `ReviewFinding` rows for one representative new review while preserving legacy `ReviewCard` reads as a separate compatibility path.
Slice: tracer-bullet
User Stories: US1, US2, US3, US4
PRD Requirements: FR1, FR2, FR3, FR4, FR5, FR11, FR13
Depends on: 1
Enables: 3, 7
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/repositories/review_repository.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `backend/app/engine/compat/review_card_mapper.py`
Out of scope: review-detail response assembly, BFF normalization, detail-page rendering, historical review migration, rollout beyond new atomic structured reviews
Stop if: persisting findings requires replacing the upstream diagnostic engine, read-time synthesis of missing fields, or making `ReviewCard` and `ReviewFinding` competing primary truths for the same review
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions such as `test_wf0081_contract_atomic_review_persists_review_findings` and `test_wf0081_contract_legacy_review_card_path_remains_unchanged` prove the current structured-review path still collapses everything directly to `ReviewCard` and does not yet persist atomic findings for the new mode.
- After the change, the same regressions pass by proving a new WF-0081-style structured review persists one `ReviewFinding` per reviewed-node plus evaluation-element finding, records `detail_mode="reviewed_node_findings"`, and leaves legacy review generation/reads on the `ReviewCard` path.
- The write path owns one bounded mapper seam from diagnostic finding to persisted `ReviewFinding` fields and fails closed when required snapshot data cannot be resolved.
- A paired regression such as `test_wf0081_contract_unmappable_diagnostic_finding_fails_closed` proves the write owner raises/logs a bounded failure instead of silently dropping a finding that cannot resolve the required evaluation criteria/element snapshot fields.
- Positive outcomes can persist `assessment_status="REQUIREMENTS_MET"` with bounded positive guidance text instead of empty issue text.
TDD Plan:
- RED: add `test_wf0081_contract_atomic_review_persists_review_findings`, `test_wf0081_contract_legacy_review_card_path_remains_unchanged`, and `test_wf0081_contract_unmappable_diagnostic_finding_fails_closed` in `backend/tests/test_structured_reviewer_service.py`; run them before changing the service/repository seam so they fail on missing findings persistence, missing compatibility separation, and missing fail-closed mapper behavior.
- GREEN: add the smallest repository/service write-path change that persists atomic findings for the new mode and preserves legacy `ReviewCard` behavior as-is.
- REFACTOR: extract a tiny typed findings payload helper or mapper only if the service/repository handoff becomes hard to follow inline; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0081_contract_atomic_review_persists_review_findings or wf0081_contract_legacy_review_card_path_remains_unchanged or wf0081_contract_unmappable_diagnostic_finding_fails_closed"`
- `cd backend && rg -n "wf0081_contract_(atomic_review_persists_review_findings|legacy_review_card_path_remains_unchanged|unmappable_diagnostic_finding_fails_closed)|ReviewFinding|detail_mode|pipeline_v1" app/services/structured_reviewer_service.py app/repositories/review_repository.py tests/test_structured_reviewer_service.py`
Risks (if any): If the write owner is split across multiple callers, later compatibility fixes can drift between persisted findings and rendered detail responses.

### [ ] Task 3 — Expose a dual-mode backend review-detail response without heuristic branching

Goal:
Return one explicit review-detail API that stays backward compatible for legacy cards while exposing grouped `reviewed_nodes[].findings[]` for new atomic reviews with an explicit `detail_mode`.
Slice: backend-detail-contract
User Stories: US1, US2, US3
PRD Requirements: FR6, FR7, FR8, FR9, FR10, FR12, FR13
Depends on: 1, 2
Enables: 4, 7
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/api.py`
- `backend/main.py`
- `backend/tests/test_api.py`
May touch files:
- `backend/app/repositories/review_repository.py`
Out of scope: BFF normalization, detail-page rendering, list/history redesign, historical backfill
Stop if: the API contract cannot make `detail_mode` explicit without flattening findings, synthesizing missing legacy cards, or widening beyond the review-detail surface
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions such as `test_wf0081_contract_review_detail_exposes_explicit_detail_mode` and `test_wf0081_contract_atomic_review_detail_groups_findings_under_reviewed_nodes` prove the current API returns cards-only detail and does not yet expose grouped findings for atomic reviews.
- After the change, the same regressions pass by proving legacy reviews still return `detail_mode="legacy_cards"` plus `cards[]`, while atomic reviews return `detail_mode="reviewed_node_findings"` plus `reviewed_nodes[].findings[]` grouped under the reviewed node with evaluation criteria/elements labels and no required `cards[]` rollup.
- A paired regression such as `test_wf0081_contract_review_detail_modes_are_mutually_exclusive` proves legacy reviews do not require `reviewed_nodes[]` and atomic reviews do not require `cards[]` as their primary researcher-visible contract.
- Atomic API coverage proves `REQUIREMENTS_MET`, `ASSESSED`, and `NOT_ASSESSABLE` all serialize correctly at the finding level.
- Same-page detail actions continue to be honest about the active contract or return a bounded limitation marker instead of silently reusing legacy-card text.
TDD Plan:
- RED: add `test_wf0081_contract_review_detail_exposes_explicit_detail_mode`, `test_wf0081_contract_atomic_review_detail_groups_findings_under_reviewed_nodes`, and `test_wf0081_contract_review_detail_modes_are_mutually_exclusive` in `backend/tests/test_api.py`; run them before changing the response contract so they fail on missing mode metadata, grouped findings, and the single-mode invariant.
- GREEN: add the minimal backend schemas and response assembly changes needed to return the explicit dual-mode contract without read-time backfill.
- REFACTOR: extract a tiny response-assembly helper only if legacy-vs-atomic branching becomes repetitive in `main.py`; otherwise skip.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0081_contract_review_detail_exposes_explicit_detail_mode or wf0081_contract_atomic_review_detail_groups_findings_under_reviewed_nodes or wf0081_contract_review_detail_modes_are_mutually_exclusive"`
- `cd backend && rg -n "detail_mode|reviewed_nodes|findings|wf0081_contract_review_detail_modes_are_mutually_exclusive|evaluation criteria|evaluation elements" app/schemas/api.py main.py tests/test_api.py`
Risks (if any): If the backend keeps both modes implicit, the BFF and page layers will need unsafe shape inference.

### [ ] Task 4 — Preserve the backend dual-mode contract across the BFF and frontend types

Goal:
Keep the BFF review-detail boundary additive and explicit by passing `detail_mode`, legacy cards, and atomic reviewed-node findings through without semantic rewrites.
Slice: bff-contract
User Stories: US2, US3
PRD Requirements: FR7, FR8, FR9, FR10, FR12, FR13
Depends on: 3
Enables: 5, 6, 7
Parallelizable: yes
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts`
- `frontend/src/lib/bff/types.ts`
May touch files:
- `none`
Out of scope: page rendering, export/copy behavior, reviews list/history changes, backend schema changes
Stop if: the BFF must infer the active mode from missing fields, rename backend semantics, or synthesize `ReviewCard` data for atomic reviews to keep the page working
Session boundary after: no
Acceptance Criteria:
- Targeted failing regressions such as `wf0081_bff_review_detail_preserves_explicit_detail_mode` and `wf0081_bff_review_detail_preserves_reviewed_node_findings` prove the current BFF/type boundary does not yet model or preserve the dual-mode contract.
- After the change, the same regressions pass by proving legacy payloads remain cards-based, atomic payloads preserve `reviewed_nodes[].findings[]` verbatim, and the BFF forwards `detail_mode` explicitly instead of inferring it locally.
- Frontend types accept all three finding assessment states, including `REQUIREMENTS_MET`.
- The task does not change UI rendering or same-page action copy yet.
TDD Plan:
- RED: add `wf0081_bff_review_detail_preserves_explicit_detail_mode` and `wf0081_bff_review_detail_preserves_reviewed_node_findings` in `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts`; run them before changing the route/types so they fail on missing explicit mode and findings carry-through.
- GREEN: make the minimum route normalization and type updates needed to preserve the backend contract verbatim.
- REFACTOR: extract a tiny findings normalizer only if optional-field handling becomes repetitive; otherwise skip.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t 'wf0081_bff_review_detail_preserves_explicit_detail_mode|wf0081_bff_review_detail_preserves_reviewed_node_findings'`
- `cd frontend && rg -n "detail_mode|reviewed_nodes|findings|REQUIREMENTS_MET" src/app/api/bff/reviews/'[reviewId]'/route.ts src/app/api/bff/reviews/'[reviewId]'/route.test.ts src/lib/bff/types.ts`
Risks (if any): If the BFF rewrites response semantics, the page can diverge from backend truth during mixed rollout.

### [ ] Task 5 — Render reviewed-node findings on the detail page while preserving legacy cards

Goal:
Make `/app/reviews/[reviewId]` render the new grouped findings contract for atomic reviews and keep the existing `ReviewCard` path intact for legacy reviews.
Slice: detail-page-render
User Stories: US1, US2, US3
PRD Requirements: FR7, FR8, FR9, FR10, FR12, FR13
Depends on: 4
Enables: 6, 7
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
- `frontend/src/components/review/ReviewNodeFindings.tsx`
May touch files:
- `none`
Out of scope: reviews list/history redesign, backend/BFF contract changes, historical migration, export/download wording
Stop if: truthful rendering requires flattening node-grouped findings back into cards, widening beyond the detail page, or changing legacy review layout semantics to accommodate the new mode
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions such as `wf0081_review_detail_renders_grouped_reviewed_node_findings` and `wf0081_review_detail_legacy_cards_still_render_without_findings` prove the current page only understands cards and cannot yet render the atomic shape safely.
- After the change, the same regressions pass by proving atomic reviews render grouped reviewed nodes with evaluation criteria/elements labels, severity, evidence basis, actionable feedback, and explicit `REQUIREMENTS_MET` positive states, while legacy reviews continue to render via the existing card path.
- The page branches once at the review-detail boundary on explicit `detail_mode`; leaf components do not guess the contract from optional fields.
- Researcher-facing copy uses `evaluation criteria` / `evaluation elements` terminology and does not surface `rubric`.
TDD Plan:
- RED: add `wf0081_review_detail_renders_grouped_reviewed_node_findings` and `wf0081_review_detail_legacy_cards_still_render_without_findings` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`; run them before the UI change so they fail on missing dual-mode rendering.
- GREEN: add the smallest page-level branch and findings render component needed to support atomic reviews while preserving the legacy card component unchanged.
- REFACTOR: extract tiny display helpers or constants only if the new findings render path repeats labeling logic; otherwise skip.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0081_review_detail_renders_grouped_reviewed_node_findings|wf0081_review_detail_legacy_cards_still_render_without_findings'`
- `cd frontend && rg -n "detail_mode|reviewed_nodes|evaluation criteria|evaluation elements|REQUIREMENTS_MET" src/app/app/reviews/'[reviewId]'/page.tsx src/app/app/reviews/'[reviewId]'/page.test.tsx src/components/review/ReviewNodeFindings.tsx`
Risks (if any): If the page branches in multiple places, later compatibility fixes can become inconsistent between node groups, headings, and empty states.

### [ ] Task 6 — Keep copy/export and empty-state behavior truthful for each detail mode

Goal:
Align same-page copy/export and zero-issue presentation with the active detail mode so atomic findings reviews remain truthful and legacy reviews stay unchanged.
Slice: detail-page-truthfulness
User Stories: US1, US3
PRD Requirements: FR5, FR10, FR12, FR13
Depends on: 5
Enables: 7
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `frontend/src/components/review/ReviewNodeFindings.tsx`
Out of scope: reviews list/history export redesign, backend schema changes, cross-page copy behavior, historical backfill
Stop if: truthful copy/export requires changing unrelated surfaces beyond the review detail page or inventing a temporary heuristic fallback between legacy and atomic text shapes
Session boundary after: yes
Acceptance Criteria:
- Targeted failing regressions such as `wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful` and `wf0081_review_detail_requirements_met_render_without_empty_issue_shells` prove the current page-local actions and empty states still assume a card-only contract.
- After the change, the same regressions pass by proving atomic copy/export uses the grouped findings contract truthfully, legacy reviews keep the current card-oriented export path, and `REQUIREMENTS_MET` findings render positive guidance without empty issue/evidence placeholders.
- A paired regression such as `wf0081_review_detail_legacy_copy_and_export_remain_card_based` proves atomic truthfulness fixes do not silently rewrite legacy review copy/export semantics.
- The page does not reuse legacy card wording for atomic findings when describing evaluation criteria/elements.
- Any bounded limitation remains explicit in the rendered copy instead of silently omitting findings content.
TDD Plan:
- RED: add `wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful`, `wf0081_review_detail_requirements_met_render_without_empty_issue_shells`, and `wf0081_review_detail_legacy_copy_and_export_remain_card_based` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`; run them before changing copy/export handling so they fail on card-only assumptions and legacy-mode regression risk.
- GREEN: make the minimum page-local copy/export and empty-state updates needed to stay truthful for both detail modes.
- REFACTOR: extract a tiny export/copy helper only if atomic-vs-legacy text assembly becomes duplicated; otherwise skip.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful|wf0081_review_detail_requirements_met_render_without_empty_issue_shells|wf0081_review_detail_legacy_copy_and_export_remain_card_based'`
- `cd frontend && rg -n "Copy as text|Download \\.txt|REQUIREMENTS_MET|evaluation criteria|evaluation elements" src/app/app/reviews/'[reviewId]'/page.tsx src/app/app/reviews/'[reviewId]'/page.test.tsx src/components/review/ReviewNodeFindings.tsx`
Risks (if any): If same-page actions remain card-shaped while the page shows findings, researchers can export misleading review content.

### [ ] Task 7 — Close mixed-rollout safety, compatibility proof, and implementation-readiness evidence

Goal:
Fail closed on the rollout boundary by proving legacy-card reviews and new findings reviews can coexist without heuristic reads, auto-backfill, or out-of-scope surface drift before claiming WF-0081 is ready to implement.
Slice: closure-gate
User Stories: US2, US3, US4
PRD Requirements: FR6, FR9, FR11, FR12, FR13
Depends on: 1, 2, 3, 4, 5, 6
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0081-atomic-findings-structured-review.md`
May touch files:
- `docs/index.md`
Out of scope: widening into reviews list/history redesign, historical backfill, `ReviewCard` retirement, new export surfaces
Stop if: any readiness claim depends on auto-migrating legacy reviews, inferring `detail_mode` from missing fields, or widening beyond the approved review-detail implementation slice
Session boundary after: yes
Acceptance Criteria:
- Phase 3 records explicit `pass`, `fail`, or approved `skipped` evidence for each verification-matrix row below before claiming the workflow is closed.
- The walkthrough becomes the single closure artifact for this workflow and records the exact baseline commit range/SHA, verification evidence pointers, and audit-disposition ledger for both legacy-card and atomic-findings paths.
- Verification proves legacy reviews still read/render from `ReviewCard`, new reviews read/render from grouped findings, no read-time backfill occurs, and no same-page truthfulness regressions remain open.
- Out-of-scope closure proof explicitly names deferred surfaces including `frontend/src/app/app/reviews/page.tsx`, `frontend/src/app/api/bff/reviews/route.ts`, and any legacy `/reviews` list/history contract files touched by the branch diff.
- If any blocking proof fails, implementation stops instead of soft-closing the workflow.
TDD Plan:
- N/A for the gate itself; this task consumes the RED/GREEN proofs from Tasks 1-6 and fails closed if they are incomplete or contradicted.
Verification Steps:
- `git log --oneline main...HEAD`
- `git diff --name-only main...HEAD -- backend/app/models/domain.py backend/app/services/structured_reviewer_service.py backend/main.py 'frontend/src/app/api/bff/reviews/[reviewId]/route.ts' 'frontend/src/app/app/reviews/[reviewId]/page.tsx'`
- `git diff --name-only main...HEAD -- 'frontend/src/app/app/reviews/page.tsx' 'frontend/src/app/api/bff/reviews/route.ts'`
- `cd backend && uv run pytest tests/test_api.py -k "wf0081_contract_review_storage_supports_detail_mode_and_findings or wf0081_contract_migration_preserves_legacy_review_cards or wf0081_contract_review_detail_exposes_explicit_detail_mode or wf0081_contract_atomic_review_detail_groups_findings_under_reviewed_nodes or wf0081_contract_review_detail_modes_are_mutually_exclusive"`
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0081_contract_atomic_review_persists_review_findings or wf0081_contract_legacy_review_card_path_remains_unchanged or wf0081_contract_unmappable_diagnostic_finding_fails_closed"`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t 'wf0081_bff_review_detail_preserves_explicit_detail_mode|wf0081_bff_review_detail_preserves_reviewed_node_findings'`
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t 'wf0081_review_detail_renders_grouped_reviewed_node_findings|wf0081_review_detail_legacy_cards_still_render_without_findings|wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful|wf0081_review_detail_requirements_met_render_without_empty_issue_shells|wf0081_review_detail_legacy_copy_and_export_remain_card_based'`
- `rg -n "Verification Matrix|Audit Disposition Ledger|baseline sha|commit range|legacy_cards|reviewed_node_findings|no backfill" docs/walkthroughs/walkthrough-WF-0081-atomic-findings-structured-review.md`
Risks (if any): Without an explicit closure task, Phase 3 can overclaim rollout safety while mixed-mode compatibility remains unproved.

## Verification Matrix

| Proof item | Task | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Persisted detail-mode discriminator proof | 1 | `test_wf0081_contract_review_storage_supports_detail_mode_and_findings` | reviews store an explicit primary detail mode instead of relying on read-time inference | `required` | required | protects mixed rollout |
| Legacy migration safety proof | 1 | `test_wf0081_contract_migration_preserves_legacy_review_cards` | existing reviews/cards remain valid without backfill | `required` | required | legacy cards stay readable |
| Atomic findings write-path proof | 2 | `test_wf0081_contract_atomic_review_persists_review_findings` | new atomic reviews persist one finding per reviewed-node plus evaluation-element outcome | `required` | required | current engine findings remain upstream truth |
| Legacy compatibility separation proof | 2 | `test_wf0081_contract_legacy_review_card_path_remains_unchanged` | legacy review generation/reads remain on `ReviewCard` and do not require `ReviewFinding` | `required` | required | no competing truths |
| Fail-closed mapping proof | 2 | `test_wf0081_contract_unmappable_diagnostic_finding_fails_closed` | unmappable diagnostic findings raise/log a bounded failure instead of being dropped silently | `required` | required | closes the PRD edge case |
| Backend dual-mode detail proof | 3 | `test_wf0081_contract_review_detail_exposes_explicit_detail_mode` | `GET /reviews/{review_id}` returns explicit `detail_mode` for every review | `required` | required | no heuristics |
| Reviewed-node grouping proof | 3 | `test_wf0081_contract_atomic_review_detail_groups_findings_under_reviewed_nodes` | atomic responses group findings beneath reviewed nodes rather than flattening them | `required` | required | primary researcher reading model |
| Single-mode invariant proof | 3 | `test_wf0081_contract_review_detail_modes_are_mutually_exclusive` | each review exposes one primary detail mode without requiring the other shape | `required` | required | prevents mixed-contract drift |
| BFF contract carry-through proof | 4 | `wf0081_bff_review_detail_preserves_explicit_detail_mode`, `wf0081_bff_review_detail_preserves_reviewed_node_findings` | BFF/types preserve the backend dual-mode contract verbatim | `required` | required | no semantic rewrite |
| Legacy render continuity proof | 5 | `wf0081_review_detail_legacy_cards_still_render_without_findings` | legacy reviews still render from `ReviewCard` without placeholder findings | `required` | required | backward compatibility |
| Atomic findings render proof | 5 | `wf0081_review_detail_renders_grouped_reviewed_node_findings` | atomic reviews render grouped findings with evaluation criteria/elements terminology | `required` | required | no `rubric` copy |
| Positive-state truthfulness proof | 6 | `wf0081_review_detail_requirements_met_render_without_empty_issue_shells` | `REQUIREMENTS_MET` renders bounded positive guidance without empty issue placeholders | `required` | required | keeps positive cases honest |
| Copy/export truthfulness proof | 6 | `wf0081_review_detail_atomic_copy_and_export_stay_mode_truthful` | same-page actions stay truthful to the active detail mode | `required` | required | no legacy text leakage |
| Legacy export continuity proof | 6 | `wf0081_review_detail_legacy_copy_and_export_remain_card_based` | atomic-mode truthfulness changes do not rewrite legacy review export semantics | `required` | required | guards backward compatibility |
| Mixed-rollout closure proof | 7 | walkthrough verification matrix + scoped diff/test commands | implementation-ready claim is blocked until legacy and atomic compatibility evidence is recorded | `required` | required | fail closed before ship |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 2.2 task review | Task 6 named atomic truthfulness work but did not require a distinct proof that legacy copy/export behavior remains card-based | non-blocking | add a dedicated legacy copy/export regression to Task 6 acceptance, TDD, verification, and the matrix | closed | protects backward compatibility during same-page truthfulness work |
| Phase 2.2 task review | Task 2 did not explicitly prove fail-closed behavior when a diagnostic finding cannot resolve the required snapshot fields | non-blocking | add `test_wf0081_contract_unmappable_diagnostic_finding_fails_closed` plus matching verification/matrix coverage | closed | prevents silent finding loss |
| Phase 2.2 task review | Task 3 did not explicitly test the per-review mutual-exclusivity invariant between legacy cards and reviewed-node findings | non-blocking | add `test_wf0081_contract_review_detail_modes_are_mutually_exclusive` and wire it through verification/matrix rows | closed | keeps the API contract single-mode and explicit |
| Phase 2.2 task review | Task 7 did not name the deferred reviews list/history surfaces in its closure proof | non-blocking | add explicit deferred-surface files to Task 7 acceptance and verification commands | closed | improves hidden-coupling detection during closure |

## Changelog

- v0.1 (2026-03-14): Initial task breakdown from the finalized WF-0081 PRD, preserving legacy `ReviewCard` compatibility and sequencing the findings-based rollout across storage, generation, API, BFF, frontend, and closure proof.
- v0.2 (2026-03-14): Applied Part B review feedback by adding fail-closed mapper proof, explicit single-mode API invariants, legacy export continuity coverage, and tighter deferred-surface closure checks before marking the plan ready.
