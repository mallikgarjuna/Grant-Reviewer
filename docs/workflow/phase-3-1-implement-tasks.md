# Phase 3.1 — Implement Tasks (Sequential + Commit Per Task)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-3-1-implement-tasks.md.
Do NOT modify this file during execution.

---

## Purpose

Execute all tasks in the tasks file sequentially.
After each task:

- verify
- commit
- continue to the next task

This produces clean, traceable progress and stable checkpoints.

---

## Required Inputs

- docs/tasks/task-WF-XXXX-<slug>.md

Tasks file must have:
Status: Ready for Implementation

---

## Phase Gate — Commit Previous Phase

Before starting Phase 3 implementation, ensure Phase 2 outputs are **saved and committed** on the WF branch:

- `docs/tasks/task-WF-XXXX-<slug>.md` is committed and marked Ready for Implementation
- `docs/index.md` Phase 3 status/links are committed if updated

---

## Phase Return — Stop Processing Here
When all tasks are implemented, STOP execution.
Do NOT create the walkthrough here.
Return control to the `phase-3-run-implement-execution.md` Part B Verification gate.

---

## Branch Rules (Mandatory for New WF)

All Phase 3 work must occur on a WF branch:

wf/WF-XXXX-<slug>

If branch does not exist:

- create it
- ensure index + artifacts are committed
- continue implementation on this branch

---

## Execution Rules (Strict)

- Implement tasks in defined order.
- Only work on ONE task at a time.
- Do NOT expand scope beyond tasks file.
- If missing requirements are discovered:
  - STOP execution
  - Step back ONE phase (usually Phase 2 or 3)
  - Update artifact
  - Bump version
  - Resume Phase 3

---

## Per-Task Execution Loop

For each task:

1. Check available skills (`ls ~/.agents/skills` or `docs/reference/skills_index.md`).
   - If a relevant skill exists, **read it**.
   - If NO skill exists for a **complex** task (e.g., new DB, new API, complex refactor), **ask the user** if they want to create a skill first or proceed.
   - If task changes behavior or is a bug fix: TDD is mandatory. Follow `docs/guides/tdd/README.md` (red/green/refactor; mock boundaries only).
   - If TDD is not feasible for a task, STOP and ask the user for an explicit exception + alternative verification evidence.
2. Implement the task.
3. Run verification steps listed under the task.
4. Fix until verification passes.
5. After coding and verification, explicitly report:
   - what could break from this task's changes
   - targeted tests to add/run for that breakage risk
6. If the task is a behavior change or a bug fix, first add/update a failing test that proves the acceptance criteria, then implement until it passes.
   - Do NOT do horizontal slicing (all tests first, all code later). Do `RED->GREEN` per increment.
7. Commit using this format:

   WF-XXXX: <slug> — Task <N> — <short title>

8. Optionally mark task complete inside tasks file (checkbox).
   Do NOT bump version unless the task plan itself changed.

Then continue automatically to the next task.

## Completion Return

When all tasks are complete, **STOP**.

Do not update `docs/index.md` or create a walkthrough here. Your job is done. The primary `phase-3-run-implement-execution.md` orchestrator will now take over to enforce Part B (Verify) and Part C (Walkthrough + Ship).

---

## How to Invoke implicitly

This instructions file is implicitly invoked by `phase-3-run-implement-execution.md` Part A. You do not need a direct prompt cheat-sheet for this file, as it should no longer be run locally or standalone.
