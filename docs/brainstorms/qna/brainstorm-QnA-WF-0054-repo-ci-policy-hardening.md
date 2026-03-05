# WF-0054 — Repo-side CI Policy Hardening

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-05

This transcript records the interactive brainstorm decisions and rationale.
The SSOT for contracts/decisions is: `docs/brainstorms/brainstorm-WF-0054-repo-ci-policy-hardening.md`.

---

## Section 1 — Problem Statement

**Brainstorming Q&A:**

**Q1: What is the primary repo-side CI policy gap we’re solving?**
- A) Event-scope correctness: PR-dependent governance must run only on `pull_request`; `push` must not deadlock or mis-evaluate PR-only evidence.
- B) Enforcement strength: governance should also run on `push` to `main` in a push-safe mode, independent of PR metadata.
- C) Both A and B equally (we accept extra complexity to get dual-event enforcement).
 > Recommendation: A. It is the highest-leverage, lowest-risk contract: align governance to the event context it depends on, preventing deadlocks/false failures on `push`. B can be added later as a push-safe subset once clearly defined; C risks scope creep early.
 > **Selected: A** (user: “Go with your recommendations for rest of the Phase 0 run”)

**Q2: Who is the primary actor we’re protecting (who experiences the pain)?**
- A) Repo maintainers merging PRs (avoid deadlocks, missing/incorrect governance, inconsistent enforcement).
- B) Contributors/agents opening PRs (clear, early feedback; deterministic failures).
- C) Both equally.
 > Recommendation: A. Maintainers feel the highest cost when CI policy behaves incorrectly on merge paths; contributors benefit as a downstream effect.
 > **Selected: A**

**Q3: What failure is most important to prevent deterministically?**
- A) PR-dependent governance running on `push` and failing for the wrong reasons (missing PR-only evidence), potentially blocking `main`.
- B) Governance not running on PRs when it should (bypass).
- C) Flaky/ambiguous governance outcomes (non-determinism/noise).
 > Recommendation: A. It is the most operationally dangerous failure mode and is directly addressed by event-scope hardening.
 > **Selected: A**

**Q4: What should “deterministic CI-policy tests” cover (minimum acceptable MVP)?**
- A) Tests that assert event-scoped governance behavior (`pull_request` vs `push`) at the workflow policy level (what must run vs must not run), plus a small number of script-level invariants if needed.
- B) Only workflow YAML structural assertions (fast, strict, repo-only).
- C) Only script-level tests (treat workflow YAML as configuration; don’t assert it directly).
 > Recommendation: A. It directly targets the regression risk (event scope), while allowing tight, deterministic checks without requiring full GitHub simulation.
 > **Selected: A**

**Q5: What is the WF-0047 cleanup requirement’s core intent for this initiative?**
- A) Make WF artifacts’ status semantics consistent across task/walkthrough/index so policy/governance never depends on contradictory status metadata.
- B) Purely a documentation tidy-up (no relation to governance behavior), but required for repo hygiene.
- C) Only fix the specific WF-0047 task/walkthrough/index mismatch; don’t generalize.
 > Recommendation: A. Inconsistent status signals create human and automation drift; this should be treated as a governance-adjacent correctness issue, not cosmetic.
 > **Selected: A**

---

## Section 2 — Desired Outcome

**Brainstorming Q&A:**

**Q1: What is the clearest success criterion for this WF (repo-only)?**
- A) CI policy contracts are explicit and enforced by deterministic tests; drift in event scoping is caught automatically.
- B) CI is “cleaner” (less YAML complexity), even if scoping remains informal.
- C) Governance becomes stricter (more checks) regardless of event scoping.
 > Recommendation: A. It matches the problem statement: correctness and determinism first, not aesthetics or blanket strictness.
 > **Selected: A**

