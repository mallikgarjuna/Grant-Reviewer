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

## 3. Scope Boundaries
- **In Scope**: Editing files within `docs/workflow/`, `AGENTS.md`, and `docs/index.md`.
- **Out of Scope**: Archiving the existing 13 WFs is deferred; we only define the *convention* here. Changing the fundamental 0-4 phase structure is out of scope.

## 4. Technical Approach / Risks
- **Risk**: Deleting sub-phase invocations from the cheat-sheet might confuse users used to running them.
- **Mitigation**: The explicit Phase Runners are widely adopted and easier to use. This strictly enforces the "Runners are Routers" rule.

## Traceability Statement
- Derived directly from `spec-WF-0022-workflow-system-upgrade.md` v1.0.
