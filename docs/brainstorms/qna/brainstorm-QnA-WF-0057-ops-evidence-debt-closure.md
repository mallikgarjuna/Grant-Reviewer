# WF-0057 — Ops Evidence Debt Closure

Artifact: brainstorm-qna
Version: v0.3
Status: Draft Complete
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

---

## Section 2 — Desired Outcome

**Brainstorming Q&A:**

**Q1: What is the primary success metric for WF-0057?**
- A) Zero `<pending live run>` placeholders anywhere; WF-0056 evidence chain fully populated with real run IDs/URLs/commit SHA/checksums.
- B) New evidence files exist, but walkthroughs may still have partial placeholders.
- C) Only status alignment (downgrade "Done"); evidence generation deferred.
 > Recommendation: A. This WF exists to close evidence debt, not re-label it. Placeholders are the core defect; success must be binary and auditable.
 > **Selected: A**

**Q2: What is the required durability bar for WF-0056 evidence?**
- A) In-repo evidence bundle (`docs/walkthroughs/evidence/WF-0056/`) + checksums, and the walkthrough links to the live Actions run + artifact identifiers/links.
- B) Actions artifacts only (links/IDs), no in-repo copies.
- C) In-repo only, no Actions linkage required.
 > Recommendation: A. In-repo + checksums is durable; Actions linkage provides immutable run attribution. Either alone is weaker.
 > **Selected: A**

**Q3: What is the acceptable outcome for WF-0040 within WF-0057?**
- A) Backfill with real staging/prod observation evidence and counts OR explicitly re-waive with updated constraints and owner sign-off.
- B) Only document a plan; no change to WF-0040 artifacts/status.
- C) Reopen WF-0040 as active work instead of backfilling it here.
 > Recommendation: A. Closure truth requires either real evidence or an explicit, current waiver with constraints and sign-off. A plan-only output preserves the existing risk.
 > **Selected: A**

**Q4: How strict should we be about "Done" semantics repo-wide after this WF?**
- A) Establish an explicit rule: no Done status if any required evidence field is placeholder/waived without a recorded waiver.
- B) Only fix WF-0056 and WF-0040; no general rule.
- C) Add advisory language only.
 > Recommendation: A. Without an explicit rule, this failure mode will recur. The rule can be lightweight but must be concrete.
 > **Selected: A**

**Q5: What is the "good enough" boundary to exit Phase 0 and proceed to Phase 1 planning?**
- A) Unambiguous acceptance checklist for WF-0056 and WF-0040, including exact required fields/locations/access needs.
- B) High-level intent only; details can be figured out in Phase 2.
- C) Must run the live evidence now during Phase 0.
 > Recommendation: A. Phase 0 should de-risk by making the acceptance conditions falsifiable and checklist-driven, without forcing execution in Phase 0.
 > **Selected: A**

---

## Section 3 — Target User / Actor

**Brainstorming Q&A:**

**Q1: Primary actor for this workflow?**
- A) Repo owner/operator (admin) running live verify/apply/rollback and capturing evidence.
- B) Any contributor via CI only (no admin actions).
- C) External auditor only (no operator actions).
 > Recommendation: A. Live apply/rollback and evidence capture typically require elevated permissions and deliberate operator action.
 > **Selected: A**

**Q2: Secondary actor we optimize auditability for?**
- A) Maintainer verifying "Done" claims from docs only (no tribal knowledge).
- B) Product user (end user of app).
- C) Vendor/compliance team outside the repo.
 > Recommendation: A. The defect is internal governance traceability, so audit-by-docs is the right secondary actor.
 > **Selected: A**

**Q3: Where should the operator primarily run the "live" rehearsal?**
- A) GitHub Actions-backed runs (preferred for immutable run URLs/IDs).
- B) Local-only CLI runs.
- C) A mix, without a preference.
 > Recommendation: A. Matches the "live evidence" attribution requirement and reduces ambiguity about provenance.
 > **Selected: A**

**Q4: What is the expected operator workflow style?**
- A) Checklist-driven runbook with copy-pasteable commands and exact evidence locations.
- B) Ad-hoc/manual steps as long as outcomes exist.
- C) Fully automated, no operator involvement.
 > Recommendation: A. Evidence debt is mainly process drift; a checklist reduces future drift.
 > **Selected: A**

