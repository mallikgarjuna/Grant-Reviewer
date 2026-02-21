# Multi-Agent Collaboration Strategy: The "Heavy Lifter vs. Fast Typist" Split

This document defines the recommended strategy for splitting the **Product Engineering Pipeline (WF Workflow)** across multiple AI coding agents with different architectural strengths.

## Why Split Agents?

Different LLM models and agent harnesses excel at different tasks:

1. **Antigravity (Gemini 3.1 Pro)**:
   - *Strengths*: Massive context integration, architectural reasoning, constraint adherence, multi-step autonomous planning.
   - *Best For*: "Reading the whole book" before making a decision. Synthesizing `AGENTS.md` and domain models.
   - *Trade-offs*: Slower Time To First Token (TTFT).

2. **VSCode + Codex (GPT-3.2/4o)**:
   - *Strengths*: Low-latency semantic autocomplete, localized syntax generation, tight inline IDE feedback loops.
   - *Best For*: Writing 50 lines of code *right now* based on the 3 files currently open. Fast syntax generation.
   - *Trade-offs*: Hallucinates global context. Struggles to keep complex `AGENTS.md` rules, phase gates, and old decisions in mind simultaneously, leading to drift if used for architectural planning.

---

## The Recommended Split (Option 1)

To maximize velocity without sacrificing architectural integrity, isolate the "Thinking" from the "Typing."

### 1. Phases 0, 1, 2, and 3 (Planning & Definition)
**Agent**: Antigravity (Gemini)
**Role**: Staff Architect

- Use Antigravity to ingest user goals, cross-reference them against project constraints (`AGENTS.md`, lessons learned), and run the interactive brainstorming phase.
- Let Antigravity generate bulletproof, architecturally sound Specs, PRDs, and the final granular Task Checklist.
- **Output**: A locked, high-quality `docs/tasks/task-WF-XXXX-<slug>.md` file.
- **Cheat Sheet**: See `docs/workflow/how-to-use-workflow-actions.md` — Phase 0, Phase 1, Phase 2 templates.

### 2. Phase 3.1 (Implementation / Inner Loop)
**Agent**: VSCode Codex / Cursor
**Role**: Junior Developer

- Once the Task Checklist is locked, the global "thinking" is done. Switch to your IDE.
- Feed the Task file to your IDE agent. Use it as a high-speed typist to execute the `docs/workflow/phase-3-1-implement-tasks.md` loop (Write code -> Run local tests -> Commit).
- Benefit from zero-latency intellisense and inline file editing.
- **Output**: Sequentially implemented and committed task features on the local branch.
- **Cheat Sheet**: See `docs/workflow/how-to-use-workflow-actions.md` — Phase 3.1 (Implement Only) template.

### 3. Phase 3.2 (Verify & Ship)
**Agent**: Antigravity (Gemini)
**Role**: Staff Architect / Reviewer

- When the IDE agent finishes the task checklist, return control to Antigravity.
- Invoke `docs/workflow/phase-3-2-verify-and-ship.md`.
- Antigravity will review the Git diffs, ensure the IDE agent didn't break global architecture or introduce lint debt, run the test suites, draft the final Walkthrough, and prepare the `Ship it` gate.
- **Output**: A thoroughly verified PR, aligned with the original Phase 1 PRD.
- **Cheat Sheet**: See `docs/workflow/how-to-use-workflow-actions.md` — Phase 3.2 (Verify & Ship) template.
