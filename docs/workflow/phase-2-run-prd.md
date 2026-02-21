# Phase 2 Runner — Spec → PRD (2.1 + 2.2 + 2.3)

This file is a workflow instruction.
Reference it in chat (Codex or Antigravity or any coding agent) using @docs/workflow/phase-2-run-prd.md.
Do NOT modify this file during execution.

---

## Purpose

Run Phase 2 end-to-end in one chat (Codex or Antigravity or any coding agent) run:

- Phase 2.1: generate PRD v0.1
- Phase 2.2: risk audit (no file edits during audit)
- Phase 2.3: revise PRD + bump version + log decisions

This runner must display clear output showing what happened in each part.

---

## Required Inputs

- docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md
- docs/index.md
- docs/logs/decisions.md

PRD output:

- docs/prds/prd-WF-XXXX-<slug>.md

---

## Phase Gate — Commit Previous Phase

Before starting Phase 2, ensure the Phase 1 spec is **saved and committed**:

- `docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md` is the committed source of truth
- Any relevant decision/Q&A logs are committed if they inform the PRD

---

## Phase Completion — Commit This Phase

After completing Phase 2 (including Part C revisions + decision logging):

- Ensure the updated PRD and any updated logs (`docs/logs/decisions.md`, `docs/index.md`) are **saved and committed** before starting Phase 3.

---

## Runner Rules (Strict)

1. **Runners are Routers**: You **MUST** read the detailed instruction file referenced in each "PART" section below. Do not guess.
2. Execute Part A, then Part B, then Part C in order.
3. Print a short "PART A/B/C" header and a bullet summary of actions taken.
4. During Part B (risk audit), do NOT edit any files.
5. If Part B identifies missing decisions that block revision:
   - Ask the user up to 5 clarification questions.
   - For each question: provide 2–3 options + one recommended option.
   - Wait for user answers BEFORE applying revisions.
   - Then continue to Part C.
5. If Part B issues are non-blocking:
   - Proceed to Part C and fix automatically.
6. Do NOT expand scope beyond the Spec.
7. Only update docs/index.md Status to Phase 2 if PRD is marked "Ready for Tasks".
8. At the end of the run, print an explicit **Traceability Statement** confirming:
   - Part B reviewed the artifact produced in Part A.
   - Part C applied feedback produced in Part B.
   - Include concrete references (path + version and/or commit IDs).

---

## PART A — Generate PRD (delegate to Phase 2.1)

Follow @docs/workflow/phase-2-1-prd-generate.md exactly.

After writing, print:

- PRD path
- version
- 5-bullet summary of what's in the PRD

---

## PART B — PRD Risk Audit (delegate to Phase 2.2)

Follow @docs/workflow/phase-2-2-prd-risk-audit.md exactly.

Print audit output.
Also print:

- `Reviewed artifact: <path> @ <version>` (include commit ID when available)

Then classify:

- Blocking (needs user decision)
- Non-blocking (can revise directly)

---

## PART C — Revise PRD + Log Decisions (delegate to Phase 2.3)

Follow @docs/workflow/phase-2-3-prd-revise.md exactly.

- Apply audit edits
- Bump version
- Update changelog
- Update docs/logs/decisions.md with decisions made

If user answered questions:

- incorporate chosen options
- log those decisions (Date, WF ID, Context, Decision, Why, Tradeoff)

Mark PRD "Ready for Tasks" if stable.

Before ending Part C, print:

- `Applied feedback from Part B: yes/no`
- If yes, list 3–5 exact edits mapped to Part B findings.

---

## End of Runner — Next Actions

After completing Part C, output:

1. Current status:

- PRD version
- whether Ready for Tasks

2. Two recommended next actions (pick from):

- Proceed to Phase 3.1 (Tasks generate)
- Re-run this runner if PRD still not stable
- Step back to Phase 1 if spec problems were discovered
- Update docs/index.md row if needed (status/links)

Keep it concise.

Also output this final block:

## Traceability Statement (Required)

- Part A output reviewed in Part B: `<yes/no>` + `<path/version/commit>`
- Part B feedback applied in Part C: `<yes/no>` + `<key edits>`

---

## How to Invoke in Chat

Use:

- @docs/workflow/phase-2-run-prd.md
- @docs/index.md
- @docs/specs/<pages|features>/spec-WF-XXXX-<slug>.md
- @docs/logs/decisions.md

Instruction:

"Run Phase 2 end-to-end for WF-XXXX/<slug> using this runner. Print what you did in Part A/B/C. Ask me questions if needed (options + recommendation). End with two suggested next actions."
