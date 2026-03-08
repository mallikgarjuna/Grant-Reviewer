<!-- docs/tasks/task-WF-0063-universal-node-visibility-reviewability.md -->
# WF-0063 — Universal Node Visibility Reviewability Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-08

Type: feature

## Task Breakdown (Sequential Order)

### [x] Task 1 — Canonical node-role and proof-call opt-in schema contract

Goal:
Freeze the minimal V2 YAML contract for split visibility/reviewability by adding one explicit `node_role` field plus one machine-readable proof-call opt-in flag, without changing runtime behavior yet.
Slice: canonical-contract
User Stories: US1, US2, US3, US4
PRD Requirements: FR1, FR1a, FR1b, FR2, FR3, FR15
Depends on: none
Enables: 2, 3, 4, 8, 9, 10, 11
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/call_definitions_v2.py`
- `backend/tests/test_call_definitions_v2_schema.py`
May touch files:
- `backend/tests/test_ingest_call_v2_db.py`
Out of scope: proof-call YAML authoring, API response changes, frontend rendering
Stop if: the smallest viable opt-in seam cannot stay as one structured canonical runtime-config field and instead requires a broader call-definition schema redesign
Session boundary after: no
Acceptance Criteria:
- `ProposalNodeDefinitionV2` accepts only `PRIMARY` or `SUPPORTING` for `node_role` and defaults omitted values to `PRIMARY`.
- Supporting nodes fail validation when `node_expectations` is non-empty.
- One canonical machine-readable runtime opt-in field exists for split visibility/reviewability and defaults to disabled for legacy calls.
TDD Plan:
- RED: add `test_wf0063_node_role_defaults_primary_and_supporting_requires_empty_expectations` and `test_wf0063_runtime_opt_in_flag_defaults_disabled` in `backend/tests/test_call_definitions_v2_schema.py`.
- GREEN: implement the minimum schema and validator changes needed to support `node_role` plus the single opt-in field.
- REFACTOR: extract a tiny schema validator helper only if role and runtime-flag checks become hard to audit inline.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_definitions_v2_schema.py -k "wf0063"`
- `cd backend && rg -n "node_role|runtime_config|split_visibility" app/schemas/call_definitions_v2.py`
Risks (if any): A stringly typed or duplicated opt-in seam will create hidden rollout drift before implementation starts.

### [ ] Task 2 — Source-grounded MSCA proof-call role authoring

Goal:
Apply the approved role split to `MSCA-PF-2025` only, keeping every official node in YAML and enabling the proof-call opt-in without inventing new evaluation criteria/elements mappings.
Slice: proof-call-authoring
User Stories: US1, US2, US3, US4
PRD Requirements: FR1a, FR2, FR3, FR13, FR14, FR15
Depends on: 1
Enables: 3, 4
Parallelizable: no
Files to modify:
Must touch files:
- `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`
- `backend/tests/test_ingest_call_v2_db.py`
May touch files:
- `backend/data/calls/sources/msca_pf_2025_full.sources.md`
Out of scope: non-MSCA call authoring, runtime API changes, reviewer-engine redesign
Stop if: the existing accepted MSCA source set does not support the planned `PRIMARY` versus `SUPPORTING` assignments for `abstract`, Part B1 Sections 1-3, Part B2 Sections 4-8, and conditional Section 9
Session boundary after: no
Acceptance Criteria:
- All official MSCA-PF nodes remain present in canonical YAML.
- Part B1 Sections 1-3 are authored as `PRIMARY`; `abstract`, Part B2 Sections 4-8, and conditional Section 9 are authored as `SUPPORTING`.
- The proof-call opt-in flag is enabled only for `MSCA-PF-2025`; no other call changes behavior in this task.
TDD Plan:
- RED: add `test_wf0063_msca_pf_2025_proof_call_roles_and_opt_in_are_source_grounded` in `backend/tests/test_ingest_call_v2_db.py`.
- GREEN: apply the minimal YAML edits needed to add role data and the proof-call opt-in marker while preserving source-grounded structure.
- REFACTOR: tighten source-manifest wording only if the new role authoring needs clearer provenance notes.
Verification Steps:
- `cd backend && uv run pytest tests/test_ingest_call_v2_db.py -k "wf0063_msca_pf_2025_proof_call_roles_and_opt_in_are_source_grounded"`
- `cd backend && rg -n "node_role|runtime_config|abstract|part_b2|gf_letter_of_commitment_outgoing_host" data/calls/canonical/msca/msca_pf_2025_full.yaml`
Risks (if any): A partial YAML edit can silently drop official nodes or reintroduce fake expectations on supporting content.

