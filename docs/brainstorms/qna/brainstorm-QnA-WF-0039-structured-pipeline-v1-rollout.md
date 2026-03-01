# WF-0039 — Structured Pipeline v1 Rollout

Artifact: brainstorm-qna
Version: v0.2
Status: Draft
Last Updated: 2026-03-01

---

## Preflight — Step 1 (Long-Form Problem Intake)

User instruction: "go with your recommendations" for Q1–Q5.

### Rollout narrative (recommended baseline)

1. Goal:
- Safely roll out `pipeline_v1` for structured reviews call-by-call with instant rollback, while preserving externally visible behavior (status codes, error codes, and review card semantics) for the same inputs.

2. Where it runs (env + entrypoints):
- `staging` first, then `prod`.
- Entry points in scope: frontend/BFF `POST /api/bff/structured-review` end-to-end and backend `POST /api/structured-review`.

3. Current vs desired behavior:
- Current: structured review engine path is gated by env vars and call config availability.
- Desired: allowlisted calls deterministically use `pipeline_v1`; all others deterministically use legacy.

4. Success criteria:
- No increase in 5xx; no increase in contract-error 4xx on the same payloads.
- p95 latency does not regress beyond an agreed budget; initial default: no worse than legacy by >20%.
- Parity: preserve user-visible outputs (card count, ordering, ratings) unless explicitly accepted and documented.

5. Rollout strategy:
- Start with one canary call code (recommended: `nwo_veni_2025_preproposal`).
- Stage: enable global flag + allowlist canary only; smoke + replay; monitor for a defined window.
- Prod: repeat with low volume; then expand allowlist call-by-call.

6. Monitoring:
- Track engine selection, status outcomes, contract error codes, idempotency conflicts, latency p50/p95, and request volume per call.

7. Rollback:
- Flip env vars (global disable or remove call code from allowlist) and redeploy/restart.
- Trigger on contract regressions, repeatable parity mismatches, or sustained latency/5xx regressions beyond thresholds.

8. Constraints / non-goals:
- No DB schema changes; no new public API shape changes; no frontend redesign; no legacy engine removal.

9. Open questions:
- Parity strictness, latency budget thresholds, and whether to use shadow-mode vs staged replay.

### Q1–Q5 (Phase 0.1 Step 1)

**Q1: Where does this rollout happen first?**
- A) Staging only (Recommended) — prove enable/disable + telemetry + rollback without user impact.
- B) Prod for a single internal user only — faster signal, higher risk.
- C) Prod for a single call allowlisted — real traffic, strict rollback required.
> Recommendation: A — Lowest blast radius; establishes rollback muscle-memory and observability. B/C are acceptable only after staging proves out the operational mechanics.
> Selected: A

---

## Section 1 — Problem Statement (5 Questions)

User instruction: "go with your recommendations" for Q1–Q5.

**Q1: Do we enforce “explicit allowlist required” as a hard guardrail in prod?**
- A) Yes (Recommended): in `prod`, if `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1` and `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` is empty, refuse to start or refuse to route to v1.
- B) No: rely on ops discipline to always set allowlist.
- C) Soft: allow it but emit loud warning logs/telemetry.
> Recommendation: A — This eliminates the highest-risk misconfiguration class (accidentally enabling v1 for all calls). B is not defensible; C still allows silent production drift.
> Selected: A

**Q2: What is the canary call code for first rollout?**
- A) `nwo_veni_2025_preproposal` (Recommended): most exercised structured call.
- B) `erc_stg_2026_full`: bigger call, higher risk.
- C) Custom: you name the call code.
> Recommendation: A — Use the most exercised structured call as the canary; it maximizes signal and reduces the chance of “passing” due to low usage.
> Selected: A

**Q3: Do we require a “forced engine” test-only bypass to validate both paths in staging?**
- A) Yes (Recommended): test-only header/env to force legacy vs v1 for verification (never enabled in prod).
- B) No: only validate by changing env vars + redeploy.
- C) Hybrid: force only in local/dev, not staging.
> Recommendation: A — Enables deterministic A/B verification without redeploy churn; must be explicitly test-only and disabled in prod.
> Selected: A

**Q4: Parity definition for rollout gate (minimum acceptable)**
- A) Structural parity (Recommended): same number of cards, same ordering, same rating per card; content text may differ.
- B) Strict parity: structural + exact text match (likely unrealistic).
- C) Contract-only parity: only status/error codes must match.
> Recommendation: A — Text-level parity is unrealistic with LLM variability; contract-only is too weak. Structural parity is enforceable and user-impact-relevant.
> Selected: A

**Q5: Rollout evidence required before expanding allowlist**
- A) Automated replay suite (Recommended): fixed payloads replayed N times, compare outputs + latency.
- B) Manual smoke only: submit a few times, eyeball results.
- C) Real-traffic only: monitor metrics, no replay harness.
> Recommendation: A — Manual-only and traffic-only approaches let regressions slip; replay gives deterministic, repeatable evidence.
> Selected: A

**Q2: What’s the rollout unit?**
- A) Per-call allowlist via `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` (Recommended) — smallest blast radius.
- B) Per-environment only (`STRUCTURED_REVIEW_PIPELINE_V1_ENABLED`) — simpler, bigger blast radius.
- C) Per-user allowlist (needs new gating work) — best isolation but extra scope.
> Recommendation: A — Aligns to existing gating code and lets us ramp call-by-call safely. B is too coarse; C expands scope.
> Selected: A

**Q3: What’s the parity requirement vs legacy behavior?**
- A) “No user-visible change” in cards/ratings for the same input (Recommended) — treat drift as a bug.
- B) “Mostly same” but improved findings allowed — requires explicit acceptance criteria.
- C) Parity only for errors/contracts, not for content — risky: silent behavior drift.
> Recommendation: A — Rollout WFs should default to no-regression; “improvements” must be a separate, explicitly accepted WF.
> Selected: A

**Q4: What telemetry/monitoring is mandatory before enabling prod?**
- A) Request count + error rate + latency + contract error codes + engine-mode tag (Recommended)
- B) Only error logs
- C) Full tracing + dashboards (bigger scope)
> Recommendation: A — Minimum viable observability to detect regressions quickly; B is insufficient; C is valuable but not required for the first safe rollout.
> Selected: A

**Q5: What’s the rollback trigger?**
- A) Any contract error regression or >X% error-rate increase (Recommended)
- B) Any content drift reports from users
- C) Only 5xx spikes
> Recommendation: A — Objective and automatable; B is too slow; C is too late.
> Selected: A
