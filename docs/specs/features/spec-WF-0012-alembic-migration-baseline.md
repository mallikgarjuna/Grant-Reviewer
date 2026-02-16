# WF-0012 — Alembic Migration Baseline Spec

Artifact: spec  
Version: v0.1  
Status: Draft  
Last Updated: 2026-02-16

## 1. Purpose

Establish a Postgres-only Alembic migration baseline for the backend so schema evolution is versioned, reproducible, and safe to operate across environments.

## 2. User / System Context

- Maintainers and contributors evolve SQLModel-backed schema in `backend/app/models`.
- Local development and integration environments use Postgres.
- The project currently needs a migration chain anchor before introducing further schema changes.

## 3. Core Behavior

1. Alembic is initialized in `backend/` with project-aware configuration.
2. Alembic environment targets the existing SQLModel metadata.
3. A first baseline migration revision is generated and checked in.
4. Team can run documented commands to inspect, apply, and roll back migrations on Postgres.

## 4. In Scope

- Alembic scaffolding and configuration for backend Postgres usage.
- First baseline revision file.
- Command-level runbook updates in docs.
- Verification commands for migration lifecycle basics.

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

## 7. Edge Considerations

- Async-vs-sync DB URL handling in Alembic env can break migration runs if not normalized.
- Baseline revision should be stable and reviewable; auto-generated output may require cleanup.
- Developer command ergonomics should avoid hidden prerequisites.

## Changelog

- v0.1 (2026-02-16): Initial spec from brainstorm
