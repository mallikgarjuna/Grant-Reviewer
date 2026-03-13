<!-- docs/memory/domain/project_docs.md -->
# Project Documentation

- **Traceability in outputs**: Workflow runner completion summaries must always include explicit provenance: which files were considered/edited and which skills/instructions were used.

- **Traceability in commits**: Every WF commit message must include both the WF ID and the relevant slug so history is self-describing (e.g., `WF-0012: alembic-migration-baseline - <change>`). (Do not rewrite history; enforce going forward).

- **Push Docs Rule**: Always update `docs/` with all relevant branch work (status/index, decisions, Q&A, prompt history, workflow artifacts) *before* pushing a branch to remote. After every successful push, explicitly confirm that docs/WF artifacts were updated (or state that none were required).

- **WF Boundary Hygiene**: Use a separate branch from `main` (e.g. `task/8.1-lint-baseline-cleanup`) to keep WF phase boundaries clean.

- **Next Actions Formatting**: Before Phase 4 completion, provide end-to-end runner options (e.g. `phase-1-run-spec`). After Phase 4 completion, replace that section with "Next 2 WF ideas/features" from the parking lot.

- **Commit Granularity**: Commits must happen per runner part (Part A output, Part C revision, and Part B only if it has edits) and per phase gate. During Phase 3/4 execution, commit after *each* completed subtask with a short message including the subtask ID.

- **Ignore files rule**: Before any commit, check `.gitignore` behavior via `git status --ignored --short` and prefer narrow unignore rules (`!pattern`) over force-adding files.

- **2026-03-01**: All new code phrases and agent chat triggers must be added to `docs/reference/code_phrases.md` (the SSOT), not directly to `AGENTS.md`. `AGENTS.md` should remain as tiny as possible.

- **2026-03-02**: WF interactive Q&A decisions must be written into `docs/brainstorms/qna/brainstorm-QnA-WF-XXXX-<slug>.md`; the main brainstorm remains the SSOT for contracts/decisions and must link to the Q&A section(s) used.

- **2026-03-06**: Docs sanitization should roll out in phases: first enforce tool/model neutrality on SSOT + a small set of sanitized workflow files, then expand guard coverage only after targeted file cleanup. Why: avoids CI churn from legacy wording while tightening policy incrementally.

- **2026-03-06**: Sanitization guard now covers workflow phase docs 0.x/1.x/2.x used for planning (`phase-0-0`..`phase-2-3`). Keep expansion to remaining workflow docs as dedicated small batches. Why: preserves 3-file discipline and keeps CI transitions low-risk.

- **2026-03-06**: Sanitization guard now enforces all `docs/workflow/*.md` plus `AGENTS.md`; workflow docs are clean of tool/model names. Why: full-folder enforcement prevents regressions while keeping adapters/history as the only place tool names appear.

- **2026-03-06**: New traceability rule: every file should encode its project-relative path at top (comment/docstring/header) so copied sources preserve provenance in external chat tools.

- **2026-03-06**: Commit-msg hook must allow non-WF maintenance commits using `fix: <short title>` or `chore: <short title>` because workflow docs already permit `fix/<slug>` and `chore/<slug>` branches. Why: forcing WF-prefixed commits on maintenance branches creates false traceability.

- **2026-03-06**: Review-detail API contract tasks must include the HTTP response assembly seam (currently `backend/main.py`) in allowed file boundaries when response fields change. Why: repository/schema changes alone cannot expose new review-detail fields.

- **2026-03-06**: Reusable post-phase "stress test and fix" chat prompt now lives at `docs/workflow/review-and-harden-prompt.md`. Use it with a single artifact path instead of rewriting phase-specific review/revise prompts each time.

- **2026-03-07**: Version-label policy: keep `vN` only for stable contracts/schemas (for example `Call Definition V2`, `DiagnosticFinding v1`, `Observation v1`, `ReviewRequest v1`). For historical implementation eras with no active `v2`, prefer `legacy`/`current` wording over `pipeline v1`. Why: reduces fake optionality and planning confusion.

- **2026-03-07**: Naming boundary policy: do not mix WF IDs, roadmap/phase numbers (`5.0`, `8.0A`), and contract/schema versions (`v1`, `V2`) in the same label or shorthand. Why: they answer different questions: history, delivery slice, and compatibility boundary.

- **2026-03-08**: Product mission statement SSOT lives in `docs/mission.md`. Preserve this wording as the default anchor for landing-page copy, internal docs, and product-positioning decisions unless a deliberate mission update is made.

- **2026-03-08**: `docs/mission.md` now distinguishes `Mission`, `Vision`, `MVP Goal`, `Product Goals`, and `MVP Success Criteria`; do not introduce a separate "MVP mission statement". Why: phase-specific intent should live under goals/success criteria while the mission remains stable.

