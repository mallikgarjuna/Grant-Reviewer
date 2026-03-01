# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: brainstorm-qna
Version: v0.3
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

---

## Section 4 — Rough Idea Exploration (2026-03-01)

**Brainstorming Q&A:**

**Q1: What is the simplest “v1-only” enforcement mechanism we should target?**
- A) **Option A (Recommended):** Make `/api/structured-review` always route to `pipeline_v1` (while legacy code still exists temporarily for rollback-by-revert only).
- B) Option B: Keep conditional routing but expand allowlist until it’s effectively “all calls”.
- C) Option C: Add a new “retirement mode” flag that forces v1-only (extra config surface).
> Recommendation: A — lowest config surface area long-term; B preserves hidden complexity; C adds a new toggle that can drift or be mis-set.
> **Selected: A**

**Q2: What is the preferred retirement sequence?**
- A) **Option A (Recommended):** Evidence first (replay/health) -> v1-only switch -> observation window -> delete legacy.
- B) Option B: Switch first -> observe -> if green, do evidence retroactively -> delete.
- C) Option C: Delete first in staging -> then switch in prod.
> Recommendation: A — prevents “we switched without knowing what good looks like” and preserves rollback options.
> **Selected: A**

**Q3: Where do we want the “readiness checklist” to live as SSOT?**
- A) **Option A (Recommended):** In the WF-0040 walkthrough artifact (runbook-like, phase-gated, linkable).
- B) Option B: In `backend/README.md` only.
- C) Option C: In the task file only.
> Recommendation: A — walkthrough is the natural place for operational gates and evidence references; README/tasks can link to it.
> **Selected: A**

**Q4: How do we want to treat environments?**
- A) **Option A (Recommended):** Stage gates: dev/staging first, then prod; prod requires explicit approval checkpoint.
- B) Option B: Only staging matters; prod follows automatically.
- C) Option C: Treat staging+prod identically (same day).
> Recommendation: A — matches a controlled deprecation program; B/C compress risk into prod.
> **Selected: A**

**Q5: What is our stance on “no behavior change first”?**
- A) **Option A (Recommended):** First change is add/strengthen tests + evidence scripts/runbook references; routing behavior changes only after gates exist.
- B) Option B: Routing change first (faster), then backfill tests.
- C) Option C: No tests needed if dashboards are green.
> Recommendation: A — ensures we can detect regressions before they happen in prod.
> **Selected: A**

---

## Section 5 — Constraints (2026-03-01)

**Brainstorming Q&A:**

**Q1: What is the most important contract invariant during retirement?**
- A) **Option A (Recommended):** Public API request/response schemas + error semantics remain stable.
- B) Option B: Telemetry shape must remain stable.
- C) Option C: Internal call YAML schema must remain stable even if API shifts.
> Recommendation: A — client-facing contracts are the highest-risk; telemetry and YAML are still important but secondary.
> **Selected: A**

**Q2: How strict is the idempotency requirement?**
- A) **Option A (Recommended):** Preserve idempotency semantics exactly, including digest mismatch and expectation resolution failure behavior.
- B) Option B: Idempotency can change if outputs improve.
- C) Option C: Idempotency is not relevant for structured reviews.
> Recommendation: A — idempotency regressions can create duplicate/incorrect persisted results and break client assumptions.
> **Selected: A**

**Q3: How do we treat call YAML ingestion/canonicalization during retirement?**
- A) **Option A (Recommended):** No changes to ingestion contracts; retirement work must be compatible with existing call YAML behaviors.
- B) Option B: Permit small call YAML schema changes if tests pass.
- C) Option C: Ignore call YAML; structured review is independent.
> Recommendation: A — avoids coupling retirement to ingestion migration scope.
> **Selected: A**

**Q4: What rollback posture do we require?**
- A) **Option A (Recommended):** While legacy code exists, rollback is operational and explicit; after deletion, rollback is revert-deploy (not “switch engines”).
- B) Option B: Keep a permanent runtime engine switch for rollback.
- C) Option C: No rollback required if staging is green.
> Recommendation: A — aligns with the end-state goal and keeps rollback honest.
> **Selected: A**

**Q5: What is the time constraint and how should it influence scope?**
- A) **Option A (Recommended):** Optimize for safety gates/observability; do not accelerate deletion at the cost of unclear rollback/evidence.
- B) Option B: Optimize for speed; delete legacy ASAP.
- C) Option C: No time constraints; we can take months.
> Recommendation: A — balances momentum with risk control.
> **Selected: A**

---

## Section 6 — Risks / Unknowns (2026-03-01)

**Brainstorming Q&A:**

**Q1: What is the highest-risk regression class during retirement?**
- A) **Option A (Recommended):** Edge-case contract and error semantics regressions (timeouts, validation order, contract error codes/fields).
- B) Option B: Latency regressions only.
- C) Option C: Minor text/content differences only.
> Recommendation: A — contract drift can silently break clients and workflows; latency is important but more detectable.
> **Selected: A**

**Q2: What do we treat as a blocker to flipping prod routing to v1-only?**
- A) **Option A (Recommended):** Missing/insufficient observability (can’t detect regressions quickly) is a blocker.
- B) Option B: Only failing tests are blockers.
- C) Option C: Nothing is a blocker if staging is green.
> Recommendation: A — without observability, you can’t manage the risk window in prod.
> **Selected: A**

**Q3: How do we handle the “legacy” naming collision risk in call-config/UI mode?**
- A) **Option A (Recommended):** Document it; keep scope to engine-execution retirement; do not rename unless it blocks the work.
- B) Option B: Rename everything now.
- C) Option C: Ignore it.
> Recommendation: A — keeps scope bounded while preventing confusion.
> **Selected: A**

**Q4: What is the failure mode we most want to prevent?**
- A) **Option A (Recommended):** Premature legacy code deletion that removes rollback options before evidence gates pass.
- B) Option B: Minor docs drift.
- C) Option C: Slightly slower runtime.
> Recommendation: A — this is the irreversible mistake; others are recoverable.
> **Selected: A**

**Q5: What is the biggest unknown that must be made explicit in Phase 1 planning?**
- A) **Option A (Recommended):** Exact observation window definitions/thresholds + rollback source-of-truth config and runbook steps.
- B) Option B: Which team owns the work.
- C) Option C: Whether to do any tests.
> Recommendation: A — those are the practical gates needed for safe execution.
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
