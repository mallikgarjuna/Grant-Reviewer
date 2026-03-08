<!-- docs/tasks/task-WF-0064-opted-in-hierarchical-submit-proof-closure.md -->
# WF-0064 — Opted-In Hierarchical Submit Proof Closure

Artifact: task
Version: v0.4
Status: Ready for Implementation
Last Updated: 2026-03-08

Type: feature

## Phase 2 Audit Gate

- This artifact passed the fail-closed Phase 2 audit after closure of the justified planning findings below.
- No implementation-complete or ship recommendation is valid until explicit pass/fail verification evidence is recorded for the WF-0064 selectors in this task after execution.
- Blocking findings must close before any proceed recommendation. Non-blocking findings must also close unless explicitly rejected with rationale.

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: proof-path submit renders supporting nodes read-only with opt-in parity

Goal:
Prove the first end-to-end WF-0064 slice by making visible supporting nodes read-only for opted-in `MSCA-PF-2025` while non-opted-in calls keep current editable behavior.
Slice: tracer-bullet
User Stories: US1, US4
PRD Requirements: FR1, FR2, FR9, FR10
Depends on: none
Enables: 2, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
May touch files:
- `frontend/src/lib/submit/renderModel.ts`
Out of scope: draft persistence cleanup, backend validation, review-detail coverage
Stop if: proof-path read-only rendering requires a second rollout seam beyond the existing `MSCA-PF-2025` opt-in or changes behavior for non-opted-in calls
Session boundary after: no
Acceptance Criteria:
- Visible supporting content nodes render in the submit UI as non-editable for opted-in `MSCA-PF-2025`.
- Eligible primary content nodes remain editable on the same proof path.
- Non-opted-in calls preserve current editable behavior for the same node shapes.
TDD Plan:
- RED: add `wf0064_submit_form_renders_supporting_nodes_read_only_for_msca_pf_2025` and `wf0064_submit_form_preserves_editable_behavior_without_opt_in` in `frontend/src/components/submit/UniversalSubmitForm.test.tsx`.
- GREEN: implement the smallest submit-form rendering change needed to gate supporting-node editability behind the existing proof-call opt-in only.
- REFACTOR: extract a tiny read-only decision helper only if role plus opt-in checks become duplicated in the form.
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0064_submit_form_renders_supporting_nodes_read_only_for_msca_pf_2025|wf0064_submit_form_preserves_editable_behavior_without_opt_in"`
- `cd frontend && rg -n "readOnly|disabled|node_role|supporting" src/components/submit/UniversalSubmitForm.tsx`
Risks (if any): A visual read-only treatment without a real input-state block will leave a hidden write path intact.

### [x] Task 2 — Block supporting draft writes and stale clear-loss on the proof path

Goal:
Remove supporting-node answer writes from local draft state on the proof path and prove stale supporting draft residue cannot be silently cleared during successful primary submit.
Slice: draft-safety
User Stories: US1
PRD Requirements: FR3, FR4, FR13
Depends on: 1
Enables: 3, 5
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/components/submit/UniversalSubmitForm.tsx`
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
- `frontend/src/lib/submit/draftStore.ts`
May touch files:
- `frontend/src/lib/submit/renderModel.ts`
Out of scope: supporting-context persistence, backend request semantics, review-detail rendering
Stop if: preventing supporting draft writes requires introducing a new supporting draft store or changing successful primary-submit semantics outside the proof path
Session boundary after: yes
Acceptance Criteria:
- Supporting nodes on opted-in `MSCA-PF-2025` do not write local answer state or persisted draft snapshots.
- Stale supporting-node draft residue is ignored for rendering and payload construction on the proof path.
- Successful primary submit does not silently clear user-visible primary content or mutate stale supporting residue as part of a hidden cleanup path.
TDD Plan:
- RED: add `wf0064_submit_form_does_not_write_supporting_nodes_to_draft_state` and `wf0064_submit_success_does_not_silently_clear_stale_supporting_draft_residue` in `frontend/src/components/submit/UniversalSubmitForm.test.tsx`.
- GREEN: implement the minimum form-state and draft-store changes needed to ignore supporting-node writes and stale supporting draft residue on the proof path.
- REFACTOR: isolate a small primary-answer filtering helper only if draft-state and submit-state filtering start to diverge.
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0064_submit_form_does_not_write_supporting_nodes_to_draft_state|wf0064_submit_success_does_not_silently_clear_stale_supporting_draft_residue"`
- `cd frontend && rg -n "loadDraft|saveDraft|clearDraft|localStorage|supporting" src/components/submit/UniversalSubmitForm.tsx src/lib/submit/draftStore.ts`
Risks (if any): Hidden autosave or submit-success cleanup code can still erase or serialize supporting entries after the form looks correct.

