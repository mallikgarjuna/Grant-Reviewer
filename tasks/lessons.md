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
