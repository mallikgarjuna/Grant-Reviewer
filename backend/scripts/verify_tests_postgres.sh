#!/usr/bin/env bash
set -euo pipefail

# Verification test run using the isolated local Postgres test stack.
# Use this as a "DB-sensitive behavior" check before shipping.

cd "$(dirname "$0")/.."

export DATABASE_URL="${DATABASE_URL:-postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable}"

if [[ "${DATABASE_URL}" != *"test"* ]]; then
  echo "[verify_tests_postgres] Refusing to run: DATABASE_URL must target a test database."
  echo "[verify_tests_postgres] Current DATABASE_URL=${DATABASE_URL}"
  exit 1
fi

if [[ "${DATABASE_URL}" != postgresql* && "${DATABASE_URL}" != postgres* ]]; then
  echo "[verify_tests_postgres] Refusing to run: expected a Postgres DATABASE_URL."
  echo "[verify_tests_postgres] Current DATABASE_URL=${DATABASE_URL}"
  exit 1
fi

RESET_DB="${RESET_DB:-1}"
if [[ "${RESET_DB}" == "1" ]]; then
  ./scripts/reset_test_db.sh
else
  docker compose -f docker-compose.test.yml up -d
fi

cid="$(docker compose -f docker-compose.test.yml ps -q postgres_test || true)"
if [[ -z "${cid}" ]]; then
  echo "[verify_tests_postgres] Could not find running container for service 'postgres_test'."
  echo "[verify_tests_postgres] Try: cd backend && docker compose -f docker-compose.test.yml up -d"
  exit 1
fi

echo "[verify_tests_postgres] Waiting for Postgres readiness..."
for _ in $(seq 1 30); do
  if docker exec "${cid}" pg_isready -U grant -d grant_reviewer_test >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker exec "${cid}" pg_isready -U grant -d grant_reviewer_test >/dev/null 2>&1; then
  echo "[verify_tests_postgres] Postgres did not become ready in time."
  exit 1
fi

if [[ $# -gt 0 ]]; then
  uv run pytest "$@"
else
  uv run pytest -q
fi
