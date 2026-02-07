# Grant Reviewer

AI-powered grant proposal review assistant. Get rubric-grounded feedback on your research proposals before submission.

## Overview

Grant Reviewer helps researchers improve their grant proposals by providing AI-generated feedback based on real funding call rubrics. The system:

1. **Ingests funding call definitions** (rubrics, evaluation criteria, proposal structure)
2. **Analyzes proposal snippets** against the relevant rubric elements
3. **Generates structured feedback** with severity ratings (Critical/Warning/Success/Note)

## Project Status

🚧 **MVP in development** - Backend core logic complete, API and frontend pending.

### Completed
- ✅ Domain models (11 SQLModel tables)
- ✅ Core reviewer service with AI integration
- ✅ Admin ingestion pipeline (YAML → Database)
- ✅ Sample ERC/NSF call definitions

### Pending
- ⏳ FastAPI REST endpoints
- ⏳ Frontend UI (Next.js)

## Quick Start

### Prerequisites
- Python 3.12+
- [UV package manager](https://github.com/astral-sh/uv)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd Grant-Reviewer

# Setup backend
cd backend
uv sync

# Create database tables
uv run python -c "from app.db import create_db_and_tables; create_db_and_tables()"

# Ingest a sample call definition
uv run python scripts/ingest_call.py data/calls/sample_erc_call.yaml
```

### Running Scripts

```bash
# Seed database with sample data
uv run python scripts/seed.py

# Run a review (demo)
uv run python scripts/run_review.py

# Ingest a call definition (dry run first)
uv run python scripts/ingest_call.py data/calls/sample_erc_call.yaml --dry-run
uv run python scripts/ingest_call.py data/calls/sample_erc_call.yaml
```

## Architecture

```
Grant-Reviewer/
├── backend/                 # Python backend (SQLModel + FastAPI)
│   ├── app/
│   │   ├── models/          # SQLModel domain models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic
│   │   └── db.py            # Database connection
│   ├── scripts/             # CLI utilities
│   │   ├── seed.py          # Sample data seeding
│   │   ├── ingest_call.py   # YAML call ingestion
│   │   └── run_review.py    # Review demo
│   └── data/calls/          # YAML call definitions
├── knowledge_base/          # Project documentation
└── tasks/                   # Task tracking
```

## Domain Model

The system uses 11 interconnected tables:

| Table | Purpose |
|-------|---------|
| `FundingAgency` | Organization (ERC, NSF, etc.) |
| `FundingCall` | Specific grant program |
| `EvaluationCriterion` | Top-level rubric dimension (Excellence, Impact) |
| `EvaluationElement` | Atomic reviewable concern |
| `ProposalNode` | Hierarchical proposal structure |
| `NodeExpectation` | Links nodes to rubric elements |
| `User` | Anonymous session owner |
| `ProposalSnippet` | User-pasted text to review |
| `PromptTemplate` | Versioned AI prompt |
| `Review` | Assessment event |
| `ReviewCard` | Individual feedback item |

## Contributing

See `GEMINI.md` for AI coding agent guidelines and development workflow.

## License

MIT