**Q2: What is the desired event-scoping contract for PR-dependent governance?**
- A) PR-dependent governance runs only on `pull_request` (or PR-scoped events) and is explicitly excluded from `push`.
- B) PR-dependent governance runs on both `pull_request` and `push`, but with a “best effort” mode on `push`.
- C) PR-dependent governance runs only on `push` to `main` post-merge to ensure final state.
 > Recommendation: A. It is deterministic and avoids the “missing PR context” class of failures; push-safety can be added later as an explicit subset.
 > **Selected: A**

**Q3: What should the WF-0047 cleanup deliver (minimum)?**
- A) Align WF-0047 task/walkthrough/index status semantics to a single consistent state and document the convention.
- B) Only adjust `docs/index.md` row; leave artifacts as-is.
- C) Only adjust the task header; avoid touching index.
 > Recommendation: A. Partial fixes increase ambiguity; we want a single consistent signal.
 > **Selected: A**

**Q4: What should “handoff to branch protection enforcement WF” look like?**
- A) A short explicit note enumerating which checks should become required branch protections and why, without implementing them here.
- B) A full branch protection configuration file ready to be applied (even if not applied).
- C) No handoff; keep it implicit.
 > Recommendation: A. It keeps this WF repo-only while still enabling a clean follow-on initiative.
 > **Selected: A**

**Q5: How should we treat existing governance behavior (don’t break intent)?**
- A) Preserve intent; make scoping explicit and tests enforce the intended behavior.
- B) Revisit and redesign governance requirements from scratch.
- C) Freeze governance logic entirely; only add tests.
 > Recommendation: A. This is hardening, not redesign; we reduce ambiguity and drift.
 > **Selected: A**

---

## Section 3 — Target User / Actor

**Brainstorming Q&A:**

**Q1: Who is the primary actor for this initiative?**
- A) Maintainers/owners merging PRs and interpreting CI governance.
- B) External contributors.
- C) End users of the app.
 > Recommendation: A. They rely on correct CI signals to ship changes safely.
 > **Selected: A**

**Q2: Who is the secondary actor?**
- A) Contributors/agents opening PRs who need early deterministic feedback.
- B) Runtime operators responding to incidents.
- C) None; only maintainers matter.
 > Recommendation: A. PR authors are the first to see governance failures; determinism reduces iteration cost.
 > **Selected: A**

**Q3: When should governance feedback surface (timing)?**
- A) On PR creation/update (`pull_request`) as early as possible.
- B) Only after merge (`push` to `main`) to validate final state.
- C) Only on manual dispatch.
 > Recommendation: A. It supports fast iteration and avoids blocking `main` due to PR-context coupling.
 > **Selected: A**

**Q4: What should be the primary “consumer interface” for the policy contract?**
- A) CI behavior + deterministic tests (and a short human-readable policy statement).
- B) Only docs; tests are optional.
- C) Only tests; docs are optional.
 > Recommendation: A. Both humans and automation should agree; docs alone drift, tests alone are opaque.
 > **Selected: A**

**Q5: How do we prevent policy drift over time?**
- A) Codify invariants as tests that fail on drift (plus minimal docs).
- B) Rely on reviewer vigilance.
- C) Periodic manual audits only.
 > Recommendation: A. Deterministic tests are the point of hardening.
 > **Selected: A**

---

## Section 4 — Rough Idea Exploration

**Brainstorming Q&A:**

**Q1: What is the core “policy contract” we want to codify?**
- A) A small set of invariants about event scope (what must run on PR vs must not run on push) and governance gating.
- B) A full matrix enumerating every job/step across all events and branches.
- C) Only “required checks” naming; ignore event scope.
 > Recommendation: A. Invariants are stable and high-signal; a full matrix is brittle.
 > **Selected: A**

**Q2: What should the deterministic policy tests assert at minimum?**
- A) Intent-level assertions (e.g., “PR-dependent governance steps are gated to `pull_request`”), plus one negative regression test.
- B) Exact YAML structure/line-by-line snapshots.
- C) Only runtime behavior via end-to-end GitHub event simulation.
 > Recommendation: A. It is deterministic and avoids brittle snapshot coupling.
 > **Selected: A**

