# WF-0055 — Platform Policy Enforcement

Artifact: brainstorm-qna
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-05

This transcript records the interactive brainstorm decisions and rationale.
The SSOT for contracts/decisions is: `docs/brainstorms/brainstorm-WF-0055-platform-policy-enforcement.md`.

---

Note: User instruction on 2026-03-05: “Go with your recommendations for rest of the Phase 0 run.”

### Addendum (Phase 0.3 risk-audit application)

- The Phase 0.1 recommendation for required checks was “require current job contexts (`backend`, `frontend`)”.
- The WF-0055 request explicitly requires six distinct required checks (backend/frontend sub-checks). Because GitHub required status checks operate on check-run contexts, WF-0055 will reshape CI so those six checks exist as separate job check contexts and can be required on `main`.

### Addendum (Adversarial pass application, v0.3)

- Policy mechanism contract: prefer repository rulesets targeting `main`, fall back to classic branch protection if rulesets are unavailable/forbidden.
- Enforcement toggles are now explicitly contracted as a minimal toggle-value matrix to eliminate ambiguity (still aligned to the “minimal toggles” intent).

## Section 1 — Problem Statement

**Brainstorming Q&A:**

**Q1: What is the primary problem we’re solving with WF-0055?**
- A) `main` can be updated/merged without the intended CI gates being required (policy bypass risk).
- B) The required-check set exists but drifts from repo intent (drift detection gap).
- C) Both equally (we accept extra scope to do enforcement + drift detection + runbook/evidence).
 > Recommendation: A. Without enforced required checks on `main`, CI policy is advisory and can be bypassed. B is still important, but drift detection is only meaningful once there is a clear enforced baseline.
 > **Selected: A** (pre-authorized)

**Q2: What’s the hard constraint on repo visibility/plan (given branch protection/rulesets API is currently 403)?**
- A) Repo stays private; upgrading plan/org settings to enable branch protection is acceptable.
- B) Repo stays private; no plan upgrades allowed, so we need an alternative enforcement mechanism (likely weaker than branch protection).
- C) Repo can be made public to enable branch protection features.
 > Recommendation: A. Branch protection is the intended enforcement mechanism; if it is plan-gated today, the cleanest solution is to enable it (via plan/org setting) rather than inventing a weaker parallel control.
 > **Selected: A** (pre-authorized)

**Q3: What should be the “required checks” contract relative to current GitHub check contexts?**
- A) Require the actual current check runs: `backend` and `frontend` (and optionally `Vercel` if desired).
- B) Refactor CI so the six items listed in `ci.yml` become distinct check runs, then require those exact six.
- C) Hybrid: require `backend` + `frontend` now; plan a follow-up to split checks later.
 > Recommendation: A. GitHub required checks operate on check-run contexts, and the current observable contexts are job-level (`backend`, `frontend`). B can be justified if the policy must require sub-checks as separate contexts, but that is an explicit CI reshaping step.
 > **Selected: A** (pre-authorized)

**Q4: Which enforcement toggles are in-scope for WF-0055 (minimum)?**
- A) Required status checks + “include administrators” + block force-push/delete.
- B) Also require PR reviews (min approvals, code-owner review), stale review dismissal rules.
- C) Full hardline policy: reviews + linear history + signed commits + conversation resolution + merge restrictions.
 > Recommendation: A. It is the minimum set that turns CI into a non-bypassable merge gate for `main` while avoiding policy sprawl.
 > **Selected: A** (pre-authorized)

**Q5: What’s the most important evidence artifact property for admin enforcement?**
- A) Machine-verifiable JSON captured via `gh api` showing the live policy state + UTC timestamp + actor/tooling path.
- B) Human-verifiable screenshots in addition to JSON (belt-and-suspenders).
- C) CI-produced “verify-only” report (no mutation) plus a documented manual apply path.
 > Recommendation: A. The most robust evidence is the raw (or normalized) JSON policy fetched from the API, tied to a timestamp and an actor/tooling path. Screenshots are brittle; verify-only reports are useful, but still benefit from the underlying JSON evidence.
 > **Selected: A** (pre-authorized)

