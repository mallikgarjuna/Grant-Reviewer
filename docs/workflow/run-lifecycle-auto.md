# Full Lifecycle Runner (Autonomous)

Reference in chat: `@docs/workflow/run-lifecycle-auto.md`

## When to Use
- **Simple Features**: Low risk, well-defined patterns, minor crud.
- **Trusted patterns**: When you trust the agent to self-correct.
- **Speed**: when you don't want to approve intermediate artifacts.

**WARNING**: Bypasses human review gates. Quality may vary.

## Required Inputs
- Title, Type, Slug

## Execution Flow
**(No stops until implementation is done)**

> **Context Limit Warning**: If context feels heavy after Phase 2, pause and advise the user to start a new chat for Phase 3.

1. **Phase 0 (Ideation)**: Initialize -> **Create Branch** (`git checkout -b wf/WF-XXXX-slug`). (Ref: `@docs/workflow/phase-0-0-start-workflow.md`) + Brainstorm. (Ref: `@docs/workflow/phase-0-1-brainstorm.md`)
2. **Phase 1 (Definition)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-12-run-planning.md`)
3. **Phase 2 (Planning)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-12-run-planning.md`)
4. **Phase 3 (Execution)**: Execute Parts A, B, C exactly. (Ref: `@docs/workflow/phase-3-run-implement-execution.md`)
   - *Stop*

## How to Invoke
```text
Use @docs/workflow/run-lifecycle-auto.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the autonomous lifecycle.
```
