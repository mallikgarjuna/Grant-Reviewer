# How To Use Workflow Actions — Chat Prompt Templates

Replace placeholders like `<WF-ID>` and `<slug>` with your current workflow values.

This is a minimal "cheat sheet" of verbatim chat prompt templates for each workflow action.

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

## Phase 0 — Ideation: Start Workflow + Brainstorm

This runs Phase 0.0 (mint WF ID + branch + register) + Phase 0.1 (brainstorm) in sequence.

```text
Use @docs/workflow/phase-0-run-start-and-brainstorm-ideation.md
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

## Phase 1 — Definition: Brainstorm → PRD

```text
Use @docs/workflow/phase-12-run-planning.md
@docs/index.md
@docs/brainstorms/brainstorm-<WF-ID>-<slug>.md

Run Phase 1 end-to-end for <WF-ID>/<slug> using this unified runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```

---

## Phase 2 — Planning: PRD → Tasks

```text
Use @docs/workflow/phase-12-run-planning.md
@docs/index.md
@docs/prds/prd-<WF-ID>-<slug>.md

Run Phase 2 end-to-end for <WF-ID>/<slug> using this unified runner.
Print what you did in Part A/B/C.
Ask me questions if needed (options + recommendation).
End with two suggested next actions.
```

---

## Phase 3 — Execution: Implement + Verify + Ship

```text
Use @docs/workflow/phase-3-run-implement-execution.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Run Phase 3 end-to-end for <WF-ID>/<slug> using this runner.
Print what you did in Part A/B/C.
Confirm verification evidence before writing the walkthrough.
End with two suggested next actions.
```

---

## Phase 3.1 — Implement Only (Split Agent)

Use when handing the implementation inner loop to a fast-typing IDE agent (e.g., Codex, Cursor).
See [Agent Collaboration Strategy](../reference/agent_collaboration_strategy.md) for the recommended split.

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

## Phase 3.2 — Verify & Ship (Split Agent)

Use when implementation was done by a different agent (e.g., Codex) and you need Antigravity to verify and ship.
See [Agent Collaboration Strategy](../reference/agent_collaboration_strategy.md) for the recommended split.

```text
Use @docs/workflow/phase-3-2-verify-and-ship.md
@docs/index.md
@docs/tasks/task-<WF-ID>-<slug>.md

Assume implementation tasks are DONE.
Run Phase 3.2 (Verify & Ship) for <WF-ID>/<slug> using this runner.
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
