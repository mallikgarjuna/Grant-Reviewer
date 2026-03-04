# WF-0047 — Git Hooks Rule Enforcement

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## Changelog

- v0.1 (2026-03-04): Initial tasks from PRD

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Implement `check_agents_md.py` hook and verify standalone
Goal: Create the Python script to validate `AGENTS.md` line counts, handling the EOF newline constraint.
Slice: tracer-bullet
User Stories: US1
PRD Requirements: FR1, FR2, FR5
Depends on: none
Enables: 3
Parallelizable: no
Files to modify:
- `scripts/hooks/check_agents_md.py` (new)
- `tests/test_hooks/test_check_agents_md.py` (new)
Acceptance Criteria:
- Script exits 0 if a target file is <= 45 lines.
- Script exits 0 if exactly 45 lines + 1 empty EOF newline.
- Script exits 1 with a clear error if > 45 lines.
- Uses only Python standard library.
TDD Plan:
- RED: Write pytest or subprocess-based tests proving the edge cases (<= 45, exactly 45+newline, > 45) fail because script doesn't exist.
- GREEN: Implement `check_agents_md.py` using `sys`, `os`.
- REFACTOR: None.
Verification Steps: Run the added tests via `pytest tests/test_hooks/test_check_agents_md.py` and ensure they pass.
Risks (if any): Off-by-one errors with empty newlines.

### [ ] Task 2 — Implement `check_commit_msg.py` hook and verify standalone
Goal: Create the Python script to validate commit messages against the `WF-XXXX:` prefix and `Merge/Revert` exceptions.
Slice: commit-validation
User Stories: US2, US3
PRD Requirements: FR3, FR4, FR5
Depends on: none
Enables: 3
Parallelizable: yes
Files to modify:
- `scripts/hooks/check_commit_msg.py` (new)
- `tests/test_hooks/test_check_commit_msg.py` (new)
Acceptance Criteria:
- Script reads the commit message file passed as an argument.
- Exits 0 if message starts with `Merge branch` or `Revert`.
- Exits 0 if message matches regex `^WF-\d{4}.*: `.
- Exits 1 with clear error for any other prefix.
- Uses only Python standard library.
TDD Plan:
- RED: Write tests simulating `.git/COMMIT_EDITMSG` file contents (valid WF prefix, Merge branch, invalid prefix). Prove they fail.
- GREEN: Implement `check_commit_msg.py` using `sys`, `re`.
- REFACTOR: None.
Verification Steps: Run `pytest tests/test_hooks/test_check_commit_msg.py` and ensure they pass.
Risks (if any): Regex is too strict or too loose for team conventions.

### [ ] Task 3 — Wire scripts into `.pre-commit-config.yaml`
Goal: Integrate both scripts into the local repository pre-commit framework.
Slice: hook-integration
User Stories: US1, US2
PRD Requirements: FR6, FR7
Depends on: 1, 2
Enables: none
Parallelizable: no
Files to modify:
- `.pre-commit-config.yaml`
Acceptance Criteria:
- `check_agents_md.py` is configured as a `repo: local` hook for the `pre-commit` stage, targeting `AGENTS.md`.
- `check_commit_msg.py` is configured as a `repo: local` hook for the `commit-msg` stage.
- Both hooks use `language: python`.
TDD Plan: N/A (configuration change).
Verification Steps:
- Run `pre-commit run --all-files` and ensure no errors are thrown by the new hooks.
- Trigger a dummy failing commit message hook manually: `echo "bad commit" > .git/COMMIT_EDITMSG && pre-commit run --hook-stage commit-msg check-commit-msg || true` to verify it catches the failure.
Risks (if any): Developers might need to run `pre-commit install --hook-type commit-msg` if they haven't explicitly installed that stage before.
