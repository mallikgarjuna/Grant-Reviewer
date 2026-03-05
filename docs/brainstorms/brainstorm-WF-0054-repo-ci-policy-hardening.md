# WF-0054 — Repo-side CI Policy Hardening

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-05

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.

---

## Repo Reality Snapshot (Read-Only) (2026-03-05)

- CI is centralized in `.github/workflows/ci.yml` and triggers on `pull_request` and `push` (to `main`).
- PR-dependent governance steps are currently gated to `pull_request` (`Contract Boundary Governance Check`, `WF-0053 Negative Smoke`).
- Some checks run on both events (example: `pytest ... -m contract_gate --strict-markers`).
- Governance script exists: `scripts/check_contract_boundary_governance.py` (invoked from CI).
- WF-0047 artifact “status” appears inconsistent: WF row is `Done` and walkthrough is `Completed`, but task header still says `Ready for Implementation` despite being under `docs/tasks/completed/`.

Open questions this suggests:
- Do we want any governance subset to run on `push` in a push-safe way, or keep PR-only?
- What is the MVP definition of “deterministic CI-policy tests” (YAML-policy assertions vs script-level invariants vs both)?

---

## 1. Problem Statement

We need repo-side CI policy hardening so governance behavior is deterministic and correctly event-scoped (`pull_request` vs `push`), without relying on GitHub branch protection admin settings. Today, policy enforcement can be inconsistent or confusing across events, and PR-dependent governance can fail for the wrong reasons if executed in non-PR contexts.

This initiative is explicitly repo-only. It must also include cleanup for WF artifact status consistency (WF-0047 task/walkthrough/index alignment) so policy checks and human operators don’t depend on contradictory “status” signals.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 1)

Contract Notes / Non-obvious constraints:
- Governance that depends on PR evidence/artifacts is **PR-scoped** by contract; it must not block `main` via post-merge `push` execution. (Q&A Section 1)
- “Deterministic CI-policy tests” must explicitly assert **event-scoped behavior** (`pull_request` vs `push`), not just unit behavior of helpers. (Q&A Section 1)

---

## 2. Desired Outcome

After this exists:
- CI policy is explicit about what runs on `pull_request` vs `push`, and why.
- We have deterministic tests that fail when event-scoping or governance gating regresses.
- WF-0047 status representation is consistent across task/walkthrough/index so humans and automation converge on one reality.
- We have a clean handoff boundary for a future workflow that enforces GitHub branch protection settings (out of scope here).

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 2)

Contract Notes / Non-obvious constraints:
- This WF must remain **repo-only**; no GitHub admin/branch protection changes. (Q&A Section 2)
- Handoff to the branch-protection WF must be explicit (what remains, what assumptions). (Q&A Section 2)

---

## 3. Target User / Actor

Primary actor: maintainers (and agents acting as maintainers) who merge PRs and must rely on CI governance signals being correct, deterministic, and non-deadlocking.

Secondary actor: contributors opening PRs who need early, predictable governance feedback.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 3)

---

## 4. Rough Idea (Unstructured Thinking)

High-level approach:
- Define a small, explicit “CI policy contract” for event scoping and governance gating (what is PR-only, what is push-safe).
- Add deterministic policy tests that validate this contract (including negative cases) so drift is caught early.
- Clean up WF-0047 artifact status consistency (task/walkthrough/index alignment) as an intentional hygiene step tied to governance clarity.
- Produce a short handoff note for the follow-on WF that enforces branch protection settings (mapping checks to settings), without changing those settings here.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 4)

Contract Notes / Non-obvious constraints:
- Prefer policy validation that is **deterministic and repo-native** (no external GitHub admin dependencies). (Q&A Section 4)

### CI Policy Contract (Event Scoping Invariants) (Draft)

Definitions:
- **PR-dependent governance**: any CI step that depends on PR context or PR-scoped evidence/artifacts to make a correct decision.
- **Push-safe checks**: CI steps that can run deterministically on `push` to `main` without PR context or PR-only evidence.

Invariants (must be enforced by deterministic tests):
- PR-dependent governance must run on `pull_request` only, and must be explicitly excluded from `push` to `main` execution paths.
  - Example (today): the governance checker invocation and “negative smoke” are PR-dependent.
- `push` to `main` must remain push-safe: it must not require PR-only evidence bundles and must not deadlock `main`.
  - Push CI can still run push-safe checks (lint, typecheck, unit tests, contract gates) that do not require PR context.

Deterministic CI-policy tests (contract):
- Add deterministic tests that assert these invariants for `.github/workflows/ci.yml`, specifically covering `pull_request` vs `push` behavior.
- Include at least one negative/regression case that fails if a PR-dependent governance step would execute on `push`.

---

## 5. Constraints

- Repo-only: no GitHub branch protection admin changes.
- Determinism: tests must be stable and event-scoped.
- Minimal disruption: changes should preserve existing workflow intent and not introduce flaky CI.
- Cleanup requirement: WF-0047 task/walkthrough/index alignment is in-scope as repo hygiene tied to governance clarity.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 5)

---

## 6. Risks / Unknowns

- “Deterministic CI-policy tests” could be interpreted too narrowly (only YAML shape) or too broadly (end-to-end GitHub simulation).
- Risk of overfitting to current CI layout if policy tests assert incidental structure rather than intent.
- Risk of false positives if governance rules are coupled to docs “status” fields that drift.
- Risk that push-safe governance subset is desired later; we must keep room for future extension without rework.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 6)

Open Questions / Deferred:
- Decide in Phase 1 whether any governance subset should run on `push` (push-safe) or remain strictly PR-only.
- Define the exact “policy contract” format (doc-only vs machine-checked spec) in Phase 1.

---

## 7. MVP Definition

If we had to ship in ~3 days:
- A clear CI policy contract for event scoping and governance gating, tied to this repo’s workflows.
- Deterministic tests that enforce the policy contract for `pull_request` vs `push` (including at least one negative/regression case).
- WF-0047 artifact status consistency cleanup (task/walkthrough/index alignment).
- A handoff note that prepares a separate WF for GitHub branch protection enforcement (mapping desired settings/checks), without implementing those settings here.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 7)

### WF-0047 Artifact Status Consistency (Explicit Cleanup Contract)

Target: WF-0047 only (do not generalize to historical WFs in this initiative).

Contract:
- Make WF-0047 “done-ness” consistent across:
  - `docs/index.md` WF row status
  - task artifact header status
  - walkthrough artifact header status
- The outcome should eliminate the specific inconsistency where WF-0047 is “Done/Completed” in index/walkthrough but “Ready for Implementation” in the task artifact header.

### Branch Protection Enforcement Handoff (Explicit Contract)

This WF must prepare a clean handoff to a follow-on WF that enforces GitHub branch protection settings (out of scope here).

Contract:
- Produce an explicit mapping of “checks we rely on for governance” to “checks that should become required in branch protection”, including event-scope notes.
- Do not implement or change GitHub branch protection settings in this WF.

---

## 8. Explicit Non-Goals

- Changing GitHub branch protection rules, required status checks, or repo admin settings (explicit follow-on WF).
- Broad CI refactors unrelated to governance event-scoping determinism.
- Building a generalized “CI policy framework” intended for reuse across many repos.
- Introducing new product/application behavior unrelated to CI governance.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0054-repo-ci-policy-hardening.md` (Section 8)
