# Full Lifecycle Runner (Interactive)

Reference in chat: `@docs/workflow/run-lifecycle-interactive.md`

## When to Use
- **Complex Features**: High risk, new patterns, or unclear requirements.
- **Strict Oversight**: When you want to review/approve every artifact (Spec, PRD, Tasks).
- **Standard Protocol**: This is the default recommended flow.

## Required Inputs
- Title, Type, Slug

## Execution Flow

> **Context Limit Warning**: If context feels heavy after Phase 3, pause and advise the user to start a new chat for Phase 4.
1. **Phase 0.0 (Start)**: Initialize -> **Create Branch** (`git checkout -b wf/WF-XXXX-slug`). (Ref: `@docs/workflow/phase-0-0-start-workflow.md`)
   - *Wait for User Signal*
2. **Phase 0.1 (Brainstorm)**: Interactive session. (Ref: `@docs/workflow/phase-0-1-brainstorm.md`)
   - *Wait for User Signal*
3. **Phase 1 (Spec)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-123-run-planning.md`)
   - *Wait for User Signal*
4. **Phase 2 (PRD)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-123-run-planning.md`)
   - *Wait for User Signal*
5. **Phase 3 (Tasks)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-123-run-planning.md`)
   - *Wait for User Signal*
6. **Phase 4 (Implement)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-4-run-implement.md`)
   - *Stop*

## How to Invoke
```text
Use @docs/workflow/run-lifecycle-interactive.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the interactive lifecycle.
```
