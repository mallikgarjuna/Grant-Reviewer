<!-- docs/prds/prd-WF-0081-atomic-findings-structured-review.md -->
# WF-0081 — Atomic Findings Structured Review

Artifact: prd
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-14

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher reading a new structured review, I want feedback grouped by reviewed section and evaluation element, so I can see exactly which evaluation elements need revision.
- US2: As a maintainer, I want new structured reviews to persist atomic findings without breaking legacy `ReviewCard` reads, so we can ship the new detail model safely.
- US3: As a frontend/backend integrator, I want one explicit dual-path review-detail contract, so legacy reviews can keep using cards while new reviews use findings grouped under reviewed nodes.
- US4: As a product owner, I want the implementation split into small sequential slices across persistence, backend generation, API, frontend, and compatibility, so the repo’s atomic-task rule stays intact.

## Deferred Stories (Not in MVP)

- As a maintainer, I want all historical legacy reviews backfilled into `ReviewFinding`.
- As a researcher, I want every review-history/list/export surface redesigned around atomic findings immediately.
- As a maintainer, I want `ReviewCard` removed entirely.

## 1. In Scope

- Introduce a new persisted `ReviewFinding` contract for new atomic-flow structured reviews. `(US1) (US2)`
- Preserve legacy review reads/renders from `ReviewCard`. `(US2) (US3)`
- Add a review-detail response shape for `reviewed_nodes[].findings[]` on new atomic reviews. `(US1) (US3)`
- Keep reviewed-node grouping as the primary reading model for findings-based reviews. `(US1) (US3)`
- Plan the full stack path: persistence/model, generation/write path, API, frontend, and compatibility gating. `(US2) (US3) (US4)`
- Explicitly define the smallest implementation slices for later phases. `(US4)`

## 2. Out of Scope

- Replacing `pipeline_v1` or redefining engine SSOT. `(US2)`
- Breaking legacy `ReviewCard` reads/renders. `(US2) (US3)`
- Backfilling historical reviews as part of the initial MVP. `(US2)`
- Broad history/list/export redesign unless a later phase proves it is required for truthful review-detail rollout. `(US3)`

## 3. User / System Flow

- Happy path — new atomic review
  - Structured review generation runs through the existing engine path, which already produces diagnostic findings before they are collapsed into `ReviewCard`. `(US1) (US2)`
  - The new atomic-flow write path persists `ReviewFinding` rows for the new review, grouped logically by reviewed node and evaluation element. `(US1) (US2)`
  - `GET /reviews/{review_id}` returns `reviewed_nodes[].findings[]` for the new review contract. `(US1) (US3)`
  - The frontend renders findings under each reviewed node, showing evaluation element, issue summary, evidence basis, actionable feedback, and positive `REQUIREMENTS_MET` states when applicable. `(US1) (US3)`
- Happy path — legacy review
  - Existing legacy review reads continue to return `ReviewCard`-based detail responses and render through the existing card flow. `(US2) (US3)`
- Failure/compatibility path
  - If a review has only legacy card data, the API/frontend must not assume findings exist.
  - If a review is on the new findings path, the UI must not require legacy card rollups to render the detail view.

## 4. Functional Requirements

- FR1 (US2): The current engine truth remains unchanged: diagnostic findings already exist before `ReviewCard` collapse, and WF-0081 must build on that reality rather than replacing it.
- FR2 (US1) (US2): New atomic-flow reviews must persist one `ReviewFinding` per visible evaluation-element-level finding.
- FR3 (US1) (US2): Each `ReviewFinding` must anchor to one review, one reviewed proposal node, and one evaluation element snapshot sufficient for historical renderability.
- FR4 (US1): Each `ReviewFinding` must expose severity, assessment status, issue summary, evidence basis, and actionable feedback as first-class fields.
- FR5 (US2) (US3): Legacy reviews must continue to read/render from `ReviewCard` without backfill.
- FR6 (US1) (US3): New review-detail responses must expose findings grouped under reviewed nodes.
- FR7 (US1) (US3): The frontend must render the findings-based detail shape for new reviews and keep legacy card rendering for old reviews.
- FR8 (US1) (US2): The new findings path must support explicit positive pass states via `REQUIREMENTS_MET`.
- FR9 (US4): The implementation plan must stay split into sequential slices that prefer touching no more than three files per slice.

## 5. Data & API Contracts

- Persisted finding contract `(FR2) (FR3) (FR4)`
  - `ReviewFinding`
  - `id`
  - `review_id`
  - `proposal_node_id`
  - `proposal_node_logical_id_snapshot`
  - `evaluation_criterion_logical_id_snapshot`
  - `evaluation_criterion_name_snapshot`
  - `evaluation_element_logical_id_snapshot`
  - `evaluation_element_name_snapshot`
  - `severity`
  - `assessment_status`
  - `issue_summary_text`
  - `evidence_basis_text`
  - `actionable_feedback_text`
  - `created_at`
- Legacy compatibility contract `(FR5)`
  - Existing reviews continue to rely on `ReviewCard` for persisted/read/render behavior.
  - No mandatory legacy backfill is required for MVP.