**Q5: What should be easiest to validate after the fact?**
- A) Evidence chain completeness (links + IDs + checksums) for verify/apply/rollback.
- B) The internal implementation details of how evidence was generated.
- C) Only the final "Done" label.
 > Recommendation: A. The goal is defensible proof, not code archaeology.
 > **Selected: A**

---

## Section 4 — Rough Idea Exploration

**Brainstorming Q&A:**

**Q1: What is the simplest WF-0056 closure strategy?**
- A) Run live verify/apply/rollback and then replace placeholders with real values in the walkthrough.
- B) Keep placeholders but add more explanation.
- C) Archive WF-0056 and restart as a new WF.
 > Recommendation: A. The intended evidence contract already exists; we need real runs and real identifiers.
 > **Selected: A**

**Q2: How do we handle WF-0056 status while placeholders exist?**
- A) Temporarily downgrade to non-Done until evidence is real.
- B) Leave as Done to avoid churn.
- C) Remove status entirely.
 > Recommendation: A. Avoids misleading closure claims; churn is the point when the label is wrong.
 > **Selected: A**

**Q3: What is the WF-0040 closure strategy inside WF-0057?**
- A) Backfill observation/count evidence from real telemetry if available; otherwise record an updated explicit waiver + sign-off.
- B) Treat it as out of scope.
- C) Re-run only local health scripts.
 > Recommendation: A. This WF is explicitly promoted from P1 #10; we should close that debt or explicitly re-waive with updated constraints.
 > **Selected: A**

**Q4: Where should the new "runtime observation + counts" evidence live?**
- A) In the WF-0040 walkthrough (as the checklist SSOT) with links to source evidence.
- B) Only in a new WF-0057 walkthrough.
- C) Only in chat.
 > Recommendation: A. WF-0040 walkthrough is the existing gate/checklist SSOT; keep the truth there.
 > **Selected: A**

**Q5: Evidence format preference for backfills?**
- A) Minimal structured record (table/checklist + links + date range + counts) that is auditable.
- B) Free-form narrative.
- C) Screenshots only.
 > Recommendation: A. Structured evidence is harder to misread and easier to audit.
 > **Selected: A**

---

## Section 5 — Constraints

**Brainstorming Q&A:**

**Q1: Scope guard for this WF?**
- A) No new governance hardening scope; only closure evidence and status alignment.
- B) Bundle one additional governance improvement since we're here.
- C) Leave scope open.
 > Recommendation: A. Evidence debt is already the bottleneck; bundling new work risks never closing.
 > **Selected: A**

**Q2: Evidence retention assumption?**
- A) Workflow artifacts may expire; in-repo evidence bundle + checksums is required for durability.
- B) Workflow artifacts are permanent; no need for in-repo copies.
- C) No durability requirement.
 > Recommendation: A. Artifact retention varies; durable in-repo evidence prevents future rot.
 > **Selected: A**

**Q3: What happens if we lack permissions/access to generate live evidence?**
- A) Treat as explicit blocker; align statuses to non-Done and document access requirements.
- B) Create simulated evidence and proceed.
- C) Ignore and keep status as Done.
 > Recommendation: A. Simulated evidence would recreate the fake-done problem; explicit blockers preserve truth.
 > **Selected: A**

**Q4: Allowed changes to enforcement code?**
- A) Only changes strictly required to produce evidence as already designed; otherwise defer.
- B) Any refactor allowed if it helps.
- C) No code changes allowed at all.
 > Recommendation: A. Preserve scope while not forbidding minimal wiring needed for evidence generation.
 > **Selected: A**

**Q5: Preferred status taxonomy during remediation?**
- A) Use explicit non-Done statuses (e.g., Phase 3 (Gate Pending) or similar) rather than leaving "Done" with caveats.
- B) Keep "Done" but add footnotes.
- C) Remove status tracking.
 > Recommendation: A. Status should be machine-readable and honest; footnotes tend to get ignored.
 > **Selected: A**

---

## Section 6 — Risks / Unknowns

**Brainstorming Q&A:**

**Q1: Biggest risk to closure?**
- A) Missing permissions/access (Actions, admin tokens, telemetry).
- B) Complexity of implementation.
- C) UI changes.
 > Recommendation: A. This is primarily an ops/access and evidence provenance issue.
 > **Selected: A**

