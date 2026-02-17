# WF-0015 — Practices Upgrade Spec

Artifact: spec
Version: v1.0
Status: Ready for PRD
Last Updated: 2026-02-17

## 1. Purpose
Upgrade the repository's engineering practices to industry standards by implementing automated Continuous Integration (CI), strict code quality checks (linting/typing), and Git hygiene hooks. This prevents regression and ensures a high quality bar for the MVP launch.

## 2. User / System Context
- **Developers**: Interaction via `git push`, `gh pr create`, and local `pre-commit` hooks.
- **System**: GitHub Actions runner executes checks on every code change.
- **Workflow**: Blocks merging of PRs if checks fail.

## 3. Core Behavior
1.  **Local Safety**: `pre-commit` hooks catch basic errors (trailing whitespace, large files) before commit execution.
2.  **Pull Request Safety**: GitHub Actions workflow (`ci.yml`) runs on every PR and push to `main`.
    -   **Backend**: Setup Python + `uv`. Installs dependencies via `uv sync`. Runs `ruff check` (lint), `mypy` (types), and `pytest`.
    -   **Frontend**: Setup Node. Installs dependencies via `npm ci`. Runs `npm run lint` and `npm run build`.
3.  **Strict Mode**:
    -   Backend enforces type safety (MyPy) on new code.
    -   Frontend enforces React hooks rules and build validity.

## 4. In Scope
-   **.github/workflows/ci.yml**: The standard CI pipeline using `actions/setup-python`, `astral-sh/setup-uv`, and `actions/setup-node`.
-   **.pre-commit-config.yaml**: Local git hooks.
-   **backend/pyproject.toml**: Add `[tool.mypy]` config and update `[tool.ruff]`.
-   **backend/uv.lock**: Update lockfile for new dev dependencies.
-   **frontend/package.json**: Verify lint scripts.
-   **Documentation**: Update `AGENTS.md` and `docs/maintenance.md` with setup instructions.

## 5. Out of Scope
-   **Deployment automation** (`cd.yml`): Deployment integration is separate.
-   **Sentry/Monitoring**: Defer to P2 (WF-00XX).
-   **Dependabot**: Defer to future maintenance.

## 6. Data & Dependencies
-   **Tools (New)**: `pre-commit` (pip/brew), `mypy`.
-   **CI Environment**: `ubuntu-latest`.
-   **Secrets**: `OPENAI_API_KEY` (required for `scripts/` tests).
    -   *Constraint*: Integration tests hitting OpenAI APIs will be skipped in CI or require repo secrets. Unit tests must be mocked.

## 7. Edge Considerations
-   **Legacy Code Debt**: Strict checks on `backend/app` will be noisy.
    -   *Strategy*: Use `exclude` in `pyproject.toml` or `per-file-ignores` to grandfather existing files if errors > 50. Prefer fixing "easy" wins (unused imports) but ignore deep type errors on legacy code initially.
-   **CI Secrets**: Integration tests needing DB/API keys must be skipped if secrets are missing.

## Changelog
- v0.1 (2026-02-17): Initial spec from brainstorm
- v1.0 (2026-02-17): Added explicit CI action steps; clarified legacy code strategy; marked Ready for PRD