## Section 2 — Desired Outcome

**Brainstorming Q&A:**

**Q1: What is the clearest success criterion for this WF?**
- A) `main` branch policy is enforced in GitHub (required checks + core toggles) and is machine-verifiably evidenced in-repo.
- B) Drift detection exists, even if enforcement remains manual.
- C) A runbook exists, even if enforcement and drift detection are partial.
 > Recommendation: A. Enforcement plus evidence is the core deliverable; drift detection and runbook then become enforceable and durable.
 > **Selected: A** (pre-authorized)

**Q2: What does “drift detection” mean operationally?**
- A) Deterministic verify command compares live GitHub policy to an expected policy definition in-repo and fails on mismatch.
- B) Best-effort reporting only (never fails CI).
- C) Manual checklist in docs.
 > Recommendation: A. Drift detection must be deterministic to prevent silent policy erosion.
 > **Selected: A** (pre-authorized)

**Q3: How should we handle token/permission limitations in CI?**
- A) CI runs verify-only; apply is a controlled, documented admin path.
- B) CI mutates policy directly using a privileged token/actor.
- C) No CI involvement; only manual apply/verify.
 > Recommendation: A. This is the safest and most common permissions model; it avoids requiring escalated credentials in CI while still preventing drift.
 > **Selected: A** (pre-authorized)

**Q4: What is the “required checks” set for the enforcement baseline (given current contexts)?**
- A) Require `backend` and `frontend` on `main`.
- B) Require `backend`, `frontend`, and `Vercel`.
- C) Block on `backend` only.
 > Recommendation: A. It matches the current workflow’s two-job shape and avoids coupling to optional integrations unless explicitly desired.
 > **Selected: A** (pre-authorized)

**Q5: What should the evidence artifact include (minimum viable set)?**
- A) UTC timestamp, repo+branch, actor (login), tool path (gh version + command), normalized required checks list, toggles, and the raw live response payload.
- B) Only the normalized expected policy and a pass/fail.
- C) Only the raw live payload.
 > Recommendation: A. It’s both human-auditable and machine-verifiable, while remaining deterministic.
 > **Selected: A** (pre-authorized)

## Section 3 — Target User / Actor

**Brainstorming Q&A:**

**Q1: Who is the primary actor for WF-0055?**
- A) Maintainers/admins responsible for protecting `main` and setting GitHub policy.
- B) External contributors.
- C) CI automation only (no human owner).
 > Recommendation: A. This is a platform policy initiative; ownership must be explicit.
 > **Selected: A** (pre-authorized)

**Q2: Who is the secondary actor?**
- A) Contributors/agents opening PRs who need deterministic merge gates.
- B) Runtime operators responding to incidents.
- C) None.
 > Recommendation: A. PR authors need predictable gating and clear failure modes.
 > **Selected: A** (pre-authorized)

**Q3: When should policy verification run?**
- A) On every PR (verify-only) to prevent drift before merge.
- B) Only on push to `main`.
- C) Only on manual dispatch.
 > Recommendation: A. PR-time verification gives earlier feedback and prevents merges under drifted policy.
 > **Selected: A** (pre-authorized)

**Q4: What is the main “interface” for the enforcement contract?**
- A) A policy definition file + deterministic verify/apply scripts.
- B) Only GitHub UI settings (documented).
- C) Terraform-only, no scripts.
 > Recommendation: A. It balances automation with repo-traceability and supports both local admin apply and CI verify.
 > **Selected: A** (pre-authorized)

**Q5: What is the explicit “safety contract” for PR-only checks (WF-0054 intent)?**
- A) Required checks must not depend on PR-only metadata when evaluated on push-only contexts; PR-dependent governance remains PR-scoped.
- B) Require all governance checks on both PR and push to `main`.
- C) Disable PR-only checks.
 > Recommendation: A. This preserves WF-0054’s event-scope correctness intent and avoids deadlocking `main`.
 > **Selected: A** (pre-authorized)
