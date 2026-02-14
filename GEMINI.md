# AI Coding Agent Guidelines (GEMINI.md)

These rules define how an AI coding agent should plan, execute, verify, communicate, and recover when working in a real codebase. Optimize for correctness, minimalism, and developer experience.

---

## Core Operating Principles (Non-Negotiable)

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
- **Correctness over cleverness**: Prefer boring, readable solutions that are easy to maintain.
- **Smallest change that works**: Minimize blast radius; don't refactor adjacent code unless it meaningfully reduces risk or complexity.
- **Leverage existing patterns**: Follow established project conventions before introducing new abstractions or dependencies.
- **Prove it works**: "Seems right" is not done. Validate with tests/build/lint and/or a reliable manual repro.
- **Sequential Tooling**: When using `task_boundary`, always call it first in a sequence of tool calls to ensure the Task View UI reflects the next step before execution begins.
- **Be explicit about uncertainty**: If you cannot verify something, say so and propose the safest next step to verify.

---

## Knowledge Base (KB) Maintenance

- **Persistent Q&A**: Update `docs/logs/qa_history.md` after every user question or technical clarification.
- **Architectural Traceability**: Log every major design decision in `docs/logs/decisions.md`.
- **Walkthroughs**: Every major task (e.g., 1.0, 2.0) must have a walkthrough in `docs/walkthroughs/` documenting the outcome and verification results. Create/update the walkthrough for each Task immediately after completing the Task (e.g., `docs/walkthroughs/walkthrough_task_[ID]_[name].md`).
- **Prompt History**: Log of all user prompts with datetimestamps for traceability and future reference in `docs/logs/prompt_history.md`.

---

## Rules

1. Before writing any code, describe your approach and wait for approval. Always ask clarifying questions before writing any code if requirements are ambiguous.

2. If a task requires changes to more than 3 files, stop and break it into smaller tasks first.

3. After writing code, list what could break and suggest tests to cover it.

4. When there’s a bug, start by writing a test that reproduces it, then fix it until the test passes.

---

## Continuous Improvement & Hyper-Learning

Every user correction or discovered mistake is an opportunity to harden the system. Follow this hierarchy for recording lessons:

### 1. Global Rule Update (GEMINI.md)

Update the `## Lessons` section in this file for **systemic failures** or changes to **AI coordination rules** (e.g., "I should have asked for clarification before editing").

- **Goal**: Prevent the same behavioral mistake across all future tasks.
- **Action**: Add a concise rule to the `## Lessons` section in this file.

### 2. Project-Specific Lessons (docs/lessons.md)

Update `./docs/lessons.md` file for **codebase-specific** pitfalls, architectural quirks, or technical edge cases.

- **Goal**: Maintain local memory of this specific project's "gotchas."
- **Action**: Capture the failure mode, the detection signal, and the prevention rule.

### 3. Execution Requirements

- **Zero-Latency Logging**: Update these logs immediately after a correction or postmortem.
- **Pre-flight Check**: Review `docs/lessons.md` at the start of every session and before major refactors.

---

## Lessons

- I must follow the **Product Engineering Pipeline** (see `## Product Engineering Pipeline` section) for all non-trivial features. Each phase has an explicit **Approval Gate** where I must ask the user for approval and wait for their signal before transitioning to the next phase.
- I must never assume "LGTM" on an artifact means "proceed to the next phase." "LGTM" means "this artifact is approved; now complete the remaining steps of the current phase and request permission to move to the next."
- **CRITICAL**: I must ALWAYS wait for the user's explicit signal BEFORE moving to writing code, changing files, or implementing a feature. This applies even for small changes. I will review this rule on every prompt.
- **Browser Autonomy**: When testing in the Agentic Browser, continue testing without asking for confirmation for individual steps. Only ask for a signal if the environment is NOT a testing environment or if the step involves sensitive/private data.
- **Phase Gate Protocol**: I must strictly respect Phase Gates. Do not create a PRD (Phase 1) until the User explicitly approves Phase 0. Do not create a Task File (Phase 2) until the User explicitly approves the PRD.

---

## Task Lifecycle & Tracking

- **The Project Index**: `docs/index.md` is the **Single Source of Truth**. It contains the **Project Dashboard** (table) linking every Major ID to its PRD, Task File, and Walkthrough.
- **Task Segregation**:
  - **Major Tasks (Non-Trivial)**: Each gets its own file: `docs/tasks/active/task-[ID]-[name].md`. This keeps implementation context isolated and clean.
  - **Minor Tasks (Maintenance)**: Appended to a single `docs/maintenance.md` file to avoid file-system clutter for small fixes.
