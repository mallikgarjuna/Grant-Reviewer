<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0061-real-call-data-expansion-single-call.md -->
# WF-0061 — Real Call Data Expansion: Single New Canonical Call

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-07

Type: feature

---

## Preflight Intake

### User Narrative (accepted as-is)

WF-0061 should prove real product progress by adding exactly one new official-source canonical call, not by doing more framework, governance, or generic hardening work. The current repo has strong machinery and several corrected canonical calls, but the validated coverage is still too narrow. We already have NWO and ERC represented; what is missing is another real call that broadens trust in the product’s claimed support surface. This workflow should answer a concrete question: can PeerLens onboard one more real call safely through the existing path, using official sources, without collapsing into another meta-workflow?

The right target for this workflow is MSCA Postdoctoral Fellowships 2025 (MSCA-PF-2025). It is a sharper next step than revisiting ERC/NWO again because those families already have canonical coverage, and reworking them again would mostly be fake progress. MSCA is also already part of the product story and repo expectations, so landing one real MSCA call would close a more meaningful credibility gap than more internal cleanup. The scope should stay to one call only: one canonical YAML, one source-grounded traceability path, one validation/ingest proof, and the minimum runtime proof that this call is operationally real.

Real progress in WF-0061 means moving MSCA-PF-2025 from absent to official-source-grounded canonical coverage with safe validation evidence. Fake progress means spending time on more onboarding machinery, frontend redesign, broad cross-call hardening, batch expansion to multiple calls, or speculative YAML authoring without the official source documents. The workflow must enforce the per-call upload gate strictly: no substantive YAML structure or criteria authoring until I upload the official MSCA-PF-2025 source documents for narrative/application structure and evaluation criteria.

The hard constraints are: keep scope tight, use the workflow system properly, do not create a new WF unless this container clearly breaks, and avoid any step that turns this into a broad platform effort. Planning can proceed before source upload, but substantive call authoring cannot. If MSCA-PF-2025 exposes a broader blocker, the default response should be to stop, document it clearly, and only absorb the smallest compatibility fix that is truly required for this one call. The goal is one real validated call, not another round of workflow churn.

## Section 1 — Problem Statement

**Q1: What exact call should `WF-0061` target?**
- A) `MSCA Postdoctoral Fellowships 2025`, full proposal only.
- B) Another MSCA call family/year/stage, still exactly one call.
- C) Keep `MSCA` generic for now and decide later.
 > Recommendation: A — it is the cleanest, narrowest, repo-aligned target. B is only justified if PF 2025 is known to be the wrong fit. C is workflow vagueness and would let scope drift survive into later phases.
 > **Selected: A** with user clarification: `MSCA Postdoctoral Fellowships 2025` (`MSCA-PF-2025`).

**Q2: What is the core problem this WF is meant to solve?**
- A) PeerLens lacks credible validated coverage beyond the current NWO/ERC set, so product claims outrun reality.
- B) The repo still needs more generic onboarding machinery before new calls can be trusted.
- C) The main issue is frontend polish for multi-call UX.
 > Recommendation: A — it targets the real product-risk. B is the framework-loop trap this WF is supposed to avoid. C is scope drift away from actual call coverage.
 > **Selected: A**

**Q3: What should count as fake progress inside this WF?**
- A) Any work that does not move one official-source `MSCA-PF-2025` call toward validated canonical coverage.
- B) Only obvious meta-doc/process work; limited platform hardening is fine even if no call lands.
- C) Nothing specific; decide case by case during implementation.
 > Recommendation: A — it creates a crisp anti-drift boundary. B leaves too much room for “useful” churn with no real call landed. C guarantees ambiguity and weak scope control.
 > **Selected: A**

**Q4: How strict is the source-upload gate before YAML work?**
- A) No substantive `MSCA-PF-2025` YAML structure/criteria authoring until the official structure source and evaluation source for that exact call are uploaded.
- B) Allow draft YAML structure before upload, but block final criteria mapping.
- C) Allow substantial authoring from public recollection and backfill sources later.
 > Recommendation: A — it is the only option that preserves source-grounded authorship. B invites speculative structure that later has to be “confirmed.” C breaks the repo's source-gating rule outright.
 > **Selected: A**

