# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: brainstorm-qna
Version: v0.2
Status: In progress
Last Updated: 2026-03-01

---

This file captures the full Phase 0.1 interactive Q&A transcript.
The main brainstorm remains SSOT for decisions/contracts.

---

## Preflight — Repo Reality Snapshot Decisions (2026-03-01)

**Brainstorming Q&A:**

**Q1: Does “legacy retirement” include only the legacy engine execution path, or also call-config/UI “legacy_*” fallbacks?**
- A) **Option A (Recommended):** Only the legacy engine execution path for `/api/structured-review` (the thing that generates reviews). Treat call-config/UI “legacy_*” as separate unless explicitly required.
- B) Option B: Include both legacy engine execution and call-config/UI “legacy_*” fallbacks in this WF.
- C) Option C: Define legacy as “anything not routed through `generate_structured_review_pipeline_v1`”, including related helpers.
> Recommendation: A — keeps the WF falsifiable and prevents scope creep due to naming collisions. B/C risk expanding to unrelated UI-mode semantics.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q2: What parity evidence do we accept as a gate for progressing toward deletion?**
- A) **Option A (Recommended):** Health + contract parity thresholds (error/contract-error/latency) plus targeted qualitative spot checks; not strict output equality.
- B) Option B: Strict output equality for a replay corpus (same cards/text).
- C) Option C: Only health thresholds; no replay/parity checks.
> Recommendation: A — strict equality is brittle for LLM-influenced outputs, while health-only (C) can miss correctness regressions. A matches “gated by evidence” without overfitting.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q3: What is the expected final state for routing flags/allowlists?**
- A) **Option A (Recommended):** Remove the legacy/v1 branching entirely; after retirement there is no “engine choice” flag because only `pipeline_v1` exists.
- B) Option B: Keep a v1 enablement flag permanently (kill legacy, but keep “off switch”).
- C) Option C: Keep per-call allowlist permanently.
> Recommendation: A — aligns with “single-engine truth” and reduces future drift surfaces. B/C preserve ongoing complexity; if an emergency switch is required, it should be a different, explicit mechanism (e.g., rate limiting / disable endpoint), not “run legacy”.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q4: What rollback mechanism is acceptable before final deletion?**
- A) **Option A (Recommended):** Configuration-first rollback that is explicit and rehearsed while legacy code still exists; after deletion, rollback is “revert deploy” not “switch engines”.
- B) Option B: Always keep a runtime switch between engines as rollback even post-deletion (contradiction).
- C) Option C: No rollback; proceed once staging is green.
> Recommendation: A — matches the brainstorm constraint “rollback remains configuration-first until final code deletion”. B contradicts the goal; C is unsafe.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q5: Should “legacy UI mode” terminology be renamed as part of this WF to reduce confusion?**
- A) **Option A (Recommended):** Not in this WF; document the distinction in the brainstorm and defer any renames unless they block retirement work.
- B) Option B: Rename immediately to avoid confusion (scope increase).
- C) Option C: Ignore it entirely.
> Recommendation: A — keeps scope contained but prevents future misunderstanding; B risks churn; C risks repeated confusion.
> **Selected: A (by user instruction: “go with recommendations”)**

---

## Section 1 — Problem Statement (2026-03-01)

**Brainstorming Q&A:**

**Q1: What is the primary driver for retiring the legacy path?**
- A) **Option A (Recommended):** Drift + maintenance overhead (two engines means inevitable divergence).
- B) Option B: Operational risk (harder incident response; hidden fallback behaviors).
- C) Option C: Product trust (users see inconsistent outcomes).
> Recommendation: A — this is the root cause; operational risk and trust issues are downstream effects of drift and duplicated logic.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q2: What exactly counts as “legacy structured-review execution path” for this WF?**
- A) **Option A (Recommended):** Only the legacy engine execution path for `/api/structured-review` (the thing that actually generates reviews).
- B) Option B: Both legacy engine execution and any “legacy_*” call-config/UI-mode fallbacks.
- C) Option C: Anything not routed through `StructuredReviewerService.generate_structured_review_pipeline_v1`.
> Recommendation: A — precise, falsifiable scope; avoids accidental broad refactors.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q3: Where is the biggest risk of unintended behavior change during deprecation?**
- A) **Option A (Recommended):** Edge cases and error contracts (timeouts, contract-error semantics, validation order).
- B) Option B: Latency and performance under load.
- C) Option C: Call-config parsing and proposal-node selection behavior.
> Recommendation: A — contract and error semantics are easiest to regress while “routing changes” look small. Latency is important but tends to be observable; contract drift can silently break clients.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q4: What is the “fail closed to legacy” stance supposed to be during Phase 0–1?**
- A) **Option A (Recommended):** Keep fail-closed behavior until evidence gates; then remove it when legacy is removed.
- B) Option B: Change it early to fail-closed to `pipeline_v1` (more aggressive).
- C) Option C: Keep dual-mode indefinitely but make v1 the default (no deletion goal).
> Recommendation: A — aligns with a gated program; B can turn config mistakes into production impact; C contradicts retirement.
> **Selected: A (by user instruction: “go with recommendations”)**

