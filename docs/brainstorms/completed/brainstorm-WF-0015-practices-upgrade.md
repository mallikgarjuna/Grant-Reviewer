# Brainstorm: WF-0015 Practices Upgrade

**Date**: 2026-02-17
**Status**: Phase 0 (Brainstorm)

## Goal
Review and upgrade engineering practices to "Industry Standard" (Safely). Establish robust CI/CD, strict linting, and automated verification without breaking existing workflows or blocking MVP progress.

## Audit Findings (Gap Analysis)

| Category | Current State | Industry Standard | Gap |
| --- | --- | --- | --- |
| **CI/CD** | None (Manual scripts). | CI on Push/PR (Lint, Test, Build). | **Critical**. No automated gate. |
| **Linting (Backend)** | Ruff (Basic: E4, E7, F, I). | Ruff (Strict: +W, SIM, N) + MyPy (Type Check). | Weak linting, no type safety check. |
| **Linting (Frontend)** | ESLint (Next.js default). | ESLint + Prettier + TSC (Check). | Acceptable, but could be stricter. |
| **Git Hygiene** | Manual `git status` checks (L17). | Pre-commit hooks (Husky / pre-commit). | Manual process is error-prone. |
| **Branching** | Local Merge (Legacy) -> PR (New). | GitHub Protection Rules + PR Checks. | PR flow is now adopted, but unenforced by code. |
| **Testing** | `pyproject.toml` has `pytest`. | Automated Pytest in CI. | Automation missing. |

## Proposed Upgrades (Scope)

### 1. GitHub Actions (CI)
 Create `.github/workflows/ci.yml` to run checks on `push` to `main` and all `pull_request`s.
- **Backend Job**: `uv run ruff check`, `uv run pytest`.
- **Frontend Job**: `npm run lint`, `npm run build`.

### 2. Strict Backend Linting (Safe Adoption)
- Add `mypy` to dev dependencies.
- Add `[tool.mypy]` to `pyproject.toml` (start with `ignore_missing_imports = true` to avoid noise).
- Expand `ruff` rules slightly (`W` for warnings, `C90` for complexity) but use `per-file-ignores` if legacy code is noisy. **Policy**: Strict on new code, lenient on old.

### 3. Pre-Commit Hooks
- Add `.pre-commit-config.yaml` using `pre-commit` framework (standard for Python/mixed repos).
- Hooks: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files` (replaces L17 manual check).

### 4. Documentation
- Update `AGENTS.md` and `docs/maintenance.md` to reflect new tooling commands (`pre-commit install`).

## Risks & Mitigation
- **Risk**: Strict linting breaks existing code.
  - **Mitigation**: Fix "easy" errors. Add `# type: ignore` or `noqa` for hard ones to establish a "clean" baseline without rewriting logic.
- **Risk**: CI is slow.
  - **Mitigation**: Use `uv` caching (fast). Next.js build caching.

## Roadmap
1. **Phase 1 (Spec)**: Define CI jobs and exact lint rules.
2. **Phase 2 (PRD)**: (Skip? It's purely technical. Maybe merge with Spec). -> Actually, keep it light.
3. **Phase 3 (Tasks)**: Implementation steps.
4. **Phase 4**: Execute.
