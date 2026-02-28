# Phase 3.2 — Technical Audit Review Gate (No Edits)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-3-2-technical-audit-review.md.
Do NOT modify this file during execution.

---

## Purpose
Perform a strict technical audit of completed Phase 3 implementation before any revision or ship actions.

This phase is review-only and produces findings in chat.
No file edits are allowed in this phase.

## Inputs Required
1. A completed Tasks artifact representing the current WF scope (e.g., `docs/tasks/task-<WF-ID>-<slug>.md`) where ALL tasks are marked as `[x]`.
2. Relevant implementation diff/commits from Phase 3.1 (or resumed Part A).

## Phase Gate & Completion
- **START**: Implementation tasks are done and implementation commits from Phase 3.1 are available for audit.
- **FINISH**: Technical audit findings are printed in chat with clear fix guidance for Phase 3.3. This is a no-edit review phase; if no files changed, there is nothing to commit.

## Runner Rules

1. Execute only this review gate (Phase 3.2). Do not implement fixes here.
2. This file is the canonical source for Phase 3 Part B (Review) behavior.
3. File edits are forbidden in this phase. If fixes are needed, defer to Phase 3.3.

---

### PART B: Technical Audit (Code Review) [GATE]
1. Stop feature work and perform a detailed technical audit (code review) of Phase 3 Part A implementation only.
2. Output the audit in this exact structure:
   1. potential bugs
   2. missing tests
   3. design issues
   4. suggested fixes
   5. refactored version with comments (only for high-impact snippets; keep minimal and actionable)
3. Keep review scope exclusive to technical audit concerns; avoid product-scope brainstorming or non-technical critique.
4. For each finding, include severity (`blocking` or `non-blocking`) and a concrete target (file/test area).
5. Do not modify files in this phase.

---

## Next Actions
After completing Phase 3.2, suggest the following next actions to the user:

1. Run Phase 3.3 revise + verify + walkthrough/ship: `@docs/workflow/phase-3-3-revise-verify-and-ship.md`
2. Re-run Phase 3.2 if the implementation changed materially.

---

## How to Invoke in Chat

Use:

```text
Use @docs/workflow/phase-3-2-technical-audit-review.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Assume implementation tasks are DONE.
Run Phase 3.2 (Technical Audit Review Gate) for <WF-ID>/<slug>.
Do NOT edit files.
Print Part B review findings in the required 1-5 structure with severity.
End with two suggested next actions.
```