- **2026-03-08**: Canonical code phrase for `docs/mission.md` drift review is `mission check`; it should classify requested changes as mission-level, goals-level, or no change, and prefer minimal edits. Why: avoids prompt drift and inconsistent trigger naming.

- **2026-03-08**: Parking-lot hygiene rule: when a WF or maintenance item lands, remove or rewrite any backlog row that still describes that solved work, and merge symptom-only duplicates into one live item. Why: stale backlog rows cause fake future planning and hide the real remaining bottlenecks.

- **2026-03-08**: WF initiative-log backlog refs are provenance snapshots only; label them as historical at promotion time rather than implying they still map to the current numbered backlog. Why: parking-lot renumbering is expected, so unlabeled refs create false traceability.

- **2026-03-08**: Docs-only planning PRDs must distinguish live correction targets from workflow bookkeeping surfaces (for example `docs/index.md`) and require per-target pass/fail evidence before any proceed recommendation. Why: otherwise Phase 2 can widen scope by accident or claim closure from generic doc-scan language.

- **2026-03-08**: Docs-only task verification must anchor changed-file proof to an explicit implementation baseline SHA or commit range, not raw `git diff` worktree state. Why: prior-phase branch diffs and per-task commits make worktree-only evidence nondeterministic for closure.

- **2026-03-08**: When a WF is closed and marked `Done` in `docs/index.md`, any standard WF artifacts still living outside `docs/*/completed/` should be archived and all registry/cross-doc links updated in the same closure pass. Why: partial closure leaves the dashboard and artifact paths out of sync and causes repeated cleanup churn.

- **2026-03-08**: Trust-surface planning inside the locked NWO/ERC/MSCA wedge should reuse the exact representative proof set `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`, and treat `source basis` as fail-closed official-call metadata only, not generic model provenance. Why: prevents Phase 1 drift from re-broadening scope or inventing unverifiable explainability claims.

- **2026-03-08**: Review-detail trust-surface planning must include both the backend response seam and `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` normalization seam, and must not assume live `supporting_context_node_logical_ids` coverage beyond explicit proof because the current repository path still resolves that list to empty. Why: schema-only planning overstates what the UI can actually render today.

- **2026-03-08**: If a WF brainstorm marks itself as the SSOT for scope/contracts, any PRD resolution of a deferred contract question must be promoted back into that brainstorm, and review-detail trust planning must keep `visible but not reviewed` separate from `no generated cards`. Why: otherwise Phase 1 can leave the SSOT stale and silently weaken boundary-honesty requirements.

- **2026-03-08**: Review-quality evaluation planning for the locked NWO/ERC/MSCA wedge must treat the primary proof object as the `snippet -> review output` pair, require a frozen evaluation baseline per batch (same commit + prompt/model config + reviewer instructions), and keep remediation in a separate follow-on WF. Why: trust-surface closure and polished demos can otherwise be mistaken for real usefulness proof.

- **2026-03-08**: Evaluation-loop planning must explicitly ban convenience sampling, require auditable per-snippet selection rationale, and block any proceed recommendation unless a named verification evidence bundle is present. Why: otherwise Phase 1 can cherry-pick easy examples and convert weak evidence into fake readiness.

- **2026-03-08**: If a Phase 1 PRD for an SSOT-marked brainstorm adds a new proceed threshold, severity scale, or provenance requirement, promote it into the brainstorm and `docs/logs/decisions.md` in the same revise pass. Why: leaving those only in the PRD creates hallucinated contract drift and false readiness for Tasks.

- **2026-03-09**: New composed code phrase `phase 3 closeout` is SSOT in `docs/reference/code_phrases.md`; execute its seven-step closure sequence in strict order and stop for explicit user approval before `ship it`. Why: reduces phase-end checklist drift and keeps shipping user-gated.

- **2026-03-09**: Remediation/closure PRDs that gate `ship`, `proceed`, or phase advance must require two explicit proofs: a baseline-SHA or commit-range-anchored scope proof and an audit-disposition ledger closing all blocking findings while closing or rejecting justified non-blocking findings with rationale. Why: replay-only evidence is not enough if diff provenance and review-findings closure stay implicit.

- **2026-03-09**: WF planning for ERC structured-review stage gating must treat existing `structured_payload.review_stage`/`submitted_leaf_ids` plus review-detail boundary fields as the first provenance seam to extend, and must explicitly audit stage-aware review-detail buckets because the current repo can still present Step 2-only ERC surfaces as merely `not reviewed` on a Step 1 review. Why: this is a hidden trust leak and a likely planning blind spot if runtime-only fixes dominate the discussion.

