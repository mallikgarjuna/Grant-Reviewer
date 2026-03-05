# WF-0055 — Platform Policy Enforcement

Artifact: brainstorm
Version: v0.3
Status: Completed
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

## Prerequisites (Hard Gates)

- GitHub branch protection / rulesets must be enabled for this repo (currently API read returns HTTP 403 on private repo). Without enabling this feature, WF-0055 cannot satisfy “main branch protection is enforced” done criteria.
- Applying policy requires an actor/token with admin permission to modify branch protection/rulesets. CI is assumed to be verify-only by default.

## Policy Mechanism (Rulesets vs Branch Protection) (Contract)

- Preferred mechanism: **Repository rulesets** (GitHub “rulesets”) targeting branch `main`.
- Fallback mechanism: **Classic branch protection** on branch `main`.
- Implementation contract:
  - Tooling must attempt to read/apply via rulesets first; if unavailable (plan-gated, endpoint forbidden/unavailable), fall back to classic branch protection.
  - Evidence artifact must record which mechanism was used (ruleset vs branch protection) and include the raw live payload from that mechanism.

## 1. Problem Statement

What problem are we solving?

- Primary gap: `main` can potentially be updated/merged without the intended CI gates being required (policy bypass risk), and enforcement can drift from repo intent over time.
- This WF exists as a follow-on to WF-0054 (repo-only); WF-0055 is explicitly platform-facing (GitHub settings), with evidence and drift detection.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0055-platform-policy-enforcement.md` (Section 1)

Contract Notes / Non-obvious constraints (Section 1):

- “Required checks” must refer to GitHub status check contexts. To enforce the six checks listed in the WF-0055 request, CI must emit those six as distinct check-run contexts (by splitting jobs and naming jobs accordingly).
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
  - Contract: WF-0055 will treat the below list as the required check-run context set for `main` (not YAML step names unless CI is refactored to produce those contexts).

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
- Evidence artifact must be generated deterministically from the same API read path used for verification/apply.

## 6. Risks / Unknowns

- GitHub plan gating: branch protection/rulesets endpoints can be unavailable for a private repo unless plan allows it.
- Check context naming mismatch: desired “required checks” list may not exist as enforceable contexts today.
- Token scope/permissions: CI tokens often cannot mutate branch protection; evidence and drift detection must still run.

## Open Questions / Deferred

- CI shape decision: we will refactor CI so the intended six checks exist as separate jobs/check contexts, so GitHub branch protection can require them deterministically.
- Toggle surface: enforce exact toggle values below; anything not listed is explicitly “do not manage” (leave as-is).

## Required Checks (Contract)

Target branch: `main`

Required status check contexts (must exist as distinct GitHub check-run contexts on PRs targeting `main`):

1. `backend / Contract Boundary Governance Check`
2. `backend / WF-0054 CI Policy Regression Sweep`
3. `backend / Contract Gate (Marker)`
4. `backend / Test (Pytest no_db)`
5. `frontend / Lint`
6. `frontend / Build`

Contract Notes:

- Today, these are step names inside two jobs (`backend`, `frontend`). WF-0055 will reshape the CI workflow so each item above becomes its own job check context (job `name:`), allowing branch protection required checks to enforce them.

## Enforcement Toggles (Contract)

These are the exact toggle values WF-0055 will enforce for `main` (whether via rulesets or classic branch protection).

- `enforce_admins`: true (aka “Include administrators”)
- `allow_force_pushes`: false
- `allow_deletions`: false
- `required_pull_request_reviews`: false (not enforced by WF-0055; if the platform object requires presence, set to “disabled” / null-equivalent)
  - `dismiss_stale_reviews`: false
  - `require_code_owner_reviews`: false
  - `required_approving_review_count`: 0
- `bypass_allowances`: none (no explicit bypass list; admins are still subject due to `enforce_admins=true`)
- `strict_required_status_checks` (aka “Require branches to be up to date before merging”): true
- `require_conversation_resolution`: false
- `require_linear_history`: false
- `require_signed_commits`: false

Contract Notes:

- This toggle set is intentionally minimal (aligns to “required checks + include admins + block force-push/delete”). Anything not listed is out of scope for WF-0055.
- Evidence must always include the full toggle surface above (even if the platform response omits fields when disabled, the evidence normalization must fill them deterministically).

## 7. MVP Definition

If we had to ship in 2–3 days:

- Define an expected policy (required status check contexts + core toggles) in-repo.
- Add a deterministic verify command that:
  - reads live policy,
  - normalizes it to a stable representation,
  - fails if mismatched,
  - writes evidence JSON with UTC timestamp.
- Add a controlled apply command for admins that applies the policy and writes the same evidence artifact.

## Evidence Artifact Contract (Machine-Verifiable)

- Store under: `docs/walkthroughs/evidence/WF-0055/`
- Filename format: `branch-protection_<repo>_<branch>_<utc-timestamp>.json`
- Must include (minimum):
  - `timestamp_utc` (RFC3339)
  - `repo` (nameWithOwner)
  - `branch`
  - `actor` (login)
  - `tooling` (gh version + command path + API endpoints used)
  - `required_checks` (full ordered list)
  - `toggles` (admin enforcement, force-push/delete, review requirements, stale dismissal, bypass allowances)
  - `mechanism` (`rulesets` | `branch_protection`)
  - `live_policy_raw` (raw API response or raw rule payload)
  - `evidence_sha256` (hash of normalized evidence payload section)

## Runbook Requirements (Contract)

WF-0055 must produce a runbook that includes:

- Rollback commands (restore previous snapshot policy to `main`)
- Re-apply commands (apply expected policy to `main`)
- Permission prerequisites (admin required; CI verify-only expectation)
- Failure modes and expected errors (plan-gated 403, insufficient token permissions, missing check contexts, stale/different check names)

## 8. Explicit Non-Goals

- Redesigning CI beyond what is necessary to ensure the required check contexts exist (if needed, that becomes an explicit, scoped step rather than incidental change).
- Enforcing unrelated security settings (dependabot, secret scanning, etc.) unless directly required for branch protection policy.