- **Hierarchical Indexing**: Use a sequential numerical system for all tasks, with sub-tasks always prefixed by their parent Major Task ID:
  - **Major Tasks**: `1.0`, `2.0`, `9.0`, etc. (feature-level)
  - **Sub-tasks**: `9.1`, `9.2`, etc. (parent phases within a major task)
  - **Nested Sub-tasks**: `9.1.1`, `9.1.2`, `9.2.3.1`, etc. (granular implementation steps)
  - **Commits**: Every commit must reference the specific ID (e.g., `feat: [9.1.2] ...`).
- **Checklist First**: Always mark tasks as `[/]` (in-progress) and `[x]` (completed) immediately after the action.
- **Verify Before Proceeding**: Every major task (parent task) must end with a **Verify** subtask that tests the implementation of the entire task. This subtask must pass before moving to the next major task.
- **3-File Limit**: If a task requires changes to more than 3 files, **stop** and break it into smaller sub-tasks before proceeding.
- **Update the Knowledge Base** continuously.
- **Skill & Workflow First**: Check for existing skills in `~/.agents/skills`, `~/.gemini/skills`, `.skills/`, `.agent/skills`, `.agents/skills`, `.claude/skills`, or workflows in `.agent/workflows/` before implementing new logic. If a reusable pattern is discovered, suggest creating a new skill/workflow.
- **Repo-relative links**: Prefer repo-relative paths in artifacts (portable across machines). Use `file:///...` only when a tool requires it for clickability.
- **Archiving Strategy**: To maintain a clean workspace:
  - **Active**: Keep PRDs and Task files under `docs/tasks/active/` during implementation.
  - **Completed**: Once finished, move both files to `docs/tasks/completed/`.
  - **Index Sync**: Immediately update `docs/index.md` links to reflect the new location. This ensures the Dashboard remains a functional portal to the project's history.

---

## Product Engineering Pipeline

For **non-trivial features** (new functional areas, complex refactors, or significant UI changes), follow the **Phase-Gated Workflow** to ensure alignment. Skip this for minor fixes, documentation updates, or simple bugs.

1.  **Phase 0: Ideation (Brainstorming)**
    - **Goal**: Move from a "vague idea" to a "validated design."
    - **Action**: Use the `brainstorming` skill. Ask the user clarifying questions to refine the vision.
    - **Output**: A Design Doc or Brainstorming Log in `docs/brainstorms/`.
    - **Approval Gate**: You MUST ask the user if the brainstorming results are satisfactory and wait for their signal before moving to Phase 1.

2.  **Phase 1: Definition (PRD)**
    - **Goal**: Turn the validated design into formal User Stories and Acceptance Criteria.
    - **Action**: Use the `prd` skill.
    - **Output**: `docs/prds/prd-[TaskID]-[feature-name].md`.
    - **Approval Gate**: You MUST ask the user to review the PRD and wait for their signal (approval) before moving to Phase 2.

3.  **Phase 2: Planning (Roadmap)**
    - **Goal**: Create a granular, chronological implementation checklist.
    - **Action**: Use the `prd-to-tasks` skill.
    - **Output**: Create a new task file `docs/tasks/active/task-[TaskID]-[name].md` and link it in `docs/index.md`.
    - **Approval Gate**: Standard planning approval process as defined in `Workflow Orchestration`.

4.  **Phase 3: Execution & Verification**
    - **Rule**: Follow the generated task list and provide a `walkthrough.md` upon completion.

---

## Git Standards

- **New Branch per major task**: (e.g., `Task 1.0`) (e.g., `git checkout -b task-1-ui-shell`).
- **New Commit per sub-task** and the **whole task**: (e.g., `git commit -m "feat: [2.1] initialize backend assisted by antigravity"`).
- Include the corresponding **task or sub-task number** and "**assisted by antigravity**" in every commit message.
- **Message Format**: Commits must start with a conventional prefix (feat:, fix:, chore:, docs:) and include the task number and the assisted tag:
  - Format: `prefix: [Task#] description assisted by antigravity`
  - Example: `feat: [7.1] add openai keys to config assisted by antigravity`
- **Force Add Logs**: Since `docs/` is critical for history, use `git add -f` if it is accidentally caught by ignore patterns.

## Git and Change Hygiene (If Applicable)

- Keep commits atomic and describable; avoid "misc fixes" bundles.
- Don't rewrite history unless explicitly requested.
- Don't mix formatting-only changes with behavioral changes unless the repo standard requires it.
- Treat generated files carefully:
  - only commit them if the project expects it.

---
