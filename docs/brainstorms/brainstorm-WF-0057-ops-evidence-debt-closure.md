# WF-0057 — Ops Evidence Debt Closure

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-06

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts/decisions (what we will implement).
- The Q&A transcript is rationale only; it must not introduce new contracts.

## Context / Trigger

- Promote `docs/parking_lot.md` P1 #10 (WF-0040 gate evidence backfill) rather than starting a new hardening WF.
- Closure defect: `docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md` is marked Done in `docs/index.md` but still contains `<pending live run>` placeholders for verify/apply/rollback evidence.

## Repo Reality Snapshot (Read-Only) (2026-03-06)

- WF-0056 walkthrough is marked Done but still has `<pending live run>` placeholders in its Evidence Chain table.
- That walkthrough also states stub/static evidence is invalid for WF-0056 completion, creating an internal closure contradiction.
- WF-0040 walkthrough is explicitly waived for staging/prod observation windows and per-call production counts (follow-up evidence debt).
- `docs/index.md` can show "Done" while walkthroughs still carry waived/placeholder evidence gates.
- This WF-0057 is explicitly about closing that residual evidence debt, not adding new hardening scope.

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 1)

### Problem

The repo has a "fake-done ops" gap: workflows can be marked Done while required live-run evidence remains placeholder/waived, which breaks governance traceability and makes sequencing decisions unreliable.

Primary closure defect:
- WF-0056 is marked Done, but its walkthrough evidence chain still contains `<pending live run>` placeholders for required fields.

Secondary evidence debt:
- WF-0040 is closed via waiver because real staging/prod observation-window evidence and per-call production counts were unavailable.

### Contract Notes / Non-Obvious Constraints (Section 1)

- Definition of "live evidence" for WF-0056: GitHub Actions run-backed evidence with run URL, `workflow_run_id`, `commit_sha`, artifact links, and sha256 checksums recorded (no placeholders).
- During this WF, WF-0056 must not remain "Done" if the placeholders persist; status must align with evidence reality.
- Evidence must be stored in the existing `docs/walkthroughs/evidence/WF-0056/` paths with checksums as a durable fallback (workflow artifacts can be transient).
- WF-0040 evidence backfill must either produce real environment evidence (observation windows + counts) or explicitly re-waive with updated constraints and owner sign-off (no silent carry-forward).

### Non-Goals

- No new governance hardening ideas or new policy surface scope.
- No "simulated" evidence presented as live; simulated artifacts may be kept only as explicitly labeled non-live.

## Open Questions / Deferred

- Do we have permissions and access to run (and retrieve artifacts from) the GitHub Actions runs needed for WF-0056 "live evidence"?
- Do we have access to staging/prod telemetry needed to satisfy WF-0040 observation-window and per-call count evidence?

---

## 2. Desired Outcome

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 2)

### Definition of Success (Binary)

- WF-0056: no `<pending live run>` placeholders remain; evidence chain is fully populated with real values and is auditable end-to-end.
- WF-0040: missing observation/count gates are either (a) backed by real environment evidence, or (b) explicitly re-waived with updated constraints and owner sign-off (no silent carry-forward).
- Repo status semantics: "Done" is evidence-backed; placeholders/waivers are visible and not mislabeled as Done.

### Acceptance Checklist (Must-Haves)

WF-0056:
- Evidence files exist at `docs/walkthroughs/evidence/WF-0056/` as referenced by the walkthrough.
- Checksums are recorded (e.g., `evidence_sha256`, and snapshot checksums if applicable).
- Walkthrough Evidence Chain table has real values for `workflow_run_id`, run URL, `commit_sha`, and `linked_artifacts`.

WF-0040:
- Checklist items for staging/prod observation windows and per-call counts are addressed with real evidence, or an updated explicit waiver is recorded (constraints + rationale + owner sign-off + date).

### Evidence Field Requirements (Minimum)

