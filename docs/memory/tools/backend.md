<!-- docs/memory/tools/backend.md -->
# Backend Quirks

- **Script Paths:** When running backend scripts, use `cd backend && PYTHONPATH=. uv run python scripts/my_script.py`.

- **Database variables:** `DATABASE_URL` is explicitly required; the backend no longer falls back to SQLite when unset.

- **2026-03-02 — Test/asset guardrails:** DB-backed tests fail-fast unless `DATABASE_URL` DB name contains `test` (local safe default used: `localhost:5433/grant_reviewer_test`); pre-commit blocks newly added files over 500KB.

- **2026-03-04 — Review-request digest canonicalization:** validate digest against schema-validated snapshot projection with `exclude_unset=True`; including defaulted fields in canonicalization (e.g., `required=False`) can create false `CALL_CONFIG_DIGEST_MISMATCH` regressions.

- 2026-03-04: WF-0053 governance gate uses `backend/scripts/check_contract_boundary_governance.py --changed-path-file`; CI computes git diff paths and checker derives evidence bundles when none are passed. Why: prevents vacuous pass when no explicit args are supplied.

- 2026-03-04: Pipeline typing must support both `ActivatedCallConfigSnapshotV1` and plain dict snapshots in `run_review_pipeline`; coercing model-only broke WF-0045 contract tests. Why: contract suites instantiate `ReviewRequestV1` directly with dict snapshots for matrix cases.

- 2026-03-05: PyYAML can parse unquoted GitHub workflow key `on:` as boolean `True`; CI-workflow tests should read `workflow.get("on")` with fallback to `workflow.get(True)` for deterministic trigger validation. Why: avoids false negatives in YAML-based workflow contract tests.

- 2026-03-05: GitHub Actions `run:` steps should explicitly export `GITHUB_TOKEN: ${{ github.token }}` when backend tooling expects `GITHUB_TOKEN` env var; context availability alone is not enough for subprocess/env-based API auth.

- 2026-03-05: WF-0056 apply preflight discovery must fail closed with evidence on discovery/API exceptions (do not raise uncaught), and rollback rehearsal should stage snapshots via `actions/download-artifact` before CLI restore. Why: preserves deterministic operator evidence and prevents false “live rehearsal” paths that never access staged snapshot artifacts.

- 2026-03-05: Env gotcha: `uv` may be missing on PATH under pyenv/shell variations; prefer `python -m uv` (or fix shell init) when repo scripts fail to resolve `uv`.

- 2026-03-06: `StructuredReviewerService` review-request payload must remain `ActivatedCallConfigSnapshotV1`-compliant (`schema_version: v1`, strict expectation keys only). Extra snapshot fields (e.g. `reviewer_policy_prompt_by_node`) or defaulted expectation keys included in digest input can trigger `MALFORMED_REVIEW_REQUEST` / `CALL_CONFIG_DIGEST_MISMATCH` and surface as `Review Failed`.

- 2026-03-06: Stage gating must use canonical call-definition stage metadata (`evaluation_elements.stage` + `proposal_nodes.node_expectations`) when available; fallback node-id heuristics are legacy-only. Why: avoid frontend/backend drift where `BOTH` nodes render for Step 2 but API rejects with `REVIEW_STAGE_NODE_MISMATCH`.

- 2026-03-06: Daily quota default is now relaxed in dev-like app envs (`APP_ENV` in `dev/development/local`) when `FREE_DAILY_REVIEW_LIMIT` is unset; explicit env value always wins. Why: prevent local workflow lockouts while preserving prod default enforcement.

- 2026-03-07: If a newly authored canonical call does not appear in Funding Call dropdown, or ERC CoG shows "nested sections not yet supported", check local DB projection first: stale/missing ingest can leave `erc_cog_2026_full` on legacy leaf IDs and omit `MSCA-PF-2025`. Re-run `uv run python scripts/ingest_call.py data/calls/canonical/erc/erc_cog_2026_full.yaml` and `.../msca/msca_pf_2025_full.yaml`. Why: frontend reads active calls/nodes from DB, not directly from YAML files.

- 2026-03-08: WF-0063 primary-path guardrails are call-definition driven: `runtime_config.split_visibility_reviewability_enabled` gates supporting-node rejection, and `proposal_nodes.node_role` is reused across config/nodes/tree/review-detail surfaces. Why: keeps rollback to legacy behavior as a metadata flip with no YAML re-authoring or extra DB flags.

- 2026-03-09: `StructuredReviewerService.generate_structured_review_pipeline_v1()` still routes assessable cards through `pipeline_v1`, while `ReviewExecutionCore` already exists with stub-backed actionable feedback generation. Why: WF-0069 planning should treat service routing as a likely smallest actionability seam before broader prompt/UI work.

- 2026-03-09: Structured review detail ordering is still node-order-first (`ReviewRepository.get_review_cards_ordered()` and `backend/main.py::_order_review_cards`), so fail-closed missing-context cards can surface ahead of actionable submitted-node cards. Why: WF-0069 prioritization closure may need a small output-order seam even if actionable feedback exists upstream.
- 2026-03-14: WF-0081 Alembic enum reuse: when `op.create_table()` reuses existing Postgres enum types like `reviewrating` and `assessmentstatus`, use `sqlalchemy.dialects.postgresql.ENUM(..., create_type=False)` instead of generic `sa.Enum(...)`. Why: the generic enum objects can still emit duplicate `CREATE TYPE` DDL during upgrade and fail the migration.
- 2026-03-14: WF-0081 tracer bullet keeps `StructuredReviewerService.generate_structured_review_pipeline_v1(..., detail_mode=...)` defaulted to `legacy_cards`; only callers that explicitly pass `reviewed_node_findings` persist `ReviewFinding` rows. Why: this preserves legacy structured-review callers/tests while the rollout is still task-sliced.
