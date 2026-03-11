<!-- docs/walkthroughs/walkthrough-WF-0074-canonical-funding-call-fidelity-hardening.md -->
# WF-0074 — Canonical Funding Call Fidelity Hardening

Artifact: walkthrough
Version: v0.1
Status: Draft
Last Updated: 2026-03-11

## Scope Summary
- Harden canonical call authoring fidelity for subordinate official prompts/questions without widening structured-review runtime consumption.
- Proof-call surface: `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`.
- Runtime claim boundary remains the expectations-only `call_config_snapshot`.

## Phase 3 Progress
- Tasks 1-5 were implemented across schema, proof-call/template, authoring docs, and durable governance surfaces.
- Phase 3.2 audit found one blocking regression: WF-0074 incorrectly blocked non-dry-run ingest of the same ERC PoC artifact already used by WF-0073 DB/API/service coverage.
- Audit remediation removed the false ingest blocker, proved subordinate prompts persist in non-dry-run canonical JSON, and added a structured-review regression showing runtime activation still emits only `schema_version` plus `expectations`.
- Docs-contract coverage was tightened to semantic anchors rather than brittle full-sentence wording, and workflow status surfaces were updated out of stale `Phase 2 (Ready)`.

## Verification Evidence

| Proof item | Command or test ID | Result | Notes |
| :--- | :--- | :--- | :--- |
| WF-0074 dry-run proof-call | `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0074_"` | pass | `1 passed, 11 deselected` |
| ERC PoC DB ingest persists subordinate prompts | `cd backend && RESET_DB=0 DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable ./scripts/verify_tests_postgres.sh tests/test_ingest_call_v2_db.py -k "wf0073_contract_erc_poc_2026_db_ingest_persists_single_step_call"` | pass | Re-run against already-ready isolated test DB after initial harness readiness timeout |
| ERC PoC structured runtime boundary | `cd backend && ./scripts/verify_tests_postgres.sh tests/test_structured_reviewer_service.py -k "wf0074_contract_erc_poc_runtime_snapshot_remains_expectations_only"` | pass | `1 passed, 25 deselected`; proves persisted subordinate prompts do not widen runtime snapshot |
| Docs/governance contract | `cd backend && uv run pytest tests/test_call_yaml_authoring_contract.py -k "wf0074_"` | pass | `2 passed` after semantic-anchor assertion refactor |

## Residual Risk
- The isolated Postgres harness showed a startup timing race on the first reset/readiness cycle; the rerun passed once the `grant_reviewer_test` database was fully ready.
- Full-suite regression coverage outside the targeted WF-0074/WF-0073 selectors was not rerun in this pass.
