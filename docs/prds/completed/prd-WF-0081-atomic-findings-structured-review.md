<!-- docs/prds/completed/prd-WF-0081-atomic-findings-structured-review.md -->
# WF-0081 — Atomic Findings Structured Review

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-14

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher reading a new structured review, I want findings grouped under the reviewed proposal nodes and labeled by evaluation criteria/elements, so I can see exactly what to revise in context.
- US2: As a maintainer, I want new structured reviews to persist atomic findings without breaking legacy `ReviewCard` reads, so the new detail contract ships safely alongside existing reviews.
- US3: As a backend/frontend integrator, I want one explicit review-detail API that can return either legacy cards or reviewed-node findings, so clients can support both contracts without guessing.
- US4: As a workflow owner, I want the implementation pre-split into sequential atomic slices across persistence, backend generation, API, frontend, and compatibility, so Phase 2 tasks can stay within the repo’s 3-file discipline.

## Deferred Stories (Not in MVP)

- As a maintainer, I want historical legacy reviews backfilled into `ReviewFinding`.
- As a researcher, I want review history, exports, and every downstream surface redesigned around findings immediately.
- As a maintainer, I want `ReviewCard` retired entirely.

## 1. In Scope

- Introduce a persisted `ReviewFinding` contract for new structured reviews on the atomic findings path. `(US1) (US2)`
- Preserve legacy review reads and rendering from `ReviewCard`. `(US2) (US3)`
- Add a dual-path review-detail response that returns `reviewed_nodes[].findings[]` for new reviews while keeping legacy card reads intact. `(US1) (US3)`
- Keep reviewed-node grouping as the primary researcher reading model for findings-based reviews. `(US1) (US3)`
- Plan the end-to-end path across persistence/model, backend generation/output, review-detail API, frontend rendering, and compatibility/migration. `(US2) (US3) (US4)`
- Encode the later implementation as sequential atomic slices that prefer three files or fewer per task. `(US4)`

## 2. Out of Scope

- Replacing the current engine SSOT or redesigning the review engine from scratch. `(US2)`
- Breaking or migrating legacy `ReviewCard` reviews as part of MVP rollout. `(US2) (US3)`
- Backfilling historical reviews into `ReviewFinding` during WF-0081. `(US2)`
- Broad history/list/export redesign beyond what is required to keep the review detail page honest. `(US1) (US3)`
- Reopening WF-0080 launch-wedge scope or coupling WF-0081 to that shipped wedge. `(US2) (US4)`

## 3. User / System Flow

- Happy path — new structured review on the atomic findings path
  - Structured review generation runs through the current engine path, which already produces diagnostic findings before collapsing them into `ReviewCard`. `(US1) (US2)`
  - The new write path maps those diagnostic findings into persisted `ReviewFinding` rows, each anchored to one review, one reviewed node, and one evaluation element snapshot. `(US1) (US2)`
  - `GET /reviews/{review_id}` returns a findings-based detail contract with `reviewed_nodes[]`, each containing `findings[]` grouped under the reviewed node. `(US1) (US3)`
  - The frontend renders grouped findings with evaluation criterion/element labels, issue summary, evidence basis, actionable feedback, and explicit `REQUIREMENTS_MET` states when no issue blocks that element. `(US1) (US3)`
- Happy path — legacy review detail
  - Existing legacy review reads continue to return `ReviewCard`-based detail responses and render through the current card flow without requiring `ReviewFinding` data. `(US2) (US3)`
- Failure path — mixed contract assumption
  - If a review has only legacy cards, backend and frontend must not assume `findings[]` exist or synthesize them on read. `(US2) (US3)`
- Failure path — incomplete findings mapping
  - If the engine diagnostic finding lacks one of the persisted detail fields, the write path must fail closed or synthesize the missing field through one bounded mapper instead of silently dropping structure. `(US1) (US2)`
- Failure path — page-local truthfulness
  - If the review detail page exposes copy/export or related same-page actions, they must stay truthful to whichever detail contract is rendered, or explicitly surface a bounded limitation until widened in a later slice. `(US1) (US3)`

## 4. Functional Requirements

