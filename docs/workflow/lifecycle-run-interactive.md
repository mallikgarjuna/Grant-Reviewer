# Workflow Runner — Lifecycle (Interactive)

Reference in chat: `@docs/workflow/lifecycle-run-interactive.md`
Do NOT modify this file during execution.

## When to Use
- **Complex Features**: High risk, new patterns, or unclear requirements.
- **Strict Oversight**: When you want to review/approve every artifact (PRD, Tasks).
- **Standard Protocol**: This is the default recommended flow.

## Required Inputs
- Title, Type, Slug

## Execution Flow

> **Context Limit Warning**: If context feels heavy after Phase 2, pause and advise the user to start a new chat for Phase 3.
>
> **Router Rule**: This file orchestrates only. Use phase runners as the source of truth; do not restate or override sub-phase instructions.
1. **Phase 0 (Ideation)**: Execute end-to-end via `@docs/workflow/phase-0-run-ideation.md`.
   - *Wait for User Signal*
2. **Phase 1 (Definition)**: Execute via `@docs/workflow/phase-1-or-2-run-planning.md` with Phase ID `1`.
   - *Wait for User Signal*
3. **Phase 2 (Planning)**: Execute via `@docs/workflow/phase-1-or-2-run-planning.md` with Phase ID `2`.
   - *Wait for User Signal*
4. **Phase 3 (Execution)**: Execute via `@docs/workflow/phase-3-run-execution.md` (which routes Part B to 3.2 and Part C to 3.3).
   - *Stop*

## Safety Guardrails
- Respect all no-edit review gates defined by phase runners.
- Do not bypass adversarial Part B gates delegated via `@docs/workflow/util-adversarial-diff-audit.md`.
- Do not skip required user-approval checkpoints in downstream runners.
- If a phase runner reports blocking ambiguity, stop and ask the user before continuing.
- Do not advance to the next phase unless the current phase's commit gate is satisfied (including per-part commit handoffs required by downstream runners).

## How to Invoke
```text
Use @docs/workflow/lifecycle-run-interactive.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the interactive lifecycle.
```
