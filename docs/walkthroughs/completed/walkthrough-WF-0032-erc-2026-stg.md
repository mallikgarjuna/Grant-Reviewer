# WF-0032 — ERC Starting Grant 2026 Walkthrough

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-02-26

## 1. Goal Overview
Deliver hierarchical proposal-node ingestion for V2 call definitions and author a source-grounded ERC StG 2026 full-call YAML with enforceable reviewer-policy metadata.

## 2. What Changed
- Added V2 schema support for hierarchical authoring and evaluation metadata (`parent_logical_id`, `max_pages`, stage metadata on evaluation elements).
- Refactored ingestion graph handling to validate duplicates/missing parents/self-parent/cycles and persist deterministic preorder with `parent_node_id` linking.
- Added/updated DB and API tests to verify end-to-end hierarchy persistence and flat-node API parent links.
- Authored ERC StG full-call YAML from provided official sources and added a traceability source manifest.
- Hardened reviewer-policy runtime behavior and aligned ERC call artifact layout under `backend/data/calls/erc/` plus `backend/data/calls/sources/`.
- Updated docs/commands to use new ERC paths and parked follow-up re-authoring work for ERC CoG in `docs/parking_lot.md`.

## 3. Verification Evidence
- `pre-commit run --all-files` passed.
- `cd backend && docker compose -f docker-compose.test.yml up -d`
- `cd backend && export DATABASE_URL="postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable" && uv run pytest -q` → `92 passed`.
- `cd backend && uv run python scripts/ingest_call.py data/calls/erc/erc_stg_2026_full.yaml --dry-run` passed.
- `cd backend && uv run python scripts/ingest_call.py data/calls/erc/erc_cog_2026_full_official.yaml --dry-run` passed.

## 4. Notable Decisions
- Kept `GET /calls/{id}/nodes` flat with correct `parent_node_id` for MVP stability.
- Stored source traceability next to call artifacts (`backend/data/calls/sources/`) instead of `docs/reference/`.
- Preserved separate `/reviews` and `/api/structured-review` endpoints; shared-core refactor remains parked.

## 5. Next Steps
- Execute shipping flow for this branch (`ship it`).
- Start the parked workflow to re-author ERC CoG from official sources (P2 #23).
