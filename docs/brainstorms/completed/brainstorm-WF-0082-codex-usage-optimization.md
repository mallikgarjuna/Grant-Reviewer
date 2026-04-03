<!-- docs/brainstorms/completed/brainstorm-WF-0082-codex-usage-optimization.md -->
# WF-0082 — Codex Usage Optimization

Artifact: brainstorm
Version: v0.4
Status: Draft Complete
Last Updated: 2026-04-03

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0082-codex-usage-optimization.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts and decisions for this WF.
- The Q&A transcript is rationale only and must not become the only source of truth.
- The current user intent is to revise and optimize how Codex is used in this repo, with explicit scrutiny on what to keep, revise, compact, or delete, and with concrete visibility into context load per prompt and per chat.

---

## Repo Reality Snapshot (Read-Only)

- `AGENTS.md` is small and mostly healthy; its biggest high-cost rule is the broad trigger to use `docs/index.md` for any work request.
- `docs/index.md` is the dominant always-nearby context surface at about 31k characters, functioning more like a large registry dump than a lightweight dashboard.
- `docs/memory/index.md` is small, but several memory leaf files have grown into large policy logs that are plausible follow-on reads in workflow-heavy chats.
- Current estimated repo-local baseline for this initiative is roughly 8.8k tokens if `AGENTS.md`, `docs/index.md`, and `docs/memory/index.md` are loaded; this rises toward ~17k if large memory files are also pulled in.
- Historical workflow/task docs are large in aggregate, but the main risk is not total repo size; it is broad default entrypoints that encourage loading heavy files too early.

## 1. Problem Statement

The repo has accumulated a thoughtful but increasingly expensive Codex operating layer. The likely problem is not missing process, but too much default process/context for ordinary work.

Why it matters now:

