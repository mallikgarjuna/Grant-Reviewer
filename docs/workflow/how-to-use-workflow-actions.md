# How To Use Workflow Actions — Chat Prompt Templates

Replace placeholders like `<WF-ID>` and `<slug>` with your current workflow values.

This is a minimal "cheat sheet" of verbatim chat prompt templates for each workflow action.

Note: phases are 0/1/2/3; Phase 1 + Phase 2 share one unified runner (`phase-1-2-run-planning.md`, Phase ID selects 1 vs 2).

---

## Lifecycle: Auto (End-to-End)

Warning: use only if `lifecycle-run-*.md` is kept in sync with `docs/workflow/README.md` invariants (US#/FR#/Slice, mandatory TDD). If unsure, use the phase runners below.

```text
Use @docs/workflow/lifecycle-run-auto.md
@docs/index.md

Title: <Title>
Type: <page|feature>
Slug: <slug>

Run the end-to-end auto lifecycle for this initiative.
```

---

## Lifecycle: Interactive (End-to-End)

Warning: use only if `lifecycle-run-*.md` is kept in sync with `docs/workflow/README.md` invariants (US#/FR#/Slice, mandatory TDD). If unsure, use the phase runners below.

```text
Use @docs/workflow/lifecycle-run-interactive.md
@docs/index.md

Title: <Title>
Type: <page|feature>
Slug: <slug>

Run the end-to-end interactive lifecycle for this initiative.
```

---

## Phase 0 — Ideation: Start Workflow + Brainstorm

This runs Phase 0.0 (mint WF ID + branch + register) + Phase 0.1 (brainstorm) in sequence.

```text
Use @docs/workflow/phase-0-run-ideation.md
@docs/index.md
@docs/templates/brainstorm-template.md

Title: <Title>
Type: <page|feature>
Slug: <slug>

Run Phase 0 end-to-end for this initiative.
Execute Part A1 (0.0), then Part A2 (0.1), then Part B (risk audit), then Part C (revise) exactly as routed.
Ask interactive brainstorm questions with options + recommendation.
End with two suggested next actions.
```

---

## Optional Add-On (Type: page) — Page Spec Appendix (Before PRD)

Use when `Type: page` and the workflow needs explicit page states/wireframe before PRD. Writes into the brainstorm (no new artifact type).

```text
Use @docs/templates/create-page-spec-prompt.md (or `create-page-spec-prompt-lite.md`)
@docs/brainstorms/brainstorm-<WF-ID>-<slug>.md

Append a `## Appendix — Page Spec (MVP)` to the brainstorm for <WF-ID>/<slug>.
Then commit and proceed to Phase 1 runner.
```

---

## Phase 1 — Definition: Brainstorm → PRD

Phase 1 output requirements (enforced by runner):
- PRD includes `User Stories (MVP)` + `Deferred Stories`, `FR#` requirement IDs linked to `US#`, `Testing Decisions (TDD)`, and US# traceability in flows/contracts.

```text
Use @docs/workflow/phase-1-2-run-planning.md
@docs/index.md
@docs/brainstorms/brainstorm-<WF-ID>-<slug>.md

Run Phase 1 end-to-end for <WF-ID>/<slug> using this unified runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```

---

## Phase 2 — Planning: PRD → Tasks

Phase 2 output requirements (enforced by runner):
- Each task includes `Slice`, `User Stories (US#)`, `PRD Requirements (FR#)`, and an early tracer-bullet task; TDD is mandatory for behavior changes/bug fixes.

```text
Use @docs/workflow/phase-1-2-run-planning.md
@docs/index.md
@docs/prds/prd-<WF-ID>-<slug>.md

Run Phase 2 end-to-end for <WF-ID>/<slug> using this unified runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
Ensure tasks include dependency metadata (`Depends on`, `Enables`, `Parallelizable`) for planning clarity only.
End with two suggested next actions.
```

---

## Phase 3 — Execution: Implement + Verify + Ship

```text
Use @docs/workflow/phase-3-run-execution.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Run Phase 3 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```

---

## Phase 3.1 — Implement Only

```text
Use @docs/workflow/phase-3-1-implement-tasks.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Implement all tasks sequentially for <WF-ID>/<slug>.
For each task: implement, run local tests, commit.
Check off each task as [x] in the task file.
When ALL tasks are done, STOP. Do NOT write the walkthrough or update docs/index.md.
```

---

## Phase 3.2 — Technical Audit Review Gate

```text
Use @docs/workflow/phase-3-2-technical-audit-review.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Assume implementation tasks are DONE.
Run Phase 3.2 (Technical Audit Review Gate) for <WF-ID>/<slug>.
Do NOT edit files.
Print findings in:
1) potential bugs
2) missing tests
3) design issues
4) suggested fixes
5) refactored version with comments
End with two suggested next actions.
```

---

## Phase 3.3 — Revise, Verify, Walkthrough & Ship

```text
Use @docs/workflow/phase-3-3-revise-verify-and-ship.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Use the Phase 3.2 review output from this session.
Run Phase 3.3 for <WF-ID>/<slug>: apply review fixes, verify, then walkthrough + ship gate.
Print what you did in Part C1/C2/C3.
End with two suggested next actions.
```

---
## Quick Tips (Implicit)

- Always supply proper `<WF-ID>` and `<slug>`.
- For WF initiatives, use branch naming: `wf/<WF-ID>-<slug>` (expanded: `wf/WF-XXXX-<slug>`).
- For non-WF maintenance, use `fix/<slug>` or `chore/<slug>` (no WF ID).
- Artifact files should follow the `<artifact>-<WF-ID>-<slug>.md` naming rule.
- These prompts should map directly to your workflow instructions in `docs/workflow/`.
- TDD is mandatory for behavior changes/bug fixes: see `docs/guides/tdd/README.md`.

---

## Maintenance — Quick Fix (Non-WF)

Use for repo hygiene/docs/tooling changes that should NOT mint a WF ID and should NOT touch WF artifacts.

```text
Use @docs/workflow/util-maintenance-quick-fix.md

Goal: <1 sentence>
Scope: <2-4 bullets>
Constraints: non-WF maintenance; do not touch docs/index.md WF rows; commit after changes.

Run the maintenance quick-fix runner end-to-end.
```

---

## Add-On: Optional Adversarial Re-Run (Same Session)

If you want an extra check during Phase 1 or 2 gates: just re-run Part B in the same session and compare findings (no edits).
