<!-- docs/prds/prd-WF-0064-opted-in-hierarchical-submit-proof-closure.md -->
# WF-0064 — Opted-In Hierarchical Submit Proof Closure

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-08

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher using `MSCA-PF-2025`, I want visible supporting sections in the structured submit flow to be clearly non-editable when they are not part of primary review, so that I am not invited to enter text that will be dropped.
- US2: As a researcher submitting a primary-path review request, I want review detail to distinguish evaluated primary sections from visible-but-excluded supporting sections, so that the product accurately reflects what was and was not reviewed.
- US3: As an engineer maintaining the structured review boundary, I want backend primary-path rejection semantics for supporting nodes to remain fail-closed and unchanged, so that frontend proof-path fixes do not weaken request validation.
- US4: As a maintainer rolling out hierarchical support safely, I want the proof-path behavior to stay opt-in and reversible for `MSCA-PF-2025` only, so that non-opted-in calls preserve current behavior.

## Deferred Stories (Not in MVP)

- DS1: Persist supporting-node content to draft state, review records, or any separate supporting-context storage surface.
- DS2: Add a separate supporting-context request branch or a secondary submit path for hierarchical calls.
- DS3: Generalize the proof-path behavior to calls beyond `MSCA-PF-2025`.
- DS4: Expand supporting nodes into scored, compliance-bearing, or prompt-context-bearing review inputs.

## 1. In Scope

- Lock the proof path to `MSCA-PF-2025` and keep supporting nodes visible but non-editable in the submit UI for that opted-in path only. (US1, US4)
- Ensure supporting nodes do not write local draft state and therefore cannot be silently cleared on successful primary submit. (US1)
- Preserve existing backend primary-path validation and rejection semantics for supporting nodes, including `SUPPORTING_NODE_NOT_ALLOWED`. (US3)
- Update review-detail coverage and labels so stage-eligible visible non-container nodes appear honestly, including visible supporting nodes under `Visible but not part of this review`. (US2)
- Prove parity and rollback safety so non-opted-in calls retain current behavior and the proof-path behavior can be removed through the existing opt-in seam. (US4)

## 2. Out of Scope

- Persisting supporting-node content anywhere in frontend or backend state beyond structural visibility. (DS1)
- Adding `supporting_context_node_logical_ids` population, supporting-context persistence, or a separate request branch. (DS1, DS2)
- Changing primary review create/idempotency semantics or broadening backend acceptance of supporting nodes. (DS1, DS2, US3)
- Generalizing the behavior to every hierarchical or split-role call in the repo. (DS3)
- Reworking call-definition semantics introduced by WF-0063 beyond what is needed to keep the MSCA proof path honest. (DS3, DS4)

## 3. User / System Flow

### Happy path

1. The researcher opens universal submit for opted-in `MSCA-PF-2025` and sees the full visible proposal structure, including supporting nodes already exposed by the WF-0063 split visibility path. (US1, US4)
2. The UI renders visible supporting content nodes with explicit non-editable treatment and supporting-only copy, while editable behavior remains available only for eligible primary content nodes. (US1)
3. Because supporting nodes are non-editable on this proof path, no local draft-state write path records supporting-node content and successful primary submit cannot silently clear unsubmitted supporting text. (US1)
4. The client builds compliance and structured-review payloads from the same primary-only node set used today; supporting nodes remain outside the request boundary. (US1, US3)
5. Backend validation continues rejecting any crafted supporting-node payload on the primary path with unchanged fail-closed semantics, including `SUPPORTING_NODE_NOT_ALLOWED`. (US3)
6. Review detail computes coverage from stage-eligible visible non-container nodes and shows visible supporting nodes in a dedicated `Visible but not part of this review` section while `supporting_context_node_logical_ids` stays empty. (US2)
7. Non-opted-in calls keep their current behavior because this proof-path behavior remains behind the existing opt-in seam only. (US4)

### Failure path A — supporting node is still editable on the proof path

