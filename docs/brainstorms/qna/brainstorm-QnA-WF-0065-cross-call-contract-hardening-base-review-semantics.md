<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0065-cross-call-contract-hardening-base-review-semantics.md -->
# WF-0065 — Cross-Call Contract Hardening of Base Review Semantics Brainstorm Q&A

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

Related brainstorm: `docs/brainstorms/brainstorm-WF-0065-cross-call-contract-hardening-base-review-semantics.md`

---

## Session Log

### Preflight Step 1 — Long-Form Problem Intake

User provided the initiating narrative directly in chat. Locked intake points:
- PeerLens' mission-critical trust surface is base review behavior grounded in official call requirements and evaluation criteria/elements.
- WF-0063 and WF-0064 already closed the current `MSCA-PF-2025` hierarchical proof-path blocker.
- The remaining launch-critical gap is insufficient deterministic evidence that base review semantics hold across supported calls and failure modes.
- Required failure-mode scope explicitly includes `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`.
- Scope must stay on trust-surface hardening; no supporting-context semantics, no new-call onboarding, no broad redesign.

### Preflight Step 2 — Repo Reality Snapshot

Read-only repo snapshot captured before Section 1 questioning:
- WF-0045 already locked the six-stage base pipeline contract and deterministic failure-class semantics in docs and tests.
- `backend/app/engine/pipeline_v1.py` implements the six-stage call-agnostic flow, but the existing cross-call matrix still uses a synthetic MSCA archetype and narrow severity-only expectations.
- `backend/tests/test_api.py` already covers `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`, but not as explicit multi-call contract-hardening evidence.
- Supported real-call repo coverage currently spans NWO, ERC, and MSCA families, matching the parking-lot rationale that breadth should not expand further in this WF.
- WF-0063 and WF-0064 already proved fail-closed proof-path behavior for `MSCA-PF-2025`; reopening supporting-node semantics would be scope creep here.

### Section 1 — Problem Statement

**Q1: What is the primary defect this WF must prove or disprove?**
- A) The base review contract is not yet proven consistent at the contract boundary across supported calls and failure gates.
- B) The engine internals are too complex and need refactoring before trust is possible.
- C) The main issue is lack of more supported calls.
 > Recommendation: A — This matches the launch blocker and keeps the WF on evidence. B broadens into redesign without first proving the trust gap. C confuses breadth with trustworthiness and would scale uncertainty instead of reducing it.
 > **Selected: A**

**Q2: What is the minimum call-coverage bar for this WF's problem statement?**
- A) One proof call only, as long as failure modes are covered deeply.
- B) One representative real call from each active family: NWO, ERC, and MSCA.
- C) Every currently supported real call that can hit the base review surface.
 > Recommendation: B — This is the smallest credible cross-call proof bar. A is too weak for a “cross-call” hardening claim. C may be warranted later, but it is a stronger scope commitment than Phase 0 currently needs.
 > **Selected: B**

**Q3: Where must fail-closed consistency be proven?**
- A) Engine pipeline only.
- B) API/service boundary only.
- C) Paired boundary: service/API entrypoints plus the underlying base-review execution seam where fail-open drift could hide.
 > Recommendation: C — API-only proof can miss hidden fail-open execution underneath, while engine-only proof misses the user-relevant contract surface. Paired proof is the safest minimum.
 > **Selected: C**

**Q4: Which inconsistency should count as a blocker in this WF?**
- A) Only fail-open behavior.
- B) Any drift in status/error semantics, gating behavior, or review-contract outcomes across calls for the same boundary case.
- C) Only user-visible message differences.
 > Recommendation: B — Mission trust depends on consistent semantics, not just avoiding catastrophic fail-open behavior. A is too narrow; C is mostly presentation-level and misses contract drift.
 > **Selected: B**

**Q5: Which scope exclusion needs to be explicit in the problem statement?**
- A) Exclude supporting-context semantics, new-call onboarding, and broad pipeline redesign.
- B) Exclude only frontend/UI work.
- C) Exclude nothing yet; keep room to widen if needed.
 > Recommendation: A — This is the cleanest scope lock and directly matches the user’s stated constraints. B is too shallow. C invites scope drift at exactly the wrong phase.
 > **Selected: A**

### Section 2 — Desired Outcome

**Q1: What is the main success condition for this WF?**
- A) A larger set of calls exists in the repo.
- B) Deterministic evidence proves the same base review semantics across representative NWO, ERC, and MSCA calls.
- C) The pipeline code becomes cleaner and easier to read.
 > Recommendation: B — This directly answers the mission question. A is breadth without proof. C may be a side effect but is not the success criterion.
 > **Selected: B**

