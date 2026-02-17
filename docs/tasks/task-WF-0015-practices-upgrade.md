# WF-0015 — Practices Upgrade Tasks

Artifact: task  
Version: v1.0  
Status: Ready for Implementation  
Last Updated: 2026-02-17

## Task Breakdown (Sequential Order)

### Task 1 — Configure Backend Tooling (MyPy + Ruff)
- **Goal**: Add MyPy and strict Ruff config to backend.
- **Files to modify**: `backend/pyproject.toml`, `backend/uv.lock`.
- **Acceptance Criteria**:
  - `mypy` installed as dev dependency.
  - `[tool.mypy]` configured (ignore missing imports initally).
  - `ruff` configured with stricter rules (W, B, SIM, I).
  - Legacy files excluded if needed (or baseline established).
- **Ref**: PRD Section 4.3 + AD 15.1.

### Task 2 — Configure Frontend Verification
- **Goal**: Ensure frontend lint/build scripts are CI-ready.
- **Files to modify**: `frontend/package.json` (verify scripts).
- **Acceptance Criteria**:
  - `npm run lint` passes (or fixes applied).
  - `npm run build` passes locally (verifies Next.js build).
- **Ref**: PRD Section 4.1.

### Task 3 — Setup GitHub Actions CI Pipeline
- **Goal**: Create the `.github/workflows/ci.yml` pipeline that triggers on push/PR.
- **Files to modify**: `[NEW] .github/workflows/ci.yml`.
- **Acceptance Criteria**:
  - Workflow runs on push to `main` and all PRs.
  - Job 1 (Backend) sets up Python + uv, installs deps, runs checks (stubbed if config missing).
  - Job 2 (Frontend) sets up Node + npm, installs deps, runs lint/build.
  - Caching is enabled for both `uv` and `npm`.
- **Ref**: PRD Section 4.1.

### Task 4 — Setup Pre-Commit Hooks
- **Goal**: Enforce Git hygiene locally.
- **Files to modify**: `[NEW] .pre-commit-config.yaml`.
- **Acceptance Criteria**:
  - Hooks configured: trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files.
  - `pre-commit run --all-files` passes locally.
- **Ref**: PRD Section 4.2.

### Task 5 — Documentation Updates
- **Goal**: Reflect new tooling in project docs.
- **Files to modify**: `AGENTS.md`, `docs/maintenance.md`.
- **Acceptance Criteria**:
  - `AGENTS.md` mentions `pre-commit` expectation.
  - `maintenance.md` explains how to run CI locally (act) or manual checks.
- **Ref**: PRD Section 2 (Documentation).

## Changelog
- v0.1 (2026-02-17): Initial tasks from PRD