### [ ] Task 3 — Tracer bullet: proof-call config and flat nodes API expose role-aware completeness

Goal:
Prove the earliest end-to-end contract slice by surfacing the proof-call opt-in and role-aware node completeness through public call config and flat nodes APIs while preserving legacy behavior for non-opted-in calls.
Slice: tracer-bullet
User Stories: US1, US2, US4
PRD Requirements: FR1a, FR5, FR6, FR15, FR16
Depends on: 1, 2
Enables: 4, 5, 6, 7, 9, 11
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/api.py`
- `backend/main.py`
- `backend/tests/test_api.py`
May touch files:
- `backend/app/services/call_definition_service.py`
Out of scope: tree shaping, frontend rendering, review-detail persistence
Stop if: exposing the opt-in seam or `node_role` requires a second metadata taxonomy instead of reusing canonical call-definition data
Session boundary after: yes
Acceptance Criteria:
- `GET /api/public/calls/{call_logical_id}/config` exposes one machine-readable split-behavior flag derived from canonical runtime config.
- `GET /calls/{call_id}/nodes` returns all official nodes plus `node_role` for opted-in proof-call behavior without removing `has_expectations`.
- Non-opted-in calls keep legacy config behavior and do not silently switch to split visibility semantics.
- The same proof-call-shaped canonical data can be forced back to legacy behavior by disabling the runtime opt-in seam, proving rollback does not require YAML re-authoring.
TDD Plan:
- RED: add `test_wf0063_call_config_exposes_split_opt_in_for_msca_pf_2025_only`, `test_wf0063_flat_nodes_api_returns_all_official_nodes_with_node_role`, and `test_wf0063_disabling_split_opt_in_restores_legacy_call_behavior` in `backend/tests/test_api.py`.
- GREEN: implement the smallest API contract changes needed to surface the opt-in flag and flat-node role metadata from canonical data while preserving explicit rollback behavior when the opt-in is off.
- REFACTOR: extract a small config-response helper only if opt-in resolution becomes duplicated inside `backend/main.py`.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0063_call_config_exposes_split_opt_in_for_msca_pf_2025_only or wf0063_flat_nodes_api_returns_all_official_nodes_with_node_role"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0063_disabling_split_opt_in_restores_legacy_call_behavior"`
- `cd backend && rg -n "node_role|split_visibility|has_expectations" app/schemas/api.py main.py`
Risks (if any): If the tracer bullet only proves MSCA and not legacy fallback in the same test area, the rollout gate can drift unnoticed.

### [ ] Task 4 — Tree API role propagation and structural completeness

