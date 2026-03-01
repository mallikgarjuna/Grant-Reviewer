# WF-0039 — Structured Pipeline v1 Rollout

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-01

## 0. User Stories (MVP)

- US1: As an operator, I want to enable `pipeline_v1` per call code, so I can limit blast radius during rollout.
- US2: As an operator, I want deterministic rollback triggers tied to measurable telemetry, so I can disable `pipeline_v1` quickly and safely.
- US3: As a researcher, I want no user-visible review card regressions during rollout, so trust in review results is preserved.
- US4: As an engineer, I want reproducible rollout evidence from replay tests, so call-by-call expansion decisions are defensible.

## Deferred Stories (Not in MVP)

- DS1: Remove legacy structured-review engine path after rollout completion.
- DS2: Introduce full shadow-mode dual execution in production for all calls.
- DS3: Add per-user engine gating.

## 1. In Scope

- Define rollout-safe gating semantics for `pipeline_v1` in staging and production.
- Enforce production guardrail behavior for empty allowlist configuration.
- Define canary-first rollout sequence and allowlist expansion gates.
- Define parity gates and replay evidence requirements.
- Define rollback triggers and operator runbook expectations.
- Add minimal telemetry requirements for engine path observability.

## 2. Out of Scope

- No DB schema changes.
- No public API payload shape changes.
- No frontend UX redesign.
- No migration of legacy call YAMLs.
- No removal of legacy structured-review engine path.

## 3. User / System Flow

### Happy path (canary rollout)

1. Operator enables `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1` in staging and sets `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES=nwo_veni_2025_preproposal`. (US1)
2. User submits structured review through frontend `POST /api/bff/structured-review`; backend `POST /api/structured-review` routes the allowlisted call to `pipeline_v1`. (US1, US3)
3. Replay suite executes required canary payloads and compares structural parity + status/error-code behavior against legacy baseline. (US3, US4)
4. Metrics pass gate; operator expands allowlist to next call code in staging, then repeats in production. (US1, US2, US4)

### Failure path 1 (prod misconfiguration: global on + empty allowlist)

1. In production, operator sets `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1` but leaves `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` empty. (US1, US2)
2. System fails closed to legacy for all calls and emits loud error telemetry/logging; no request routes to `pipeline_v1`. (US1, US2)

### Failure path 2 (parity or error regression during canary)

1. Replay suite detects structural parity violation or sustained contract/5xx regression above threshold. (US2, US3, US4)
2. Operator removes canary from allowlist (or disables global flag) and redeploys/restarts.
3. System routes all calls to legacy path until issue is fixed and replay suite passes again. (US2)

### Failure path 3 (latency regression in canary window)

1. p95 latency regression exceeds defined threshold for canary call during observation window. (US2)
2. Operator executes rollback action and records incident note for follow-up tuning. (US2, US4)

## 4. Functional Requirements

- FR1 (US1): Gating uses existing env vars only: `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED` + `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES`.
- FR2 (US1, US2): In production, if global flag is on and allowlist is empty, route fail-closed to legacy (never implicit all-call enable).
- FR3 (US1): Rollout unit is per-call allowlist; first canary call code is `nwo_veni_2025_preproposal`.
- FR4 (US3): Rollout parity gate is structural parity for the same payloads: card count, card ordering, and card rating.
- FR5 (US4): Evidence gate requires automated replay suite with minimum `2 payloads x 20 replays`.
- FR6 (US4): Replay payload set includes one valid happy payload and one deterministic contract-error payload.
- FR7 (US2): Rollback triggers must include: unknown/new contract errors, sustained 5xx/4xx regression, structural parity violations, and p95 latency regression over threshold.
- FR8 (US2): Rollback action must be configuration-only and immediate (disable global flag and/or remove call from allowlist), followed by service restart/redeploy.
- FR9 (US2, US4): Telemetry must tag engine path (`legacy` vs `pipeline_v1`) and expose request counts, status outcomes, error codes, and latency.
- FR10 (US3): End-user API contract behavior remains unchanged (status-code semantics and idempotency behavior preserved).

## 5. Data & API Contracts

### 5.1 Environment Contract

- `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED`: `0|1` global rollout switch.
- `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES`: comma-separated call-code allowlist.
- Production guardrail:
  - If `ENV=prod` (or equivalent runtime production indicator) and global flag is `1` with empty allowlist, system must fail-closed to legacy path.

### 5.2 Request/Response Contract Preservation

- Frontend/BFF request shape for structured review remains unchanged. (FR10)
- Backend `/api/structured-review` response shape and error semantics remain unchanged. (FR10)
- Idempotency semantics remain unchanged:
  - missing key => validation error,
  - payload mismatch for same key => idempotency mismatch error,
  - matching key/payload => prior result reuse.

### 5.3 Replay Contract

- Replay comparator inputs:
  - same call id, stage, nodes payload, and idempotency strategy.
- Replay assertions:
  - structural parity (count/order/rating),
  - status/error-code stability,
  - latency window check vs baseline.

## 6. Components / Modules

- `backend/main.py`
  - owns routing decision between legacy and `pipeline_v1` for `/api/structured-review`.
  - enforce production fail-closed guardrail behavior.
- `backend/app/services/structured_reviewer_service.py`
  - owns `generate_structured_review()` and `generate_structured_review_pipeline_v1()` execution paths.
- `backend/app/engine/telemetry.py`
  - owns engine-path-aware telemetry primitives used by pipeline.
- `backend/scripts/`
  - rollout/replay operational script entrypoints for canary verification.
- `backend/tests/`
  - parity/regression coverage for gating behavior and replay assertions.

Design tree / ordering:
1. Lock guardrail semantics in backend route.
2. Add replay harness contract and assertions.
3. Add telemetry coverage + rollback trigger checks.
4. Document operator rollout sequence and evidence gate.

## 7. Edge Cases

- Empty allowlist in non-prod with global flag on: allowed for local/staging experimentation, but must be visible via warning telemetry.
- Unknown call code in allowlist: should not crash; call simply remains legacy-routed unless matched.
- Mixed-call submissions over time: per-request engine selection must be deterministic by call code.
- Engine fallback under misconfiguration must not mutate request/response contracts.
- Replay noise from LLM variability: structural parity gate intentionally avoids strict text parity.

## 8. Testing Decisions (TDD)

- Behavior changes use TDD with RED/GREEN/REFACTOR logs.
- Test seams:
  - route-level gating/guardrail behavior in backend API tests.
  - deterministic path selection tests for allowlisted vs non-allowlisted calls.
  - replay comparator tests for structural parity and error-code stability.
  - rollback trigger threshold evaluation tests.
- Boundary-only mocking:
  - mock external LLM boundary only; do not mock internal routing decisions or contracts.

## 9. Telemetry (Minimal)

- Required metrics/events:
  - structured-review request count by call code and engine path.
  - status distribution (`COMPLETED`, `FAILED`) by engine path.
  - contract error-code counts by engine path.
  - latency p50/p95 by engine path and call code.
- Required logs:
  - production guardrail activation (fail-closed reason).
  - rollback action execution marker.

## 10. Deferred / Not in MVP

- Full production shadow-mode.
- Legacy engine deprecation/removal.
- Per-user gating.
- Automated dashboard provisioning (beyond minimal metrics exposure).

## 11. Open Questions (if any)

- Threshold values for “sustained regression” (error-rate and latency) to be fixed in task phase.
- Exact observation window duration before allowlist expansion in production.
- Whether non-prod should also hard-fail closed for empty allowlist or only warn.

## 12. Changelog

- v0.1 (2026-03-01): Initial PRD from brainstorm
