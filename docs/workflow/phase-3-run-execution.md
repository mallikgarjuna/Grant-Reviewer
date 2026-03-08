<!-- docs/workflow/phase-3-run-execution.md -->
# Workflow Runner — Phase 3 (Execution)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-3-run-execution.md.
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
4. If Part B identifies blocking technical findings, you must address them in Part C (Phase 3.3) before ship.
4.1. Before Task 1 in Part A, run a baseline test command to confirm a green starting state (see `docs/workflow/phase-3-1-implement-tasks.md` “Preflight — First Run the Tests”).
5. For any behavior change or bug fix implemented during Part A, ensure the chat log contains explicit TDD loop labels (`RED`, `GREEN`, `REFACTOR`) as required by `phase-3-1-implement-tasks.md`.
6. TDD is mandatory for behavior changes/bug fixes. Enforce red/green/refactor and boundary-only mocking via `docs/guides/tdd/README.md`.
6.1. Part A is allowed to stop before the full task file is complete only when the Phase 3.1 context-bloat/context-drift stop rules are triggered. This is a safety success, not a runner failure.
7. Commit handoff safety between parts:
   - After Part A: ensure task checkboxes, implementation changes, and task-level commits are complete before entering Part B.
   - After Part B: review-only; no file edits and no commit expected.
   - After Part C: if implementation scope is complete, ensure revise/verify/walkthrough/index/archive updates are **saved and committed** before ending the runner.

---

### PART A: Execute (The Loop)
1. Read the execution rules in `docs/workflow/phase-3-1-implement-tasks.md`.
2. Following those rules exactly, process tasks in order until either:
   - all tasks are complete, or
   - a Phase 3.1 context-bloat/context-drift safety stop is hit.
3. Implement each task and commit sequentially as instructed in that file.
4. Check off (`[x]`) tasks in the task artifact as you go.
5. If Part A stopped early, do not proceed to Part B/C as though implementation were complete. Report the stop reason and hand back the next unfinished task.
6. If Part A encountered non-stop continuation risks such as task-plan mismatch, verification instability, file-surface spillover, or planned session-boundary guidance, report them as warnings with a recommendation, but continue in the same chat unless Phase 3.1 escalates them into context-bloat/context-drift risk.
7. If the stop reason is context bloat or context drift, explicitly warn that reasoning quality is at risk, say whether Part B/C is blocked, recommend a fresh chat/session, and print a copy-pasteable resume prompt.
8. Only proceed to Part B when implementation scope is complete for the current approved task plan.

### PART B: Review [GATE]
1. Stop implementing features.
2. Execute Phase 3.2 from `docs/workflow/phase-3-2-technical-audit-review.md` (technical audit review gate, no edits).
3. Part B is fail-closed: do not continue unless review output includes all five required sections from `@docs/workflow/util-adversarial-diff-audit.md` and explicitly covers the six mandatory focus areas.
4. If Part B reports findings, proceed to Part C (Phase 3.3) where Part C1 handles revisions from that review.
5. If findings imply missing/incorrect task scope (not just implementation defects), step back to planning per workflow backtracking rules before continuing.

### PART C: Revise + Verify + Walkthrough/Ship [GATE]
1. Execute Phase 3.3 from `docs/workflow/phase-3-3-revise-verify-and-ship.md` exactly (Part C1 revise, Part C2 verify, Part C3 walkthrough + ship gate).

---

## Next Actions
After completing Phase 3 (including Part C revisions and commits), suggest the following next actions to the user:

1. \`ship it\` (See `AGENTS.md` for PR/Merge definition).
2. Provide an explicit, copy-pasteable prompt block that starts a fail-closed adversarial review in a new chat using `@docs/workflow/review-and-harden-prompt.md` against the finalized walkthrough artifact before shipping. The prompt block must explicitly require:
   - hallucination/scope-drift detection versus approved prior-phase artifacts (if any),
   - strict reporting of bugs/missing tests/design issues/suggested fixes,
   - safe closure of all justified findings (blocking mandatory; non-blocking unless rejected with rationale),
   - explicit pass/fail verification evidence before final ship recommendation,
   - and end with this exact instruction: `And then: Address ALL your audit findings (raised bugs/tests/issues/fixes/comments/etc.) safely and carefully.`

---

## How to Invoke in Chat

Use:

```text
Use @docs/workflow/phase-3-run-execution.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Run Phase 3 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```
