# Workflow Runner — Lifecycle (Autonomous)

Reference in chat: `@docs/workflow/lifecycle-run-auto.md`
Do NOT modify this file during execution.

## When to Use
- **Simple Features**: Low risk, well-defined patterns, minor crud.
- **Trusted patterns**: When you trust the agent to self-correct.
- **Speed**: when you don't want to approve intermediate artifacts.

**WARNING**: Faster than interactive mode, but it must still respect mandatory gates from downstream runners (including no-edit review gates and explicit user-approval checkpoints).

## Required Inputs
- Title, Type, Slug

## Execution Flow
**(No discretionary stops between phases; mandatory downstream gates still apply)**

> **Context Limit Warning**: If context feels heavy after Phase 2, pause and advise the user to start a new chat for Phase 3.
>
> **Router Rule**: This file orchestrates only. Use phase runners as the source of truth; do not restate or override sub-phase instructions.

1. **Phase 0 (Ideation)**: Execute end-to-end via `@docs/workflow/phase-0-run-ideation.md`.
2. **Phase 1 (Definition)**: Execute via `@docs/workflow/phase-1-2-run-planning.md` with Phase ID `1`.
3. **Phase 2 (Planning)**: Execute via `@docs/workflow/phase-1-2-run-planning.md` with Phase ID `2`.
4. **Phase 3 (Execution)**: Execute via `@docs/workflow/phase-3-run-execution.md` (which routes Part B to 3.2 and Part C to 3.3).
   - *Stop*

## Safety Guardrails
- Respect all no-edit review gates defined by phase runners.
- Do not skip required user-approval checkpoints in downstream runners.
- If a phase runner reports blocking ambiguity, stop and ask the user before continuing.

## How to Invoke
```text
Use @docs/workflow/lifecycle-run-auto.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the autonomous lifecycle.
```
