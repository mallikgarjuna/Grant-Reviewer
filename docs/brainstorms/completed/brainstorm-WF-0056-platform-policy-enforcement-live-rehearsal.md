# WF-0056 — Platform Policy Enforcement Live Rehearsal

Artifact: brainstorm
Version: v0.4
Status: Draft Complete
Last Updated: 2026-03-05

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0056-platform-policy-enforcement-live-rehearsal.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts/decisions (what we will implement).
- The Q&A transcript is rationale only; it must not introduce new contracts.
- If Q&A reveals a new contract or contradicts this brainstorm, promote the contract into this brainstorm.

---

## Repo Reality Snapshot (Read-Only)

Date: 2026-03-05

- Existing tooling exists for WF-0055: `backend/tools/gh_policy` supports `verify|apply|rollback`.
- Expected policy is in-repo: `config/platform_policy/main_policy.yaml` (includes required checks + toggle surface).
- There is a GitHub Action that runs verify-only on PRs to `main`: `.github/workflows/verify-platform-policy.yml`.
- Existing evidence in `docs/walkthroughs/evidence/WF-0055/` is currently tracer/offline style (placeholder `owner/repo`), not proof of live enforcement for this repo.
- Critical reality check: `apply` and `rollback` currently use static clients (no live GitHub mutation); they produce evidence but do not change repo policy.

Open questions this snapshot suggests (to be resolved in this WF):
- Token/permissions model: where an admin-scoped token lives and how we prevent accidental mutation.
- How to implement durable evidence retention for live runs (workflow artifacts as primary; local docs evidence as fallback).
- How to implement required-check-context discovery for apply preflight (fail-closed).

---

## Scope Contract (MVP)

- Target repo: `mallikgarjuna/Grant-Reviewer`
- Verify target: `main`
- Apply/rollback rehearsal target: dedicated rehearsal branch `policy-rehearsal` (created for this purpose; never `main` for MVP).
- Enforcement mechanism: prefer rulesets, fall back to classic branch protection (inherit WF-0055 contract; record mechanism used in evidence).

Evidence retention contract (MVP):
- Primary: GitHub Actions workflow artifacts uploaded from live runs (verify/apply/rollback) and referenced in the walkthrough.
- Fallback: local evidence files stored under `docs/walkthroughs/evidence/WF-0056/` and referenced in the walkthrough, including `evidence_sha256`/`snapshot_sha256` fields.

Mutation capability contract (MVP):
- Implement live apply + live rollback for the selected mechanism(s); static/offline stubs do not count as rehearsal.
- Apply preflight must validate required check contexts against the real check-run surface (not a self-derived set).

---

## 1. Problem Statement

We have a platform policy enforcement stack (WF-0055) that is largely validated via local/tracer evidence and tests, but not yet proven under live GitHub enforcement for this repo.

The key risk: until live verify plus controlled apply/rollback rehearsal succeeds with evidence artifacts, the governance claims are theoretical, and drift/bypass could go undetected or be unfixable under pressure.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0056-platform-policy-enforcement-live-rehearsal.md` (Section 1)

Contract notes / non-obvious constraints:
- WF-0056 is not re-designing WF-0055; it is operationalizing it in the live repo with auditable evidence.
- CI remains verify-only; apply/rollback are explicit admin actions with safeguards.
- Evidence retention is part of "done": console output alone does not count as proof.

---

## 2. Desired Outcome

After WF-0056:
- We can run `verify` against the real repo/branch and produce a durable evidence artifact that shows the live GitHub policy matches `config/platform_policy/main_policy.yaml`.
- We can run an intentionally controlled `apply` rehearsal (including snapshot creation) and a `rollback` rehearsal that restores the prior state, both with deterministic evidence artifacts.
- We have a runbook/walkthrough that makes the above repeatable and safe.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0056-platform-policy-enforcement-live-rehearsal.md` (Section 2)

Contract notes / non-obvious constraints:
- Evidence must be retained and reviewable (not just console logs).
- Rehearsal must be low-risk: no accidental weakening of `main` branch protection, and a deterministic rollback path.
- Rehearsal applies to `policy-rehearsal` for MVP; `main` is verify-only for this WF.

---

## 3. Target User / Actor

- Primary actor: repo maintainer/admin who can read policy (verify) and, when explicitly intended, mutate protections (apply/rollback).
- Secondary actor: CI (GitHub Actions) which runs verify-only drift detection on PRs to `main`.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0056-platform-policy-enforcement-live-rehearsal.md` (Section 3)

---

## 4. Rough Idea (Unstructured Thinking)

- Treat WF-0055 as the underlying mechanism and expected policy contract.
- Add an operational layer:
  - live verification evidence capture for this repo/branch
  - a safe apply/rollback rehearsal procedure with strict intent confirmation and snapshots
  - repeatable runbook/walkthrough with explicit preflight checks (permissions, mechanism, required check contexts)

---

## 5. Constraints

- Least privilege: CI uses `github.token` verify-only; no CI mutation.
- Safety: apply/rollback rehearsal should not permanently weaken `main` protections.
- Evidence: output must be durable (files/artifacts), not only terminal output.
- Scope: operationalization and evidence; avoid expanding tool surface unless required to capture durable evidence.

---

## 6. Risks / Unknowns

- Permissions: admin mutation permission may be unavailable without a PAT or org-level approval.
- Mechanism differences: rulesets may be plan-gated; branch protection fallback must remain acceptable.
- Required check contexts: required checks must correspond to real, emitted check-run contexts on PRs; mismatch can deadlock merges.
- Evidence retention: deciding the canonical storage mechanism for live evidence (repo vs workflow artifacts vs local-only with checksum references).
- Tooling gap: current `apply`/`rollback` implementations are static; live mutation must be implemented before any rehearsal claims are valid.
- Tooling gap: apply preflight currently cannot detect missing check contexts in GitHub; this must be implemented to avoid false success.

---

## Open Questions / Deferred

- Which repo(s) are in scope beyond `mallikgarjuna/Grant-Reviewer` (assumed only this repo for MVP).
- Whether to extend GitHub Actions to upload evidence artifacts as workflow run artifacts (preferred) vs committing evidence into the repo.
  - Resolved for MVP: use workflow artifacts as primary retention; local evidence under `docs/walkthroughs/evidence/WF-0056/` is fallback.

---

## 7. MVP Definition

Ship in 2-3 days:
- A repeatable live verify run that produces a durable evidence artifact for `mallikgarjuna/Grant-Reviewer:main`.
- Implement live mutation support (apply + rollback) for the selected mechanism(s), including snapshot creation and post-operation verification.
- Implement real required-check-context discovery for apply preflight (fail with deterministic `missing_required_checks` when contexts do not exist).
- A controlled apply rehearsal (against `policy-rehearsal`) that:
  - captures a snapshot artifact
  - attempts apply with explicit intent gates
  - records deterministic evidence
- A controlled rollback rehearsal that restores the snapshot and records deterministic evidence (and validates restore success).
- Documentation: one runbook and one walkthrough capturing commands, safety checks, and evidence references.

---

## 8. Explicit Non-Goals

- Enforcing any GitHub settings outside the WF-0055 contracted policy surface (required checks + toggles).
- Auto-mutation from CI (apply/rollback).
- Redesigning the expected policy schema or expanding required check context lists beyond the WF-0055 contract.
