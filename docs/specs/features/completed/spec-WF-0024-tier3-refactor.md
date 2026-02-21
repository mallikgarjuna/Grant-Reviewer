# WF-0024 — Tier 3: Phase 1-3 Runner Refactor

Artifact: spec
Version: v1.0
Status: Ready for PRD
Last Updated: 2026-02-21

## 1. Goal
Consolidate the heavily duplicated Phase 1, 2, and 3 runner orchestrators into a single parametric file (`docs/workflow/phase-123-run-planning.md`), drastically reducing context bloat and centralizing the Part A/B/C verification logic for the planning phases.

## 2. User Stories
- **As an AI Coding Agent**, I need to read fewer duplicate workflow lines when setting up context, so I have more token capacity left for analyzing the user's actual codebase.
- **As a Project Maintainer**, I want a single source of truth for the "Planning Phase Gates" (Part A: Generate, Part B: Review, Part C: Revise) so I don't have to keep 3 identical files in sync.

## 3. Functional Requirements
### The Unified Runner (`docs/workflow/phase-123-run-planning.md`)
- **FR1**: Create `docs/workflow/phase-123-run-planning.md`.
- **FR2**: Structure the file to accept a generic `Phase ID` (1, 2, or 3) as input.
- **FR3**: Define a matrix linking the Phase ID to its respective Input (e.g., Phase 1 takes Brainstorm, Phase 2 takes Spec) and Output (Phase 1 generates Spec, etc.).
- **FR4**: Consolidate the Part A (Execution), Part B (Review Gate), and Part C (Revision) instructions into a single universal set of steps.
- **FR5**: Explicitly warn the agent that the underlying execution loops (e.g., `phase-1-1-spec-generate.md`) remain entirely unchanged; this is solely an orchestrator upgrade.

### Archival of Deprecated Runners
- **FR6**: Remove `docs/workflow/phase-1-run-spec.md`.
- **FR7**: Remove `docs/workflow/phase-2-run-prd.md`.
- **FR8**: Remove `docs/workflow/phase-3-run-task.md`.

### Workflow Registry & Cheat Sheet Updates
- **FR9**: Update `docs/workflow/how-to-use-workflow-actions.md` to map the Phase 1, Phase 2, and Phase 3 invocation prompts to the single unified runner file.
- **FR10**: Update the shortcut links at the top of `docs/workflow/README.md` to reflect the new structure.
- **FR11**: Update `run-lifecycle-auto.md` and `run-lifecycle-interactive.md` to reference the unified runner.

## 4. Non-Functional Requirements
- **Simplicity**: The parametric translation (Input X -> Output Y) must be foolproof for an LLM to comprehend at a glance.
- **Tone**: Maintain the strict "Runners are Routers" tone.

## Traceability Statement
- Derived directly from `brainstorm-WF-0024-tier3-refactor.md` v1.0.
