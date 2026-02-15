# Phase 4.1 — Implement Tasks (Sequential + Commit Per Task)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-4-1-implement-tasks.md.
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

Before starting Phase 4 implementation, ensure Phase 3 outputs are **saved and committed** on the WF branch:

- `docs/tasks/task-WF-XXXX-<slug>.md` is committed and marked Ready for Implementation
- `docs/index.md` Phase 3 status/links are committed if updated

---

## Phase Completion — Commit This Phase

After completing Phase 4 (all tasks implemented, walkthrough updated, and `docs/index.md` set to Done), ensure those final docs changes are **saved and committed**.

---

## Branch Rules (Mandatory for New WF)

All Phase 4 work must occur on a WF branch:

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
  - Resume Phase 4

---

## Per-Task Execution Loop

For each task:

1. Check available skills with `ls ~/.agents/skills` or `docs/reference/skills_index.md`. If a relevant skill exists, read it.
2. Implement the task.
3. Run verification steps listed under the task.
3. Fix until verification passes.
4. Commit using this format:

   WF-XXXX: <slug> — Task <N> — <short title>

5. Optionally mark task complete inside tasks file (checkbox).
   Do NOT bump version unless the task plan itself changed.

Then continue automatically to the next task.

---

## Completion

When all tasks are complete:

1. Update docs/index.md Status to:
   Done

2. Create or update walkthrough file:
   docs/walkthroughs/walkthrough-WF-XXXX-<slug>.md

Walkthrough must include:

- How to run
- How to verify
- Known limitations (if any)

---

## How to Invoke in Codex Chat

Use:

- @docs/workflow/phase-4-1-implement-tasks.md
- @docs/tasks/task-WF-XXXX-<slug>.md

Instruction:

"Execute all tasks sequentially. Commit after each task using the required commit format. Continue automatically until all tasks are complete."

---

## Stop Condition

Stop when all tasks are completed, the walkthrough is drafted/updated, and `docs/index.md` is updated to Status `Done`.

---

## After You Finish (Next 2 Actions)

In your final chat message, suggest the next 2 actions (so I can choose what to do next):

1. Open a PR for the WF branch and merge it to `main` (then update local `main`).
2. Start the next workflow (Phase 0.0) for the next idea/feature.
