# Phase 3 — Implement Tasks

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-3-run-implement-execution.md.
Do NOT modify this file during execution.

---

## Purpose
To execute Phase 3 end-to-end: implement tasks, run the technical audit gate, apply review-driven revisions with verification, then finalize walkthrough + ship gate artifacts.

## Inputs Required
1. A completed and approved Tasks artifact representing the current WF scope (e.g., `docs/tasks/task-<WF-ID>-<slug>.md`).

## Phase Gate & Completion
- **START**: Tasks document must be marked "Status: Ready for Implementation".
- **FINISH**: Walkthrough document is drafted/updated, index is updated, and all changes are cleanly committed sequentially.

## Runner Rules

1. **Runners are Routers**: You **MUST** read the detailed instruction file referenced in each "PART" section below. Do not guess.
2. Execute Part A, then Part B, then Part C in strict order.
3. Print a short "PART A/B/C" header and a bullet summary of actions taken at the end of each part.
4. If Part B identifies regressions or test failures, you must fix them before proceeding to Part C.
4.1. Before Task 1 in Part A, run a baseline test command to confirm a green starting state (see `docs/workflow/phase-3-1-implement-tasks.md` “Preflight — First Run the Tests”).
5. For any behavior change or bug fix implemented during Part A, ensure the chat log contains explicit TDD loop labels (`RED`, `GREEN`, `REFACTOR`) as required by `phase-3-1-implement-tasks.md`.
6. TDD is mandatory for behavior changes/bug fixes. Enforce red/green/refactor and boundary-only mocking via `docs/guides/tdd/README.md`.

---

### PART A: Execute (The Loop)
1. Read the execution rules in `docs/workflow/phase-3-1-implement-tasks.md`.
2. Following those rules exactly, loop through every task in the provided task file.
3. Implement each task and commit sequentially as instructed in that file.
4. Check off (`[x]`) tasks in the task artifact as you go.
5. Do not proceed to Part B until all tasks are implemented.

### PART B: Review [GATE]
1. Stop implementing features.
2. Execute Phase 3.2 from `docs/workflow/phase-3-2-verify-and-ship.md` (technical audit review gate, no edits).
3. If the Part B gate requires fixes, drop back to Part A, implement them, then re-run Part B.
4. Await explicit user approval ("go ahead", "LGTM") before proceeding to Part C.

### PART C: Revise + Verify + Walkthrough/Ship [GATE]
1. Execute Phase 3.3 from `docs/workflow/phase-3-3-revise-verify-and-ship.md` exactly (Part C1 revise, Part C2 verify, Part C3 walkthrough + ship gate).

---

## Next Actions
After completing Phase 3 (including Part C revisions and commits), suggest the following next actions to the user:

1. \`ship it\` (See `AGENTS.md` for PR/Merge definition).
2. Start a new workflow / idea.

---

## How to Invoke in Chat

Use:

```text
Use @docs/workflow/phase-3-run-implement-execution.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Run Phase 3 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```