1. A supporting node on opted-in `MSCA-PF-2025` renders as an editable field. (US1)
2. The path is unsafe because the entered text is not part of the primary request boundary or persisted supporting context. (US1, US3)
3. UI tests must fail until the node is rendered non-editable and removed from draft-state writes on the proof path. (US1)

### Failure path B — backend acceptance semantics drift

1. A client crafts a primary submit or compliance payload that includes a supporting node. (US3)
2. If backend validation stops rejecting that payload with the established fail-closed error, the proof path has widened scope incorrectly. (US3)
3. API tests must fail unless the backend still rejects the request with unchanged primary-path semantics. (US3)

### Failure path C — review detail remains misleading

1. Review detail coverage is still derived from `has_expectations` leaves or another expectation-only proxy. (US2)
2. Visible supporting nodes such as `abstract` disappear from coverage accounting or are implied to have been reviewed. (US2)
3. UI/API tests must fail until coverage is derived from stage-eligible visible non-container nodes and supporting nodes are listed under `Visible but not part of this review`. (US2)

## 4. Functional Requirements

- FR1 (US1, US4): The WF-0064 MVP must remain locked to the opted-in `MSCA-PF-2025` proof path and must not broaden behavior for non-opted-in calls.
- FR2 (US1): Visible supporting nodes on the proof path must remain rendered in submit UI but non-editable.
- FR3 (US1): Supporting nodes on the proof path must not write local draft state, local persisted draft snapshots, or other client-side answer state that would later be cleared by successful primary submit.
- FR4 (US1, US3): Primary submit and compliance payload construction must remain primary-only; supporting nodes must stay excluded from payload generation.
- FR5 (US3): Backend `/api/check-compliance` and `/api/structured-review` primary-path validation semantics must remain unchanged, including rejection of supporting nodes with `SUPPORTING_NODE_NOT_ALLOWED`.
- FR6 (US2): Review-detail coverage must be derived from stage-eligible visible non-container nodes, not from `has_expectations` leaves.
- FR7 (US2): Visible supporting nodes for the proof path must appear in review detail under `Visible but not part of this review`.
- FR8 (US2): `supporting_context_node_logical_ids` must remain empty for this WF because no supporting-context request or persistence path is introduced.
- FR9 (US4): The behavior must remain reversible through the existing opt-in seam; removing the opt-in must restore current non-proof-path behavior without extra rollback work.
- FR10 (US4): Non-opted-in calls must preserve current behavior with explicit parity coverage proving no regression from the proof-path change.
- FR11 (US1, US2, US3, US4): Structural containers may remain visible as grouping elements, but coverage and review-detail classification must operate on visible non-container nodes only.
- FR12 (US2, US4): Stage eligibility, visible non-container classification, and visible-supporting classification for review detail must derive from one authoritative role-aware source, not separate frontend-only heuristics or page-local allowlists.
- FR13 (US1): If stale supporting-node draft entries already exist from older proof-path behavior, the revised path must ignore them for rendering/payload purposes and must not silently clear user-visible primary content when submit succeeds.

## 5. Data & API Contracts

### 5.1 Submit and draft-state contract

- The existing primary-path request contract remains the only submit/compliance contract in scope. (US1, US3, FR4, FR5)
- Supporting nodes remain visible UI structure only for this WF; they must not produce answer-state writes in the proof path. (US1, FR2, FR3)
- No new frontend or backend persistence shape is introduced for supporting-node answers. (US1, US3, FR3, FR8)
- The proof path must not add a separate `supporting_nodes`, `supporting_context`, or similar request branch. (US3, FR4, FR8)

### 5.2 Backend validation contract

- Backend primary-path validation for `/api/check-compliance` and `/api/structured-review` remains authoritative and unchanged. (US3, FR5)
- Any supporting node submitted through the primary path must still fail closed with the existing rejection posture, including `SUPPORTING_NODE_NOT_ALLOWED`. (US3, FR5)
- Frontend exclusion of supporting nodes is a UX safeguard only; backend validation remains the enforcement boundary. (US3, FR4, FR5)

### 5.3 Review-detail contract

