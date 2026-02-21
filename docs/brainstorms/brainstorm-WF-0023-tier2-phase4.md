# WF-0023 — Tier 2 Phase 4 Runner

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-02-21

## 1. Problem Statement
The current WF workflow system is missing a formal "Phase 4 Runner." Existing implementations rely on a loose `phase-4-1-implement-tasks.md` file that specifies sequential commitments but fails to enforce the strict Part A (Execute), Part B (Verify), and Part C (Walkthrough) gating discipline found in Phases 1-3.

Additionally, the lifecycle runners (`run-lifecycle-auto.md`, `run-lifecycle-interactive.md`) are thin and lack explicit context-window resets, causing agents to lose track of the A/B/C phase gates during deep execution.

Finally, "workflow preflight" and "verify workflow" are recognized code phrases in `AGENTS.md` but lack defined procedures.

## 2. Desired Outcome
- Create a strict `docs/workflow/phase-4-run-implement.md`.
- Update lifecycle runners to explicitly reference Part A/B/C for each phase and warn about context exhaustion.
- Document the `workflow preflight` and `verify workflow` checklist stubs in `docs/workflow/README.md`.

## 3. Target User / Actor
- AI Coding Agents (Antigravity, Codex) executing implementation tasks.
- Project Maintainer overseeing the implementation phase.

## 4. MVP Definition & Rough Idea
This is explicitly scoped as the "Tier 2 (Risk Mitigation)" step of the Workflow System Upgrade previously approved. It includes:
- Writing the Phase 4 runner instructions.
- Adding safety warnings to lifecycles.
- Documenting two missing code phrases.

## 5. Constraints & Non-Goals
- **Non-Goal**: We will not refactor Phases 1-3 (that is reserved for WF-0024 Tier 3).
- **Constraint**: The Phase 4 runner must map cleanly to the existing prompt stored in `how-to-use-workflow-actions.md`.

## Traceability Statement
- Derived from the explicit user directive to split the workflow upgrade and focus WF-0023 entirely on Tier 2: The Risk Mitigation (Phase 4 Runner creation).
