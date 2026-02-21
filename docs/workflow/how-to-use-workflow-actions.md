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

## Phase 1 — Run Spec (End-to-End)

```text
Use @docs/workflow/phase-1-run-spec.md
@docs/index.md
@docs/brainstorms/brainstorm-<WF-ID>-<slug>.md

Run Phase 1 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```

---

## Phase 2 — Run PRD (End-to-End)

```text
Use @docs/workflow/phase-2-run-prd.md
@docs/index.md
@docs/specs/<pages|features>/spec-<WF-ID>-<slug>.md
@docs/logs/decisions.md

Run Phase 2 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```

---

## Phase 3 — Run Tasks (End-to-End)

```text
Use @docs/workflow/phase-3-run-task.md
@docs/index.md
@docs/prds/prd-<WF-ID>-<slug>.md

Run Phase 3 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```

---

## Phase 4.1 — Implement Tasks

```text
Use @docs/workflow/phase-4-1-implement-tasks.md
@docs/tasks/task-<WF-ID>-<slug>.md

Execute tasks sequentially.
Commit after each with messages like:
<WF-ID>: <slug> — Task N — <short title>

Continue through all tasks.
When completed:

* Draft/Update walkthrough in docs/walkthroughs/walkthrough-<WF-ID>-<slug>.md
* Update docs/index.md Status to Done.

Stop when complete and suggest my next 2 actions.
```

---

## Quick Tips (Implicit)

- Always supply proper `<WF-ID>` and `<slug>`.
- Use branch naming: `wf/<WF-ID>-<slug>` to protect main.
- Artifact files should follow the `<artifact>-<WF-ID>-<slug>.md` naming rule.
- These prompts should map directly to your workflow instructions in `docs/workflow/`.
