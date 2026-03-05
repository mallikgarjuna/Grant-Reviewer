# WF-0055 — Platform Policy Enforcement

Artifact: prd
Version: v0.3
Status: Completed
Last Updated: 2026-03-05

## 0. User Stories (MVP)

- US1: As a maintainer, I want `main` protected by required status checks, so that merges cannot bypass CI gates.
- US2: As a maintainer, I want a verify-only drift detector, so that changes to GitHub policy are detected deterministically and produce evidence.
- US3: As an admin maintainer, I want a controlled apply flow, so that I can safely enforce the expected policy (with preflight + snapshot + evidence).
- US4: As a maintainer, I want rollback instructions, so that I can restore the previous live policy if enforcement causes issues.

## Deferred Stories (Not in MVP)

- Enforce PR review approvals, CODEOWNERS, or conversation resolution gates.
- Enforce signed commits, linear history, or other repo-wide security settings.
- Manage protections for branches other than `main`.

## 1. In Scope

- Enforce GitHub protection on branch `main` via:
  - preferred: repository **rulesets** targeting `main`
  - fallback: classic **branch protection** for `main`
- Required status check contexts (6) for merges to `main`:
  1. `backend / Contract Boundary Governance Check`
  2. `backend / WF-0054 CI Policy Regression Sweep`
  3. `backend / Contract Gate (Marker)`
  4. `backend / Test (Pytest no_db)`
  5. `frontend / Lint`
  6. `frontend / Build`
- Enforcement toggles for `main`:
  - include administrators (`enforce_admins=true`)
  - disallow force-push and deletion
  - strict required status checks (require up-to-date)
  - explicitly do **not** manage PR review requirements and other unrelated toggles
- Evidence artifact generation (machine-verifiable JSON) from the same read/apply tool path.
- Drift detection:
  - verify-only in CI (no mutation)
  - controlled apply by an authorized actor (manual or explicitly dispatched)
- Rollback/runbook for restore + re-apply.
- Plan/permission preflight and deterministic error surfacing when GitHub plan or token permissions block reads/writes.

## 2. Out of Scope

- Broader CI redesign beyond what is required to ensure the six required check contexts exist as enforceable GitHub check-run contexts.
- Enforcing review policies (approvals, CODEOWNERS), conversation resolution, signed commits, linear history, or any security settings not listed in WF-0055 brainstorm contracts.
- Managing organization-level settings or non-`main` branches.

## 2.1 MVP Acceptance Criteria (Ship / Prove It)

- AC1 (US2, FR2–FR5, FR7, FR11): Verify-only command reads live policy (rulesets → fallback branch protection), emits evidence JSON, and fails on drift with a minimal diff.
- AC2 (US3, FR1–FR6, FR11–FR12): Controlled apply performs preflight + snapshot, applies expected policy, re-reads to confirm match, and emits evidence JSON.
- AC3 (US4, FR8, FR12, FR14): Rollback restores the last captured snapshot deterministically and emits rollback evidence JSON.
- AC4 (US1, FR9–FR10, FR13): Merges to `main` cannot bypass the six required check contexts; enforcement includes administrators and blocks force-push/delete.

## 3. User / System Flow

### Happy path (US1, US2, US3, US4)

1. Define expected `main` policy in-repo (US1, US2, US3).
2. Verify-only CI job runs on PRs targeting `main`:
   - reads live policy (rulesets → fallback branch protection),
   - normalizes it,
   - compares against expected,
   - writes evidence JSON,
   - fails the job if drift is detected (US2).
3. Admin performs controlled apply (manual command or explicit workflow dispatch):
   - preflight (plan/permissions + required check contexts existence),
   - reads and snapshots current live policy (for rollback),
   - applies expected policy,
   - re-reads and verifies match,
   - writes evidence JSON (US1, US3, US4).
4. If rollback is required, admin restores the most recent snapshot taken by apply:
   - restore via the same mechanism path (rulesets → fallback branch protection),
   - re-read and verify restoration,
   - write rollback evidence JSON (US4).

### Failure path A — Plan-gated / API forbidden (US2, US3)

