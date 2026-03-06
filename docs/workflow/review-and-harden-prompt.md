<!-- docs/workflow/review-and-harden-prompt.md -->

# Review-And-Harden Prompt

Use this prompt after any workflow phase when you want a single reusable "stress test and fix" pass against the latest artifact without manually selecting the phase-specific review/revise docs.

## Generic Prompt

```text
Take a Senior Principal Software Architect / Engineer review posture.

Use the workflow docs and current branch state to determine the active WF, the latest completed phase artifact, and the correct review/revise sub-phase instructions.
Start from:
- @docs/index.md
- the current WF branch
- the relevant workflow runner/instruction docs for that phase

Your job:
1. Detect which artifact was just produced for the active WF.
2. Run the correct adversarial review gate (Part B / review sub-phase) for that artifact using `main...HEAD`.
3. Be fail-closed and cover all mandatory focus areas for that phase.
4. Do not edit files during Part B.
5. If no findings remain, make no edits.
6. If findings remain, run the correct revise step (Part C / revise sub-phase) and apply only the minimum required fixes.
7. If revisions are made, bump the artifact version/status exactly as the phase rules require and update any required companion docs.
8. End by stating:
   - whether any blocking issues remain
   - whether any non-blocking deltas remain
   - whether the artifact is solid enough to proceed to the next phase

Constraints:
- Use the approved artifact for the current phase as SSOT.
- Do not expand scope beyond the current artifact.
- Keep the review adversarial, concrete, and architecture-first.
- If the workflow docs for the detected phase do not define a review/revise path, say so explicitly and perform the closest valid adversarial review without inventing process.
```

## How To Use

1. Paste the prompt into chat.
2. Replace `@docs/ARTIFACT_PATH_HERE` with the artifact you want to solidify.
3. Keep the rest unchanged.

## Common Artifact Paths

- Brainstorm: `@docs/brainstorms/brainstorm-WF-XXXX-<slug>.md`
- PRD: `@docs/prds/prd-WF-XXXX-<slug>.md`
- Tasks: `@docs/tasks/task-WF-XXXX-<slug>.md`
- Walkthrough: `@docs/walkthroughs/walkthrough-WF-XXXX-<slug>.md`

## Lowest-Friction Chat Usage

After this file exists, the shortest chat prompt is:

```text
Use @docs/workflow/review-and-harden-prompt.md
@docs/ARTIFACT_PATH_HERE
```

The agent should then load this file, use the supplied artifact as SSOT, and run the appropriate review-and-harden pass for the detected phase.
