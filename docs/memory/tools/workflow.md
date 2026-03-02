# Agent Workflow

- **Chat hygiene:** If a new chat is warranted (context bloat, WF/branch switch, runner needs clean session), explicitly say so to the user and provide a copy-paste prompt. Workflow rules do not strictly require starting a new chat for every phase, but it is highly recommended (especially moving from Phase 0 to Phase 1) to manage context limits.
- **Skills check:** Before starting a new category of work, check for an existing skill in `~/.agents/skills` (or ask the user to run `ls ~/.agents/skills`) and follow the most relevant `SKILL.md`. This is an always-on habit.
- **Interactive brainstorms:** When a user requests an interactive brainstorm, run it interactively (e.g., asking 5 questions at a time if requested) rather than silently synthesizing answers.
- **Heredoc loop prevention:** Avoid using `cat <<EOF` (heredoc) in terminal commands for large file writes; prefer filesystem tools or `replace_file_content` to prevent looping and token burn. If the system overrides your response repeatedly, stop the loop and ask the user for clarification.
- **2026-03-01 — WF task review rigor:** In adversarial Phase 2 reviews, require one deterministic WF-focused pytest selector contract (e.g., `wf0043_contract_<surface>_<case_id>`) and align every task-level verification command to it to avoid ambiguous `-k` filters.
- **2026-03-01 — Branch cleanup hygiene:** After PR merge/branch deletion, always run `git fetch --prune origin` locally to remove stale remote-tracking refs before reporting branch cleanup status.
