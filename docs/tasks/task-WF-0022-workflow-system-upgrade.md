# WF-0022 — Workflow System Upgrade

Artifact: task
Version: v1.0
Status: Ready for Implementation
Last Updated: 2026-02-21

## 1. Context
Execute the 3-tier upgrade for the `docs/workflow/` system as defined in the PRD.

## 2. Tasks

### [ ] Task 1.0: Tier 1 (Quick Wins & Cheat Sheet)
- [ ] Fix formatting/numbering gaps in `phase-1-run-spec.md`, `phase-2-run-prd.md`, `phase-3-run-task.md` (if they are to be kept momentarily before replacement).
- [ ] Fix typos ("Oversignt", "recommmended") in `run-lifecycle-interactive.md`.
- [ ] Standardize terminology to "Codex or Antigravity or any coding agent" across `phase-4-1-implement-tasks.md`.
- [ ] Delete duplicate line 139 in `AGENTS.md`.
- [ ] Truncate `how-to-use-workflow-actions.md` to remove individual sub-phase prompts, keeping only the full phase runners and lifecycle runners.
- **Verify**: `git diff` shows only markdown cleanup. No broken links.

### [ ] Task 2.0: Tier 2 (Risk Mitigation: Phase 4 & Lifecycles)
- [ ] Create `docs/workflow/phase-4-run-implement.md` enforcing Part A (Implement), Part B (Verify/Integrate), Part C (Walkthrough + Ship).
- [ ] Update `run-lifecycle-auto.md` and `run-lifecycle-interactive.md` to reference explicit A/B/C gates and add context-window warnings.
- [ ] Add `workflow preflight` and `verify workflow` checklist stubs to `docs/workflow/README.md`.
- **Verify**: The new Phase 4 runner reads similarly to Phases 1-3 in its strictness.

### [ ] Task 3.0: Tier 3 (Refactoring & Archival)
- [ ] Create `docs/workflow/universal-phase-runner.md` defining variables for Phase 1, Phase 2, and Phase 3.
- [ ] Delete `phase-1-run-spec.md`, `phase-2-run-prd.md`, `phase-3-run-task.md`.
- [ ] Update `how-to-use-workflow-actions.md`, `README.md`, and lifecycle runners to point to `universal-phase-runner.md`.
- [ ] Add explicit archival instructions to `README.md` (move "Done" artifacts to `docs/archive/WF-XXXX/`).
- **Verify**: All references to old runners are removed. All workflow instructions point to the unified runner.

## Traceability Statement
- Derived directly from `prd-WF-0022-workflow-system-upgrade.md` v1.0.