Goal:
Extend the same role-aware completeness guarantee to tree responses so nested consumers do not fall back to `has_expectations` as a visibility proxy.
Slice: tree-contract
User Stories: US1, US4
PRD Requirements: FR4, FR5, FR6, FR16
Depends on: 3
Enables: 11
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/node_tree_service.py`
- `backend/tests/test_call_nodes_tree_api.py`
- `backend/tests/test_node_tree_service.py`
May touch files:
- `backend/main.py`
Out of scope: frontend render changes, submit filtering, review-detail semantics
Stop if: tree propagation would require remapping or inventing canonical parentage beyond the existing YAML structure
Session boundary after: no
Acceptance Criteria:
- Tree responses include `node_role` on every returned node.
- Supporting nodes and structural containers remain present in the proof-call tree even when `has_expectations` is false.
- Existing tree mismatch/cycle protections stay intact.
TDD Plan:
- RED: add `test_wf0063_tree_api_keeps_supporting_nodes_visible_with_node_role` in `backend/tests/test_call_nodes_tree_api.py` and `test_wf0063_node_tree_service_carries_node_role_without_filtering_non_expectation_nodes` in `backend/tests/test_node_tree_service.py`.
- GREEN: implement the minimal tree-node propagation changes required to preserve role-aware completeness.
- REFACTOR: simplify tree-node construction only if `NodeSummary` to `NodeTreeNode` mapping starts duplicating role fields in multiple places.
Verification Steps:
- `cd backend && uv run pytest tests/test_call_nodes_tree_api.py -k "wf0063_tree_api_keeps_supporting_nodes_visible_with_node_role"`
- `cd backend && uv run pytest tests/test_node_tree_service.py -k "wf0063_node_tree_service_carries_node_role_without_filtering_non_expectation_nodes"`
- `cd backend && rg -n "node_role" app/services/node_tree_service.py tests/test_call_nodes_tree_api.py tests/test_node_tree_service.py`
Risks (if any): A flat API fix can mask a still-broken tree path that continues to hide supporting nodes in nested consumers.

### [ ] Task 5 — Frontend/BFF node-role typing and single-source classification helper

Goal:
Create one frontend-side role-classification path derived from backend contracts so BFF adapters, submit rendering, and review detail do not drift into separate MSCA-specific allowlists.
Slice: role-plumbing
User Stories: US2, US4
PRD Requirements: FR5, FR6a, FR15, FR16
Depends on: 3
Enables: 6, 7, 11
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/lib/bff/types.ts`
- `frontend/src/lib/submit/nodeRoles.ts`
- `frontend/src/lib/submit/nodeRoles.test.ts`
May touch files:
- `frontend/src/lib/submit/loadStructuredCalls.ts`
Out of scope: visual rendering changes, backend validation, review-detail copy
Stop if: consistent role derivation cannot be expressed from backend contract fields alone and would require hardcoded call-code branches
Session boundary after: no
Acceptance Criteria:
- Frontend types carry the new role-aware backend fields needed for config and node responses.
- One shared helper derives primary/supporting/container semantics from backend contract data.
- No new MSCA-only hardcoded reviewable/supporting allowlists are introduced.
TDD Plan:
- RED: add `wf0063_node_role_helper_uses_backend_contract_without_call_specific_allowlists` in `frontend/src/lib/submit/nodeRoles.test.ts`.
- GREEN: implement the smallest shared helper and type updates needed to centralize role classification.
- REFACTOR: fold duplicated boolean checks from existing consumers into the shared helper only after the helper is green.
Verification Steps:
- `cd frontend && npx vitest run src/lib/submit/nodeRoles.test.ts -t "wf0063_node_role_helper_uses_backend_contract_without_call_specific_allowlists"`
- `cd frontend && rg -n "node_role|split_visibility" src/lib/bff/types.ts src/lib/submit/nodeRoles.ts`
Risks (if any): If the helper and BFF types diverge, later UI fixes can appear correct while still encoding hidden coupling.

### [ ] Task 6 — Render model decouples visibility from expectations

