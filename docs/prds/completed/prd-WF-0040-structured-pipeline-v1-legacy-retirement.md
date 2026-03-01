# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: prd
Version: v0.3
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

- Legacy engine retirement for `POST /api/structured-review` execution path only.
- Formal deprecation gates from dual-path to single-path execution.
- Runtime switch to `pipeline_v1` only after evidence gates are green.
- Removal of legacy structured-review execution branches.
- Removal/cleanup of obsolete env logic tied to dual-engine routing.
- Regression tests and docs/runbook updates for single-engine operations.

## 2. Out of Scope

- Public API schema changes.
- Call-definition redesign.
- New ingestion model scope.
- Renaming call-config/UI `legacy_*` naming unless required to unblock engine-path retirement.

## 3. User / System Flow

### Happy path

1. Operator runs readiness checks (replay/parity/error/latency windows) and confirms retirement gate criteria. (US1, US2)
2. Backend routes all structured-review requests through `pipeline_v1` while legacy code still exists for pre-deletion rollback. (US1, US2, US3)
3. Staging and production observation windows stay green for the checklist-defined durations and thresholds. (US1, US2)
4. Legacy runtime code and dual-path flag logic are deleted after explicit approval and evidence sign-off. (US1, US2)
5. Regression suite passes; docs and runbook switch to single-engine operations. (US1, US2, US3)

### Failure path (pre-deletion gate fails)

1. Gate checks show parity, contract-semantic, or reliability regressions. (US2, US3)
2. Retirement pauses and no routing change or code deletion proceeds. (US1, US2)
3. Team fixes issues and reruns gate checks before reattempting cutover. (US1, US2)

### Failure path (post-switch instability before deletion)

1. v1-only routing shows threshold regressions during observation window. (US2, US3)
2. Operator executes explicit, runbook-defined configuration rollback while legacy path still exists. (US1, US2)
3. Legacy deletion remains blocked until a fresh green observation window is completed. (US1, US2)

## 4. Functional Requirements

- FR1 (US1): Define explicit retirement gate checklist and required evidence artifacts.
- FR2 (US2): Keep replay/parity and rollout-health scripts as hard gate inputs.
- FR3 (US1, US3): Switch runtime behavior to v1-only without API contract changes.
- FR4 (US1): Remove legacy structured-review execution path only after FR1/FR2 gates pass.
- FR5 (US2): Remove dual-engine routing env logic that is obsolete after v1-only cutover.
- FR6 (US2, US3): Maintain telemetry signals needed to detect regressions in v1-only mode.
- FR7 (US1): Update operational runbook to single-engine mode with rollback notes and escalation steps.
- FR8 (US2, US3): Preserve concrete API error semantics during retirement (`CALL_CONFIG_DIGEST_MISMATCH`, `EXPECTATION_REF_UNRESOLVABLE`, `TIMEOUT`, validation ordering behavior).
- FR9 (US1, US2): Require explicit approval checkpoint in walkthrough checklist before deleting legacy code.
- FR10 (US1, US2): Use fixed observation-window thresholds and minimum production sample-size gates before deletion approval.

## 5. Data & API Contracts

### 5.1 Stable External Contracts

- Frontend -> BFF structured-review create request shape remains unchanged. (US3, FR3)
- BFF -> backend `POST /api/structured-review` request/response shape remains unchanged. (US3, FR3)
- Backend review detail/listing endpoint payloads remain unchanged. (US3, FR3)

### 5.2 Idempotency + Validation Contract

- Idempotency behavior remains unchanged: same key/same payload returns existing result; key/payload mismatch returns idempotency mismatch error. (US3, FR3)
- Validation ordering for malformed payloads stays stable relative to idempotency checks. (US3, FR8)

### 5.3 Error Semantics Contract

- Existing contract errors remain semantically stable during retirement, including digest mismatch and expectation resolution errors. (US3, FR8)
- Existing execution-failure semantics remain stable, including timeout/error classification and status behavior. (US3, FR8)
- Any contract-semantic change requires explicit architectural decision log entry before implementation. (US1, FR8)

### 5.4 State Transition Contract