**Q2: What is the MVP-ready evidence bar?**
- A) A planning artifact plus a few spot checks.
- B) A deterministic proof bundle covering happy path and fail-closed gating for the chosen representative calls.
- C) A full test sweep over every runtime permutation in the product.
 > Recommendation: B — This is evidence-driven and still bounded. A is too weak; C is too broad for a tight hardening WF.
 > **Selected: B**

**Q3: What behavioral change should this WF create internally?**
- A) Release decisions no longer rely on proof slices from one call or one mode.
- B) Teams can onboard new calls immediately after Phase 0.
- C) Engineers can redesign the pipeline with more confidence.
 > Recommendation: A — It captures the actual shift in trust posture. B is premature. C over-centers redesign instead of contract certainty.
 > **Selected: A**

**Q4: How should the named failure modes be treated in the outcome?**
- A) As secondary checks outside the main proof story.
- B) As first-class contract outcomes that must be shown to fail closed consistently.
- C) As generic platform behavior not tied to call semantics.
 > Recommendation: B — The user named them explicitly because they matter to trust at the contract boundary. A and C both understate that.
 > **Selected: B**

**Q5: What kind of output matters most by the end of the WF?**
- A) Tests and pass/fail evidence tied to the contract boundary.
- B) Architecture notes and future-state diagrams.
- C) A generalized coverage dashboard.
 > Recommendation: A — This WF is trust-surface hardening, not architecture planning. B and C may help later, but neither is the core deliverable.
 > **Selected: A**

### Section 3 — Target User / Actor

**Q1: Who is the primary actor for this WF?**
- A) Internal product/engineering/release owners deciding if the review surface is trustworthy enough to ship.
- B) End users directly interacting with a new UI.
- C) External partners evaluating documentation quality.
 > Recommendation: A — This is an internal trust-hardening WF. B is secondary and outcome-oriented. C is not the relevant decision-maker.
 > **Selected: A**

**Q2: Who is the protected secondary actor?**
- A) Researchers relying on consistent, traceable review behavior across supported calls.
- B) Marketing stakeholders expanding the supported-calls claim.
- C) Admin users managing internal tooling.
 > Recommendation: A — Researcher trust is the mission anchor. B and C are downstream concerns, not the protected user here.
 > **Selected: A**

**Q3: What pain are these actors feeling now?**
- A) Missing UI polish.
- B) Uncertainty that contract semantics really hold when call shape or failure gating changes.
- C) Slow onboarding of new funding programs.
 > Recommendation: B — That is the real blocker described in the prompt. A and C are adjacent but not mission-critical here.
 > **Selected: B**

**Q4: What audience should the brainstorm optimize for?**
- A) Cross-phase planning and implementation owners who need a sharply bounded trust-hardening scope.
- B) Broad product stakeholders who want feature-roadmap context.
- C) External documentation readers.
 > Recommendation: A — The artifact needs to drive PRD/tasks cleanly. B and C dilute the operational value.
 > **Selected: A**

**Q5: What should this WF prioritize for these actors?**
- A) Contract-boundary reliability over breadth, UX, and cleanup.
- B) Equal treatment of trust work and feature expansion.
- C) Fastest path to more supported calls.
 > Recommendation: A — That is the explicit mission and constraint set. B and C would undermine the WF’s purpose.
 > **Selected: A**

### Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction?**
- A) Contract-hardening through deterministic engine and API/service tests on representative real calls.
- B) A pipeline redesign that bakes in new abstractions first.
- C) A broader quality initiative covering docs, UI, and runtime behavior together.
 > Recommendation: A — It is the narrowest path to real evidence. B and C broaden scope before proving the actual gap.
 > **Selected: A**

**Q2: What call set should the rough idea start from?**
- A) Real supported family representatives already present in-repo.
- B) Synthetic archetypes only.
- C) Newly onboarded calls added specifically for this WF.
 > Recommendation: A — Real supported calls are the strongest trust evidence. B is too weak on its own. C violates the scope lock unless needed as a blocker response.
 > **Selected: A**

**Q3: How should failure-mode coverage relate to happy-path coverage?**
- A) Keep them separate as unrelated concerns.
- B) Treat them as the same contract-hardening story: same boundary, same fail-closed invariants, different cases.
- C) Focus only on failure modes because happy path already exists.
 > Recommendation: B — This keeps the contract surface coherent. A fragments the work. C risks missing cross-call semantic drift on success paths.
 > **Selected: B**

