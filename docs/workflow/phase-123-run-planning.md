# Phase 1/2/3 Unified Runner — Planning

This file is a workflow instruction orchestrator.
Reference it in chat (Codex, Antigravity, or any coding agent) using `@docs/workflow/phase-123-run-planning.md`.
Do NOT modify this file during execution.

---

## Purpose
Run the specified planning phase (Phase 1, Phase 2, or Phase 3) end-to-end in a single chat session. This runner wraps the Part A (Generate), Part B (Review Gate), and Part C (Revise) sub-phases into one parameterized flow.

---

## Required Parameters
When invoking this runner, the user MUST specify the **Phase ID** (1, 2, or 3), the **WF-ID**, and the **Slug**.

Based on the **Phase ID**, use the following matrix to define your Inputs, Targets, and Sub-phase instructions:

| Phase ID | Input Artifact (Read) | Target Output Artifact (Write) | Part A (Generate) | Part B (Review) | Part C (Revise) |
|---|---|---|---|---|---|
| **Phase 1** | `brainstorms/brainstorm-WF-XXXX-<slug>.md` | `specs/.../spec-WF-XXXX-<slug>.md` | `@docs/workflow/phase-1-1-spec-generate.md` | `@docs/workflow/phase-1-2-spec-review.md` | `@docs/workflow/phase-1-3-spec-revise.md` |
| **Phase 2** | `specs/.../spec-WF-XXXX-<slug>.md` | `prds/prd-WF-XXXX-<slug>.md` | `@docs/workflow/phase-2-1-prd-generate.md` | `@docs/workflow/phase-2-2-prd-risk-audit.md` | `@docs/workflow/phase-2-3-prd-revise.md` |
| **Phase 3** | `prds/prd-WF-XXXX-<slug>.md` | `tasks/task-WF-XXXX-<slug>.md` | `@docs/workflow/phase-3-1-task-generate.md` | `@docs/workflow/phase-3-2-task-review.md` | `@docs/workflow/phase-3-3-task-revise.md` |

*(Note: Spec output path depends on whether it is a page or feature: `docs/specs/pages/` or `docs/specs/features/`)*

---

## Phase Gate — Commit Previous Phase

Before starting, ensure the **Input Artifact** for the specified phase is **saved and committed** on the WF branch, and `docs/index.md` is updated.

---

## Phase Completion — Commit This Phase

After completing Part C revisions, ensure the **Target Output Artifact** (and any `docs/index.md` status/link changes) are **saved and committed** before the user starts the next phase.

---

## Runner Rules (Strict)

1. **Runners are Routers**: You **MUST** read the detailed instruction file referenced in the matrix for each "PART" below. Do not guess the logic.
2. Execute Part A, then Part B, then Part C in strict order.
3. Print a short "PART A/B/C" header and a bullet summary of actions taken at the end of each part.
4. During Part B (review/audit), do NOT edit any files.
5. If Part B finds blocking issues:
   - Ask the user up to 5 clarification questions.
   - For each question: provide 2–3 options + one recommended option.
   - Wait for user answers BEFORE applying revisions (Part C).
6. If Part B finds only minor non-blocking issues:
   - Proceed to Part C and fix them automatically.
7. Do NOT expand scope beyond the Input Artifact.
8. Only update `docs/index.md` Status if the output is marked as "Ready for [Next Phase]" in Part C.

---

## PART A — Generate

1. Identify the Phase ID.
2. Follow the corresponding **Part A (Generate)** sub-phase instructions from the matrix exactly.
3. Output the v0.1 draft of the Target Output Artifact.
4. Print the artifact path, version, and a 5-bullet summary of what it contains.

---

## PART B — Review Gate (No Edits)

1. Identify the Phase ID.
2. Follow the corresponding **Part B (Review)** sub-phase instructions from the matrix exactly.
3. Print the review output.
4. Print: `Reviewed artifact: <path> @ <version>`.
5. Classify issues found into Blocking or Non-blocking.

---

## PART C — Revise & Bump

1. Identify the Phase ID.
2. Follow the corresponding **Part C (Revise)** sub-phase instructions from the matrix exactly.
3. Apply edits from Part B, bump the version (v0.1 -> v0.2), update the changelog, and update the status marker (Ready for PRD/Tasks/Implementation).
4. If the user answered blocking questions, incorporate their decisions.
5. Before ending Part C, print:
   - `Applied feedback from Part B: yes/no`
   - If yes, list 3–5 exact edits mapped to Part B findings.

---

## End of Runner — Next Actions

After completing Part C, output:

1. **Current Status**: Target Artifact version and readiness state.
2. **Two recommended next actions**, keeping it concise (e.g., Proceed to the next Phase, re-run this Phase, or update index).
3. **Traceability Statement (Required)**:
   - Part A output reviewed in Part B: `<yes/no>` + `<path/version>`
   - Part B feedback applied in Part C: `<yes/no>` + `<key edits>`

---

## How to Invoke in Chat

Use:

```text
Use @docs/workflow/phase-123-run-planning.md
@docs/index.md
@docs/INPUT/artifact-WF-XXXX-<slug>.md

Run Phase [ID] end-to-end for WF-XXXX/<slug> using this unified runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```