Goal:
Make the render model treat node-role-aware structural completeness, not `has_expectations`, as the visibility contract for opted-in calls while preserving legacy fallback for non-opted-in nested calls.
Slice: render-model
User Stories: US1, US2, US4
PRD Requirements: FR4, FR6, FR7, FR7a, FR8, FR15
Depends on: 5
Enables: 7, 11
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/lib/submit/renderModel.ts`
- `frontend/src/lib/submit/renderModel.test.ts`
- `frontend/src/lib/submit/nodeRoles.ts`
May touch files:
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
Out of scope: backend request validation, review-detail output fields, non-proof-call redesign
Stop if: supporting-node visibility for opted-in calls requires broad recursive-form redesign beyond the current universal render model
Session boundary after: no
Acceptance Criteria:
- Opted-in proof-call render model includes visible supporting nodes and grouping-only structural containers even when `has_expectations` is false.
- Structural containers remain non-editable/non-submittable in the render model.
- Non-opted-in nested calls preserve current behavior instead of silently adopting split semantics.
TDD Plan:
- RED: add `wf0063_render_model_uses_node_role_for_opted_in_visibility` and `wf0063_render_model_preserves_legacy_nested_fallback_without_opt_in` in `frontend/src/lib/submit/renderModel.test.ts`.
- GREEN: implement the smallest render-model changes needed to switch opted-in visibility to shared role classification.
- REFACTOR: extract a narrow grouping helper only if container and supporting-node handling becomes hard to read.
Verification Steps:
- `cd frontend && npx vitest run src/lib/submit/renderModel.test.ts -t "wf0063_render_model_uses_node_role_for_opted_in_visibility"`
- `cd frontend && npx vitest run src/lib/submit/renderModel.test.ts -t "wf0063_render_model_preserves_legacy_nested_fallback_without_opt_in"`
- `cd frontend && rg -n "has_expectations|node_role|split_visibility" src/lib/submit/renderModel.ts src/lib/submit/nodeRoles.ts`
Risks (if any): A partial render-model fix can still leave hidden `has_expectations` filtering in grouping or fallback code paths.

### [ ] Task 7 — Universal submit form labels supporting nodes and filters primary-only payloads

Goal:
Complete the first-path submit UX by distinguishing primary versus supporting nodes in the form, preserving draft state for supporting content, and sending only primary nodes across submit/compliance boundaries.
Slice: submit-ui
User Stories: US1, US2
PRD Requirements: FR7, FR7a, FR8, FR10, FR12
Depends on: 5, 6
Enables: 11
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
May touch files:
- `frontend/src/components/submit/ComplianceBypassModal.tsx`
- `frontend/src/lib/submit/renderModel.ts`
Out of scope: backend enforcement, persisted supporting-context mode, review-detail page changes
Stop if: preserving supporting-node draft state would require a new server persistence surface instead of local/UI state only
Session boundary after: yes
Acceptance Criteria:
- The form labels nodes so users can distinguish primary reviewed content from supporting/non-primary content.
- Structural containers render as grouping-only and never become editable fields.
- Compliance and review submission payload construction includes only primary nodes, while supporting content remains in local draft state.
TDD Plan:
- RED: add `wf0063_submit_form_labels_primary_and_supporting_nodes` and `wf0063_submit_form_posts_only_primary_nodes_for_opted_in_calls` in `frontend/src/components/submit/UniversalSubmitForm.test.tsx`.
- GREEN: implement the minimum form-state and payload-filtering changes needed to keep supporting drafts visible but non-submittable.
- REFACTOR: extract a compact payload-builder helper only if primary-only filtering appears in multiple form branches.
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0063_submit_form_labels_primary_and_supporting_nodes"`
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0063_submit_form_posts_only_primary_nodes_for_opted_in_calls"`
- `cd frontend && rg -n "draft_nodes|nodes:|supporting|primary" src/components/submit/UniversalSubmitForm.tsx`
Risks (if any): The UI can look correct while still leaking supporting nodes into compliance or review payloads through hidden form transforms.

### [ ] Task 8 — Backend single-source role derivation replaces hardcoded reviewability fallbacks