**Q3: How should WF-0047 cleanup be treated relative to CI policy?**
- A) As part of governance clarity hygiene: statuses must not contradict each other.
- B) As unrelated; exclude it.
- C) As a separate refactor effort across many WFs.
 > Recommendation: A. It is explicitly in scope for this WF and ties to policy clarity.
 > **Selected: A**

**Q4: How should we prepare the follow-on branch protection WF (without doing it)?**
- A) Identify which checks should be required and what branch scope, and note any missing pieces that prevent enforcement today.
- B) Implement branch protection changes in code anyway.
- C) Leave it for later with no note.
 > Recommendation: A. It creates a clean handoff without violating repo-only constraints.
 > **Selected: A**

**Q5: How strict should we be about push behavior on `main` in this WF?**
- A) Define what is push-safe and ensure PR-dependent governance does not run on push; defer push-safe governance expansion decisions.
- B) Enforce the same governance on push and PR immediately.
- C) Disable push CI entirely.
 > Recommendation: A. It matches repo reality and reduces risk of deadlocks while preserving room for future hardening.
 > **Selected: A**

---

## Section 5 — Constraints

**Brainstorming Q&A:**

**Q1: What is the hard boundary on GitHub admin settings?**
- A) No branch protection / required checks / admin setting changes in this WF.
- B) Allow minor branch protection tweaks if needed.
- C) Decide later.
 > Recommendation: A. It is an explicit scope constraint.
 > **Selected: A**

**Q2: What is the determinism requirement for policy tests?**
- A) Fully deterministic (no network, no timing/race dependence).
- B) “Mostly deterministic” is fine.
- C) End-to-end GitHub-driven tests only.
 > Recommendation: A. Otherwise policy hardening becomes flaky and untrustworthy.
 > **Selected: A**

**Q3: How should policy tests relate to CI runtime duration?**
- A) Keep them fast (seconds) and runnable locally in CI context.
- B) Slow is acceptable if comprehensive.
- C) Only run them nightly.
 > Recommendation: A. They should guard merge-time behavior.
 > **Selected: A**

**Q4: How should we handle future CI workflow evolution?**
- A) Tests should assert invariants, not incidental structure, to avoid churn.
- B) Tests can be tightly coupled; update them often.
- C) Avoid tests to reduce maintenance.
 > Recommendation: A. Hardening should reduce churn, not amplify it.
 > **Selected: A**

**Q5: What is the minimum acceptable scope for WF-0047 alignment?**
- A) Align status semantics across task/walkthrough/index for WF-0047, and clarify the convention so it can’t regress.
- B) Only update one file.
- C) Expand to all historical WFs.
 > Recommendation: A. Targeted and concrete.
 > **Selected: A**

---

## Section 6 — Risks / Unknowns

**Brainstorming Q&A:**

**Q1: What assumption is most fragile?**
- A) That “policy invariants” can be expressed in stable, non-brittle tests against our workflows/scripts.
- B) That maintainers will never bypass CI.
- C) That GitHub events won’t change.
 > Recommendation: A. If we get this wrong, we’ll create brittle tests or miss true regressions.
 > **Selected: A**

**Q2: What must be validated early to avoid rework?**
- A) What exactly counts as “PR-dependent governance” vs “push-safe” checks in this repo.
- B) Whether we should move to a different CI provider.
- C) Whether Python or Node should own CI logic.
 > Recommendation: A. It directly affects scoping contracts and tests.
 > **Selected: A**

**Q3: What could cause the most rework?**
- A) Over-coupling tests to YAML layout/structure and then refactoring CI.
- B) Adding too many new checks.
- C) Changing the coding style.
 > Recommendation: A. It’s a classic drift trap.
 > **Selected: A**

