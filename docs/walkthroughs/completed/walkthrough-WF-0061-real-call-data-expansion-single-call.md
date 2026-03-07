<!-- docs/walkthroughs/completed/walkthrough-WF-0061-real-call-data-expansion-single-call.md -->
# WF-0061 — Real Call Data Expansion: Single New Canonical Call

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-07

Type: feature

## Scope Claim (Locked)

WF-0061 lands exactly one new promised canonical call:
- `MSCA-PF-2025`

Out-of-scope work remained excluded:
- no frontend redesign
- no BFF redesign
- no cross-call hardening program
- no second-call expansion

## Canonical Artifacts

- Canonical YAML: `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`
- Source manifest: `backend/data/calls/sources/msca_pf_2025_full.sources.md`

## Uploaded Source Evidence Used

Official source classes (required):
- proposal/application structure source:
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/af_he-msca-pf_en.pdf`
- evaluation criteria/elements sources:
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/ef_he-msca_en.pdf`
  - `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/wp-2-msca-actions_horizon-2023-2024_en.pdf`

Supplemental semantic source:
- `/home/mgurram/Projects/Non-Github/PeerLens_proj/MSCA-PF-2025/Guide for applicants_MSCA PF 2025.pdf`

Durable provenance and `SHA256` hashes are recorded in:
- `backend/data/calls/sources/msca_pf_2025_full.sources.md`

## What Changed

1. Fail-closed ingest upload gate for `MSCA-PF-2025`:
   - `backend/scripts/ingest_call.py` now blocks dry-run/ingest for `MSCA-PF-2025` when manifest evidence is missing or incomplete.
2. Real source-grounded canonical call authoring:
   - `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml` added from uploaded official sources.
3. Backend tracer seam proof only:
   - Runtime proof scoped to backend `POST /api/structured-review`.
4. No-fix backend compatibility outcome:
   - Existing structured-review seam handled `MSCA-PF-2025` without widening production compatibility surfaces.
5. Ordered-gate and blocker-boundary contract coverage:
   - Runtime-proof credit is blocked without ingest readiness.
   - Unknown cross-surface node candidates fail closed as malformed structured requests.

## Verification Commands and Deterministic Outcomes

Task 1:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0061_contract_ingest_blocks_msca_pf_2025_without_two_uploaded_sources"` -> PASS

Task 2:
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0061_contract_msca_pf_2025_dry_run_passes_with_uploaded_sources"` -> PASS
- `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/msca/msca_pf_2025_full.yaml --dry-run` -> PASS

Task 3:
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py -k "wf0061_contract_structured_api_tracer_accepts_real_msca_pf_2025_call"` -> PASS
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0061_contract_structured_service_uses_real_msca_pf_2025_snapshot"` -> PASS
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run python scripts/ingest_call.py data/calls/canonical/msca/msca_pf_2025_full.yaml` -> PASS (`checksum_match` deterministic idempotent ingest behavior)

Task 4:
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0061_contract_msca_backend_compatibility_stays_single_seam"` -> PASS

Task 5:
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py -k "wf0061_contract_runtime_proof_requires_upload_validate_ingest_order"` -> PASS
- `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0061_contract_multisurface_proof_candidate_stops_for_rescope"` -> PASS
- `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k "wf0061_contract_ingest_gate_blocks_runtime_credit_without_uploaded_msca_manifest"` -> PASS

## Seam and Boundary Evidence

Selected MVP runtime proof seam:
- backend `POST /api/structured-review` only

Compatibility seam result:
- no production seam expansion was required for `MSCA-PF-2025`; regression tests prove existing backend seam behavior remains bounded.

## Final Outcome

WF-0061 completion evidence supports only this claim:
- one new promised canonical call landed: `MSCA-PF-2025`.
