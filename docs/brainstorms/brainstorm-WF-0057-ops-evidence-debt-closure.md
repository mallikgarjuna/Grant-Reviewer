# WF-0057 — Ops Evidence Debt Closure

Artifact: brainstorm
Version: v0.1
Status: Draft
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
