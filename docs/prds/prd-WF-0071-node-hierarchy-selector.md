# WF-0071 — Node Hierarchy Selector

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-10

## 0. User Stories (MVP)
- US1: As a researcher applying to complex nested grants (ERC, MSCA), I want to see a hierarchical grouping of evaluable nodes (e.g., "Part B1 / Section a") in the submission form, so that I can easily find and select the specific section I need to review or submit.

## Deferred Stories (Not in MVP)
- Multi-node chunk submissions (submitting an entire parent node at once).

## 1. In Scope
- Nested node parsing in `renderModel.ts` using `parent_node_id` and `parent_logical_id`.
- UI visual grouping in `UniversalSubmitForm.tsx` (1-level flat grouping with indentation).
- Breadcrumb updates in `ReviewCard.tsx` (or equivalent context display).

## 2. Out of Scope
- Expanding the backend database schema to hold native tree arrays (SQL recursion).
- Multi-node chunk submissions.
- N-deep recursive accordion components.

## 3. User / System Flow
- Happy path (US1): User opens `UniversalSubmitForm` for a complex call (e.g., MSCA or ERC) -> Frontend parses flat `NodeSummary[]` and identifies containers and leaf nodes -> UI renders a flat list with 1-level visual grouping (indentation/headers) -> User selects a leaf node smoothly.
- Failure path 1 (US1): Orphan nodes (missing `parent_logical_id` resolution) -> Fallback to a generic "Uncategorized" group.

## 4. Functional Requirements
- FR1 (US1): `frontend/src/lib/submit/renderModel.ts` MUST transform `NodeSummary[]` to build out groups and nodes arrays supporting an `isContainer` check.
- FR2 (US1): `UniversalSubmitForm.tsx` MUST display a flat list with visual indentation or grouping headers for elements identified as children.
- FR3 (US1): `ReviewCard.tsx` (or its parent wrapper) MUST construct and display breadcrumbs by looking up the `node_id` in the `callConfig` fetched from the BFF.
- FR4 (US1): The frontend MUST NOT submit a structural container ID; it MUST only submit the evaluable child node's ID.

## 5. Data & API Contracts
- No backend endpoint changes required. (US1)
- The frontend relies on `parent_node_id` (on the node instance) and `parent_logical_id` (from call definition metadata) provided by existing BFF payloads. (US1, FR1)

## 6. Components / Modules
- `frontend/src/lib/submit/renderModel.ts`: Updated to support `isContainer` detection and synthetic ancestor group labels.
- `frontend/src/components/submit/UniversalSubmitForm.tsx`: Updated to render 1-level grouped items.
- `frontend/src/components/review/ReviewCard.tsx` (or equivalent context wrapper): Updated to build and show the ancestor breadcrumb dynamically. (Note: `callConfig` will be accessed via existing React context rather than prop drilling).

## 7. Edge Cases
- Missing `parent_logical_id` (US1): Uncategorized fallback.
- User accidentally clicks a structural container header (US1): Ensure grouping headers are not selectable for submission; only evaluable leaves are selectable.

## 8. Testing Decisions (TDD)
- Unit test in `renderModel.ts` for flat-to-grouped parsing logic.
- React Testing Library integration test for `UniversalSubmitForm.tsx` to verify the exact `node_id` submitted matches the leaf node, preventing the regression of submitting a parent container's ID.
- Unit/integration test for the breadcrumb construction in `ReviewCard.tsx` (or its equivalent container) to ensure `node_id` correctly resolves to its ancestor path using provided context.

## 9. Telemetry (Minimal)
- No new telemetry strictly required for MVP.

## 10. Deferred / Not in MVP
- Deep recursive styling and multi-node chunk submissions.

## 11. Open Questions (if any)
- None.

## 12. Changelog
- v0.1 (2026-03-10): Initial PRD from brainstorm
- v0.2 (2026-03-10): Applied risk audit edits (added breadcrumb test and clarified context usage for callConfig)
