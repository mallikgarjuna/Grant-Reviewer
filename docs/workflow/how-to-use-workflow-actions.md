# How To Use Workflow Actions — Chat Prompt Templates

Replace placeholders like `<WF-ID>` and `<slug>` with your current workflow values.

This is a minimal “cheat sheet” of verbatim chat prompt templates for each workflow action.

---

## Lifecycle: Auto (End-to-End)

```text
Use @docs/workflow/run-lifecycle-auto.md
@docs/index.md

Title: <Title>
Type: <page|feature>
Slug: <slug>

Run the end-to-end auto lifecycle for this initiative.
```

---

## Lifecycle: Interactive (End-to-End)

```text
Use @docs/workflow/run-lifecycle-interactive.md
@docs/index.md

Title: <Title>
Type: <page|feature>
Slug: <slug>

Run the end-to-end interactive lifecycle for this initiative.
```

---

## Phase 0.0 — Start Workflow (Mint WF ID + Branch + Register)

```text
Use @docs/workflow/phase-0-0-start-workflow.md
and @docs/index.md

Title: <Title>
Type: <page|feature>
Slug: <slug>

Please:

1. Determine the next WF ID from @docs/index.md
2. Create the required artifact files
3. From the latest main, create git branch: wf/<WF-ID>-<slug>
4. Commit the new artifacts with:
   <WF-ID>: start workflow (<slug>)
5. Add a new row in @docs/index.md with Status "Phase 0"

Stop after completing these steps and suggest my next 2 actions.
```

---

## Phase 0.1 — Interactive Brainstorm

```text
Use @docs/workflow/phase-0-1-brainstorm.md
@docs/templates/brainstorm-template.md
@docs/index.md
@docs/brainstorms/brainstorm-<WF-ID>-<slug>.md

Run an interactive, context-aware brainstorming session:

* Ask 2–3 options + best recommendation per question
* Wait for my input for each selection
* Update brainstorm file incrementally

Start with Section 1 (Problem Statement).

When I say the brainstorm is “good enough” (or I say “stop”), stop and suggest my next 2 actions.
```

---

## Phase 0 — Run Start + Brainstorm (End-to-End)

This runs Phase 0.0 + 0.1 in sequence.

```text
Use @docs/workflow/phase-0-run-start-and-brainstorm.md
@docs/index.md
@docs/templates/brainstorm-template.md

Title: <Title>
Type: <page|feature>
Slug: <slug>

Run Phase 0 end-to-end for this initiative.
Execute Part A (0.0) then Part B (0.1) exactly as routed.
Ask interactive brainstorm questions with options + recommendation.
End with two suggested next actions.
```

---

## Phase 1/2/3 — Run Planning (End-to-End)

```text
Use @docs/workflow/phase-123-run-planning.md
@docs/index.md
@docs/<INPUT_FOLDER>/<artifact>-<WF-ID>-<slug>.md

Run Phase [ID] end-to-end for <WF-ID>/<slug> using this unified runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```

---

## Phase 4 — Run Implement (End-to-End)

```text
Use @docs/workflow/phase-4-run-implement.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Run Phase 4 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```

---

## Phase 4.2 — Verify & Ship (Post-Implementation)

```text
Use @docs/workflow/phase-4-2-verify-and-ship.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Assume implementation tasks are DONE.
Run Phase 4.2 (Verify & Ship) for <WF-ID>/<slug> using this runner.
Print what you did in Part B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```

---
## Quick Tips (Implicit)

- Always supply proper `<WF-ID>` and `<slug>`.
- Use branch naming: `wf/<WF-ID>-<slug>` to protect main.
- Artifact files should follow the `<artifact>-<WF-ID>-<slug>.md` naming rule.
- These prompts should map directly to your workflow instructions in `docs/workflow/`.
