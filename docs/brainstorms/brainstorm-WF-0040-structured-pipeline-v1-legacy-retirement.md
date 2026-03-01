# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: brainstorm
Version: v0.4
Status: Draft Complete
Last Updated: 2026-03-01

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0040-structured-pipeline-v1-legacy-retirement.md`

## Repo Reality Snapshot (Read-Only) (2026-03-01)

- `backend/main.py` still selects `legacy` vs `pipeline_v1` for `/api/structured-review` using a feature flag + allowlist/per-call gating.
- Rollout guardrails exist as scripts: `backend/scripts/replay_structured_rollout.py` + `backend/scripts/evaluate_rollout_health.py`.
- Tests cover `pipeline_v1` engine behavior, determinism/stress, and telemetry (`engine_path`).
- API tests already assert v1 routing when enabled; retirement likely needs tests asserting v1-only when in retirement mode.
- “legacy” terminology exists in call-config/UI mode (`ui_mode="legacy_single_snippet"`) and may not be the same as the legacy engine path (naming collision risk).

## 1. Problem Statement

The app still carries a legacy structured-review execution path after WF-0039 rollout guardrails were shipped. Keeping two engines increases operational and cognitive overhead, and creates future drift risk. We need a controlled deprecation program that retires the legacy path safely, with measurable gates and rollback coverage.

Contract notes / non-obvious constraints:
- No “big-bang” cutover; retirement must be gated by parity evidence and canary history.
- No API contract regressions for frontend/BFF clients during deprecation.
- Rollback must remain configuration-first until final code deletion is complete.
- Legacy code removal is allowed only after explicit evidence checkpoints pass.

Primary driver (selected): drift + maintenance overhead; secondary: operational risk.

## 2. Desired Outcome

- `pipeline_v1` becomes the only structured-review execution path in runtime behavior.
- Legacy routing flags and dead compatibility branches are removed from backend runtime code.
- Operational docs and tests reflect single-engine truth.
- If rollback is needed before final deletion, rollback path is explicit and rehearsed.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0040-structured-pipeline-v1-legacy-retirement.md` (Section 2)

Success signals (selected):
- Primary: 100% of `/api/structured-review` runtime executions use `pipeline_v1` for a full observation window in staging and production.
- Observation windows are explicit, checklist-driven, and required to be green before deletion.
- Evidence bundle required before deletion: replay/parity artifact + rollout health evaluation output + API contract tests (all referenced from the readiness checklist).
- Call coverage scope: validate currently-supported calls only (no expansion); ensure gating/allowlist behavior does not hide behavior changes.
- Telemetry: keep `engine_path` but it should always be `pipeline_v1`; ops expectations updated to single-engine truth.

## 3. Target User / Actor

- Primary: platform operator/engineer maintaining safe production behavior.
- Secondary: end users submitting reviews who should see stable outcomes.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0040-structured-pipeline-v1-legacy-retirement.md` (Section 3)

Actor decisions (selected):
- Gate runner: backend/platform engineer on-call.
- Pre-flip requirement: documented runbook + metrics/alerts that make regressions obvious/actionable.
- Legacy deletion approval: explicit tech lead/repo owner sign-off checkpoint.
- Call ownership: platform owns global behavior; consult call owners only on specific regressions.

## 4. Rough Idea (Unstructured Thinking)

- Treat retirement as a deprecation program with stage gates:
  1. Freeze and audit legacy usage.
  2. Enforce v1-only in controlled envs.
  3. Validate parity and reliability over observation windows.
  4. Remove fallback toggles and legacy execution code.
  5. Clean tests/docs and finalize runbooks.

## 5. Constraints

- Do not change public API request/response schemas.
- Keep idempotency behavior stable.
- Do not break existing call YAML ingestion contracts.
- Preserve auditability and telemetry during transition.

## 6. Risks / Unknowns

- Hidden dependency on legacy behavior in edge cases.
- Incomplete observability can mask regressions.
- Premature code deletion can remove practical rollback options.
- Test suite may rely implicitly on legacy helpers.

## 7. MVP Definition

A safe MVP deprecation is complete when:
- All structured-review traffic runs on `pipeline_v1` in staging and production for a full observation window.
- Replay/parity and error/latency thresholds remain green for the window.
- A formal “removal readiness” checklist is complete.
- Legacy runtime path + routing flag branches are removed with passing regression tests.

## 8. Explicit Non-Goals

- Re-architecture of prompt strategy beyond removing legacy code paths.
- New frontend UX scope unrelated to engine retirement.
- Expanding call coverage scope beyond validating current supported calls.

## Open Questions / Deferred

- Define parity acceptance: strict equality vs “no regressions” thresholds + spot checks (Phase 1).
- Confirm rollback mechanism and which config/flags are the source of truth during observation windows (Phase 1).
- Disambiguate scope: legacy engine execution retirement vs call-config/UI “legacy_*” fallbacks (Phase 1).
- Define exact observation window durations and thresholds by environment (Phase 1; via readiness checklist).
