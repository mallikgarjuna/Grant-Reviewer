<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md -->
# WF-0075 — ERC PoC Proof-Call Fidelity Completion

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-12

## Preflight Step 1 — Long-Form Problem Intake

**User-provided narrative adopted as baseline problem framing**

WF-0074 is treated as already true for this workflow: it successfully added the subordinate-prompt authoring mechanism, template default, docs/checklist hardening, governance updates, and compatibility posture. The remaining defect is not that the repo lacks a way to represent subordinate prompts.

The unresolved problem is that the real proof-call `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` still encodes subordinate prompts only for ERC PoC evaluation element `1.a Breakthrough Innovation Potential`. The same proof-call still does not encode the detailed official subordinate prompts for `1.b Approach and Methodology` and `1.c Principal Investigator - Strategic Leadership and Project Management`, even though those prompts are present on page 43 of `wp_horizon-erc-2026_en.pdf`.

That means the repository can now support high-fidelity subordinate-prompt authoring in principle, but the canonical proof artifact used to substantiate that claim remains only partially encoded. As long as a real proof-call can still be treated as fidelity-complete in that state, the closure standard is fail-open.

WF-0075 should therefore focus on completing the ERC PoC proof-call and adding fail-closed coverage proof so partial subordinate-prompt encoding in a real proof-call cannot pass as full canonical fidelity. Runtime review consumption remains intentionally out of scope unless separately re-approved.

## Preflight Step 2 — Repo Reality Snapshot

- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` currently encodes typed subordinate prompts for `1.a` only.
- `1.b` and `1.c` remain flat evaluation elements even though page 43 includes official subordinate prompts for them.
- `backend/app/schemas/call_definitions_v2.py` already supports typed `subordinate_prompts`; representability is not the main blocker anymore.
- `docs/call-yaml/authoring-workflow.md`, `docs/call-yaml/onboarding-checklist.md`, `docs/logs/decisions.md`, and `docs/memory/domain/project_docs.md` already preserve the WF-0074 governance and runtime-boundary posture.
- WF-0074's approved bounded compatibility posture remains prior truth: existing flat canonical YAMLs stay temporarily compatible unless a later phase explicitly narrows that policy with proof and re-approval.
- The remaining gap is closure proof: the repo still needs a fail-closed way to distinguish absent-by-source, fully encoded, and partially encoded subordinate-prompt coverage for a real proof-call.

## Section 1 — Problem Statement

**Q1: What is the root defect WF-0075 should name precisely?**
- A) The schema/governance mechanism for subordinate prompts is still incomplete.
- B) The real ERC PoC proof-call remains only partially encoded against the official page-43 subordinate prompts, so the repo cannot honestly claim full canonical fidelity for that proof-call.
- C) The structured-review runtime still does not consume subordinate prompts.
  > Recommendation: B — this carries forward the actual unresolved defect. A reopens WF-0074 work that is already done. C is true but intentionally out of scope for this workflow.
  > **Selected: B**

**Q2: How should this WF describe the status of `1.a`, `1.b`, and `1.c`?**
- A) `1.a` is already the proof of fidelity, so the remaining issue is minor completeness polish.
- B) `1.a` proves the mechanism works, but the proof-call is still fidelity-incomplete until `1.b` and `1.c` also encode the official subordinate prompts from page 43.
- C) All three elements should be treated as equally incomplete from scratch.
  > Recommendation: B — it preserves the exact prior truth without minimizing the remaining defect. A is too soft and would let a partial proof-call look complete. C erases the fact that `1.a` already demonstrates the landed mechanism.
  > **Selected: B**

**Q3: What must “fidelity complete” mean for this WF?**
- A) The proof-call contains some subordinate prompts where useful.
- B) The proof-call preserves all official subordinate prompts on page 43 across `1.a`, `1.b`, and `1.c`, or explicitly proves a prompt is absent by source.
- C) The runtime uses subordinate prompts during review generation.
  > Recommendation: B — this is the only option that closes the real gap fail closed. A preserves the current failure mode. C widens the workflow into deferred runtime-consumption work.
  > **Selected: B**

**Q4: What failure mode must the problem statement call out explicitly?**
- A) Real proof-calls can currently look compliant even when subordinate prompts are only partially encoded.
- B) YAML files are too long when subordinate prompts are added.
- C) The UI does not expose subordinate prompts directly.
  > Recommendation: A — this is the exact fail-open condition that makes the fidelity claim incomplete today. B and C are unrelated to the motivating defect.
  > **Selected: A**

**Q5: What scope boundary must be embedded directly into the problem framing?**
- A) This WF may expand into runtime-consumption redesign if the implementation gets awkward.
- B) This WF is proof-call fidelity completion plus fail-closed coverage proof; runtime consumption stays out of scope unless explicitly re-approved.
- C) This WF should broaden into multi-call migration so the rule is globally uniform.
  > Recommendation: B — it locks the narrow defect and prevents familiar scope drift. A is a scope escape hatch. C turns one proof-call completion WF into a migration program.
  > **Selected: B**

## Section 2 — Desired Outcome

**Q1: What is the primary outcome this workflow should deliver?**
- A) A fully page-43-complete ERC PoC proof-call plus evidence that partial encoding cannot pass as complete.
- B) A broad refresh of the subordinate-prompt authoring mechanism.
- C) A runtime redesign that consumes subordinate prompts.
  > Recommendation: A — it addresses the live defect directly. B relitigates already-landed work. C widens into explicitly deferred runtime scope.
  > **Selected: A**

**Q2: Which artifact should carry the main proof burden?**
- A) `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` as the real canonical proof-call.
- B) A separate fixture only.
- C) Docs text only.
  > Recommendation: A — the defect lives in the real proof-call, so closure must prove the real artifact is now complete. B is acceptable only as a supplemental seam. C cannot prove artifact truth.
  > **Selected: A**

**Q3: What must the coverage proof distinguish?**
- A) Only whether the YAML validates.
- B) Whether subordinate prompts are absent by source, fully encoded, or only partially encoded.
- C) Whether the runtime became more specific.
  > Recommendation: B — this is the minimum fail-closed distinction the repo currently lacks. A is too weak. C is out of scope.
  > **Selected: B**

**Q4: How much supporting tightening is acceptable?**
- A) The smallest test/doc/checklist tightening needed to enforce honest proof-call completeness.
- B) A broad rewrite of the call-authoring system.
- C) No supporting tightening at all; just edit the YAML.
  > Recommendation: A — it matches the narrow workflow boundary. B is over-scoped. C would leave the closure rule fail-open.
  > **Selected: A**

**Q5: What claim must remain explicitly out of scope in the desired outcome?**
- A) Immediate structured-review runtime consumption of subordinate prompts.
- B) Canonical proof-call completion.
- C) Source traceability to page 43.
  > Recommendation: A — the workflow must not overclaim beyond the expectations-only runtime seam. B and C are core in-scope requirements.
  > **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary actor operating the changed surfaces in this workflow?**
- A) A maintainer or coding agent updating canonical YAML and closure evidence.
- B) A researcher end-user interacting with review results.
- C) A frontend designer.
  > Recommendation: A — the direct surfaces are canonical YAML, tests, and narrow governance artifacts. B is an indirect beneficiary. C is unrelated.
  > **Selected: A**

**Q2: Who is the primary beneficiary of a correct closure rule here?**
- A) Future maintainers and agents who need to know whether a real proof-call is actually fidelity-complete.
- B) Only the schema author.
- C) Only runtime-service owners.
  > Recommendation: A — this WF hardens repository truth and prevents future false closure. B is too narrow. C misframes the scope around runtime work.
  > **Selected: A**

**Q3: What trust surface is this workflow mainly protecting?**
- A) The canonical proof-call and its verification evidence.
- B) The frontend interaction model.
- C) The prompt-engine runtime.
  > Recommendation: A — that is where the defect lives. B and C are outside the narrow target.
  > **Selected: A**

**Q4: What actor-model mistake should the workflow avoid?**
- A) Treating this as a user-facing product feature instead of a repository-truth and closure-integrity fix.
- B) Treating this as source-grounded authoring work.
- C) Treating page-43 fidelity as the main source anchor.
  > Recommendation: A — misclassifying the workflow would encourage runtime and UI scope drift. B and C are actually required viewpoints.
  > **Selected: A**

**Q5: What tradeoff priority should govern decisions?**
- A) Honest proof-call completeness and fail-closed evidence first; implementation convenience second.
- B) Implementation speed first, evidence later.
- C) Perfect symmetry between proof-call and runtime work.
  > Recommendation: A — the current defect exists because a partial proof artifact could still look acceptable. B repeats that mistake. C blurs in-scope and out-of-scope surfaces.
  > **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest credible implementation direction?**
- A) Complete `1.b` and `1.c` in the real ERC PoC proof-call using the existing subordinate-prompt shape and add fail-closed coverage proof for completeness.
- B) Replace the subordinate-prompt contract with a new generic schema.
- C) Redesign runtime consumption first and come back to the proof-call later.
  > Recommendation: A — it uses the already-landed mechanism and fixes the actual proof artifact. B and C both widen scope unnecessarily.
  > **Selected: A**

**Q2: Where should the first proof of closure live?**
- A) In tests or equivalent executable evidence tied directly to the real proof-call and page-43 source expectations.
- B) In brainstorm text only.
- C) In runtime review-output examples.
  > Recommendation: A — closure needs a replayable, fail-closed seam. B is too soft. C widens into runtime territory.
  > **Selected: A**

**Q3: What kind of supporting documentation change is acceptable?**
- A) Only a narrow correction if needed to make partial encoding explicitly insufficient for a real proof-call.
- B) Rewriting the full authoring guidance stack.
- C) No documentation updates under any circumstance.
  > Recommendation: A — it preserves WF-0074 as prior truth while allowing necessary fail-closed clarification. B is overkill. C can leave closure semantics implicit.
  > **Selected: A**

**Q4: How should the workflow treat the three-state distinction?**
- A) Make it explicit in the closure proof and any required supporting contract text.
- B) Leave it implicit and assume future maintainers will infer it.
- C) Collapse absent-by-source and partially encoded into the same state.
  > Recommendation: A — the point of the WF is to prevent false completeness. B and C both preserve ambiguity.
  > **Selected: A**

**Q5: What broadening move should be explicitly rejected?**
- A) Multi-call migration or runtime redesign as part of this same WF.
- B) Completing the ERC PoC proof-call itself.
- C) Traceability to page 43.
  > Recommendation: A — this is the main shape of likely scope drift. B and C are core in-scope needs.
  > **Selected: A**

## Section 5 — Constraints

**Q1: What prior truth must remain fixed during this workflow?**
- A) WF-0074 already landed the subordinate-prompt authoring mechanism, template default, docs/checklist hardening, governance updates, and compatibility posture.
- B) WF-0074 failed completely and must be reopened.
- C) The ERC PoC proof-call is already fully complete.
  > Recommendation: A — this is the starting contract for WF-0075. B and C are both false and would distort scope.
  > **Selected: A**

**Q2: What source-grounding constraint is mandatory?**
- A) Every completeness claim must stay traceable to page 43 of `wp_horizon-erc-2026_en.pdf`.
- B) Similar ERC calls can be used to infer missing prompts.
- C) Prompt wording can be normalized freely for convenience.
  > Recommendation: A — this keeps the workflow defensible. B and C would weaken fidelity and traceability.
  > **Selected: A**

**Q3: What runtime boundary must stay explicit?**
- A) Runtime remains expectations-only and stays out of scope unless separately re-approved.
- B) Runtime may be widened implicitly if tests are convenient.
- C) Runtime must become in-scope to close the WF.
  > Recommendation: A — this preserves the prior approved boundary. B and C both create unapproved expansion.
  > **Selected: A**

**Q4: What planning discipline should constrain the implementation later?**
- A) Prefer the minimal proof surfaces needed to close the exact defect safely.
- B) Take the chance to clean up all adjacent fidelity issues repo-wide.
- C) Decide scope opportunistically during coding.
  > Recommendation: A — this keeps the WF tractable and aligned to the defect. B and C both encourage sprawl.
  > **Selected: A**

**Q5: What must not be accepted as a shortcut?**
- A) Treating a YAML patch alone as sufficient without fail-closed coverage proof.
- B) Reusing the existing subordinate-prompt schema.
- C) Checking the real proof-call artifact.
  > Recommendation: A — the missing closure proof is half the defect. B and C are part of the intended narrow solution.
  > **Selected: A**

**Q6: What compatibility rule from WF-0074 must this workflow preserve unless it is explicitly re-approved later?**
- A) Existing flat canonical YAMLs remain temporarily compatible, while WF-0075 completes one real proof-call and must not silently turn that into a repo-wide rejection rule.
- B) WF-0075 should tighten the schema immediately so all remaining flat canonical YAMLs fail by default.
- C) Compatibility posture no longer matters because the proof-call is real.
  > Recommendation: A — this carries forward the approved WF-0074 boundary and prevents scope drift from one proof-call completion into unapproved repo-wide migration or rejection work.
  > **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the highest closure risk?**
- A) The repo still overclaims fidelity after only partial subordinate-prompt encoding.
- B) The YAML gets somewhat longer.
- C) The branch name becomes verbose.
  > Recommendation: A — this is the actual integrity risk the workflow exists to remove. B and C are trivial.
  > **Selected: A**

**Q2: What is the biggest proof-design risk?**
- A) Choosing evidence that proves schema validity but not page-43 completeness.
- B) Adding too many markdown headings.
- C) Using the real proof-call artifact.
  > Recommendation: A — a weak proof seam would let the same defect survive under stronger wording. B and C are irrelevant or backwards.
  > **Selected: A**

**Q3: What is the biggest scope risk?**
- A) Drifting back into runtime consumption or generic redesign because those surfaces are nearby from WF-0074.
- B) Staying focused on `1.b` and `1.c`.
- C) Using the same official source page as the anchor.
  > Recommendation: A — this is the most likely way the WF becomes unfocused. B and C are strengths, not risks.
  > **Selected: A**

**Q4: What unknown should Phase 1 clarify first?**
- A) The smallest fail-closed seam that proves complete versus partial subordinate-prompt coverage for the real proof-call.
- B) Whether to redesign the structured reviewer.
- C) Which additional agencies should migrate now.
  > Recommendation: A — this determines the narrowest credible implementation plan. B and C are outside scope.
  > **Selected: A**

**Q5: What secondary uncertainty is worth tracking?**
- A) Whether a narrow doc/checklist/governance correction is needed so the three-state distinction is explicit outside tests.
- B) Whether to rename evaluation elements.
- C) Whether to broaden to multi-call onboarding.
  > Recommendation: A — it is plausible and still narrow. B is cosmetic. C is out of scope.
  > **Selected: A**

## Section 7 — MVP Definition

**Q1: What must absolutely exist for MVP?**
- A) The ERC PoC proof-call fully encodes page-43 subordinate prompts for `1.a`, `1.b`, and `1.c`.
- B) A new generic hierarchy model.
- C) Runtime prompt consumption.
  > Recommendation: A — this is the non-negotiable core of the WF. B and C are outside the narrow MVP.
  > **Selected: A**

**Q2: What proof must accompany the artifact change?**
- A) Fail-closed evidence that partial subordinate-prompt encoding in a real proof-call does not qualify as fidelity complete.
- B) Only a manual note saying the file was updated.
- C) A runtime review demo.
  > Recommendation: A — without this, the closure rule remains soft. B is insufficient. C widens scope.
  > **Selected: A**

**Q3: What supporting change is acceptable within MVP if needed?**
- A) The smallest test/doc/checklist/governance tightening needed to distinguish absent, complete, and partial states.
- B) Broad repo-wide migration tasks.
- C) Frontend surfacing of subordinate prompts.
  > Recommendation: A — this is the narrow, justified support scope. B and C are out of scope.
  > **Selected: A**

**Q4: What must MVP explicitly exclude?**
- A) Runtime-consumption redesign.
- B) Encoding `1.b` and `1.c`.
- C) Source-traceability proof.
  > Recommendation: A — this is the main excluded adjacent surface. B and C are required for closure.
  > **Selected: A**

**Q5: What is the minimum acceptable closure claim after MVP?**
- A) The ERC PoC proof-call is now a fidelity-complete canonical representation of page 43, and partial encoding would now fail closed.
- B) The repo can represent subordinate prompts in some situations.
- C) Runtime reviews are now subordinate-prompt-aware.
  > Recommendation: A — that is the honest claim this WF can close. B understates the intended outcome. C overclaims beyond scope.
  > **Selected: A**

**Q6: What additional closure proof must exist before any proceed or ship recommendation?**
- A) A `main...HEAD`-anchored scope proof that cites the approved WF-0074 artifacts and shows compatibility posture, proof-call policy, and runtime-boundary honesty were preserved without hallucinated scope drift.
- B) Only a note that the latest files were reviewed manually.
- C) A runtime demo showing no obvious errors.
  > Recommendation: A — the workflow now depends on approved prior-phase truth, so closure must prove it stayed inside that boundary instead of assuming it.
  > **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: Which tempting adjacent initiative must be explicitly postponed?**
- A) Structured-review runtime consumption of subordinate prompts.
- B) Completing the ERC PoC proof-call.
- C) Page-43 traceability.
  > Recommendation: A — this is the most tempting nearby expansion and must stay deferred. B and C are core to this WF.
  > **Selected: A**

**Q2: What broader repo activity must remain out of scope?**
- A) Multi-call canonical migration.
- B) Testing the real ERC PoC proof-call.
- C) Checking docs for narrow corrective wording.
  > Recommendation: A — repo-wide migration would swamp the narrow proof-call completion goal. B and C may be required in narrow form.
  > **Selected: A**

**Q3: What modeling direction must remain out of scope?**
- A) Generic ontology or broader schema redesign.
- B) Reusing the existing subordinate-prompt structure.
- C) Source-grounded page-43 mapping.
  > Recommendation: A — the mechanism is already landed; this WF is not a modeling rethink. B and C are intended inputs.
  > **Selected: A**

**Q4: What closure shortcut must be rejected as a non-goal?**
- A) Declaring the proof-call "good enough" while `1.b` or `1.c` remain only partially encoded.
- B) Proving completeness against page 43.
- C) Using fail-closed tests.
  > Recommendation: A — this is the exact false-closure path the WF must block. B and C are part of the real goal.
  > **Selected: A**

**Q5: What historical work should not be reopened except for a narrow correction?**
- A) WF-0074 mechanism/governance implementation.
- B) The ERC PoC proof-call itself.
- C) The need for source traceability.
  > Recommendation: A — WF-0074 is prior truth and should not be re-litigated here. B and C are directly in scope.
  > **Selected: A**
