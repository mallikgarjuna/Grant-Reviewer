# WF-0057 — Ops Evidence Debt Closure

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-06

---

## 0. User Stories (MVP)

- US1: As a maintainer, I want WF-0056 walkthrough evidence placeholders replaced with real live-run evidence, so that closure is auditable and not "fake-done."
- US2: As a maintainer, I want WF-0040 runtime evidence debt resolved via real backfill or explicit re-waiver with owner sign-off, so that closure claims are truthful.
- US3: As an auditor, I want `docs/index.md` status semantics aligned to evidence reality, so that "Done" reliably means evidence-backed completion.
- US4: As an operator, I want a deterministic evidence record contract for walkthroughs, so that future reviewers can reproduce and verify governance claims.

## Deferred Stories (Not in MVP)

- Build new policy-enforcement automation or new governance feature surfaces.
- Add net-new CI gates beyond what is needed to document and close current debt.
- Re-architect workflow system or revise historical WFs outside WF-0056/WF-0040 closure semantics.

## 1. In Scope

- Replace WF-0056 walkthrough `<pending live run>` entries with real live-run evidence metadata and links.
- Ensure WF-0056 evidence artifacts referenced by walkthrough exist in `docs/walkthroughs/evidence/WF-0056/` and include checksums.
- Resolve WF-0040 missing observation-window/count evidence via:
  - real evidence backfill, or
  - explicit waiver refresh with constraints, rationale, owner sign-off, and date.
- Reconcile `docs/index.md` WF status labels with the evidence state for WF-0056 and WF-0040.
- Capture closure decisions in `docs/logs/decisions.md` when architecture/scope/contract choices are made.

## 2. Out of Scope

- New hardening initiatives unrelated to existing evidence debt.
- Synthetic or simulated evidence presented as live.
- Refactors outside the workflow docs/evidence/status surfaces needed for closure truth.

## 3. User / System Flow

### Happy path

1. Operator collects live GitHub Actions evidence for WF-0056 verify/apply/rollback and stores durable references and checksums (US1, US4).
2. Operator updates WF-0056 walkthrough Evidence Chain rows with real `workflow_run_id`, run URL, `commit_sha`, and `linked_artifacts` references (US1, US4).
3. Operator evaluates WF-0040 evidence debt and either attaches real staging/prod observation/count evidence or records an explicit re-waiver with owner sign-off (US2, US4).
4. Maintainer updates `docs/index.md` statuses so workflows with unresolved placeholders are not shown as evidence-backed Done (US3).
5. Auditor can review docs-only artifacts and confirm closure consistency without tribal knowledge (US1, US2, US3, US4).

### Failure path A — Live evidence unavailable

1. Required live run access/artifacts are unavailable in current environment (US1, US4).
2. Workflow is not marked Done; blocker or explicit waiver state is documented with constraint details (US2, US3).

### Failure path B — WF-0040 telemetry unavailable

1. Staging/prod observation windows or per-call counts cannot be produced (US2, US4).
2. Updated explicit waiver record is created with risk/tradeoff and owner sign-off; status semantics remain non-misleading (US2, US3).

### Failure path C — Evidence links incomplete

1. Walkthrough points to evidence files that are missing or not checksummed (US1, US4).
2. Closure is blocked until references are repaired and checksum fields are populated (US1, US4).

## 4. Functional Requirements

- FR1 (US1): WF-0056 walkthrough Evidence Chain must not contain `<pending live run>` placeholders for required live-run fields.
- FR2 (US1, US4): WF-0056 walkthrough must record real `workflow_run_id`, run URL, `commit_sha`, and deterministic `linked_artifacts` references.
- FR3 (US1, US4): Referenced WF-0056 evidence artifacts must exist at documented paths and include `evidence_sha256` (and snapshot checksum where applicable).
- FR4 (US2): WF-0040 unresolved runtime gates must be closed by either real evidence backfill or an explicit refreshed waiver record.
- FR5 (US2, US4): Any WF-0040 waiver must include date, waived gates, exact constraint, residual risk, owner sign-off, and where sign-off is recorded.
- FR6 (US3): `docs/index.md` status values for WF-0056/WF-0040 must align with evidence reality and never silently imply evidence-backed Done when debt remains.
- FR7 (US4): Evidence records must include enough source linkage to reproduce verification intent (links or deterministic query steps for counts/telemetry).
- FR8 (US1, US2, US3): Final closure package must be auditable via repo docs alone (walkthrough + evidence files + index status + decisions log).

