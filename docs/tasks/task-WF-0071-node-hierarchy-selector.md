# WF-0071 — Node Hierarchy Selector Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-03-10

## Task Breakdown (Sequential Order)

### [x] Task 1 — Node Hierarchy Parsing Logic
Goal: Transform flat NodeSummary[] into a structured format supporting `isContainer`, handling orphan nodes with an "Uncategorized" fallback, and remove the legacy exception `nested_nodes`.
Slice: Node Hierarchy Parsing
User Stories: US1
PRD Requirements: FR1
Depends on: none
Enables: Task 2
Parallelizable: no
Files to modify:
Must touch files: `frontend/src/lib/submit/renderModel.ts`, `frontend/src/lib/submit/renderModel.test.ts`
May touch files: none
Out of scope: Recursive N-deep tree structures; changing backend schemas.
Stop if: Parsing logic cannot handle existing flat structures or breaks other form types.
Session boundary after: no
Acceptance Criteria: `isContainer` correctly identifies nodes with children; orphan nodes missing a parent are grouped under "Uncategorized"; `parent_node_id !== null` no longer throws an error.
TDD Plan:
- RED: Add unit test in `renderModel.test.ts` for flat-to-grouped parsing logic, container identification, and the "Uncategorized" fallback for orphans.
- GREEN: Update `renderModel.ts` to implement grouping logic and remove the `nested_nodes` exception.
- REFACTOR: skip
Verification Steps: Run tests with `cd frontend && npm test -- renderModel.test.ts`.

### [x] Task 2 — Submit Form Visual Grouping
Goal: Ensure the submit form renders 1-level visual grouping for nested nodes and that grouping headers are unselectable.
Slice: Submit Form Grouping
User Stories: US1
PRD Requirements: FR2, FR4
Depends on: Task 1
Enables: none
Parallelizable: no
Files to modify:
Must touch files: `frontend/src/components/submit/UniversalSubmitForm.tsx`, `frontend/src/components/submit/UniversalSubmitForm.test.tsx`
May touch files: none
Out of scope: Deep recursive styling and multi-node chunk submissions.
Stop if: Tests fail to simulate form submission or the grouping headers become selectable.
Session boundary after: no
Acceptance Criteria: Form displays a flat list with visual grouping/indentation; "not yet supported" message is removed; only leaf nodes (child nodes) are selectable for submission.
TDD Plan:
- RED: Add integration test in `UniversalSubmitForm.test.tsx` verifying leaf `node_id` submission and asserting grouping headers are not selectable.
- GREEN: Update `UniversalSubmitForm.tsx` to render 1-level grouped items and remove the unsupported state message.
- REFACTOR: skip
Verification Steps: Run tests with `cd frontend && npm test -- UniversalSubmitForm.test.tsx`.

### [x] Task 3 — Review Card Breadcrumb Context
Goal: Construct and display an ancestor breadcrumb path for a node to show its structural context.
Slice: Review Card Context
User Stories: US2
PRD Requirements: FR3
Depends on: none
Enables: none
Parallelizable: no
Files to modify:
Must touch files: `frontend/src/components/review/ReviewCard.tsx` (or equivalent context wrapper), `frontend/src/components/review/ReviewCard.test.tsx`
May touch files: none
Out of scope: Modifying backend call configuration data structures.
Stop if: `callConfig` is missing the necessary metadata to resolve breadcrumbs or `parent_logical_id`.
Session boundary after: no
Acceptance Criteria: Breadcrumb shows ancestor path for the node using `node_id` lookup in `callConfig`.
TDD Plan:
- RED: Add test in `ReviewCard.test.tsx` for dynamic breadcrumb ancestor path resolution.
- GREEN: Update `ReviewCard.tsx` to construct and render the breadcrumb using context.
- REFACTOR: skip
Verification Steps: Run tests with `cd frontend && npm test -- ReviewCard.test.tsx`.
Risks (if any): None identified.

## Changelog

- v0.1 (2026-03-10): Initial tasks from PRD
- v0.2 (2026-03-10): Applied Phase 2.2 review (no blocking issues found) and marked Ready for Implementation
- v0.3 (2026-03-10): Addressed Phase 2 Part B adversarial review: Added "Uncategorized fallback" edge case to Task 1.