**Q5: If the chosen MSCA call reveals a broader product blocker, what is the default response?**
- A) Stop, document the blocker, and keep `WF-0061` limited to the smallest compatibility fix needed for this one call or pause for re-scope.
- B) Absorb the broader blocker into `WF-0061` so the call can ship end-to-end no matter what.
- C) Switch immediately to a new hardening WF.
 > Recommendation: A — it protects the single-call boundary while still allowing a necessary compatibility fix. B invites scope explosion. C is premature unless the single-call container is clearly no longer viable.
 > **Selected: A**, with user clarification: allow a limited amount of B only when it is directly relevant to the tight single-call scope.

## Section 2 — Desired Outcome

**Q1: What is the minimum success condition for `WF-0061`?**
- A) `MSCA-PF-2025` canonical YAML exists, is source-grounded, validates cleanly, ingests locally, and has a minimal proof that it works through the existing path.
- B) YAML exists and validates, but ingest/runtime proof can wait for a later WF.
- C) Planning artifacts are enough if the source set and structure are clear.
 > Recommendation: A — it is the smallest credible “real expansion” bar. B leaves the repo with another almost-real call. C is documentation-only churn.
 > **Selected: A** by delegated recommendation.

## Part B Clarifications

**Q1: What exact coverage claim should `WF-0061` use consistently?**
- A) One new promised canonical call, specifically `MSCA-PF-2025`, regardless of how agency taxonomy is labeled.
- B) One new program family under the EU/Horizon umbrella.
- C) One new agency-level coverage expansion.
 > Recommendation: A — it is the least ambiguous and best aligned with the actual deliverable. B is workable but still taxonomy-heavy. C is the weakest unless agency semantics are defended explicitly.
 > **Selected: A**

**Q2: What minimum proof bar should count as `operationally real`?**
- A) Canonical YAML validation pass, local ingest pass, and at least one deterministic verification proving the call can be exercised through the intended product path.
- B) Validation pass and ingest pass only.
- C) Validation pass, ingest pass, and a manual smoke check only.
 > Recommendation: A — B is too weak, and C still leaves too much room for subjective proof.
 > **Selected: A**

**Q3: What exact upload set should be locked before Phase 3 authoring starts?**
- A) The official `MSCA-PF-2025` application/narrative structure source and the official evaluation/assessment criteria source; reviewer guide or annexes are optional supplements if needed.
- B) Only one official source document if it appears to contain both structure and criteria.
- C) Any two official MSCA documents that seem close enough.
 > Recommendation: A — it preserves the source gate without creating ambiguity.
 > **Selected: A**

**Q2: How strong should the runtime proof be for this WF?**
- A) Minimal but real: enough deterministic validation/ingest proof plus one narrow operational smoke proof that the call is actually usable.
- B) Full end-to-end parity across every submit/review UI path.
- C) No runtime proof beyond dry-run validation.
 > Recommendation: A — it proves real product progress without inflating scope. B likely becomes another platform WF in disguise. C is too weak to support the stated product goal.
 > **Selected: A** by delegated recommendation.

**Q3: What should be the default file/output target for the new canonical call?**
- A) One new canonical YAML only, expected at `backend/data/calls/canonical/msca/msca_pf_2025_full.yaml`.
- B) YAML plus parallel alternate variants or drafts for the same call.
- C) Keep filename/path undecided until implementation.
 > Recommendation: A — it keeps the deliverable concrete and auditable. B adds noise and duplicate truth. C weakens planning clarity for no benefit.
 > **Selected: A** by delegated recommendation.

**Q4: What is the acceptable scope for compatibility fixes discovered while onboarding `MSCA-PF-2025`?**
- A) Only the smallest fix required to land this one call safely, with no generic platform expansion unless the call cannot exist without it.
- B) Any improvement that seems broadly useful once we are already touching the area.
- C) No fixes at all; if anything breaks, stop the WF.
 > Recommendation: A — it keeps the WF honest while allowing necessary unblockers. B is the usual path to fake progress. C is too rigid to be practical.
 > **Selected: A** by delegated recommendation.

**Q5: What should explicitly remain out of scope even if it looks adjacent?**
- A) A second new call, broad frontend redesign, cross-call hardening, and generic onboarding framework work.
- B) Only a second call is out of scope; the other items can be absorbed if convenient.
- C) Keep out-of-scope flexible for later.
 > Recommendation: A — this is the anti-drift boundary the WF needs. B and C both create loopholes large enough to swallow the workflow.
 > **Selected: A** by delegated recommendation.