Goal:
Remove role/reviewability drift in backend policy logic by deriving proof-call primary/supporting behavior from canonical data instead of hardcoded Step 2 or MSCA-specific fallback sets.
Slice: backend-role-source
User Stories: US2, US4
PRD Requirements: FR6a, FR15, FR16
Depends on: 1, 3
Enables: 9, 10, 11
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/reviewer_policy.py`
- `backend/tests/test_reviewer_policy.py`
May touch files:
- `backend/app/services/call_definition_service.py`
- `backend/app/models/domain.py`
Out of scope: submit rejection, review-detail persistence, frontend helpers
Stop if: canonical role derivation cannot be reused by backend policy code without introducing a second backend-only taxonomy
Session boundary after: no
Acceptance Criteria:
- Backend review-stage/reviewability logic for the proof call derives from canonical role/expectation data rather than hardcoded MSCA fallback IDs.
- Existing expectation-backed legacy calls keep current behavior.
- The resulting classification path is auditable and reusable by later backend validation tasks.
TDD Plan:
- RED: add `test_wf0063_reviewer_policy_derives_proof_call_roles_from_canonical_data` in `backend/tests/test_reviewer_policy.py`.
- GREEN: implement the smallest reviewer-policy change needed to replace hardcoded proof-call fallback logic with canonical derivation.
- REFACTOR: extract a focused backend role-resolution helper only if reviewer-policy code becomes overloaded with canonical parsing.
Verification Steps:
- `cd backend && uv run pytest tests/test_reviewer_policy.py -k "wf0063_reviewer_policy_derives_proof_call_roles_from_canonical_data"`
- `cd backend && rg -n "_STEP_2_NODE_IDS|node_role|has_expectations" app/services/reviewer_policy.py`
Risks (if any): Leaving even one proof-call hardcoded fallback behind defeats the single-source role requirement across layers.

### [ ] Task 9 — Fail-closed backend submit and compliance validation for supporting nodes

Goal:
Make the backend authoritative on the primary-only boundary by rejecting supporting-node content in structured review and compliance requests instead of silently accepting or dropping it.
Slice: backend-submit-guard
User Stories: US2, US4
PRD Requirements: FR8, FR9, FR10, FR16
Depends on: 8
Enables: 10, 11
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/services/structured_reviewer_service.py`
- `backend/app/services/compliance_engine.py`
- `backend/tests/test_api.py`
May touch files:
- `backend/tests/test_structured_reviewer_service.py`
- `backend/app/schemas/compliance.py`
Out of scope: new supporting-context request modes, frontend-only filtering, DB schema migrations
Stop if: enforcing the boundary requires new persistence columns, per-review flags, or a second request payload branch for supporting nodes
Session boundary after: yes
Acceptance Criteria:
- Structured review requests containing supporting node IDs fail with deterministic contract errors.
- Compliance requests treat supporting nodes as invalid primary-review draft input for opted-in calls.
- Legacy non-opted-in calls preserve current behavior.
TDD Plan:
- RED: add `test_wf0063_structured_review_rejects_supporting_nodes_for_primary_path` and `test_wf0063_compliance_rejects_supporting_nodes_for_primary_path` in `backend/tests/test_api.py`.
- GREEN: implement the minimum service-layer validation needed to reject supporting-node submissions against canonical role data.
- REFACTOR: isolate shared primary-only boundary checks only if review and compliance validation start duplicating the same canonical lookup logic.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0063_structured_review_rejects_supporting_nodes_for_primary_path or wf0063_compliance_rejects_supporting_nodes_for_primary_path"`
- `cd backend && rg -n "supporting|node_role|submitted_leaf_ids|draft_nodes" app/services/structured_reviewer_service.py app/services/compliance_engine.py`
Risks (if any): Silent dropping of supporting-node payloads would violate the WF’s fail-closed semantic boundary even if the UI filters correctly.

### [ ] Task 10 — Backend review-detail role labeling seam

Goal:
Add explicit review-detail output fields for primary evaluated content and reserved supporting context so downstream consumers no longer infer participation semantics from cards or submitted-leaf heuristics alone.
Slice: review-detail-contract
User Stories: US2, US4
PRD Requirements: FR11, FR12, FR16
Depends on: 8, 9
Enables: 11
Parallelizable: no
Files to modify:
Must touch files:
- `backend/app/schemas/api.py`
- `backend/app/repositories/review_repository.py`
- `backend/tests/test_api.py`
May touch files:
- `backend/main.py`
Out of scope: frontend copy polish, supporting-context execution mode, mixed-version compatibility redesign beyond this WF
Stop if: explicit role-label fields would require retrofitting old review records with a DB migration instead of deriving safe defaults at read time
Session boundary after: no
Acceptance Criteria:
- Review-detail responses expose `primary_evaluated_node_logical_ids`.
- Review-detail responses expose `supporting_context_node_logical_ids` and default it to `[]` for MVP primary-path reviews.
- Backend output semantics never imply supporting-node participation in primary review when no explicit context mode exists.
TDD Plan:
- RED: add `test_wf0063_review_detail_exposes_primary_evaluated_and_empty_supporting_context_fields` in `backend/tests/test_api.py`.
- GREEN: implement the minimum repository/API response changes needed to persist or derive the new role-label seams safely.
- REFACTOR: centralize role-label field derivation only if repository and API assembly duplicate the same fallback logic.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0063_review_detail_exposes_primary_evaluated_and_empty_supporting_context_fields"`
- `cd backend && rg -n "primary_evaluated_node_logical_ids|supporting_context_node_logical_ids" app/schemas/api.py app/repositories/review_repository.py`
Risks (if any): If review detail keeps relying on cards-only inference, supporting nodes can appear silently reviewed despite fail-closed submit enforcement.

### [ ] Task 11 — Review-detail BFF and page label primary evaluated versus supporting context

