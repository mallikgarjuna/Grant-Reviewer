# WF-0056 — Platform Policy Enforcement Live Rehearsal

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-05

## 0. User Stories (MVP)

- US1: As a maintainer, I want a live verify run against `mallikgarjuna/Grant-Reviewer:main`, so that I can prove WF-0055 policy alignment with durable evidence.
- US2: As an admin maintainer, I want controlled live apply rehearsal on `policy-rehearsal`, so that I can prove policy mutation works safely without touching `main`.
- US3: As an admin maintainer, I want controlled live rollback rehearsal on `policy-rehearsal`, so that I can restore prior policy deterministically with evidence.
- US4: As a maintainer/auditor, I want durable evidence retention standards for verify/apply/rollback, so that compliance claims are reviewable after the run.

## Deferred Stories (Not in MVP)

- Auto-mutation from CI or scheduled workflows.
- Expanding enforcement surface beyond WF-0055 contract (reviews, CODEOWNERS, signed commits, linear history).
- Multi-repo orchestration beyond `mallikgarjuna/Grant-Reviewer`.
- Full production `main` apply rehearsal in this WF.

## 1. In Scope

- Operationalize WF-0055 in this live repo with evidence-first execution.
- Live verify against `main` using expected policy from `config/platform_policy/main_policy.yaml`.
- Live apply + rollback rehearsal on dedicated branch `policy-rehearsal` only.
- Real required-check-context discovery during apply preflight; fail-closed on missing contexts.
- Durable evidence retention:
  - Primary: workflow artifacts from live runs.
  - Fallback: `docs/walkthroughs/evidence/WF-0056/` with checksums.
- Runbook + walkthrough that make the rehearsal repeatable and auditable.

## 2. Out of Scope

- Re-designing WF-0055 policy schema/contracts.
- Enforcing protections on branches beyond `main` and `policy-rehearsal`.
- Implementing unrelated GitHub governance policies.
- Replacing CI verify-only model with automatic mutation.

## 2.1 MVP Acceptance Criteria

- AC1 (US1, FR1, FR2, FR11, FR12): Live verify on `main` produces deterministic pass/fail drift output and durable evidence that includes workflow run linkage.
- AC2 (US2, FR3, FR4, FR5, FR6, FR11): Apply rehearsal on `policy-rehearsal` succeeds only after permissions + required-check preflight and records snapshot + post-apply verification evidence.
- AC3 (US3, FR7, FR8, FR11, FR12): Rollback rehearsal restores from captured snapshot and emits restoration-verification evidence linked to the apply snapshot.
- AC4 (US4, FR9, FR10): Final walkthrough includes a complete evidence chain (`verify -> apply -> rollback`) with checksum fields and artifact references.

## 3. User / System Flow

### Happy path

1. Maintainer prepares expected policy + live credentials and confirms branch targets (`main` verify, `policy-rehearsal` mutation) (US1, US2, US3).
2. Verify command reads live policy for `main`, normalizes vs expected policy, and emits durable evidence artifact with drift verdict (US1, US4).
3. Apply rehearsal preflight validates mutation permissions, mechanism availability, and required check contexts; if valid, apply executes on `policy-rehearsal` and captures snapshot + evidence (US2, US4).
4. Rollback rehearsal restores from captured snapshot on `policy-rehearsal`, verifies restoration, and emits rollback evidence (US3, US4).
5. Walkthrough records artifact references, checksums, command history, and final rehearsal outcome for audit trail (US4).

### Failure path A — Missing required check contexts

1. Apply preflight discovers missing check contexts for required checks on `policy-rehearsal` (US2).
2. Apply aborts with deterministic `missing_required_checks` output and evidence; no mutation occurs (US2, US4).

### Failure path B — Insufficient permissions

1. Mutation preflight detects token/admin scope is insufficient (US2, US3).
2. Tool emits `permission_denied` evidence and remains non-mutating (US2, US3, US4).