- Review-detail response contract `(FR5) (FR6) (FR7)`
  - Legacy mode: existing `ReviewCard` response shape remains valid.
  - Atomic mode: `ReviewDetailResponse.reviewed_nodes[]` with:
    - `proposal_node_logical_id`
    - `proposal_node_title`
    - `node_role`
    - `findings[]`
  - Each `finding` includes:
    - `finding_id`
    - `evaluation_criterion`
    - `evaluation_element`
    - `severity`
    - `assessment_status`
    - `issue_summary`
    - `evidence_basis`
    - `actionable_feedback`

## 6. Components / Modules

- Persistence/model seam
  - `ReviewFinding` model plus migration ownership.
- Backend generation/output seam
  - structured review generation path that maps engine findings into persisted `ReviewFinding` rows.
- Review-detail API seam
  - backend response assembly that chooses legacy cards vs findings-based reviewed nodes.
- Frontend render seam
  - review detail page/components that render legacy cards or reviewed-node findings appropriately.
- Compatibility seam
  - gating logic, response typing, and migration rules that keep both contracts honest during rollout.

## 7. Smallest Implementation Slices

- Slice 1 — Persistence/model slice
  - RED: prove the current persistence contract cannot store atomic evaluation-element findings.
  - GREEN: add `ReviewFinding` model + migration with only the minimum snapshot fields.
  - REFACTOR: keep legacy `ReviewCard` untouched.
- Slice 2 — Backend generation/output slice
  - RED: prove the current write path still collapses everything to cards.
  - GREEN: persist `ReviewFinding` rows for new atomic reviews by reusing existing diagnostic finding inputs where possible.
  - REFACTOR: keep mapper ownership explicit so new findings and legacy cards do not become competing truths.
- Slice 3 — Review-detail API slice
  - RED: prove `GET /reviews/{review_id}` cannot yet return reviewed nodes with findings.
  - GREEN: add dual-path response assembly for legacy cards vs findings-based reviewed nodes.
  - REFACTOR: keep response typing explicit and backward compatible.
- Slice 4 — Frontend rendering slice
  - RED: prove the review detail page cannot yet render grouped findings.
  - GREEN: render reviewed nodes with findings while preserving legacy card rendering.
  - REFACTOR: keep researcher-facing terminology aligned to evaluation criteria/elements.
- Slice 5 — Compatibility/migration slice
  - RED: prove legacy reviews or mixed rollout assumptions would break without explicit gating.
  - GREEN: add rollout rules that keep old reviews on cards and new atomic reviews on findings.
  - REFACTOR: document any deferred backfill/removal work explicitly.

## 8. Derived vs New Behavior

- Derived from existing pipeline findings
  - diagnostic findings already exist before `ReviewCard` collapse;
  - node/evaluation-element grounding already exists in the engine and call-definition path;
  - existing `ASSESSED` / `NOT_ASSESSABLE` semantics provide a baseline for findings status;
  - subordinate-prompt and deterministic-guidance context can ground element-level finding generation.
- Requires new generation/persistence behavior
  - durable `ReviewFinding` storage;
  - explicit persisted summary/evidence/actionable fields;
  - explicit `REQUIREMENTS_MET` handling;
  - dual-shape review-detail API behavior;
  - frontend dual-render behavior and compatibility gating.

## 9. Must-Ship vs Deferred

- Must ship
  - `ReviewFinding` persistence for new atomic reviews;
  - backend generation/write path for findings;
  - dual-path review-detail API;
  - frontend findings render grouped under reviewed nodes;
  - legacy `ReviewCard` compatibility.
- Deferred
  - historical backfill;
  - `ReviewCard` retirement;
  - broader review-history/list/export redesign.

## 10. Key Risks

- Duplicate-truth risk between `ReviewFinding` and `ReviewCard`.
- Response-shape drift risk if legacy/new review detail modes are not explicit.
- Hidden engine-coupling risk if we assume every persisted finding field already exists in stable form.
- Frontend regression risk if legacy reviews are not exercised alongside new findings-based reviews.

## 11. Testing Decisions (TDD)

- Start with RED tests at each slice boundary.
- Prove both compatibility paths explicitly: legacy `ReviewCard` reviews and new findings-based reviews.
- Prefer targeted backend/API/frontend tests over broad end-to-end rewrites.

## 12. Verification / Proceed Gate

- No later task plan is valid unless it preserves legacy `ReviewCard` compatibility explicitly.
- No implementation-ready recommendation is valid unless each slice stays atomic and topologically ordered.
- No ship recommendation is valid unless the implementation proves:
  - legacy reviews still read/render from `ReviewCard`;
  - new reviews read/render from findings grouped under reviewed nodes;
  - the current engine diagnostic findings remain the upstream source before `ReviewCard` collapse.

## 13. Changelog

- v0.1 (2026-03-14): Created the canonical WF-0081 PRD draft during Phase 0 to lock the end-to-end atomic findings contract and implementation slices.
