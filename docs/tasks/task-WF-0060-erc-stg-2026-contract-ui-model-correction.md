<!-- docs/tasks/task-WF-0060-erc-stg-2026-contract-ui-model-correction.md -->
# WF-0060 — ERC StG 2026 Contract/UI Model Correction Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-06

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Source-gated canonical ERC contract correction

Goal:
Correct the ERC StG 2026 canonical hierarchy to the approved source-first leaf/container model and lock it with deterministic contract tests before cross-stack behavior changes begin.
Slice: canonical-contract
User Stories: US1, US4
PRD Requirements: FR1, FR2, FR3, FR4, FR13, FR15
Depends on: none
Enables: 2, 3, 4, 5, 6, 7
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`
- `backend/tests/test_call_nodes_tree_api.py`
- `backend/tests/test_call_nodes_metadata_api.py`
May touch files:
- `backend/data/calls/sources/erc_stg_2026_full.sources.md`
Out of scope: frontend render changes, structured-review persistence changes, compatibility-note UI
Stop if: Task 1 would require any substantive ERC YAML re-authoring or RED test authoring tied to refreshed source interpretation and the official ERC StG 2026 application-form and assessment-criteria PDFs are not confirmed as the accepted source set for this run; stop before editing files and ask whether the user needs to upload or refresh source files first
Session boundary after: no
Acceptance Criteria:
- Phase 3 must explicitly confirm either the existing traced ERC source set or new uploaded ERC source PDFs before any substantive canonical-YAML correction begins.
- Canonical ERC StG 2026 metadata models `part_a`, `budget`, `part_b`, `b1`, and `b2` as structural containers only.
- `resources_time_commitment` is located under `part_a -> budget` while preserving its logical leaf identity.
- Contract-facing metadata tests prove only the five approved leaf nodes remain input-bearing/reviewable in MVP.
TDD Plan:
- RED: add `wf0060_erc_tree_models_structural_containers_without_review_surfaces` in `backend/tests/test_call_nodes_tree_api.py` and `wf0060_erc_metadata_moves_resources_under_budget_without_changing_leaf_identity` in `backend/tests/test_call_nodes_metadata_api.py`.
- GREEN: apply the minimal canonical YAML correction needed to satisfy the approved PRD and existing traced source set.
- REFACTOR: update source-manifest wording only if the canonical correction changes traceability notes.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_nodes_tree_api.py -k "wf0060_erc_tree_models_structural_containers_without_review_surfaces"`
- `cd backend && uv run pytest tests/test_call_nodes_metadata_api.py -k "wf0060_erc_metadata_moves_resources_under_budget_without_changing_leaf_identity"`
- `cd backend && rg -n "id: (part_a|budget|part_b|b1|b2|resources_time_commitment)" data/calls/canonical/erc/erc_stg_2026_full.yaml`
Risks (if any): A partial YAML correction can leave hidden container expectations behind, so the tests must assert both hierarchy and reviewability semantics.

### [x] Task 2 — Tracer bullet: grouped submit UI with leaf-only editing

Goal:
Prove one end-to-end submit tracer where ERC grouping renders correctly but only corrected leaf nodes can be edited and posted across the submit boundary.
Slice: tracer-bullet
User Stories: US1
PRD Requirements: FR5, FR6, FR13, FR15
Depends on: 1
Enables: 3, 4, 5, 7
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/lib/submit/renderModel.ts`
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
May touch files:
- `frontend/src/lib/submit/renderModel.test.ts`
Out of scope: backend persistence format, review-detail compatibility messaging
Stop if: the submit renderer requires broad multi-call hierarchy generalization beyond the ERC StG 2026 path to stay correct
Session boundary after: no
Acceptance Criteria:
- ERC submit UI renders structural grouping for Part A / Budget and Part B / B1 / B2 without exposing those containers as editable fields.
- Only the approved leaf logical IDs can be entered and included in the structured-review submit payload.
- Container logical IDs are blocked from submit payload construction at the frontend boundary.
TDD Plan:
- RED: add `wf0060_render_model_excludes_structural_containers_from_submittable_nodes` in `frontend/src/lib/submit/renderModel.test.ts` and `wf0060_submit_tracer_renders_grouping_but_posts_only_leaf_nodes` in `frontend/src/components/submit/UniversalSubmitForm.test.tsx`.
- GREEN: implement the smallest `renderModel` and form changes needed to keep grouping metadata while filtering submittable fields down to corrected leaves.
- REFACTOR: extract a small helper only if container/leaf filtering logic becomes duplicated between render-model and form code.
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0060_submit_tracer_renders_grouping_but_posts_only_leaf_nodes"`
- `cd frontend && npx vitest run src/lib/submit/renderModel.test.ts -t "wf0060_render_model_excludes_structural_containers_from_submittable_nodes"`
- `cd frontend && rg -n "submitted_nodes|node_logical_id" src/components/submit/UniversalSubmitForm.tsx src/lib/submit/renderModel.ts`
Risks (if any): It is easy to preserve old container-as-field behavior in hidden form-state transforms even if the visible UI looks correct.

