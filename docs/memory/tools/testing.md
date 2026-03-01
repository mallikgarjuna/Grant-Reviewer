# Testing Isolation

- **DB Isolation (Tests):** Never run tests against the dev DB. Always isolate them.
  - Example: `cd backend && docker compose -f docker-compose.test.yml up -d && export DATABASE_URL=...  # match backend/docker-compose.test.yml && uv run pytest`
