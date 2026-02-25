# Knowledge Base & Project Structure

This guide outlines directory structure, Zero-Latency logging requirements, and reference artifacts.

## Key Directories

- `backend/`: application code and scripts
- `frontend/`: React components and UI code
- `docs/`: documentation + task tracking (SSOT: `docs/index.md`)
- `docs/guides/`: detailed agent instructions (workflow, engineering standards, etc.)
- If missing, create at minimum: `docs/index.md`, `docs/maintenance.md`, `docs/lessons.md`, `docs/logs/qa_history.md`, `docs/logs/decisions.md`, `docs/logs/prompt_history.md`

## Knowledge Base Maintenance (Always-On)

Use repo-relative paths (don’t require machine-specific `file:///...` links).

- Q&A / clarifications: `docs/logs/qa_history.md` (log conceptual/clarification questions when asked)
- Architectural decisions: `docs/logs/decisions.md`
- Prompt history (datetimestamps): `docs/logs/prompt_history.md`
- WF brainstorming notes: `docs/brainstorms/brainstorm-<WF-ID>-<slug>.md`
- WF tasks list: `docs/tasks/task-<WF-ID>-<slug>.md`
- WF walkthrough: `docs/walkthroughs/walkthrough-<WF-ID>-<slug>.md`
- Legacy (pre-WF) artifacts remain in `docs/brainstorms/`, `docs/walkthroughs/`, `docs/tasks/`, and `docs/prds/` with their existing Task ID naming.

Update these immediately after decisions/clarifications ("zero-latency logging").
