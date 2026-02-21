# WF-0022 — Workflow System Upgrade

Artifact: prd
Version: v1.0
Status: Ready for Tasks
Last Updated: 2026-02-21

## 1. Context & Purpose
The workflow system has proven successful but is currently creating cognitive overload and maintenance debt via file sprawl (21 files) and duplication. We are upgrading the system to enforce safety gates in Phase 4 and reduce the runner footprint for agents.

## 2. Acceptance Criteria (AC)
- **AC1**: All numbering errors and typos in `docs/workflow/` are fixed.
- **AC2**: `how-to-use-workflow-actions.md` contains only the Phase 0, 1, 2, 3, 4 runner invocations and lifecycle invocations (no sub-phase invocations).
- **AC3**: `phase-4-run-implement.md` exists and enforces Part A (implement), Part B (verify), Part C (walkthrough + ship).
- **AC4**: Both `run-lifecycle-auto.md` and `run-lifecycle-interactive.md` instruct the agent to stop and advise the user to start a new chat if context gets too long, and explicitly enforce Part A/B/C logic per phase.
- **AC5**: `workflow preflight` and `verify workflow` are defined in `docs/workflow/README.md`.
- **AC6**: Phase 1, Phase 2, and Phase 3 runners are consolidated into a single `universal-phase-runner.md` that leverages variables for input/output targets.
- **AC7**: Archival strategy is documented in `README.md`.

## 3. Scope Boundaries
- **In Scope**: Editing files within `docs/workflow/`, `AGENTS.md`, and `docs/index.md`.
- **Out of Scope**: Archiving the existing 13 WFs is deferred; we only define the *convention* here. Changing the fundamental 0-4 phase structure is out of scope.

## 4. Technical Approach / Risks
- **Risk**: The `universal-phase-runner.md` relies on the agent correctly substituting variables (e.g., `<Phase>`, `<Input Artifact>`). If the agent fails to substitute correctly, it may generate a PRD when it should be generating a Spec.
- **Mitigation**: We will construct the `universal-phase-runner.md` with explicit, idiot-proof conditional logic tables so any LLM can easily map the Phase number to the correct input/output files.

## Traceability Statement
- Derived directly from `spec-WF-0022-workflow-system-upgrade.md` v1.0.