WF-0056 evidence chain table (walkthrough) must include real values for:
- `workflow_run_id`
- `run URL`
- `commit_sha`
- `linked_artifacts` (enough to retrieve artifacts deterministically later)
- Checksums (`evidence_sha256` and snapshot checksums where applicable)

WF-0040 evidence backfill must record, at minimum:
- Environment (`staging` / `prod`)
- Observation window start/end timestamps (and whether v1-only routing was active)
- Result (`pass` / `fail` / `unavailable`)
- Per-call completed request counts for the relevant window
- Source links (dashboard links, log queries, exported reports) or a short "how to reproduce the query"
- Explicit waiver record if evidence is unavailable (see template below)

### Files This WF Intends To Update (Explicit)

- `docs/index.md` (WF-0056 status semantics; WF-0040 status semantics if they change)
- `docs/walkthroughs/completed/walkthrough-WF-0056-platform-policy-enforcement-live-rehearsal.md` (replace placeholders)
- `docs/walkthroughs/evidence/WF-0056/` (ensure referenced evidence exists + checksums)
- `docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md` (backfill evidence or record updated explicit waiver + sign-off)

### WF-0040 Waiver Record Template (If Evidence Unavailable)

If staging/prod observation or counts cannot be produced in this environment, record:
- Date
- Gate(s) waived (staging window, prod window, counts threshold)
- Why unavailable (exact constraint)
- Residual risk statement
- Owner sign-off (who/where)
and keep WF status semantics non-misleading (no silent "Done" that reads like evidence-backed closure).

---

## 3. Target User / Actor

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 3)

- Primary actor: repo owner/operator performing the live verify/apply/rollback rehearsals and capturing evidence.
- Secondary actor: maintainer/auditor verifying governance claims from docs alone (no tribal knowledge).

---

## 4. Rough Idea (Non-Architectural)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 4)

- WF-0056:
  - Execute the intended live verify/apply/rollback rehearsals via GitHub Actions-backed runs (preferred), producing evidence artifacts.
  - Update the WF-0056 walkthrough Evidence Chain table to replace placeholders with real run IDs/URLs/commit SHA and checksum values.
  - Align `docs/index.md` WF-0056 status to non-Done until placeholders are removed.
- WF-0040:
  - Define the minimum acceptable "runtime observation + counts" evidence record.
  - Backfill the missing checklist items with real environment evidence if available; otherwise re-waive explicitly with updated constraints and owner sign-off.

---

## 5. Constraints

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 5)

- Do not start new governance hardening scope until evidence debt is closed (this WF is about closure truth).
- Prefer durable evidence in-repo (checksummed) because workflow artifacts can expire.
- If access/permissions prevent producing live evidence, treat that as an explicit blocker and align statuses accordingly (no "fake-done").

---

## 6. Risks / Unknowns

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 6)

- Permissions/access risk:
  - Can we run the required Actions workflows and retrieve artifact metadata/IDs/URLs?
  - Can we access staging/prod telemetry for WF-0040 observation/count evidence?
- Evidence retention risk: artifact retention policies may delete evidence if not also stored in-repo with checksums.
- Status drift risk: future WFs could reintroduce "Done" without evidence unless the rule is written and followed.

---

## 7. MVP Definition

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 7)

If we had to ship in 2-3 days:
- Fix WF-0056 first: remove all placeholders by producing real live-run evidence and recording it.
- Then close WF-0040 evidence debt: real evidence if possible, otherwise explicit re-waive with updated constraints/sign-off.
- Ensure `docs/index.md` statuses reflect evidence reality (no Done while placeholders/waived gates exist without explicit waiver).

---

## 8. Explicit Non-Goals

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0057-ops-evidence-debt-closure.md` (Section 8)

- No new policy enforcement features or expansion of governance scope.
- No refactors unrelated to evidence capture, evidence linkage, and status alignment.
- No simulated/local-only artifacts presented as "live rehearsal" completion for WF-0056.
