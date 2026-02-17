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

1. **Phase 0.0 (Start)**: Initialize -> **Create Branch** (`git checkout -b wf/WF-XXXX-slug`). (Ref: `@docs/workflow/phase-0-0-start-workflow.md`)
2. **Phase 0.1 (Brainstorm)**: 5 questions in one batch -> Baseline. (Ref: `@docs/workflow/phase-0-1-brainstorm.md`)
3. **Phase 1 (Spec)**: Generate -> Self-Review -> Revise. (Ref: `@docs/workflow/phase-1-run-spec.md`)
4. **Phase 2 (PRD)**: Generate -> Self-Audit -> Revise. (Ref: `@docs/workflow/phase-2-run-prd.md`)
5. **Phase 3 (Tasks)**: Generate -> Self-Review -> Revise. (Ref: `@docs/workflow/phase-3-run-task.md`)
6. **Phase 4 (Implement)**: Code -> Verify -> Walkthrough. (Ref: `@docs/workflow/phase-4-1-implement-tasks.md`)
   - *Stop*

## How to Invoke
```text
Use @docs/workflow/run-lifecycle-auto.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the autonomous lifecycle.
```
