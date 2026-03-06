# Phase 2.2 — Tasks Review (No Edits)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-2-2-task-review.md.
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

Phase 2.2 produces review output in chat only (no file edits). If you made no file changes, there is nothing to commit for this phase.

---

## Output (in chat only)

1. Use review range `main...HEAD` by default (unless the user explicitly requests a narrower range).
2. Execute `@docs/workflow/util-adversarial-diff-audit.md` with profile `planning`.
3. Fail-closed rule: do not consider this gate complete unless output includes all five required sections and explicit coverage of the six mandatory focus areas.
4. Keep task-specific rigor: include exact task-file edit guidance where findings exist, and enforce sequential, atomic execution constraints.
5. `Parallelizable` remains planning metadata only; do NOT recommend parallel task execution for Phase 3.
6. Do NOT edit files.
