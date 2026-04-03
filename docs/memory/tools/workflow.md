<!-- docs/memory/tools/workflow.md -->
# Agent Workflow

- **Chat hygiene:** If a new chat is warranted (context bloat, WF/branch switch, runner needs clean session), explicitly say so to the user and provide a copy-paste prompt. Workflow rules do not strictly require starting a new chat for every phase, but it is highly recommended (especially moving from Phase 0 to Phase 1) to manage context limits.

- **Skills check:** Before starting a new category of work, check for an existing skill in `~/.agents/skills` (or ask the user to run `ls ~/.agents/skills`) and follow the most relevant `SKILL.md`. This is an always-on habit.

- **Interactive brainstorms:** When a user requests an interactive brainstorm, run it interactively (e.g., asking 5 questions at a time if requested) rather than silently synthesizing answers.

- **Heredoc loop prevention:** Avoid using `cat <<EOF` (heredoc) in terminal commands for large file writes; prefer filesystem tools or `replace_file_content` to prevent looping and token burn. If the system overrides your response repeatedly, stop the loop and ask the user for clarification.

- **2026-03-01 — WF task review rigor:** In adversarial Phase 2 reviews, require one deterministic WF-focused pytest selector contract (e.g., `wf0043_contract_<surface>_<case_id>`) and align every task-level verification command to it to avoid ambiguous `-k` filters.

- **2026-03-01 — Branch cleanup hygiene:** After PR merge/branch deletion, always run `git fetch --prune origin` locally to remove stale remote-tracking refs before reporting branch cleanup status.

- **2026-03-02 — Unified Phase 1 runner status cadence:** For `phase-1-or-2-run-planning`, Phase 1 should update `docs/index.md` to `Phase 1` after Part A and `Phase 1 (Ready)` only after Part C marks PRD `Ready for Tasks`; keeps runner traceability and avoids premature readiness signaling.

- **2026-03-02 — Unified Phase 2 runner handoff discipline:** For `phase-1-or-2-run-planning`, commit Task v0.1 after Part A before Part B review, then mark `docs/index.md` as `Phase 2 (Ready)` only after Part C sets task artifact to `Ready for Implementation`.

- **2026-03-04 — WF-0048 Phase 2 scope lock:** Keep tasks constrained to `ActivatedCallConfigSnapshotV1` boundary + deterministic contract-failure semantics + deterministic contract tests; avoid adding broader pipeline/UI refactors in task plans.

- **2026-03-04 — Phase 2 PRD scope FR coverage:** If PRD includes explicit scope-guard requirements (for example `FR11`, `FR12`), include a dedicated atomic scope-guard task with deterministic verification selectors before marking `Ready for Implementation`.

- **2026-03-04 — Adversarial Task Review delta pattern:** Treat broad verification filters (for example `-k wfXXXX_contract_`) as non-blocking precision gaps; tighten to task-specific deterministic selectors in Part C before final readiness handoff.

- **2026-03-04 — Contract gate namespace drift:** After adding a new WF contract namespace (e.g., `wf0050_contract_`), update `.github/workflows/ci.yml` contract-gate selectors immediately; otherwise CI can stay green while new boundary hardening loses explicit merge-time enforcement.

- **2026-03-04 — Brainstorm/Q&A metadata sync:** When Phase 0.1 substantially expands brainstorm sections, bump the paired Q&A artifact version/status in lockstep before/with Phase 0.3 to preserve traceability consistency.

- **2026-03-04 — Governance gate event scope:** Evidence-coupling governance checks (WF-0053) should run on `pull_request` events, not post-merge `push` events on `main`; push-only runs can deadlock main with missing PR artifact bundles.

- **2026-03-05 — Phase 0.0 artifact fanout vs 3-file limit:** `phase-0-0-start-workflow` requires 5 artifact files plus `docs/index.md` row (6+ file changes). If repo guidance says “3-file limit”, treat workflow runner instructions as SSOT for Phase 0 initiation; otherwise Phase 0 cannot be executed as specified.

- **2026-03-05 — Stale `.git/index.lock` during Phase 0.0:** If `git commit` fails with an `index.lock` error, first confirm no real git process is active, check whether `.git/index.lock` still exists (it may auto-clear), then retry the commit; avoid pushing the WF branch before the baseline artifacts are actually committed.

- **2026-03-05 — Pre-commit whitespace auto-fix retry:** If commit fails on `trailing-whitespace` and hook auto-edits files, immediately re-stage and re-run commit; this is expected and not a logical content conflict.

- **2026-03-05 — WF artifact status semantics drift:** Completed WFs can retain stale task headers (e.g., `Ready for Implementation`) while index/walkthrough show done; add deterministic alignment selectors for task/walkthrough/index to prevent silent historical drift.

- **2026-03-05 — WF selector CI wiring:** For WF-scoped governance tests, run a full namespace selector in CI (e.g., `-k "wf0054_ci_policy_"`) instead of a single tracer so newly added deterministic cases are automatically enforced.

