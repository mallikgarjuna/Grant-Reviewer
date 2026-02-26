# Phase 0 Runner — Start Workflow + Brainstorm + Review Gate (0.0 + 0.1)

This file is a workflow instruction.
Reference it in chat (any coding agent) using @docs/workflow/phase-0-run-start-and-brainstorm-ideation.md.
Do NOT modify this file during execution.

---

## Purpose

Run Phase 0 end-to-end in one chat run:

- Phase 0.0 (Part A1): mint WF ID, create artifacts, create branch, register WF row
- Phase 0.1 (Part A2): run interactive brainstorm and capture baseline direction
- Part B: run a critical risk audit (no edits)
- Part C: revise + bump the brainstorm using Part B feedback

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
2. Execute Part A1, then Part A2, then Part B, then Part C in order.
3. Print a short "PART A1/A2/B/C" header and a bullet summary of actions taken.
4. Phase 0.1 (Part A2) is interactive:
   - ask one question block at a time
   - provide 2-3 options + one recommended option
   - wait for user reply before continuing
5. Keep scope within the selected WF item; do not jump to PRD generation in this runner.
6. Ensure Phase 0.0 artifacts are committed before continuing to Part A2.
7. Ensure the brainstorm edits from Part A2 are committed before continuing to Part B.
8. During Part B (review/audit), do NOT edit any files.
9. Ensure Part C revisions are committed before ending the runner.
10. At the end of the run, print an explicit **Traceability Statement** confirming:
   - Part A2/B/C used the WF ID/slug created in Part A1
   - include concrete references (branch name + artifact path/version and/or commit ID)

---

## PART A1 — Start Workflow (delegate to Phase 0.0)

Follow @docs/workflow/phase-0-0-start-workflow.md exactly.

After completion, print:

- WF ID
- branch name
- list of created artifact paths
- commit ID

---

## PART A2 — Interactive Brainstorm (delegate to Phase 0.1)

Follow @docs/workflow/phase-0-1-brainstorm.md exactly.

Start at Section 1 and proceed until the user says "good enough" or "stop".

After completion, print:

- brainstorm path
- version
- status
- 5-bullet summary of chosen directions

---

## PART B — Review Gate (No Edits)

Follow @docs/workflow/phase-0-2-brainstorm-risk-audit.md exactly.

After completion, print:

- review output
- `Reviewed artifact: <path> @ <version>`
- issue classification: Blocking vs Non-blocking

---

## PART C — Revise & Bump

Follow @docs/workflow/phase-0-3-brainstorm-revise.md exactly.

After completion, print:

- brainstorm path
- new version
- new status
- `Applied feedback from Part B: yes/no` + 3–5 exact edits (if yes)

---

## End of Runner — Next Actions

After completing Part C, output:

1. Current status:

- WF ID + slug
- brainstorm version and readiness

2. Two recommended next actions:

- **Run Phase 1 runner**: `@docs/workflow/phase-12-run-planning.md`
   - **CRITICAL**: For the recommended next phase, you MUST provide an explicit, copy-pasteable prompt block that the user can run to start it.
   - Example format for the prompt block:
     ```text
     Use @docs/workflow/phase-12-run-planning.md
     @docs/index.md
     @docs/INPUT/...

     Run Phase 1 ...
     ```
- **Optional Adversarial Pass (Same Session, No Edits):** Re-run Part B’s risk audit and summarize deltas since Part C.

If `Type: page` and UX/state/positioning is non-trivial, you MAY recommend this optional add-on before Phase 1:

- Use `@docs/templates/create-page-spec-prompt.md` (or `create-page-spec-prompt-lite.md`) to append `## Appendix — Page Spec (MVP)` into the brainstorm, commit, then proceed to Phase 1.

Also output this final block:

## Traceability Statement (Required)

- Part A1 output used in Part A2: `<yes/no>` + `<WF ID/branch/commit>`
- Part A2 output reviewed in Part B: `<yes/no>` + `<path/version>`
- Part B feedback applied in Part C: `<yes/no>` + `<key edits>`
- Brainstorm file updated in Part C: `<path/version/status>`

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-0-run-start-and-brainstorm-ideation.md
- @docs/index.md
- @docs/templates/brainstorm-template.md

Instruction:

"Run Phase 0 end-to-end for this new initiative using this runner. Execute Part A1 then Part A2 then Part B then Part C. Ask me interactive brainstorm questions with options + recommendation. Do not edit files during Part B."
