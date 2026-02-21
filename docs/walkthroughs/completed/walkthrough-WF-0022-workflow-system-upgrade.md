# Walkthrough: WF-0022 — Workflow System Upgrade (Tier 1)

Date: 2026-02-21

## 1. Goal
Execute the first phase (Tier 1) of the workflow system upgrade to harden phase gates and reduce documentation maintenance debt that caused context-window overflow for AI agents.

## 2. Changes Made
- Downscoped WF-0022's Spec, PRD, and Tasks strictly to Tier 1, deferring Tier 2 and 3 into isolated PRs (upcoming WF-0023, WF-0024) to manage risk.
- **`docs/workflow/phase-*-run-*.md`**: Fixed numbering gaps and standard agent references.
- **`run-lifecycle-interactive.md`**: Fixed typos in the introductory text.
- **`AGENTS.md`**: Removed a duplicate "After each successful push..." line.
- **`how-to-use-workflow-actions.md`**: Stripped out individual sub-phase cheat-sheet prompts. The file now exclusively contains End-to-End phase runners (Phase 0, 1, 2, 3) and Lifecycle runners, enforcing the "Runners are Routers" mental model.

## 3. Verification Performed
- `git diff` review confirmed all changes were strictly markdown documentation fixes.
- `pre-commit run --all-files` successfully enforced EOF newlines and trailing whitespace.
- Links and references in `how-to-use-workflow-actions.md` remain valid and correctly route to the designated runners.

## 4. Next Steps
- Open a Pull Request for PR #1 (WF-0022 Tier 1).
- Start `WF-0023` (Tier 2 Phase 4 Hardening) on a fresh branch originating from main.
