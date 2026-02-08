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

### Pending
- ⏳ Frontend UI

## Quick Start

### Prerequisites
- Python 3.12+
- [UV package manager](https://github.com/astral-sh/uv)
- OpenAI API key

### Setup

```bash
# Clone and setup backend
cd backend
uv sync

# Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the review demo
uv run python scripts/run_review.py
```

### Running the API (Stub Mode, No OpenAI Cost)

```bash
cd backend
LLM_MODE=stub uv run uvicorn main:app --reload
```

Then try:
```bash
curl http://127.0.0.1:8000/health
```

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
├── knowledge_base/          # Project documentation
└── tasks/                   # Task tracking
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
| 8.0 | Frontend UI | ⏳ Pending |

See `tasks/index.md` for detailed task tracking.

## Contributing

See `GEMINI.md` for AI coding agent guidelines and development workflow.

## License

MIT
