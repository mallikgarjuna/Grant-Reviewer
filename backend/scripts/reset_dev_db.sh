#!/usr/bin/env bash
set -euo pipefail

echo "[reset_dev_db] Resetting local dev Postgres (destructive local-only)..."
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d

echo "[reset_dev_db] Ensuring active prompt template..."
uv run python scripts/ensure_prompt_template.py

echo "[reset_dev_db] Ingesting canonical Veni call definition..."
uv run python scripts/ingest_call.py data/calls/nwo/nwo_veni_2025_preproposal.yaml

echo "[reset_dev_db] Done."
