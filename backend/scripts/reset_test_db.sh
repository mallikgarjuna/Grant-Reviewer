#!/usr/bin/env bash
set -euo pipefail

if [[ "${GRANT_REVIEWER_TEST_DB_LOCKED:-0}" != "1" ]]; then
  LOCK_FILE="${TMPDIR:-/tmp}/grant-reviewer-postgres-test.lock"
  exec 9>"${LOCK_FILE}"
  flock 9
fi

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