Goal:
Thread the new backend role-label fields through the BFF and review page so researchers can distinguish what was evaluated, what remains reserved supporting context, and what was visible but not part of the review.
Slice: review-detail-ui
User Stories: US2
PRD Requirements: FR6a, FR11, FR12, FR16
Depends on: 5, 10
Enables: 12
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `frontend/src/lib/bff/types.ts`
Out of scope: card-generation redesign, persisted supporting-context mode, generic review-detail visual refresh
Stop if: the page cannot render the three required states without backend semantics beyond Task 10
Session boundary after: no
Acceptance Criteria:
- Review detail labels `Primary evaluated` separately from `Supporting context`.
- MVP proof-call reviews show `Supporting context` as empty/reserved unless a later explicit context mode exists.
- Nodes visible in the call but not part of the review are labeled distinctly from evaluated content.
TDD Plan:
- RED: add `wf0063_review_detail_labels_primary_evaluated_supporting_context_and_not_part_of_review` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`.
- GREEN: implement the minimum BFF/page changes needed to consume the new fields and render the three distinct labels.
- REFACTOR: extract a tiny label-mapping helper only if role-aware copy selection becomes repetitive.
Verification Steps:
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0063_review_detail_labels_primary_evaluated_supporting_context_and_not_part_of_review"`
- `cd frontend && rg -n "Primary evaluated|Supporting context|Visible but not part of this review" 'src/app/api/bff/reviews/[reviewId]/route.ts' 'src/app/app/reviews/[reviewId]/page.tsx'`
Risks (if any): A UI-only label update without backend field plumbing can reintroduce inference-based semantics and hide regressions.

### [ ] Task 12 — Proof-call parity and legacy-behavior closure guard

Goal:
Close the workflow with deterministic regressions that prove opted-in `MSCA-PF-2025` behavior across YAML/API/submit/review-detail seams while confirming non-opted-in legacy calls do not flip behavior.
Slice: closure-guard
User Stories: US1, US2, US3, US4
PRD Requirements: FR1a, FR4, FR10, FR12, FR15, FR16
Depends on: 4, 7, 9, 10, 11
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `backend/tests/test_call_nodes_tree_api.py`
- `backend/tests/test_ingest_call_v2_db.py`
Out of scope: broader multi-call rollout, new telemetry framework, walkthrough completion docs
Stop if: parity proof requires broadening scope beyond the proof call or weakening legacy-behavior assertions to keep tests passing
Session boundary after: yes
Acceptance Criteria:
- Automated coverage proves `MSCA-PF-2025` opt-in behavior is aligned across canonical YAML, nodes API, submit/compliance boundaries, and review-detail labels.
- Automated coverage proves supporting nodes never silently influence primary review outputs in MVP.
- Automated coverage proves non-opted-in legacy calls retain current behavior.
- Automated coverage proves the proof-call runtime opt-in can be disabled to restore legacy behavior without re-authoring the canonical YAML.
TDD Plan:
- RED: add `wf0063_proof_call_parity_holds_across_api_submit_and_review_detail`, `wf0063_non_opted_in_calls_preserve_legacy_behavior`, and `wf0063_proof_call_opt_in_rollback_restores_legacy_behavior` across the touched backend/frontend test files.
- GREEN: add only the final assertions and fixture wiring required after Tasks 1 through 11 are green.
- REFACTOR: trim duplicated WF-0063 fixtures if parity setup becomes noisy across backend and frontend tests.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0063_proof_call_parity_holds_across_api_submit_and_review_detail or wf0063_non_opted_in_calls_preserve_legacy_behavior"`
- `cd backend && uv run pytest tests/test_api.py -k "wf0063_proof_call_opt_in_rollback_restores_legacy_behavior"`
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0063_proof_call_parity_holds_across_api_submit_and_review_detail"`
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0063_non_opted_in_calls_preserve_legacy_behavior"`
Risks (if any): Without an explicit closure guard, the proof call can look correct in one surface while still leaking silent regressions across another.

## Changelog

- v0.1 (2026-03-08): Initial task breakdown from PRD.
- v0.2 (2026-03-08): Tightened proof-call opt-in versus legacy boundaries, split frontend/backend role seams into atomic tasks, and added explicit parity and fail-closed closure coverage; marked Ready for Implementation.
- v0.3 (2026-03-08): Review-and-harden pass added explicit proof-call rollback coverage so disabling the opt-in seam must restore legacy behavior without YAML re-authoring.
