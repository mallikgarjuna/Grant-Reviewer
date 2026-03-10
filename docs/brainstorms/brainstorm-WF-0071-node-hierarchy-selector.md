# WF-0071 — Node Hierarchy Selector

Artifact: brainstorm
Version: v0.0
Status: Not started
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