### [x] Task 3 — Preserve fail-closed backend rejection for supporting-node primary submits

Goal:
Lock unchanged backend primary-path behavior so crafted supporting-node payloads still fail closed with `SUPPORTING_NODE_NOT_ALLOWED` on both compliance and structured-review endpoints.
Slice: backend-guardrail
User Stories: US3
PRD Requirements: FR4, FR5, FR8
Depends on: 1
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
May touch files:
- `backend/main.py`
Out of scope: broad backend acceptance changes, supporting-context request branches, new persistence
Stop if: any proposed fix requires widening backend request acceptance instead of preserving the current fail-closed boundary
Session boundary after: no
Acceptance Criteria:
- Crafted supporting-node payloads sent to `/api/check-compliance` still fail with `SUPPORTING_NODE_NOT_ALLOWED`.
- Crafted supporting-node payloads sent to `/api/structured-review` still fail with `SUPPORTING_NODE_NOT_ALLOWED`.
- `supporting_context_node_logical_ids` remains unused and empty for WF-0064; no backend path starts accepting supporting context.
TDD Plan:
- RED: add `test_wf0064_check_compliance_rejects_supporting_nodes_with_existing_error` and `test_wf0064_structured_review_rejects_supporting_nodes_with_existing_error` in `backend/tests/test_api.py`.
- GREEN: change backend code only if required to preserve the existing rejection behavior under the revised proof-path UI contract.
- REFACTOR: skip unless test setup duplication around supporting-node payload crafting becomes hard to audit.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0064_check_compliance_rejects_supporting_nodes_with_existing_error or wf0064_structured_review_rejects_supporting_nodes_with_existing_error"`
- `cd backend && rg -n "SUPPORTING_NODE_NOT_ALLOWED|supporting_context_node_logical_ids" main.py tests/test_api.py`
Risks (if any): Frontend-only filtering can mask a widened backend boundary unless the fail-closed contract stays explicitly tested.

### [x] Task 4 — Reuse the existing role-aware classification seam for review detail

Goal:
Extend the existing proof-path classification seam across the live role and render-model helpers so review detail distinguishes reviewed primary nodes from visible supporting nodes without introducing a second review-only helper.
Slice: shared-classification
User Stories: US2, US4
PRD Requirements: FR6, FR7, FR11, FR12
Depends on: 3
Enables: 5
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/lib/submit/nodeRoles.ts`
- `frontend/src/lib/submit/nodeRoles.test.ts`
- `frontend/src/lib/submit/renderModel.ts`
- `frontend/src/lib/submit/renderModel.test.ts`
May touch files:
- `frontend/src/lib/bff/types.ts`
Out of scope: review-detail page copy polish, submit-form rendering, new cross-layer abstraction beyond the existing seam
Stop if: single-source review-detail classification cannot be implemented by extending the current role plus render-model seam and instead needs a new generalized backend/frontend framework
Session boundary after: no
Acceptance Criteria:
- The existing shared role-aware seam derives stage-eligible visible non-container nodes, visible supporting nodes, and structural containers for review detail without duplicating child/container inference in the page.
- Review detail does not fall back to `has_expectations` leaves, page-local call-specific allowlists, or a new review-only classifier.
- The change stays scoped to current seams and does not introduce a broader multi-call framework beyond WF-0064 needs.
TDD Plan:
- RED: add `wf0064_node_roles_support_review_detail_classification_without_new_helper` in `frontend/src/lib/submit/nodeRoles.test.ts` and `wf0064_render_model_and_node_roles_share_review_detail_classification_contract` in `frontend/src/lib/submit/renderModel.test.ts`.
- GREEN: implement the minimum shared seam changes needed so submit and review detail consume the same reviewed-versus-visible-supporting classification source.
- REFACTOR: inline or collapse duplicated boolean branches only after tests prove the shared `nodeRoles` plus `renderModel` seam remains the single classification source.
Verification Steps:
- `cd frontend && npx vitest run src/lib/submit/nodeRoles.test.ts src/lib/submit/renderModel.test.ts -t "wf0064_node_roles_support_review_detail_classification_without_new_helper|wf0064_render_model_and_node_roles_share_review_detail_classification_contract"`
- `cd frontend && rg -n "has_expectations|supporting|visible|isContainer|reviewStage" src/lib/submit/nodeRoles.ts src/lib/submit/nodeRoles.test.ts src/lib/submit/renderModel.ts src/lib/submit/renderModel.test.ts`
Risks (if any): A helper that still mirrors page-local fallbacks will hide the same coupling behind a new filename.

### [x] Task 5 — Review detail labels visible supporting nodes and preserves empty supporting context

Goal:
Use the shared classifier in review detail so visible supporting nodes appear under `Visible but not part of this review`, coverage counts only stage-eligible visible non-container nodes, and `supporting_context_node_logical_ids` stays empty.
Slice: review-detail
User Stories: US2
PRD Requirements: FR6, FR7, FR8, FR11, FR12
Depends on: 4
Enables: 6
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `frontend/src/lib/submit/nodeRoles.ts`
Out of scope: backend review record persistence, new supporting-context submission, non-proof-path UI redesign
Stop if: honest review-detail labeling requires a backend schema change larger than reusing the existing review-detail response and shared classification source
Session boundary after: yes
Acceptance Criteria:
- Visible supporting nodes such as `abstract` appear under `Visible but not part of this review`.
- Review coverage is computed from stage-eligible visible non-container nodes only, excluding structural containers.
- `supporting_context_node_logical_ids` remains present but empty in the rendered review-detail contract for this WF.
- The visible-supporting section remains scoped to opted-in `MSCA-PF-2025` proof behavior only.
TDD Plan:
- RED: add `wf0064_review_detail_shows_visible_supporting_nodes_with_empty_supporting_context_ids` and `wf0064_review_detail_coverage_ignores_expectations_proxy_and_containers` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`.
- GREEN: implement the smallest review-detail page changes needed to consume the shared classifier and preserve empty supporting-context labeling.
- REFACTOR: extract a tiny section-mapping helper only if label and coverage rendering start duplicating classifier branches.
Verification Steps:
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0064_review_detail_shows_visible_supporting_nodes_with_empty_supporting_context_ids|wf0064_review_detail_coverage_ignores_expectations_proxy_and_containers"`
- `cd frontend && rg -n "Visible but not part of this review|supporting_context_node_logical_ids|coverage" src/app/app/reviews/[reviewId]/page.tsx`
Risks (if any): Coverage can appear honest in one example while still drifting on other visible supporting nodes if the page bypasses the shared classifier anywhere.

