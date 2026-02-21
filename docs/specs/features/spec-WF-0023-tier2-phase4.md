# WF-0023 — Tier 2 Phase 4 Runner

Artifact: spec
Version: v1.0
Status: Ready for PRD
Last Updated: 2026-02-21

## 1. Goal
Add formal Part A/B/C verification discipline to Phase 4 (Implementation) and harden the lifecycle runners against context exhaustion and sequence skipping.

## 2. User Stories
- **As an AI Coding Agent**, I need Phase 4 to explicitly tell me to *stop and verify* my work (Part B) before jumping to writing the post-task Walkthrough (Part C), so I don't embed regressions into `main`.
- **As an AI Coding Agent**, I need the auto/interactive lifecycle runners to warn me explicitly about context exhaustion so I know to advise the user to start a new chat midway through a complex features execution.
- **As a Project Maintainer**, I need `workflow preflight` and `verify workflow` to be explicitly defined in docs so agents know what I mean when I use those code phrases.

## 3. Functional Requirements
### Phase 4 Runner (`docs/workflow/phase-4-run-implement.md`)
- **FR1**: Create a new file `docs/workflow/phase-4-run-implement.md`.
- **FR2**: Structure it strictly into `Part A: Task Execution`, `Part B: Verification Gate`, and `Part C: Walkthrough & Ship Gate`.
- **FR3**: Point Part A to use the existing `phase-4-1-implement-tasks.md` logic (which is well-tested for task iteration).
- **FR4**: Require agents to report back after Part B with verification evidence *before* jumping to Part C.

### Lifecycle Runners (`docs/workflow/run-lifecycle-*.md`)
- **FR5**: Update `run-lifecycle-auto.md` to explicitly state `Execute Phase X (Parts A, B, C)` for each step.
- **FR6**: Add a bold context-warning note to both lifecycle files advising the agent to recommend starting a new chat session after Phase 2 or 3 if the context window is getting heavy.

### Glossary Updates (`docs/workflow/README.md`)
- **FR7**: Add a section describing the `verify workflow` definition (Status, Diff, Lint/Build, Pass/Fail Summary).
- **FR8**: Add a section describing the `workflow preflight` definition (Critical review of current WF closure state, artifact synchronization, and next WF readiness).

## 4. Non-Functional Requirements
- **Backward Compatibility**: The existing `how-to-use-workflow-actions.md` already expects `phase-4-run-implement.md` to exist as the orchestrator (with `phase-4-1-implement-tasks.md` as the underlying looping mechanism). We are fulfilling that implicit contract.
- **Tone**: Must match the strict, authoritative "Runners are Routers" tone of the other docs.

## Traceability Statement
- Derived directly from `brainstorm-WF-0023-tier2-phase4.md` v1.0.
