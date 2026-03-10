<!-- docs/tasks/task-WF-0072-e2e-trust-proof-nwo-erc-msca.md -->
# WF-0072 — E2E Trust Proof for Representative NWO/ERC/MSCA Flows

Artifact: task
Version: v0.2
Status: Ready for Implementation
Last Updated: 2026-03-10

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Author the WF-0072 verification-matrix contract and tracer-bullet validator
Goal: Establish one canonical WF-0072 verification bundle contract that enforces the locked representative set, required row fields, deterministic `evidence_ref` replay metadata, conditional auth-lane reporting, and closure-artifact references. Seed it with one passing NWO happy-path tracer-bullet row so later scenario work extends a stable proof object instead of inventing incompatible artifacts.
Slice: tracer-bullet / evidence-contract
User Stories: US1, US3, US4
PRD Requirements: FR1, FR6, FR7, FR8, FR10, FR11, FR12
Depends on: none
Enables: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8
Parallelizable: no
Files to modify:
Must touch files: `backend/scripts/validate_wf_0072_bundle.py`, `backend/tests/test_wf_0072_bundle_contract.py`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Scenario-specific proof execution, walkthrough prose, unrelated evidence frameworks.
Stop if: The existing repo cannot support one matrix artifact that records row-level seam labels, auth lanes, deterministic replay metadata, and closure-artifact references without introducing a second competing proof format.
Session boundary after: no
Acceptance Criteria: The validator fails closed if a row uses an unlocked representative call, omits any required row field, leaves replay metadata incomplete, claims a protected `/app` or `/api/bff/*` seam without dual-lane or skip metadata, or marks a row pass/fail without a concrete `evidence_ref`; the seed matrix contains exactly one NWO happy-path tracer row plus placeholders for baseline-scope and audit-disposition references.
TDD Plan:
- RED: Add `backend/tests/test_wf_0072_bundle_contract.py` covering locked representative-set enforcement, required row fields, deterministic replay metadata, and protected-surface auth-lane validation; run it against an incomplete seed matrix and watch it fail.
- GREEN: Implement `backend/scripts/validate_wf_0072_bundle.py` and author the initial `docs/walkthroughs/evidence/WF-0072/verification-matrix.json` structure so the contract test passes.
- REFACTOR: Normalize field names and error messages so later tasks can append rows without bespoke translation.
Verification Steps: `cd backend && uv run pytest tests/test_wf_0072_bundle_contract.py -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
Risks (if any): If the matrix contract is under-specified here, later proof tasks will drift into incompatible artifacts and the closure task will become manual reconciliation work.

### [ ] Task 2 — Prove the representative NWO happy path on the real structured-review entry seam
Goal: Land one deterministic happy-path proof for `nwo_veni_2025_preproposal` through the real structured-review API seam and record the resulting evidence as one matrix row with exact replay metadata.
Slice: tracer-bullet / representative-happy-path
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR6, FR7, FR9
Depends on: Task 1
Enables: Task 8
Parallelizable: no
Files to modify:
Must touch files: `backend/tests/test_wf_0072_nwo_happy_path.py`, `docs/walkthroughs/evidence/WF-0072/nwo_veni_2025_preproposal_happy_path.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Protected app/BFF coverage, policy-blocking negatives, widening NWO coverage beyond `nwo_veni_2025_preproposal`.
Stop if: The claimed NWO happy path cannot be exercised on the real user-path seam honestly; do not relabel an API-only proof as end-to-end. If only an API-scoped proof is currently honest, record that scope note explicitly in the matrix and surface the protected-surface gap as a blocker before closure.
Session boundary after: no
Acceptance Criteria: A dedicated automated proof for `nwo_veni_2025_preproposal` passes through the family’s actual user-path seam, persists or returns the expected review payload without scope drift, and appends one `pass` row to the matrix naming the exact entrypoint boundary, proof surface, side-effect assertion, result, and evidence reference with exact command/test ID and assertion metadata; if implementation can only prove a narrower API-scoped claim honestly, the row must say so explicitly and closure remains blocked until the end-to-end gap is resolved.
TDD Plan:
- RED: Add `backend/tests/test_wf_0072_nwo_happy_path.py` that expects a replayable happy-path artifact and matching matrix row for `nwo_veni_2025_preproposal`; run it before the evidence file and row exist.
- GREEN: Implement the minimal proof harness and write `docs/walkthroughs/evidence/WF-0072/nwo_veni_2025_preproposal_happy_path.json`, then append the matching matrix row.
- REFACTOR: Remove duplicated assertion metadata between the test output and matrix row if a single canonical evidence payload can supply both.
Verification Steps: `cd backend && uv run pytest tests/test_wf_0072_nwo_happy_path.py -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row nwo_veni_2025_preproposal:happy_path --require-real-user-path`
Risks (if any): If this proof quietly uses a lower-level seam than the claimed user path, the whole WF will overstate launch trust.

