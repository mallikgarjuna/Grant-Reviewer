# Full Lifecycle Runner (Interactive)

Reference in chat: `@docs/workflow/run-lifecycle-interactive.md`

## When to Use
- **Complex Features**: High risk, new patterns, or unclear requirements.
- **Strict Oversignt**: When you want to review/approve every artifact (Spec, PRD, Tasks).
- **Standard Protocol**: This is the default recommmended flow.

## Required Inputs
- Title, Type, Slug

## Execution Flow
1. **Phase 0.0 (Start)**: Initialize branch/files.
   - *Wait for User Signal*
2. **Phase 0.1 (Brainstorm)**: Interactive session.
   - *Wait for User Signal*
3. **Phase 1 (Spec)**: Generate -> Review -> Revise.
   - *Wait for User Signal*
4. **Phase 2 (PRD)**: Generate -> Audit -> Revise.
   - *Wait for User Signal*
5. **Phase 3 (Tasks)**: Generate -> Review -> Revise.
   - *Wait for User Signal*
6. **Phase 4 (Implement)**: Code -> Verify -> Walkthrough.
   - *Stop*

## How to Invoke
```text
Use @docs/workflow/run-lifecycle-interactive.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the interactive lifecycle.
```
