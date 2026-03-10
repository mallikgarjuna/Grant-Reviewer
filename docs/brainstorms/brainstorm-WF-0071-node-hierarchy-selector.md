# WF-0071 — Node Hierarchy Selector

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-10
## Repo Reality Snapshot (Read-Only)
*2026-03-10*

- Backend `CallDefinitionV2` and `ProposalNodeDefinitionV2` already contain a `parent_logical_id` field enabling a flat but hierarchical structure.
- The BFF / frontend actively rejects nested nodes: `renderModel.ts` throws `"nested_nodes"` and blocks rendering if any node has a `parent_node_id !== null` (unless they are structural containers).
- The `UniversalSubmitForm` shows an unsupported message: "This call uses nested sections and is not yet supported in this form."
- ERC and MSCA demo calls are the primary active workflows triggering these nested/hierarchical states in tests.
- We recently added `structuralContainerNodeLogicalIds` mapping and role definitions to `renderModel.ts` in WF-0063/64 but we need proper UX to traverse non-container nested parts natively.

**Open Questions:**
1. Do we want a flat list with indentation, an accordion, or a drill-down wizard UX for nested nodes?
2. Are evaluable nodes ever nested *inside* other evaluable nodes (e.g. MSCA B1 inside B2?), or just inside structural containers?
3. If a node is nested, do we submit it as a single chunk, or does the nested structure dictate multi-chunk submission boundaries?

## Desired Outcome
- **Success Metric:** A researcher can load MSCA or ERC in the `UniversalSubmitForm`, see the hierarchical grouping without errors, and select "Part B1 / Section a" to review.
- **MVP Threshold:** We only need read-only visual grouping for parents, and full submittability for their children.

## Target User / Actor
- **Target:** Researchers applying to complex nested grants (ERC, MSCA).

## Flow & Architecture Exploration
- **Implementation Direction:** Transform `NodeSummary[]` in `frontend/src/lib/submit/renderModel.ts` to build out the `groups` and `nodes` arrays specifically to support an `isContainer` check and a visual indent/grouping pass in `UniversalSubmitForm.tsx`.
  - *Contract Note:* `renderModel.ts/buildRenderModel` will maintain a flat `RenderGroup[]` (or flat `nodes` array), but synthesize the ancestor path (e.g., 'Part B1 / Section a') for labels or grouping keys, ensuring the UI does not need a complex recursive accordion component.
- **Constraint:** Do not change the backend definition; rely strictly on `parent_logical_id` to build the tree on the frontend.

## Risks / Unknowns
- **Fragile Assumption:** That all `parent_logical_id` values resolve successfully in the payload. Mitigation: Filter out orphans gracefully or attach them to a fallback generic "Uncategorized" group.
- **Regression Risk:** UI submitting a parent container's ID instead of the child's. Mitigation: Add an explicit React Testing Library integration test to verify the exact `node_id` submitted matches the leaf node.

## MVP Definition
- **Must Have:** Nested node parsing in `renderModel.ts`, UI grouping in `UniversalSubmitForm.tsx`, and breadcrumb updates in `ReviewCard.tsx` (or equivalent context display).
  - *Note:* To avoid backend changes, `ReviewCard.tsx` (or its parent wrapper) must construct the breadcrumb by looking up the `node_id` in the `callConfig` (or similar frontend state) fetched from the BFF, rather than expecting the BFF review payload to inherently contain the ancestor string.
- **Must NOT Have:** N-deep recursive accordion components. 1-level flat grouping with indentation is sufficient for MVP.

## Explicit Non-Goals
- Expanding the backend database schema to hold native tree arrays (SQL recursion). Flat lists with `parent_logical_id` are fine.
- Multi-node chunk submissions (submitting an entire parent node at once).
