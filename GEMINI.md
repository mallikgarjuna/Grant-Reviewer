# AI Coding Agent Guidelines (GEMINI.md)

**CRITICAL RULE:** This file (`GEMINI.md`) is DEPRECATED as the source of truth for all rules.

You must IMMEDIATELY read and follow `AGENTS.md`. `AGENTS.md` is the Single Source of Truth for all workflow rules, phase gates, git conventions, avoiding coordination failures, and project-specific gotchas.

## Core Directives for the AI Agent

1. **Read AGENTS.md First:** Before starting any task, proposing any plan, or writing any code, you must read the `AGENTS.md` file in the root of the repository.
2. **Follow Phase Runners:** Never execute a workflow phase without strictly reading and following the runner file in `docs/workflow/`.
3. **Do Not Duplicate Rules Here:** If you are instructed to "remember a rule" or "add a lesson", you must add it to `AGENTS.md` or `docs/lessons.md`. Do NOT add it to this file.
4. **Assume Nothing:** If you are unsure about an architectural approach, stop and ask the user. You are expected to act as a Staff Engineer.

-- END --
*Agent: If you are reading this, stop reading GEMINI.md and go read AGENTS.md.*