### [x] Task 3 — Backend stage and submit-boundary leaf enforcement

Goal:
Replace legacy ERC container-stage assumptions with corrected leaf-stage and submit-boundary enforcement in backend review-entry seams.
Slice: backend-submit-guard
User Stories: US1, US4
PRD Requirements: FR4, FR6, FR10, FR13, FR15
Depends on: 1, 2
Enables: 4, 5, 7
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/reviewer_policy.py`
- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_structured_reviewer_service.py`
May touch files:
- `backend/tests/test_reviewer_policy.py`
Out of scope: persisted review-detail response shape, frontend review page rendering
Stop if: submit-boundary enforcement needs schema or repository changes that cannot stay within the planned service-layer slice
Session boundary after: no
Acceptance Criteria:
- Backend rejects structural container logical IDs as direct submitted content for corrected ERC reviews.
- Step-scope enforcement recognizes only corrected leaf nodes as reviewable surfaces for ERC StG 2026.
- Legacy top-level `resources_time_commitment` handling remains compatible without reintroducing container submissions.
TDD Plan:
- RED: add `wf0060_structured_review_rejects_erc_container_submission_ids` in `backend/tests/test_structured_reviewer_service.py` and `wf0060_reviewer_policy_uses_corrected_erc_leaf_stage_scope` in `backend/tests/test_reviewer_policy.py`.
- GREEN: implement the minimum reviewer-policy and structured-review service changes needed to enforce corrected leaf-only submissions.
- REFACTOR: split any ERC-specific helper from generic service code only if the leaf-resolution logic becomes difficult to audit inline.
Verification Steps:
- `cd backend && uv run pytest tests/test_structured_reviewer_service.py -k "wf0060_structured_review_rejects_erc_container_submission_ids"`
- `cd backend && uv run pytest tests/test_reviewer_policy.py -k "wf0060_reviewer_policy_uses_corrected_erc_leaf_stage_scope"`
- `cd backend && rg -n "b2|resources_time_commitment|STEP_2" app/services/reviewer_policy.py app/services/structured_reviewer_service.py`
Risks (if any): Stage rules can look green while still accepting deprecated container IDs unless rejection is asserted explicitly.

### [ ] Task 4 — Persist submitted leaf coverage and legacy compatibility state

Goal:
Persist review-linked submitted leaf coverage and deprecated-container compatibility metadata so review detail no longer infers ERC coverage from cards or containers.
Slice: persisted-coverage
User Stories: US2, US3, US4
PRD Requirements: FR7, FR8, FR9, FR10, FR11, FR15
Depends on: 3
Enables: 5, 6, 7
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/repositories/review_repository.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_api.py`
May touch files:
- `backend/app/services/structured_reviewer_service.py`
Out of scope: frontend rendering of compatibility notes, broad historical data backfill
Stop if: persistence changes require a schema migration or wider review model redesign not described in the PRD
Session boundary after: yes
Acceptance Criteria:
- Review creation/detail persistence preserves corrected `submitted_leaf_ids` independently from emitted review cards.
- Legacy `b1` and `b2` evidence is preserved as ambiguous compatibility metadata rather than auto-expanded leaf coverage.
- Legacy `resources_time_commitment` aliases resolve to the corrected moved leaf without changing downstream logical ID expectations.
TDD Plan:
- RED: add `wf0060_review_detail_persists_leaf_coverage_and_legacy_compatibility_state` in `backend/tests/test_api.py`.
- GREEN: implement the smallest repository/API contract changes needed to expose submitted leaf coverage plus explicit legacy compatibility metadata.
- REFACTOR: extract a focused compatibility-mapping helper if review repository and API assembly duplicate alias/deprecated-ID logic.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0060_review_detail_persists_leaf_coverage_and_legacy_compatibility_state"`
- `cd backend && rg -n "submitted_leaf_ids|legacy_ambiguous|compatibility" app/repositories/review_repository.py app/schemas/api.py`
Risks (if any): A flat replacement of old `submitted_nodes` data can silently destroy evidence needed for mixed-version review interpretation.

### [ ] Task 5 — Review-detail grouping and ordering from corrected metadata

