<!-- docs/walkthroughs/walkthrough-WF-0073-erc-poc-2026-call-onboarding.md -->
# WF-0073 — ERC PoC 2026 Call Onboarding

Artifact: walkthrough
Version: v1.0
Status: Completed (Awaiting Ship Approval)
Last Updated: 2026-03-11

## Scope Summary
- One-call onboarding only: `ERC-2026-PoC`.
- Proof seams: source manifest gate, dry-run ingest, DB ingest, `/calls`, `/api/public/calls/{call_logical_id}/nodes/metadata`, and `POST /api/structured-review`.
- No frontend/BFF launch claims.

## Implementation + Audit Closure
- Canonical call authored at `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` with single-step semantics.
- Source manifest authored at `backend/data/calls/sources/erc_poc_2026_full.sources.md`.
- Backend test seams added for ingest/exposure/structured-review smoke.
- Phase 3 audit fix applied in commit `2f95acf`:
  - Hardened WF-0073 manifest gate to require distinct source evidence blocks.
  - Added regression coverage for single-entry combined-source false pass.

## Verification Matrix (Task 5 Closure)

| Proof item | Exercised seam | Command or test ID | Expected outcome | Result | Evidence reference | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Source manifest gate | source manifest | `uv run pytest tests/test_ingest_call_dry_run.py -k "wf0073_contract_erc_poc_2026_manifest_gate_fails_closed_on_missing_required_traceability" -q` | manifest rejects missing source class / `SHA256` / `Used for` and accepts complete manifest | pass | `2 passed, 9 deselected` from `tests/test_ingest_call_dry_run.py -k "wf0073"` | Includes regression for single-entry combined-source claim. |
| Dry-run ingest | `backend/scripts/ingest_call.py --dry-run` | `uv run pytest tests/test_ingest_call_dry_run.py -k "wf0073_contract_erc_poc_2026_dry_run_passes_with_single_step_source_grounded_yaml" -q` | dry-run exits 0 with clean summary and PoC single-step contract | pass | `2 passed, 9 deselected` from `tests/test_ingest_call_dry_run.py -k "wf0073"` | Confirms `split_visibility_reviewability_enabled=false`. |
| DB ingest | ingest script + DB persistence | `DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest tests/test_ingest_call_v2_db.py -k "wf0073" -q` | call persists cleanly | pass | `1 passed, 11 deselected` | DB-backed proof executed on dedicated test DB. |
| Call exposure | `GET /calls` | `DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0073_contract_erc_poc_2026_ingest_exposes_call_listing" -q` | `/calls` includes `ERC-2026-PoC` | pass | `2 passed, 147 deselected` from `tests/test_api.py -k "wf0073"` | Shared run also covered structured-review API smoke. |
| Node metadata exposure | `GET /api/public/calls/{call_logical_id}/nodes/metadata` | `DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest tests/test_call_nodes_metadata_api.py -k "wf0073" -q` | metadata endpoint resolves authored PoC nodes | pass | `1 passed, 6 deselected` | Validated nodes: `poc_idea_innovation`, `poc_approach_methodology`, `poc_pi_strategic_leadership`. |
| Structured-review smoke | `POST /api/structured-review` | `DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0073_contract_structured_api_accepts_erc_poc_2026_payload" -q` and `... pytest tests/test_structured_reviewer_service.py -k "wf0073" -q` | smoke request succeeds without call-contract errors | pass | API: `2 passed, 147 deselected`; service: `2 passed, 23 deselected` | Fixture: `backend/tests/fixtures/wf_0073_erc_poc_2026_structured_review.json`. |

## Compatibility Fix Boundary
- Required compatibility fix: yes, one narrow backend seam only.
- Fix seam: `backend/scripts/ingest_call.py` WF-0073 manifest gate logic.
- Scope impact: confined to `ERC-2026-PoC` source-manifest fail-closed enforcement; no broad ERC runtime changes.

## Risks and Follow-ups
- Residual risk: full-suite regressions outside WF-0073 selectors were not rerun in this closure pass.
- Deferred by scope: frontend/BFF/browser-level proof.

## Ship Recommendation
- Phase 3.3 closure status: ready.
- Ship gate: pending explicit user approval.
