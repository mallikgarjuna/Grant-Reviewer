# Phase 1 Runner — Brainstorm → Spec (1.1 + 1.2 + 1.3)

This file is a workflow instruction.
Reference it in chat (Codex or Antigravity or any coding agent) using @docs/workflow/phase-1-run-spec.md.
Do NOT modify this file during execution.

---

## Purpose

Run Phase 1 end-to-end in one chat (Codex or Antigravity or any coding agent) run:

- Phase 1.1: generate spec v0.1
- Phase 1.2: review gate (no file edits during review)
- Phase 1.3: revise spec + bump version

This runner must output a clear transcript of what happened in each part.

---

## Required Inputs

- docs/brainstorms/brainstorm-WF-XXXX-<slug>.md
- docs/index.md

Spec output path depends on type (page vs feature):

- docs/specs/pages/spec-WF-XXXX-<slug>.md
  or
- docs/specs/features/spec-WF-XXXX-<slug>.md

---

## Phase Gate — Commit Previous Phase

Before starting Phase 1, ensure the Phase 0 brainstorm artifact is **saved and committed**:

- `docs/brainstorms/brainstorm-WF-XXXX-<slug>.md`
- `docs/index.md` WF row is present and correct

---

## Phase Completion — Commit This Phase

After completing Phase 1 (including Part C revisions):

- Ensure the updated spec (and any `docs/index.md` status/link changes) are **saved and committed** before starting Phase 2.

---

## Runner Rules (Strict)

1. **Runners are Routers**: You **MUST** read the detailed instruction file referenced in each "PART" section below. Do not guess.
2. Execute Part A, then Part B, then Part C in order.
2. Print a short "PART A/B/C" header and a bullet summary of actions taken.
3. During Part B (review), do NOT edit any files.
4. If Part B finds blocking issues:
   - Ask the user up to 5 clarification questions.
   - For each question: provide 2–3 options + one recommended option.
   - Wait for user answers BEFORE applying revisions.
   - Then continue to Part C.
5. If Part B finds only minor issues:
   - Proceed to Part C and fix them automatically.
6. Do NOT expand scope beyond brainstorm.
7. Only update docs/index.md Status to Phase 1 if spec is marked "Ready for PRD".
8. At the end of the run, print an explicit **Traceability Statement** confirming:
   - Part B reviewed the spec produced in Part A.
   - Part C applied feedback produced in Part B.
   - Include concrete references (path + version and/or commit IDs).

---

## PART A — Generate Spec (delegate to Phase 1.1)

Follow @docs/workflow/phase-1-1-spec-generate.md exactly.

Output:

- spec v0.1

After writing, print:

- spec path
- version
- 5-bullet summary of what the spec contains

---

## PART B — Spec Review Gate (delegate to Phase 1.2)

Follow @docs/workflow/phase-1-2-spec-review.md exactly.

Print review output.
Also print:

- `Reviewed artifact: <path> @ <version>` (include commit ID when available)

Then classify issues:

- Blocking (cannot proceed without user input)
- Non-blocking (can be fixed automatically)

---

## PART C — Revise Spec (delegate to Phase 1.3)

Follow @docs/workflow/phase-1-3-spec-revise.md exactly.

- Apply review edits
- Bump version
- Update changelog
- Mark Ready for PRD if stable

If user answered questions:

- incorporate decisions
- note them succinctly in the spec (where appropriate)

Before ending Part C, print:

- `Applied feedback from Part B: yes/no`
- If yes, list 3–5 exact edits mapped to Part B findings.

---

## End of Runner — Next Actions

After completing Part C, output:

1. Current status:

- spec version
- whether Ready for PRD

2. Two recommended next actions (pick from):

- Run Phase 0.1 again to refine brainstorm (if spec still unclear)
- Run Phase 1 runner again (if still not ready)
- Proceed to Phase 2.1 (PRD generate)
- Update docs/index.md row if needed (status/links)

Keep it concise.

Also output this final block:

## Traceability Statement (Required)

- Part A output reviewed in Part B: `<yes/no>` + `<path/version/commit>`
- Part B feedback applied in Part C: `<yes/no>` + `<key edits>`

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-1-run-spec.md
- @docs/index.md
- @docs/brainstorms/brainstorm-WF-XXXX-<slug>.md

Instruction:

"Run Phase 1 end-to-end for WF-XXXX/<slug> using this runner. Print what you did in Part A/B/C. Ask me questions if needed (options + recommendation). End with two suggested next actions."
