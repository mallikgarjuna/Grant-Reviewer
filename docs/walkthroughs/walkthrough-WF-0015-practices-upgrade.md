# Walkthrough - WF-0015 Practices Upgrade

**Goal**: Upgrade engineering practices to industry standards (CI/CD, Strict Linting, Pre-commit).

## Changes

### 1. Backend Tooling
- **MyPy**: Validation enabled (baseline established).
- **Ruff**: Stricter rules (`W`, `B`, `SIM`, `I`).
- **Configuration**: `pyproject.toml` updated. `backend/app` excluded from strict typing to manage legacy debt (AD 15.1).

### 2. Frontend Verification
- **Lint**: `npm run lint` passing.
- **Build**: `npm run build` passing.

### 3. CI Pipeline
- **GitHub Actions**: `.github/workflows/ci.yml` installed.
- **Triggers**: Push to `main`, Pull Requests.
- **Jobs**: Backend (Python 3.12, UV) & Frontend (Node 22, NPM). Caching enabled.

### 4. Git Hooks
- **Pre-commit**: Installed `.pre-commit-config.yaml`.
- **Checks**: Trailing whitespace, End of file, Check YAML, Large files.

## Verification Results

### Automated Checks
- **Backend**: `uv run ruff check` (Clean), `uv run mypy` (Clean).
- **Frontend**: `npm run lint` (Clean), `npm run build` (Clean).
- **Hooks**: `pre-commit run --all-files` (Clean).

### Manual Verification
- Verified local execution of all check commands.
- Verified hooks install via `pip install pre-commit`.

## Next Steps
- Merge via PR.
- CI will trigger on first push to `main` (or PR).