**Q2: What is the most likely failure mode?**
- A) Evidence still ends up non-durable (artifact expires, no in-repo checksums).
- B) Performance regression.
- C) Style drift in docs.
 > Recommendation: A. Without durability, the same gap can reappear even after doing the run once.
 > **Selected: A**

**Q3: What is the highest-risk ambiguity we must eliminate?**
- A) "What counts as live evidence" and the required fields/links.
- B) Which linter to use.
- C) Which UI theme to pick.
 > Recommendation: A. The workflow fails if "live" is undefined or permissive.
 > **Selected: A**

**Q4: What is the risk of touching `docs/index.md` statuses?**
- A) Short-term churn/confusion.
- B) Long-term trust loss if we do not.
- C) No risk either way.
 > Recommendation: A (and accept it). Short-term churn is acceptable; long-term trust loss is worse if we keep incorrect Done labels.
 > **Selected: A**

**Q5: What is the mitigation strategy for uncertainty?**
- A) Write explicit acceptance checklists + preflight access checks in Phase 1 planning.
- B) Start coding immediately.
- C) Defer decisions.
 > Recommendation: A. This keeps Phase 0 about clarity and prevents wasted implementation.
 > **Selected: A**

---

## Section 7 — MVP Definition

**Brainstorming Q&A:**

**Q1: MVP sequencing?**
- A) Fix WF-0056 placeholders first, then address WF-0040 backfill.
- B) Do WF-0040 first.
- C) Do both without ordering.
 > Recommendation: A. WF-0056 is an internal contradiction while labeled Done; fix it first to restore trust.
 > **Selected: A**

**Q2: MVP deliverable for WF-0056?**
- A) Walkthrough evidence chain fully populated with real values + evidence bundle checksums present.
- B) Only one of verify/apply/rollback fully evidenced.
- C) Only narrative proof.
 > Recommendation: A. Partial evidence leaves the same closure gap.
 > **Selected: A**

**Q3: MVP deliverable for WF-0040?**
- A) Real telemetry evidence or explicit updated re-waive with sign-off; checklist updated accordingly.
- B) Only local replays.
- C) No change.
 > Recommendation: A. This is the promoted evidence debt item.
 > **Selected: A**

**Q4: MVP deliverable for status semantics?**
- A) Ensure `docs/index.md` does not show Done while placeholders/waived gates exist without explicit waiver.
- B) Leave statuses unchanged.
- C) Remove registry.
 > Recommendation: A. Status truth is part of the closure objective.
 > **Selected: A**

**Q5: MVP timebox posture if blocked by access?**
- A) Document blockers and downgrade statuses; do not fabricate evidence.
- B) Fabricate evidence to meet the deadline.
- C) Stop all progress.
 > Recommendation: A. Keeps forward motion without compromising truth.
 > **Selected: A**

---

## Section 8 — Explicit Non-Goals

**Brainstorming Q&A:**

**Q1: Are we expanding governance scope in this WF?**
- A) No; closure evidence only.
- B) Yes; add one extra enforcement feature.
- C) Unclear.
 > Recommendation: A. Prevents scope creep.
 > **Selected: A**

**Q2: Are we refactoring unrelated systems?**
- A) No; only changes strictly required to generate/record evidence.
- B) Yes; refactor for cleanliness while here.
- C) Depends.
 > Recommendation: A. Refactors increase risk and delay closure.
 > **Selected: A**

**Q3: Are we allowed to accept simulated evidence as "live"?**
- A) No; simulated evidence must be explicitly labeled non-live and cannot close WF-0056.
- B) Yes; any evidence is fine.
- C) Only for verify.
 > Recommendation: A. Matches the WF-0056 stub evidence policy and the purpose of this WF.
 > **Selected: A**

**Q4: Are we changing product behavior?**
- A) No; this is ops evidence and docs/status alignment work.
- B) Yes; adjust review pipeline behavior.
- C) Maybe.
 > Recommendation: A. Keeps the initiative scoped.
 > **Selected: A**

**Q5: Are we committing to new infra/tooling adoption?**
- A) No; reuse existing workflow surfaces and repo evidence conventions.
- B) Yes; adopt a new monitoring tool in this WF.
- C) Undecided.
 > Recommendation: A. Infrastructure changes are unrelated to the closure defect.
 > **Selected: A**
