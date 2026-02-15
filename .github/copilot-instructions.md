# Why this file exists

This repo includes `.github/copilot-instructions.md` because GitHub Copilot Chat / OpenAI Codex in VS Code will automatically load it as always-on agent instructions.

`AGENTS.md` is the **Source of Truth** for workflow and conventions. This file is a **tool-specific adapter** whose job is to point Copilot/Codex back to `AGENTS.md` (and keep the instructions short).

If you use a different coding agent tool that has its own instruction mechanism, either:
- disable/remove this file for that workflow, or
- keep it and ensure the tool is configured to prioritize `AGENTS.md` (see `docs/reference/README_agent_instructions.md`).

---

ALWAYS read `AGENTS.md` first and follow it as the Source of Truth for this repo (workflow phases, conventions, boundaries, verification, and docs logging).

If anything conflicts, `AGENTS.md` wins over all other instruction files (including `README.md`, `GEMINI.md`, and any “copy” files).

When working in a subdirectory, also read any nested `AGENTS.md` files that apply to files you touch (more specific scopes override broader ones).

Before starting a *new type of task* (e.g., migrations, accessibility audits, prompt engineering, API integration), **check whether a relevant agent skill exists**:
- If you have shell access: run `ls ~/.agents/skills` (and open the most relevant `SKILL.md`).
- If you don’t have shell access: ask the user to list available skills or to run that command for you.

Notes:
- `Dont-read-this-AGENTS copy.md` is not the Source of Truth.
