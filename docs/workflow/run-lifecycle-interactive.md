# Full Lifecycle Runner (Interactive)

Reference in chat: `@docs/workflow/run-lifecycle-interactive.md`

## When to Use
- **Complex Features**: High risk, new patterns, or unclear requirements.
- **Strict Oversight**: When you want to review/approve every artifact (PRD, Tasks).
- **Standard Protocol**: This is the default recommended flow.

## Required Inputs
- Title, Type, Slug

## Execution Flow

> **Context Limit Warning**: If context feels heavy after Phase 2, pause and advise the user to start a new chat for Phase 3.
1. **Phase 0 (Ideation)**: Initialize -> **Create Branch** (`git checkout -b wf/WF-XXXX-slug`). (Ref: `@docs/workflow/phase-0-0-start-workflow.md`) + Brainstorm. (Ref: `@docs/workflow/phase-0-1-brainstorm.md`)
   - *Wait for User Signal*
2. **Phase 1 (Definition)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-12-run-planning.md`)
   - *Wait for User Signal*
3. **Phase 2 (Planning)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-12-run-planning.md`)
   - *Wait for User Signal*
4. **Phase 3 (Execution)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-3-run-implement-execution.md`)
   - *Stop*

## How to Invoke
```text
Use @docs/workflow/run-lifecycle-interactive.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the interactive lifecycle.
```
