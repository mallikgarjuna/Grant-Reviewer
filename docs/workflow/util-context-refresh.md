# Utility Runner — Context Refresh

This file is a workflow instruction.
Reference it in chat (Codex, Antigravity, or any coding agent) using `@docs/workflow/util-context-refresh.md`.
Do NOT modify this file during execution.

---

## Purpose

To reliably transfer context when switching between different AI coding agents (or starting a new session), ensuring the new agent is fully grounded in the current project state, active workflow, and uncompleted tasks.

---

## Required Inputs

- `docs/index.md` (to locate the active WF and its artifacts)
- The active Phase document (e.g., the PRD or Task file, depending on the current phase)

---

## Runner Rules (Strict)

When the user invokes the `"context refresh"` code phrase or references this utility, you MUST execute the following steps in order:

### 1. Read the Dashboard (`docs/index.md`)
- Identify the currently active Workflow (WF-XXXX) that is not marked as `Done`.
- Identify its current Phase (e.g., Phase 1, Phase 2, Phase 3).
- Identify the explicit paths to its artifact files (PRD, Tasks, Walkthrough).

### 2. Read the Active Artifacts
- **If in Phase 1 or 2**: Read the active PRD (`docs/prds/prd-WF-XXXX-<slug>.md`).
- **If in Phase 3**: Read the active Task file (`docs/tasks/task-WF-XXXX-<slug>.md`).
- *Note: You must use the actual file path found in `docs/index.md`.*

### 3. Analyze the State
- Scan the Task file for completed items (`[x]`) vs uncompleted items (`[ ]`).
- Note the exact next uncompleted task in the sequence.

### 4. Output the Context Summary
Print a concise summary to the user containing:
1. **Active Workflow**: WF ID + Title
2. **Current Phase**: (e.g., Phase 3 - Implementation)
3. **Progress**: X/Y tasks completed.
4. **Next Action**: State the exact title and goal of the next uncompleted `[ ]` task.

### 5. Request Permission to Proceed
End your response by asking the user for explicit permission to begin executing the identified next action. Do NOT begin writing code or editing files until the user says "go ahead" or otherwise confirms.

---

## How to Invoke in Chat

Copy and paste this exact prompt into your new coding agent session:

```text
Use @docs/workflow/util-context-refresh.md
@docs/index.md

Execute a "context refresh" to get up to speed on the current project state.
```
