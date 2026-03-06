# WF-0057 — Ops Evidence Debt Closure

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-06

## Task Breakdown (Sequential Order)

### [x] Task 1 — Tracer bullet: close one WF-0056 live-evidence row end-to-end

Goal:
Replace one required WF-0056 Evidence Chain placeholder row with real live-run metadata and linked artifact checksum to prove the closure path works end-to-end.
Slice: tracer-bullet
User Stories: US1, US4
PRD Requirements: FR1, FR2, FR3, FR8
Depends on: none
Enables: 2, 6
Parallelizable: no
Files to modify:
- `docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md`
- `docs/walkthroughs/evidence/WF-0056/README.md`
- `docs/walkthroughs/evidence/WF-0056/live-run-index.md` (new)
Acceptance Criteria:
- At least one required Evidence Chain row no longer uses `<pending live run>` and includes real `workflow_run_id`, run URL, `commit_sha`, and `linked_artifacts`.
- The referenced artifact path exists in `docs/walkthroughs/evidence/WF-0056/` and has an `evidence_sha256` entry.
- Evidence location and checksum workflow are documented so another maintainer can reproduce lookup.
TDD Plan: N/A (documentation and evidence bookkeeping)
Verification Steps:
- `rg -n "<pending live run>|workflow_run_id|commit_sha|linked_artifacts|evidence_sha256" docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md docs/walkthroughs/evidence/WF-0056/README.md docs/walkthroughs/evidence/WF-0056/live-run-index.md`
- `test -f docs/walkthroughs/evidence/WF-0056/live-run-index.md`
Risks (if any): Live run metadata may be unavailable in the current environment, forcing a documented blocker state.

### [x] Task 2 — Complete WF-0056 evidence-chain replacement for verify/apply/rollback

Goal:
Replace all remaining required WF-0056 placeholders with real live evidence metadata for verify/apply/rollback flows.
Slice: wf0056-evidence-completion
User Stories: US1, US4
PRD Requirements: FR1, FR2, FR3, FR7, FR8
Depends on: 1
Enables: 5, 6
Parallelizable: no
Files to modify:
- `docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md`
- `docs/walkthroughs/evidence/WF-0056/live-run-index.md`
- `docs/walkthroughs/evidence/WF-0056/README.md`
Acceptance Criteria:
- No required WF-0056 evidence field contains `<pending live run>`.
- Verify/apply/rollback rows each include real `workflow_run_id`, run URL, `commit_sha`, `linked_artifacts`, and `evidence_sha256` values.
- Linked artifact references are deterministic and resolvable from repo docs alone.
TDD Plan: N/A (documentation and evidence bookkeeping)
Verification Steps:
- `if rg -n "<pending live run>" docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md; then echo "placeholders remain"; exit 1; else echo "no placeholders"; fi`
- `rg -n "verify|apply|rollback|workflow_run_id|commit_sha|linked_artifacts|evidence_sha256" docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md docs/walkthroughs/evidence/WF-0056/live-run-index.md`
Risks (if any): If any run artifact cannot be recovered, completion must be replaced by explicit debt/waiver state rather than synthetic placeholders.

### [x] Task 3 — Decide WF-0040 closure path (backfill vs waiver refresh) with owner traceability

