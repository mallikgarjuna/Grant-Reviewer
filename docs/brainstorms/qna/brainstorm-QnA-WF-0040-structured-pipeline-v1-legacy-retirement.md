# WF-0040 — Structured Pipeline v1 Legacy Retirement

Artifact: brainstorm-qna
Version: v0.1
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
