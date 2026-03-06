#!/usr/bin/env bash
set -euo pipefail

# Verification test run using the isolated local Postgres test stack.
# Use this as a "DB-sensitive behavior" check before shipping.

cd "$(dirname "$0")/.."

LOCK_FILE="${TMPDIR:-/tmp}/grant-reviewer-postgres-test.lock"
exec 9>"${LOCK_FILE}"
flock 9
export GRANT_REVIEWER_TEST_DB_LOCKED=1

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
READY_TIMEOUT_SECONDS="${READY_TIMEOUT_SECONDS:-60}"
for _ in $(seq 1 "${READY_TIMEOUT_SECONDS}"); do
  # Prefer Docker health status when available (compose defines a healthcheck).
  health_status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "${cid}" 2>/dev/null || true)"
  if [[ "${health_status}" == "healthy" ]]; then
    break
  fi

  if docker exec "${cid}" pg_isready -U grant -d grant_reviewer_test >/dev/null 2>&1; then
    break
  fi

  sleep 1
done

health_status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "${cid}" 2>/dev/null || true)"
if [[ "${health_status}" != "healthy" ]] && ! docker exec "${cid}" pg_isready -U grant -d grant_reviewer_test >/dev/null 2>&1; then
  echo "[verify_tests_postgres] Postgres did not become ready in time."
  echo "[verify_tests_postgres] Container health_status=${health_status}"
  echo "[verify_tests_postgres] Recent container logs:"
  docker logs --tail 200 "${cid}" || true
  exit 1
fi

if [[ $# -gt 0 ]]; then
  uv run pytest "$@"
else
  uv run pytest -q
fi