Goal:
Record a single explicit WF-0040 closure strategy decision and owner/sign-off trail before updating runtime evidence claims.
Slice: wf0040-decision-gate
User Stories: US2, US4
PRD Requirements: FR4, FR5, FR7, FR8
Depends on: 2
Enables: 4
Parallelizable: no
Files to modify:
- `docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
- `docs/logs/decisions.md`
Acceptance Criteria:
- WF-0040 walkthrough explicitly states chosen closure path: real backfill or waiver refresh.
- `docs/logs/decisions.md` records owner sign-off location and date for the chosen path.
- Decision text states why the alternative path was not used in this run.
TDD Plan: N/A (documentation and decision log updates)
Verification Steps:
- `rg -n "WF-0040|backfill|waiver|owner|sign-off|date" docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md docs/logs/decisions.md`
Risks (if any): Missing owner sign-off metadata blocks closure regardless of technical evidence completeness.

### [ ] Task 4 — Close WF-0040 runtime evidence debt using selected path

Goal:
Execute the selected WF-0040 closure path and remove unresolved runtime-evidence ambiguity.
Slice: wf0040-closure-execution
User Stories: US2, US4
PRD Requirements: FR4, FR5, FR7, FR8
Depends on: 3
Enables: 5, 6
Parallelizable: no
Files to modify:
- `docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
- `docs/logs/decisions.md`
- `docs/walkthroughs/evidence/WF-0040/runtime-evidence-index.md` (new, if backfill path)
Acceptance Criteria:
- Exactly one closure mode is fully documented: either reproducible real observation/count evidence, or refreshed waiver with waived gates, exact constraint, residual risk, owner sign-off, and date.
- WF-0040 walkthrough no longer leaves runtime gates in an implicit or ambiguous state.
- If backfill is used, source links/query steps and count evidence are recorded deterministically.
TDD Plan: N/A (documentation and evidence/waiver records)
Verification Steps:
- `rg -n "observation window|per-call|waived gate|residual risk|constraint|owner sign-off" docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md docs/logs/decisions.md`
- `test ! -f docs/walkthroughs/evidence/WF-0040/runtime-evidence-index.md || rg -n "source|query|count|sha256" docs/walkthroughs/evidence/WF-0040/runtime-evidence-index.md`
- `python - <<'PY'\nfrom pathlib import Path\ntext = Path(\"docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md\").read_text()\nhas_backfill = \"observation window\" in text and \"per-call\" in text\nhas_waiver = \"waived gate\" in text and \"residual risk\" in text and \"owner sign-off\" in text\nraise SystemExit(0 if has_backfill ^ has_waiver else 1)\nPY`
Risks (if any): Telemetry access limits can force waiver path; waiver quality must still satisfy FR5.

### [ ] Task 5 — Align WF-0056/WF-0040 status semantics in docs index

Goal:
Update status semantics in `docs/index.md` so WF-0056 and WF-0040 states truthfully reflect evidence-backed or waiver-backed closure.
Slice: status-semantics
User Stories: US3
PRD Requirements: FR6, FR8
Depends on: 2, 4
Enables: 6
Parallelizable: no
Files to modify:
- `docs/index.md`
- `docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md`
- `docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
Acceptance Criteria:
- WF rows do not imply evidence-backed `Done` while unresolved debt remains.
- Status labels explicitly match closure evidence or waiver reality recorded in walkthroughs.
- Status wording is consistent between index and walkthrough status markers.
TDD Plan: N/A (documentation status alignment)
Verification Steps:
- `rg -n "WF-0040|WF-0056|Done|waiver|debt|evidence" docs/index.md docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`
Risks (if any): Historical expectations around `Done` can conflict with strict evidence semantics.

### [ ] Task 6 — Final audit pass for docs-only closure package

Goal:
Perform one deterministic docs-only audit pass proving WF-0057 closure can be verified without tribal knowledge.
Slice: closure-audit
User Stories: US1, US2, US3, US4
PRD Requirements: FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8
Depends on: 5
Enables: none
Parallelizable: no
Files to modify:
- `docs/walkthroughs/walkthrough-WF-0057-ops-evidence-debt-closure.md`
- `docs/logs/decisions.md`
Acceptance Criteria:
- WF-0057 walkthrough records what was closed, what evidence/waiver references were used, and what remains (if anything).
- Closure checklist includes explicit pass/fail for WF-0056 placeholders, WF-0040 runtime gates, and index semantic alignment.
- Decisions log has final closure note with audit date and reviewer identity.
TDD Plan: N/A (documentation closure audit)
Verification Steps:
- `rg -n "WF-0057|placeholder|runtime gate|index status|pass|fail|reviewer|date" docs/walkthroughs/walkthrough-WF-0057-ops-evidence-debt-closure.md docs/logs/decisions.md`
- `if rg -n "<pending live run>" docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md; then echo "placeholders remain"; exit 1; else echo "no placeholders"; fi`
Risks (if any): Without explicit pass/fail checklist fields, future audits may reintroduce subjective interpretation.

## Changelog

- v0.1 (2026-03-06): Initial task breakdown from PRD
- v0.2 (2026-03-06): Applied Phase 2.2 review edits; tightened verification commands for placeholder absence and WF-0040 single-path closure proof; marked Ready for Implementation
