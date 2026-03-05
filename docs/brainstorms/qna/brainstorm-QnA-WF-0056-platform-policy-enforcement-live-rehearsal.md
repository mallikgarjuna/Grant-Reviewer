# WF-0056 — Platform Policy Enforcement Live Rehearsal

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-05

> Note: Per user instruction on 2026-03-05 ("Go with your recommendations for rest of the Phase 0 run"),
> selections below record the recommended option for each question.

---

## Section 1 - Problem Statement

**Q1: Who primarily experiences the risk/problem we are addressing?**
- A) Repo maintainers/releasers who need merges to `main` to be safely gated.
- B) Contributors who want clearer feedback when CI/policy blocks a PR.
- C) Compliance/governance owners who need auditability of platform settings.
  > Recommendation: A - The MVP is about enforceable merge governance; maintainers feel the pain first. B and C are downstream benefits.
  > Selected: A

**Q2: What is the core gap WF-0056 is solving (falsifiable)?**
- A) "WF-0055 is not yet proven on live GitHub settings for this repo with durable evidence artifacts."
- B) "GitHub Actions CI is missing jobs/steps and needs refactoring first."
- C) "We need to replace branch protection with rulesets everywhere."
  > Recommendation: A - This WF is about operational proof with evidence; CI refactors and mechanism migrations are separate unless they block proof.
  > Selected: A

**Q3: What does "live enforcement proven" mean for MVP?**
- A) Live verify on the real repo/branch produces evidence showing no drift vs `config/platform_policy/main_policy.yaml`.
- B) Apply/rollback rehearsal runs end-to-end once (with snapshots and evidence) without leaving persistent changes.
- C) Both A and B.
  > Recommendation: C - Verify alone is insufficient to prove we can recover from drift; apply/rollback without verify does not prove correctness.
  > Selected: C

**Q4: Where should the apply/rollback rehearsal happen (safety)?**
- A) On `main` protections directly.
- B) On a dedicated rehearsal branch (e.g. `policy-rehearsal`) first; verify still targets `main`.
- C) On a separate sandbox repo.
  > Recommendation: B - This minimizes risk to `main` while still proving the mutation/rollback path works.
  > Selected: B

**Q5: What is the expected evidence retention target for MVP?**
- A) Local evidence files referenced in the walkthrough (sha256 + paths), stored under `docs/walkthroughs/evidence/WF-0056/`.
- B) GitHub Actions run artifacts uploaded for verify/apply/rollback runs (preferred for durability), referenced from the walkthrough.
- C) Commit evidence JSON into the repo.
  > Recommendation: B - Workflow artifacts are durable without repo churn. Local evidence is acceptable fallback; committing evidence increases noise and review burden.
  > Selected: B

---

## Section 2 - Desired Outcome

**Q1: What is the acceptance criteria for the live verify outcome?**
- A) `verify` exits 0 and evidence records `drift.is_drifted=false` against expected policy.
- B) The verify GitHub Action is green on a PR and logs "no drift".
- C) Both A and B.
  > Recommendation: C - We want both the tool-level evidence and the CI signal; logs alone are not sufficient.
  > Selected: C

**Q2: What is the acceptance criteria for apply rehearsal?**
- A) Apply runs with explicit intent gating and writes: pre-snapshot, post-apply verify evidence, and a snapshot artifact for rollback.
- B) Apply only (no snapshot), trusting manual rollback.
- C) Do apply only if drift exists.
  > Recommendation: A - Snapshot-based rollback is the safety contract; rehearsal must exercise it.
  > Selected: A

**Q3: What is the acceptance criteria for rollback rehearsal?**
- A) Rollback restores from snapshot, and a post-rollback verify confirms no drift vs pre-snapshot (with evidence).
- B) Rollback runs without verifying the restored policy.
- C) Skip rollback if apply was a no-op.
  > Recommendation: A - Restoration without verification is not proof; no-op apply still benefits from snapshot/restore rehearsal.
  > Selected: A

**Q4: What should the walkthrough contain for "evidence artifacts"?**
- A) Exact commands run + paths/IDs of evidence + sha256 fields from evidence payloads.
- B) Screenshots only.
- C) Only narrative, no references.
  > Recommendation: A - Machine-verifiable evidence is the point of governance traceability.
  > Selected: A

**Q5: How should we define "done" for WF-0056 in docs/index.md status?**
- A) Phase 0 only (ideation done).
- B) Done after Phase 3 with walkthrough evidence references of live verify + apply/rollback rehearsal.
- C) Completed after CI verify is green once.
  > Recommendation: B - The request is about operational proof; CI green alone is insufficient.
  > Selected: B

---

## Section 3 - Target User / Actor

**Q1: Who is allowed to run apply/rollback?**
- A) Only a human admin maintainer with explicit intent.
- B) Any maintainer.
- C) CI.
  > Recommendation: A - Least privilege; CI should remain verify-only.
  > Selected: A

**Q2: Where should admin credentials live (if needed)?**
- A) A dedicated GitHub Actions secret with least privilege, used only for manual workflow_dispatch (not automatic).
- B) Personal PAT passed locally only.
- C) Both (local primary, optional workflow_dispatch later).
  > Recommendation: C - Local is simplest for rehearsal; workflow_dispatch is a good follow-on for repeatability if approved.
  > Selected: C

**Q3: What should be the primary user-facing surface?**
- A) CLI commands (`uv run python -m tools.gh_policy.cli ...`) + runbook.
- B) GitHub UI click paths only.
- C) A custom web UI.
  > Recommendation: A - Deterministic and auditable; aligns to WF-0055 runbook.
  > Selected: A

**Q4: What should CI do?**
- A) Run verify-only on PRs to `main`; fail closed on drift (policy mismatch).
- B) Only warn on drift.
- C) Apply fixes automatically.
  > Recommendation: A - Governance enforcement requires fail-closed semantics; auto-apply is too risky.
  > Selected: A

**Q5: What is the minimum set of repos/branches in scope for MVP?**
- A) Only `mallikgarjuna/Grant-Reviewer` on `main` (verify) + one rehearsal branch (apply/rollback).
- B) All repos in the org.
- C) Multiple branches per repo.
  > Recommendation: A - Keep scope tight; expand after one proven rehearsal.
  > Selected: A