## Section 3 — Target User / Actor

**Q1: Who is the primary actor for this workflow?**
- A) Internal developer/operator onboarding one real call safely into the product.
- B) End-user researchers directly interacting with a new MSCA UI.
- C) General admin users managing many calls at once.
 > Recommendation: A — this WF is fundamentally about proving onboarding/product readiness. B is downstream value, not the primary actor for Phase 0 planning. C implies unnecessary admin-platform scope.
 > **Selected: A** by delegated recommendation.

**Q2: Who is the secondary actor that benefits from this workflow?**
- A) Product/demo owner who needs evidence that supported-call claims are becoming real.
- B) Frontend team seeking a reason to generalize the UI further.
- C) Governance/ops owner seeking stronger process controls.
 > Recommendation: A — that is the clearest secondary value. B and C both pull the workflow toward machinery rather than validated call coverage.
 > **Selected: A** by delegated recommendation.

**Q3: What user-facing value matters most here?**
- A) Researchers benefit indirectly because one more real call becomes source-grounded and reviewable.
- B) Immediate polished MSCA-specific UX is the main value.
- C) Better internal workflow/process consistency is the main value.
 > Recommendation: A — it stays aligned to the actual product-readiness problem. B is too UI-centric for this WF. C is internal quality, not the core user outcome.
 > **Selected: A** by delegated recommendation.

**Q4: What frustration does this workflow address for the product owner?**
- A) Current multi-call support claims are ahead of validated real-call evidence.
- B) The repo lacks enough generic call-onboarding abstractions.
- C) The main problem is that admin tooling is still limited.
 > Recommendation: A — it names the real credibility gap. B is a tempting but off-target abstraction complaint. C is not the leading product risk here.
 > **Selected: A** by delegated recommendation.

**Q5: What should this workflow optimize for?**
- A) Operator trust, traceability, and one-call proof of safe expansion.
- B) Maximum breadth of adjacent improvements while touching the area.
- C) Lowest-effort docs-only closure.
 > Recommendation: A — it sets the correct quality bar. B is scope drift. C is fake progress.
 > **Selected: A** by delegated recommendation.

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction?**
- A) Add exactly one new canonical MSCA call from official sources, with traceability, validation, ingest, and a narrow operational proof.
- B) Use this WF to design a more general multi-agency onboarding framework first, then add MSCA.
- C) Batch-author several adjacent calls while the authoring context is warm.
 > Recommendation: A — it is the only direction that directly answers the product question. B is framework churn. C is batch-scope drift.
 > **Selected: A** by delegated recommendation.

**Q2: How should this WF treat existing product seams?**
- A) Reuse the existing path as far as possible and only change what `MSCA-PF-2025` directly forces.
- B) Opportunistically refactor old seams to make future onboarding nicer.
- C) Avoid touching any seam even if the call cannot land cleanly.
 > Recommendation: A — it balances realism and scope control. B is a refactor trap. C is too brittle to support a real onboarding attempt.
 > **Selected: A** by delegated recommendation.

**Q3: What should happen if `MSCA-PF-2025` immediately demands major UI/runtime redesign?**
- A) Treat that as a scoping warning or blocker and surface it early.
- B) Expand this WF to include the redesign so the call still ships.
- C) Hide the issue until implementation clarifies it.
 > Recommendation: A — it keeps the planning honest. B would turn the WF into another platform umbrella. C delays obvious risk.
 > **Selected: A** by delegated recommendation.

**Q4: What should be the implicit deliverable shape?**
- A) One real canonical call plus minimum supporting evidence.
- B) One call plus generic onboarding toolkit improvements.
- C) Mostly risk/notes artifacts with implementation deferred.
 > Recommendation: A — it anchors the workflow in a concrete product result. B and C both weaken the “one real call” contract.
 > **Selected: A** by delegated recommendation.

**Q5: What should this section reject explicitly?**
- A) Any second deliverable that becomes the real center of gravity instead of landing `MSCA-PF-2025`.
- B) Only obviously unrelated work.
- C) Nothing explicit; trust later phases to stay disciplined.
 > Recommendation: A — the workflow needs an explicit anti-shadow-scope rule. B is too vague. C is how drift wins.
 > **Selected: A** by delegated recommendation.

