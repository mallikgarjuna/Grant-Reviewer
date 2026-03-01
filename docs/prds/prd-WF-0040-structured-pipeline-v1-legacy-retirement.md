# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: prd
Version: v0.1
Status: Ready for Tasks
Last Updated: 2026-03-01

## 0. User Stories (MVP)

- US1: As an operator, I want a gated legacy-retirement plan, so I can remove fallback logic without unsafe downtime risk.
- US2: As an engineer, I want deterministic verification and rollback gates, so deprecation decisions are evidence-based.
- US3: As a researcher, I want stable review behavior while migration completes, so trust is not disrupted.

## Deferred Stories (Not in MVP)

- DS1: Broader pipeline-v2 refactors.
- DS2: New product UX features unrelated to structured-review engine retirement.

## 1. In Scope

- Formal deprecation gates from dual-path to single-path execution.
- Runtime switch to v1-only behavior after evidence gate.
- Removal of legacy structured-review execution branches.
- Removal/cleanup of obsolete env logic tied to dual-engine routing.
- Regression tests and docs/runbook updates for single-engine operations.

## 2. Out of Scope

- Public API schema changes.
- Call-definition redesign.
- New ingestion model scope.

## 3. User / System Flow

### Happy path

1. Operator runs readiness checks (replay/parity/error/latency windows) and confirms retirement gate criteria.
2. Backend routes all structured-review requests via `pipeline_v1`.
3. Observation window remains green.
4. Legacy runtime code and dual-path flag logic are deleted.
5. Regression suite passes; docs and runbook switch to single-engine instructions.

### Failure path (pre-deletion gate fails)

1. Gate checks show parity or reliability issues.
2. Retirement pauses; no code deletion proceeds.
3. Issues are fixed and gate checks rerun.

### Failure path (post-switch instability before deletion)

1. v1-only runtime switch shows threshold regressions during observation window.
2. Operator uses pre-defined rollback mechanism (config/runbook) while legacy code still exists.
3. Code deletion is blocked until new green window is achieved.

## 4. Functional Requirements

- FR1 (US1): Define explicit retirement gate checklist and required evidence artifacts.
- FR2 (US2): Keep replay/parity and rollout-health scripts as hard gate inputs.
- FR3 (US1, US3): Switch runtime behavior to v1-only without API contract changes.
- FR4 (US1): Remove legacy structured-review execution path only after FR1/FR2 gates pass.
- FR5 (US2): Remove dual-engine routing env logic that is obsolete after v1-only cutover.
- FR6 (US2, US3): Maintain telemetry signals needed to detect regressions in v1-only mode.
- FR7 (US1): Update operational runbook to single-engine mode with rollback notes and escalation steps.

## 5. Data & API Contracts

- No request/response shape change for:
  - frontend -> BFF structured-review create flow,
  - BFF -> backend structured-review call,
  - backend review detail/listing endpoints.
- Idempotency contract remains unchanged.
- Error-code taxonomy must remain stable; any changes require explicit ADR and migration notice.

## 6. Components / Modules

- `backend/main.py`: routing simplification to single v1 path.
- `backend/app/services/structured_reviewer_service.py`: remove legacy-only execution entrypoints/helpers no longer needed.
- `backend/scripts/replay_structured_rollout.py`: retained as regression gate.
- `backend/scripts/evaluate_rollout_health.py`: retained as regression gate.
- `backend/tests/`: update/remove dual-path tests; add v1-only contract coverage.
- `backend/README.md` and docs workflow files: update operational instructions.

## 7. Edge Cases

- Requests for calls previously never canaried: must still execute deterministically via v1 and preserve contract semantics.
- Missing/invalid call config must keep stable error behavior.
- Observability must continue after legacy telemetry labels are removed/normalized.

## 8. Testing Decisions (TDD)

- Use RED/GREEN/REFACTOR for all behavior edits.
- Keep contract tests for API/status/error/idempotency unchanged where possible.
- Add negative tests for unsupported or malformed structured submissions in v1-only mode.
- Re-run replay and health scripts as part of verification gate before and after deletion.

## 9. Telemetry (Minimal)

- Required signals in v1-only mode:
  - structured-review request count by call code,
  - status and error code distributions,
  - latency p50/p95,
  - explicit deployment marker for “legacy retired”.

## 10. Rollback & Cutover Policy

- Phase R1 (pre-delete): config rollback allowed and tested.
- Phase R2 (delete-ready): only enter after a full green observation window.
- Phase R3 (post-delete): emergency rollback is code rollback (git deploy rollback), not runtime branch toggle.

## 11. Open Questions

- Required observation window duration before deletion (recommend 7 days).
- Minimum production sample size per canaried call for removal confidence.

## 12. Changelog

- v0.1 (2026-03-01): Initial PRD for controlled deprecation program after WF-0039 rollout completion.
