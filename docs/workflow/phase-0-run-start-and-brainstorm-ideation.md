# Phase 0 Runner — Start Workflow + Brainstorm (0.0 + 0.1)

This file is a workflow instruction.
Reference it in chat (Codex or Antigravity or any coding agent) using @docs/workflow/phase-0-run-start-and-brainstorm.md.
Do NOT modify this file during execution.

---

## Purpose

Run Phase 0 end-to-end in one chat run:

- Phase 0.0: mint WF ID, create artifacts, create branch, register WF row
- Phase 0.1: run interactive brainstorm and capture baseline direction

This runner removes manual handoff errors between 0.0 and 0.1.

---

## Required Inputs

- Title
- Type: page OR feature
- Slug
- docs/index.md
- docs/templates/brainstorm-template.md

---

## Runner Rules (Strict)

1. **Runners are Routers**: You **MUST** read the detailed instruction file referenced in each "PART" section below. Do not guess.
2. Execute Part A, then Part B in order.
3. Print a short "PART A/B" header and a bullet summary of actions taken.
4. Phase 0.1 is interactive:
   - ask one question block at a time
   - provide 2-3 options + one recommended option
   - wait for user reply before continuing
5. Keep scope within the selected WF item; do not jump to Spec/PRD generation in this runner.
6. Ensure Phase 0.0 artifacts are committed before continuing to Part B.
7. At the end of the run, print an explicit **Traceability Statement** confirming:
   - Part B used the WF ID/slug created in Part A
   - include concrete references (branch name + artifact path/version and/or commit ID)

---

## PART A — Start Workflow (delegate to Phase 0.0)

Follow @docs/workflow/phase-0-0-start-workflow.md exactly.

After completion, print:

- WF ID
- branch name
- list of created artifact paths
- commit ID

---

## PART B — Interactive Brainstorm (delegate to Phase 0.1)

Follow @docs/workflow/phase-0-1-brainstorm.md exactly.

Start at Section 1 and proceed until the user says "good enough" or "stop".

After completion, print:

- brainstorm path
- version
- status
- 5-bullet summary of chosen directions

---

## End of Runner — Next Actions

After completing Part B, output:

1. Current status:

- WF ID + slug
- brainstorm version and readiness

2. Two recommended next actions:

- Run Phase 1 runner: `@docs/workflow/phase-1-run-prd-definition.md`
- Sanity-check brainstorm quality/coverage and commit a small doc fix if needed

Keep it concise.

Also output this final block:

## Traceability Statement (Required)

- Part A output used in Part B: `<yes/no>` + `<WF ID/branch/commit>`
- Brainstorm file updated in Part B: `<path/version/status>`

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-0-run-start-and-brainstorm.md
- @docs/index.md
- @docs/templates/brainstorm-template.md

Instruction:

"Run Phase 0 end-to-end for this new initiative using this runner. Execute Part A then Part B, and ask me interactive brainstorm questions with options + recommendation."