- **2026-03-05 — Branch protection API can be plan-gated:** On private repos without GitHub Pro/Team, `gh api .../branches/main/protection` and `.../rulesets` return HTTP 403 (“Upgrade to GitHub Pro or make this repository public”); WF enforcing branch protection must include a plan/permissions preflight and a fallback read/verify path.

- **2026-03-05 — WF-0055 Phase 2 dependency hygiene:** Keep verify-only CI wiring task dependent on verify readiness (Task 5) and not on apply/rollback tasks; this preserves MVP sequencing and avoids unnecessary coupling in Ready-for-Implementation plans.

- **2026-03-05 — Phase 2 command-surface completeness:** If PRD requires controlled commands (verify/apply/rollback), ensure at least one task explicitly wires each command entrypoint (e.g., CLI `apply`) with verification; otherwise plans can be “Ready” but non-executable.

- **2026-03-05 — Adversarial Part B precision check:** Treat task text/verification mismatches (for example task claims covering rollback while verification only asserts verify/apply) as a revise-before-ready issue; tighten scope language and FR mapping in Part C.

- **2026-03-06 — CI script CWD coupling:** Repo-root scripts invoked from backend job (`working-directory: backend`) can fail when using relative repo paths; resolve `REPO_ROOT` from script location and build absolute target paths. Why: prevents false CI failures from directory-dependent behavior.

- **2026-03-06 — Canonical adversarial review utility:** Use `docs/workflow/util-adversarial-diff-audit.md` as the single Part B adversarial review contract; phase/lifecycle runners should delegate to it rather than duplicating review checklists. Why: prevents instruction drift and keeps audit quality consistent.

- **2026-03-06 — Fail-closed adversarial gates:** Phase/sub-phase/lifecycle review gates should default to `main...HEAD` and stop progression unless audit output includes all required sections and the six mandatory focus areas. Why: removes ambiguous “partial review” passes.

- **2026-03-06 — Parent vs sub-phase routing discipline:** Parent runners should not duplicate Part B execution details when sub-phase files already enforce them; keep parent files as routers and sub-phases as operational contracts. Why: avoids contradictory instructions and double-execution drift.

- **2026-03-06 — Avoid persona prompts in gates:** For Part B review rigor, encode behavior contracts (adversarial, fail-closed, invariants-first) in `util-adversarial-diff-audit.md` instead of role labels like “obedient agent” or title-based personas. Why: reduces style drift and keeps quality criteria explicit.

- **2026-03-06 — Phase 3 continuation-first contract:** Keep Phase 2 `task` as the only planning/commit unit, but treat `Session boundary after` and other task-level boundary hints as advisory continuation-risk signals, not automatic stops. Why: users may prefer uninterrupted Phase 3 runs as long as reasoning quality remains stable.

- **2026-03-06 — Context-risk stop handoff:** If reasoning quality is at risk from context load or context drift, warn explicitly in chat, say whether downstream runner parts are blocked, identify the next unfinished task, and print a copy-pasteable resume prompt. Why: Phase 3 now auto-stops only for context-risk, so the handoff must stay explicit.

- **2026-03-06 — WF-0059 proof-closure planning split:** If a PRD requires both deterministic parity/scope-guard tests and a concrete walkthrough evidence artifact, keep them as separate late Phase 2 tasks. Why: avoids coupling documentation capture to regression proof and keeps review findings non-ambiguous.

- **2026-03-06 — Historical WF branch reconciliation:** When a later merged WF changes the contract of an older unmerged WF branch, merge `main` first, keep the newer contract as baseline, and re-base the older WF tests/artifacts before deciding rerun scope. Why: avoids re-implementing stale assumptions on top of obsolete branch state.

- **2026-03-06 — Parking lot promotion drift:** `docs/parking_lot.md` (P0/P1/P2 + WF initiative log) can drift from `docs/index.md`. When promoting an item, update both the priority table and the WF initiative log so “pick” references stay real.

- **2026-03-08 — Phase 2 fail-closed realism check:** Do not leave a task artifact at `Ready for Implementation` when the PRD or audit gate requires explicit pass/fail evidence that has not yet been captured, and validate every named file seam against the live repo before finalizing the task plan. Why: nonexistent paths or omitted live seams (`draftStore`, `renderModel`) create false readiness and hidden coupling.

- **2026-03-08 — Phase 2 cross-call proof lock:** When a PRD locks a representative-call matrix, carry that exact call set into every parity, idempotency, and gate acceptance criterion plus verification step, and require persistence-side-effect assertions on success paths. Why: otherwise Phase 3 can pass narrow single-call or status-only proofs while claiming cross-call semantic closure.

- **2026-03-08 — Commit cadence preference:** User preference is to commit after each completed change request by default (unless explicitly asked not to). Why: prevents uncommitted drift and missed saves between turns.

- **2026-03-08 — Phase 2 task-proof hygiene:** Split tracer bullets when BFF and page seams would force more than 3 files in one task, require deterministic `wfXXXX_<surface>_<case>` selectors instead of fuzzy `-k`/`-t` filters, and anchor scope-guard verification to an explicit baseline SHA rather than `HEAD~1`. Why: keeps Phase 3 proof atomic and resilient to multi-commit execution.