- Context overhead reduces reasoning headroom before real code or docs work starts.
- Large default docs increase the chance that agents over-index on process history instead of the immediate task.
- The project now needs a sharper line between durable high-signal instructions and archival workflow history.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0082-codex-usage-optimization.md` (Preflight / Intake)

Contract Notes / Non-obvious constraints:

- This WF should optimize Codex usage for this repo specifically, not produce generic prompting advice.
- The first proof surface should include measurable context-load estimates, not only subjective “feels better” guidance.
- The priority is to reduce default context load while preserving current workflow rigor.
- `docs/index.md` is the first likely cleanup target, and historical workflow material should be compacted behind active dashboards rather than deleted outright.

## 2. Desired Outcome

After this WF:

- The repo should have a leaner default instruction surface for Codex.
- It should be clearer which docs are first-load, on-demand, or archival only.
- The project should have an explicit policy for context budgeting across AGENTS, dashboard, memory, and workflow docs.
- The user should be able to explain roughly how much repo-local context a normal Codex chat is likely to load.
- Success should be evaluated using practical likely-load estimates for normal Codex sessions, not exhaustive exact counts for every possible path.

Success threshold for MVP:

- Reduce the likely repo-local default-load surface materially, with the first target being `docs/index.md`.
- Keep or improve traceability, workflow safety, and researcher-facing terminology correctness.
- Leave behind a durable classification policy so future docs can be added without silently becoming default prompt payload.

## 3. Target User / Actor

Primary actor:

- The repo owner/operator using Codex repeatedly across planning, coding, and workflow-heavy sessions.

Current pain:

- It is hard to tell which instructions are genuinely helping versus silently consuming attention budget.
- Historical workflow rigor may be leaking into everyday chats as default context.

Secondary beneficiaries:

- Future agent sessions that need a clearer distinction between active instructions and archived historical reference.
- The repo owner when reasoning about when to start a fresh chat because of context bloat.

## 4. Rough Idea (Unstructured Thinking)

Working direction:

- Separate the system into three layers: tiny always-on instructions, small indexed on-demand docs, and archived history.
- Replace broad “read this for any work request” rules with narrow triggers tied to actual task types.
- Shrink dashboard-style files so they route to active work instead of embedding historical registries inline.
- Preserve traceability and workflow rigor, but move historical detail out of default entry paths.

Recommended design direction:

- `AGENTS.md`: keep tiny and high-signal; narrow broad triggers rather than adding new policy here.
- `docs/index.md`: convert from heavy registry dump to lightweight active dashboard with links to dedicated archive registries.
- `docs/memory/index.md`: keep as a small router.
- large memory leaves: keep valuable content, but distinguish active operating rules from historical/reference notes.

## 5. Constraints

- Preserve the repo's workflow system and traceability standards unless there is strong evidence a rule is net harmful.
- Avoid turning this into a broad product or architecture WF; scope should stay on Codex usage, instruction surfaces, and context hygiene.
- Keep changes auditable and small enough to validate with concrete before/after context estimates.
- Valuable but rarely needed rules should be retained behind narrow triggers or reference docs rather than kept in default entrypoints.
- History-heavy files that remain useful for humans should be split into compact active summaries plus archive/reference files where needed.
- Preserve researcher-facing terminology and existing provenance/traceability rules unless a later phase explicitly proves a change is necessary.

## 6. Risks / Unknowns

- Over-trimming could remove protections that are only needed occasionally but matter a lot when they do.
- Some “large” docs may not actually be loaded often in practice, so we need to separate theoretical from likely load paths.
- The right boundary between `AGENTS.md`, `docs/index.md`, and memory files is not yet locked.
- Context savings that come only from wording trims may look clean without materially changing likely-load behavior.
- A failed outcome would be shrinking docs while weakening workflow safety or traceability.

## Open Questions / Deferred

- Exact post-change target threshold for the default repo-local context estimate.
- Whether memory should use explicit `active` versus `archive` folders, or a lighter summary-plus-reference pattern.
- Whether any workflow guide should be elevated into the active dashboard, or remain purely on-demand.
- Phase 1 should decide the smallest acceptable verification standard for before/after context estimates.

## 7. MVP Definition

If we had to ship in 2-3 days, the smallest useful slice would:

- identify the highest-cost default context sources,
- classify current guidance into keep/revise/compact/delete,
- implement a minimal repo-doc cleanup that reduces default load without breaking workflow use,
- and document a simple context-budget policy for future additions.

MVP shape:

- start with `docs/index.md` as the first cleanup target,
- treat default context as files the repo explicitly encourages opening early or for most tasks,
- move rare but valuable rules behind narrow triggers or compact reference docs,
- and prefer active-summary plus archive splits over deletion for history-heavy surfaces.

MVP success evidence:

- a concrete before/after estimate for the likely repo-local default-load path,
- at least one high-cost default entrypoint materially reduced or rerouted,
- no loss of workflow traceability or safety semantics,
- and a documented operating rule that distinguishes always-on, on-demand, and archival instruction surfaces.

## 8. Explicit Non-Goals

- Rewriting the entire workflow system.
- Auditing every historical WF artifact in depth.
- Building a generalized Codex framework for other repos.
- Chasing exact token counts for every possible session path before making any improvements.
- Deleting historical material purely for neatness when a split/archive approach preserves more value.
- Quietly changing researcher-facing terminology, workflow provenance expectations, or safety rules without making that change explicit and justified.

## Section 1 Decisions

- Primary success criterion: reduce default context load while preserving current workflow rigor.
- Primary measurement standard: practical estimate of likely repo-local context loaded in normal Codex sessions.
- First cleanup target: `docs/index.md`.
- Archive posture: moderate; keep history, but route default use toward compact active dashboards first.
- Primary optimization target: better day-to-day Codex performance in this repo.

Contract Notes / Non-obvious constraints:

- We should prefer changes that improve everyday Codex operation before improving documentation aesthetics.
- Archive strategy should preserve traceability and lookup value, but historical registries should stop acting like default prompt payloads.

## Section 2-8 Decisions

- Proof standard before changing a surface: a strong practical case from repo inspection plus estimated likely-load impact.
- Rare but valuable rules: keep them, but move them behind narrow triggers or reference docs.
- Human-useful but agent-expensive files: split into compact active summaries plus archive/reference files.
- Default context for this WF: files the repo explicitly encourages opening early or for most tasks.
- Failed outcome definition: reducing docs while making the workflow less safe or less traceable.
- Recommended system shape: tiny always-on instructions, compact active dashboard/router files, and archive/reference history behind links.
- Sequencing rule: prefer entrypoint cleanup first (`docs/index.md`, broad `AGENTS.md` triggers), then deeper memory/archive splits only where the likely-load win remains strong.

Contract Notes / Non-obvious constraints:

- This WF should optimize likely agent behavior, not only document intent; changes that look tidy but do not change likely load paths are insufficient.
- Any compaction must preserve the ability to recover workflow history and rationale on demand.

## Initial Surface Inventory

- `AGENTS.md`: always-on repo instruction surface; should remain tiny.
- `docs/index.md`: active dashboard candidate, currently overloaded.
- `docs/memory/index.md`: routing index, likely should stay small.
- `docs/memory/domain/*.md` and `docs/memory/tools/*.md`: mixed active/reference memory surfaces; likely need classification.
- `docs/guides/*.md` and `docs/workflow/*.md`: on-demand procedural references, not default context except when explicitly triggered.

## Verification Guardrails

- Measure the likely repo-local default-load path before and after edits using the same estimation method.
- Verify that active workflow guidance still routes correctly after any dashboard or archive split.
- Verify that traceability/provenance rules and researcher-facing terminology are preserved unless intentionally changed.
- Prefer the smallest edits that materially change likely load behavior before broader documentation cleanup.

## Initial Step Breakdown

1. Lock the problem statement, success target, and measurement standard for this WF.
2. Define the instruction-surface inventory and classify each surface as always-on, on-demand, or archival.
3. Convert that policy into concrete repo changes with the smallest high-impact edits first.
4. Verify the revised context footprint and check for workflow/traceability regressions.
5. Capture the operating guidance so future additions do not re-bloat the default prompt surface.

## Changelog

- v0.1 (2026-04-03): Seeded the brainstorm from the user's request and a read-only repo snapshot, including initial scope, desired outcome, constraints, and a first-pass step breakdown.
- v0.2 (2026-04-03): Locked the initial Step 1 success direction, measurement posture, first cleanup target, archive posture, and optimization target from the first interactive Q&A batch.
- v0.3 (2026-04-03): Completed the remaining Phase 0.1 direction using approved recommended defaults, tightening success thresholds, default-context definition, archive posture, and MVP boundaries.
- v0.4 (2026-04-03): Applied Phase 0.2 tightening edits by adding explicit success evidence, preserving terminology/traceability boundaries, defining the initial surface inventory, and adding verification guardrails; marked brainstorm Draft Complete.
