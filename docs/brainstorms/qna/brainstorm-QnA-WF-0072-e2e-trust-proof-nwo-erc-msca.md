<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0072-e2e-trust-proof-nwo-erc-msca.md -->
# WF-0072 — E2E Trust Proof for Representative NWO/ERC/MSCA Flows

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-10

This file captures the full Phase 0.1 interactive Q&A transcript.

> Note: User instruction on 2026-03-10 approved the assistant recommendations for Section 1 and for the rest of the Phase 0 run.

## Section 1 — Problem Statement

**Q1: What is the primary trust claim this WF must prove?**
- A) Full launch claim: a researcher can complete a representative review flow end-to-end for NWO/ERC/MSCA, and the system fails closed on the named negative cases.
- B) Backend/runtime claim only: API and service behavior are correct across the wedge, even if browser/user-path evidence is partial.
- C) Browser smoke claim only: the visible app path works, with deeper runtime guarantees deferred.
> Recommendation: A. The parking-lot item explicitly asks for real user-path proof and warns against selector-only substitutes. B is too narrow because it drops the real user path. C is too weak to support launch evidence.
> **Selected: A**

**Q2: Which representative call set should be the locked default proof set?**
- A) `nwo_veni_2025_preproposal` + `erc_stg_2026_full` + `MSCA-PF-2025`
- B) `nwo_vidi_2025_full_proposal` + `erc_stg_2026_full` + `MSCA-PF-2025`
- C) Keep family-level names only for now and let Phase 1 choose exact calls.
> Recommendation: A. These are the strongest current in-repo representatives for the locked wedge and align with adjacent WF evidence. B broadens NWO scope unnecessarily. C leaves the proof target too ambiguous.
> **Selected: A**

**Q3: What should “policy-blocking behavior” mean in the WF contract?**
- A) Browser-visible block plus explicit proof of zero downstream side effects (no review creation, no pipeline run, no partial persistence).
- B) API error semantics plus zero downstream side effects; browser UX can be secondary if clearly documented.
- C) Error response only; side-effect proof can be inferred from existing lower-level tests.
> Recommendation: A. The user path matters here, and fail-closed should be both visible and verifiable. B is acceptable only if browser proof becomes impractical, but A is the stronger launch bar. C is too weak because it over-infers trust from lower-level coverage.
> **Selected: A**

**Q4: How should we treat auth in the problem statement?**
- A) Include auth lanes as conditional mandatory verification: if protected browser/BFF surfaces are in scope, run both `AUTH_MODE=test_bypass` and `AUTH_MODE=clerk`, and report skips.
- B) Exclude auth from the core problem statement and handle it only if implementation touches auth code.
- C) Require only `test_bypass`; Clerk is optional.
> Recommendation: A. This matches the kickoff guardrail and keeps the browser proof honest if protected surfaces are involved. B is too easy to under-scope. C weakens the explicit auth-lane rule without justification.
> **Selected: A**

**Q5: What environment assumption should the problem statement lock for later verification planning?**
- A) Assume local/test-fixture automation is the primary lane, with a separate clearly marked manual/live lane only if real creds are available.
- B) Assume real external credentials/environments will be available and make them part of the primary proof path.
- C) Leave environment assumptions unresolved until Phase 1.
> Recommendation: A. It keeps Phase 0 fail-closed and plannable without depending on unknown external access. B is risky unless confirmed now. C leaves the verification scope too ambiguous.
> **Selected: A**

## Auto-Piloted Sections (User Approved Default Recommendations)

## Section 2 — Desired Outcome

**Q1: What should count as success for this WF?**
- A) A deterministic evidence bundle with one real happy path per representative family plus the named fail-closed negative cases.
- B) A broad regression suite across every supported call and edge case.
- C) A manual “looks good” walkthrough with supporting screenshots.
> Recommendation: A. It is the smallest credible trust-proof bar. B is broader than the locked wedge requires. C is too subjective for launch evidence.
> **Selected: A**

**Q2: What is the MVP “good enough” boundary?**
- A) Representative NWO/ERC/MSCA proof plus the named negative cases only.
- B) Full supported-call matrix with all major variants.
- C) Happy-path only, with failure modes deferred.
> Recommendation: A. This stays tight and matches kickoff scope. B is scope creep. C misses the key trust failures.
> **Selected: A**

**Q3: What should change after this WF exists?**
- A) Launch-readiness discussions can point to explicit evidence instead of inferred trust.
- B) The product supports more calls.
- C) The UI becomes generally more polished.
> Recommendation: A. This WF is about trust proof, not breadth or polish.
> **Selected: A**

**Q4: How should verification be presented?**
- A) Exact commands, exact deterministic steps, and recorded outcomes.
- B) High-level test names with a short narrative summary.
- C) Only a walkthrough prose description.
> Recommendation: A. The user explicitly asked for deterministic commands and a verifiable bundle. B and C are too weak for rerunability.
> **Selected: A**