Goal:
Switch ERC review detail to corrected leaf-group ordering backed by persisted review-linked coverage plus call metadata, not legacy query-param or container assumptions.
Slice: review-detail-ordering
User Stories: US2, US3
PRD Requirements: FR8, FR10, FR11, FR14, FR15
Depends on: 4
Enables: 6, 7
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `frontend/src/app/app/page.test.tsx`
Out of scope: submit-flow rendering, non-ERC review-detail redesign
Stop if: the BFF route cannot derive the required grouping/ordering without new backend API fields beyond Task 4
Session boundary after: yes
Acceptance Criteria:
- ERC review detail renders Part A / Budget and Part B / B1 / B2 grouping from corrected call metadata.
- Reviewed/not-reviewed coverage derives from persisted submitted leaf coverage plus corrected call metadata, not from `submitted_nodes` query params or cards-only inference.
- Corrected leaf ordering keeps `resources_time_commitment` under Part A / Budget in review detail.
TDD Plan:
- RED: add `wf0060_review_detail_uses_corrected_leaf_grouping_and_ordering` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`.
- GREEN: implement the minimum BFF/page changes needed to consume persisted coverage and corrected call hierarchy for ERC review detail.
- REFACTOR: extract a small ordering helper if group assembly becomes hard to read in the page or route.
Verification Steps:
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0060_review_detail_uses_corrected_leaf_grouping_and_ordering"`
- `cd frontend && rg -n "submitted_nodes|compatibility|resources_time_commitment" src/app/api/bff/reviews/[reviewId]/route.ts src/app/app/reviews/[reviewId]/page.tsx`
Risks (if any): Query-param fallback can remain accidentally reachable for ERC even after the corrected call-linked path is added.

### [ ] Task 6 — Explicit compatibility notes for mixed-version ERC reviews

Goal:
Render deterministic compatibility-state semantics for deprecated container evidence, moved-node aliases, and mixed-version precedence without overstating reviewed coverage.
Slice: compatibility-notes
User Stories: US2, US3
PRD Requirements: FR9, FR10, FR11, FR14
Depends on: 4, 5
Enables: 7
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/api.py`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
Out of scope: generalized compatibility framework for other calls, telemetry redesign
Stop if: compatibility-note requirements expand beyond the three PRD states (`deprecated_container_submission`, `moved_legacy_node_reference`, `mixed_version_review`)
Session boundary after: no
Acceptance Criteria:
- Review detail shows explicit compatibility-note semantics for deprecated container submissions, moved legacy node references, and mixed-version reviews.
- Mixed-version precedence uses corrected leaf IDs as the only proven reviewed coverage source.
- Deprecated `b1` and `b2` evidence remains visible for traceability without inflating leaf-reviewed counts.
TDD Plan:
- RED: add `wf0060_review_detail_renders_explicit_compatibility_notes_for_legacy_erc_evidence` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`.
- GREEN: implement the minimum API shape and page rendering changes needed to surface deterministic compatibility notes and mixed-version precedence.
- REFACTOR: consolidate compatibility-note copy mapping only if state-to-copy translation becomes repetitive.
Verification Steps:
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0060_review_detail_renders_explicit_compatibility_notes_for_legacy_erc_evidence"`
- `cd backend && rg -n "deprecated_container_submission|moved_legacy_node_reference|mixed_version_review" app/schemas/api.py`
Risks (if any): Mixed-version handling is easy to under-specify; if precedence rules are not asserted, UI copy may imply stronger evidence than the record supports.

### [ ] Task 7 — Closure regressions for leaf-only ERC submit and review detail

Goal:
Close the workflow with deterministic regressions that prove corrected ERC leaf-only submission, zero-card coverage retention, and no fallback leakage from legacy container assumptions.
Slice: closure-guard
User Stories: US1, US2, US3, US4
PRD Requirements: FR6, FR7, FR8, FR9, FR11, FR12, FR13
Depends on: 2, 3, 4, 5, 6
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `backend/tests/test_structured_reviewer_service.py`
Out of scope: walkthrough evidence capture, unrelated call regressions
Stop if: verification requires expanding the closure guard beyond deterministic WF-0060 selectors into broad suite rewrites
Session boundary after: yes
Acceptance Criteria:
- Automated regressions prove container IDs are blocked from corrected ERC submission paths on both frontend and backend seams.
- Automated regressions prove submitted corrected leaves remain traceable in review detail even when a submitted leaf emits zero review cards.
- Automated regressions prove legacy query-param/container fallback does not leak into corrected ERC review-detail ordering and coverage.
TDD Plan:
- RED: add `wf0060_container_ids_blocked_from_corrected_erc_submission`, `wf0060_zero_card_leaf_stays_visible_in_review_detail`, and `wf0060_erc_review_detail_blocks_legacy_fallback_leakage`.
- GREEN: add only the final assertions needed once Tasks 3 through 6 are green.
- REFACTOR: trim duplicated ERC fixtures/setup if closure selectors become noisy across backend and frontend tests.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0060_zero_card_leaf_stays_visible_in_review_detail"`
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0060_container_ids_blocked_from_corrected_erc_submission"`
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0060_erc_review_detail_blocks_legacy_fallback_leakage"`
Risks (if any): Without WF-specific closure selectors, Phase 3 can claim success while still missing the corrected leaf-coverage invariant.

## Changelog

- v0.1 (2026-03-06): Initial task breakdown from PRD.
- v0.2 (2026-03-06): Tightened deterministic verification selectors, added explicit reviewer-policy test coverage, and marked Ready for Implementation.
- v0.3 (2026-03-06): Hardened Task 1 upload-gate wording and exact test selectors; fixed Task 7 dependency on the frontend tracer slice.