## 5. Data & API Contracts

### WF-0056 evidence chain contract (FR1, FR2, FR3, FR8)

- Required walkthrough fields with real values: `workflow_run_id`, run URL, `commit_sha`, `linked_artifacts`, `evidence_sha256`.
- `linked_artifacts` must be sufficient to locate evidence deterministically later (artifact names/paths and run linkage).
- Placeholder tokens (including `<pending live run>`) are invalid in closure-ready state.

### WF-0040 waiver/evidence contract (FR4, FR5, FR7, FR8)

- For real backfill: record environment, observation window start/end, routing context, result, per-call counts, and source references.
- For waiver refresh: record date, waived gate list, exact blocking constraint, residual risk statement, owner sign-off identity/location.
- Silent carry-forward waivers without refreshed metadata are invalid.

### Status semantics contract (FR6, FR8)

- `Done` denotes evidence-backed closure or explicit waiver-backed closure with visible waiver details.
- If required evidence is unresolved, status must remain non-Done (or explicitly marked waiver/debt state).

## 6. Components / Modules

- `docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md`: canonical evidence-chain truth for WF-0056 closure.
- `docs/walkthroughs/evidence/WF-0056/`: durable evidence files and checksums referenced by walkthrough.
- `docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`: runtime evidence backfill or explicit waiver refresh.
- `docs/index.md`: status registry semantics for WF closure readiness.
- `docs/logs/decisions.md`: major scope/contract/status decisions for traceability.

## 7. Edge Cases

- WF-0056 has mixed state where some runs are live and others remain placeholders (US1, FR1, FR2).
- Artifact URLs resolve but evidence files/checksums are missing in-repo fallback paths (US1, FR3).
- WF-0040 has partial telemetry (window timestamps but no counts) requiring explicit pass/fail/unavailable handling (US2, FR4, FR7).
- Owner sign-off exists in chat but not traceably linked in docs (US2, FR5, FR8).
- Index row is updated before walkthrough evidence is corrected, causing temporary semantic drift (US3, FR6).

## 8. Testing Decisions (TDD)

- Behavior-change rule applies to any automation/script edits used to validate evidence placeholders or status semantics; use RED → GREEN → refactor.
- Public verification seams:
  - walkthrough evidence-chain field completeness checks,
  - evidence artifact presence + checksum checks,
  - index status alignment checks against documented evidence state.
- Boundary mocking only when adding automation (e.g., GitHub API retrieval adapters); do not mock internal closure decision logic.
- Minimum prove-it checks by story:
  - US1: prove no required WF-0056 placeholders remain and fields are real-valued.
  - US2: prove WF-0040 has either real backfill data or refreshed explicit waiver record.
  - US3: prove index status text matches documented closure state.
  - US4: prove evidence references/checksums are traceable and reproducible.

## 9. Telemetry (Minimal)

- Capture run identifiers and commit SHAs used as closure evidence.
- Capture count of missing/placeholder required fields before and after closure update.
- Capture unresolved gate count for WF-0040 (pre/post update).

## 10. Deferred / Not in MVP

- New enforcement tooling to prevent future evidence debt automatically.
- Broad historical audit/remediation of all older workflows.
- Expansion of runtime policy surface beyond WF-0056/WF-0040 debt closure.

## 11. Open Questions (if any)

- Do current credentials allow collecting all required WF-0056 live-run artifacts?
- Is staging/prod telemetry access available now for WF-0040 evidence backfill, or will waiver refresh be required?

## 12. Changelog

- v0.1 (2026-03-06): Initial PRD from brainstorm.
- v0.2 (2026-03-06): Applied Phase 1 risk-audit refinements; clarified waiver contract, status semantics, and closure traceability; marked Ready for Tasks.
