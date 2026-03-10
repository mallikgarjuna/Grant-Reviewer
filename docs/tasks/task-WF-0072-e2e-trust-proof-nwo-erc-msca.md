<!-- docs/tasks/task-WF-0072-e2e-trust-proof-nwo-erc-msca.md -->
# WF-0072 — E2E Trust Proof for Representative NWO/ERC/MSCA Flows

Artifact: task
Version: v0.4
Status: Ready for Implementation
Last Updated: 2026-03-10

## Task Breakdown (Sequential Order)

### [x] Task 1 — Author the WF-0072 verification-matrix contract and tracer-bullet validator
Goal: Establish one canonical WF-0072 verification bundle contract that enforces the locked representative set, required row fields, valid proof-surface enum values, `scenario_scope_note`, deterministic `evidence_ref` replay metadata, explicit automated-vs-manual lane labeling, conditional auth-lane reporting, paired negative-case semantics, and closure-artifact references. Seed it with one passing NWO happy-path tracer-bullet row so later scenario work extends a stable proof object instead of inventing incompatible artifacts.
Slice: tracer-bullet / evidence-contract
User Stories: US1, US3, US4
PRD Requirements: FR1, FR6, FR7, FR8, FR10, FR11, FR12
Depends on: none
Enables: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `backend/scripts/validate_wf_0072_bundle.py`, `backend/tests/test_wf_0072_bundle_contract.py`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Scenario-specific proof execution, walkthrough prose, unrelated evidence frameworks.
Stop if: The existing repo cannot support one matrix artifact that records row-level seam labels, auth lanes, deterministic replay metadata, and closure-artifact references without introducing a second competing proof format.
Session boundary after: no
Acceptance Criteria: The validator fails closed if a row uses an unlocked representative call, omits any required row field including `scenario_scope_note`, uses a proof surface outside `browser`/`API`/`paired`, leaves replay metadata incomplete, leaves automated/manual lane state implicit, records a negative case without the paired visible-block plus no-side-effect claim, claims a protected `/app` or `/api/bff/*` seam without dual-lane or skip metadata, or marks a row pass/fail without a concrete `evidence_ref`; the seed matrix contains exactly one NWO happy-path tracer row plus placeholders for baseline-scope and audit-disposition references.
TDD Plan:
- RED: Add `backend/tests/test_wf_0072_bundle_contract.py` covering locked representative-set enforcement, required row fields including `scenario_scope_note`, proof-surface enum enforcement, deterministic replay metadata, automated/manual lane labeling, paired negative-case validation, and protected-surface auth-lane validation; run it against an incomplete seed matrix and watch it fail.
- GREEN: Implement `backend/scripts/validate_wf_0072_bundle.py` and author the initial `docs/walkthroughs/evidence/WF-0072/verification-matrix.json` structure so the contract test passes.
- REFACTOR: Normalize field names and error messages so later tasks can append rows without bespoke translation.
Verification Steps: `cd backend && uv run pytest tests/test_wf_0072_bundle_contract.py -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
Risks (if any): If the matrix contract is under-specified here, later proof tasks will drift into incompatible artifacts and the closure task will become manual reconciliation work.

### [x] Task 2 — Prove the representative NWO happy path on the protected submit path in `AUTH_MODE=test_bypass`
Goal: Land one deterministic happy-path proof for `nwo_veni_2025_preproposal` through its actual protected user path (`/app` -> `/api/bff/structured-review`) in `AUTH_MODE=test_bypass`, paired with exact backend-side effect evidence, and record the result as one matrix row with exact replay metadata.
Slice: tracer-bullet / representative-happy-path
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR6, FR7, FR9
Depends on: Task 1
Enables: Task 3, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-nwo-happy-path.spec.ts`, `docs/walkthroughs/evidence/WF-0072/nwo_veni_2025_preproposal_happy_path_test_bypass.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Policy-blocking negatives, widening NWO coverage beyond `nwo_veni_2025_preproposal`, generic submit-form redesign.
Stop if: The claimed NWO happy path cannot be exercised on `/app` -> `/api/bff/structured-review` honestly; do not relabel an API-only proof as end-to-end. If the real user path proves different from the planned protected seam, stop and revise the task plan before implementation rather than silently downgrading the claim.
Session boundary after: no
Acceptance Criteria: A dedicated automated proof for `nwo_veni_2025_preproposal` passes through `/app` -> `/api/bff/structured-review` in `AUTH_MODE=test_bypass`, reaches the real protected submit surface, persists or returns the expected review payload without scope drift, captures the exercised network boundary plus the resulting review detail or persistence side effect, and appends one `pass` matrix row naming `proof_surface=paired`, auth lane `test_bypass`, the exact entrypoint boundary, side-effect assertion, result, and evidence reference with exact command/test ID and assertion metadata.
TDD Plan:
- RED: Add `frontend/e2e/wf-0072-nwo-happy-path.spec.ts` that expects a replayable protected-surface happy-path artifact and matching matrix row for `nwo_veni_2025_preproposal` in `AUTH_MODE=test_bypass`; run it before the evidence file and row exist.
- GREEN: Implement the minimal proof harness and write `docs/walkthroughs/evidence/WF-0072/nwo_veni_2025_preproposal_happy_path_test_bypass.json`, then append the matching matrix row.
- REFACTOR: Remove duplicated assertion metadata between the browser evidence artifact and matrix row if a single canonical payload can supply both.
Verification Steps: `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-nwo-happy-path.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row nwo_veni_2025_preproposal:happy_path:test_bypass --require-real-user-path`
Risks (if any): If this proof quietly uses a lower-level seam than `/app` -> `/api/bff/structured-review`, the whole WF will overstate launch trust.

### [x] Task 3 — Add the second auth lane for the protected NWO happy path or fail closed with an explicit skip reason
Goal: Satisfy the auth-lane parity requirement for the protected NWO happy-path proof by running the same `/app` -> `/api/bff/structured-review` scenario under Clerk-backed auth or by recording a concrete blocked-lane reason if Clerk cannot be exercised honestly in local verification.
Slice: protected-surface auth-lane parity
User Stories: US3, US4
PRD Requirements: FR6, FR7, FR8, FR9, FR12
Depends on: Task 2
Enables: Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-nwo-happy-path.spec.ts`, `docs/walkthroughs/evidence/WF-0072/nwo_veni_2025_preproposal_happy_path_clerk.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New auth-system design, replacing Clerk with test-only mocks, unrelated protected routes.
Stop if: Clerk-mode proof would require storing live credentials in repo or bypassing the protected `/app`/`/api/bff/*` surface; in that case, record an explicit skip row and stop rather than faking parity.
Session boundary after: yes
Acceptance Criteria: Every protected NWO happy-path row touching `/app` or `/api/bff/structured-review` is represented in both `test_bypass` and `clerk` lanes, or the matrix records one explicit skipped-lane row with a concrete reason tied to the same proof item; unlabeled omission is impossible.
TDD Plan:
- RED: Extend `frontend/e2e/wf-0072-nwo-happy-path.spec.ts` and the bundle validator expectations so a missing Clerk lane or skip reason fails the WF-0072 contract.
- GREEN: Add the Clerk-lane proof or explicit skip artifact in `docs/walkthroughs/evidence/WF-0072/nwo_veni_2025_preproposal_happy_path_clerk.json` and update the matrix accordingly.
- REFACTOR: Factor lane-specific setup into small helpers only if the proof still exposes the exact lane and boundary in the evidence metadata.
Verification Steps: `cd frontend && AUTH_MODE=clerk npx playwright test e2e/wf-0072-nwo-happy-path.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes --require-row nwo_veni_2025_preproposal:happy_path`
Risks (if any): This is the highest place for fake confidence because a single bypass-only proof can look complete unless the validator treats the second lane as mandatory or explicitly skipped.

### [x] Task 4 — Prove ERC happy path and fail-closed stage mismatch on the canonical ERC seam
Goal: Extend the existing ERC structured-review end-to-end seam so WF-0072 has both a representative `erc_stg_2026_full` happy-path proof and the required stage-mismatch negative proof with explicit zero-side-effect evidence.
Slice: representative-happy-path / fail-closed-stage-mismatch
User Stories: US1, US2, US3
PRD Requirements: FR1, FR2, FR3, FR6, FR7, FR12
Depends on: Task 1
Enables: Task 13
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

### [x] Task 5 — Prove the representative MSCA happy path on the protected submit path in `AUTH_MODE=test_bypass`
Goal: Add one deterministic happy-path proof for `MSCA-PF-2025` through its actual protected user path (`/app` -> `/api/bff/structured-review`) in `AUTH_MODE=test_bypass`, while preserving the already-closed hierarchical scope boundaries from earlier WFs and pairing the browser/BFF proof with exact backend-side effect evidence.
Slice: representative-happy-path
User Stories: US1, US3
PRD Requirements: FR1, FR2, FR6, FR7, FR9
Depends on: Task 1
Enables: Task 6, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-msca-happy-path.spec.ts`, `docs/walkthroughs/evidence/WF-0072/msca_pf_2025_happy_path_test_bypass.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Reworking supporting-node visibility, broad MSCA onboarding changes, generic submit-form redesign.
Stop if: Producing an honest MSCA happy-path proof would require reopening WF-0063/WF-0064 behavior outside the representative trust-claim seam, or if the family’s real user path proves different from the planned protected seam; in either case, stop and revise the task plan before implementation rather than silently counting an API-only proof as end-to-end.
Session boundary after: no
Acceptance Criteria: `MSCA-PF-2025` has one passing happy-path matrix row backed by deterministic evidence showing the protected `/app` -> `/api/bff/structured-review` path in `AUTH_MODE=test_bypass`, paired with backend evidence that the expected review payload was created or returned, and the matrix explicitly records `proof_surface=paired`, auth lane `test_bypass`, the exact boundary, and deterministic replay metadata.
TDD Plan:
- RED: Add `frontend/e2e/wf-0072-msca-happy-path.spec.ts` that expects a replayable protected-surface MSCA happy-path artifact and matching matrix row in `AUTH_MODE=test_bypass`; run before the evidence artifact exists.
- GREEN: Implement the minimal proof harness and author `docs/walkthroughs/evidence/WF-0072/msca_pf_2025_happy_path_test_bypass.json`, then append the matrix row.
- REFACTOR: Reuse any existing representative client factories from `backend/tests/test_api.py` rather than duplicating per-call setup.
Verification Steps: `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-msca-happy-path.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row MSCA-PF-2025:happy_path:test_bypass --require-real-user-path`
Risks (if any): MSCA is the easiest place to accidentally smuggle in prior compatibility assumptions as proof; this task must stay anchored to the exact protected seam actually exercised.

### [x] Task 6 — Add the second auth lane for the protected MSCA happy path or fail closed with an explicit skip reason
Goal: Satisfy the auth-lane parity requirement for the protected MSCA happy-path proof by running the same `/app` -> `/api/bff/structured-review` scenario under Clerk-backed auth or by recording a concrete blocked-lane reason if Clerk cannot be exercised honestly in local verification.
Slice: protected-surface auth-lane parity
User Stories: US3, US4
PRD Requirements: FR6, FR7, FR8, FR9, FR12
Depends on: Task 5
Enables: Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-msca-happy-path.spec.ts`, `docs/walkthroughs/evidence/WF-0072/msca_pf_2025_happy_path_clerk.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New auth-system design, replacing Clerk with test-only mocks, unrelated protected routes.
Stop if: Clerk-mode proof would require storing live credentials in repo or bypassing the protected `/app`/`/api/bff/*` surface; in that case, record an explicit skip row and stop rather than faking parity.
Session boundary after: yes
Acceptance Criteria: Every protected MSCA happy-path row touching `/app` or `/api/bff/structured-review` is represented in both `test_bypass` and `clerk` lanes, or the matrix records one explicit skipped-lane row with a concrete reason tied to the same proof item; unlabeled omission is impossible.
TDD Plan:
- RED: Extend `frontend/e2e/wf-0072-msca-happy-path.spec.ts` and the bundle validator expectations so a missing Clerk lane or skip reason fails the WF-0072 contract.
- GREEN: Add the Clerk-lane proof or explicit skip artifact in `docs/walkthroughs/evidence/WF-0072/msca_pf_2025_happy_path_clerk.json` and update the matrix accordingly.
- REFACTOR: Factor lane-specific setup into small helpers only if the proof still exposes the exact lane and boundary in the evidence metadata.
Verification Steps: `cd frontend && AUTH_MODE=clerk npx playwright test e2e/wf-0072-msca-happy-path.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes --require-row MSCA-PF-2025:happy_path`
Risks (if any): A single bypass-only MSCA proof can look complete unless the validator treats the second lane as mandatory or explicitly skipped.

### [x] Task 7 — Prove missing `key_outputs` blocks on the representative NWO protected submit path in `AUTH_MODE=test_bypass`
Goal: Exercise the real protected NWO submit path through `/app` and `/api/bff/structured-review` and prove that omitting the representative mandatory NWO primary input `key_outputs` blocks before the review-creation boundary in the local deterministic auth lane.
Slice: protected-surface fail-closed
User Stories: US2, US3, US4
PRD Requirements: FR4, FR6, FR7, FR8, FR12
Depends on: Task 1
Enables: Task 8, Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-protected-submit.spec.ts`, `docs/walkthroughs/evidence/WF-0072/protected-submit-missing-key-outputs-test-bypass.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Clerk credential flow, policy-blocking, unrelated submit-form UX polish.
Stop if: The protected submit path cannot be exercised locally under `AUTH_MODE=test_bypass` without bypassing `/app` or `/api/bff/structured-review` entirely.
Session boundary after: yes
Acceptance Criteria: A browser-driven proof under `AUTH_MODE=test_bypass` reaches the protected NWO submit surface, omits `key_outputs`, shows researcher-visible blocking tied to the NWO representative contract, proves the submit seam did not cross into review creation, and writes a matrix row that names both the exercised protected boundary and the auth lane.
TDD Plan:
- RED: Add a failing Playwright case in `frontend/e2e/wf-0072-protected-submit.spec.ts` asserting that omitting NWO `key_outputs` blocks before the submit request or review creation side effect; run it under `AUTH_MODE=test_bypass`.
- GREEN: Add the minimum evidence capture/output logic to record the deterministic browser proof in `docs/walkthroughs/evidence/WF-0072/protected-submit-missing-key-outputs-test-bypass.json` and append the matching matrix row.
- REFACTOR: Share selectors or helper setup with existing auth-flow smoke tests only if it reduces drift without obscuring the exact exercised submit seam.
Verification Steps: `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-protected-submit.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row nwo_veni_2025_preproposal:missing_key_outputs:test_bypass`
Risks (if any): Browser-visible validation can still be dishonest if the submit request fires underneath; this task must treat hidden network invocation as a failure.

### [x] Task 8 — Add the second auth lane for the protected missing-`key_outputs` proof or fail closed with an explicit skip reason
Goal: Satisfy the auth-lane parity requirement for the protected NWO missing-`key_outputs` fail-closed proof by running the same `/app` -> `/api/bff/structured-review` scenario under Clerk-backed auth or by recording a concrete blocked-lane reason if Clerk cannot be exercised honestly in local verification.
Slice: protected-surface auth-lane parity
User Stories: US3, US4
PRD Requirements: FR6, FR7, FR8, FR12
Depends on: Task 7
Enables: Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-protected-submit.spec.ts`, `docs/walkthroughs/evidence/WF-0072/protected-submit-missing-key-outputs-clerk.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New auth-system design, replacing Clerk with test-only mocks, unrelated protected routes.
Stop if: Clerk-mode proof would require storing live credentials in repo or bypassing the protected `/app`/`/api/bff/*` surface; in that case, record an explicit skip row and stop rather than faking parity.
Session boundary after: yes
Acceptance Criteria: The protected `nwo_veni_2025_preproposal:missing_key_outputs` proof item is represented in both `test_bypass` and `clerk` lanes, or the matrix records one explicit skipped-lane row with a concrete reason tied to the same proof item; unlabeled omission is impossible.
TDD Plan:
- RED: Extend `frontend/e2e/wf-0072-protected-submit.spec.ts` and the bundle validator expectations so a missing Clerk lane or skip reason for `nwo_veni_2025_preproposal:missing_key_outputs` fails the WF-0072 contract.
- GREEN: Add the Clerk-lane proof or explicit skip artifact in `docs/walkthroughs/evidence/WF-0072/protected-submit-missing-key-outputs-clerk.json` and update the matrix accordingly.
- REFACTOR: Factor lane-specific setup into small helpers only if the proof still exposes the exact lane and boundary in the evidence metadata.
Verification Steps: `cd frontend && AUTH_MODE=clerk npx playwright test e2e/wf-0072-protected-submit.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes --require-row nwo_veni_2025_preproposal:missing_key_outputs`
Risks (if any): A single bypass-only negative proof can look complete unless the validator treats the second lane as mandatory or explicitly skipped.

### [x] Task 9 — Prove policy-blocking is visibly blocked on the representative NWO protected path
Goal: Add the required user-surface half of the policy-blocking proof for the locked wedge on the representative NWO protected path, showing that `QUOTA_EXCEEDED` or `REVIEWS_DISABLED` is researcher-visible on `/app` -> `/api/bff/structured-review` rather than only asserted at a lower-level API seam.
Slice: fail-closed-policy-block / user-surface
User Stories: US2, US3
PRD Requirements: FR5, FR6, FR7, FR12
Depends on: Task 1
Enables: Task 10, Task 11, Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-policy-blocking.spec.ts`, `docs/walkthroughs/evidence/WF-0072/policy_blocking.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New policy gates, service-entry refactors, non-representative calls, backend non-invocation assertions.
Stop if: The existing policy gates cannot be shown honestly on the NWO protected user path without bypassing `/app` or `/api/bff/structured-review`.
Session boundary after: no
Acceptance Criteria: At least one `nwo_veni_2025_preproposal` row records a policy-blocking response (`QUOTA_EXCEEDED` or `REVIEWS_DISABLED`) on the exercised `/app` -> `/api/bff/structured-review` path, captures the exact researcher-visible blocking semantics, and records the row as the user-surface half of a paired policy claim that is not closable until Task 11 supplies the zero-side-effect backend evidence.
TDD Plan:
- RED: Add a failing Playwright case in `frontend/e2e/wf-0072-policy-blocking.spec.ts` that expects researcher-visible policy blocking on the protected NWO path and a matching matrix row.
- GREEN: Add the minimum user-surface proof artifact in `docs/walkthroughs/evidence/WF-0072/policy_blocking.json` and append the matching matrix row.
- REFACTOR: Reuse existing representative-path helpers for `nwo_veni_2025_preproposal` rather than introducing a generic synthetic policy harness.
Verification Steps: `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-policy-blocking.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row nwo_veni_2025_preproposal:policy_blocking:user_surface`
Risks (if any): Visible blocking alone is insufficient for closure; if Task 11 never lands, this row must remain explicitly non-closing.

### [x] Task 10 — Add the second auth lane for the protected policy-blocking user-surface proof or fail closed with an explicit skip reason
Goal: Satisfy the auth-lane parity requirement for the protected NWO policy-blocking user-surface proof by running the same `/app` -> `/api/bff/structured-review` scenario under Clerk-backed auth or by recording a concrete blocked-lane reason if Clerk cannot be exercised honestly in local verification.
Slice: protected-surface auth-lane parity
User Stories: US3, US4
PRD Requirements: FR6, FR7, FR8, FR12
Depends on: Task 9
Enables: Task 11, Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `frontend/e2e/wf-0072-policy-blocking.spec.ts`, `docs/walkthroughs/evidence/WF-0072/policy_blocking_clerk.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New auth-system design, replacing Clerk with test-only mocks, unrelated protected routes.
Stop if: Clerk-mode proof would require storing live credentials in repo or bypassing the protected `/app`/`/api/bff/*` surface; in that case, record an explicit skip row and stop rather than faking parity.
Session boundary after: yes
Acceptance Criteria: The protected `nwo_veni_2025_preproposal:policy_blocking:user_surface` proof item is represented in both `test_bypass` and `clerk` lanes, or the matrix records one explicit skipped-lane row with a concrete reason tied to the same proof item; unlabeled omission is impossible.
TDD Plan:
- RED: Extend `frontend/e2e/wf-0072-policy-blocking.spec.ts` and the bundle validator expectations so a missing Clerk lane or skip reason for `nwo_veni_2025_preproposal:policy_blocking:user_surface` fails the WF-0072 contract.
- GREEN: Add the Clerk-lane proof or explicit skip artifact in `docs/walkthroughs/evidence/WF-0072/policy_blocking_clerk.json` and update the matrix accordingly.
- REFACTOR: Factor lane-specific setup into small helpers only if the proof still exposes the exact lane and boundary in the evidence metadata.
Verification Steps: `cd frontend && AUTH_MODE=clerk npx playwright test e2e/wf-0072-policy-blocking.spec.ts --project=chromium`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes --require-row nwo_veni_2025_preproposal:policy_blocking:user_surface`
Risks (if any): A single bypass-only protected policy row can look complete unless the validator treats the second lane as mandatory or explicitly skipped.

### [ ] Task 11 — Prove policy-blocking remains zero-side-effect on the representative NWO backend path
Goal: Add the backend half of the representative NWO policy-blocking proof, anchored to the existing API-boundary gates (`QUOTA_EXCEEDED` / `REVIEWS_DISABLED`), and prove explicit downstream non-invocation with zero side effects so the paired policy claim can close honestly.
Slice: fail-closed-policy-block / backend-zero-side-effect
User Stories: US2, US3
PRD Requirements: FR5, FR6, FR7, FR12
Depends on: Task 9, Task 10
Enables: Task 12, Task 13
Parallelizable: no
Files to modify:
Must touch files: `backend/tests/test_api.py`, `docs/walkthroughs/evidence/WF-0072/policy_blocking.json`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: New policy gates, service-entry refactors, non-representative calls, user-surface browser blocking.
Stop if: The existing API-boundary gates cannot be proven on the representative NWO path without inventing a new gate location or weakening the zero-side-effect assertion.
Session boundary after: no
Acceptance Criteria: The `nwo_veni_2025_preproposal` policy-blocking row is only marked `pass` once it pairs the Task 9 user-surface block with explicit zero review creation, zero pipeline execution, and zero partial persistence evidence from the existing backend gate seam; any narrower API-only proof must stay explicitly non-closing.
TDD Plan:
- RED: Extend `backend/tests/test_api.py` with a representative-call policy-blocking case that expects downstream non-invocation evidence paired to the Task 9 user-surface claim; run before the WF-0072 evidence artifact and final row exist.
- GREEN: Add the backend zero-side-effect proof details to `docs/walkthroughs/evidence/WF-0072/policy_blocking.json` and update the matching matrix row to a closable paired claim.
- REFACTOR: Reuse existing real-call client factories for `nwo_veni_2025_preproposal` instead of the generic synthetic helper path.
Verification Steps: `cd backend && ./scripts/reset_test_db.sh && DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0072 and (quota or reviews_disabled)" -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-row nwo_veni_2025_preproposal:policy_blocking`
Risks (if any): Existing policy tests already risk over-claiming through synthetic fixtures, so this task must stay on the representative NWO backend path or explicitly mark scope narrower.

### [ ] Task 12 — Extend the WF-0072 closure validator for final protected-row parity and closure artifacts
Goal: Tighten the WF-0072 bundle validator so final closure fails if any protected proof row lacks required auth-lane parity or explicit skip rationale, or if baseline-scope / audit-disposition artifacts are missing from the final bundle.
Slice: closure-contract
User Stories: US1, US3, US4
PRD Requirements: FR6, FR7, FR8, FR10, FR11, FR12
Depends on: Task 8, Task 10, Task 11
Enables: Task 13
Parallelizable: no
Files to modify:
Must touch files: `backend/scripts/validate_wf_0072_bundle.py`, `backend/tests/test_wf_0072_bundle_contract.py`, `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`
May touch files: none
Out of scope: Walkthrough prose, new proof scenarios, broad validator generalization outside WF-0072.
Stop if: The existing validator cannot express final protected-row parity or closure-artifact checks without introducing a second competing proof contract.
Session boundary after: no
Acceptance Criteria: The validator fails closed when any protected WF-0072 row lacks `test_bypass` plus `clerk` coverage or an explicit skip rationale tied to the same proof item, or when baseline scope proof / audit disposition references are missing from the final bundle.
TDD Plan:
- RED: Extend `backend/tests/test_wf_0072_bundle_contract.py` with closure assertions proving the final bundle fails when protected-row parity or closure-artifact references are missing; run before the validator changes land.
- GREEN: Implement the minimal validator updates in `backend/scripts/validate_wf_0072_bundle.py` and matrix contract scaffolding so the new closure assertions pass.
- REFACTOR: Keep protected-row parity and closure-artifact enforcement in one validator path so walkthrough prose is not carrying hidden gate logic.
Verification Steps: `cd backend && uv run pytest tests/test_wf_0072_bundle_contract.py -k "wf0072 and closure" -v`; `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes --require-closure`
Risks (if any): If final parity and closure checks stay implicit, Phase 3 can claim readiness with green scenario tests but a structurally non-closing bundle.

### [ ] Task 13 — Close WF-0072 with matrix completion, baseline scope proof, and audit disposition
Goal: Finalize the WF-0072 closure artifact so implementation readiness depends on the completed verification matrix, a baseline-SHA or commit-range scope proof, and an audit-disposition ledger that closes all justified findings.
Slice: closure-evidence
User Stories: US1, US2, US3, US4
PRD Requirements: FR6, FR7, FR8, FR10, FR11, FR12
Depends on: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12
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
- RED: Run the final closure gate against an incomplete walkthrough or matrix and confirm `--require-closure` fails before the closure artifact is finished.
- GREEN: Complete the walkthrough and matrix references so the existing closure checks pass and the artifact can honestly recommend or block proceed.
- REFACTOR: Keep closure evidence centralized in the walkthrough instead of scattering recommendation state across multiple docs.
Verification Steps: `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes --require-closure`; `rg -n "baseline sha|commit range|audit-disposition|WF-0072" docs/walkthroughs/walkthrough-WF-0072-e2e-trust-proof-nwo-erc-msca.md`
Risks (if any): Without an explicit closure task, later phases can mark the WF ready while still hiding skipped rows or unresolved review findings.

## Changelog

- v0.1 (2026-03-10): Initial task breakdown from PRD
- v0.2 (2026-03-10): Applied Phase 2.2 review edits to tighten real-user-path scope, protected auth-lane coverage, and representative-specific policy-blocking verification; marked Ready for Implementation
- v0.3 (2026-03-10): Applied adversarial hardening edits to require protected-surface NWO/MSCA happy-path closure, lock the NWO missing-input case to `key_outputs`, require paired user-surface policy blocking, and strengthen the matrix validator contract
- v0.4 (2026-03-10): Closed adversarial review findings by adding protected negative-case auth parity tasks, separating closure-validator work from walkthrough closure, and making final closure depend on explicit protected-lane and artifact checks
