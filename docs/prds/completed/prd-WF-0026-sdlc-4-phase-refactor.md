# PRD: WF-0026 — SDLC 4-Phase Refactor

**Version:** v0.1
**Last Updated:** 2026-02-21
**Status:** Draft — Ready for Review

---

## 1. Problem Statement

The current workflow system has **5 phases** before code ships:

```
Phase 0 (Brainstorm) → Phase 1 (Spec) → Phase 2 (PRD) → Phase 3 (Tasks) → Phase 4 (Implement)
```

Phase 1 (Spec) and Phase 2 (PRD) are **redundant translation layers**. A Spec defines the "How" and a PRD defines the "What" — but with a long-context LLM, both belong in a single unified document. The current system forces the agent to rewrite the same information in two different templates, wasting tokens, time, and creating translation errors.

## 2. Goal

Compress the pipeline into a **4-phase SDLC**:

```
Phase 0 (Ideation) → Phase 1 (Definition) → Phase 2 (Planning) → Phase 3 (Execution)
```

- Eliminate the standalone Spec phase entirely.
- Merge the "What" and "How" into the PRD artifact (Phase 1 = Definition).
- Preserve all existing artifact filename prefixes (`brainstorm`, `prd`, `task`, `walkthrough`).
- Introduce the human-readable stage vocabulary (Ideation, Definition, Planning, Execution) in runner filenames and documentation.

## 3. SDLC Stage ↔ Artifact Mapping

| Stage | Phase | Runner Filename | Input Artifact | Output Artifact |
|---|---|---|---|---|
| Ideation | 0 | `phase-0-run-start-and-brainstorm-ideation.md` | User idea | `brainstorm-WF-XXXX-<slug>.md` |
| Definition | 1 | `phase-1-run-prd-definition.md` | `brainstorm-WF-XXXX-<slug>.md` | `prd-WF-XXXX-<slug>.md` |
| Planning | 2 | `phase-2-run-tasks-planning.md` | `prd-WF-XXXX-<slug>.md` | `task-WF-XXXX-<slug>.md` |
| Execution | 3 | `phase-3-run-implement-execution.md` | `task-WF-XXXX-<slug>.md` | Code + `walkthrough-WF-XXXX-<slug>.md` |

## 4. File Operations

### 4.1 Renames (git mv)

| Old Path | New Path |
|---|---|
| `phase-0-run-start-and-brainstorm.md` | `phase-0-run-start-and-brainstorm-ideation.md` |
| `phase-0-0-start-workflow.md` | *(no change — sub-phase file)* |
| `phase-0-1-brainstorm.md` | *(no change — sub-phase file)* |
| `phase-2-1-prd-generate.md` | `phase-1-1-prd-generate.md` |
| `phase-2-2-prd-risk-audit.md` | `phase-1-2-prd-risk-audit.md` |
| `phase-2-3-prd-revise.md` | `phase-1-3-prd-revise.md` |
| `phase-3-1-task-generate.md` | `phase-2-1-task-generate.md` |
| `phase-3-2-task-review.md` | `phase-2-2-task-review.md` |
| `phase-3-3-task-revise.md` | `phase-2-3-task-revise.md` |
| `phase-4-run-implement.md` | `phase-3-run-implement-execution.md` |
| `phase-4-1-implement-tasks.md` | `phase-3-1-implement-tasks.md` |
| `phase-4-2-verify-and-ship.md` | `phase-3-2-verify-and-ship.md` |
| `phase-123-run-planning.md` | `phase-12-run-planning.md` |

### 4.2 Deletes

| File | Reason |
|---|---|
| `phase-1-1-spec-generate.md` | Spec phase eliminated |
| `phase-1-2-spec-review.md` | Spec phase eliminated |
| `phase-1-3-spec-revise.md` | Spec phase eliminated |

*(Note: `phase-1-run-spec.md` does not exist on disk — it was previously deleted.)*

### 4.3 No Change

| File | Reason |
|---|---|
| `call-yaml-authoring-workflow.md` | Unrelated to SDLC phases |
| `phase-0-0-start-workflow.md` | Sub-phase; no number change needed |
| `phase-0-1-brainstorm.md` | Sub-phase; no number change needed |

## 5. Content Updates (Cross-References)

Every file that contains a hardcoded reference to old phase numbers or old filenames must be updated. The affected files are:

| File | What to Update |
|---|---|
| `phase-0-run-start-and-brainstorm-ideation.md` | Line 86: change `phase-1-run-spec.md` → `phase-1-run-prd-definition.md` |
| `phase-12-run-planning.md` (was `phase-123-run-planning.md`) | Remove the entire Phase 1/Spec row from the routing matrix. Renumber Phase 2→1 and Phase 3→2. Update all inner-loop file references. |
| `run-lifecycle-auto.md` | Rewrite execution flow: remove Phase 1 (Spec) step, renumber all references, update runner filenames |
| `run-lifecycle-interactive.md` | Same as above |
| `how-to-use-workflow-actions.md` | Update all prompt templates with new runner filenames and phase numbers |
| `README.md` | Update phase list, runner shortcuts, status values, artifact hierarchy |
| `AGENTS.md` (project root) | Update WF Workflow section with new phase names, runner references, status vocabulary |

## 6. docs/index.md Registry Changes

### 6.1 Column Change
The `Spec` column becomes permanently `-` for all future WFs. Existing completed WFs (WF-0009 through WF-0025) retain their Spec links as historical artifacts. No retroactive changes.

### 6.2 Status Vocabulary
Old: `Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Done`
New: `Phase 0 | Phase 1 | Phase 2 | Phase 3 | Done`

## 7. docs/specs/ Directory

- **Not deleted.** It contains completed artifacts from WF-0009 through WF-0025.
- Add a `docs/specs/DEPRECATED.md` file explaining the Spec phase was merged into the unified PRD as of WF-0026.
- No new files will be created here going forward.

## 8. Acceptance Criteria

1. All 13 `git mv` operations succeed cleanly.
2. All 3 deprecated spec files are deleted.
3. `rg "phase-1-run-spec"` returns zero results across the entire repo.
4. `rg "phase-2-run-prd"` returns zero results (replaced by `phase-1-run-prd-definition`).
5. `rg "phase-3-run-task"` returns zero results (replaced by `phase-2-run-tasks-planning`).
6. `rg "phase-4-run-implement"` returns zero results (replaced by `phase-3-run-implement-execution`).
7. `rg "Phase 4"` returns zero results in workflow instruction files (replaced by `Phase 3`).
8. `pre-commit run --all-files` passes.
9. The `how-to-use-workflow-actions.md` cheat sheet contains valid, copy-pasteable prompts that reference only the new filenames.

---

## Changelog

- v0.1 (2026-02-21): Initial draft.