- Review detail must continue exposing the primary reviewed set while explicitly separating visible supporting nodes that were not part of the review. (US2, FR6, FR7)
- Coverage derivation must use the stage-eligible visible non-container node set for the proof path. (US2, FR6, FR11)
- Supporting nodes such as `abstract` and visible Part B2 sections must be listed under `Visible but not part of this review` rather than omitted or implied reviewed. (US2, FR7)
- `supporting_context_node_logical_ids` remains present but empty in this WF. (US2, FR8)
- Review-detail classification must be computed from the same authoritative role-aware stage-eligibility source used to decide visible reviewed versus visible supporting nodes, so coverage and labels cannot drift from the proof-path contract. (US2, US4, FR6, FR7, FR11, FR12)

### 5.4 Rollout and compatibility contract

- The only proof call in scope is `MSCA-PF-2025`. (US1, US4, FR1)
- Existing opt-in wiring from WF-0063 remains the rollout seam; WF-0064 must not introduce a second activation mechanism. (US4, FR1, FR9)
- Non-opted-in calls retain current behavior and form the regression baseline for parity testing. (US4, FR10)
- Existing stale supporting-node client draft entries, if any, are compatibility residue only; they must not re-enable editing, payload inclusion, or silent clear-loss behavior on the proof path. (US1, FR3, FR13)

## 6. Components / Modules

- `frontend/src/components/submit/UniversalSubmitForm.tsx`
  - Enforce proof-path non-editable supporting-node rendering and keep primary-node editability intact. (FR2, FR4)
- `frontend/src/lib/submit/`
  - Keep payload construction primary-only and remove supporting-node answer-state writes on the proof path. (FR3, FR4)
- `backend/main.py`
  - Preserve current primary-path rejection semantics for supporting nodes without changing accepted payload boundaries. (FR5)
- `backend/tests/test_api.py`
  - Lock unchanged backend fail-closed behavior for supporting-node requests. (FR5)
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Rebuild coverage and display logic from stage-eligible visible non-container nodes and surface `Visible but not part of this review`. (FR6, FR7, FR11)
- Shared role/stage-eligibility derivation seam across backend/BFF/frontend review detail inputs
  - Keep reviewed-versus-visible-supporting classification single-sourced so page rendering cannot drift from proof-path submit semantics. (FR12)
- Existing WF-0063 opt-in seam and related call metadata/runtime plumbing
  - Keep the proof-path rollout reversible and limited to `MSCA-PF-2025`. (FR1, FR9, FR10)

Design tree / dependencies / ordering:
1. Freeze the narrow contract: visible-but-non-editable supporting nodes, no supporting persistence, unchanged backend rejection semantics. (FR2-FR5, FR8)
2. Correct submit UI behavior so supporting nodes cannot be edited or written into draft state on the proof path. (FR2, FR3)
3. Preserve primary-only payload construction and backend fail-closed enforcement. (FR4, FR5)
4. Correct review-detail coverage derivation and labeling for visible supporting nodes. (FR6, FR7, FR11)
5. Ensure the same role-aware classification source feeds review-detail coverage and labels. (FR12)
6. Verify compatibility, stale-draft safety, and rollback behavior for non-opted-in calls and opt-in removal. (FR1, FR9, FR10, FR13)

Deep module guidance:

- Keep one proof path only: `MSCA-PF-2025`.
- Keep fail-closed semantics explicit in both UI affordance and backend validation.
- Do not create a shadow supporting-context data flow to solve a UI honesty problem.
- Derive review-detail coverage from node visibility/stage eligibility and container status, not from expectations-only heuristics.
- Keep review-detail classification single-sourced across any backend/BFF/frontend seam; page-local lists are hidden coupling.
- Treat opt-in removal and non-opted-in behavior as compatibility seams, not optional tests.
- Treat stale supporting drafts from pre-fix behavior as fail-closed compatibility residue; do not quietly revive or silently delete them as part of primary submit success.

Suggested file-path clusters (coarse only):

- submit rendering and payload logic under `frontend/src/components/submit/` and `frontend/src/lib/submit/`
- review-detail display logic under `frontend/src/app/app/reviews/`
- primary-path validation and API tests under `backend/`