- **2026-03-08 — Evaluation-WF fail-closed planning:** If the PRD requires `coverage_gap` or `insufficient_evidence` recording, Phase 2 tasks must persist those states in artifacts instead of using them as stop-only conditions; also do not invent impossible inputs like “mixed baseline” unless the planned artifact shape can express them. Why: stop-only handling drops required evidence and creates false readiness.

- **2026-03-08 — Tracer-bullet proof realism:** A tracer-bullet task cannot claim raw-output persistence if its verification uses `--dry-run`; require one real persisted-output assertion on the named seam before downstream evidence-capture tasks depend on it. Why: dry-run checks parse/validation only and do not prove the execution seam.

- **2026-03-09 — Phase 2 remediation seam proof:** When a PRD names primary suspected seams and conditional downstream seams, Task 1 must prove the narrowest primary seam first and fail closed before planning service/API reroutes or ordering work. Why: otherwise the task plan bakes in hidden coupling and scope drift before repo evidence justifies it.

- **2026-03-10 — Protected-row parity sequencing:** If a Phase 2 task plan adds protected `/app` or `/api/bff/*` negative scenarios after happy-path auth tasks, add explicit later parity tasks or a final protected-row parity sweep plus closure validator checks. Why: otherwise FR8/FR12 can fail only at closure even though the plan looked implementation-ready.

- **2026-03-11 — Brainstorm hardening closure contract:** During Phase 0 Part C hardening, ensure brainstorm revisions include both a fail-closed verification evidence matrix (default `fail` until executed) and a changelog entry when version is bumped. Why: this prevents premature proceed claims and keeps artifact version history compliant with workflow rules.

- **2026-03-11 — Phase 2 fail-closed proof must be executable, not grep-only:** If a task plan claims fail-closed manifest or closure gates, require at least one deterministic regression/test selector for the gate and replayable row-level evidence refs in the matrix; `rg`/`git diff` alone is not enough. Why: otherwise the artifact looks strict while still allowing false-positive readiness.

- **2026-03-12 — Phase 3 closeout status alignment:** Before any ship recommendation, ensure the task artifact, walkthrough, index row, and parking-lot WF initiative log all reflect the same post-implementation state for the active WF. Why: executable proof can be correct while closure still remains non-auditable if status surfaces lag behind reality.

- **2026-03-13 — Review-and-harden artifact detection:** On a WF branch with fresh Phase 0 scaffold files (`prd/task/walkthrough` at `v0.0` / `Not started`), treat the brainstorm marked `Draft Complete` as the latest completed artifact for Part B/C review. Why: auditing placeholder artifacts instead of the finalized brainstorm creates false gate selection and misses the real handoff surface.
- **2026-03-13 — Phase 2 RED/GREEN proof split:** If a task plan requires a TDD RED before implementation and a GREEN after implementation, keep the same contract traceable but separate the initial failing-evidence capture from the final passing proof in the matrix and acceptance criteria. Why: mixing both states into one row or one assertion makes the task look ready while the evidence contract is still non-executable.
- **2026-03-13 — Phase 1 fail-closed carry-through:** If a brainstorm requires explicit proceed-gate prose, audit-ledger closure, and scope-gate proof for a narrow rollout, the PRD must retain all three explicitly instead of only copying the verification matrix. Why: otherwise readiness can drift into implicit approval while non-targeted scope expansion remains unproved.
- **2026-03-14 — Phase 2 closure-gate evidence carrier:** If a task plan requires final pass/fail rows, baseline scope proof, or an audit-disposition ledger before ship, name the walkthrough (or another concrete artifact) as the required evidence surface in the task itself. Why: a `none` file list leaves Phase 3 unable to record closure evidence without inventing process.
- **2026-03-14 — Phase 2 frontend proof selectors:** When a task references frontend test files that already contain unrelated WF coverage, verification steps must use exact `-t` selectors for the new WF cases instead of whole-file runs. Why: whole-file passes are not replayable row-level evidence for fail-closed matrices.
- **2026-03-14 — Phase 2 cross-surface gate/trace split:** If a cohort gate or support-trace slice would require both backend and BFF code plus both test suites, split it into sequential backend/BFF tasks and add a stop-if against accidental public-contract widening. Why: otherwise the plan violates the `<=3`-file atomic-task rule and hides trace-contract drift.
- **2026-03-14 — Commit message hook prefixes:** Repo `check-commit-msg` enforces prefixes. Use `WF-XXXX: ...` for WF work, otherwise use `fix: ...` or `chore: ...`; avoid unprefixed “Docs:” style subjects.
- **2026-03-14 — `gh pr merge` flag + local update:** Some `gh` versions do not support `--yes`. `gh pr merge <N> --merge --delete-branch` can succeed non-interactively and may also fast-forward the local base branch to the just-merged `origin/main`.
- **2026-03-14 — Phase 2 fail-closed matrix + telemetry carry-through:** If a PRD includes telemetry requirements or ship-gate proof semantics, Phase 2 tasks must keep those as explicit task slices/rows, and verification-matrix `Result` cells must default to `fail` or `skipped` with rationale rather than placeholders like `required`. Why: otherwise ready-for-implementation artifacts can drop approved scope and overstate closure readiness.
