#!/usr/bin/env bash
set -euo pipefail

export DATABASE_URL="${DATABASE_URL:-postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable}"

if [[ "${DATABASE_URL}" != *"test"* ]]; then
  echo "[reset_test_db] Refusing to run: DATABASE_URL must target a test database."
  echo "[reset_test_db] Current DATABASE_URL=${DATABASE_URL}"
  exit 1
fi

echo "[reset_test_db] Resetting local test Postgres (destructive local-only)..."
docker compose -f docker-compose.test.yml down -v
docker compose -f docker-compose.test.yml up -d

echo "[reset_test_db] Done. DATABASE_URL=${DATABASE_URL}"