## Section 5 — Constraints

**Q1: How many calls are in scope?**
- A) Exactly one: `MSCA-PF-2025`.
- B) One primary call plus a backup call if time allows.
- C) Multiple calls if they share the same family.
 > Recommendation: A — it is the hard scope lock. B and C reopen the batch-expansion behavior this WF is supposed to prevent.
 > **Selected: A** by delegated recommendation.

**Q2: When does the source-upload gate apply?**
- A) Before any substantive YAML structure or criteria authoring for `MSCA-PF-2025`.
- B) Only before finalizing the YAML.
- C) Only if ambiguity appears.
 > Recommendation: A — that is the repo's actual source-gating discipline. B and C allow speculative authoring to leak in.
 > **Selected: A** by delegated recommendation.

**Q3: What categories of work are out of scope by default?**
- A) Frontend redesign, cross-call hardening, ops/governance cleanup, and a second call.
- B) Only frontend redesign; other adjacent improvements are acceptable.
- C) Keep scope flexible if the code area already needs cleanup.
 > Recommendation: A — it closes the most common loopholes. B and C would both produce fake progress.
 > **Selected: A** by delegated recommendation.

**Q4: How strict should task sizing remain in later phases?**
- A) Keep tasks small enough to preserve bounded-step discipline and safe verification.
- B) Allow larger tasks because call onboarding naturally touches many surfaces.
- C) Ignore file/task discipline until implementation starts.
 > Recommendation: A — the point of discipline is to stop scope spillover from hiding inside “necessary onboarding.” B and C remove that protection.
 > **Selected: A** by delegated recommendation.

**Q5: What is the limit on compatibility fixes?**
- A) Only the smallest direct fix needed for this one call to land safely.
- B) Any reusable improvement discovered along the way.
- C) None, even if the call cannot land otherwise.
 > Recommendation: A — it is the workable narrow boundary. B is platform creep. C would make the WF artificially brittle.
 > **Selected: A** by delegated recommendation.

## Section 6 — Risks / Unknowns

**Q1: What is the biggest execution risk?**
- A) Spending most of the WF on new onboarding machinery instead of landing `MSCA-PF-2025`.
- B) Moving too fast and landing the call with minimal evidence.
- C) Not enough documentation polish in the artifacts.
 > Recommendation: A — that is the core fake-progress risk this WF was created to avoid. B matters, but the repo's current failure mode is more likely A. C is comparatively minor.
 > **Selected: A** by delegated recommendation.

**Q2: What is the main structural unknown about `MSCA-PF-2025`?**
- A) Whether it fits the current structured-review path without requiring broad runtime or UX redesign.
- B) Whether the repo can store one more YAML file.
- C) Whether MSCA is strategically interesting enough as a program family.
 > Recommendation: A — it is the real product-fit uncertainty. B is trivial. C was already resolved by scope selection.
 > **Selected: A** by delegated recommendation.

**Q3: What is the main governance/backlog risk?**
- A) Treating stale multi-call backlog wording as still active and accidentally bloating the WF.
- B) Having too many artifact files for one workflow.
- C) Forgetting to mention MSCA in future product copy.
 > Recommendation: A — stale backlog text is a real source of scope corruption here. B and C are lower-order issues.
 > **Selected: A** by delegated recommendation.

**Q4: What role does the source-upload gate play in risk control?**
- A) It prevents false confidence from speculative YAML authoring before official documents are in hand.
- B) It is mostly documentation ceremony.
- C) It can be relaxed if the call looks familiar.
 > Recommendation: A — this is a substantive correctness gate, not ceremony. B and C would undermine the whole source-grounding policy.
 > **Selected: A** by delegated recommendation.

**Q5: What should Phase 0.2 treat as a likely blocker?**
- A) Any ambiguity that leaves room for this WF to become broader than one real `MSCA-PF-2025` onboarding.
- B) Only direct syntax or wording issues.
- C) No blockers unless implementation has already started.
 > Recommendation: A — ambiguity in scope/evidence is exactly what the audit should fail closed on. B is too shallow. C defeats the point of Phase 0 review.
 > **Selected: A** by delegated recommendation.
