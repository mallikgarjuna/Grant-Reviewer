# Backend

Python backend for Grant Reviewer using SQLModel and OpenAI.

## Tech Stack

- **Python 3.12+**
- **SQLModel** - ORM with Pydantic validation
- **PostgreSQL (local dev default)** with **SQLite fallback** when `DATABASE_URL` is unset
- **OpenAI** - LLM integration (gpt-4o-mini default)
- **UV** - Package manager
- **FastAPI** - HTTP API

## Structure

```
backend/
├── app/
│   ├── models/domain.py         # 11 SQLModel tables
│   ├── schemas/
│   │   ├── call_definitions.py  # YAML ingestion schemas
│   │   └── llm_response.py      # LLM output validation
│   ├── repositories/            # Data access layer
│   ├── services/
│   │   ├── reviewer_service.py  # Core review logic
│   │   ├── llm_client.py        # OpenAI API client
│   │   └── prompt_builder.py    # Prompt assembly
│   └── db.py                    # Database connection
├── scripts/
│   ├── seed.py                  # Sample data seeding
│   ├── ingest_call.py           # YAML call ingestion CLI
│   ├── ensure_prompt_template.py # Ensures active PromptTemplate
│   └── run_review.py            # Review demo (real LLM)
├── data/
│   ├── calls/                   # YAML call definitions
│   └── grant_reviewer.db        # SQLite database (gitignored)
└── .env                         # API keys (gitignored)
```

## Setup

```bash
# Install dependencies
uv sync

# Create .env from template
cp .env.example .env
# Add your OPENAI_API_KEY

# Run review demo (seeds DB + calls LLM)
uv run python scripts/run_review.py
```

## Local Postgres Runbook (Canonical)

This is the primary local development path.

### 1) Start local Postgres

```bash
cd backend
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps
```

Optional DB GUI (pgAdmin):
- Open `http://localhost:5050`
- Login with:
  - Email: `admin@local.dev`
  - Password: `admin`
- Add server in pgAdmin with:
  - Host: `postgres`
  - Port: `5432`
  - Username: `grant`
  - Password: `grant`
  - Database: `grant_reviewer_dev`

### 2) Configure local env

In `backend/.env`, use localhost Postgres:

```env
DATABASE_URL=postgresql://grant:grant@localhost:5432/grant_reviewer_dev?sslmode=disable
LLM_MODE=stub
```

Safety rule:
- Keep local `.env` pointed to `localhost` by default.
- Do not keep Neon/prod hosts as your default local `DATABASE_URL`.

### 3) Bootstrap minimum required data

```bash
cd backend
uv run python scripts/ensure_prompt_template.py
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml
```

### 4) Verify readiness thresholds

```bash
cd backend
uv run python -c "from app.db import get_session; from app.models.domain import PromptTemplate, FundingCall, ProposalNode; from sqlmodel import select; s=get_session(); print('active_prompt_templates=', len(s.exec(select(PromptTemplate).where(PromptTemplate.is_active == True)).all())); print('funding_calls=', len(s.exec(select(FundingCall)).all())); print('proposal_nodes=', len(s.exec(select(ProposalNode)).all())); s.close()"
```

Expected minimums:
- `active_prompt_templates >= 1`
- `funding_calls >= 1`
- `proposal_nodes >= 1`

### 5) Verify one Postgres-backed stub review flow

```bash
cd backend
LLM_MODE=stub uv run uvicorn main:app --reload
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health/db
```

Then submit one local stub review through backend or BFF path:
- backend API path: `POST /reviews`
- frontend BFF path: `POST /api/bff/reviews`

Expected behavior:
- request returns review payload with terminal status (`COMPLETED` or `FAILED`).

### 6) Stop local Postgres

```bash
cd backend
docker compose -f docker-compose.dev.yml down
```

### 7) Reset local Postgres (destructive, local-only)

Warning:
- This deletes local dev DB data for the compose volume.
- Before running, confirm `DATABASE_URL` host is `localhost`.

```bash
cd backend
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
uv run python scripts/ensure_prompt_template.py
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml
```

No-Docker fallback (secondary path only):
- Use a local native Postgres instance that matches the same `DATABASE_URL` contract.
- Keep this as a temporary alternative; the blessed path remains Docker Compose.

## Run API

### Stub Mode (Recommended for Local Verification)

```bash
# No external API calls
LLM_MODE=stub uv run uvicorn main:app --reload
```