### [ ] Task 3 — Prove ERC happy path and fail-closed stage mismatch on the canonical ERC seam
Goal: Extend the existing ERC structured-review end-to-end seam so WF-0072 has both a representative `erc_stg_2026_full` happy-path proof and the required stage-mismatch negative proof with explicit zero-side-effect evidence.
Slice: representative-happy-path / fail-closed-stage-mismatch
User Stories: US1, US2, US3
PRD Requirements: FR1, FR2, FR3, FR6, FR7, FR12
Depends on: Task 1
Enables: Task 8
Parallelizable: no
Files to modify:
Must touch files: `backend/tests/test_erc_structured_review_e2e.py`, `docs/walkthroughs/evidence/WF-0072/erc_stg_2026_full_proofs.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Protected auth-lane browser proof, generic ERC redesign, non-stage ERC failure families.
Stop if: The current ERC end-to-end test seam cannot prove both visible rejection and downstream non-invocation without inventing a new service-entry gate outside `/api/structured-review`.
Session boundary after: yes
Acceptance Criteria: WF-0072 captures one passing ERC happy-path row and one failing-closed stage-mismatch row for `erc_stg_2026_full`; the mismatch row proves the exact offending stage input is blocked at the exercised seam and pairs that block with explicit no-review-creation / no-execution / no-persistence assertions.
TDD Plan:
- RED: Extend `backend/tests/test_erc_structured_review_e2e.py` with WF-0072 assertions for one happy-path row and one stage-mismatch zero-side-effect row; run before the new evidence artifact and matrix rows exist.
- GREEN: Add the minimal test/evidence plumbing in `docs/walkthroughs/evidence/WF-0072/erc_stg_2026_full_proofs.json` and append the two ERC rows to the matrix.
- REFACTOR: Consolidate duplicated stage-mismatch assertion helpers with any WF-0070 helpers while keeping WF-0072 evidence references separate.
Verification Steps: `cd backend && uv run pytest tests/test_erc_structured_review_e2e.py -k "wf0072 or fr14" -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row erc_stg_2026_full:happy_path --require-row erc_stg_2026_full:stage_mismatch`
Risks (if any): ERC already carries hidden trust debt around stage scope, so a weak proof here can regress into “error seen later” rather than true fail-closed enforcement.

### [ ] Task 4 — Prove the representative MSCA happy path without reopening hierarchical scope
Goal: Add one deterministic happy-path proof for `MSCA-PF-2025` using the existing structured-review seam, while preserving the already-closed hierarchical scope boundaries from earlier WFs.
Slice: representative-happy-path
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR6, FR7, FR9
Depends on: Task 1
Enables: Task 8
Parallelizable: no
Files to modify:
Must touch files: `backend/tests/test_wf_0072_msca_happy_path.py`, `docs/walkthroughs/evidence/WF-0072/msca_pf_2025_happy_path.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Reworking supporting-node visibility, broad MSCA onboarding changes, protected browser submit proof.
Stop if: Producing an honest MSCA happy-path proof would require reopening WF-0063/WF-0064 behavior outside the representative trust-claim seam, or if the family’s real user path is protected and implementation attempts to count an API-only proof as the end-to-end claim without an explicit scope note and blocker.
Session boundary after: no
Acceptance Criteria: `MSCA-PF-2025` has one passing happy-path matrix row backed by deterministic evidence that explicitly states whether the proof is browser/BFF plus backend paired evidence or a narrower API-scoped claim; implementation-ready closure remains blocked if the family’s real user path is protected and no protected proof exists.
TDD Plan:
- RED: Add `backend/tests/test_wf_0072_msca_happy_path.py` that expects a replayable MSCA happy-path artifact and matching matrix row; run before the evidence artifact exists.
- GREEN: Implement the minimal proof harness and author `docs/walkthroughs/evidence/WF-0072/msca_pf_2025_happy_path.json`, then append the matrix row.
- REFACTOR: Reuse any existing representative client factories from `backend/tests/test_api.py` rather than duplicating per-call setup.
Verification Steps: `cd backend && uv run pytest tests/test_wf_0072_msca_happy_path.py -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row MSCA-PF-2025:happy_path --require-scope-note`
Risks (if any): MSCA is the easiest place to accidentally smuggle in prior compatibility assumptions as “proof”; this task must stay anchored to one explicit exercised seam.

