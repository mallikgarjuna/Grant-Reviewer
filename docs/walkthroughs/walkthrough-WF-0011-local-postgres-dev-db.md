# WF-0011 — Local Postgres Dev DB

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-02-15

## Overview

WF-0011 implemented a local Postgres-first developer runbook for backend work, with SQLite retained as explicit fallback when `DATABASE_URL` is unset.

## Verification Evidence

### 1) Local Postgres startup check

Command:
```bash
cd backend && docker compose -f docker-compose.dev.yml up -d
```

Observed outcome:
- `grant-reviewer-postgres-dev` container started successfully.

Command:
```bash
cd backend && docker compose -f docker-compose.dev.yml ps
```

Observed outcome:
- Service listed as `Up` with health status and port mapping `0.0.0.0:5432->5432/tcp`.

### 2) Bootstrap scripts

Commands:
```bash
cd backend
DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_dev?sslmode=disable' uv run python scripts/ensure_prompt_template.py
DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_dev?sslmode=disable' uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml
```

Observed outcome:
- Active prompt template created.
- Call ingest completed successfully for `ERC-COG-2026`.

### 3) Readiness count checks

Command:
```bash
cd backend
DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_dev?sslmode=disable' uv run python -c "from app.db import get_session; from app.models.domain import PromptTemplate, FundingCall, ProposalNode; from sqlmodel import select; s=get_session(); print('active_prompt_templates=', len(s.exec(select(PromptTemplate).where(PromptTemplate.is_active == True)).all())); print('funding_calls=', len(s.exec(select(FundingCall)).all())); print('proposal_nodes=', len(s.exec(select(ProposalNode)).all())); s.close()"
```

Observed outcome:
- `active_prompt_templates= 1`
- `funding_calls= 1`
- `proposal_nodes= 7`

### 4) Local reset flow (destructive, local-only)

Command:
```bash
cd backend && docker compose -f docker-compose.dev.yml down -v && docker compose -f docker-compose.dev.yml up -d
```

Observed outcome:
- Container, network, and volume removed and recreated successfully.

Post-reset rebootstrap + counts:
- Re-ran bootstrap scripts and count checks.
- Thresholds reconfirmed at/above required minimums.

### 5) Stub review terminal-status verification

Command:
- Executed signed `POST /reviews` against app via FastAPI `TestClient` with:
  - `DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_dev?sslmode=disable`
  - `LLM_MODE=stub`
  - valid BFF signature headers and idempotency key.

Observed outcome:
- `status_code= 200`
- `review_status= COMPLETED` (terminal status reached).

## Deviations / Fixes

- Initial signed `POST /reviews` attempt returned `401` due incorrect signature payload construction.
- Fixed by matching backend signature contract from tests (`user.timestamp.sha256(body)`), then verification passed.
- Initial sandbox execution could not access Docker daemon; Docker steps were run with elevated permissions.

## How To Run

1. `cd backend && docker compose -f docker-compose.dev.yml up -d`
2. Set local `DATABASE_URL` to localhost Postgres with `sslmode=disable`.
3. Run:
   - `uv run python scripts/ensure_prompt_template.py`
   - `uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml`
4. Run readiness count check command from `backend/README.md`.
5. Run one stub review verification (`POST /reviews`) and confirm terminal status.

## Known Limitations

- Docker is required for the blessed local path.
- No full native Postgres troubleshooting runbook is included in WF-0011.
- Alembic and CI dual-engine strategy are explicitly deferred to follow-up workflow.

## Changelog

- v0.1 (2026-02-15): Initial walkthrough with local Postgres runbook verification evidence and deviations
- v1.0 (2026-02-15): Finalized walkthrough for WF-0011 completion
