# Phase 3.2 — Tasks Review (No Edits)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-3-2-task-review.md.
Do NOT modify this file during execution.

---

## Purpose

Critically evaluate task breakdown before implementation.

This step MUST NOT modify any files.

---

## Required Input

- docs/tasks/task-WF-XXXX-<slug>.md

---

## Phase Gate — Commit Previous Phase

Before running the task review gate, ensure the task file being reviewed is **saved and committed** (so review feedback maps to a specific task version).

---

## Phase Completion — Commit This Phase

Phase 3.2 produces review output in chat only (no file edits). If you made no file changes, there is nothing to commit for this phase.

---

## Output (in chat only)

Return:

1. Task sequencing issues
2. Missing integration/glue tasks
3. Over-engineering warnings
4. Redundant or mergeable tasks
5. Exact edits required (task number + change)
6. Next 2 actions I should take (choose one)

Max 100 lines.
Be strict about MVP.

Do NOT edit files.