**Q5: What makes this problem falsifiable (so we know we solved it)?**
- A) **Option A (Recommended):** No code path exists that can execute legacy engine; tests confirm single-engine routing; rollout evidence recorded.
- B) Option B: Config flags removed and docs updated.
- C) Option C: A production canary window completes without regressions.
> Recommendation: A — combines code-level truth with evidence; B is insufficient; C is necessary but not sufficient without code deletion and test coverage.
> **Selected: A (by user instruction: “go with recommendations”)**

---

## Section 2 — Desired Outcome (2026-03-01)

**Brainstorming Q&A:**

**Q1: What is the top-level success metric for the retirement program?**
- A) **Option A (Recommended):** 100% of `/api/structured-review` runtime executions use `pipeline_v1` for a full observation window in staging and production.
- B) Option B: Legacy code deleted + tests green (code-only).
- C) Option C: Operational docs/runbooks updated (process-only).
> Recommendation: A — ties success to runtime truth and safety gating; B/C are necessary but not sufficient.
> **Selected: A**

**Q2: What is the minimum acceptable “observation window” definition for MVP?**
- A) **Option A (Recommended):** Explicitly define a window per env (staging + prod) in the readiness checklist; require a green window before deletion.
- B) Option B: “A couple days” informal.
- C) Option C: Only staging needs a window; prod is immediate after switch.
> Recommendation: A — forces falsifiable gates and prevents premature deletion.
> **Selected: A**

**Q3: What’s the required evidence bundle before allowing code deletion?**
- A) **Option A (Recommended):** Replay/parity artifact + rollout health evaluation output + API contract test pass, all referenced from a checklist.
- B) Option B: Only rollout health eval output.
- C) Option C: Only API tests.
> Recommendation: A — balances safety (observational + replay) with contract protection.
> **Selected: A**

**Q4: What is “good enough” for call coverage during retirement?**
- A) **Option A (Recommended):** Only currently-supported calls in prod (no expansion); ensure allowlist/call gating doesn’t hide unsupported-call behavior changes.
- B) Option B: Expand to more calls to be safe.
- C) Option C: Ignore call-level differences; routing is global.
> Recommendation: A — avoids turning this WF into a call-coverage program while still preventing hidden regressions due to gating.
> **Selected: A**

**Q5: What outcome do we want for telemetry after retirement?**
- A) **Option A (Recommended):** Keep `engine_path` telemetry but it should always be `pipeline_v1`; alerts/dashboards updated to assume single-engine.
- B) Option B: Remove `engine_path` entirely.
- C) Option C: Keep dual-engine metrics “just in case” even after deletion.
> Recommendation: A — preserves observability while removing ambiguity.
> **Selected: A**

---

## Section 3 — Target User / Actor (2026-03-01)

**Brainstorming Q&A:**

**Q1: Who is the primary “actor” responsible for running the retirement gates?**
- A) **Option A (Recommended):** Backend/platform engineer on-call (owns ops + rollback).
- B) Option B: Product engineer (feature owner, not on-call).
- C) Option C: SRE/DevOps only.
> Recommendation: A — authority and operational responsibility should match ownership of gates and rollback.
> **Selected: A**

**Q2: Who is the primary “customer” harmed if we get this wrong?**
- A) **Option A (Recommended):** End users/researchers (behavior regressions undermine trust).
- B) Option B: Internal engineers (time lost, incidents, maintenance overhead).
- C) Option C: Both equally (treat as co-primary).
> Recommendation: A — internal pain is real, but external regressions are the highest-cost failures.
> **Selected: A**

**Q3: What operational capability must exist before we flip to v1-only in prod?**
- A) **Option A (Recommended):** A documented runbook + metrics/alerts that make regressions obvious and actionable.
- B) Option B: Just a manual checklist in docs.
- C) Option C: Only automated tests (no ops changes).
> Recommendation: A — flipping runtime behavior without a runbook/alerts turns detection into guesswork.
> **Selected: A**

**Q4: Who has authority to approve “deletion of legacy code” after gates pass?**
- A) **Option A (Recommended):** Tech lead / repo owner sign-off (explicit checkpoint).
- B) Option B: Any engineer who sees green dashboards.
- C) Option C: CI alone (merge if tests pass).
> Recommendation: A — deletion is irreversible within the deprecation window; require explicit accountability.
> **Selected: A**

**Q5: How do we treat “tenants/calls” ownership during retirement?**
- A) **Option A (Recommended):** Platform owns global behavior; call owners only consulted if a specific call regresses.
- B) Option B: Each call owner must opt-in/out explicitly.
- C) Option C: Ignore call differences entirely.
> Recommendation: A — keeps the program operationally tractable while retaining an escalation path.
> **Selected: A**
