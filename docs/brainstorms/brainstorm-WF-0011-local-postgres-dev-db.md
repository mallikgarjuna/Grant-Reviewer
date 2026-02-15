# WF-0011 — Local Postgres Dev DB

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-02-15

---

## 1. Problem Statement

### Final Decisions
- Primary problem: improve local/prod DB parity so SQL behavior and constraints match production (Q1:B).
- Affected users: all local app contributors (backend + frontend contributors running full flows), not just backend-only work (Q2:B).
- Most painful failure mode: SQLite/Postgres divergence causing late-cycle bugs (Q3:B).
- Why now: MVP is near shipping; we need stable, repeatable local verification (Q4:A).
- Optimization target: high production-fidelity local DB behavior with acceptable setup overhead (Q5:B).

### Problem Definition (Locked for this brainstorm stage)
Local development currently risks behavior drift versus production because SQLite defaults do not faithfully represent Postgres behavior. This creates late discovery of defects and unstable pre-release verification. WF-0011 should establish a local Postgres-first development path that preserves MVP delivery speed while improving correctness confidence.

## 2. Desired Outcome

### Final Decisions
- Primary success signal: any developer can run app flows locally against Postgres in under 15 minutes via documented steps (Q1:A).
- MVP target behavior: Postgres for local runtime plus at least one Postgres-backed verification path (Q2:B).
- SQLite policy: retain SQLite only as an explicit fallback, not the default path (Q3:A).
- Canonical onboarding location: centralize in `backend/README.md` with `.env.example` alignment (Q4:A).
- “Enough data” threshold: require a minimum bootstrap set (active prompt template + at least one call + nodes) with count verification (Q5:A).

### Outcome Definition (Locked for this brainstorm stage)
The workflow should produce a local Postgres-first developer path that is fast to start, straightforward to verify, and safe by default. Success means local contributors can reproduce key app flows without Neon dependency, while preserving a small fallback path and objective “minimum data loaded” checks.

## 3. Target User / Actor

### Final Decisions
- Primary actor: full-stack contributors running end-to-end `/app` flows locally (Q1:B).
- Secondary actor: new contributors who need reliable onboarding (Q2:A).
- Behavior change to drive: move from ad-hoc DB URL usage to local Postgres by default, with Neon only as explicit opt-in (Q3:B).
- Friction priority: address both DB startup and bootstrap completeness, with explicit attention to data bootstrap once DB is reachable (Q4:C).
- Standardization stance: define one blessed local setup path with optional alternatives documented separately (Q5:A).

### Actor Definition (Locked for this brainstorm stage)
WF-0011 serves developers who must run realistic app flows locally with predictable database behavior. The initiative should reduce setup ambiguity for both active contributors and newcomers by providing a default local Postgres path and a reliable bootstrap sequence.

## 4. Rough Idea Exploration

### Final Decisions
- Implementation direction: Docker-based local Postgres with documented environment and bootstrap flow (Q1:A).
- Startup artifact: provide a repository-managed `docker compose` service as the blessed path (Q2:A).
- Config behavior: set local `DATABASE_URL` in `backend/.env` for normal dev; SQLite remains only as fallback when `DATABASE_URL` is unset (Q3:A).
- Bootstrap path: standardize on existing scripts (`ensure_prompt_template.py`, `ingest_call.py`) rather than introducing new data loaders now (Q4:A).
- Verification approach: require a small readiness checklist (connectivity + data counts + one stub review flow) (Q5:A).

### Direction Summary (Locked for this brainstorm stage)
WF-0011 should ship a documented, reproducible local Postgres setup and bootstrap path with minimal new surface area. The emphasis is standardization and confidence, not platform-specific tuning or new migration tooling in this phase.

## 5. Constraints

