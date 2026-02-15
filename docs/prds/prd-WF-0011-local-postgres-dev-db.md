# WF-0011 — Local Postgres Dev DB PRD

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-02-15

## 1. In Scope

- Add a single blessed local Postgres startup path using `backend/docker-compose.dev.yml`.
- Standardize local backend DB configuration to localhost Postgres by default in local `.env` guidance.
- Keep SQLite as explicit fallback when `DATABASE_URL` is unset.
- Reuse existing bootstrap scripts:
  - `backend/scripts/ensure_prompt_template.py`
  - `backend/scripts/ingest_call.py`
- Define and document minimum local data readiness thresholds:
  - active prompt templates >= 1
  - funding calls >= 1
  - proposal nodes >= 1
- Add/update canonical docs for setup and verification in `backend/README.md` and `backend/.env.example`.
- Define one Postgres-backed verification flow proving stub review creation reaches terminal status.

## 2. Out of Scope

- Production Neon/Render changes.
- Alembic adoption or schema migration framework rollout.
- Full SQLite/Postgres CI matrix.
- ORM/repository refactors.
- Large benchmark seed datasets.
- Full OS-specific native Postgres troubleshooting guides.

## 3. User / System Flow

### Happy path
1. Developer starts local Postgres via `docker compose` using `backend/docker-compose.dev.yml`.
2. Developer configures `DATABASE_URL` in `backend/.env` to local Postgres (`sslmode=disable`).
3. Backend starts successfully using local Postgres.
4. Developer runs bootstrap scripts to ensure required template and call/node data exist.
5. Developer runs local stub review flow (`POST /reviews`) and receives terminal status.
6. Developer confirms readiness checks pass.

### Failure path A: Postgres container unavailable
1. `docker compose up` fails or container exits.
2. Backend cannot connect and readiness checks fail.
3. Developer follows documented recovery (container status, restart, port check).

### Failure path B: Misconfigured `DATABASE_URL`
1. `DATABASE_URL` points to Neon or malformed local URL.
2. Backend either connects to wrong environment or fails startup/query checks.
3. Developer corrects URL to localhost Postgres contract and retries.

### Failure path C: Bootstrap incomplete
1. DB connectivity is healthy, but required rows are missing.
2. Stub review flow fails due to missing template/call data.
3. Developer reruns bootstrap commands and re-checks counts.

## 4. Functional Requirements

- FR1: Repository provides a single compose file for local Postgres startup/stop.
- FR2: Local dev guidance explicitly defines localhost `DATABASE_URL` with `sslmode=disable`.
- FR3: SQLite fallback remains available only when `DATABASE_URL` is unset.
- FR4: Bootstrap workflow uses existing scripts and is documented as required precondition for review flows.
- FR5: Readiness verification includes objective data count checks for required entities.
- FR6: Readiness verification includes one Postgres-backed stub review creation that reaches terminal state.
- FR7: Documentation clearly distinguishes local development env values from production secrets.

## 5. Data & API Contracts

### Environment contract
- Required local variable contract:
  - `DATABASE_URL=postgresql://<user>:<pass>@localhost:5432/<db>?sslmode=disable`
- Recommended local verification mode:
  - `LLM_MODE=stub`

### Data readiness contract
- `prompt_templates`: at least 1 active row.
- `funding_calls`: at least 1 row.
- `proposal_nodes`: at least 1 row.

### Bootstrap contract
- `ensure_prompt_template.py` must succeed without errors.
- `ingest_call.py` must succeed for at least one supported call YAML.

### Review flow validation contract
- A local stub review submission request must return success with terminal review state (`COMPLETED` or `FAILED` with canonical shape).
- Failure responses must remain canonical and actionable (no silent partial success).

### State transitions
- Local DB lifecycle: `not-running -> running -> bootstrapped -> verified`.
- If bootstrap missing: `running -> bootstrap-required`.
- If review flow passes: `bootstrapped -> verified`.

## 6. Components / Modules

- `backend/docker-compose.dev.yml`
  - Local Postgres service definition for dev startup.
- `backend/.env.example`
  - Local DB contract guidance and safe defaults.
- `backend/README.md`
  - Canonical setup/bootstrap/verification instructions.
- `backend/app/db.py`
  - Existing `DATABASE_URL`/fallback behavior (no architectural redesign).
- `backend/scripts/ensure_prompt_template.py`
  - Ensures required template exists.
- `backend/scripts/ingest_call.py`
  - Seeds call + nodes from YAML.

## 7. Edge Cases

- Local machine already uses port 5432.
- Docker unavailable on contributor machine.
- Developer accidentally keeps Neon URL in local `.env`.
- Local DB starts but bootstrap scripts run against wrong target DB.
- Existing tests still pass on SQLite while local Postgres flow fails.

## 8. Telemetry (Minimal)

- No new product telemetry.
- Minimal operational verification evidence captured in walkthrough:
  - commands run,
  - success/failure outcomes,
  - timestamped readiness result.

## Deferred / Not in MVP

- Alembic migration policy and migration scripts.
- Full dual-engine CI strategy.
- Persistent shared dev DB environment.
- Advanced performance/load testing for local DB path.

## Open Questions (if any)

- Should we standardize a local DB reset command in this WF or defer to task-phase implementation detail?
- Should fallback no-Docker guidance include a single remote-dev option reference, or keep it to one sentence only?

## Changelog

- v0.1 (2026-02-15): Initial PRD from spec
