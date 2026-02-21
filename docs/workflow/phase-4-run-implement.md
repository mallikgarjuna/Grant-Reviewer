# Phase 4 — Implement Tasks

This file is a workflow instruction.
Reference it in chat (Codex or Antigravity or any coding agent) using @docs/workflow/phase-4-run-implement.md.
Do NOT modify this file during execution.

---

## Purpose
To execute the granular development tasks defined in Phase 3, rigorously verify the implementation, and synthesize the results into a walkthrough document.

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

---

### PART A: Execute (The Loop)
1. Read the execution rules in `docs/workflow/phase-4-1-implement-tasks.md`.
2. Following those rules exactly, loop through every task in the provided task file.
3. Implement each task and commit sequentially as instructed in that file.
4. Check off (`[x]`) tasks in the task artifact as you go.
5. Do not proceed to Part B until all tasks are implemented.

### PART B: Verify [GATE]
1. Stop implementing features.
2. Run `pre-commit run --all-files` (or the equivalent linter/formatter).
3. Run the project's test suite (if applicable) and explicitly print the results.
4. If the work touched UI/Frontend, ask the user if they wish to perform a manual visual validation or if you should use an Agentic Browser to verify the UI.
5. If any verification fails, drop back to Part A to implement the fix, then return to Part B.
6. Await explicit user approval ("go ahead", "LGTM") before proceeding to Part C.

### PART C: Walkthrough + Ship [GATE]
1. Read the artifact file: `docs/walkthroughs/walkthrough-<WF-ID>-<slug>.md`.
2. Follow the template and instructions inside that file (or create it using a standard format if it's empty).
3. Draft the walkthrough summarizing what was changed, what was verified, and the next steps.
4. Execute `git mv` via terminal to move the 5 active artifacts (Brainstorm, Spec, PRD, Tasks, Walkthrough) for this `<WF-ID>` into their respective `completed/` subdirectories.
5. Update `docs/index.md`:
   - Change the `Status` column for this WF to `Done`.
   - Update the markdown links in this WF's row to point to the new `completed/` paths.
6. Run a final `git add` and `git commit` for the walkthrough, the file moves, and the index update.

---

## Next Actions
After completing Phase 4 (including Part C revisions and commits), suggest the following next actions to the user:

1. \`ship it\` (See `AGENTS.md` for PR/Merge definition).
2. Start a new workflow / idea.

---

## How to Invoke in Chat

Use:

```text
Use @docs/workflow/phase-4-run-implement.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Run Phase 4 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```