### Failure path C — Mechanism/API gating or partial failure

1. Ruleset/branch-protection API read or mutation fails due to plan gating/endpoint constraints (US1, US2, US3).
2. Command exits non-zero with deterministic error category and durable evidence for postmortem/retry decisions (US1, US4).

## 4. Functional Requirements

- FR1 (US1): Verify must read live policy for `main`, compare to expected policy, and return deterministic drift status.
- FR2 (US1, US4): Verify must always produce durable evidence artifact containing mechanism used, normalized policy, and drift summary.
- FR3 (US2): Apply rehearsal must only target `policy-rehearsal` and must never mutate `main`.
- FR4 (US2): Apply preflight must validate required-check contexts against real check-run surface and fail-closed when missing.
- FR5 (US2): Apply rehearsal must capture a pre-mutation snapshot artifact that is sufficient for rollback.
- FR6 (US2, US4): Apply rehearsal must emit deterministic success/failure evidence including mutation intent, preflight verdict, and post-apply verification.
- FR7 (US3): Rollback rehearsal must restore from captured snapshot and verify restoration against expected prior state.
- FR8 (US3, US4): Rollback rehearsal must emit deterministic success/failure evidence with snapshot linkage.
- FR9 (US4): Evidence retention policy must prioritize workflow artifacts and support local fallback with `evidence_sha256`/`snapshot_sha256`.
- FR10 (US4): Walkthrough must include reproducible run sequence, artifact references, and explicit proof that rehearsal was live (not static stubs).
- FR11 (US1, US2, US3): All verify/apply/rollback failure modes must be classified with stable error kinds (e.g., `missing_required_checks`, `permission_denied`, `plan_gated`, `api_failure`).
- FR12 (US1, US2, US3, US4): Rehearsal completion criteria require a full verify + apply + rollback evidence chain in this repo context.

## 5. Data & API Contracts

### Expected policy input (FR1, FR3, FR4)

- Source of truth: `config/platform_policy/main_policy.yaml` (US1, FR1).
- Required fields used in this WF: branch target, required checks, toggle surface, mechanism preference (US1, FR1, FR3).
- Mutation target override for rehearsal branch must be explicit and auditable in command/evidence metadata (US2, FR3).

### Verify/apply/rollback evidence schema (FR2, FR6, FR8, FR9, FR11, FR12)

- Required metadata: `timestamp_utc`, `repo`, `branch`, `actor`, `operation`, `mechanism`, `intent_mode`, `result` (US4, FR2).
- Required trace metadata: `workflow_run_id`, `workflow_job_name`, `commit_sha`, `snapshot_id` (when applicable) (US4, FR9, FR10, FR12).
- Policy payloads: `expected_policy_ref`, `normalized_live_policy`, optional `live_policy_raw` (redacted to response bodies only) (US1, FR2).
- Failure surface: `error.kind`, `error.message`, `error.endpoint` (nullable) (US1, US2, US3, FR11).
- Checksum fields: `evidence_sha256` for evidence payload and `snapshot_sha256` for snapshots (US4, FR9).
- Traceability fields: `preflight`, `post_apply_verify`, `rollback_source_snapshot`, `linked_artifacts[]` (US2, US3, US4, FR6, FR8, FR12).

### Snapshot contract (FR5, FR7, FR8)

- Created immediately before apply mutation (US2, FR5).
- Contains sufficient raw/normalized policy state for deterministic restore (US3, FR7).
- Linked from apply and rollback evidence through stable snapshot ID/path (US3, US4, FR8).

### Durable evidence locations (FR9, FR10)

- Primary: workflow run artifacts attached to live verify/apply/rollback runs (US4, FR9).
- Fallback: `docs/walkthroughs/evidence/WF-0056/` with machine-readable files and checksums (US4, FR9).
- Walkthrough references both artifact location and integrity fields (US4, FR10).