### Final Decisions
- Delivery window: complete within 2-3 days including documentation and verification (Q1:B).
- Change-size constraint: keep to minimal churn (config, docs, and orchestration only), avoid broad refactors (Q2:A).
- Runtime dependency stance: Docker is the blessed path, with documented fallback guidance for no-Docker environments (Q3:A).
- Safety constraint: local defaults must not point at production Neon; localhost Postgres should be default local target (Q4:A).
- Verification constraint: run targeted checks for changed DB setup paths; defer broad dual-engine CI matrix expansion (Q5:A).

### Constraint Summary (Locked for this brainstorm stage)
The workflow must remain lean and execution-focused: minimal code movement, explicit safety defaults, and practical verification. This keeps the initiative MVP-fast while reducing operational and onboarding risk.

## 6. Risks / Unknowns

### Final Decisions
- Most fragile assumption: existing bootstrap scripts may not always produce sufficient data for all local flows (Q1:B).
- Earliest required validation: fresh setup path (start DB -> bootstrap -> run local flow) to avoid late surprises (Q2:A).
- Highest operational risk: accidental local usage of production Neon credentials (Q3:A).
- Primary drift vectors: combined risk of SQLite-only test coverage and inconsistent local env profile usage (Q4:C).
- Required mitigation in this WF: explicit environment profile rules plus a short verification checklist with expected results (Q5:A).

### Risk Summary (Locked for this brainstorm stage)
WF-0011 should treat bootstrap sufficiency and safe env defaults as first-class concerns. A reproducible setup path is only successful if data readiness and profile discipline are validated together.

## 7. MVP Definition

### Final Decisions
- Minimum ship slice: local Postgres startup path, local `.env` default, bootstrap commands, and verification checklist (Q1:A).
- Mandatory verification: DB connectivity + minimum required seeded entities + one successful local stub review flow (Q2:A).
- Explicit out-of-scope items for this WF: Alembic rollout, broad CI dual-engine matrix, and production DB/provider changes (Q3:A).
- SQLite policy in MVP slice: retain as explicit fallback only, not recommended default (Q4:A).
- Done gate: a new contributor can follow docs and run a working local Postgres-backed review flow without Neon defaulting in local env (Q5:A).

### MVP Scope Summary (Locked for this brainstorm stage)
WF-0011 is a developer-experience reliability slice, not a platform rewrite. It should deliver a complete, verified local Postgres workflow that is safe by default and onboarding-friendly.

## 8. Explicit Non-Goals

### Final Decisions
- Alembic/migration-framework rollout is explicitly deferred to a follow-up WF/task (Q1:A).
- Production Neon/Render configuration changes are out of scope for WF-0011 (Q2:A).
- Full Postgres-only CI enforcement is deferred; this WF keeps targeted local verification (Q3:A).
- ORM/data-access architectural redesign is out of scope (Q4:A).
- Large benchmark-scale data seeding is out of scope; minimum functional bootstrap only (Q5:A).

### Non-Goal Summary (Locked for this brainstorm stage)
WF-0011 is intentionally constrained to local developer workflow reliability. It will not broaden into production infra changes, schema migration strategy, or large-scale data operations.

---

## Brainstorm Outcome Snapshot

### Problem (what and why)
Local dev needs Postgres-first behavior to match production semantics and reduce late defect discovery from SQLite/Postgres drift.

### Intended users
Primary: full-stack contributors running local app flows.  
Secondary: new contributors onboarding to the repo.

### MVP slice for this WF
- One blessed local Postgres startup path (Docker Compose).
- Local `.env` defaults to localhost Postgres (Neon not default for local dev).
- Reuse existing bootstrap scripts for minimum required data.
- Short verification checklist (connectivity + seed counts + one stub review flow).

### Guardrails
- Minimal churn (no broad refactors).
- Keep SQLite as explicit fallback only.
- Keep production config untouched.

### Deferred follow-ups
- Alembic migrations and DB evolution policy.
- Full CI dual-engine strategy (SQLite + Postgres matrix).
- Large representative seed datasets/perf-oriented fixtures.
