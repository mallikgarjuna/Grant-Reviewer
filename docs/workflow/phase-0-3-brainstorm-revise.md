# Phase 0.3 — Brainstorm Revise & Bump (Apply Risk Audit)

This file is a workflow instruction.
Reference it in Codex chat using @docs/workflow/phase-0-3-brainstorm-revise.md.
Do NOT modify this file during execution.

---

## Purpose

Incorporate the Part B risk-audit feedback into the brainstorm artifact created in Phase 0.1.

This part converts “audit feedback” into “tightened artifact”, while preserving the original scope and the no-behavior-change boundaries.

---

## Inputs Required

- Brainstorm artifact path (same one reviewed in Part B)
- Part B audit output (Blocking + Non-blocking findings)
- User answers to any clarification questions (if Part B asked them)

## Phase Gate & Completion

- **START**: Ensure Phase 0.2 review output is captured in chat and the current brainstorm file is saved.
- **FINISH**: Ensure the revised brainstorm artifact is **saved and committed** before moving to the next phase.

---

## Rules (Strict)

1. Apply edits from Part B; do not introduce new scope.
2. Preserve the brainstorm’s intent; tighten ambiguity.
3. Bump:
   - `Version`: `v0.x` → next `v0.(x+1)`
   - `Last Updated`: today (YYYY-MM-DD)
4. Update `Status`:
   - If blocking issues are resolved: `Draft Complete`
   - Otherwise: keep as `Draft` and explicitly call out remaining blockers.
5. Commit the brainstorm updates before ending this part.

---

## Output Format (Required)

After edits, print:

- `Brainstorm updated: <path> @ <new version> (<status>)`
- `Applied feedback from Part B: yes/no`
- If yes: list 3–5 exact edits mapped to Part B findings
- If no: explain why (e.g., no findings, user declined changes)
