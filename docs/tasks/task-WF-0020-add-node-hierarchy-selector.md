# WF-0020 — Add node hierarchy selector

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-02-18

## Task Breakdown (Sequential Order)

### Task 1 — Audit current node selector surface and hierarchy inputs

Goal:
- Confirm the exact in-scope selector surface and verify available node hierarchy metadata from existing payloads.

Files to modify:
- `frontend/src/app/app/page.tsx`
- `frontend/src/lib/bff/types.ts` (read/adjust typing only if needed)

Acceptance Criteria:
- In-scope selector surface is explicitly confirmed as `/app` submit flow.
- Node payload fields used for parent/child grouping are documented.
- Fallback criteria for incomplete metadata are documented before implementation.
- No production behavior changes are introduced in this audit step.

Verification Steps:
- Inspect `/app` selector implementation and node payload shape.
- `cd frontend && npm run lint`

Risks (if any):
- Assuming hierarchy fields incorrectly can cause broken grouping logic.

### Task 2 — Implement parent-first selector state and grouping adapter

Goal:
- Add parent-first selection flow and deterministic grouping/fallback transformation based on existing node payload.

Files to modify:
- `frontend/src/app/app/page.tsx`
- `frontend/src/lib/**` grouping helper(s) (if extracted)
- optional shared selector UI file under `frontend/src/components/**`

Acceptance Criteria:
- Parent must be selected before child options become active.
- Child options only show nodes valid for selected parent.
- Nodes with missing parent metadata are placed under `Other Sections`.
- Existing submission payload still sends valid `node_id` mapped to selected child node.

Verification Steps:
- Manual scenario checks for parent selection, child filtering, and fallback bucket behavior.
- `cd frontend && npm run lint`

Risks (if any):
- State-reset bugs when parent changes after child selection.

### Task 3 — Add label disambiguation and stable ordering

Goal:
- Ensure duplicated/ambiguous child labels are distinguishable and node ordering remains predictable.

Files to modify:
- `frontend/src/app/app/page.tsx`
- grouping/helper files created in Task 2 (if applicable)

Acceptance Criteria:
- Ambiguous child labels include enough parent context to avoid confusion.
- Ordering is deterministic within each parent grouping.
- Existing submit form behavior remains unchanged outside selector UX.

Verification Steps:
- Manual checks with representative calls containing similar child titles.
- `cd frontend && npm run lint`

Risks (if any):
- Over-formatting labels can reduce readability if not concise.

### Task 4 — Validate end-to-end behavior and capture walkthrough

Goal:
- Verify PRD scenarios and document reproducible verification notes.

Files to modify:
- `docs/walkthroughs/walkthrough-WF-0020-add-node-hierarchy-selector.md`
- `docs/tasks/task-WF-0020-add-node-hierarchy-selector.md` (progress updates)

Acceptance Criteria:
- Manual checks cover parent-first flow, parent switch reset, ambiguous label clarity, and fallback bucket usability.
- Walkthrough captures run/verify steps and known limitations.
- Lint/pre-commit checks pass for changed files.

Verification Steps:
- `cd frontend && npm run lint`
- `pre-commit run --all-files`

Risks (if any):
- Incomplete manual coverage may miss edge regressions.

## Changelog

- v0.1 (2026-02-18): Initial task breakdown from PRD
- v0.2 (2026-02-18): Tightened sequencing, added node_id integration acceptance criterion, and marked Ready for Implementation

## Implementation Progress

- [x] Task 1 — Audit current node selector surface and hierarchy inputs
  - Confirmed in-scope selector surface: `frontend/src/app/app/page.tsx` (`Proposal Section` field in `/app` submit flow).
  - Confirmed hierarchy/grouping inputs from `NodeSummary`: `parent_node_id`, `title`, `order_index`, `has_expectations` (`frontend/src/lib/bff/types.ts`).
  - Confirmed fallback criteria for implementation: when a node has missing/non-resolvable `parent_node_id`, place it in deterministic `Other Sections` bucket while preserving valid child `node_id` submission.
- [x] Task 2 — Implement parent-first selector state and grouping adapter
  - Added hierarchy adapter at `frontend/src/lib/node-hierarchy.ts` with deterministic parent buckets and fallback `Other Sections`.
  - Updated `/app` submit flow to use parent-first selection, child filtering by selected parent, and unchanged submission payload mapping to selected child `node_id`.