Notes:
- This is a long-running server process; the terminal will stay “busy” while it waits for requests.
- You should see output like `Uvicorn running on http://127.0.0.1:8000` and `Application startup complete.`
- Use a second terminal tab/window to call endpoints while the server runs.
- Stop the server with `Ctrl+C`.
- `main.py` auto-loads `backend/.env` when it exists (it does not override already-set environment variables).
- If you're running the Next.js BFF frontend, set `BFF_SHARED_SECRET` in `backend/.env` to match the frontend.

### OpenAI Mode (Costs Money)

```bash
# Requires OPENAI_API_KEY in .env
LLM_MODE=openai uv run uvicorn main:app --reload
```

Endpoints:
- `GET /health` (liveness: process up)
- `GET /health/db` (readiness: `200 {"ok":true}` when DB reachable; `503` canonical error when unavailable)
- `GET /calls`
- `GET /calls/{call_id}/nodes`
- `POST /reviews`
- `GET /reviews/{review_id}`
- `DELETE /reviews/{review_id}`

Review deletion behavior:
- Requires the same signed BFF auth headers used by other protected review endpoints.
- Ownership is enforced (`REVIEW_NOT_FOUND` for non-owner requests).
- Success response is `200 {"ok": true}`.
- Delete is hard delete for review + review cards + associated snippet.

Quick smoke checks (run in another terminal while the server is running):
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/db
```
Open interactive docs:
- `http://127.0.0.1:8000/docs`

## Scripts

### Review Demo (with real LLM)

```bash
uv run python scripts/run_review.py
```

**Output:**
```
✓ Review created with status=COMPLETED
✓ Generated 3 ReviewCards with AI feedback

Sample feedback:
"The objectives of the proposal are not articulated in a clear and 
detailed manner..."
```

### YAML Ingestion (Admin)

```bash
# Validate a call definition (dry run)
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml --dry-run

# Ingest to database
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml
```

### Ensure PromptTemplate (Bootstrap Precondition)

```bash
# Creates one active PromptTemplate if none exists
uv run python scripts/ensure_prompt_template.py
```

### Production Bootstrap Runbook (Manual)

Use this when provisioning a fresh production database (Task 8.0C).

```bash
# 1) Ensure active prompt template exists (required by POST /reviews)
uv run python scripts/ensure_prompt_template.py

# 2) Ingest at least one real call definition
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml
```

Verification checklist:
- `GET /calls` returns at least one call.
- `GET /calls/{call_id}/nodes` returns nodes.
- In `LLM_MODE=stub`, one BFF `POST /reviews` completes successfully.

### Legacy SQLite Reset (fallback only)

```bash
# Delete and recreate SQLite fallback database
rm -f data/grant_reviewer.db
uv run python scripts/run_review.py  # Seeds fresh DB
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `DATABASE_URL` | Local DB URL (`postgres://`/`postgresql://` normalized automatically) | localhost Postgres in `.env.example` |
| `BFF_SHARED_SECRET` | Shared secret for BFF signature verification | (none) |
| `LLM_MODEL` | Model to use | `gpt-4o-mini` |
| `LLM_MODE` | `openai` or `stub` | `openai` |
| `REVIEWS_ENABLED` | Kill switch for new submissions | `true` |
| `FREE_DAILY_REVIEW_LIMIT` | Free-tier per-user daily review limit | `5` |
| `REVIEW_TIMEOUT_SECONDS` | Timeout budget for synchronous reviews | `30` |

Copy `.env.example` to `.env` for local development.

## Tests

```bash
uv run pytest -q
```

Recent API coverage includes:
- signed auth and idempotency behavior
- quota / kill switch handling
- ownership checks for read + delete
- hard-delete lifecycle assertions

## LLM Integration

The review service:
1. Builds a structured prompt with expectations (strength, intent, guidance)
2. Calls OpenAI API with JSON output mode
3. Validates response against Pydantic schema
4. Creates ReviewCards with AI-generated feedback
5. Stores prompt and raw response for debugging

**Traceability fields on Review:**
- `prompt_sent` - Full prompt sent to LLM
- `raw_llm_response` - Raw JSON response
- `llm_model` - Model used (e.g., "gpt-4o-mini")

## Call Definition Files

YAML files in `data/calls/` follow this naming convention:
```
{agency}_{program}_{year}_{stage}.yaml
```

Examples:
- `erc_cog_2026_full.yaml` - ERC Consolidator Grant 2026, full proposal
- `nwo_vici_2026_pre.yaml` - NWO Vici 2026, pre-proposal

See `data/calls/README.md` for details.
