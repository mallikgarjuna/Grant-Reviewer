<!-- docs/tasks/task-WF-0066-peerlens-scope-lock-nwo-erc-msca.md -->
# WF-0066 — PeerLens Scope Lock to NWO/ERC/MSCA

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

Type: docs

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Tracer bullet: remove the active breadth blocker from the parking lot

Goal:
Rewrite the active P1 contradiction in `docs/parking_lot.md` so launch readiness is framed around truthful usefulness within the permanent NWO/ERC/MSCA wedge instead of a missing broader-program expansion.
Slice: tracer-bullet
User Stories: US1, US2, US3
PRD Requirements: FR1, FR1a, FR2, FR3, FR5, FR9
Depends on: none
Enables: 2, 3
Parallelizable: no
Files to modify:
Must touch files:
- `docs/parking_lot.md`
May touch files:
- `none`
Out of scope: adding new agency/program work, rewriting historical backlog provenance, changing `docs/logs/decisions.md`, changing `docs/memory/domain/project_docs.md`, changing `docs/mission.md`
Stop if: removing the stale blocker requires widening beyond `docs/parking_lot.md` or inventing replacement roadmap work that is not already justified by the PRD
Session boundary after: no
Acceptance Criteria:
- Active P1 rows and the P1 rationale snapshot no longer state or imply that ZonMw or another broader promised-program gap is planned, deferred, or required for launch.
- The replacement wording explicitly anchors launch readiness to truthful usefulness within the NWO/ERC/MSCA wedge.
- Historical sections in `docs/parking_lot.md` remain intact except for minimal provenance-safe superseding wording tied to active planning truth.
TDD Plan: N/A
Verification Steps:
- `rg -n "ZonMw|promised-program|launch blocker|launch-critical|broader coverage|breadth" docs/parking_lot.md`
- `git diff -- docs/parking_lot.md`
Risks (if any): A too-generic rewrite can remove the stale blocker but leave no actionable launch-readiness framing.

### [ ] Task 2 — Verify the other named targets and keep compliant docs as no-op

Goal:
Inspect `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, and `docs/mission.md`; preserve them as verified no-ops unless a concrete active contradiction or missing scope-lock rule is found at execution time.
Slice: scope-lock-anchor-verification
User Stories: US2, US3, US4
PRD Requirements: FR1, FR1a, FR6, FR7, FR8, FR9
Depends on: 1
Enables: 3
Parallelizable: no
Files to modify:
Must touch files:
- `none`
May touch files:
- `docs/logs/decisions.md`
- `docs/memory/domain/project_docs.md`
- `docs/mission.md`
Out of scope: gratuitous rewrites of already compliant docs, edits to completed artifacts, mission restyling without a quoted contradiction, widening to any doc outside the named target set
Stop if: more than one supposedly compliant target doc needs a real edit, or `docs/mission.md` appears to require a mission rewrite rather than a contradiction fix
Session boundary after: no
Acceptance Criteria:
- `docs/logs/decisions.md` still contains an explicit WF-0066 scope-lock decision compatible with the permanent NWO/ERC/MSCA wedge.
- `docs/memory/domain/project_docs.md` still contains an explicit future-session rule preventing reintroduction of broader scope commitments beyond NWO/ERC/MSCA.
- `docs/mission.md` is explicitly checked and remains unchanged unless a concrete contradictory sentence is identified.
- Each of the three named docs receives an explicit execution result of `edited` or `verified no-op`; the expected outcome from current repo reality is `verified no-op` for all three.
TDD Plan: N/A
Verification Steps:
- `rg -n "WF-0066|NWO/ERC/MSCA|broader promised-program expansion is not deferred|broader scope commitments beyond NWO/ERC/MSCA|mission" docs/logs/decisions.md docs/memory/domain/project_docs.md docs/mission.md`
- `git diff --name-only -- docs/logs/decisions.md docs/memory/domain/project_docs.md docs/mission.md`
Risks (if any): Treating “inspect all” as “edit all” would create unnecessary churn and violate provenance rules.

### [ ] Task 3 — Produce the named-file evidence bundle and prove scope stayed narrow

Goal:
Generate the final pass/fail evidence bundle for the four named docs so WF-0066 cannot be closed with a generic “docs verified” claim.
Slice: closure-evidence
User Stories: US1, US2, US3, US4
PRD Requirements: FR1a, FR4, FR8, FR10, FR10a
Depends on: 2
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `none`
May touch files:
- `none`
Out of scope: additional content edits, repo-wide scans that hide named-file results, any recommendation to proceed without explicit pass/fail evidence
Stop if: the evidence cannot name each inspected file, its action (`edited` or `verified no-op`), and deterministic command output proving the result
Session boundary after: yes
Acceptance Criteria:
- The final evidence bundle has four rows covering `docs/parking_lot.md`, `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, and `docs/mission.md`.
- Each row records `pre-state`, `action`, `post-state`, and `pass/fail`.
- Verification proves that only contradiction-bearing live docs changed and that historical/completed artifacts were not edited for this WF.
- Mission-check evidence explicitly shows that `docs/mission.md` stayed unchanged unless a concrete contradiction was logged.
TDD Plan: N/A
Verification Steps:
- `rg -n "ZonMw|promised-program|launch blocker|launch-critical|broader coverage|breadth|WF-0066|NWO/ERC/MSCA" docs/parking_lot.md docs/logs/decisions.md docs/memory/domain/project_docs.md docs/mission.md`
- `git diff --name-only`
- `git diff --name-only -- docs/parking_lot.md docs/logs/decisions.md docs/memory/domain/project_docs.md docs/mission.md docs/index.md`
Risks (if any): If closure depends on a repo-wide assertion instead of named-file evidence, the workflow can incorrectly pass while hiding scope drift.

## Changelog

- v0.1 (2026-03-08): Initial task breakdown from PRD.
