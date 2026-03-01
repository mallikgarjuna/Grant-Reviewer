# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: brainstorm
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-01

## 1. Problem Statement

The app still carries a legacy structured-review execution path after WF-0039 rollout guardrails were shipped. Keeping two engines increases operational and cognitive overhead, and creates future drift risk. We need a controlled deprecation program that retires the legacy path safely, with measurable gates and rollback coverage.

Contract notes / non-obvious constraints:
- No “big-bang” cutover; retirement must be gated by parity evidence and canary history.
- No API contract regressions for frontend/BFF clients during deprecation.
- Rollback must remain configuration-first until final code deletion is complete.
- Legacy code removal is allowed only after explicit evidence checkpoints pass.

## 2. Desired Outcome

- `pipeline_v1` becomes the only structured-review execution path in runtime behavior.
- Legacy routing flags and dead compatibility branches are removed from backend runtime code.
- Operational docs and tests reflect single-engine truth.
- If rollback is needed before final deletion, rollback path is explicit and rehearsed.

## 3. Target User / Actor

- Primary: platform operator/engineer maintaining safe production behavior.
- Secondary: end users submitting reviews who should see stable outcomes.

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
