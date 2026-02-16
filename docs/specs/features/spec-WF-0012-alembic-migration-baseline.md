# WF-0012 — Alembic Migration Baseline Spec

Artifact: spec  
Version: v0.2  
Status: Ready for PRD  
Last Updated: 2026-02-16

## 1. Purpose

Establish a Postgres-only Alembic migration baseline for the backend so schema evolution is versioned, reproducible, and safe to operate across environments.

## 2. User / System Context

- Maintainers and contributors evolve SQLModel-backed schema in `backend/app/models`.
- Local development and integration environments use Postgres.
- The project currently needs a migration chain anchor before introducing further schema changes.

## 3. Core Behavior

1. Alembic is initialized in `backend/` with project-aware configuration.
2. Alembic environment targets the existing SQLModel metadata source used by the app.
3. A first baseline migration revision is generated and checked in.
4. Team can run documented commands to inspect, apply, and roll back migrations on Postgres.

Baseline definition:
- The first migration is an initial schema revision for the current SQLModel state.
- The revision is the only root migration (`down_revision = None`) for this workflow.

## 4. In Scope

- Alembic scaffolding and configuration for backend Postgres usage.
- First baseline revision file.
- Runbook updates in docs that explain setup and migration command usage.
- Verification commands for migration lifecycle basics and expected outcomes.

## 5. Out of Scope

- SQLite migration support.
- CI/CD production deployment automation for migrations.
- Schema redesign unrelated to migration baseline.
- Advanced zero-downtime migration patterns.

## 6. Data & Dependencies

- DB dependency: PostgreSQL (dev/local and production class).
- Backend model source: SQLModel metadata from app domain models.
- Environment dependency: `DATABASE_URL` configured to Postgres.
- Tooling dependency: Alembic runtime/config files under `backend/`.
- Documentation dependency: update existing backend/runbook docs rather than creating duplicate guidance files.

## 7. Edge Considerations

- Async-vs-sync DB URL handling in Alembic env can break migration runs if not normalized.
- Baseline revision should be stable and reviewable; auto-generated output may require cleanup.
- Developer command ergonomics should avoid hidden prerequisites.
- Local DB drift risk: existing developer databases may need reset/stamp guidance before upgrade.

## 8. Acceptance Criteria

1. Alembic config exists and resolves project metadata without manual path hacks.
2. Baseline migration file is present and runnable on Postgres dev DB.
3. `alembic upgrade head` succeeds on a clean Postgres DB.
4. `alembic downgrade -1` and re-upgrade flow succeeds for the baseline.
5. Docs include exact commands for initialize/check/apply/rollback paths.

## 9. Verification Commands

From `backend/`:

1. `uv run alembic current`
2. `uv run alembic history --verbose`
3. `uv run alembic upgrade head`
4. `uv run alembic downgrade -1`
5. `uv run alembic upgrade head`

## Changelog

- v0.1 (2026-02-16): Initial spec from brainstorm
- v0.2 (2026-02-16): Applied review edits for baseline definition, acceptance criteria, and verification command clarity
