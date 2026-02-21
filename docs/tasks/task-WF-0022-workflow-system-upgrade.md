# WF-0022 — Workflow System Upgrade

Artifact: task
Version: v1.0
Status: Ready for Implementation
Last Updated: 2026-02-21

## 1. Context
Execute the 3-tier upgrade for the `docs/workflow/` system as defined in the PRD.

## 2. Tasks

### [x] Task 1.0: Tier 1 (Quick Wins & Cheat Sheet)
*Note: This task will be executed on the current branch `wf/WF-0022-workflow-system-upgrade` and merged as PR #1.*
- [x] Fix formatting/numbering gaps in `phase-1-run-spec.md`, `phase-2-run-prd.md`, `phase-3-run-task.md`.
- [x] Fix typos ("Oversignt", "recommmended") in `run-lifecycle-interactive.md`.
- [x] Standardize terminology to "Codex or Antigravity or any coding agent" across `phase-4-1-implement-tasks.md`.
- [x] Delete duplicate line 139 in `AGENTS.md`.
- [x] Truncate `how-to-use-workflow-actions.md` to remove individual sub-phase prompts, keeping only the full phase runners and lifecycle runners.
- **Verify**: `git diff` shows only markdown cleanup. No broken links.

## Traceability Statement
- Derived directly from `prd-WF-0022-workflow-system-upgrade.md` v1.0.
