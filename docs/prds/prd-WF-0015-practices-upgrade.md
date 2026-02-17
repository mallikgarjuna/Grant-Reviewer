# WF-0015 — Practices Upgrade PRD

Artifact: prd
Version: v1.0
Status: Ready for Tasks
Last Updated: 2026-02-17

## 1. Goal
Implementation of industry-standard engineering practices to ensure code quality, type safety, and automated verification for every PR.

## 2. Requirements (Must Have)
- **CI Pipeline**: GitHub Actions workflow (`ci.yml`) triggering on `push: main`, `pull_request`.
- **Backend Checks**: `uv run ruff check`, `uv run mypy` (new code only/baseline), `uv run pytest`.
- **Frontend Checks**: `npm ci`, `npm run lint`, `npm run build`.
- **Caching**: Actions cache for `uv` and `npm` (Critical for DX).
- **Local Hooks**: `pre-commit` setup for whitespace/large-file checks.
- **Documentation**: Instructions for `pre-commit install` and running CI locally.

## 3. Requirements (Nice to Have)
- **Badge**: Build status badge in README (P2).

## 4. Technical Implementation
### 4.1 GitHub Actions (`.github/workflows/ci.yml`)
- **Triggers**: `push` (branches: main), `pull_request`.
- **Job 1: Backend**
  - Image: `ubuntu-latest`
  - Steps: Checkout, Setup Python (3.12), Install `uv` (with cache), Install Dependencies (`uv sync`), Lint (`ruff check`), Types (`mypy`), Test (`pytest`).
- **Job 2: Frontend**
  - Image: `ubuntu-latest`
  - Steps: Checkout, Setup Node (22), Cache (`~/.npm`), Install (`npm ci`), Lint (`npm run lint`), Build (`npm run build`).

### 4.2 Local Pre-Commit
- **Config**: `.pre-commit-config.yaml`
- **Hooks**: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`.
- **Install**: Developer runs `pip install pre-commit && pre-commit install` once.

### 4.3 Backend Linting Profile
- **Ruff**: Enable `W` (Warning), `B` (Bugbear), `SIM` (Simplify), `I` (Isort), `UP` (Pyupgrade).
- **MyPy**: `ignore_missing_imports = true`, `check_untyped_defs = true`. Exclude `migrations/`.

## 5. Security & Privacy
- **Secrets**: No new secrets required for CI logic itself.
- **Environment**: CI runs in isolated runners. API keys for tests must be mocked or provided via GitHub Secrets if integration tests are enabled. (Constraint: Skip OpenAI tests if key missing).

## 6. Verification Plan
- **Automated**: The CI pipeline *is* the verification.
- **Manual**:
  - Run `act` (if available) or push to a branch and verify Action run.
  - Run `pre-commit run --all-files` locally to verify hooks.
  - Run `uv run mypy .` and confirm it passes (after baselining).

## Changelog
- v0.1 (2026-02-17): Initial PRD from Spec v1.0
