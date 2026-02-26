# Phase 3.2 — Verify & Ship (Post-Implementation)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-3-2-verify-and-ship.md.
Do NOT modify this file during execution.

---

## Purpose
To cleanly resume a workflow that has already completed Part A (Implementation) in a prior session. This runner explicitly skips task implementation and jumps straight into Review + Verification and Walkthrough generation.

## Inputs Required
1. A completed Tasks artifact representing the current WF scope (e.g., `docs/tasks/task-<WF-ID>-<slug>.md`) where ALL tasks are marked as `[x]`.

## Phase Gate & Completion
- **START**: Implementation tasks are done.
- **FINISH**: Walkthrough document is drafted/updated, index is updated, and the user is prompted for the push signal.

## Runner Rules

1. **Runners are Routers**: You **MUST** execute Part B, then Part C in strict order.
2. Note that there is no Part A (Execute) in this instruction, because the implementation is already complete.
3. Print a short "PART B/C" header and a bullet summary of actions taken at the end of each part.
4. If Part B identifies regressions or test failures, you must fix them before proceeding to Part C.
5. If fixes require behavior changes, TDD is mandatory (red/green/refactor; mock boundaries only): `docs/guides/tdd/README.md`.
6. This file is the canonical source for Phase 3 Part B and Part C gate behavior. The end-to-end runner (`phase-3-run-implement-execution.md`) must reference this file for those gates.

---

### PART B: Technical Audit + Verify [GATE]
1. Stop feature work and perform a detailed **technical audit (code review) of Part A only**.
2. Output the audit in this exact structure:
   1. potential bugs
   2. missing tests
   3. design issues
   4. suggested fixes
   5. refactored version with comments (only for high-impact snippets; keep minimal and actionable)
3. Keep Part B review scope exclusive to technical audit concerns; do not add product-scope brainstorming or non-technical critique.
4. If audit finds issues, implement fixes, then restart Part B from step 1.
5. Run `pre-commit run --all-files` (or equivalent lint/format checks).
6. Run the project's relevant automated test suite and explicitly print pass/fail evidence.
7. If work touched UI/Frontend, ask the user whether to do manual visual validation or agentic browser validation.
8. For each bug found during Part B, add/update a failing reproducer test before fixing; re-run verification.
9. If any verification fails, implement fixes and return to Part B step 1.
10. Await explicit user approval ("go ahead", "LGTM") before proceeding to Part C.

### PART C: Walkthrough + Ship [GATE]
1. Read the artifact file: `docs/walkthroughs/walkthrough-<WF-ID>-<slug>.md`.
2. Follow the template and instructions inside that file (or create it using a standard format if it's empty).
3. Draft the walkthrough summarizing what was changed, what was verified, and the next steps.
4. Execute `git mv` via terminal to move the active artifacts (Brainstorm, PRD, Tasks, Walkthrough) for this `<WF-ID>` into their respective `completed/` subdirectories.
5. Update `docs/index.md`:
   - Change the `Status` column for this WF to `Done`.
   - Update the markdown links in this WF's row to point to the new `completed/` paths.
6. Run a final `git add` and `git commit` for the walkthrough, the file moves, and the index update.
7. **STOP**: You must strictly await explicit user approval ("Ship it") before autonomously executing `git push`, opening a PR, or merging. Do not push to remote without a direct command.

---

## Next Actions
After completing Phase 3.2 (including Part C revisions and commits), suggest the following next actions to the user:

1. `ship it` (See `AGENTS.md` for PR/Merge definition).
2. Start a new workflow / idea.

---

## How to Invoke in Chat

Use:

```text
Use @docs/workflow/phase-3-2-verify-and-ship.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Assume implementation tasks are DONE.
Run Phase 3.2 (Verify & Ship) for <WF-ID>/<slug> using this runner.
Print what you did in Part B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```
