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

## Risks / Notes

- DB-backed test commands require a `DATABASE_URL` whose database name includes `test`.
- Large source binaries above repository pre-commit threshold are not committed; manifests remain the auditable source-of-truth.

## Source Retention Rule

- Keep copied WF-0044 source files through implementation + technical review.
- After completion and manifest/hash verification, move required copies to secure store or purge local non-required copies.
- Preserve committed manifests for long-term provenance.