1. Verify/apply attempts to read rulesets/branch-protection endpoints.
2. GitHub responds with a deterministic “feature unavailable”/403 plan gate (as observed in brainstorm snapshot).
3. Tool exits non-zero and prints:
   - what endpoint failed,
   - why (plan gating),
   - next steps (upgrade plan / make repo public / use UI), and
   - that enforcement cannot be claimed without platform support (US2, US3).

### Failure path B — Missing required check contexts (US1, US3)

1. Apply preflight detects one or more required check contexts do not exist as check-run contexts.
2. Apply refuses to enforce required checks and reports the missing contexts and how to make them exist (CI job naming split) (US1, US3).

### Failure path C — Insufficient permissions (US3)

1. Apply preflight detects token lacks admin rights for mutation.
2. Tool runs in verify-only mode, writes evidence, and exits with a clear “mutation not permitted” reason (US3).

## 4. Functional Requirements

- FR1 (US1, US2, US3): Provide a single “expected policy” definition in-repo (required checks + toggles + mechanism preference).
- FR2 (US2, US3): Read live policy for `main` using rulesets first; if unavailable, fall back to branch protection.
- FR3 (US2, US3): Normalize live policy to a stable representation (fill defaults deterministically, order lists, stable field names).
- FR4 (US2): Compare normalized live vs expected policy; output a minimal drift diff; exit non-zero on drift.
- FR5 (US2, US3): Emit evidence JSON on every verify/apply attempt, including raw live payload and a SHA-256 over the normalized evidence payload.
- FR6 (US3): Controlled apply supports:
  - explicit “apply” intent (no accidental mutation),
  - a preflight stage,
  - snapshot of previous live policy for rollback,
  - re-read verification after apply.
- FR7 (US2): CI runs verify-only; CI must not mutate branch protection/rulesets.
- FR8 (US4): Rollback restores the prior snapshot policy to `main` (same mechanism path used to read/apply), then emits evidence.
- FR9 (US1): Required status checks enforced are exactly the six contexts listed in-scope; no additional contexts are required by WF-0055.
- FR10 (US1): Enforcement toggles match the contract set (include admins, no force-push/delete, strict status checks).
- FR11 (US2, US3): Every verify/apply/rollback attempt writes evidence; evidence includes an `error` surface when failures occur.
- FR12 (US4): Controlled apply writes a rollback snapshot artifact that can be replayed deterministically.
- FR13 (US1): CI emits the six required check contexts as enforceable GitHub check-run contexts (workflow name + job name).
- FR14 (US4): Provide a runbook covering verify/apply/rollback prerequisites, commands, and failure modes.

## 5. Data & API Contracts

### Expected policy definition (US1, US2, US3) (FR1)

- Stored in-repo as a machine-readable file (YAML or JSON).
- Fields (minimum):
  - `schema_version`: `v1`
  - `repo`: `<owner>/<repo>` (or inferred at runtime, but recorded in evidence)
  - `target_branch`: `main`
  - `mechanism_preference`: `rulesets_first`
  - `required_checks`: ordered list of 6 contexts (exact strings)
  - `toggles` (full surface; exact values enforced by WF-0055):
    - `enforce_admins`: true
    - `allow_force_pushes`: false
    - `allow_deletions`: false
    - `strict_required_status_checks`: true
    - `required_pull_request_reviews`: false
    - `require_conversation_resolution`: false
    - `require_linear_history`: false
    - `require_signed_commits`: false
    - `bypass_allowances`: [] (none)

### Evidence artifact JSON (US2, US3, US4) (FR5)

Location + naming contract: `docs/walkthroughs/evidence/WF-0055/branch-protection_<repo>_<branch>_<utc-timestamp>.json`

Minimum fields:
- `timestamp_utc` (RFC3339)
- `repo` (nameWithOwner)
- `branch`
- `actor` (login)
- `tooling` (version + command path + endpoints used)
- `mechanism` (`rulesets` | `branch_protection`)
- `required_checks` (full ordered list)
- `toggles` (full normalized toggle surface)
- `live_policy_raw` (raw API response payload)
- `normalized_policy` (stable normalized representation used for drift compare)
- `drift`:
  - `is_drifted` (bool)
  - `diff` (field-level changes)
- `error` (nullable):
  - `kind` (e.g. `plan_gated`, `permission_denied`, `missing_required_checks`, `api_unreachable`)
  - `message`
  - `endpoint` (if applicable)