- Pre-deletion: explicit configuration rollback is allowed and rehearsed while legacy code exists. (US1, FR7)
- Post-deletion: rollback is revert-deploy only; there is no runtime engine-choice switch. (US1, FR4, FR5)

## 6. Components / Modules

- `backend/main.py`
  - owns routing simplification to v1-only path for `POST /api/structured-review`.
- `backend/app/services/structured_reviewer_service.py`
  - remove legacy-only execution entrypoints/helpers after deletion gate.
- `backend/scripts/replay_structured_rollout.py`
  - retained and required for parity evidence gate.
- `backend/scripts/evaluate_rollout_health.py`
  - retained and required for rollout health threshold evaluation.
- `backend/tests/`
  - update/remove dual-path tests; add v1-only routing unreachability and API contract invariants coverage.
- `docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
  - readiness checklist SSOT with evidence links and approval checkpoint.
- `backend/README.md` and workflow docs
  - update operator runbook text to single-engine truth.

Design tree / ordering:
1. Strengthen contract tests + checklist evidence references (FR1, FR8).
2. Flip runtime to v1-only and run observation windows (FR2, FR3, FR6).
3. Delete legacy execution + obsolete routing logic (FR4, FR5, FR9).
4. Finalize docs/runbook and preserve telemetry expectations (FR6, FR7).

## 7. Edge Cases

- Requests for currently-supported calls that were lightly exercised in canary still must execute deterministically through v1 and preserve contract semantics. (US3, FR3, FR8)
- Missing/invalid call config keeps stable error behavior; no silent fallback contract changes. (US3, FR8)
- Observation-window gaps (missing telemetry series, missing replay artifacts) block deletion readiness. (US1, US2, FR1, FR6)
- UI/call-config `legacy_*` naming must not be interpreted as permission to widen scope beyond engine execution retirement. (US1)

## 8. Testing Decisions (TDD)

- Use RED/GREEN/REFACTOR for all behavior edits touching routing/deletion seams.
- Test seams:
  - API routing test that proves legacy path is unreachable when v1-only mode is active. (FR3, FR4)
  - API contract tests for idempotency + core error semantics invariants listed in Section 5. (FR8)
  - Script-level tests/verification for replay + rollout health gate output expectations. (FR1, FR2)
- Boundary-only mocking:
  - mock external LLM boundary only; do not mock routing-decision code or contract assertions.
- Evidence gate execution:
  - run replay and health scripts before v1-only switch,
  - rerun across defined observation windows before legacy deletion.

## 9. Telemetry (Minimal)

- Required signals in v1-only mode:
  - structured-review request count by call code and `engine_path` (expected steady-state `pipeline_v1`),
  - status and error code distributions,
  - latency p50/p95,
  - explicit deployment marker for “legacy retired”.

## 9.1 Observation Window + Sample Gates (MVP Defaults)

- Staging pre-delete gate:
  - at least 24 consecutive green hours in v1-only mode,
  - replay + rollout-health evidence captured and linked in walkthrough checklist.
- Production pre-delete gate:
  - at least 7 consecutive green days in v1-only mode,
  - minimum 50 completed structured-review requests per currently-supported call code,
  - no contract-semantic regressions for invariant errors in Section 5.
- Deletion approval requires all FR1/FR2/FR9/FR10 checklist items to be marked complete in the walkthrough SSOT.

## 10. Deferred / Not in MVP

- Shared-core/pipeline redesign beyond retiring legacy execution path.
- Broad naming cleanup of `legacy_*` identifiers outside blocking retirement surfaces.
- Expansion of call coverage scope beyond currently-supported calls.

## 11. Open Questions (if any)

- None for MVP Phase 2 planning.

## 12. Changelog

- v0.1 (2026-03-01): Initial PRD for controlled deprecation program after WF-0039 rollout completion.
- v0.2 (2026-03-01): Applied Phase 1 risk-audit revisions (traceability tags, explicit legacy scope boundary, concrete API invariants, checklist/approval gate requirements, and test seam hardening).
- v0.3 (2026-03-01): Resolved remaining audit deltas by pinning observation-window thresholds and production sample-size gates; cleared open questions for MVP planning.