**Q4: How should WF-0045 and WF-0063/WF-0064 influence the idea?**
- A) Use them as baseline contracts and evidence inputs, not as areas to reopen.
- B) Partially revisit them to refresh architecture choices.
- C) Ignore them and define a new trust model.
 > Recommendation: A — Those WFs already define the baseline and close adjacent gaps. B and C would waste effort and create drift.
 > **Selected: A**

**Q5: What should happen if the current test seams are insufficient?**
- A) Add the minimum seam or correction required to prove the contract, then stop.
- B) Expand into a broader test-framework redesign.
- C) Defer the proof and document the limitation.
 > Recommendation: A — The WF is allowed to do narrow enabling work in service of hard evidence. B is too broad; C leaves the trust gap unresolved.
 > **Selected: A**

### Section 5 — Constraints

**Q1: What is the top scope constraint?**
- A) Keep the WF strictly on trust-surface hardening for base review semantics.
- B) Use the WF to absorb nearby backlog items while context is fresh.
- C) Leave scope flexible until Phase 2.
 > Recommendation: A — This preserves the mission and avoids planning drift. B and C both invite uncontrolled widening.
 > **Selected: A**

**Q2: What contract constraint applies to implementation changes?**
- A) Preserve existing fail-closed behavior unless a specific deterministic proof gap requires a minimal fix.
- B) Freely refactor any affected modules if tests still pass.
- C) Avoid implementation changes entirely even if proof is impossible otherwise.
 > Recommendation: A — Minimal, proof-driven change is the right balance. B is too loose. C can block legitimate hardening.
 > **Selected: A**

**Q3: What breadth constraint should apply to call coverage?**
- A) Stay within active real-call families already supported in-repo unless lack of a representative becomes a documented blocker.
- B) Add any missing promised program now to maximize confidence.
- C) Restrict to one existing proof call only.
 > Recommendation: A — This gives credible cross-call breadth without expanding onboarding scope. B is too broad; C is too narrow.
 > **Selected: A**

**Q4: What evidence constraint should guide the WF?**
- A) Prefer deterministic tests and contract evidence over prose and broad cleanup.
- B) Treat documentation quality as equal to executable proof.
- C) Focus on prose first, tests later.
 > Recommendation: A — This aligns with the user’s trust-surface instruction. B and C weaken the evidence-first posture.
 > **Selected: A**

**Q5: What adjacent work must remain out unless forced by a blocker?**
- A) Supporting-context semantics, onboarding work, unrelated UI, and broad refactors.
- B) Only frontend tasks.
- C) Nothing; all adjacent fixes are fair game if discovered.
 > Recommendation: A — It is the only option consistent with the explicit scope lock.
 > **Selected: A**

### Section 6 — Risks / Unknowns

**Q1: What is the highest risk if this WF is scoped poorly?**
- A) We keep claiming trust while relying on shallow or one-off proof slices.
- B) We miss a chance to clean up architecture.
- C) We do not add enough new calls.
 > Recommendation: A — That is the core mission risk. B and C are secondary.
 > **Selected: A**

**Q2: What hidden failure should this WF watch for?**
- A) Boundary responses look correct while internal execution still fails open underneath.
- B) Docs become too detailed.
- C) Tests take longer to run.
 > Recommendation: A — This is exactly why paired boundary proof matters. B and C are operational nuisances, not trust defects.
 > **Selected: A**

**Q3: What is the biggest scope-creep trap?**
- A) Slipping into onboarding, supporting-context semantics, or generalized cleanup.
- B) Adding a few extra assertions to tests.
- C) Reusing existing fixtures.
 > Recommendation: A — That is the realistic trap for this WF. B and C are normal hardening work.
 > **Selected: A**

**Q4: What is the main genuine unknown to carry forward?**
- A) Whether one representative real call per family is enough, or whether family variance still exposes material contract differences.
- B) Whether the product should eventually support more programs.
- C) Whether the frontend labels need refinement.
 > Recommendation: A — This is the only unknown that could legitimately change Phase 1 scope.
 > **Selected: A**

**Q5: What should the first validation target be?**
- A) Identify the exact unproven semantic invariants that still matter for launch trust.
- B) Maximize the number of tests added.
- C) Broaden the mission statement.
 > Recommendation: A — This keeps the WF precise and evidence-driven. B can create noise; C is irrelevant.
 > **Selected: A**

### Section 7 — MVP Definition

**Q1: What is the smallest functional slice for this WF?**
- A) A deterministic proof bundle over representative NWO, ERC, and MSCA calls at paired engine and API/service boundaries.
- B) A new generalized platform for review verification.
- C) A planning-only package that defers evidence to later.
 > Recommendation: A — It is the minimum executable slice that answers the trust question. B and C both miss the WF goal.
 > **Selected: A**