- FR1 (US2): WF-0081 must preserve the current engine truth that diagnostic findings already exist before `ReviewCard` collapse; the workflow may re-expose and persist that structure, but must not replace the upstream engine in MVP.
- FR2 (US1) (US2): New structured reviews on the atomic path must persist one `ReviewFinding` per visible evaluation-element-level finding.
- FR3 (US1) (US2): Each `ReviewFinding` must anchor to one review, one reviewed proposal node, and one evaluation element snapshot sufficient for historical renderability.
- FR4 (US1): Each `ReviewFinding` must expose first-class fields for severity, assessment status, issue summary, evidence basis, and actionable feedback rather than one collapsed text blob.
- FR5 (US1) (US2): The findings path must support an explicit positive `REQUIREMENTS_MET` state alongside existing `ASSESSED` and `NOT_ASSESSABLE` semantics.
- FR6 (US2) (US3): Legacy reviews must continue to read and render from `ReviewCard` without mandatory backfill.
- FR7 (US1) (US3): New review-detail responses must expose `reviewed_nodes[].findings[]` grouped under reviewed nodes rather than a flat review-level list.
- FR8 (US1) (US3): The frontend must render the findings-based detail shape for new reviews while preserving the current legacy `ReviewCard` path for old reviews.
- FR9 (US2) (US3): The API contract must make the legacy-vs-atomic mode explicit so backend and frontend do not infer the response shape heuristically.
- FR10 (US1) (US3): Researcher-facing copy for the new detail path must use `evaluation criteria` / `evaluation elements` terminology and must not surface `rubric`.
- FR11 (US2): The generation and persistence flow must name one canonical owner for `ReviewFinding` writes so findings and cards do not become competing truths.
- FR12 (US1) (US3): Any same-page detail actions that expose rendered findings content must remain truthful to the active contract or declare a bounded limitation until widened deliberately.
- FR13 (US4): Phase 2 planning must preserve sequential atomic slices that prefer touching no more than three files each and remain independently testable.

## 5. Data & API Contracts

- Persisted finding contract `(US1) (US2) (FR2) (FR3) (FR4) (FR5)`
  - `ReviewFinding`
  - Required fields:
    - `id`
    - `review_id`
    - `proposal_node_id`
    - `proposal_node_logical_id_snapshot`
    - `proposal_node_title_snapshot`
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
  - Validation rules:
    - one row represents one reviewed-node plus one evaluation-element finding;
    - snapshot fields are required for historical renderability even if upstream call definitions later change;
    - `assessment_status` must reject unknown states and explicitly permit `REQUIREMENTS_MET`, `ASSESSED`, and `NOT_ASSESSABLE`;
    - text fields must be trimmed non-empty for issue-bearing findings; positive findings may use bounded positive guidance text rather than empty blobs.
- Generation/write-path contract `(US1) (US2) (FR1) (FR11)`
  - Input: current engine diagnostic findings plus reviewed-node context.
  - Output: persisted `ReviewFinding` rows for new atomic reviews only.
  - Write-owner rule: one backend mapping seam owns the transformation from engine diagnostic finding to persisted `ReviewFinding`; legacy `ReviewCard` compatibility reads remain separate.
  - Fail-closed rule: if a diagnostic finding cannot be mapped to the required persisted contract, the write path must raise/log a bounded failure rather than silently dropping the finding.
- Review-detail response contract `(US1) (US2) (US3) (FR6) (FR7) (FR8) (FR9)`
  - Legacy mode:
    - existing `ReviewCard` response shape remains valid for legacy reviews;
    - response metadata must include `detail_mode = legacy_cards`.
  - Atomic mode:
    - response metadata must include `detail_mode = reviewed_node_findings`;
    - `reviewed_nodes[]` fields:
      - `proposal_node_id`
      - `proposal_node_logical_id`
      - `proposal_node_title`
      - `node_role`
      - `findings[]`
    - each `finding` includes:
      - `finding_id`
      - `evaluation_criterion`
      - `evaluation_element`
      - `severity`
      - `assessment_status`
      - `issue_summary`
      - `evidence_basis`
      - `actionable_feedback`
  - Response invariants:
    - each review exposes exactly one primary researcher-visible detail mode;
    - legacy responses do not require findings;
    - atomic responses do not require legacy card rollups to render;
    - grouping stays under reviewed nodes, not a flat review-wide findings array.
- State transitions `(US1) (US2) (FR5) (FR6)`
  - legacy review: stored and read through `ReviewCard`;
  - new atomic review: stored and read through `ReviewFinding` grouped under reviewed nodes;
  - per-review detail mode is immutable for researcher-visible reads once persisted;
  - mixed rollout safety: existing legacy reviews are never auto-migrated at read time.

## 6. Components / Modules

- Persistence/model seam
  - Responsibility: define `ReviewFinding`, its migration boundary, and the minimum snapshot fields needed for durable renders.
  - Suggested file paths: `backend/app/models/...`, migration module, repository seam for finding reads/writes.
- Backend generation/output seam
  - Responsibility: map current engine diagnostic findings into `ReviewFinding` writes for new reviews only.
  - Suggested file paths: structured review generation service, mapper/helper module, repository write seam.
- Review-detail API seam
  - Responsibility: assemble legacy-card or reviewed-node-findings responses explicitly and preserve backward compatibility.
  - Suggested file paths: review-detail schema module, repository/query seam, HTTP response assembly seam.
