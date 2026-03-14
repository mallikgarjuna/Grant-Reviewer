<!-- docs/memory/tools/testing.md -->
# Testing Isolation & Practice

- **DB Isolation (Tests):** Never run tests against the dev DB. Always isolate them. Tests must run only when `DATABASE_URL` points to a test database whose name includes `test`.
  - Example: `cd backend && docker compose -f docker-compose.test.yml up -d && export DATABASE_URL=...  # match backend/docker-compose.test.yml && uv run pytest`

- **Reset Scripts:** Use `backend/scripts/reset_dev_db.sh` and `backend/scripts/reset_test_db.sh` to get deterministic local state. This is mandatory preflight before QA/testing.

- **Linting vs Legacy:** Enforce strict linting (`ruff`, `mypy`) on *new* code, but use per-file ignores or excludes for legacy code to avoid blocking progress. "Changed-files lint now, full debt cleanup as separate task."

- **Verification Before Commit:** Always require at least one targeted verification (test, lint, build, or manual check) per Phase 3 subtask *before* committing.

- **2026-03-01 — Matrix-driven contracts:** When using a shared fixture matrix across test surfaces, avoid global row-count assertions in one module. Enforce coverage and schema by surface, and ensure PROMPT_ONLY policy tests assert prompt-influence (not just non-blocking behavior).

- **2026-03-03 — Stage gate compatibility:** If compliance gates validate `stage_ref`, prefer format-level checks (for example `STEP_<int>`) over single-value allowlists to avoid breaking call-agnostic stress fixtures that legitimately use multiple stage refs.

- **2026-03-04 — Canonical digest in tests:** For request validator tests, build `call_config_digest` from `ActivatedCallConfigSnapshotV1.model_validate(snapshot).to_canonical_payload()` (not raw snapshot JSON), otherwise defaults/coercions trigger false digest-mismatch failures.

- **2026-03-04 — Contract gate selection strategy:** Prefer `pytest -m contract_gate` over WF-name `-k` expressions in CI. Marker selection is fail-closed when no tests match and avoids namespace drift when new WFs add contract tests.

- **2026-03-04 — Real snapshot compatibility grounding:** For producer-compat matrix tests, include `source_call_path` + `grounding_element_ids` in fixtures and assert IDs exist in source call `evaluation_criteria/evaluation_elements` before request-validation assertions; prevents synthetic drift disguised as "real snapshot" coverage.

- **2026-03-04 — Strict marker enforcement:** Run CI contract-gate with `--strict-markers` so unregistered marker usage fails early instead of silently bypassing test intent.

- **2026-03-04 — WF-0021 ingest hardening:** Concurrent v2 ingest can race on unique keys (agency/call/doc). Keep a one-retry `IntegrityError` path in ingestion, and run migration downgrade/re-upgrade smoke only against isolated PostgreSQL test databases (not SQLite).

- **2026-03-06 — Postgres test-run locking:** `backend/scripts/verify_tests_postgres.sh` and `backend/scripts/reset_test_db.sh` now take a shared `flock` lock under `/tmp` before resetting or using the isolated Postgres test DB. Why: concurrent verification runs can race on `drop_all/create_all` and produce false `UndefinedTable` failures.

- **2026-03-07 — WF-0061 DB selector contention:** Do not run DB-mutating pytest selectors in parallel against the same local Postgres test DB; serialize runs or use the repo reset/verify scripts first. Why: parallel `drop_all/create_all` can deadlock or leave enum/table state collisions (`duplicate type`, `undefined table`).

- **2026-03-08 — WF-0065 cross-call evidence discipline:** `backend/tests/test_api.py` already has real-call client factories for `erc_cog_2026_full`, `erc_stg_2026_full`, and `MSCA-PF-2025`, but the current `QUOTA_EXCEEDED` / `REVIEWS_DISABLED` assertions still run through the generic synthetic `create_client_with_seed` path. Why: avoid overstating multi-call fail-closed evidence during WF-0065 planning/audit work.

- **2026-03-08 — WF-0065 DB test execution:** Run WF-0065 DB-backed selectors serially with explicit `DATABASE_URL` set to the isolated test DB (e.g., `grant_reviewer_test`). Why: parallel runs can hang on DB reset/metadata locks and block deterministic verification.

