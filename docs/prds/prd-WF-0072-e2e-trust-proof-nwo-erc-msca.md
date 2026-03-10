<!-- docs/prds/prd-WF-0072-e2e-trust-proof-nwo-erc-msca.md -->
# WF-0072 — E2E Trust Proof for Representative NWO/ERC/MSCA Flows

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-10

Type: feature

## 0. User Stories (MVP)

- US1: As a release owner, I want one deterministic end-to-end happy-path proof for each representative NWO, ERC, and MSCA call, so that launch trust claims are tied to concrete evidence instead of inferred confidence.
- US2: As a release owner, I want the required negative cases to fail closed with explicit zero-side-effect evidence, so that blocked paths cannot still create reviews, trigger pipelines, or partially persist data.
- US3: As a maintainer, I want every trust-proof item recorded in a verification matrix with exact seams and evidence references, so that another maintainer can rerun and audit the claim without guessing.
- US4: As a maintainer verifying protected app or BFF surfaces, I want the auth obligation to be explicit per exercised surface, so that test-bypass proof does not silently substitute for Clerk-backed proof where protected paths matter.

## Deferred Stories (Not in MVP)

- DS1: Add launch-proof coverage for any calls outside `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- DS2: Generalize the verification bundle into a broad regression platform or reusable multi-program certification framework.
- DS3: Add new prompt, extraction, evaluation-quality, or unrelated UX work not required to make the trust proof honest and repeatable.
- DS4: Require live external-credential/manual proof as a primary lane rather than an explicitly separated optional lane.

## 1. In Scope

- Lock the representative proof set to `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`, with same-family substitution allowed only if a documented blocker proves one representative cannot honestly support the trust claim. (US1, US3)
- Define one truly end-to-end happy-path proof per representative family through the real user path, with paired backend evidence where needed to prove the claim honestly. (US1, US2, US3)
- Require explicit fail-closed proof for the three mandatory failure classes: ERC stage mismatch, missing mandatory input, and policy-blocking with zero downstream side effects. (US2, US3)
- Require a verification matrix where each proof item is one row with representative call, scenario, proof surface, exercised boundary, auth lane, side-effect assertion, pass/fail result, and `evidence_ref`. (US3, US4)
- Require conditional dual auth-lane verification when protected `/app` or `/api/bff/*` surfaces are exercised, and require explicit skip reasons if a lane is not run. (US3, US4)
- Require proceed/ship gating artifacts to include a baseline-SHA or commit-range scope proof and an audit-disposition ledger in addition to passing verification rows. (US1, US3)

## 2. Out of Scope

- Broadening proof coverage beyond the three locked representative calls. (DS1)
- Replacing real user-path evidence with API-only proof or selector-only smoke. (DS2)
- Auth-system redesign, generalized environment orchestration, or unrelated BFF/app cleanup. (DS2, DS4)
- New funding-call onboarding, review-quality remediation, or prompt/extraction work. (DS1, DS3)
- Parallel DB-mutating verification or any harness change that weakens determinism and traceability. (DS2)

## 3. User / System Flow

### Happy path

1. A maintainer starts the bounded verification bundle against one of the locked representative calls and records the exact command, environment, and baseline scope being exercised. (US1, US3)
2. The proof enters through the real user path for that representative family, using protected app or BFF seams when they are part of the claim rather than substituting a lower-level shortcut silently. (US1, US4)
3. The exercised entrypoint and downstream trust boundary are captured in the matching verification-matrix row, including whether the proof is browser, API, or paired evidence. (US1, US3)
4. The representative flow completes successfully for `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, or `MSCA-PF-2025`, and the result is recorded with concrete artifacts such as command output, network assertions, screenshots, or logs. (US1, US3)
5. When the proof uses protected `/app` or `/api/bff/*` surfaces, the run covers `AUTH_MODE=test_bypass` and `AUTH_MODE=clerk`, or the skipped lane is explicitly documented with a concrete reason in the same evidence set. (US3, US4)
6. The final evidence bundle maps each happy-path and negative-case claim to a matrix row, plus the baseline scope proof and audit-disposition ledger required for any proceed recommendation. (US1, US3)

### Failure path A — ERC stage mismatch still crosses the execution boundary

1. The proof submits ERC Step 1 vs Step 2 data that intentionally mismatches the allowed stage semantics for `erc_stg_2026_full`. (US2, US3)
2. If the request reaches review creation, pipeline execution, or partial persistence before rejection, the trust claim is invalid even if the user saw an error later. (US2)
3. The workflow remains blocked until the verification row shows researcher-visible blocking and explicit non-invocation / no-persistence evidence tied to the exercised boundary. (US2, US3)

### Failure path B — missing mandatory input blocks late instead of pre-execution

1. The proof omits a mandatory field on a browser-driven or equivalent real user path for one representative flow. (US2, US3)
2. If submit crosses the review-creation boundary and only fails later at the server or runtime layer, the fail-closed claim is not proven. (US2)
3. The workflow remains blocked until the evidence shows submit blocked before execution or persistence, with the verification row naming the protected submit seam that was not invoked. (US2, US3, US4)

### Failure path C — policy-blocking returns an error but still causes side effects

1. The proof triggers a policy gate such as `QUOTA_EXCEEDED` or `REVIEWS_DISABLED` on a representative path. (US2, US3)
2. Visible blocking alone is insufficient if any review row, pipeline run, or partial persistence still occurs downstream. (US2)
3. The workflow remains blocked until the evidence bundle pairs the user-facing block with explicit zero-side-effect assertions at the API/runtime seam. (US2, US3)

## 4. Functional Requirements

- FR1 (US1, US3): The PRD must lock MVP proof coverage to `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`, and Phase 2 must treat any representative substitution as blocking unless a documented same-family blocker justifies it.
- FR2 (US1, US3): The final verification bundle must contain at least one truly end-to-end happy-path proof per representative family, and each proof must exercise the real user path for that family rather than a lower-level substitute presented as equivalent.
- FR3 (US2, US3): The negative-case matrix must include ERC stage mismatch and must prove both researcher-visible blocking and zero downstream side effects for the exact exercised seam.
- FR4 (US2, US3): The negative-case matrix must include missing mandatory input and must prove submit is blocked before crossing the review-creation boundary when browser or protected submit proof is used.
- FR5 (US2, US3): The negative-case matrix must include policy-blocking behavior such as `QUOTA_EXCEEDED` or `REVIEWS_DISABLED` and must prove no review creation, no pipeline execution, and no partial persistence.
- FR6 (US3): Every proof item must map one-to-one to a verification-matrix row containing representative call, scenario, proof surface, auth lane, exercised entrypoint/boundary, side-effect assertion, pass/fail result, `evidence_ref`, and a note stating whether the scenario is proven on the same representative family or intentionally on a different representative for the strongest fail-closed evidence.
- FR7 (US3): No proof row may be marked `pass` or `fail` without a deterministic evidence reference such as command output, API response artifact, recorded network assertion, screenshot, or log.
- FR8 (US4): If any proof item exercises protected `/app` or `/api/bff/*` surfaces, the verification bundle must include both `AUTH_MODE=test_bypass` and `AUTH_MODE=clerk` lanes for that surface, or must mark the skipped lane explicitly with a concrete reason.
- FR9 (US1, US3): The verification bundle must distinguish automated proof from manual confirmation and keep any manual/live lane explicitly separate from the local/test-fixture primary lane.
- FR10 (US1, US3): Any proceed, phase-advance, or ship recommendation for this WF must include a baseline-SHA or explicit commit-range scope proof covering the exact implementation and evidence surface being claimed.
- FR11 (US1, US3): Any proceed, phase-advance, or ship recommendation for this WF must include an audit-disposition ledger that closes every blocking finding and closes or explicitly rejects each justified non-blocking finding with rationale.
- FR12 (US1, US2, US3): Verification must stop and be fixed on failure; no later phase may treat a failing, skipped-without-rationale, or unlabeled verification row as non-blocking.

## 5. Data & API Contracts

- Contract C1 (US2, US3, FR3-FR5): The trust-proof matrix must model negative-case outcomes as paired contracts: the user-facing blocking result and the backend side-effect assertion are one claim, not separate optional checks.
- Contract C2 (US3, FR6, FR7): Each matrix row must carry these fields at minimum: `representative_call`, `scenario`, `proof_surface`, `auth_lane`, `entrypoint_boundary`, `side_effect_assertion`, `result`, `evidence_ref`, and `scenario_scope_note`.
- Contract C3 (US1, US3, FR2, FR9): The proof-surface contract is limited to `browser`, `API`, or `paired`, where `paired` is required whenever browser-visible behavior alone cannot prove the zero-side-effect invariant honestly.
- Contract C4 (US4, FR8): Auth-lane state is conditional metadata, not a hidden assumption. Rows that touch protected app/BFF surfaces must name either `test_bypass`, `clerk`, or an explicit skipped-lane note tied to the same proof item.
- Contract C5 (US1, US3, FR10, FR11): Closure contracts for this WF require two non-test artifacts in addition to matrix results: scope proof (`baseline_sha` or `commit_range`) and audit disposition (`finding_id`, `severity`, `status`, `rationale`).
- Contract C6 (US2, US3, FR3-FR5): Policy-blocking proof must stay anchored to existing API-boundary gates and downstream non-invocation evidence; Phase 2 must not invent a new service-entry contract unless a blocker proves the current boundary cannot support honest verification.

Validation and state transitions:

- `entrypoint_boundary` must use exact seam labels such as `/app`, `/api/bff/structured-review`, `/api/structured-review`, or another exact repo seam if the proof targets a narrower boundary. (US3, FR6, FR7)
- A verification item transitions from `planned` to `pass` or `fail` only when its matrix row contains a concrete `evidence_ref`. (US3, FR6, FR7)
- A skipped auth lane or skipped representative row is blocking unless the recorded reason preserves the locked-wedge trust claim honestly. (US3, US4, FR8, FR12)
- A negative-case run is invalid if it proves only returned semantics without proving the matched no-side-effect assertion. (US2, FR3-FR5)

## 6. Components / Modules

- Verification artifact seam
  - Owns the PRD-defined matrix shape, evidence references, and closure requirements. (FR6-FR12)
- Browser/app or BFF proof seam
  - Owns the real user-path evidence for representative happy paths and browser-visible fail-closed behavior when protected surfaces are exercised. (FR2-FR5, FR8)
- API/runtime proof seam
  - Owns zero-side-effect assertions and non-invocation evidence for blocked paths, especially policy gates and any path where browser proof alone is insufficient. (FR3-FR5, FR12)
- Auth-lane verification seam
  - Owns conditional dual-lane coverage for protected `/app` and `/api/bff/*` surfaces and explicit skip reporting when a lane cannot be run honestly. (FR8)
- Closure-evidence seam
  - Owns baseline scope proof and the audit-disposition ledger required for proceed or ship claims. (FR10, FR11)

Design tree / dependencies / ordering:
1. Freeze the representative proof set and verification-matrix schema before planning individual proof items. (FR1, FR6)
2. Freeze the mandatory negative-case claims and the no-side-effect assertions that must pair with them. (FR3-FR5)
3. Map each representative proof item to the correct user-path seam and only then decide where paired backend evidence is needed. (FR2, FR8, FR9)
4. Add closure artifacts for scope proof and audit disposition so readiness claims cannot overrun the evidence. (FR10-FR12)

Deep module guidance:

- Keep the trust proof evidence-first: if a claim cannot be proven with deterministic artifacts, Phase 2 should narrow or block rather than infer.
- Do not let browser proof and backend proof drift into separate unpaired narratives; one matrix row should represent one claim.
- Reuse existing protected app, BFF, and API boundaries rather than designing a new verification-only path.
- Preserve the locked wedge; representative coverage is breadth enough for MVP.

Suggested file-path clusters (coarse only):

- walkthrough / docs evidence artifacts under `docs/`
- browser or app/BFF proof seams under `frontend/src/app/`
- API-boundary and runtime assertion seams under `backend/`
- automated verification seams under test directories

## 7. Edge Cases

- One representative call becomes unstable because setup or ingest drift breaks the real user path; Phase 2 must document whether to fix setup, substitute within the same family, or stop rather than silently widening scope. (US1, US3, FR1)
- A browser happy-path passes under `AUTH_MODE=test_bypass`, but the same protected surface is never exercised under Clerk and the omission is left implicit; this is blocking. (US4, FR8, FR12)
- Missing mandatory input is shown as a client-side validation error, but network traces or backend state still show the submit boundary fired; this fails the contract. (US2, FR4)
- Policy-blocking is proven only on an API surface even though the claimed user path exercises a protected app/BFF seam; Phase 2 must either pair the browser-visible proof or narrow the claim. (US2, US4, FR5, FR8)
- A verification row claims cross-family coverage by saying a failure case is “covered elsewhere” without naming the representative call and seam used for that row; this is untraceable and blocking. (US3, FR6, FR7)
- Closure evidence relies on passing tests alone without baseline scope proof or audit-disposition closure; proceed remains blocked even if all current tests are green. (US1, US3, FR10-FR12)

## 8. Testing Decisions (TDD)

- This WF is a behavior-hardening and verification workflow. Any implementation changes in Phase 3 must follow RED -> GREEN -> REFACTOR. (US1, US2, US3, US4)
- Public seams under test must include:
  - representative browser/app or BFF entrypoints used for happy-path proof,
  - API-boundary or runtime seams used to prove zero side effects,
  - verification artifact generation or assertion seams that produce the matrix and closure evidence. (US1, US2, US3, US4)
- Mock only external boundaries that are not part of the trust claim itself. Do not mock the exercised entrypoint, fail-closed gate, or downstream side-effect assertion being proven. (US2, US3)
- Minimum required coverage for Phase 3 planning:
  - one happy-path proof per representative family with deterministic evidence refs. (US1, FR1, FR2, FR6, FR7)
  - one ERC stage-mismatch proof showing visible blocking plus zero-side-effect evidence. (US2, FR3, FR6, FR7)
  - one missing-mandatory-input proof showing submit never crossed the review-creation boundary. (US2, FR4, FR6, FR7)
  - one policy-blocking proof showing visible blocking on any exercised user-facing surface plus zero review creation, zero pipeline execution, and zero partial persistence. (US2, FR5, FR6, FR7)
  - matrix validation proving every row uses an exact exercised seam label and records whether the scenario is tied to the same representative family or intentionally demonstrated elsewhere. (US3, FR6, FR7)
  - conditional dual auth-lane coverage for each protected app/BFF surface touched by the proof bundle, with explicit skip handling where necessary. (US4, FR8)
  - closure checks proving the final trust claim includes baseline scope proof and an audit-disposition ledger. (US1, US3, FR10, FR11)

## 8.1 Readiness Gate

- This WF is not ready for Tasks unless the planned verification matrix can cover the three representative happy paths plus the three mandatory failure classes without unlabeled scope drift or substitute seams. (US1, US2, US3)
- Any protected `/app` or `/api/bff/*` proof item must have an explicit auth-lane plan before implementation planning is considered ready. (US3, US4)
- No implementation-ready, proceed, or ship recommendation is valid unless the matrix rows, baseline scope proof, and audit-disposition ledger are all planned as first-class outputs rather than post-hoc documentation. (US1, US3, FR10-FR12)

## 9. Telemetry (Minimal)

- No new product telemetry is required for MVP.
- Narrow diagnostic logging or assertion helpers are acceptable only if they are strictly required to produce deterministic zero-side-effect evidence or matrix traceability without widening the product surface. (US2, US3)

## 10. Deferred / Not in MVP

- Coverage for non-representative calls or additional failure families.
- A generalized launch-certification framework spanning unrelated workflows.
- Mandatory live external-credential verification as part of the primary proof lane.
- Unrelated UX, auth, or runtime cleanup outside the seams needed to make the trust claim honest.

## 11. Open Questions (if any)

- Whether all three representative happy-path proofs can be fully automated locally, or whether one or more require a clearly separated manual/live lane. The PRD keeps this open while preserving local/test-fixture automation as the primary assumption.

## 12. Changelog

- v0.1 (2026-03-10): Initial PRD from brainstorm.
- v0.2 (2026-03-10): Applied risk-audit edits to lock exact matrix seam labels, representative-scope labeling, and an explicit readiness gate; marked Ready for Tasks.
