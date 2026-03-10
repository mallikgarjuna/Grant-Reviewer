<!-- docs/workflow/phase-0-2-audit-findings.md -->

### 1) Scope + Problem Clarity
- **Finding (Non-blocking):** The brainstorm mentions updating the "Review Context breadcrumb in `ReviewCard.tsx`" but does not explicitly state *how* `ReviewCard.tsx` gets this label. If it requires backend API changes to return the full ancestor path in the review payload, that contradicts the "Constraint: Do not change the backend definition" in Section 4.
  *Suggested Edit:* In the MVP Definition, clarify: "If backend changes are avoided, `ReviewCard.tsx` (or its parent wrapper) must construct the breadcrumb by looking up the `node_id` in the `callConfig` dictionary fetched from the BFF, rather than expecting the BFF review payload to inherently contain the ancestor string."

### 2) Contract Safety
- **Finding (Blocking):** The exact contract change for `renderModel.ts` is ambiguous. It says "Transform `NodeSummary[]`... to build out the `groups` and `nodes` arrays". It must be explicitly stated whether we are changing the `RenderModelReady` interface (which currently has a flat `groups: RenderGroup[]` with `nodes: RenderNode[]` inside) to allow nested groups, or just populating the existing flat `RenderGroup` with a concatenated name "Part B1 / Section a".
  *Suggested Edit:* Add a Contract Note to the main brainstorm: "Contract: `renderModel.ts/buildRenderModel` will maintain a flat `RenderGroup[]` output, but use the ancestor path (e.g., 'Part B1 / Section a') as the `groupLabel` so the UI does not need a recursive component."

### 3) Shared-Core Boundary Quality
- *No issues. The boundary is strictly contained within the frontend presentation layer.*

### 4) Migration Strategy Soundness
- *No issues. The plan gracefully degrades for flat calls.*

### 5) Testing Seams + Regression Prevention
- **Finding (Blocking):** The brainstorm mentions testing but lacks explicit parity assertions for the nested submission. If a user selects "Part B1 / Section a", the payload to the backend must submit the node ID for "Section a", NOT "Part B1". This is a critical risk since parent nodes are not submittable.
  *Suggested Edit:* Add to Risks/Unknowns: "Risk: UI submitting a parent container's ID instead of the child's. Mitigation: Add an explicit React Testing Library test to `UniversalSubmitForm.test.tsx` asserting the exact `node_id` submitted matches the child leaf."
