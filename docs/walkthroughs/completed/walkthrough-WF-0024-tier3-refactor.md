# Walkthrough: WF-0024 — Tier 3 Phase 1-3 Runner Refactor

Date: 2026-02-21

## 1. Goal
Execute the final piece of the Workflow System Upgrade (Tier 3) by coalescing the highly redundant Phase 1, Phase 2, and Phase 3 runners into a single, parametric Phase 1-3 flow orchestrator, then surgically deleting the legacy runners.

## 2. Changes Made
- **Created `docs/workflow/phase-123-run-planning.md`**: Implemented a unified runner that accepts a `Phase ID` parameter. It maps that parameter to a dedicated Input/Output matrix to correctly route to the precise Generate, Review, and Revise sub-instructions without any duplication of the Part A/B/C gating logic itself.
- **Updated `how-to-use-workflow-actions.md`**: Consolidated the three separate "End-to-End" planning phase blocks into one `Phase 1/2/3 — Run Planning` template block.
- **Updated `run-lifecycle-auto.md` and `run-lifecycle-interactive.md`**: Updated their Steps 3, 4, and 5 to route through the new `phase-123-run-planning.md` file.
- **Excised Legacy Runners**: Deleted `phase-1-run-spec.md`, `phase-2-run-prd.md`, and `phase-3-run-task.md` from the repo completely.
- **Updated `README.md`**: Updated the shortcut map pointing to the new runner path.

## 3. Verification Performed
- **Automated Formatting Checks**: Formatted using `pre-commit run --all-files`.
- **Dangling Reference Check**: Ran `git grep "phase-[123]-run-"` globally in the project. Verified that the only remaining references point gracefully to historical records (like `qa_history.md` or `decisions.md`) or the specific PRD planning text for this exact refactor. No operational logic files map to the deleted files.
- **Artifact Traceability**: Verified index linking is intact, all files share the `WF-0024` ID prefix, and WF status was successfully marked `Done`.

## 4. Next Steps
- Run `wrap up` and `ship it` to merge the Tier 3 refactor to main.
- With Tier 1, Tier 2, and Tier 3 all complete, the Workflow System Upgrade is entirely finished.
- Proceed to the next feature task or park the item.
