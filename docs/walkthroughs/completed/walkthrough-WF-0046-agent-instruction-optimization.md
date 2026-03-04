# WF-0046 — Agent Instruction Optimization Walkthrough

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-03-04

## 1. What Changed

Successfully executed a low-risk optimization to consolidate context loaded by AI coding agents.

- **`AGENTS.md` (Project Rules)**: Extracted 3 critical, project-specific behavioral rules from the user-global registry (Wait for Signal, 3-File Limit, TDD Behavior Changes). Kept file strict to its <=45 lines budget limit.
- **`GEMINI.md` (Repo Duplicate)**: Deleted the byte-identical duplicate in the repo root to prevent instruction ambiguity.
- **`~/.gemini/GEMINI.md` (User Global)**: Secured a backup to `/tmp/GEMINI.md.bak`, then trimmed the active global rules down to 7 lines of absolute safety-nets (Sequential tooling, UI Verification, Blocked Single-Question, Acknowledge Heartbeat).
- **Parking Lot**: Logged two deferred enhancements in `docs/parking_lot.md` (hooks-based enforcement and loop-style Phase 3 execution).

## 2. Verification Evidence

This was a non-code task. Verification relied on concrete CLI assertions defined in the PRD and Tasks.

- `wc -l AGENTS.md` → Verified 36 lines (<= 45 requirement met).
- `ls GEMINI.md` → Verified file no longer exists in repo.
- `wc -l ~/.gemini/GEMINI.md` → Verified 7 lines (<= 15 requirement met).
- `ls /tmp/GEMINI.md.bak` → Backup secured prior to trimming.
- `pre-commit run --all-files` → Passed clean on final commit.

## 3. Remaining Risks / Follow-ups

- **Risk**: The 45-line and 15-line limits are currently only enforced via workflow audits instead of hard pre-commit hooks.
- **Next Steps**: Address the deferred parking lot items (P2 #31 and #32) in subsequent maintenance sprints to harden these rules physically via `git` hooks or `Makefile` steps.

## 4. Archiving

- Brainstorm: `docs/brainstorms/brainstorm-WF-0046-agent-instruction-optimization.md` → `docs/brainstorms/completed/`
- PRD: `docs/prds/prd-WF-0046-agent-instruction-optimization.md` → `docs/prds/completed/`
- Tasks: `docs/tasks/task-WF-0046-agent-instruction-optimization.md` → `docs/tasks/completed/`
- Walkthrough: `docs/walkthroughs/walkthrough-WF-0046-agent-instruction-optimization.md` → `docs/walkthroughs/completed/`
