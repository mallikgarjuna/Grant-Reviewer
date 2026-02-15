# WF-0011 — Local Postgres Dev DB Spec

Artifact: spec
Version: v0.1
Status: Draft
Last Updated: 2026-02-15

## 1. Purpose

Establish a local Postgres-first development workflow so local behavior matches production DB semantics more closely, reduces SQLite/Postgres drift risk, and improves confidence in MVP verification.

## 2. User / System Context

Primary users are full-stack contributors running local `/app` flows, with new contributors as a secondary audience for onboarding consistency. The backend currently supports `DATABASE_URL` with SQLite fallback; this spec defines the expected local operating standard and verification expectations without changing production infrastructure.

## 3. Core Behavior

Developers should be able to:
- start a local Postgres instance using one blessed path,
- configure local backend env to use localhost Postgres by default,
- bootstrap minimum required application data using existing scripts,
- verify readiness using a short checklist (connectivity, minimum data counts, and one stub review flow).

## 4. In Scope

- Define one blessed local Postgres startup path (Docker Compose-based).
- Define local environment defaults that point to localhost Postgres, not Neon.
- Keep SQLite available only as explicit fallback when `DATABASE_URL` is unset.
- Reuse existing bootstrap scripts (`ensure_prompt_template.py`, `ingest_call.py`) for minimum local data setup.
- Define minimum data readiness criteria (active prompt template + at least one ingested call + nodes).
- Add/update canonical developer documentation (`backend/README.md` and `.env.example`) for setup and verification.
- Include one Postgres-backed local verification path that proves end-to-end stub review flow works.

## 5. Out of Scope

- Production Neon/Render configuration or deployment changes.
- Alembic adoption or broader schema migration strategy changes.
- Full SQLite/Postgres CI test-matrix rollout.
- ORM/repository architecture redesign.
- Large benchmark/performance seed datasets.

## 6. Data & Dependencies

- Local dependency: Docker runtime for blessed path.
- Database engine: local PostgreSQL instance for default development path.
- Existing backend dependency path: SQLModel + SQLAlchemy engine via `DATABASE_URL`.
- Existing bootstrap dependencies: backend scripts in `backend/scripts/`.
- Existing safety dependency: local `.env` hygiene to avoid production Neon credentials during normal local development.

## 7. Edge Considerations

- Local Postgres connection configuration must be explicit for local SSL behavior to avoid startup confusion.
- Contributors without Docker need documented fallback guidance (secondary path, not primary).
- Bootstrap sufficiency can drift over time; readiness checks should verify minimum required entities, not just DB connectivity.
- Some tests may still validate SQLite paths only; local verification must explicitly include at least one Postgres-backed functional flow.
- Documentation must clearly separate local profiles from production secrets to reduce accidental data writes.

## Changelog

- v0.1 (2026-02-15): Initial spec from brainstorm