- **2026-03-08 — Walkthrough evidence counts can drift:** For WF closure docs, re-run listed verification commands and update numeric pass/deselect totals instead of copying earlier counts (example: `pytest -m no_db` moved to `234 passed, 179 deselected`). Why: stale totals create audit noise even when behavior is correct.

- **2026-03-08 — Frontend test command reality:** `frontend` has no `npm test` script; use `npm run test:ui` for the bundled UI suite or `npx vitest run <paths> -t <selector>` for WF-scoped selectors. Why: audit/verification commands that call `npm test` fail before any test executes.

- **2026-03-09 — WF-0068 fail-closed decision checks:** In evidence-bundle validators, gate `proceed_to_narrow_follow_on_wf` on `coverage_status == locked` and `baseline_consistency_status == consistent`, and enforce unique `item_id` across both raw outputs and records. Why: without these checks, proceed decisions can pass through drifted coverage/baselines or ambiguous traceability mappings.

- **2026-03-09 — DB-backed selector orchestration:** Do not run multiple DB-mutating pytest commands in parallel in the same automation step; serialize them and reset test DB first. Why: concurrent `drop_all/create_all` paths trigger Postgres enum/table deadlocks or undefined-table races that look like code regressions.

- **2026-03-09 — WF-0069 replay role invariants:** In `backend/scripts/evaluate_wf_0069_actionability.py`, validate exact `item_id -> role` (stress vs baseline) in addition to `item_id -> call_id` before scoring. Why: role drift can silently bypass the stress gate and produce false closure.

- **2026-03-10 — Zsh globbing on Next.js `[param]` paths:** When running `npx vitest run` against test files under `src/**/[routeParam]/...`, quote the path (or escape `[`/`]`) or zsh will treat it as a glob and fail before tests execute.

- **2026-03-10 — Playwright WF spec parallelism:** Do not launch multiple `npx playwright test e2e/wf-0072-*.spec.ts` commands in parallel locally; each command starts a web server on `:3000` and parallel starts can fail with `EADDRINUSE`. Run WF-scoped specs serially (or override `PLAYWRIGHT_APP_PORT` per process).

- **2026-03-11 — WF-0073 DB verify sequencing:** When running multiple DB-backed pytest selectors that each call `reset_database()` (drop/create all), execute them sequentially against the same PostgreSQL test DB to avoid lock-order deadlocks (`DROP TABLE ... deadlock detected`). Why: parallel DB test invocations can contend on DDL locks and produce false-negative verification failures.
- **2026-03-11 — Postgres verify startup race:** `backend/scripts/verify_tests_postgres.sh` can false-fail on the first readiness check immediately after `reset_test_db.sh` because the container may report `starting` while `grant_reviewer_test` is still being created. If the container is otherwise healthy, rerun with `RESET_DB=0` against the already-running test DB before treating it as a code regression.
- **2026-03-12 — Validator seam verification:** If a task changes `backend/app/engine/review_request_validator.py` or strict request-contract models, verify both `backend/tests/engine/test_review_request_contracts.py` and `backend/tests/test_review_request_validator.py`. Why: engine-focused contract tests do not fully cover the shared validator baseline, so single-suite verification can miss hidden coupling.
- **2026-03-12 — WF-0076 subordinate prompt contract checks:** Treat expectation-level `subordinate_prompts` as additive; no-carriage payloads stay valid, but duplicate subordinate-prompt IDs within one expectation must fail closed in `validate_review_request_payload`. Why: proves compatibility and strictness simultaneously.
- 2026-03-14 — WF-0079 migration proof must use a temporary PostgreSQL test database derived from a safe `DATABASE_URL`; SQLite Alembic runs fail on the legacy constraint-alter steps before the new migration is reached. Why: migration evidence against SQLite is a tooling false-negative, not an honest WF regression.
- 2026-03-14 — Browser validation after schema WFs should check `alembic current` on the local dev DB before trusting a protected-submit failure. Why: stale dev schemas can surface as live `500` submit errors even when isolated tests and migrations already pass.
