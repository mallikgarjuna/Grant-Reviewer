# WF-0071 — Node Hierarchy Selector

Artifact: brainstorm-qna
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-10

**Auto-Piloted Sections (User Approved Default Recommendations)**

**Section 2 — Desired Outcome**
> Recommended: Focus on read-only visual formatting for parents rather than complex accordion state management to hit the MVP faster while ensuring researchers can trace their snippet location.

**Section 3 — Target User / Actor**
> Recommended: Researchers facing MSCA/ERC nested forms specifically.

**Section 4 — Rough Idea Exploration**
> Recommended: UI grouping in `UniversalSubmitForm` derived from an enriched `renderModel.ts` output (e.g., passing ancestor names or group keys) rather than building a heavy recursive TreeComponent.

**Section 5 — Constraints**
> Recommended: Avoid backend `CallDefinitionV2` changes. This is 100% a frontend presentation problem.

**Section 6 — Risks / Unknowns**
> Recommended: The biggest risk is orphan nodes (where `parent_logical_id` points to a missing container). Mitigation is to ensure `renderModel.ts` handles missing parents gracefully by falling back to root-level rendering.

**Section 7 — MVP Definition**
> Recommended: Basic indented grouping mapped from 1 level of `parent_logical_id`.

**Section 8 — Explicit Non-Goals**
> Recommended: No multi-node batch submission in this workflow.
