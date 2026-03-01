# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: brainstorm
Version: v0.7
Status: Draft Complete
Last Updated: 2026-03-01

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0040-structured-pipeline-v1-legacy-retirement.md`

## Contract Safety (SSOT)

- This brainstorm is the SSOT for decisions/contracts (what we will implement).
- The Q&A transcript is rationale only; it must not introduce new contracts.
- Any contract discovered during implementation must be promoted into this brainstorm (do not let “truth” live only in code or in Q&A).

## Definitions (Scope Guard)

- "Legacy" in this WF means: the legacy structured-review engine execution path for `POST /api/structured-review`.
- Out of scope unless explicitly needed: call-config/UI mode naming such as `ui_mode="legacy_single_snippet"`.

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

## Evidence Gates (Deletion Preconditions)

Before deleting legacy engine code or removing routing/flag branches:
- Produce a replay/parity artifact and evaluate it using existing rollout scripts.
- Produce a rollout health evaluation output (error/contract-error/latency thresholds) for the defined observation windows.
- Ensure API contract tests are green, and add targeted tests for v1-only routing behavior.
- Record evidence locations + decision in the WF-0040 walkthrough (readiness checklist SSOT).

## Rollback Posture

- Pre-deletion (legacy still exists): rollback is operational and explicit (runbook-driven); switching engines is not the long-term posture.
- Post-deletion: rollback is revert-deploy; there is no runtime engine-choice switch.

## Rollback Semantics (Clarified)

During the v1-only observation window (pre-deletion), we must support an explicit, configuration-first rollback to the legacy engine path (while legacy code still exists).
After legacy code deletion, rollback is revert-deploy only; there is no runtime engine-choice switch.

## API Contract Invariants (Concrete)

Before any routing change, enumerate the concrete error/response semantics for `POST /api/structured-review` that must remain stable (idempotency digest mismatch, expectation resolution errors, timeout behavior, validation ordering).
These invariants must be covered by targeted API/contract tests before switching prod routing.

## Explicit Boundary (Not A Refactor WF)

This WF is a controlled deprecation of the legacy engine execution path, not a shared-core refactor or pipeline redesign.

## Reversibility Guarantee

All steps prior to legacy code deletion must be reversible via runbook/config (no irreversible actions before the deletion gate).

## Required Tests (Minimum)

Add/confirm an API-level test that proves the legacy engine path is unreachable when v1-only mode is enabled, and a contract test suite covering the enumerated API invariants.

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

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0040-structured-pipeline-v1-legacy-retirement.md` (Section 4)

Rough idea decisions (selected):
- Enforce v1-only by making `/api/structured-review` route to `pipeline_v1` (remove conditional selection once gates are satisfied).
- Retirement sequence: evidence first (replay/health) -> v1-only switch -> observation window -> delete legacy.
- Readiness checklist SSOT lives in the WF walkthrough artifact.
- Environment progression: dev/staging first, then prod with explicit approval checkpoint.
- “No behavior change first”: strengthen tests + evidence references before changing routing behavior.

## 5. Constraints

- Do not change public API request/response schemas.
- Keep idempotency behavior stable.
- Do not break existing call YAML ingestion contracts.
- Preserve auditability and telemetry during transition.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0040-structured-pipeline-v1-legacy-retirement.md` (Section 5)

Constraint decisions (selected):
- Public API contract invariants: request/response schemas + error semantics remain stable throughout.
- Idempotency invariants: existing digest mismatch and expectation resolution error behavior remains unchanged.
- Retirement must not alter call YAML ingestion/canonicalization contracts.
- Rollback posture: while legacy exists, rollback is operational and explicit; after deletion, rollback is revert-deploy.
- Time constraint: prioritize de-risking gates and observability over speed of deletion.

## 6. Risks / Unknowns

- Hidden dependency on legacy behavior in edge cases.
- Incomplete observability can mask regressions.
- Premature code deletion can remove practical rollback options.
- Test suite may rely implicitly on legacy helpers.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0040-structured-pipeline-v1-legacy-retirement.md` (Section 6)

Risk/unknown decisions (selected):
- Highest risk class: edge-case contract and error semantics regressions; guard with targeted API/contract tests.
- Observability gaps are treated as blockers to switching prod routing to v1-only.
- Naming collision risk ("legacy" in UI mode) is documented; scope remains engine-execution retirement only.
- Deletion is gated by explicit evidence bundle + approval checkpoint.
- Unknown: exact window durations/thresholds and rollback source-of-truth config must be made explicit in Phase 1 planning/runbook.
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
