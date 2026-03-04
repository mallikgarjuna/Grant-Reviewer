# Backend Quirks

- **Script Paths:** When running backend scripts, use `cd backend && PYTHONPATH=. uv run python scripts/my_script.py`.
- **Database variables:** `DATABASE_URL` is explicitly required; the backend no longer falls back to SQLite when unset.
- **2026-03-02 — Test/asset guardrails:** DB-backed tests fail-fast unless `DATABASE_URL` DB name contains `test` (local safe default used: `localhost:5433/grant_reviewer_test`); pre-commit blocks newly added files over 500KB.
- **2026-03-04 — Review-request digest canonicalization:** validate digest against schema-validated snapshot projection with `exclude_unset=True`; including defaulted fields in canonicalization (e.g., `required=False`) can create false `CALL_CONFIG_DIGEST_MISMATCH` regressions.

- 2026-03-04: WF-0053 governance gate uses `backend/scripts/check_contract_boundary_governance.py --changed-path-file`; CI computes git diff paths and checker derives evidence bundles when none are passed. Why: prevents vacuous pass when no explicit args are supplied.

- 2026-03-04: Pipeline typing must support both `ActivatedCallConfigSnapshotV1` and plain dict snapshots in `run_review_pipeline`; coercing model-only broke WF-0045 contract tests. Why: contract suites instantiate `ReviewRequestV1` directly with dict snapshots for matrix cases.
