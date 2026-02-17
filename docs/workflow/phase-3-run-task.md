# Phase 3 Runner — PRD → Tasks (3.1 + 3.2 + 3.3)

This file is a workflow instruction.
Reference it in chat (Codex or Antigravity or any coding agent) using @docs/workflow/phase-3-run-task.md.
Do NOT modify this file during execution.

---

## Purpose

Run Phase 3 end-to-end in one chat (Codex or Antigravity or any coding agent) run:

- Phase 3.1: generate Tasks v0.1
- Phase 3.2: tasks review (no file edits during review)
- Phase 3.3: revise tasks + bump version

This runner must display clear output showing what happened in each part.

---

## Required Inputs

- docs/prds/prd-WF-XXXX-<slug>.md
- docs/index.md

Tasks output:

- docs/tasks/task-WF-XXXX-<slug>.md

---

## Phase Gate — Commit Previous Phase

Before starting Phase 3, ensure the Phase 2 PRD is **saved and committed**:

- `docs/prds/prd-WF-XXXX-<slug>.md` is committed and marked Ready for Tasks
- `docs/index.md` status/links are committed if updated in Phase 2

---

## Phase Completion — Commit This Phase

After completing Phase 3 (including Part C revisions):

- Ensure the task file (and any `docs/index.md` status/link updates) are **saved and committed** before starting Phase 4.

---

## Runner Rules (Strict)

1. **Runners are Routers**: You **MUST** read the detailed instruction file referenced in each "PART" section below. Do not guess.
2. Execute Part A, then Part B, then Part C in order.
2. Print a short "PART A/B/C" header and a bullet summary of actions taken.
3. During Part B (review), do NOT edit any files.
4. If Part B identifies blocking sequencing or missing integration tasks:
   - Ask the user up to 5 clarification questions.
   - For each question: provide 2–3 options + one recommended option.
   - Wait for user answers BEFORE applying revisions.
   - Then continue to Part C.
5. If issues are non-blocking:
   - Proceed to Part C and fix automatically.
6. Do NOT expand scope beyond the PRD.
7. Only update docs/index.md Status to Phase 3 if tasks are marked "Ready for Implementation".
8. At the end of the run, print an explicit **Traceability Statement** confirming:
   - Part B reviewed the artifact produced in Part A.
   - Part C applied feedback produced in Part B.
   - Include concrete references (path + version and/or commit IDs).

---

## PART A — Generate Tasks (delegate to Phase 3.1)

Follow @docs/workflow/phase-3-1-task-generate.md exactly.

After writing, print:

- tasks path
- version
- number of tasks created
- 5-bullet summary of task structure

---

## PART B — Tasks Review (delegate to Phase 3.2)

Follow @docs/workflow/phase-3-2-task-review.md exactly.

Print review output.
Also print:

- `Reviewed artifact: <path> @ <version>` (include commit ID when available)

Then classify:

- Blocking (requires user decision)
- Non-blocking (can revise directly)

---

## PART C — Revise Tasks (delegate to Phase 3.3)

Follow @docs/workflow/phase-3-3-task-revise.md exactly.

- Apply review edits
- Bump version
- Update changelog
- Mark "Ready for Implementation" if stable

If user answered clarification questions:

- incorporate selected options
- ensure sequencing is consistent

Before ending Part C, print:

- `Applied feedback from Part B: yes/no`
- If yes, list 3–5 exact edits mapped to Part B findings.

---

## End of Runner — Next Actions

After completing Part C, output:

1. Current status:

- tasks version
- whether Ready for Implementation

2. Two recommended next actions (pick from):

- Proceed to Phase 4.1 (Implement Tasks)
- Re-run this runner if task breakdown still unclear
- Step back to Phase 2 if PRD issues were discovered
- Update docs/index.md row if needed (status/links)

Keep it concise.

Also output this final block:

## Traceability Statement (Required)

- Part A output reviewed in Part B: `<yes/no>` + `<path/version/commit>`
- Part B feedback applied in Part C: `<yes/no>` + `<key edits>`

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-3-run-task.md
- @docs/index.md
- @docs/prds/prd-WF-XXXX-<slug>.md

Instruction:

"Run Phase 3 end-to-end for WF-XXXX/<slug> using this runner. Print what you did in Part A/B/C. Ask me questions if needed (options + recommendation). End with two suggested next actions."
