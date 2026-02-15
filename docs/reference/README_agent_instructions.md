# Agent Instruction Files (What / Why / How to Change)

Note: This doc was renamed from `docs/reference/agent_instructions.md` on 2026-02-15. Older logs may reference the old filename.

## Source of Truth

- **SSOT**: `AGENTS.md` (plus any nested `AGENTS.md` under subdirectories you edit).
- If anything conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Tool-specific “adapter” files in this repo

These exist to support specific tools that look for particular filenames/locations:

- **Copilot / Codex in VS Code**: `.github/copilot-instructions.md`
  - Why: Copilot/Codex auto-loads this file as always-on context.
  - Policy: Keep it short and point it to `AGENTS.md` as the SSOT.
  - How to change: edit or delete this file if you want different behavior for Copilot/Codex.

- **Gemini CLI / agents**: `GEMINI.md`
  - Why: Some Gemini setups look for `GEMINI.md` as an agent behavior guide.
  - Policy: It must defer to `AGENTS.md` for workflow/process.
  - How to change: edit or delete if you don’t use Gemini in this repo.

## VS Code settings that affect loading

VS Code’s Chat/Copilot instruction loading can be toggled via settings (names may vary by VS Code version/extension):

- Prefer enabling loading of `AGENTS.md` (and nested `AGENTS.md` files) so the SSOT is always present.
- If you switch to a different agent tool, decide whether it should read:
  - `AGENTS.md` directly,
  - the tool adapter file(s),
  - or its own tool-specific rule file(s) (in which case, add a new adapter that points back to `AGENTS.md`).
