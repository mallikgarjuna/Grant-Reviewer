#!/usr/bin/env bash
set -euo pipefail

# Fast local DB-backed test run using SQLite.
# This intentionally keeps the "test DB only" safety guard satisfied by ensuring
# the SQLite filename contains "test".

cd "$(dirname "$0")/.."

TEST_DB_PATH="${TEST_DB_PATH:-/tmp/grant_reviewer_test_sqlite.db}"

if [[ "${TEST_DB_PATH}" != *"test"* ]]; then
  echo "[verify_tests_sqlite] Refusing to run: TEST_DB_PATH must include 'test' for safety."
  echo "[verify_tests_sqlite] Current TEST_DB_PATH=${TEST_DB_PATH}"
  exit 1
fi

rm -f "${TEST_DB_PATH}"

# For absolute paths, SQLAlchemy expects four slashes.
export DATABASE_URL="sqlite:////${TEST_DB_PATH#/}"

if [[ $# -gt 0 ]]; then
  uv run pytest "$@"
else
  uv run pytest -q
fi
