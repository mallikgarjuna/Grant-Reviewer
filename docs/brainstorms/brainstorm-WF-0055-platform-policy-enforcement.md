# WF-0055 — Platform Policy Enforcement

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-03-05

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0055-platform-policy-enforcement.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1–3 “Contract Notes / Non-obvious constraints” bullets and link to the relevant Q&A section header.

---

## Repo Reality Snapshot (Read-Only) (2026-03-05)

- `.github/workflows/ci.yml` runs on `pull_request` and on `push` to `main`.
- Current Actions check-run contexts observed on `main`: `backend`, `frontend` (not step-level names).
- Attempting to read branch protection or repo rulesets via GitHub REST API returned HTTP 403 with message: “Upgrade to GitHub Pro or make this repository public to enable this feature.”
- This implies branch protection/rulesets enforcement may be plan-gated (private repo + current plan), so WF-0055 must include a plan/permissions preflight and a read/verify fallback.
- Any “required checks” enforcement must target check-run contexts GitHub recognizes for required status checks (not YAML step names).

## 1. Problem Statement

What problem are we solving?

- Primary gap: `main` can potentially be updated/merged without the intended CI gates being required (policy bypass risk), and enforcement can drift from repo intent over time.
- This WF exists as a follow-on to WF-0054 (repo-only); WF-0055 is explicitly platform-facing (GitHub settings), with evidence and drift detection.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0055-platform-policy-enforcement.md` (Section 1)

Contract Notes / Non-obvious constraints (Section 1):

- “Required checks” must refer to GitHub status check contexts. Current observed contexts are job-level (`backend`, `frontend`); the step names listed in `ci.yml` are not currently enforceable as branch protection required checks without CI refactor.
- Branch protection/rulesets APIs can be disabled by plan for private repos; enforcement must detect and surface this deterministically (no silent partial application).
- Preserve WF-0054 event-scope intent: PR-context-coupled governance must not be required on push-only contexts in a way that can deadlock `main`.

## 2. Desired Outcome

What changes after this exists?

- `main` is protected in GitHub with a deterministic, auditable policy: required status checks are enforced for merges to `main`.
- We can generate machine-verifiable evidence (timestamp, repo, branch, tool/actor, required checks set, enforcement toggles) and store it in-repo.
- We can deterministically detect policy drift between the repo’s expected policy and the live GitHub policy.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0055-platform-policy-enforcement.md` (Section 2)

Contract Notes / Non-obvious constraints (Section 2):

- Enforcement must be automatable (API/CLI/Terraform/script), but must also support a “verify-only” mode when tokens lack admin mutation permissions.
- Evidence must be generated from the same tool path used to read/apply (avoid manual transcription).
- Required checks selection must align with current CI naming, or the workflow must be reshaped so the intended checks exist as enforceable contexts.

## 3. Target User / Actor

Who is this for?

- Primary actor: repo maintainers/admins responsible for protecting `main` and interpreting CI as a merge gate.
- Secondary actor: contributors/agents opening PRs who need deterministic, non-bypassable feedback at merge time.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0055-platform-policy-enforcement.md` (Section 3)

Contract Notes / Non-obvious constraints (Section 3):

- “Admin evidence” must be sufficient for a maintainer to attest to policy state without clicking through UI.
- The policy should not introduce false negatives (for example, requiring PR-context-only checks on push-only events).

## 4. Rough Idea (Unstructured Thinking)

- Provide a single deterministic policy definition (expected required check contexts + enforcement toggles) in-repo.
- Provide a scriptable apply path (admin) and a CI-safe verify path (read-only).
- Emit an evidence JSON artifact that includes the entire live policy object (or normalized subset) and a SHA-256 hash for machine verification.

## 5. Constraints

- Must verify current live platform state before changing anything (no assumptions).
- Must support plan/permission gating: if branch protection is unavailable (plan) or token cannot mutate admin settings, workflow must degrade to verify-only with a documented controlled apply path.
- Must preserve WF-0054 event-scope intent: PR-context-coupled checks should be enforced on PRs, not incorrectly required for push-only contexts.

## 6. Risks / Unknowns

- GitHub plan gating: branch protection/rulesets endpoints can be unavailable for a private repo unless plan allows it.
- Check context naming mismatch: desired “required checks” list may not exist as enforceable contexts today.
- Token scope/permissions: CI tokens often cannot mutate branch protection; evidence and drift detection must still run.

## Open Questions / Deferred

- Do we require `backend`/`frontend` as required checks (current enforceable contexts), or refactor CI so the intended six checks exist as separate jobs/check contexts?
- Do we need rulesets (org-level) vs classic branch protection, or either is acceptable?
- Which toggles beyond required checks are mandatory: PR review count, stale dismissal, admin bypass, force-push/delete, linear history?

## 7. MVP Definition

If we had to ship in 2–3 days:

- Define an expected policy (required status check contexts + core toggles) in-repo.
- Add a deterministic verify command that:
  - reads live policy,
  - normalizes it to a stable representation,
  - fails if mismatched,
  - writes evidence JSON with UTC timestamp.
- Add a controlled apply command for admins that applies the policy and writes the same evidence artifact.

## 8. Explicit Non-Goals

- Redesigning CI beyond what is necessary to ensure the required check contexts exist (if needed, that becomes an explicit, scoped step rather than incidental change).
- Enforcing unrelated security settings (dependabot, secret scanning, etc.) unless directly required for branch protection policy.
