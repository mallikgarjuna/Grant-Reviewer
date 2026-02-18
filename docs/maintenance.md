# Maintenance Tasks Tracking

This file tracks minor fixes, refactors, and maintenance tasks to avoid cluttering the major task list.

| ID | Task Description | Status | Commit |
| :--- | :--- | :--- | :--- |
| M.1 | Refactor Python code for PEP 8 compliance using Ruff | [x] | `feat: [M.1] be9c53d` |
| M.2 | Add descriptive docstrings to domain models          | [x] | `feat: [M.2] 0612f38` |
| M.3 | Fix magic values in ReviewerService                  | [x] | `feat: [M.3] 0612f38` |
| M.4 | Add Field-level descriptions to all domain models    | [x] | `feat: [M.4] 9f48c3a` |
| M.5 | Audit and fix relationship back_populates symmetry   | [x] | `feat: [M.5] 6a7ded7` |
| M.6 | WF-0016 scorecard hardening (badge fallback, summary spacing, API assertion) | [x] | pending commit |
| M.7 | CI stabilization: frontend Clerkless build fallback + backend file-based sqlite test DB | [x] | pending commit |

## Local Maintenance & Verification (WF-0015)

To ensure your code passes CI/CD:

### Backend
```bash
cd backend
uv sync                     # Install dependencies
uv run ruff check .         # Linting
uv run mypy .               # Type Checking
uv run pytest               # Tests
```

### Frontend
```bash
cd frontend
npm ci                      # Install dependencies
npm run lint                # Linting
npm run build               # Production Build Check
```

### Git Hooks
```bash
# Install hooks (once)
pip install pre-commit
pre-commit install

# Run checks manually
pre-commit run --all-files
```