### [ ] Task 6 — Rollback and non-opted-in parity proof for the existing opt-in seam

Goal:
Prove the proof-path behavior is fully reversible through the existing opt-in seam and that removing or disabling that seam restores current behavior without extra rollback work.
Slice: compatibility
User Stories: US4
PRD Requirements: FR1, FR9, FR10
Depends on: 5
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `backend/tests/test_api.py`
Out of scope: new feature rollout controls, multi-call expansion, production flag plumbing
Stop if: parity or rollback proof needs a second flag or per-page exception instead of the existing proof-call opt-in seam
Session boundary after: yes
Acceptance Criteria:
- Disabling the existing proof-call opt-in for `MSCA-PF-2025` restores legacy editable submit behavior and removes proof-path-only review-detail labeling.
- Non-opted-in calls continue matching legacy behavior across submit and review detail.
- Non-opted-in calls do not render the `Visible but not part of this review` supporting label unless they separately opt in through the existing seam.
- No task introduces a second activation or rollback mechanism.
TDD Plan:
- RED: add `wf0064_submit_form_rolls_back_when_proof_opt_in_disabled` in `frontend/src/components/submit/UniversalSubmitForm.test.tsx` and `wf0064_review_detail_preserves_legacy_behavior_without_proof_opt_in` in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`.
- GREEN: implement only the minimal opt-in seam usage fixes needed so both submit and review detail obey the same reversible rollout contract.
- REFACTOR: skip unless opt-in resolution is duplicated across submit and review-detail test setup.
Verification Steps:
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0064_submit_form_rolls_back_when_proof_opt_in_disabled"`
- `cd frontend && npx vitest run src/app/app/reviews/[reviewId]/page.test.tsx -t "wf0064_review_detail_preserves_legacy_behavior_without_proof_opt_in"`
- `cd frontend && rg -n "opt_in|MSCA-PF-2025|Visible but not part of this review" src/components/submit/UniversalSubmitForm.test.tsx src/app/app/reviews/[reviewId]/page.test.tsx`
Risks (if any): If rollback is only proven in one surface, the other can retain proof-path behavior and make the seam non-reversible in practice.

## Changelog

- v0.1 (2026-03-08): Initial task breakdown from PRD.
- v0.2 (2026-03-08): Applied review-gate edits to reuse the existing role-aware classification seam, tighten backend guardrail ordering, and make proof-path scope/rollback expectations explicit; marked Ready for Implementation.
- v0.3 (2026-03-08): Reopened readiness after fail-closed audit; required explicit verification evidence before proceed recommendation, replaced nonexistent payload seam with the real draft-store boundary, and expanded shared-classification work to include the live render-model seam.
- v0.4 (2026-03-08): Closed the remaining planning blocker by aligning the PRD readiness gate with Phase 3 runner semantics, then restored `Ready for Implementation` with the hardened Task 2 and Task 4 seams intact.
