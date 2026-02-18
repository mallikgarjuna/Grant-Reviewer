# How To Use Workflow Actions — Chat Prompt Templates

Replace placeholders like `<WF-ID>` and `<slug>` with your current workflow values.

This is a minimal “cheat sheet” of verbatim Codex chat prompt templates for each workflow action.

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

This runs Phase 1.1 + 1.2 + 1.3 in sequence.

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

## Phase 1.1 — Generate Spec (v0.1)

```text
Use @docs/workflow/phase-1-1-spec-generate.md
@docs/index.md
@docs/brainstorms/brainstorm-<WF-ID>-<slug>.md

Generate spec v0.1 from brainstorm for:

* docs/specs/pages/spec-<WF-ID>-<slug>.md
  or
* docs/specs/features/spec-<WF-ID>-<slug>.md

Stop after writing spec v0.1 and suggest my next 2 actions.
```

---

## Phase 1.2 — Spec Review Gate (No Edits)

```text
Use @docs/workflow/phase-1-2-spec-review.md
@docs/specs/<pages|features>/spec-<WF-ID>-<slug>.md

Run the spec review gate.
Return the review output only.
Include: Next 2 actions I should take (choose one).
Do NOT edit any files.
```

---

## Phase 1.3 — Revise Spec + Bump Version

```text
Use @docs/workflow/phase-1-3-spec-revise.md
@docs/specs/<pages|features>/spec-<WF-ID>-<slug>.md

Apply the review feedback,
bump version (v0.1 → v0.2),
update changelog,
mark Ready for PRD when stable.
Update @docs/index.md Status to Phase 1 as needed.

Stop after revising and suggest my next 2 actions.
```

---

## Phase 2 — Run PRD (End-to-End)

This runs Phase 2.1 + 2.2 + 2.3 in sequence.

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

## Phase 2.1 — Generate PRD (v0.1)

```text
Use @docs/workflow/phase-2-1-prd-generate.md
@docs/specs/<pages|features>/spec-<WF-ID>-<slug>.md

Generate PRD v0.1 in:
docs/prds/prd-<WF-ID>-<slug>.md

Stop after writing PRD v0.1 and suggest my next 2 actions.
```

---

## Phase 2.2 — PRD Risk Audit (No Edits)

```text
Use @docs/workflow/phase-2-2-prd-risk-audit.md
@docs/prds/prd-<WF-ID>-<slug>.md

Run a risk audit on the PRD.
Return the required audit output only.
Include: Next 2 actions I should take (choose one).
Do NOT edit any files.
```

---

## Phase 2.3 — Revise PRD + Bump Version

```text
Use @docs/workflow/phase-2-3-prd-revise.md
@docs/prds/prd-<WF-ID>-<slug>.md

Apply audit edits,
bump version (v0.1 → v0.2),
update changelog,
mark Ready for Tasks when stable,
and update docs/logs/decisions.md.

Stop after revising and suggest my next 2 actions.
```

---

## Phase 3 — Run Tasks (End-to-End)

This runs Phase 3.1 + 3.2 + 3.3 in sequence.

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

## Phase 3.1 — Generate Tasks (v0.1)

```text
Use @docs/workflow/phase-3-1-task-generate.md
@docs/prds/prd-<WF-ID>-<slug>.md

Generate tasks v0.1 in:
docs/tasks/task-<WF-ID>-<slug>.md

Stop after writing tasks v0.1 and suggest my next 2 actions.
```

---

## Phase 3.2 — Tasks Review (No Edits)

```text
Use @docs/workflow/phase-3-2-task-review.md
@docs/tasks/task-<WF-ID>-<slug>.md

Run tasks review.
Return the review output only.
Include: Next 2 actions I should take (choose one).
Do NOT edit any files.
```

---

## Phase 3.3 — Revise Tasks + Bump Version

```text
Use @docs/workflow/phase-3-3-task-revise.md
@docs/tasks/task-<WF-ID>-<slug>.md

Apply the review edits,
bump version,
update changelog,
mark Ready for Implementation when stable.
Update @docs/index.md Status to Phase 3 as needed.

Stop after revising and suggest my next 2 actions.
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
