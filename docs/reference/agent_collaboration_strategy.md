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
- Feed the Task file to your IDE agent. Use it as a high-speed typist to execute the `docs/workflow/phase-3-1-implement-tasks.md` loop (Write code -> Run local tests -> Commit), but only until the next explicit stop boundary is hit.
- Benefit from zero-latency intellisense and inline file editing.
- **Output**: Sequentially implemented and committed task features on the local branch, with a clean handoff if the task plan says to stop or context gets heavy.
- **Cheat Sheet**: See `docs/workflow/how-to-use-workflow-actions.md` — Phase 3.1 (Implement Only) template.

### 3. Phase 3.2 (Verify & Ship)
**Agent**: Antigravity (Gemini)
**Role**: Staff Architect / Reviewer

- When the IDE agent finishes the approved implementation scope for the current session, return control to Antigravity.
- Invoke `docs/workflow/phase-3-2-technical-audit-review.md`.
- Antigravity will review the Git diffs, ensure the IDE agent didn't break global architecture or introduce lint debt, run the test suites, draft the final Walkthrough, and prepare the `Ship it` gate.
- **Output**: A thoroughly verified PR, aligned with the original Phase 1 PRD.
- **Cheat Sheet**: See `docs/workflow/how-to-use-workflow-actions.md` — Phase 3.2 (Verify & Ship) template.

## Optional "Adversarial Review" (Option 2)

If you want Codex's input on high-risk planning phases (Phase 0, 1, or 2), inject it safely into **Part B (Review Gate)** without breaking the pipeline.

1. **In Antigravity:** Run the phase normally (e.g., Phase 1). Antigravity will pause after Part B to ask if you approve the draft before revising (Part C).
2. **In VS Code (Codex):** While Antigravity is paused, point Codex at the exact same review instruction file:
   > "Use `@docs/workflow/phase-1-2-prd-risk-audit.md` to run a critical risk audit on the current PRD draft. Output the findings in chat."
3. **Back to Antigravity:** Paste Codex's findings into Antigravity:
   > "Here is Codex's adversarial review. Merge this feedback into your own Part B feedback, answer the open questions, and proceed to Part C to apply revisions."

*Why this works:* It uses the existing "Part B" architecture as a no-edit review gate, forcing Codex to follow strict project rules rather than hallucinating unstructured criticism.

---
### When Antigravity Does Not Pause (Auto-Pass)
Antigravity's unified runners are designed to automatically proceed to Part C if Part B finds only minor, non-blocking issues.

**If Antigravity finishes Part C and completes the phase before you can run Codex:**
1. **Do not panic:** The artifact is still fully valid.
2. **Run Codex anyway:** You can still run the Codex review on the final Part C artifact:
   > "Use `@docs/workflow/phase-1-2-prd-risk-audit.md` to run a critical risk audit on the finalized PRD."
3. **Handle feedback via a "Point Revision":** If Codex finds a major flaw that Antigravity missed, do *not* run the entire phase again. Instead, paste the Codex feedback back to Antigravity and say:
   > "Codex reviewed your final artifact and found these issues. Please apply a point-revision to the draft to address them, bump the version, and update the changelog."
