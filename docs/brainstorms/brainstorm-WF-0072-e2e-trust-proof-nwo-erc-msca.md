<!-- docs/brainstorms/brainstorm-WF-0072-e2e-trust-proof-nwo-erc-msca.md -->
# WF-0072 — E2E Trust Proof for Representative NWO/ERC/MSCA Flows

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-10

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts/decisions for WF-0072.
- The Q&A transcript is rationale only; it must not introduce new contracts.
- If a later phase or Q&A block reveals a new contract, verification invariant, or fail-closed boundary, promote it into this brainstorm instead of leaving truth only in chat or the transcript.

## Preflight Step 1 — Long-Form Problem Intake

- User-selected target: promote parking-lot P1 #1 into `WF-0072` and define a launch-credible end-to-end trust proof for the locked NWO/ERC/MSCA wedge.
- Required proof bar: real user path evidence, not selector-only or unit-only substitutes.
- Required coverage: at least one truly end-to-end flow per representative family call (`NWO`, `ERC`, `MSCA`) plus the explicit failure modes named at kickoff.
- Named failure modes from kickoff: stage mismatch (especially ERC Step 1 vs Step 2 correctness), missing mandatory input, and policy-blocking behavior with zero side effects.
- Verification discipline from kickoff: deterministic selectors and commands, explicit evidence bundle, minimal manual steps only where automation cannot carry the proof, and fail-closed stop/fix behavior if any verification step fails.
- Carry-forward auth rule from kickoff: if this WF touches auth/proxy/sign-in/BFF boundaries, ship verification must include both auth lanes (`AUTH_MODE=test_bypass` and `AUTH_MODE=clerk`) with skipped lanes called out explicitly.

## Repo Reality Snapshot (Read-Only) (2026-03-10)

- The locked wedge and representative-proof framing are already documented: `docs/parking_lot.md`, `docs/memory/domain/project_docs.md`, and adjacent WFs expect one representative NWO, one ERC, and `MSCA-PF-2025` rather than broad program expansion.
- Real canonical call artifacts already exist for `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`, which makes them the most defensible default proof set for this WF.
- Recent repo memory records an explicit auth-bypass E2E lane (`AUTH_MODE=test_bypass`) plus a Clerk lane expectation for protected `/app` and `/api/bff/*`, which means auth verification is a likely concern if browser-driven proof hits those surfaces.
- Recent repo memory also records that quota/reviews-disabled gates live at the API boundary in `backend/main.py`, so policy-blocking proof must show downstream non-invocation and zero persistence side effects rather than inventing a service-entry gate.
- Adjacent WFs already narrowed the trust bar: WF-0065 locked cross-call semantic parity, WF-0070 locked ERC stage-truth expectations, and WF-0071 closed the node-hierarchy selector gap. WF-0072 should convert those contract claims into end-to-end launch evidence rather than reopen their scope.

### Repo Snapshot Open Questions

- Is the representative NWO proof call definitely `nwo_veni_2025_preproposal`, or is there a stronger current candidate in the repo for launch evidence?
- Should policy-blocking proof target only API/runtime no-side-effects, or also browser-visible UX messaging in the same WF?
- Does “truly end-to-end” for this WF require live browser submission through the protected app surface for all three families, or is a mixed bundle of browser plus API evidence acceptable when the user path and no-side-effect claims stay explicit?
- Are real external credentials/environments available for later live/manual proof, or should the artifact assume local/test-fixture automation plus an explicitly separate manual lane?

## 1. Problem Statement