**Q5: What is the fail-closed proceed rule?**
- A) No proceed/ship recommendation while any blocking verification item is failing, skipped without rationale, or unproven.
- B) Proceed if the happy paths pass and negatives are mostly green.
- C) Proceed if manual inspection looks credible.
> Recommendation: A. This preserves the requested fail-closed discipline. B and C weaken the trust bar.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary actor for this WF?**
- A) Internal release/engineering owner deciding whether the locked wedge is trustworthy enough for launch claims.
- B) Any general end user browsing the site.
- C) External auditors only.
> Recommendation: A. The direct decision-maker is internal, though researcher trust remains the protected outcome.
> **Selected: A**

**Q2: Which end user is protected by this WF?**
- A) Researchers using NWO/ERC/MSCA flows who need visible behavior and fail-closed boundaries to be honest.
- B) Only admins maintaining call data.
- C) Future non-wedge funder users.
> Recommendation: A. This matches the locked wedge and the real trust claim.
> **Selected: A**

**Q3: What frustration is this WF really addressing?**
- A) Uncertainty about whether the product behaves consistently and safely in real representative flows.
- B) Missing advanced features.
- C) Slow local development ergonomics.
> Recommendation: A. The trust gap is about reliability evidence, not convenience.
> **Selected: A**

**Q4: Who needs to consume the artifact after Phase 0?**
- A) Engineering and QA owners implementing a bounded verification bundle.
- B) Marketing and brand teams first.
- C) General open-source contributors with no repo context.
> Recommendation: A. They are the immediate downstream actors.
> **Selected: A**

**Q5: What should this WF prioritize over all else?**
- A) Launch-trust evidence.
- B) Convenience and feature breadth.
- C) Generalized platform cleanup.
> Recommendation: A. Anything else would dilute the WF purpose.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest credible implementation direction?**
- A) A mixed bundle: browser-driven end-to-end proof for user-visible flows plus API/runtime assertions for zero-side-effect guarantees.
- B) Browser-only Playwright proof for everything.
- C) API-only verification with no real user-path coverage.
> Recommendation: A. It keeps the user path real while covering side-effect invariants the browser alone cannot prove. B overclaims. C misses the launch-evidence requirement.
> **Selected: A**

**Q2: What should the representative browser path use?**
- A) Existing real calls and current protected product surfaces.
- B) Synthetic demo-only fixtures.
- C) A brand-new special-case harness detached from the app.
> Recommendation: A. This is the most honest proof surface. B and C drift away from the real user path.
> **Selected: A**

**Q3: How should ERC stage-mismatch proof be handled?**
- A) Researcher-visible blocking plus runtime non-execution evidence.
- B) Backend validation only.
- C) UI filtering only.
> Recommendation: A. The trust claim spans both visible behavior and fail-closed execution.
> **Selected: A**

**Q4: How should policy-blocking proof be structured?**
- A) Reuse current API-boundary gate knowledge and add explicit non-invocation evidence.
- B) Invent a new service-entry gate just for this WF.
- C) Rely only on UI text.
> Recommendation: A. It aligns with repo reality and avoids unnecessary redesign. B changes contracts without need. C cannot prove zero side effects.
> **Selected: A**

**Q5: What verification style should this WF prefer?**
- A) Deterministic selectors, existing auth seams, and non-parallel DB-mutating runs.
- B) Broad test-platform redesign.
- C) Mostly manual exploratory sessions.
> Recommendation: A. It is the narrowest path to credible evidence.
> **Selected: A**

## Section 5 — Constraints

**Q1: What exact cases should stay in scope?**
- A) Happy path, ERC stage mismatch, missing mandatory input, and policy-blocking behavior for the representative wedge only.
- B) Any adjacent issue discovered during implementation.
- C) All supported calls and all edge cases.
> Recommendation: A. This is the locked scope from kickoff. B and C invite drift.
> **Selected: A**

**Q2: What contract stance should implementation take?**
- A) Preserve existing public contracts unless a specific blocking proof gap forces a correction.
- B) Freely reshape boundaries while working on trust proof.
- C) Avoid any code changes even if evidence cannot be proven honestly.
> Recommendation: A. It keeps changes narrow and reversible. B is too loose. C risks fake proof if the seams are inadequate.
> **Selected: A**

**Q3: How deterministic must the verification be?**
- A) Exact commands and exact browser/manual steps only.
- B) Approximate steps are acceptable.
- C) Manual memory of what was tested is enough.
> Recommendation: A. Determinism is explicit in the user request.
> **Selected: A**

**Q4: How should DB-mutating verification be run?**
- A) Not in parallel when contamination could affect evidence.
- B) Parallel by default for speed.
- C) Unspecified.
> Recommendation: A. The user explicitly warned against parallel DB-mutating tests.
> **Selected: A**

**Q5: What happens if auth/proxy/BFF boundaries are touched?**
- A) Run both auth lanes and report skips concretely.
- B) Ignore Clerk unless auth code changed directly.
- C) Defer auth verification entirely.
> Recommendation: A. This preserves the carry-forward guardrail.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the highest risk?**
- A) Overclaiming end-to-end proof while still depending on hidden lower-level assumptions.
- B) Spending slightly longer on documentation.
- C) Minor UI polish regressions.
> Recommendation: A. This is the main failure mode for a trust-proof WF.
> **Selected: A**

