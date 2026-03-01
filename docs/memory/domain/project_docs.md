# Project Documentation

- **2026-03-01**: All new code phrases and agent chat triggers must be added to `docs/reference/code_phrases.md` (the SSOT), not directly to `AGENTS.md`. `AGENTS.md` should remain as tiny as possible.
- **Traceability in outputs**: Workflow runner completion summaries must always include explicit provenance: which files were considered/edited and which skills/instructions were used.
- **Traceability in commits**: Every WF commit message must include both the WF ID and the relevant slug so history is self-describing (e.g., `WF-0012: alembic-migration-baseline - <change>`). (Do not rewrite history; enforce going forward).
- **Push Docs Rule**: Always update `docs/` with all relevant branch work (status/index, decisions, Q&A, prompt history, workflow artifacts) *before* pushing a branch to remote. After every successful push, explicitly confirm that docs/WF artifacts were updated (or state that none were required).
- **WF Boundary Hygiene**: Use a separate branch from `main` (e.g. `task/8.1-lint-baseline-cleanup`) to keep WF phase boundaries clean.
- **Next Actions Formatting**: Before Phase 4 completion, provide end-to-end runner options (e.g. `phase-1-run-spec`). After Phase 4 completion, replace that section with "Next 2 WF ideas/features" from the parking lot.
- **Commit Granularity**: Commits must happen per runner part (Part A output, Part C revision, and Part B only if it has edits) and per phase gate. During Phase 3/4 execution, commit after *each* completed subtask with a short message including the subtask ID.
- **Ignore files rule**: Before any commit, check `.gitignore` behavior via `git status --ignored --short` and prefer narrow unignore rules (`!pattern`) over force-adding files.