- The primary trust gap is not missing low-level tests; it is missing launch-credible proof that a researcher can complete the representative review flow across the locked `NWO` / `ERC` / `MSCA` wedge and that the system fails closed on the named negative cases.
- The locked representative proof set for this WF is `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- “Policy-blocking behavior” in this WF means both researcher-visible blocking behavior and explicit proof of zero downstream side effects: no review creation, no pipeline execution, and no partial persistence when the gate blocks.
- Auth verification is conditionally mandatory: if the later implementation or verification bundle uses protected app or BFF surfaces, both auth lanes (`AUTH_MODE=test_bypass` and `AUTH_MODE=clerk`) must be run or explicitly reported as skipped with reason.
- The primary execution assumption is local/test-fixture automation first, with any real external/manual lane clearly separated and never silently required for Phase 0 completeness.

Contract Notes / Non-obvious constraints:

- This WF must not collapse into “API proof only”; user-path evidence is part of the problem definition.
- The representative set is fixed unless Phase 1 documents a blocker showing one of these calls cannot honestly prove the trust claim.
- “Fail closed” requires both returned semantics and absence-of-side-effects evidence.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 1)

## 2. Desired Outcome

- Success means an evidence bundle can show at least one truly end-to-end happy path for each representative call family and the named failure modes with deterministic pass/fail results.
- “Good enough” for MVP is not exhaustive matrix coverage of every call permutation; it is one representative NWO flow, one representative ERC flow, and one representative MSCA flow, plus cross-cutting negative cases that prove the trust boundaries named at kickoff.
- The expected behavior change is that launch-readiness discussions can point to concrete evidence rather than inferred confidence from lower-level tests or prior WFs.
- The verification bundle must be explicit, reproducible, and minimal: automation where possible, minimal manual steps only when required, and exact commands/selectors/results documented.
- A proceed recommendation is invalid if any blocking verification item fails, is skipped without rationale, or cannot prove zero side effects for a fail-closed claim.

Contract Notes / Non-obvious constraints:

- This WF is evidence-first; implementation only exists to make the evidence honest and repeatable.
- The bundle must distinguish automated proof from manual confirmation rather than blending them into a vague “tested” claim.
- Deterministic commands and selectors are part of the desired outcome, not later polish.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 2)

## 3. Target User / Actor

- The direct actor is the internal release owner deciding whether the locked wedge is trustworthy enough for launch claims.
- The protected end user is the researcher who relies on the product’s visible behavior and fail-closed boundaries being honest for `NWO`, `ERC`, and `MSCA`.
- The core frustration is not feature absence; it is uncertainty about whether the product behaves consistently and safely once a real call family or a failure gate is involved.
- The artifact audience includes engineering and QA owners who must implement a verification bundle without drifting into broad test-harness work.
- The WF prioritizes launch-trust evidence over convenience, feature expansion, or broader call onboarding.

Contract Notes / Non-obvious constraints:

- Internal actor priority raises the bar: evidence must support an actual go/no-go decision.
- Researcher trust still shapes the workflow because browser-visible behavior must align with backend fail-closed semantics.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 3)

## 4. Rough Idea (Unstructured Thinking)

- The simplest credible direction is a mixed verification bundle: browser-driven end-to-end proof on the protected app path for representative happy paths and visible failure UX, paired with API/runtime assertions where zero-side-effect proof cannot be observed honestly from the browser alone.
- The representative browser path should stay tied to existing real calls and the current product surfaces rather than synthetic demo-only fixtures.
- ERC stage-mismatch proof must stay end-to-end enough to show researcher-visible blocking plus runtime non-execution, not just a backend validation unit.
- Policy-blocking proof should reuse the existing API-boundary gate knowledge and add explicit non-invocation evidence instead of inventing a new service-entry contract.
- The implementation direction should prefer deterministic selectors, existing auth-lane seams, and non-parallel DB-mutating verification runs over broader harness redesign.

Contract Notes / Non-obvious constraints:

- “Mixed bundle” is acceptable only if each proof item is explicit about what is browser-visible and what requires backend verification.
- This WF can extend existing verification seams, but should not create a generalized launch-test platform.
- Protected-surface proof means auth-lane handling must be designed deliberately, not treated as an afterthought.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 4)

## 5. Constraints

- Scope stays locked to the representative wedge and the named trust proof cases: happy path, ERC stage mismatch, missing mandatory input, and policy-blocking behavior.
- The WF must remain fail-closed and verifiable; any new verification seam or implementation change must preserve the existing public contract unless a specific blocking proof gap forces a correction.
- Verification commands and browser steps must be deterministic and documented exactly; no “click around until it works” manual lane is acceptable.
- DB-mutating tests or scripts must not run in parallel when they could contaminate trust evidence.
- If auth/proxy/sign-in/BFF boundaries are touched, the verification bundle must include both auth lanes and explicitly report skips such as missing Clerk credentials.

Contract Notes / Non-obvious constraints:

- Minimal manual steps means a short deterministic checklist, not an informal exploratory session.
- “Verifiable” includes proving zero side effects for blocked paths, not just proving the UI showed an error.
- Scope does not include new call onboarding, prompt tuning, or general test-infrastructure cleanup.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 5)

## 6. Risks / Unknowns

- Highest risk is overclaiming end-to-end proof while still relying on lower-level assertions for the parts that matter most, especially side-effect absence and auth-boundary truth.
- Another key risk is that one or more representative calls may still require setup or ingest work that makes the planned browser proof brittle.
- There is a scope-creep risk toward broad automation-platform work or toward reopening already-closed adjacent WFs instead of proving their contracts.
- There is an evidence risk that browser-visible failure states may not by themselves prove non-execution or no-persistence, requiring careful pairing with backend assertions.
- The main planning unknown is how much of the final bundle can be fully automated locally versus needing a clearly separated manual/live lane.

Contract Notes / Non-obvious constraints:

- If a proof item cannot be automated honestly, the manual fallback must still be deterministic and minimal.
- A green browser test alone does not close the trust gap if the blocking/no-side-effect invariant remains unproven.
- Any representative-call setup blocker must be documented before Phase 1 broadens scope.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 6)

## Open Questions / Deferred

- Whether the final verification bundle should include a real external-credential manual lane depends on actual credential availability later; default planning assumes local/test-fixture automation plus a clearly marked optional manual/live lane.
- If one representative call proves unstable due to setup drift, Phase 1 must document whether to fix setup, switch representatives within the same family, or stop.
- The exact boundary between browser assertions and backend side-effect assertions is deferred to Phase 1 tasking, but the obligation to prove both is locked now.

## 7. MVP Definition

- The smallest acceptable slice is a verification bundle that proves one representative happy path for `NWO`, `ERC`, and `MSCA` through the real user path and proves the named negative cases fail closed with zero side effects.
- Minimum negative-case coverage is explicit: ERC Step 1 vs Step 2 mismatch, missing mandatory input with blocked submit, and policy-blocking behavior such as `QUOTA_EXCEEDED` or `REVIEWS_DISABLED`.
- Minimum verification outputs are explicit: exact commands, exact browser/manual steps if any, exact expected outcomes, and recorded results suitable for a walkthrough/evidence ledger.
- Minimum auth rule is explicit: if protected browser/BFF surfaces are in scope, run both auth lanes or mark skipped with concrete reason.
- Anything not required to make that bundle honest and repeatable is out of MVP.

## Acceptance Criteria

- AC1: The WF locks the representative proof set to `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025` unless a documented blocker forces a same-family substitution.
- AC2: At least one truly end-to-end happy-path flow exists per representative call family and is recorded in a deterministic verification ledger.
- AC3: ERC stage mismatch is proven fail-closed with researcher-visible blocking and zero downstream side effects.
- AC4: Missing mandatory input is proven fail-closed with submit blocked before execution or persistence.
- AC5: Policy-blocking behavior is proven fail-closed with visible blocking semantics on any user-facing surface exercised by the proof item, plus explicit zero-side-effect evidence even when the strongest proof lane is API-first.
- AC6: The verification bundle records exact commands/selectors/results and distinguishes automated evidence from manual confirmation.
- AC7: If protected app/BFF surfaces are exercised, both auth lanes are run or explicitly marked skipped with concrete reason.
- AC8: No ship or proceed recommendation is allowed while any blocking verification item is failing or unverified.

## Verification Bundle Shape

- Automated lane: deterministic browser and/or API runs covering the representative happy paths and the named fail-closed negative cases.
- Side-effect lane: deterministic backend assertions or evidence checks proving no review row, no pipeline run, and no partial persistence for blocked paths.
- Auth lane: `AUTH_MODE=test_bypass` smoke plus `AUTH_MODE=clerk` lane when credentials are available; skipped Clerk coverage must be stated explicitly.
- Manual lane: only the smallest deterministic checklist still needed after automation, with exact prerequisites and pass/fail outcomes.
- Walkthrough/evidence output: exact commands, exact results, and a concise checklist that another maintainer can rerun without guesswork.

## Verification Matrix Requirement

- Every proof item in the later walkthrough must map one-to-one to a matrix row containing: representative call, scenario (`happy-path`, `stage-mismatch`, `missing-mandatory-input`, `policy-blocking`), proof surface (`browser`, `API`, or paired), auth lane, side-effect assertion, and pass/fail result.
- The matrix must make clear whether a negative case is tied to one representative family only (for example ERC stage mismatch) or is intentionally demonstrated on a different representative call for the strongest fail-closed evidence.
- No final trust claim may rely on an unlabeled proof item or on a “covered elsewhere” assumption that is not traceable to a matrix row.

Contract Notes / Non-obvious constraints:

- “One E2E flow per family” must mean the real user path, not isolated component or service tests.
- Negative-case proof can pair browser and backend evidence, but both must map to the same fail-closed claim.
- Verification must stop and fix on failure; Phase progression cannot paper over red evidence.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 7)

## 8. Explicit Non-Goals

- No new funding-call onboarding or expansion beyond the locked representative wedge.
- No substitution of unit tests or selector-level smoke for launch evidence.
- No broad auth-system redesign, prompt tuning, extraction work, or unrelated UI cleanup.
- No generalized test-platform rewrite unless a narrow addition is strictly required to make the verification bundle honest.
- No parallelized DB-mutating verification that weakens determinism or traceability.

Contract Notes / Non-obvious constraints:

- This WF proves trust claims on the current surface; it does not enlarge that surface.
- Any adjacent improvement not required for the evidence bundle should be parked, not absorbed.
- “Minimal manual lane” is not permission to leave core proof gaps to human judgment.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md` (Section 8)
