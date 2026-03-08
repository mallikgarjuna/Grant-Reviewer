<!-- docs/tasks/task-WF-0066-peerlens-scope-lock-nwo-erc-msca.md -->
# WF-0066 — PeerLens Scope Lock to NWO/ERC/MSCA

Artifact: task
Version: v0.3
Status: Completed
Last Updated: 2026-03-08

Type: docs

## Task Breakdown (Sequential Order)

### [x] Task 1 — Inspect the named target set and classify edit vs verified no-op

Goal:
Inspect `docs/parking_lot.md`, `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, and `docs/mission.md` before any edits, record the per-file `edit required` vs `verified no-op` classification in the walkthrough, and capture the Phase 3 baseline commit SHA there before any implementation edits so later verification can compare against a deterministic range.
Slice: target-set-inspection
User Stories: US1, US2, US3, US4
PRD Requirements: FR1, FR1a, FR6, FR7, FR8, FR10, FR10a
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0066-peerlens-scope-lock-nwo-erc-msca.md`
May touch files:
- `none`
Out of scope: editing the named target docs during inspection, widening to non-target docs, claiming mission contradiction without quoting the sentence
Stop if: inspection shows any active contradiction outside the named target set, or `docs/logs/decisions.md` / `docs/memory/domain/project_docs.md` need semantic edits beyond the already-landed scope-lock wording
Session boundary after: no
Acceptance Criteria:
- The walkthrough records one pre-state row for each named file: `docs/parking_lot.md`, `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, and `docs/mission.md`.
- The walkthrough records one explicit `phase_3_baseline_sha` captured before any implementation edit.
- The recorded expected classification from current repo reality is `edit required` for `docs/parking_lot.md` and `verified no-op` for the other three named targets.
- The inspection explicitly calls out every active contradiction-bearing `docs/parking_lot.md` location that must be fixed later in Phase 3, including any active rows outside the P1 rationale snapshot.
- The inspection explicitly confirms the mission check happened before any mission edit is considered.
TDD Plan: N/A
Verification Steps:
- `git rev-parse HEAD`
- `sed -n '/## 🟡 P1/,/## Rejected \\/ Ignored/p' docs/parking_lot.md | rg -n "ZonMw|remaining promised-program gap|launch blocker|broader promised-program expansion|broader coverage remains part of the current commitment"`
- `rg -n "AD 66\\.1|broader promised-program expansion is not deferred" docs/logs/decisions.md`
- `rg -n "broader scope commitments beyond NWO/ERC/MSCA" docs/memory/domain/project_docs.md`
- `sed -n '1,120p' docs/mission.md`
Risks (if any): If the inspection scan is too broad, execution will falsely treat historical wording as an active contradiction and widen the edit set.

### [x] Task 2 — Tracer bullet: rewrite all active parking-lot contradictions without touching historical sections

Goal:
Rewrite every active contradiction-bearing `docs/parking_lot.md` row or rationale line so launch readiness is framed around truthful usefulness within the permanent NWO/ERC/MSCA wedge instead of a missing broader-program expansion, while preserving the no-op status of the other named targets and leaving historical sections untouched.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR1, FR1a, FR2, FR3, FR5, FR9
Depends on: 1
Enables: 3
Parallelizable: no
Files to modify:
Must touch files:
- `docs/parking_lot.md`
- `docs/walkthroughs/walkthrough-WF-0066-peerlens-scope-lock-nwo-erc-msca.md`
May touch files:
- `none`
Out of scope: adding new agency/program work, rewriting historical backlog provenance, changing `docs/logs/decisions.md`, changing `docs/memory/domain/project_docs.md`, changing `docs/mission.md`
Stop if: removing the stale blocker requires widening beyond `docs/parking_lot.md` or inventing replacement roadmap work that is not already justified by the PRD
Session boundary after: no
Acceptance Criteria:
- Every active contradiction-bearing row or rationale line in `docs/parking_lot.md` no longer states or implies that ZonMw or another broader promised-program gap is planned, deferred, or required for launch.
- The replacement wording explicitly anchors launch readiness to truthful usefulness within the NWO/ERC/MSCA wedge.
- Active dependency notes outside P1 that still encode the forbidden breadth gap are either rewritten or explicitly confirmed absent.
- Historical sections in `docs/parking_lot.md` remain intact except for minimal provenance-safe superseding wording tied to active planning truth.
- The walkthrough records `docs/parking_lot.md` as `edited` and the other named targets as still pending final no-op confirmation.
TDD Plan: N/A
Verification Steps:
- `sed -n '/## 🟡 P1/,/## Rejected \\/ Ignored/p' docs/parking_lot.md | rg -n "truthful|usefulness|NWO/ERC/MSCA|launch readiness"`
- `bash -lc '! sed -n "/## 🟡 P1/,/## Rejected \\/ Ignored/p" docs/parking_lot.md | rg -n "ZonMw|remaining promised-program gap|launch blocker|broader promised-program expansion|broader coverage remains part of the current commitment"'`
- `git diff -- docs/parking_lot.md docs/walkthroughs/walkthrough-WF-0066-peerlens-scope-lock-nwo-erc-msca.md`
Risks (if any): A too-generic rewrite can remove the stale blocker but leave no actionable launch-readiness framing.

### [x] Task 3 — Produce the named-file evidence bundle and prove scope stayed narrow

Goal:
Finalize the walkthrough evidence bundle for the four named docs so WF-0066 cannot be closed with a generic “docs verified” claim.
Slice: closure-evidence
User Stories: US1, US2, US3, US4
PRD Requirements: FR1a, FR4, FR8, FR10, FR10a
Depends on: 2
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `docs/walkthroughs/walkthrough-WF-0066-peerlens-scope-lock-nwo-erc-msca.md`
May touch files:
- `none`
Out of scope: additional content edits, repo-wide scans that hide named-file results, any recommendation to proceed without explicit pass/fail evidence
Stop if: the evidence cannot name each inspected file, its action (`edited` or `verified no-op`), and deterministic command output proving the result
Session boundary after: yes
Acceptance Criteria:
- The final walkthrough evidence bundle has four rows covering `docs/parking_lot.md`, `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, and `docs/mission.md`.
- Each row records `pre-state`, `action`, `post-state`, and `pass/fail`.
- Verification proves against the recorded `phase_3_baseline_sha` that only contradiction-bearing live docs changed and that historical/completed artifacts were not edited for this WF.
- Mission-check evidence explicitly shows that `docs/mission.md` stayed unchanged unless a concrete contradiction was logged.
TDD Plan: N/A
Verification Steps:
- `rg -n "AD 66\\.1|broader promised-program expansion is not deferred" docs/logs/decisions.md`
- `rg -n "broader scope commitments beyond NWO/ERC/MSCA" docs/memory/domain/project_docs.md`
- `git diff --exit-code <phase_3_baseline_sha> -- docs/mission.md`
- `git diff --name-only <phase_3_baseline_sha>...HEAD -- docs/parking_lot.md docs/logs/decisions.md docs/memory/domain/project_docs.md docs/mission.md docs/walkthroughs/walkthrough-WF-0066-peerlens-scope-lock-nwo-erc-msca.md`
- `bash -lc 'test -z "$(git diff --name-only <phase_3_baseline_sha>...HEAD | rg -n \"^(docs/parking_lot\\\\.md|docs/tasks/task-WF-0066-peerlens-scope-lock-nwo-erc-msca\\\\.md|docs/walkthroughs/walkthrough-WF-0066-peerlens-scope-lock-nwo-erc-msca\\\\.md|docs/index\\\\.md)$\" -v)"'`
Risks (if any): If closure depends on the live worktree instead of the recorded baseline range, the workflow can incorrectly pass or fail depending on unrelated branch state.

## Changelog

- v0.1 (2026-03-08): Initial task breakdown from PRD.
- v0.2 (2026-03-08): Reordered tasks so named-target inspection happens before edits, narrowed stale-language verification to the active P1 surface, and assigned the evidence bundle to the walkthrough artifact; marked Ready for Implementation.
- v0.3 (2026-03-08): Applied Phase 2 audit fixes by widening parking-lot contradiction coverage beyond P1, removing self-modifying task scope, and requiring baseline-anchored verification evidence instead of raw worktree diffs.
- v0.4 (2026-03-08): Marked all Phase 3 tasks complete after walkthrough evidence closure and updated task artifact status to Completed.