### Required-check discovery contract (FR4, FR11)

- Discovery source: real GitHub check-run contexts from recent PR check suites relevant to target branch policy enforcement (US2, FR4).
- Apply preflight behavior:
  - derive actual available contexts from live check-run data,
  - compare expected required checks against discovered contexts,
  - fail-closed with `missing_required_checks` when any expected context is absent (US2, FR4, FR11).

## 6. Components / Modules

- `policy verify command`: live read/normalize/diff/evidence for `main` (FR1, FR2).
- `policy apply command`: intent-gated live mutation flow for `policy-rehearsal` with preflight + snapshot + post-check (FR3, FR4, FR5, FR6).
- `policy rollback command`: snapshot-based restore + verification + evidence (FR7, FR8).
- `required-check discovery adapter`: obtains real check-run contexts for preflight decisions (FR4, FR11).
- `evidence writer`: deterministic schema serialization + checksum generation + artifact publishing hooks (FR2, FR6, FR8, FR9).
- `walkthrough/runbook docs`: reproducible operator instructions + proof chain assembly (FR10, FR12).

Suggested coarse file paths:
- `backend/tools/gh_policy/` (command + client + preflight + evidence)
- `.github/workflows/` (verify/apply/rollback workflow wiring and artifact upload)
- `docs/walkthroughs/evidence/WF-0056/` (fallback evidence storage)
- `docs/walkthroughs/` (WF-0056 walkthrough/runbook)

## 7. Edge Cases

- Required checks exist for `main` but not for rehearsal branch event contexts (US2, FR4).
- Ruleset read succeeds but write path is disallowed; fallback behavior must be deterministic and explicit (US2, FR11).
- Snapshot is captured but rollback verification fails; workflow must preserve partial evidence for diagnosis (US3, FR8, FR11).
- Artifact upload succeeds but local fallback write fails (or vice versa); proof chain must still indicate retention completeness state (US4, FR9).
- Rehearsal run executed with wrong branch target; intent metadata must expose mismatch before mutation (US2, FR3, FR6).

## 8. Testing Decisions (TDD)

- Behavior changes in preflight, apply, rollback, and evidence generation follow RED→GREEN→refactor per unit/integration seam.
- Public test seams:
  - command entrypoints (`verify`, `apply`, `rollback`)
  - required-check discovery boundary
  - evidence serialization/checksum boundary
- Boundary mocking only:
  - mock GitHub API transport/auth and artifact upload adapters
  - avoid mocking internal policy normalization/diff logic
- Minimum prove-it tests by story:
  - US1: verify live-read path emits deterministic drift/evidence.
  - US2: apply preflight fails on missing check contexts; apply success includes snapshot + post-verify.
  - US3: rollback restores snapshot and reports verification status.
  - US4: durable evidence includes required metadata + checksums + links.

## 9. Telemetry (Minimal)

- Log operation start/end with operation type and target branch.
- Emit preflight decision summary (`permissions_ok`, `mechanism`, `missing_required_checks_count`).
- Emit evidence publication summary (workflow artifact ID/path, fallback local path).
- Emit deterministic error kind on all failures.

## 10. Deferred / Not in MVP

- Automatic periodic rehearsal scheduling.
- UI layer for policy rehearsal operations.
- Generalized evidence ingestion dashboard.
- Cross-repo policy fleet enforcement.

## 11. Open Questions (if any)

- Which mechanism paths (rulesets only vs rulesets + branch-protection fallback) are writable in this repo with available admin credentials?

## 12. Changelog

- v0.1 (2026-03-05): Initial PRD from brainstorm
- v0.2 (2026-03-05): Applied risk-audit refinements; added acceptance criteria, trace metadata contract, required-check discovery contract; marked Ready for Tasks
- v0.3 (2026-03-05): Adversarial Part B re-audit pass; confirmed no blocking gaps for Phase 2 task planning
