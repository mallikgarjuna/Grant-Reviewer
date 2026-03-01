# WF-0039 — Structured Pipeline v1 Rollout

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-01

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0039-structured-pipeline-v1-rollout.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- For each major decision, add 1–3 “Contract Notes / Non-obvious constraints” bullets and link to the relevant Q&A section header.

---

## Repo Reality Snapshot (Read-Only) (2026-03-01)

- Engine selection happens in backend `POST /api/structured-review` (FastAPI) via env vars: `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED` + optional per-call allowlist `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES`.
- BFF `POST /api/bff/structured-review` is a proxy and does not decide the engine; it enforces idempotency header and signs the request.
- Frontend submit flow always sends an `Idempotency-Key` and currently defaults `review_stage` to `STEP_1` in the universal submit form.
- Pipeline-v1 path stores `engine_path: "pipeline_v1"` in `Review.structured_payload` for traceability.
- Allowlist behavior: when `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1` and `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` is empty, pipeline-v1 is enabled for **all calls** (high risk if misconfigured in prod).

Open questions suggested by snapshot:
- Do we require `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` to be non-empty in production (policy/guardrail)?
- What is the canary call code and the exact ramp sequence (call-by-call)?
- What parity definition is required for a “successful rollout” (structural vs content parity)?
- What telemetry signals are required to make rollback decisions quickly?

---

## 1. Problem Statement

We need an operationally safe, incremental rollout of structured review `pipeline_v1` without breaking user-visible behavior or contracts, and with immediate rollback.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0039-structured-pipeline-v1-rollout.md` (Preflight + Section 1)

Contract notes / non-obvious constraints:
- Production safety requires explicit allowlisting: in production, do not rely on “empty allowlist means all calls” behavior.
- Rollout must preserve API contracts: status codes, error codes, idempotency semantics.
- Parity gate for rollout is structural parity: same number of cards, same ordering, same rating per card (content text may differ).
- Evidence gate for allowlist expansion requires an automated replay suite (not manual-only).
- Any “force engine” control is test-only and must not be available in production.
- Production guardrail (explicit): in `prod`, if `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1` and `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` is empty, **fail closed to legacy** (do not route any call to `pipeline_v1`) and emit a loud error signal.
- Legacy path retirement is out of scope (parked separately).

## 2. Desired Outcome

- For allowlisted calls, structured review requests deterministically run via `pipeline_v1`; for all others, they deterministically run via the legacy structured engine.
- Rollout is reversible via configuration (env var changes + redeploy/restart), with clear rollback triggers and monitoring.
- We have an explicit canary plan (staging first, then production) and parity criteria to decide expand/rollback.

## 3. Target User / Actor

- Primary: Developer/operator shipping production changes (you) who needs safe rollout and confidence.
- Secondary: End-user submitting a structured review who must not experience regressions.

## 4. Rough Idea (Unstructured Thinking)

- Treat this as an ops-safety WF: define rollout contracts, guardrails, and a verifiable ramp plan; implement only what is necessary to enforce/observe the plan.

## 5. Constraints

- No DB schema changes.
- No public API shape changes.
- No frontend redesign.
- No removal of legacy engine path (separate parked item).

## 6. Risks / Unknowns

- Silent “enable for all calls” if allowlist is omitted (misconfiguration risk).
- Parity scope ambiguity (structural vs content).
- Monitoring insufficiency leading to slow rollback.

## Open Questions / Deferred

- Exact rollback thresholds (set in Phase 1 PRD): acceptable error-rate delta, latency regression %, and minimum sample size window.
- Whether we need “shadow mode” computation (compute both engines but return one) vs staged replay only (default: staged replay only).
- Expansion schedule beyond canary (dates + call list), once staging evidence is recorded.

## 7. MVP Definition

In 2–3 days:
- Staging rollout: canary allowlist + explicit kill switch procedure + monitoring/telemetry signals defined and verified.
- Evidence gate (minimum): automated replay suite, run against staging:
  - 2 payloads x 20 replays each:
    - Payload A: minimal “happy path” structured submit for canary call.
    - Payload B: edge/invalid structured submit that deterministically triggers a contract error (stable error code).
  - Assertions:
    - Structural parity (card count/order/rating) between legacy and `pipeline_v1` for Payload A.
    - Stable status/error codes for Payload B.
    - p95 latency regression within agreed threshold (set in Phase 1 PRD).
- Production rollout: same mechanics with a controlled canary window and explicit rollback triggers.
- Rollback triggers (minimum, thresholds set in Phase 1 PRD):
  - Any new/unknown contract error codes appearing in v1 path.
  - Sustained increase in 5xx or contract-error 4xx over baseline.
  - Structural parity violations in replay suite or observed production canary samples.

## 8. Explicit Non-Goals

- Migrating legacy call YAMLs (e.g., ERC CoG v1 -> v2) in this WF.
- Removing legacy structured review engine code path.
- Reworking the structured review UX.
