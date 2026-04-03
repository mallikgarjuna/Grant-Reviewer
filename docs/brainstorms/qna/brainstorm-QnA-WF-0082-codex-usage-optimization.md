<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0082-codex-usage-optimization.md -->
# WF-0082 — Codex Usage Optimization

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-04-03

## Preflight / Intake

Source: user request on 2026-04-03

- User asked to revise and optimize how Codex is used in this project.
- User explicitly requested critical judgment on what to keep versus revise, compact, or delete.
- User asked for concrete understanding of how much context is being loaded per prompt and per chat window.

## Repo Reality Snapshot Notes

- `AGENTS.md` is compact and high-signal overall.
- `docs/index.md` is the largest likely default-load surface.
- Large memory leaf files appear to have accumulated many dated policy notes that may be better treated as reference history than likely first-load context.
- Initial context estimate produced in chat: about 8.8k repo-local tokens for `AGENTS.md` + `docs/index.md` + `docs/memory/index.md`, rising toward ~17k if large memory leaves are also loaded.

## Section 1 — Problem Statement / Success Boundary

**Q1: What is the main success criterion for this WF?**
- A) Reduce default context load while preserving current workflow rigor.
- B) Simplify the workflow system overall, even if some rigor is lost.
- C) Improve visibility and measurement only; make little or no process change.
> Recommendation: A — it targets the biggest likely pain without throwing away workflow discipline that the repo intentionally built up. B is too destructive for a first pass, and C is too observational to solve the operational problem.
> **Selected: A**

**Q2: What should count as the primary measurement standard?**
- A) Practical estimate of likely repo-local context loaded in normal Codex sessions.
- B) Exact tokenizer-based counts for all important prompt paths.
- C) File-count and line-count only.
> Recommendation: A — it is decision-useful and cheap enough to repeat. B is attractive but too expensive for the first optimization loop, and C is too weak to support meaningful keep/revise/delete decisions.
> **Selected: A**

**Q3: Which surface should we treat as the first likely cleanup target?**
- A) `docs/index.md`
- B) `AGENTS.md`
- C) `docs/memory/*`
> Recommendation: A — it is the highest-cost likely default surface and gives the best chance of large wins with limited risk. B is already relatively compact, and C matters too, but is more useful after the dashboard/entrypoint policy is clarified.
> **Selected: A**

**Q4: How aggressive should we be about archiving historical workflow material?**
- A) Aggressive: move historical registries out of default entrypoints now.
- B) Moderate: keep history, but route to compact active dashboards first.
- C) Minimal: mostly keep structure, just trim wording.
> Recommendation: B — it preserves traceability while still addressing context bloat. A may overshoot before we confirm lookup needs, and C is likely too weak to materially change day-to-day load.
> **Selected: B**

**Q5: What output do you want this WF to optimize for most?**
- A) Better day-to-day Codex performance in this repo.
- B) Cleaner process documentation for humans.
- C) A reusable pattern for other repos.
> Recommendation: A — it matches the actual pain and gives us a clear decision criterion when tradeoffs appear. B is secondary, and C should remain a later byproduct rather than a current scope driver.
> **Selected: A**

## Section 2+ — Recommended Defaults Approved by User

User instruction: "and go with your recommendations for the rest of the Phase 0"

**Q1: What level of proof should be enough before we change a doc or instruction surface?**
- A) A strong practical case from repo inspection and estimated context load.
- B) Exact before/after token proof for every changed surface.
- C) Mostly intuition and qualitative judgment.
> Recommendation: A — it is strong enough to prevent arbitrary churn while staying cheap enough for iterative cleanup. B would slow the WF without proportional value, and C is too weak for a keep/revise/delete pass.
> **Selected: A**

**Q2: How should we treat rules that are valuable but rarely needed?**
- A) Keep them, but move them behind narrow triggers or reference docs.
- B) Keep them in default entrypoints just in case.
- C) Delete most of them unless used weekly.
> Recommendation: A — it preserves safety while reducing default context tax. B keeps the current bloat pattern, and C risks losing valuable safeguards.
> **Selected: A**

**Q3: What should happen if a history-heavy file is useful for humans but bad as default agent context?**
- A) Split it into a compact active summary plus archive/reference file.
- B) Leave it as-is and rely on agent discretion.
- C) Delete most of the historical material.
> Recommendation: A — it aligns with the moderate archive posture and preserves traceability. B likely preserves the current problem, and C is unnecessarily destructive.
> **Selected: A**

**Q4: How should we define "default context" for this WF?**
- A) Files the repo explicitly encourages opening early or for most tasks.
- B) Any file that exists in `docs/`.
- C) Only files manually opened in the current chat.
> Recommendation: A — it gives us an actionable and repo-specific definition tied to actual guidance. B is too broad, and C is too narrow to improve repo policy.
> **Selected: A**

**Q5: What should be considered a failed outcome for this WF?**
- A) We shrink docs, but make the workflow less safe or less traceable.
- B) We keep rigor, but only achieve small context savings.
- C) We mainly produce analysis without changing the repo.
> Recommendation: A — it defines the primary guardrail against over-optimization. B may still be acceptable if the change is low-risk and measurable, while C is weak but recoverable if the analysis materially guides the next step.
> **Selected: A**

## Changelog

- v0.1 (2026-04-03): Recorded initial user intake and read-only repo snapshot notes before the first interactive brainstorm batch.
- v0.2 (2026-04-03): Recorded Section 1 success-boundary decisions covering success criteria, measurement posture, first cleanup target, archive posture, and primary optimization target.
- v0.3 (2026-04-03): Recorded the user-approved recommended defaults for the rest of Phase 0, covering proof standard, treatment of rare rules, split strategy for history-heavy files, default-context definition, and failure condition.