### [ ] Task 5 — Prove missing mandatory input blocks on the protected submit path in `AUTH_MODE=test_bypass`
Goal: Exercise the real protected submit path through `/app` and `/api/bff/structured-review` and prove that omitting a mandatory input blocks before the review-creation boundary in the local deterministic auth lane.
Slice: protected-surface fail-closed
User Stories: US2, US3, US4
PRD Requirements: FR4, FR6, FR7, FR8, FR12
Depends on: Task 1
Enables: Task 6, Task 8
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-protected-submit.spec.ts`, `docs/walkthroughs/evidence/WF-0072/protected-submit-test-bypass.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Clerk credential flow, policy-blocking, unrelated submit-form UX polish.
Stop if: The protected submit path cannot be exercised locally under `AUTH_MODE=test_bypass` without bypassing `/app` or `/api/bff/structured-review` entirely.
Session boundary after: yes
Acceptance Criteria: A browser-driven proof under `AUTH_MODE=test_bypass` reaches the protected submit surface, omits a mandatory field, shows researcher-visible blocking, proves the submit seam did not cross into review creation, and writes a matrix row that names both the exercised protected boundary and the auth lane.
TDD Plan:
- RED: Add a failing Playwright case in `frontend/e2e/wf-0072-protected-submit.spec.ts` asserting missing mandatory input blocks before the submit request or review creation side effect; run it under `AUTH_MODE=test_bypass`.
- GREEN: Add the minimum evidence capture/output logic to record the deterministic browser proof in `docs/walkthroughs/evidence/WF-0072/protected-submit-test-bypass.json` and append the matching matrix row.
- REFACTOR: Share selectors or helper setup with existing auth-flow smoke tests only if it reduces drift without obscuring the exact exercised submit seam.
Verification Steps: `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-protected-submit.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row protected_submit:missing_mandatory_input:test_bypass`
Risks (if any): Browser-visible validation can still be dishonest if the submit request fires underneath; this task must treat hidden network invocation as a failure.

### [ ] Task 6 — Add the second auth lane for the protected submit proof or fail closed with an explicit skip reason
Goal: Satisfy the dual auth-lane requirement for every protected WF-0072 proof row, starting with the protected submit scenario, by running the same proof under Clerk-backed auth or by recording a concrete blocked-lane reason if Clerk cannot be exercised honestly in local verification.
Slice: protected-surface auth-lane parity
User Stories: US3, US4
PRD Requirements: FR6, FR7, FR8, FR12
Depends on: Task 5
Enables: Task 8
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-protected-submit.spec.ts`, `docs/walkthroughs/evidence/WF-0072/protected-submit-clerk.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New auth-system design, replacing Clerk with test-only mocks, unrelated protected routes.
Stop if: Clerk-mode proof would require storing live credentials in repo or bypassing the protected `/app`/`/api/bff/*` surface; in that case, record an explicit skip row and stop rather than faking parity.
Session boundary after: yes
Acceptance Criteria: Every WF-0072 matrix row that touches `/app` or `/api/bff/*` is represented in both `test_bypass` and `clerk` lanes, or the matrix records one explicit skipped-lane row with a concrete reason tied to the same proof item; unlabeled omission is impossible.
TDD Plan:
- RED: Extend `frontend/e2e/wf-0072-protected-submit.spec.ts` and the bundle validator expectations so a missing Clerk lane or skip reason fails the WF-0072 contract.
- GREEN: Add the Clerk-lane proof or explicit skip artifact in `docs/walkthroughs/evidence/WF-0072/protected-submit-clerk.json` and update the matrix accordingly.
- REFACTOR: Factor lane-specific setup into small helpers only if the proof still exposes the exact lane and boundary in the evidence metadata.
Verification Steps: `cd frontend && AUTH_MODE=clerk npx playwright test e2e/wf-0072-protected-submit.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes`
Risks (if any): This is the highest place for fake confidence because a single bypass-only proof can look “complete” unless the validator treats the second lane as mandatory or explicitly skipped.

