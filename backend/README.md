# Backend

Python backend for Grant Reviewer using SQLModel and OpenAI.

## Tech Stack

- **Python 3.12+**
- **SQLModel** - ORM with Pydantic validation
- **SQLite** - File-based database (PostgreSQL-ready)
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
- `GET /health`
- `GET /calls`
- `GET /calls/{call_id}/nodes`
- `POST /reviews`
- `GET /reviews/{review_id}`

Quick smoke checks (run in another terminal while the server is running):
```bash
curl http://127.0.0.1:8000/health
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

### Database Reset

```bash
# Delete and recreate database
rm -f data/grant_reviewer.db
uv run python scripts/run_review.py  # Seeds fresh DB
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `BFF_SHARED_SECRET` | Shared secret for BFF signature verification | (none) |
| `LLM_MODEL` | Model to use | `gpt-4o-mini` |
| `LLM_MODE` | `openai` or `stub` | `openai` |
| `REVIEWS_ENABLED` | Kill switch for new submissions | `true` |
| `FREE_DAILY_REVIEW_LIMIT` | Free-tier per-user daily review limit | `5` |
| `REVIEW_TIMEOUT_SECONDS` | Timeout budget for synchronous reviews | `30` |

Copy `.env.example` to `.env` for local development.

## Tests

```bash
uv run pytest tests/test_api.py -q
```

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
