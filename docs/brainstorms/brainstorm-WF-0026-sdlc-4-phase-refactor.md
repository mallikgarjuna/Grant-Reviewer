# Brainstorm: WF-0026 (SDLC 4-Phase Refactor)

**Goal:** Convert the current 5-phase heavy workflow (Brainstorm → Spec → PRD → Tasks → Implement) into a leaner, industry-standard 4-phase SDLC (Ideation → Definition → Planning → Execution).

**Why:** The current "Spec" phase is redundant. A PRD and a Technical Spec should be unified when using long-context LLMs.

**Requested Nomenclature Changes:**
- `phase-0-run-start-and-brainstorm.md` -> `phase-0-run-start-and-brainstorm-ideation.md`
- `phase-1-run-spec.md` -> DELETED
- `phase-2-run-prd.md` -> `phase-1-run-prd-definition.md`
- `phase-3-run-tasks.md` -> `phase-2-run-tasks-planning.md`
- `phase-4-run-implement.md` -> `phase-3-run-implement-execution.md`

We keep the standard artifact file conventions (`brainstorm`, `prd`, `task`, `walkthrough`) but elevate the stage names in the runner scripts and documentation.
