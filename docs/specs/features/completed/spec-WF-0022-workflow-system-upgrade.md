# WF-0022 — Workflow System Upgrade

Artifact: spec
Version: v1.0
Status: Ready for PRD
Last Updated: 2026-02-21

## 1. Goal
Refactor the Project Workflow System (`docs/workflow/`) to reduce file sprawl, enforce verification in Phase 4, and eliminate documentation maintenance debt, explicitly targeting issues discovered during WF-0009 through WF-0021 execution.

## 2. User Stories
- **As an AI Coding Agent**, I need shorter, non-repetitive instruction files so I don't exhaust my context window and miss critical instructions.

## 3. Functional Requirements
### Tier 1: Quick Wins & Cheat-Sheet Reduction
- **FR1.1**: Fix numbering gaps in existing phase runners (e.g., duplicate `2.` bullets).
- **FR1.2**: Correct typos in `run-lifecycle-interactive.md`.
- **FR1.3**: Standardize agent terminology ("Codex or Antigravity or any coding agent") across all runners.
- **FR1.4**: Remove duplicate line 139 in `AGENTS.md`.
- **FR1.5**: Truncate `how-to-use-workflow-actions.md` to contain *only* phase-runner prompts and lifecycle runners. Delete individual sub-phase prompts to enforce "Runners are Routers".

## 4. Non-Functional Requirements
- **Backward Compatibility**: Existing active branches (`WF-0021`) must remain operational after syncing `main`.
- **Clarity**: All edits must maintain the existing strict, imperative tone.

## Traceability Statement
- Derived from `brainstorm-WF-0022-workflow-system-upgrade.md` v1.0.