- `evidence_sha256` (sha256 of `normalized_policy` + required metadata subset)

### Rollback snapshot artifact (US4) (FR12)

- Written during controlled apply before mutation.
- Location: `docs/walkthroughs/evidence/WF-0055/snapshots/`
- Filename format: `snapshot_<repo>_<branch>_<utc-timestamp>.json`
- Content (minimum):
  - `mechanism` (`rulesets` | `branch_protection`)
  - `live_policy_raw` (raw payload sufficient to restore)
  - `captured_from_endpoints` (list)
  - `snapshot_sha256`

### GitHub API surface (US2, US3) (FR2)

- Read:
  - rulesets (preferred): list + identify rule targeting `main` (or a ruleset whose conditions match `main`)
  - branch protection (fallback): protection object for `main` including required status checks and toggles
- Apply (admin-only):
  - create/update ruleset OR set branch protection fields

Note: plan/feature gating must be treated as a first-class, deterministic failure mode (no silent partial success).

## 6. Components / Modules

- `ExpectedPolicy` loader: reads expected policy file and validates it (FR1).
- `GitHubPolicyClient`:
  - reads rulesets and/or branch protection (FR2),
  - applies via selected mechanism when permitted (FR6).
- `PolicyNormalizer`: converts raw live policy into normalized representation (FR3).
- `PolicyDiff`: compares normalized live vs expected; produces diff used by CI logs/evidence (FR4).
- `EvidenceWriter`: writes evidence JSON and computes sha256 (FR5).
- `VerifyCommand`: verify-only entrypoint used by CI (FR7).
- `ApplyCommand`: controlled apply entrypoint guarded by explicit flag + preflight (FR6).
- `RollbackCommand`: restore from snapshot + evidence (FR8).

Suggested coarse file layout (subject to Phase 2 task planning):
- `tools/gh_policy/` (core logic)
- `tools/gh_policy/fixtures/` (golden payloads for tests)
- `.github/workflows/verify-platform-policy.yml` (verify-only CI wiring)
- `docs/walkthroughs/runbooks/WF-0055-platform-policy-enforcement.md` (runbook)

## 7. Edge Cases

- GitHub API returns 403 for rulesets/branch-protection due to plan gating (Failure path A).
- Required checks list contains contexts that do not exist as check-run contexts yet (Failure path B).
- “Strict required status checks” can deadlock if required checks never run on the relevant event; verify must ensure the checks actually run in PR context (US1).
- Rulesets and branch protection may have different field surfaces; normalization must map them into the same canonical toggle set (FR3).
- Evidence artifact must be generated even on failure (include error surface and partial context where available) (US2).
- Evidence raw payloads should be treated as potentially sensitive metadata; avoid including tokens/headers and keep evidence to response bodies only (US2, US3).

## 8. Testing Decisions (TDD)

- Unit tests:
  - normalizer: rulesets payload → normalized policy; branch-protection payload → normalized policy
  - diff: expected vs live produces stable, minimal diff
  - evidence: sha256 stable for identical normalized payload
- Fixture-driven tests:
  - golden raw payload fixtures captured from GitHub (redacted as needed) to ensure normalization stability across changes.
- Optional integration-ish test (non-CI, manual):
  - behind env flag + real token to read live policy; never run by default in CI.

## 9. Telemetry (Minimal)

- CI logs:
  - mechanism selected (`rulesets` vs `branch_protection`)
  - whether plan/permission gating occurred (with endpoint)
  - drift summary (top-level fields changed)
  - evidence artifact path written

## 10. Deferred / Not in MVP

- Managing additional policy toggles beyond the contract set.
- Auto-applying policy in CI on push/PR (explicitly disallowed; apply must be controlled).
- Managing protections for additional branches/tags.

## 11. Open Questions (if any)

- Confirm whether rulesets endpoints are available on this repo once plan prerequisites are met; if not, treat classic branch protection as the sole supported enforcement mechanism.

## 12. Changelog

- v0.1 (2026-03-05): Initial PRD from brainstorm
- v0.2 (2026-03-05): Applied risk audit edits; added rollback snapshot + explicit toggle surface; marked Ready for Tasks
- v0.3 (2026-03-05): Adversarial risk-audit polish; added MVP acceptance criteria