**Q2: What setup risk is most likely?**
- A) Representative calls may need setup or ingest stabilization before browser proof is reliable.
- B) The repo has no relevant calls.
- C) The whole wedge likely needs expansion first.
> Recommendation: A. The calls exist, but setup drift remains plausible.
> **Selected: A**

**Q3: What scope-creep risk matters most?**
- A) Sliding into broad automation-platform work or reopening adjacent WFs.
- B) Adding too many comments to docs.
- C) Minor naming debates.
> Recommendation: A. This is the real planning risk.
> **Selected: A**

**Q4: What evidence risk must planning acknowledge?**
- A) Browser-visible states may not by themselves prove non-execution or no persistence.
- B) Screenshots alone are always sufficient.
- C) Existing unit tests automatically cover end-to-end truth.
> Recommendation: A. This is exactly why the mixed bundle is needed. B and C are false.
> **Selected: A**

**Q5: What key unknown should remain explicit?**
- A) How much of the final bundle can be fully automated locally versus needing a separated manual/live lane.
- B) Whether the wedge should expand.
- C) Whether trust proof matters at all.
> Recommendation: A. This is the only real unresolved planning variable still needed for execution design.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: What is the smallest acceptable slice?**
- A) One representative happy path for NWO/ERC/MSCA plus fail-closed proof for the named negative cases.
- B) Complete supported-call certification.
- C) Happy-path demos only.
> Recommendation: A. It is the narrowest credible MVP. B is too broad. C is too weak.
> **Selected: A**

**Q2: Which negative cases are mandatory?**
- A) ERC stage mismatch, missing mandatory input, and policy-blocking behavior.
- B) Only stage mismatch.
- C) Whatever is easiest to automate.
> Recommendation: A. These are explicitly required by the user.
> **Selected: A**

**Q3: What outputs must the verification bundle contain?**
- A) Exact commands, exact expected outcomes, and recorded results suitable for a walkthrough/evidence ledger.
- B) Only passing test names.
- C) Only screenshots.
> Recommendation: A. This is necessary for traceability and reruns.
> **Selected: A**

**Q4: What is the minimum auth rule inside MVP?**
- A) If protected app/BFF surfaces are exercised, run both auth lanes or mark skipped with concrete reason.
- B) Always ignore Clerk.
- C) Always require live Clerk regardless of environment availability.
> Recommendation: A. It matches the kickoff guardrail without inventing impossible requirements.
> **Selected: A**

**Q5: What should be excluded from MVP?**
- A) Anything not required to make the trust-proof bundle honest and repeatable.
- B) Only code cleanup.
- C) Nothing; include all adjacent improvements.
> Recommendation: A. This keeps the WF tight and defensible.
> **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: Which expansion is explicitly out of scope?**
- A) New funding-call onboarding beyond the locked wedge.
- B) Same-family substitutions if a blocker is documented.
- C) Narrow setup fixes for current representatives.
> Recommendation: A. New onboarding would re-open scope. B and C may still be necessary within the locked wedge.
> **Selected: A**

**Q2: What should not be counted as launch evidence?**
- A) Unit tests or selector-only smoke standing in for the real user path.
- B) Deterministic mixed browser/API evidence.
- C) Minimal manual confirmation documented explicitly.
> Recommendation: A. The user explicitly prohibited this substitution.
> **Selected: A**

**Q3: Which adjacent work stays out?**
- A) Broad auth redesign, prompt tuning, extraction, and unrelated UI cleanup.
- B) Narrow evidence-enabling seam fixes.
- C) Deterministic verification documentation.
> Recommendation: A. B and C may still be required to make the proof honest.
> **Selected: A**

**Q4: What kind of testing infrastructure work is out?**
- A) Generalized platform rewrites unless a narrow addition is strictly required.
- B) Any testing code at all.
- C) All browser automation.
> Recommendation: A. The WF can add narrow seams, but not a platform overhaul.
> **Selected: A**

**Q5: What run style is explicitly forbidden?**
- A) Parallel DB-mutating verification that weakens determinism or traceability.
- B) Sequential deterministic runs.
- C) A tiny deterministic manual checklist after automation.
> Recommendation: A. This follows the user’s verification discipline guardrail.
> **Selected: A**

## Addendum — Phase 0.3 Risk-Audit Application

- Audit finding 1 (`non-blocking`): the original AC5 wording could be read as requiring browser-visible proof even when the strongest honest proof lane for a policy block is API-first. Applied edit: refined AC5 so user-facing blocking is required on any exercised UI surface, while API-first proof is still allowed when paired with explicit zero-side-effect evidence.
- Audit finding 2 (`non-blocking`): the brainstorm required deterministic evidence but did not explicitly force a one-row-per-proof-item matrix, which could let later phases overstate coverage. Applied edit: added `## Verification Matrix Requirement` to force each proof item to declare representative call, scenario, proof surface, auth lane, side-effect assertion, and pass/fail result.