- **2026-03-10**: WF-0072 planning locks the representative end-to-end trust-proof set to `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`, and requires a one-row-per-proof-item verification matrix (call, scenario, surface, auth lane, side-effect assertion, result). Why: keeps launch-evidence claims bounded, traceable, and fail-closed.
- **2026-03-10**: Any trust-proof WF that gates `proceed` or `ship` must require each verification-matrix row to name the exact exercised entrypoint/boundary plus an `evidence_ref`, and must require baseline-SHA/commit-range scope proof plus an audit-disposition ledger before closure. Why: pass/fail rows without provenance let later phases overclaim launch evidence and hide unresolved findings.
- **2026-03-10**: Trust-proof planning must also require each `evidence_ref` to resolve to deterministic replay metadata (exact command or test ID, exact selector/assertion or manual checklist step, expected outcome). Why: attributable artifacts alone are not enough for rerunnable launch-proof claims.
- **2026-03-10**: For trust-proof WFs, do not let a happy-path task fall back to API-only evidence with only a “closure blocked later” note unless the task plan also includes an explicit follow-on task that closes the real user-path gap; protected-surface policy-blocking proof must pair user-surface blocking with backend zero-side-effect evidence, and missing-mandatory-input negatives should name one representative call plus one exact field/node. Why: otherwise Phase 2 can detect the trust gap but still leave Phase 3 with no honest path to closure.
- **2026-03-11**: For SSOT-marked brainstorms, Phase 1 PRDs must preserve any explicit `decision/memory guidance` MVP surface and any fail-closed verification matrix or audit-disposition gate as enforceable PRD requirements, not soften them into generic testing prose. Why: otherwise approved governance and closure contracts can disappear during PRD compression and reappear later as hallucinated scope.
- **2026-03-11**: If a Phase 2 task artifact is derived from a PRD that makes decision/memory guidance mandatory, Tasks must carry an explicit implementation slice for those durable governance surfaces and keep verification rows in explicit `pass`/`fail`/`skipped` form. Why: otherwise a task plan can look Ready while silently dropping mandatory governance work and fail-closed closure semantics.
- **2026-03-11**: WF-0074 planning/execution must preserve durable decision/memory guidance for subordinate-prompt fidelity, temporary compatibility posture, proof-call policy, and seam-boundary honesty. No proceed or ship recommendation is valid without explicit `pass`/`fail`/`skipped` evidence plus audit-disposition closure for every justified finding. Why: otherwise closure can overclaim canonical fidelity impact while dropping the governance and verification contract that makes the claim auditable.
- **2026-03-12**: When a brainstorm/PRD says docs/checklist/governance follow-ons are required only "if needed," Phase 2 tasks must keep those slices conditional and gate them on unresolved ambiguity after executable proof. Why: making them unconditional reopens prior-truth governance scope and creates fake mandatory work.
- **2026-03-12**: WF-0076 repo-reality anchor: subordinate-prompt fidelity is currently discarded at the live structured-review activation seam in `backend/app/services/structured_reviewer_service.py`, which emits `call_config_snapshot` with only `schema_version` plus `expectations`. Why: future runtime-consumption planning must start from this verified seam rather than reopening WF-0074/WF-0075 authoring or proof-call scope.
- **2026-03-12**: Runtime-consumption planning must anchor proof seams and verification rows to the active execution path actually exercised by the target runtime flow; parallel or legacy prompt-building surfaces are not valid default proof seams unless the active flow is proven to route through them. Why: otherwise planning can pass symbolic contract changes against inactive code paths and overclaim runtime effect.
- **2026-03-12**: For WF-0076-style runtime-consumption work, prefer evaluator-produced finding `reason` as the first proof artifact when the active path already delegates there, and treat observation-based proof skeptically if `extract_observations` depends on snapshot sections the activation seam does not populate. Why: this avoids widening scope around inactive proof surfaces and keeps MVP proofs tied to the smallest live seam.
- **2026-03-12**: Runtime-consumption PRDs that require canonical-source lookup, malformed-payload rejection, or negative live-path proof must carry each one as an explicit verification-matrix row, not only as functional requirements or test prose. Why: otherwise proceed gates can pass with positive-only evidence and leave fail-closed closure gaps.
- **2026-03-12**: WF-0076 contract hardening must treat subordinate prompt `id`/`prompt` as trimmed non-empty values and reject trim-colliding duplicate prompt IDs in request validation. Why: min-length-only validation allowed whitespace-only malformed payloads and duplicate-ID bypass via padding.
- **2026-03-13**: WF planning/docs must reuse the canonical funding-call `code` exactly (`ERC-2026-PoC` here) and must not swap in source-folder/programme naming like `ERC-PoC-2026`. Why: call-code drift in PRD/decision text can mis-scope tests, implementation guards, and audit claims even when the underlying repo truth is already correct.
- **2026-03-13**: If a Phase 1 PRD closes MVP as backend seam proof, do not describe additive fields/provenance as public/user-facing by default; require an explicit carry-through decision and a no-attempt proof for out-of-scope calls/cards. Why: otherwise PRDs hide API/UI scope drift and can appear "Ready" while still contradicting their own rollout boundary.
