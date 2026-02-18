# Grant Reviewer

AI-powered grant proposal review assistant. Get rubric-grounded feedback on your research proposals before submission.

## Overview

Grant Reviewer helps researchers improve their grant proposals by providing AI-generated feedback based on real funding call rubrics. The system:

1. **Ingests funding call definitions** (rubrics, evaluation criteria, proposal structure)
2. **Analyzes proposal snippets** against the relevant rubric elements
3. **Generates structured feedback** with actionable suggestions

## Project Status

🎉 **MVP Core Complete** - Real LLM integration working!

### Completed
- ✅ Domain models (11 SQLModel tables)
- ✅ Core reviewer service with real OpenAI integration
- ✅ Admin ingestion pipeline (YAML → Database)
- ✅ Sample ERC call definition
- ✅ End-to-end review flow verified
- ✅ FastAPI REST endpoints (minimal MVP)
- ✅ BFF contract hardening on backend (auth signature, ownership checks, idempotency, quotas, kill switch)
- ✅ Next.js frontend scaffold + BFF adapter + SEO guardrails + app UI pages (Task 8.0A implementation)
- ✅ Deployment wiring (Neon Postgres + Render backend + Vercel frontend + Clerk auth) + deploy verification (Task 8.0C)
- ✅ PeerLens landing release (WF-0009): new `/` marketing page, `/privacy`, static call demos, review export, and self-serve delete flow
- ✅ Review detail auto-polling (WF-0017): pending reviews now auto-refresh every 3s with a 90s cap and safe fallback messaging
- ✅ Submit flow hardening (WF-0018): added deterministic `Start new review` reset flow, actionable slow-state guidance, and stricter auth/sign-out redirect continuity

### Notes
- MVP stack (current): **Neon** (Postgres) + **Render** (FastAPI) + **Vercel** (Next.js) + **Clerk** (auth).
- Production bootstrap runs from a developer machine (Render free tier has no shell). See `docs/walkthroughs/walkthrough_task_8.0C_deployment_wiring.md`.
- Workflow status: `WF-0018` is complete (`docs/index.md` marked `Done`).

## Quick Start

