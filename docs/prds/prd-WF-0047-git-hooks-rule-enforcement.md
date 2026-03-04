# WF-0047 — Git Hooks Rule Enforcement

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-04

## Changelog

- v0.1 (2026-03-04): Initial PRD from brainstorm

## 0. User Stories (MVP)

- US1: As a repository maintainer, I want `AGENTS.md` to be mechanically restricted to 45 lines or fewer, so that AI agents do not exceed context limits or break instruction bounds.
- US2: As a repository maintainer, I want commit messages to be mechanically enforced to start with `WF-\d{4}: `, so that all work is explicitly traceable back to a tracking ID.
- US3: As a developer, I want merge and revert commits to be excluded from the prefix rule, so that standard git operations do not fail validation.

## Deferred Stories (Not in MVP)

- As a maintainer, I want these rules enforced in CI (GitHub Actions) so that bypassed local hooks do not poison the `main` branch.

## 1. In Scope

- Python-based local `pre-commit` hooks for `AGENTS.md` line count validation.
- Python-based local `commit-msg` hooks for `WF-XXXX: ` prefix validation.
- Wiring these scripts into `.pre-commit-config.yaml` using `repo: local`.
- Handling trailing newlines properly in line counting.
- Ignoring `Merge branch` and `Revert` commits.

## 2. Out of Scope

- CI pipeline enforcement (GitHub Actions).
- Generic conventional commits checking (`feat:`, `fix:`, etc).
- Validation of any other markdown files or other constraints besides `AGENTS.md`.
- Implementing an entire `Makefile` abstraction layer.

## 3. User / System Flow

- **Happy path 1: Valid File Change**: Developer/Agent edits `AGENTS.md` keeping it under 45 lines. They commit with message `WF-0047: some change`. The `pre-commit` hook (US1) passes. The `commit-msg` hook (US2) passes. Commit succeeds.
- **Happy path 2: Merge Commit**: Developer merges a branch. The `commit-msg` hook sees `Merge branch` and exits 0 immediately (US3). Commit succeeds.
- **Failure path 1: File Too Long**: Developer/Agent bloats `AGENTS.md` to 46 lines. They attempt to commit. `pre-commit` hook runs, counts lines, and exits 1. Commit fails (US1).
- **Failure path 2: Bad Commit Message**: Developer commits valid files with message `fixed typo`. `commit-msg` hook runs, regex `^WF-\d{4}: ` fails to match. Commit fails (US2).

## 4. Functional Requirements

- FR1 (US1): The system shall provide a `check_agents_md.py` script that reads `AGENTS.md` and exits 1 if the line count exceeds 45.
- FR2 (US1): The line counting logic must account for `pre-commit`'s trailing EOF newline (i.e. if the file is exactly 45 text lines plus one trailing newline, it must pass).
- FR3 (US2): The system shall provide a `check_commit_msg.py` script that reads the `.git/COMMIT_EDITMSG` file and exits 1 if the first line does not match the regex `^WF-\d{4}: `.
- FR4 (US3): The `check_commit_msg.py` script must exit 0 immediately if the commit message begins with `Merge branch` or `Revert`.
- FR5 (US1, US2): The hook scripts must use only Python standard library modules (`sys`, `re`, `os`, etc.).
- FR6 (US1, US2): The hooks must be integrated into `.pre-commit-config.yaml` under `repo: local` for the `pre-commit` and `commit-msg` stages respectively.

## 5. Data & API Contracts

- **AGENTS.md Check Contract** (US1, FR1, FR2, FR5):
  - Input: File path passed as an argument by `pre-commit`.
  - Output: Exit 0 if line count <= 45 (excluding trailing EOF newline). Exit 1 with error message otherwise.
- **Commit Message Check Contract** (US2, US3, FR3, FR4, FR5):
  - Input: File path to `.git/COMMIT_EDITMSG` passed by `pre-commit` during the `commit-msg` stage.
  - Output: Exit 0 if match `^WF-\d{4}: ` or starts with `Merge branch`/`Revert`. Exit 1 with error message otherwise.

## 6. Components / Modules

- `scripts/hooks/check_agents_md.py`
  - Responsibilities: Validates line count of provided files against a hardcoded 45 limit.
- `scripts/hooks/check_commit_msg.py`
  - Responsibilities: Validates commit message file against regex and exception list.
- `.pre-commit-config.yaml`
  - Responsibilities: Wires the new local repo hooks into the git workflow.

## 7. Edge Cases

- (US1) `AGENTS.md` is exactly 45 lines but has no trailing newline. (Fix: Should pass, but `end-of-file-fixer` will run first and add it).
- (US1) `AGENTS.md` is exactly 45 lines AND has a trailing newline. (Fix: The script must not count the trailing empty string/newline as line 46).
- (US3) A commit message legitimately starts with `Revert` but is manually constructed. (Fix: Allow it. Standardizing reverts is out of scope).

## 8. Testing Decisions (TDD)

- TDD seams: `check_agents_md.py` and `check_commit_msg.py` can be tested via `subprocess.run` by passing paths to temporary files containing passing/failing content.
- What to mock: No mocking needed. Use real temporary files (`tempfile.NamedTemporaryFile`) to simulate inputs (`AGENTS.md` and `COMMIT_EDITMSG`).
- Tests should live in `backend/tests/` (e.g. `tests/test_hooks/test_git_hooks.py`) or a top-level `tests/` directory if one exists for scripts.

## 9. Telemetry (Minimal)

- Hooks will `print()` clear error messages to stdout/stderr so the developer/agent sees the exact reason for the block in their git output.

## 10. Deferred / Not in MVP

- CI Pipeline enforcement (GitHub Actions blocking PRs).
- Adding custom Makefile commands.

## 11. Open Questions (if any)

- None. Scope is completely bound.