## 7. Edge Cases

- A visible supporting node is styled as read-only but still emits answer-state writes through a hidden form handler; this remains a blocker because silent clear-loss risk still exists. (US1, FR2, FR3)
- A successful primary submit clears a stale supporting-node draft bucket even though the UI no longer exposes editing; regression tests must prove no silent clear-loss path remains. (US1, FR3)
- Coverage logic includes structural containers and inflates review-detail accounting; the contract requires visible non-container nodes only. (US2, FR6, FR11)
- Coverage logic falls back to `has_expectations` and omits visible supporting nodes such as `abstract`; this is a review-honesty defect. (US2, FR6, FR7)
- Review detail derives visible-supporting coverage from a page-local heuristic different from the primary submit/reviewed-node classification path; this hidden coupling is a blocker candidate. (US2, US4, FR12)
- Backend or frontend introduces a second seam for enabling proof behavior, making rollback ambiguous; the existing opt-in seam must remain the only rollout control. (US4, FR9, FR10)
- Non-opted-in calls accidentally inherit read-only supporting-node UI behavior; parity tests must block that regression. (US4, FR10)

## 8. Testing Decisions (TDD)

- This WF is a behavior-fix workflow. Implementation must follow RED -> GREEN -> REFACTOR. (US1, US2, US3, US4)
- Public seams under test must include submit UI behavior, submit/draft-state logic, backend primary-path validation, and review-detail display/coverage logic. (US1, US2, US3, US4)
- Mock only external boundaries. Do not mock the logic that decides node editability, draft-state writes, payload inclusion, or review-detail coverage classification. (US1, US2, US3)
- Required automated coverage:
  - submit-form UI test proving visible supporting nodes render as non-editable on `MSCA-PF-2025` while primary nodes remain editable. (US1, FR2)
  - draft-state regression test proving supporting nodes do not write local draft state and cannot be silently cleared on successful primary submit. (US1, FR3)
  - backend API tests proving primary-path submit/compliance still reject supporting nodes with `SUPPORTING_NODE_NOT_ALLOWED`. (US3, FR5)
  - review-detail UI/API tests proving visible supporting nodes such as `abstract` appear under `Visible but not part of this review`, while `supporting_context_node_logical_ids` remains empty. (US2, FR6, FR7, FR8)
  - shared-classification test proving review-detail coverage/labels use the same role-aware stage-eligibility source as the proof-path visibility contract instead of a `has_expectations` or page-local fallback. (US2, US4, FR6, FR11, FR12)
  - parity test proving non-opted-in calls preserve current behavior when the proof-call opt-in seam is absent. (US4, FR9, FR10)
  - rollback-oriented parity test proving the proof-path behavior is removed when the existing opt-in seam is disabled for `MSCA-PF-2025`. (US4, FR9)
  - stale-draft compatibility test proving pre-existing supporting-node draft residue does not re-enable editing, leak into payloads, or silently disappear as a user-visible data loss event. (US1, FR3, FR13)

## 9. Telemetry (Minimal)

- No new telemetry is required for MVP unless one narrow diagnostic is needed to distinguish proof-path read-only rendering from primary-node editability during implementation verification.

## 10. Deferred / Not in MVP

- Any supporting-node persistence layer or server-backed draft semantics.
- Any review record population of supporting context.
- Any separate submit/compliance branch for supporting content.
- Any multi-call rollout beyond the existing `MSCA-PF-2025` proof path.

## 11. Open Questions (if any)

- Exact researcher-facing copy for the proof-path non-editable supporting-node treatment.
- Exact wording and visual treatment of `Visible but not part of this review` in review detail, so long as the semantic contract remains fixed.

## 12. Changelog

- v0.1 (2026-03-08): Initial PRD from brainstorm.
- v0.2 (2026-03-08): Applied risk-audit edits for single-source review-detail classification, stale supporting-draft fail-closed handling, and explicit empty supporting-context verification; marked Ready for Tasks.