### Prerequisites
- Python 3.12+
- [UV package manager](https://github.com/astral-sh/uv)
- OpenAI API key (only needed for `LLM_MODE=openai`)
- Node.js 22.17.0 (for `frontend/`; if using `nvm`, run `nvm use v22.17.0`)

### Setup

```bash
# Clone and setup backend
cd backend
uv sync

# Configure local environment
cp .env.example .env
# Edit .env and set at least:
# - BFF_SHARED_SECRET
# - DATABASE_URL (optional locally; required for Postgres)
# - OPENAI_API_KEY (only if using LLM_MODE=openai)

# Run the review demo
uv run python scripts/run_review.py
```

### Running the API (Stub Mode, No OpenAI Cost)

```bash
cd backend
LLM_MODE=stub uv run uvicorn main:app --reload
```

Notes:
- This command starts a web server and will keep running (it will look “stuck” because it’s waiting for requests).
- Leave it running and use a second terminal tab/window to make requests.
- Stop the server with `Ctrl+C`.

Then try (in a second terminal):
```bash
curl http://127.0.0.1:8000/health
```

Or open API docs in your browser:
- `http://127.0.0.1:8000/docs`

MVP API note:
- Protected review endpoints now require BFF-style signed headers and idempotency key (`POST /reviews`, `GET /reviews/{review_id}`).
- See `docs/walkthroughs/walkthrough_task_8.0B_bff_contracts.md` for concrete verification examples.

### Deployment Notes (Neon + Render)

- Prefer Neon **direct** connection strings for Render (pooler + `channel_binding=require` triggered intermittent SSL disconnects with real queries).
- Avoid `source backend/.env` if your `DATABASE_URL` contains `&` (bash/zsh will parse it); set env vars via your shell (`export DATABASE_URL='...'`) or rely on `python-dotenv` in `backend/main.py`.
- Bootstrap in production by running scripts locally against the same Neon DB used by Render:
  - `cd backend && DATABASE_URL='...' uv run python scripts/ensure_prompt_template.py`
  - `cd backend && DATABASE_URL='...' uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml`

### Running The Frontend (Local)

Prereqs:
- A Clerk application (publishable key + secret key).
- A shared secret for BFF signing (`BFF_SHARED_SECRET`) that matches the backend.

```bash
source ~/.nvm/nvm.sh
nvm use v22.17.0

cd frontend
npm install

cp .env.local.example .env.local
# Edit .env.local:
# - CLERK_SECRET_KEY
# - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
# - FASTAPI_BASE_URL (e.g. http://127.0.0.1:8000)
# - BFF_SHARED_SECRET (must match backend)

npm run lint
npm run check:bff
npm run check:seo

npm run dev
```

Recommended local verification entrypoint (from repo root):

```bash
bash scripts/verify_local_8_0A.sh
```

### End-to-End Local Verification Checklist

1. Start backend in one terminal:
   - `cd backend`
   - `LLM_MODE=stub uv run uvicorn main:app --reload`
2. Start frontend in a second terminal:
   - `source ~/.nvm/nvm.sh && nvm use v22.17.0`
   - `cd frontend && npm run dev`
3. Open `http://localhost:3000/` and confirm landing page loads.
4. Open `http://localhost:3000/app` while signed out and confirm redirect to `/sign-in`.
5. Sign in with email code and confirm redirect back to `/app`.
6. Submit a review and confirm redirect to `/app/reviews/<review_id>`.
7. Refresh `/app/reviews/<review_id>` and confirm result still renders.
8. If a step fails, capture both terminal logs and the failing URL before retrying.
9. Verify landing truthfulness flow:
   - `/` shows PeerLens landing sections and CTA to `/sign-in`
   - `/privacy` contains retention/training/deletion statements
   - open a completed review at `/app/reviews/<review_id>`, test `Copy as text`, `Download .txt`, and `Delete review`
   - refreshing the deleted review URL returns not found behavior

Notes:
- `/app/*` and `/api/bff/*` are Clerk-protected.
- `/app/*` is `noindex` and disallowed in `robots.txt`; marketing + blog routes are indexable.

### Running a Review Demo

```bash
cd backend

# Seeds database + runs review with real LLM
uv run python scripts/run_review.py
```

**Sample output:**
```
TEST 1: Reviewing Section 1 (has 3 expectations)
✓ Review created with status=COMPLETED
✓ Generated 3 ReviewCards with AI feedback

Sample feedback:
"The objectives of the proposal are not articulated in a clear and
detailed manner. It is essential to expand on the specific goals..."
```

### Ingesting Call Definitions

```bash
# Validate first (dry run)
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml --dry-run

# Ingest to database
uv run python scripts/ingest_call.py data/calls/erc_cog_2026_full.yaml
```

## Architecture

```
Grant-Reviewer/
├── backend/                 # Python backend
│   ├── app/
│   │   ├── models/          # SQLModel domain models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic + LLM integration
│   │   └── db.py            # Database connection
│   ├── scripts/             # CLI utilities
│   └── data/calls/          # YAML call definitions
└── docs/                    # Project docs + task tracking
```

## Domain Model

The system uses 11 interconnected tables:

| Table | Purpose |
|-------|---------|
| `FundingAgency` | Organization (ERC, NWO, etc.) |
| `FundingCall` | Specific grant program |
| `EvaluationCriterion` | Top-level rubric dimension (Excellence, Impact) |
| `EvaluationElement` | Atomic reviewable concern |
| `ProposalNode` | Hierarchical proposal structure |
| `NodeExpectation` | Links nodes to rubric elements + guidance |
| `User` | Anonymous session owner |
| `ProposalSnippet` | User-pasted text to review |
| `PromptTemplate` | Versioned AI prompt |
| `Review` | Assessment event + LLM traceability |
| `ReviewCard` | Individual feedback item |

## Development Progress

| Task | Description | Status |
|------|-------------|--------|
| 0.0-4.0 | Domain model & core logic | ✅ Complete |
| 5.0 | Admin YAML ingestion | ✅ Complete |
| 6.0 | LLM Integration MVP | ✅ Complete |
| 7.0 | FastAPI endpoints | ✅ Complete |
| 8.0B | BFF Contracts (backend) | ✅ Complete |
| 8.0A | Frontend UI Slice | ✅ Complete (Verify-Local done; Verify-Deploy deferred to 8.0C) |
| 8.0C | Deployment wiring | ✅ Complete |
| WF-0009 | PeerLens landing page | ✅ Complete |

See `docs/index.md` for detailed task tracking.

## Contributing

See `GEMINI.md` for AI coding agent guidelines and development workflow.

## License

MIT
