# Phase 3.3 — Revise, Verify, Walkthrough & Ship

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-3-3-revise-verify-and-ship.md.
Do NOT modify this file during execution.

---

## Purpose
Apply fixes from Phase 3.2 technical audit, verify the final implementation, then complete walkthrough + ship-gate artifacts.

---

## Inputs Required
1. A completed Tasks artifact for the WF (e.g., `docs/tasks/task-<WF-ID>-<slug>.md`) where implementation is complete.
2. Phase 3.2 technical audit output from chat.

---

## Phase Gate & Completion
- **START**: Phase 3.2 review output exists and implementation baseline is available.
- **FINISH**: Revisions (if needed) are applied and verified; walkthrough/index/archive updates are committed; push/merge remains user-gated.

---

## Runner Rules

1. Execute PART C1, then PART C2, then PART C3 in strict order.
2. Scope is limited to implementing Phase 3.2 findings plus required verification/walkthrough/ship steps.
3. If Part C1 introduces behavior changes or bug fixes, TDD is mandatory (red/green/refactor; boundary-only mocking): `docs/guides/tdd/README.md`.
4. For any bug fixed in Part C1, add/update a failing reproducer test before code fix.
5. If Part C2 fails, return to Part C1, fix, then re-run Part C2.

---

### PART C1: Revise (Mini Implement Loop)
1. Convert Phase 3.2 findings into a minimal fix list.
2. Implement only required fixes; do not expand product scope.
3. For each code-writing change, explicitly report:
   - what could break
   - what tests were run
   - what additional targeted tests are recommended
4. If behavior change/bug fix:
   - log `RED`, `GREEN`, `REFACTOR` in chat
   - keep changes minimal and traceable
5. Commit fix changes with clear messages.

### PART C2: Verify [GATE]
1. Run `pre-commit run --all-files` (or equivalent lint/format checks).
2. Run the project's relevant automated tests and explicitly print pass/fail evidence.
3. If work touched UI/Frontend, ask the user whether to do manual visual validation or agentic browser validation.
4. If changed files include auth boundary surface (`frontend/src/proxy.ts`, `frontend/src/app/sign-in/**`, `frontend/src/lib/auth/**`, `frontend/src/lib/bff/**`, or Playwright auth specs/workflows), explicitly remind the user to run both auth lanes (`verify auth lanes`): `AUTH_MODE=test_bypass` and `AUTH_MODE=clerk`.
5. For the Clerk lane, explicitly report whether credentialed login flow was executed or skipped due to missing test credentials.
6. If any check fails, return to Part C1 and fix.
7. Await explicit user approval ("go ahead", "LGTM") before proceeding to Part C3.

### PART C3: Walkthrough + Ship [GATE]
1. Read `docs/walkthroughs/walkthrough-<WF-ID>-<slug>.md`.
2. Follow its template/instructions (or create a standard walkthrough if empty).
3. Draft walkthrough: what changed, what was verified, remaining risks, next steps.
4. Run `git mv` to move active WF artifacts (Brainstorm, PRD, Tasks, Walkthrough) to corresponding `completed/` directories.
5. Update `docs/index.md`:
   - set WF status to `Done`
   - update that WF row links to `completed/` paths
6. Run final `git add` + `git commit` for walkthrough, moves, and index updates.
7. **STOP**: wait for explicit user approval ("Ship it") before `git push`, PR open, or merge.

---

## Next Actions
After completing Phase 3.3, suggest the following next actions:

1. `ship it` (See `AGENTS.md` for PR/Merge definition).
2. Start a new workflow / idea.

---

## How to Invoke in Chat

Use:

```text
Use @docs/workflow/phase-3-3-revise-verify-and-ship.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Use the Phase 3.2 review output from this session.
Run Phase 3.3 for <WF-ID>/<slug>: apply review fixes, verify, then walkthrough + ship gate.
Print what you did in Part C1/C2/C3.
End with two suggested next actions.
```
