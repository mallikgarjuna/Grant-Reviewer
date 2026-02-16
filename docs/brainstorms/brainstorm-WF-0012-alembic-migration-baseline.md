# WF-0012 — Alembic Migration Baseline

Artifact: brainstorm  
Version: v0.1  
Status: Draft Complete  
Last Updated: 2026-02-16

## 1. Problem Statement

The backend currently relies on SQLModel metadata initialization without an explicit migration history, which creates risk for schema drift across environments and blocks safe iterative schema changes.

- Primary affected users: backend engineers and reviewers running local/dev/prod deployments.
- Why now: local Postgres setup is in place and needs a migration baseline before future DB changes stack up.

## 2. Desired Outcome

Define a minimal Postgres-only migration foundation so schema changes can be tracked, reviewed, and applied consistently.

- Success means Alembic is initialized and can run `upgrade`/`downgrade` against Postgres.
- MVP should be usable immediately by developers without introducing broad platform changes.

## 3. Target User / Actor

- Primary actor: project maintainers editing SQLModel models and shipping backend changes.
- Secondary actor: contributors onboarding and needing a deterministic DB setup path.

Current pain: no canonical migration runbook and no baseline revision to anchor future changes.

## 4. Rough Idea (Unstructured Thinking)

MVP-fast direction:

1. Initialize Alembic in `backend/` for Postgres only.
2. Configure Alembic env to target project SQLModel metadata.
3. Create first baseline migration representing current schema state.
4. Add concise runbook instructions for creating/running migrations and verification commands.

Keep this narrow and avoid deployment automation or migration policy expansion.

## 5. Constraints

- Database scope: Postgres only; explicitly no SQLite fallback path.
- Scope limit: baseline + first migration + docs/runbook + verification commands.
- Time: keep changes implementable in one focused iteration.
- Dependencies: avoid adding unnecessary packages beyond Alembic support.

## 6. Risks / Unknowns

- Fragile assumption: current model metadata cleanly generates an accurate baseline migration.
- Potential risk: env/config mismatches (`DATABASE_URL`, async/sync driver handling) during Alembic execution.
- Validation needed early: commands for `alembic current`, `history`, `upgrade head`, and rollback behavior.

## 7. MVP Definition

Must exist:

1. Alembic initialized and checked into repo under `backend/`.
2. Baseline revision file created and runnable on Postgres dev DB.
3. Docs/runbook updates with exact local commands.
4. Verification command list with expected pass criteria.

Can wait:

- Multi-environment migration automation.
- Zero-downtime production migration strategies.
- Non-Postgres compatibility.

## 8. Explicit Non-Goals

- No application feature changes beyond migration foundation.
- No schema redesign or domain-model refactors.
- No production release orchestration or CI/CD rollout in this WF.
