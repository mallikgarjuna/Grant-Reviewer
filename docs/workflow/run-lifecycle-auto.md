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

1. **Phase 0.0 (Start)**: Initialize.
2. **Phase 0.1 (Brainstorm)**: 5 questions in one batch -> Baseline.
3. **Phase 1 (Spec)**: Generate -> Self-Review -> Revise.
4. **Phase 2 (PRD)**: Generate -> Self-Audit -> Revise.
5. **Phase 3 (Tasks)**: Generate -> Self-Review -> Revise.
6. **Phase 4 (Implement)**: Code -> Verify -> Walkthrough.
   - *Stop*

## How to Invoke
```text
Use @docs/workflow/run-lifecycle-auto.md
Title: <Title>
Type: <feature>
Slug: <slug>

Run the autonomous lifecycle.
```
