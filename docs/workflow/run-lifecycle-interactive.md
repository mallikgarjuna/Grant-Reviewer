# Full Lifecycle Runner (Interactive)

Reference in chat: `@docs/workflow/run-lifecycle-interactive.md`

## When to Use
- **Complex Features**: High risk, new patterns, or unclear requirements.
- **Strict Oversignt**: When you want to review/approve every artifact (Spec, PRD, Tasks).
- **Standard Protocol**: This is the default recommmended flow.

## Required Inputs
- Title, Type, Slug

## Execution Flow
1. **Phase 0.0 (Start)**: Initialize -> **Create Branch** (`git checkout -b wf/WF-XXXX-slug`). (Ref: `@docs/workflow/phase-0-0-start-workflow.md`)
   - *Wait for User Signal*
2. **Phase 0.1 (Brainstorm)**: Interactive session. (Ref: `@docs/workflow/phase-0-1-brainstorm.md`)
   - *Wait for User Signal*
3. **Phase 1 (Spec)**: Generate -> Review -> Revise. (Ref: `@docs/workflow/phase-1-run-spec.md`)
   - *Wait for User Signal*
4. **Phase 2 (PRD)**: Generate -> Audit -> Revise. (Ref: `@docs/workflow/phase-2-run-prd.md`)
   - *Wait for User Signal*
5. **Phase 3 (Tasks)**: Generate -> Review -> Revise. (Ref: `@docs/workflow/phase-3-run-task.md`)
   - *Wait for User Signal*
6. **Phase 4 (Implement)**: Code -> Verify -> Walkthrough. (Ref: `@docs/workflow/phase-4-1-implement-tasks.md`)
   - *Stop*

## How to Invoke
```text
Use @docs/workflow/run-lifecycle-interactive.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the interactive lifecycle.
```