### [ ] Task 7 — Prove policy-blocking remains zero-side-effect on a representative path
Goal: Add the required policy-blocking proof for the locked wedge, anchored to the existing API-boundary gates (`QUOTA_EXCEEDED` / `REVIEWS_DISABLED`) and explicit downstream non-invocation evidence with zero side effects.
Slice: fail-closed-policy-block
User Stories: US2, US3
PRD Requirements: FR5, FR6, FR7, FR12
Depends on: Task 1
Enables: Task 8
Parallelizable: no
Files to modify:
Must touch files: `backend/tests/test_api.py`, `docs/walkthroughs/evidence/WF-0072/policy_blocking.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New policy gates, service-entry refactors, non-representative calls, browser-only proof that omits backend side-effect assertions.
Stop if: The existing API-boundary gates cannot be proven on any representative path without inventing a new gate location or weakening the zero-side-effect assertion.
Session boundary after: no
Acceptance Criteria: At least one `nwo_veni_2025_preproposal` row proves a policy-blocking response (`QUOTA_EXCEEDED` or `REVIEWS_DISABLED`) on the exercised path and pairs that visible block with explicit zero review creation, zero pipeline execution, and zero partial persistence evidence; the scenario is marked `pass` only if both halves of the claim are present, and any future alternate representative would require an explicit task-plan revision.
TDD Plan:
- RED: Extend `backend/tests/test_api.py` with a representative-call policy-blocking case that expects paired user-visible error semantics and downstream non-invocation evidence; run before the WF-0072 evidence artifact and row exist.
- GREEN: Add the minimal proof artifact in `docs/walkthroughs/evidence/WF-0072/policy_blocking.json` and append the matching matrix row.
- REFACTOR: Reuse existing real-call client factories for `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, or `MSCA-PF-2025` instead of the generic synthetic helper path.
Verification Steps: `cd backend && uv run pytest tests/test_api.py -k "wf0072 and (quota or reviews_disabled)" -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row nwo_veni_2025_preproposal:policy_blocking`
Risks (if any): Existing policy tests already risk over-claiming through synthetic fixtures, so this task must stay on a representative path or explicitly mark scope narrower.

### [ ] Task 8 — Close WF-0072 with matrix completion, baseline scope proof, and audit disposition
Goal: Finalize the WF-0072 closure artifact so implementation readiness depends on the completed verification matrix, a baseline-SHA or commit-range scope proof, and an audit-disposition ledger that closes all justified findings.
Slice: closure-evidence
User Stories: US1, US2, US3, US4
PRD Requirements: FR6, FR7, FR8, FR10, FR11, FR12
Depends on: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
Enables: none
Parallelizable: no
Files to modify:
Must touch files: `docs/walkthroughs/walkthrough-WF-0072-e2e-trust-proof-nwo-erc-msca.md`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New proof scenarios, reopening implementation seams already covered by prior tasks, vague ship language without explicit pass/fail evidence.
Stop if: Any required representative or failure-class row is still missing, any protected-surface lane is omitted without a concrete skip reason, or the scope proof / audit ledger cannot be tied to exact commits and evidence references.
Session boundary after: yes
Acceptance Criteria: The walkthrough records the final matrix status, the exact baseline SHA or commit range for the verification claim, and an audit-disposition ledger covering every blocking and justified non-blocking finding; readiness remains blocked if any matrix row is failing, skipped without rationale, or unbacked by deterministic replay metadata.
TDD Plan:
- RED: Extend the WF-0072 bundle validator or a focused closure assertion to fail when baseline scope proof, audit disposition, or any mandatory matrix row is missing from the final artifact set.
- GREEN: Complete the walkthrough and matrix references so the closure checks pass and the artifact can honestly recommend or block proceed.
- REFACTOR: Keep closure evidence centralized in the walkthrough instead of scattering recommendation state across multiple docs.
Verification Steps: `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-closure`; `rg -n "baseline sha|commit range|audit-disposition|WF-0072" docs/walkthroughs/walkthrough-WF-0072-e2e-trust-proof-nwo-erc-msca.md`
Risks (if any): Without an explicit closure task, later phases can mark the WF ready while still hiding skipped rows or unresolved review findings.

## Changelog

- v0.1 (2026-03-10): Initial task breakdown from PRD
- v0.2 (2026-03-10): Applied Phase 2.2 review edits to tighten real-user-path scope, protected auth-lane coverage, and representative-specific policy-blocking verification; marked Ready for Implementation
