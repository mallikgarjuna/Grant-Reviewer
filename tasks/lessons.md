# Project Lessons

## Stage 3 Learnings

### L1: sys.path for Script Imports
**Issue**: `ModuleNotFoundError` when running scripts from `/backend/scripts/`.
**Fix**: Add `sys.path.insert(0, str(Path(__file__).parent.parent))` at top of scripts.
**Prevention**: Always add path manipulation in scripts that import from `app/`.

### L2: SQLModel Session Lifecycle
**Issue**: `DetachedInstanceError` when accessing entity attributes after `session.close()`.
**Fix**: Capture IDs into a dict before closing session.
**Prevention**: Never access model attributes after session is closed.

### L3: In-Memory DB Persistence
**Issue**: SQLite in-memory DB resets when new session is created, causing UNIQUE constraint errors on re-seed.
**Fix**: Don't re-seed; reuse existing session for related tests.
**Prevention**: Design tests to share one seeded database instance.

### L4: Call Definition Filename Convention
**Convention**: `{agency}_{program}_{year}_{stage}.yaml`
**Example**: `erc_cog_2026_full.yaml`, `nwo_vici_2026_pre.yaml`
**Reference**: See `backend/data/calls/README.md` for full documentation.

### L5: Task File Updates During Execution
**Issue**: Updated internal artifact `task.md` but forgot to update the project task file `tasks/task-X.0-*.md`.
**Fix**: After each subtask completion, update the project task file (not just internal artifacts).
**Prevention**: Always update `tasks/task-X.0-*.md` with `[x]` checkmarks as subtasks complete. Also update `tasks/index.md` when task status changes.

### L6: Brainstorming Log Naming Convention
**Issue**: Brainstorming logs were created without a task ID in the filename.
**Fix**: Rename brainstorming log files to include the task ID.
**Prevention**: For each major task, name Phase 0 brainstorming logs like `knowledge_base/logs/brainstorming-[TaskID]-[slug].md`.

### L7: Phase 3 Commit Granularity
**Issue**: Phase 3 implementation progressed without commits at each completed subtask boundary (e.g., `7.1`, `7.2`).
**Fix**: Commit after each completed Phase 3 subtask with a short, scoped message that includes the subtask ID.
**Prevention**: Treat each subtask as a commit checkpoint during implementation; avoid batching multiple completed subtasks into one commit.
