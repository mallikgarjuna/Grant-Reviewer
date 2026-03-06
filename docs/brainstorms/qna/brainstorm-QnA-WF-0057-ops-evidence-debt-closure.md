# WF-0057 — Ops Evidence Debt Closure

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-06

---

## Section 1 — Problem Statement

**Brainstorming Q&A:**

**Q1: Primary defect we are fixing first**
- A) WF-0056: "Done" status with `<pending live run>` placeholders.
- B) WF-0040: waived observation/counts evidence backfill.
- C) Both in parallel, but WF-0056 must be unblocked first.
 > Recommendation: A. WF-0056 is internally inconsistent today (Done + "stub evidence invalid" + placeholders), so it is the highest-impact closure defect to fix first. B remains important but WF-0040 is explicitly documented as waived; WF-0056 claims completion while lacking the required evidence.
 > **Selected: A**

**Q2: Definition of "live evidence" for WF-0056**
- A) GitHub Actions run-backed evidence: run URL + `workflow_run_id` + `commit_sha` + artifact links + sha256 recorded in the walkthrough.
- B) Local CLI runs only, with sha256 + `commit_sha` recorded (no run URL/workflow id).
- C) Mix: local for verify, Actions for apply/rollback.
 > Recommendation: A. The WF-0056 walkthrough explicitly requires immutable workflow/commit linkage; Actions gives durable run identifiers and URLs, improving auditability and reducing "was this really live?" disputes. B can be a fallback but should not be used to claim "live rehearsal" completion.
 > **Selected: A**

**Q3: What we will do with `docs/index.md` status during this WF**
- A) Change WF-0056 status to non-Done until placeholders are removed.
- B) Leave WF-0056 as Done; only fix evidence content.
- C) Add a status note in WF-0057 only; do not touch WF-0056 status.
 > Recommendation: A. Status must align with evidence reality; leaving WF-0056 as Done while placeholders exist perpetuates the fake-done gap. Updating status makes the closure defect visible and forces correct sequencing.
 > **Selected: A**

**Q4: Evidence storage policy for WF-0056 (source of truth)**
- A) Use the existing `docs/walkthroughs/evidence/WF-0056/` paths and ensure they are populated and checksummed.
- B) Store evidence only as workflow artifacts; docs just link to run URLs.
- C) Store evidence only under a new WF-0057 evidence directory.
 > Recommendation: A. In-repo evidence paths + checksums are a durable fallback even if workflow artifacts expire. B is convenient but can decay over time. C is scope confusing and breaks the intended WF-0056 evidence bundle contract.
 > **Selected: A**

**Q5: WF-0040 backfill success threshold**
- A) Fill the missing checklist items with real environment evidence (observation windows + production counts), or explicitly re-waive with updated justification.
- B) Only produce updated replay/health artifacts; do not pursue environment evidence.
- C) Mark WF-0040 "not done" and reopen it instead of backfilling.
 > Recommendation: A. The point of this WF is closure truth, not just more local simulated artifacts. If we cannot access staging/prod evidence, that constraint must be re-stated with updated waiver rationale and owner sign-off rather than silently carried forward.
 > **Selected: A**