**Q4: What is a major operational risk to guard against?**
- A) Deadlocking `main` via push-only enforcement that requires PR-only evidence.
- B) Missing a lint issue.
- C) Frontend build slowness.
 > Recommendation: A. It is the core failure mode described by the initiative.
 > **Selected: A**

**Q5: What governance-docs drift risk exists?**
- A) WF status semantics drift across artifacts; future checks might read the wrong signal or humans misinterpret readiness.
- B) PRD format drift.
- C) Code comments drift.
 > Recommendation: A. This is why WF-0047 alignment is in-scope.
 > **Selected: A**

---

## Section 7 — MVP Definition

**Brainstorming Q&A:**

**Q1: If limited to ~3 days, what must exist?**
- A) Explicit event-scoping policy contract + deterministic tests enforcing it + WF-0047 alignment + handoff note for branch protections.
- B) Only docs updates.
- C) Only CI YAML refactor.
 > Recommendation: A. It is the smallest “hardening” that actually prevents regression and cleans up the known inconsistency.
 > **Selected: A**

**Q2: What can explicitly wait?**
- A) Any expansion to push-safe governance beyond the current PR-scoped model; branch protection enforcement itself.
- B) All tests.
- C) All docs.
 > Recommendation: A. Keep the MVP tight and aligned to constraints.
 > **Selected: A**

**Q3: What must NOT be included?**
- A) Applying GitHub branch protection settings (separate WF).
- B) Refactoring unrelated CI jobs.
- C) Both A and B.
 > Recommendation: C. Both are scope traps; focus on governance event scoping + tests + WF-0047 alignment.
 > **Selected: C**

**Q4: What is the minimum negative/regression case the tests must cover?**
- A) A test that fails if a PR-dependent governance step is not gated to `pull_request` (or equivalently, would run on `push`).
- B) A test that checks YAML formatting.
- C) A test that depends on GitHub API calls.
 > Recommendation: A. It directly enforces the core policy.
 > **Selected: A**

**Q5: What is the minimum “handoff artifact” content?**
- A) A list of checks that should become required in branch protection, plus event scope and rationale.
- B) A full operational runbook.
- C) Nothing.
 > Recommendation: A. Concrete enough for a follow-on WF without expanding scope.
 > **Selected: A**

---

## Section 8 — Explicit Non-Goals

**Brainstorming Q&A:**

**Q1: What belongs to a future WF (explicitly)?**
- A) GitHub branch protection enforcement/configuration.
- B) Rewriting the entire CI pipeline.
- C) Frontend performance refactors.
 > Recommendation: A. It is explicitly out of scope and should be a follow-on WF.
 > **Selected: A**

**Q2: What tempting governance enhancement must be postponed?**
- A) Adding new governance rules unrelated to event scoping/determinism (scope creep).
- B) Removing existing governance checks.
- C) Expanding to multi-repo governance.
 > Recommendation: A. Hardening means clarifying and enforcing intent, not adding new policies.
 > **Selected: A**

**Q3: What policy direction should we avoid in this WF?**
- A) A generalized “policy framework” intended for reuse across many repos.
- B) Simple invariant-based tests.
- C) Status alignment cleanup.
 > Recommendation: A. Over-generalization is high-risk and not required for the stated problem.
 > **Selected: A**

**Q4: What should we avoid coupling to?**
- A) Incidental `.github/workflows/ci.yml` layout details that change frequently.
- B) Intent-level invariants.
- C) Repo-only constraints.
 > Recommendation: A. Coupling to layout creates churn and brittle tests.
 > **Selected: A**

**Q5: What must we explicitly NOT promise here?**
- A) That `main` is protected by GitHub-required checks (admin settings).
- B) That tests exist.
- C) That statuses are consistent.
 > Recommendation: A. Repo-only means we cannot promise branch-protection enforcement in this WF.
 > **Selected: A**
