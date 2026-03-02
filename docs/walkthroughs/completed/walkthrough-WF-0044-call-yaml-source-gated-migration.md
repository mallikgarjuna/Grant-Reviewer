# WF-0044 — Source-Gated Call YAML Migration + Structured Policy Enforcement

Artifact: walkthrough
Version: v1.0
Status: Ready for Ship Gate
Last Updated: 2026-03-02

## Scope Delivered

- Added canonical v2 call definition for `erc_cog_2026_full` and refreshed legacy mirror traceability.
- Refreshed source manifests for:
  - `nwo_veni_2025_preproposal`
  - `nwo_vidi_2025_full_proposal`
  - `erc_stg_2026_full`
  - `erc_cog_2026_full`
- Added WF-0044 source-copy traceability regression coverage in no-DB ingest tests.
- Added CoG DB ingest + structured API acceptance tests.
- Wired structured pipeline to resolve call-definition `reviewer_policy` by node/stage scope.
- Added deterministic structured policy enforcement contract:
  - `PROMPT_ONLY` affects prompt snapshot only.
  - `POST_CHECK` appends deterministic warning summary.
  - `BLOCKING` fails with stable `POLICY_BLOCKING:` prefix and persists zero cards.
- Added dedicated WF-0044 policy matrix fixture and selector-based tests (`wf0044_policy_*`).

## Strict Upload Checkpoints (Rerun 2026-03-02)

- Re-ran WF-0044 Phase 3 with explicit per-call upload gate enforcement before authoring refreshes.
- **Checkpoint 1 (ERC CoG 2026) — satisfied**
  - User-uploaded sources accepted for this call:
    - `wp_horizon-erc-2026_en.pdf` (declared SSOT for ERC evaluation criteria/elements)
    - `af_he-erc-cog_en.pdf`
    - `erc-rules-for-submission-and-evaluation_he-erc_en.pdf`
    - `guide-for-peer-reviewers_he-erc-stg-cog_en.pdf`
    - `information-for-applicants_he-erc-stg-cog_en.pdf`
  - Applied rerun updates:
    - Refreshed canonical CoG source-header comments to include SSOT + supplemental cross-check sources.
    - Expanded CoG source manifest to include all uploaded source files and corrected SHA traceability metadata.
  - Rerun verification evidence:
    - `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k erc_cog_2026_full` -> `1 passed`
    - `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml --dry-run` -> `schema_version=v2`, dry-run success
- **Checkpoint 2 (NWO Veni 2025 pre-proposal) — satisfied**
  - User-uploaded sources accepted for this call:
    - `Call for Proposals Veni 2025_EN_0.pdf`
    - `veni_pre-proposal_form_2025.docx`
  - Applied rerun updates:
    - Corrected manifest origin paths to uploaded `PeerLens_proj/NWO-Veni-2025/...` sources.
    - Added missing copied-local call PDF under `backend/data/calls/source_files/WF-0044/nwo_veni_2025_preproposal/`.
    - Updated provenance notes to strict-checkpoint upload context.
  - Rerun verification evidence:
    - `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k nwo_veni_2025_preproposal` -> `1 passed`
    - `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run` -> `schema_version=v2`, dry-run success
- **Checkpoint 3 (NWO Vidi 2025 full proposal) — satisfied**
  - User-uploaded sources accepted for this call:
    - `Call-for-Proposals-Vidi-2025_Eng.pdf`
    - `Vidi-2025-Full-proposal-form.docx`
  - Applied rerun updates:
    - Confirmed source hashes match uploaded files for both source entries.
    - Added missing copied-local call PDF under `backend/data/calls/source_files/WF-0044/nwo_vidi_2025_full_proposal/`.
    - Updated manifest provenance notes/dates to strict-checkpoint upload context.
  - Rerun verification evidence:
    - `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k nwo_vidi_2025_full_proposal` -> `1 passed`
    - `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml --dry-run` -> `schema_version=v2`, dry-run success
- **Checkpoint 4 (ERC StG 2026) — satisfied**
  - User-uploaded sources accepted for this call:
    - `wp_horizon-erc-2026_en.pdf` (SSOT for ERC criteria/elements)
    - `af_he-erc-stg_en.pdf`
    - `erc-rules-for-submission-and-evaluation_he-erc_en.pdf`
    - `guide-for-peer-reviewers_he-erc-stg-cog_en.pdf`
    - `information-for-applicants_he-erc-stg-cog_en.pdf`
  - Applied rerun updates:
    - Updated StG canonical source-header comments to reflect ERC SSOT + supplemental sources.
    - Expanded StG source manifest from 2 to 5 source entries with strict-checkpoint provenance and hashes.
    - Added missing copied-local source files under `backend/data/calls/source_files/WF-0044/erc_stg_2026_full/` for traceability completeness.
  - Rerun verification evidence:
    - `cd backend && uv run pytest tests/test_ingest_call_dry_run.py -k erc_stg_2026_full` -> `1 passed`
    - `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml --dry-run` -> `schema_version=v2`, dry-run success

## Verification Evidence

Commands run and passing in this workflow:

```bash
cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml --dry-run
cd backend && uv run python scripts/ingest_call.py data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml --dry-run
cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_stg_2026_full.yaml --dry-run
cd backend && uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml --dry-run
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest -k wf0044_policy_
```

Additional task-level checks run:

```bash
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_ingest_call_v2_db.py -k erc_cog_2026_full
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py -k "structured_review and erc_cog_2026_full"
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py -k "structured_review and policy"
```

Rerun status (strict upload-checkpoint pass, 2026-03-02):
- Re-executed the full WF-0044 verification bundle above after checkpoint updates; all commands passed.

## Risks / Notes

- DB-backed test commands require a `DATABASE_URL` whose database name includes `test`.
- Large source binaries above repository pre-commit threshold are not committed; manifests remain the auditable source-of-truth.

## Source Retention Rule

- Keep copied WF-0044 source files through implementation + technical review.
- After completion and manifest/hash verification, move required copies to secure store or purge local non-required copies.
- Preserve committed manifests for long-term provenance.
