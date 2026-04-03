<!-- docs/tasks/task-WF-0082-codex-usage-optimization.md -->
# WF-0082 — Codex Usage Optimization Tasks

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-04-03

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: baseline context estimate and surface inventory

Goal:
Produce the first concrete proof artifact for this WF by capturing the likely default-load baseline and a compact surface inventory for the in-scope instruction surfaces without changing behavior yet.
Slice: tracer-bullet
User Stories: US1, US2, US4
PRD Requirements: FR1, FR1A, FR2, FR8, FR10
Depends on: none
Enables: 2, 3, 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0082-codex-usage-optimization.md`
May touch files:
- `docs/tasks/task-WF-0082-codex-usage-optimization.md`
Out of scope: editing `AGENTS.md`, `docs/index.md`, memory leaf docs, or adding new routing policy
Stop if: the baseline estimate cannot be reproduced with one deterministic command/formula or the inventory cannot be expressed compactly in the walkthrough without inventing a new artifact type
Session boundary after: no
Acceptance Criteria:
- A baseline default-load estimate is recorded using one repeatable method and explicitly lists the included surfaces.
- A compact surface inventory is recorded for the in-scope surfaces with posture/action/rationale fields.
- The task file is updated only as needed to reflect task completion status during Phase 3; no repo behavior changes occur yet.
TDD Plan: N/A
Verification Steps:
- `python3 - <<'PY'\nfrom pathlib import Path\nfiles=['AGENTS.md','docs/index.md','docs/memory/index.md']\nfor f in files:\n    text=Path(f).read_text()\n    print(f'{f}\\tchars={len(text)}\\test_tokens~={round(len(text)/4)}')\nprint('combined_est_tokens', round(sum(len(Path(f).read_text()) for f in files)/4))\nPY`
- `rg -n "Baseline|Surface inventory|default-load" docs/walkthroughs/walkthrough-WF-0082-codex-usage-optimization.md`
Risks (if any): If the baseline artifact is vague or non-replayable, later tasks can look green while losing measurement comparability.

### [x] Task 2 — Convert `docs/index.md` into a compact active dashboard

Goal:
Reduce the highest-cost likely default entrypoint by turning `docs/index.md` into a lightweight active dashboard that routes to archive/history instead of embedding large historical registries inline.
Slice: entrypoint-dashboard
User Stories: US1, US2, US4
PRD Requirements: FR3, FR6, FR7, FR9, FR10
Depends on: 1
Enables: 4, 5
Parallelizable: no
Files to modify:
Must touch files:
- `docs/index.md`
- `docs/reference/workflow_archive_index.md`
May touch files:
- `docs/walkthroughs/walkthrough-WF-0082-codex-usage-optimization.md`
Out of scope: editing `AGENTS.md`, memory leaves, or performing broad cleanup/rewriting of archive content beyond what is needed to preserve routing and registry access
Stop if: preserving discoverability requires touching more than these files or the archive split would break existing registry links without a safe replacement path
Session boundary after: no
Acceptance Criteria:
- `docs/index.md` becomes materially smaller and functions as an active dashboard/router rather than a historical registry dump.
- Historical workflow/task registry content remains reachable through a linked archive/reference surface.
- Routing from the active dashboard to the archive surface is explicit and preserves traceability.
- The compact dashboard still exposes the active WF and the essential top-level routes needed to navigate current work.
TDD Plan: N/A
Verification Steps:
- `python3 - <<'PY'\nfrom pathlib import Path\nfor f in ['docs/index.md','docs/reference/workflow_archive_index.md']:\n    text=Path(f).read_text()\n    print(f'{f}\\tchars={len(text)}\\test_tokens~={round(len(text)/4)}')\nPY`
- `rg -n "workflow_archive_index|Active|Archive|WF-0082" docs/index.md docs/reference/workflow_archive_index.md`
- `rg -n "WF-0082|Mission|Parking lot|workflow_archive_index" docs/index.md`
Risks (if any): A bad split can hide history or create a lighter file that no longer routes users or agents to the necessary archive surfaces.

### [x] Task 3 — Narrow `AGENTS.md` default-entrypoint trigger

Goal:
Remove or narrow the broad `docs/index.md` trigger in `AGENTS.md` so the repo stops encouraging the heavy dashboard path for every work request.
Slice: agents-trigger
User Stories: US1, US2, US3
PRD Requirements: FR4, FR5, FR7, FR9
Depends on: 1
Enables: 5
Parallelizable: no
Files to modify:
Must touch files:
- `AGENTS.md`
- `docs/walkthroughs/walkthrough-WF-0082-codex-usage-optimization.md`
May touch files:
- `none`
Out of scope: adding new broad policy to `AGENTS.md`, changing terminology rules, or editing memory files
Stop if: the narrower trigger cannot be stated without introducing ambiguity about when `docs/index.md` is still required
Session boundary after: no
Acceptance Criteria:
- `AGENTS.md` no longer routes “any work request” through `docs/index.md`.
- The revised rule clearly distinguishes workflow/task tracking from ordinary code or doc work.
- Existing high-signal AGENTS safeguards remain intact and concise.
TDD Plan: N/A
Verification Steps:
- `rg -n "SSOT tasks|docs/index.md|any work request|workflow/task" AGENTS.md`
- `wc -l AGENTS.md`
Risks (if any): Over-correcting the trigger could make workflow/task tracking ambiguous or accidentally weaken other global guardrails.

### [x] Task 4 — Classify memory surfaces and add active-vs-reference routing

Goal:
Make the memory system cheaper to navigate by distinguishing the active router from history/reference-heavy memory surfaces without attempting a full memory redesign.
Slice: memory-routing
User Stories: US1, US2, US3
PRD Requirements: FR2, FR5, FR6, FR8, FR9
Depends on: 1, 2
Enables: 5
Parallelizable: no
Files to modify:
Must touch files:
- `docs/memory/index.md`
- `docs/memory/domain/project_docs.md`
- `docs/memory/tools/workflow.md`
May touch files:
- `none`
Out of scope: full reorganization of all memory files, new folder hierarchies, or sweeping edits across every memory leaf
Stop if: a safe classification requires touching additional memory files beyond this bounded surface or inventing a new memory subsystem
Session boundary after: yes
Acceptance Criteria:
- `docs/memory/index.md` clearly signals which memory surfaces are active routers versus reference/history-heavy material.
- `project_docs.md` and `workflow.md` gain explicit framing that prevents them from looking like default first-load context for every task.
- No existing durable rule is silently deleted; the change is classification/routing-first.
TDD Plan: N/A
Verification Steps:
- `rg -n "active|reference|history|on-demand|default" docs/memory/index.md docs/memory/domain/project_docs.md docs/memory/tools/workflow.md`
- `python3 - <<'PY'\nfrom pathlib import Path\nfor f in ['docs/memory/index.md','docs/memory/domain/project_docs.md','docs/memory/tools/workflow.md']:\n    text=Path(f).read_text()\n    print(f'{f}\\tchars={len(text)}\\test_tokens~={round(len(text)/4)}')\nPY`
Risks (if any): If the framing is too weak, the files remain practical default context; if too strong, genuinely useful guidance may become hard to find.

### [ ] Task 5 — Final verification and durable operating rule

Goal:
Record the before/after comparison, verify that routing/safety/terminology still hold, and encode the durable operating rule that future instruction surfaces must follow.
Slice: closure-policy
User Stories: US2, US3, US4
PRD Requirements: FR1, FR1A, FR5, FR8, FR9, FR10
Depends on: 2, 3, 4
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0082-codex-usage-optimization.md`
- `docs/logs/decisions.md`
- `docs/tasks/task-WF-0082-codex-usage-optimization.md`
May touch files:
- `none`
Out of scope: new cleanup work outside the already approved task slices
Stop if: the before/after estimate does not show a meaningful change or routing/safety checks fail, because Phase 3 should then stop for reassessment rather than forcing closure
Session boundary after: yes
Acceptance Criteria:
- The walkthrough captures the same before/after estimation method with explicit included surfaces and comparable values.
- The walkthrough or decision log records the durable operating rule for always-on, on-demand, and archival surfaces.
- Verification explicitly confirms preservation of workflow safety, provenance/traceability, and researcher-facing terminology.
TDD Plan: N/A
Verification Steps:
- `python3 - <<'PY'\nfrom pathlib import Path\nfiles=['AGENTS.md','docs/index.md','docs/memory/index.md']\ncombined=sum(len(Path(f).read_text()) for f in files)\nprint('combined_est_tokens', round(combined/4))\nfor f in files:\n    text=Path(f).read_text()\n    print(f'{f}\\tchars={len(text)}\\test_tokens~={round(len(text)/4)}')\nPY`
- `rg -n "before|after|default-load|always-on|on-demand|archival|traceability|terminology" docs/walkthroughs/walkthrough-WF-0082-codex-usage-optimization.md docs/logs/decisions.md`
Risks (if any): If closure evidence is hand-wavy, the WF may claim optimization success without actually proving that likely-load behavior improved safely.

## Changelog

- v0.1 (2026-04-03): Initial task breakdown from PRD
- v0.2 (2026-04-03): Applied review edits by restoring 3-file atomicity for the memory-routing task, tightening the tracer-bullet file surface, and adding stronger active-dashboard routing proof for the index compaction slice.