**Q2: Which named failure modes must be in the MVP?**
- A) `QUOTA_EXCEEDED` and `REVIEWS_DISABLED`, both shown as fail-closed contract outcomes.
- B) Only whichever is easiest to test first.
- C) Neither; they can stay as generic platform checks.
 > Recommendation: A — The user made these explicit requirements, so excluding them would be a scope failure.
 > **Selected: A**

**Q3: What source material should MVP prefer?**
- A) Existing real call snapshots and current runtime seams.
- B) Mostly synthetic fixtures because they are easier to control.
- C) Newly onboarded calls for additional breadth.
 > Recommendation: A — Trust claims are stronger when grounded in real supported calls. B is insufficient as the main proof base. C is out of scope unless a blocker forces it.
 > **Selected: A**

**Q4: What must the MVP enable by the end of later phases?**
- A) A clear ship/no-ship judgment about whether current review behavior is dependable across calls and failure modes.
- B) Immediate expansion to the next promised program.
- C) A broader product roadmap reset.
 > Recommendation: A — That is the stated expected outcome. B and C are separate initiatives.
 > **Selected: A**

**Q5: What should be excluded from MVP even if tempting?**
- A) Anything not required to produce that dependability judgment.
- B) Only visual polish.
- C) Only work outside the backend.
 > Recommendation: A — This is the tightest and safest MVP boundary.
 > **Selected: A**

### Section 8 — Explicit Non-Goals

**Q1: What onboarding-related non-goal should be explicit?**
- A) No new call onboarding unless a documented blocker shows the current supported-call set cannot prove the contract.
- B) Onboard the missing promised program in parallel.
- C) Leave onboarding undecided.
 > Recommendation: A — This preserves scope while allowing a documented blocker path if reality forces it.
 > **Selected: A**

**Q2: What semantics-related non-goal should be explicit?**
- A) No supporting-context semantic expansion beyond the existing proof-call boundary.
- B) Revisit supporting-node behavior while reviewing MSCA evidence.
- C) Keep semantics flexible for later planning.
 > Recommendation: A — Supporting-context expansion is already parked and explicitly out of scope here.
 > **Selected: A**

**Q3: What engineering non-goal should be explicit?**
- A) No broad pipeline redesign, architecture rewrite, or unrelated refactor work.
- B) Refactor freely if nearby files are touched.
- C) Delay all code changes even if proof requires them.
 > Recommendation: A — Minimal proof-driven fixes are allowed, but broad redesign is not.
 > **Selected: A**

**Q4: What product-surface non-goal should be explicit?**
- A) No UX/content breadth work whose main value is expansion rather than trust hardening.
- B) Add any small adjacent product fixes discovered during testing.
- C) Keep product scope open.
 > Recommendation: A — This prevents the WF from becoming a grab bag of adjacent improvements.
 > **Selected: A**

**Q5: What general non-goal should close the section?**
- A) No speculative features or planning work outside the base review contract boundary.
- B) No docs updates.
- C) No test additions.
 > Recommendation: A — The WF still needs docs and tests; what it must exclude is speculative scope outside the boundary.
 > **Selected: A**

### Part B Clarifications — Blocking Audit Resolution

**Q1: How should the representative-call contract be locked?**
- A) Exactly 3 calls for MVP: one real call each from NWO, ERC, and MSCA; widen only if Phase 1 documents a blocker.
- B) At least 3 calls, with freedom to include more during planning.
- C) All currently supported real calls.
 > Recommendation: A — This locks a real MVP boundary while preserving a fail-closed expansion path if evidence shows the 3-call set is not enough. B leaves too much drift. C may be stronger than needed and can inflate scope before the gap is proven.
 > **Selected: A**

**Q2: How should `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` be scoped?**
- A) API/service-entry gate proofs only, with explicit assertions that pipeline execution and persistence do not happen.
- B) Require paired engine+API proof for those gates too.
- C) Treat them as secondary and leave seam choice open.
 > Recommendation: A — These are entry-gate semantics, so the correct fail-closed proof is that they stop before engine execution and before persistence side effects. B confuses the runtime seam. C leaves a critical trust rule ambiguous.
 > **Selected: A**

**Q3: What fail-closed side-effect rule should be locked?**
- A) Blocked gate outcomes create no review, run no pipeline, and leave no partial persisted review state.
- B) Only “no successful review creation” needs to be guaranteed.
- C) Leave persistence semantics to Phase 1.
 > Recommendation: A — This is the strictest trustworthy contract and matches the user’s trust-surface goal. B still allows silent partial state. C defers a core fail-closed invariant.
 > **Selected: A**