- Frontend render seam
  - Responsibility: render the active detail mode truthfully on the review detail page using evaluation criteria/elements terminology.
  - Suggested file paths: review detail page/container, detail view component, typed response adapter.
- Compatibility/migration seam
  - Responsibility: gate which reviews use cards vs findings, preserve mixed-rollout safety, and document deferred backfill/removal work.
  - Suggested file paths: migration file, rollout discriminator/config seam, compatibility helper or response adapter.
- Design tree / ordering
  - 1. Persistence/model seam lands first so later slices have a durable contract.
  - 2. Backend generation/output seam lands second so new reviews can write findings.
  - 3. Review-detail API seam lands third so stored findings become readable.
  - 4. Frontend render seam lands fourth so researchers can see the new contract.
  - 5. Compatibility/migration seam closes rollout safety and same-page truthfulness edges.
- Deep-module expectations
  - Keep one narrow mapper boundary for diagnostic-finding-to-`ReviewFinding` transformation.
  - Keep response assembly explicit rather than spreading legacy/new branching across multiple callers.
  - Keep frontend branching at the review-detail boundary instead of duplicating heuristics across leaf components.

## 7. Edge Cases

- Legacy reviews with only `ReviewCard` rows must still render without placeholder findings. `(US2) (US3)`
- New atomic reviews with zero issue findings for a reviewed node must still be able to surface explicit positive `REQUIREMENTS_MET` guidance. `(US1)`
- If a diagnostic finding can anchor to a node but not to a stable evaluation-element snapshot, the write path must fail closed or route through one approved synthesis seam rather than persisting partial truth. `(US1) (US2)`
- Mixed-rollout environments must not auto-backfill or infer contract mode from missing fields alone. `(US2) (US3)`
- Same-page copy/export actions on `/app/reviews/[reviewId]` must not show legacy-card text while the page renders findings-based detail unless that limitation is made explicit to the researcher. `(US1) (US3)`

## 8. Testing Decisions (TDD)

- Use TDD for each behavior change: write one RED test per slice before implementation, then make the minimal GREEN change, then refactor. `(US2) (US4)`
- Test seams:
  - persistence/model seam: model + migration + repository contract;
  - backend generation/output seam: mapping/write owner for diagnostic finding to `ReviewFinding`;
  - API seam: review-detail response assembly for legacy vs atomic mode;
  - frontend seam: review detail rendering for both response modes and same-page truthfulness boundaries.
- Mock only boundaries:
  - mock external service boundaries and persistence boundaries where needed;
  - do not mock away the mapper or response assembler being verified.
- Minimal required proof by story:
  - US1: deterministic backend/API/frontend assertions that findings render grouped under reviewed nodes with evaluation criteria/elements labels and positive states;
  - US2: deterministic compatibility tests proving legacy `ReviewCard` reads still work, new reviews persist/read `ReviewFinding`, and one review cannot expose both modes as primary read truth;
  - US3: deterministic contract tests for explicit `detail_mode`, dual-path response assembly, and same-page truthful handling when copy/export actions are present;
  - US4: Phase 2 tasks must keep selectors/task seams atomic enough to prove each slice independently.
- Proceed gate:
  - no Phase 2 plan should mark Ready for Implementation unless it carries proof for both legacy and atomic paths and preserves the note that diagnostic findings already exist before `ReviewCard` collapse.

## 9. Telemetry (Minimal)

- Record review-detail mode usage (`legacy_cards` vs `reviewed_node_findings`) to confirm rollout behavior. `(US2) (US3)`
- Record bounded write-path failures for diagnostic-finding-to-`ReviewFinding` mapping. `(US2)`
- Record findings render/copy limitations only if a same-page truthful fallback is temporarily needed. `(US1) (US3)`

## 10. Deferred / Not in MVP

- Historical backfill from `ReviewCard` to `ReviewFinding`.
- Retirement of `ReviewCard` as a compatibility surface.
- Broad review history, export, and cross-surface redesign beyond the detail page truthfulness seam.
- Engine redesign beyond reusing the current diagnostic findings truth.

## 11. Open Questions (if any)

- None blocking for Phase 1. If same-page copy/export behavior proves coupled during Phase 2 repo grounding, keep the smallest truthful MVP path explicit rather than widening silently.

## 12. Changelog

- v0.1 (2026-03-14): Initial PRD from the approved WF-0081 brainstorm, preserving legacy `ReviewCard` compatibility and the existing diagnostic-finding engine truth.
- v0.2 (2026-03-14): Applied Phase 1 risk-audit edits, locking explicit detail-mode metadata, single-mode read invariants, and task-phase proof expectations.
