<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0063-universal-node-visibility-reviewability.md -->
# WF-0063 — Universal Node Visibility Reviewability

Artifact: brainstorm-qna
Version: v0.1
Status: Draft Complete
Last Updated: 2026-03-08

---

This file captures the full brainstorm interview transcript for WF-0063.
The main brainstorm artifact remains the SSOT for decisions and contracts.

## Preflight Intake

### User Narrative (accepted as-is)

We have a structural fidelity problem in the universal submit/review flow for real funding calls, exposed clearly by `MSCA-PF-2025`.

Today, the UI effectively treats `node_expectations` as the gate for whether a proposal node appears at all. That means the UI only shows sections that are directly mapped to evaluation criteria/elements. In `MSCA-PF-2025`, this causes Part B1 sections 1-3 to appear, but hides other official proposal nodes such as the abstract and Part B2 sections 4-8, even though those sections are part of the real application structure and may matter for context, completeness, or interpretation.

This is a modeling problem, not just a frontend bug. We currently overload one concept, `node_expectations`, to mean at least three different things:
1. this node is an official proposal section,
2. this node should appear in the UI,
3. this node is directly reviewable against evaluation criteria/elements.

Those are not the same thing. For MSCA-PF-2025, the official source documents support the existence of Part A, Part B1, and Part B2 as real proposal structure. But the award criteria are centered on the scored evaluation dimensions reflected mainly in B1. So the current behavior is structurally inaccurate, while the obvious quick fix, adding fake expectations to B2 just to force visibility, would be evaluation-model corruption.

What I want this workflow to solve is the contract split between structural visibility, primary criterion-grounded reviewability, and supporting/context-only proposal content. After this workflow, PeerLens should be able to represent all official proposal nodes in a call definition without pretending that every visible node is a primary scored review node. The UI should be able to show all relevant official sections for a call, while the review engine remains strict about which sections can generate normal criterion-grounded review cards.

I want us to stay strict on source-grounded evaluation criteria/elements. We should not invent criterion mappings for B2 or other supporting sections unless the source documents clearly justify them. At the same time, I do want abstract and Part B2 sections 4-8 to be usable in the product. My current view is that these sections should at least support visibility in the UI and may also feed context, cross-section interpretation, and some compliance or completeness checks. But they should not automatically generate the same kind of direct scored review cards as B1 sections 1-3 unless we have explicit grounding for that.

For this workflow, I want us to decide the right product and contract model first, not jump into implementation detail too early. The repo-safe goal is to define a universal rule that works across agencies, not just patch MSCA. The likely direction is that every official proposal section can exist as a node and be visible in the UI, while only source-justified primary review nodes carry direct expectation mappings. Supporting nodes may still influence the review flow as context or compliance inputs.

Current pain:
- real proposal structure is hidden from users,
- the UI misrepresents what belongs to the application,
- call authors are pushed toward abusing `node_expectations` just to make sections visible,
- the universal review engine is at risk of conflating visibility with reviewability.

Desired behavior after this workflow:
- UI visibility does not depend on `node_expectations`,
- primary criterion-grounded review remains strict and source-grounded,
- supporting sections can be captured and used without fake scoring semantics,
- the contract becomes clearer for future calls beyond MSCA.

Constraints:
- keep this workflow repo-safe and narrow,
- preserve backward compatibility where feasible,
- avoid a large multi-call migration in one step,
- do not introduce speculative evaluation semantics,
- keep the first implementation slice small enough to validate quickly.

Non-goals for this workflow:
- not redesigning the full review engine end-state,
- not reauthoring many calls at once,
- not inventing new scoring logic for unsupported sections,
- not solving every agency-specific nuance in one pass.

The core question for this workflow is:
How should PeerLens model and render official proposal nodes that are real and useful, but not directly mapped to award-criteria review cards?

## Preflight Repo Snapshot (Read-Only)

- `frontend/src/lib/submit/renderModel.ts` renders only nodes with `has_expectations=true`, so visibility is hard-coupled to expectations today.
- `frontend/src/components/submit/UniversalSubmitForm.tsx` uses that rendered node set for both display and payload assembly, so visibility and submit semantics are coupled.
- WF-0035 intentionally scoped universal submit to flat nodes and explicit unsupported states rather than a richer node-role model.
- Current contracts expose `has_expectations` as a derived hint, but not a separate visible/supporting/primary concept.
- Parking-lot history already suggests future cross-node context semantics, which reinforces that current contracts are too narrow for supporting nodes.

## Section 1 — Problem Statement

**Q1: What is the primary problem this WF should claim to solve?**
- A) UI completeness only: official proposal sections should appear even if non-primary.
- B) Contract split: separate structural visibility, primary reviewability, and supporting/context semantics.
- C) Review-engine enhancement: supporting sections should actively influence generated review behavior.
> Recommendation: B — It addresses the root cause without prematurely promising engine behavior. A is too symptom-level and risks another local patch. C may be directionally valuable later, but it jumps straight to behavioral semantics before the contract is made coherent.
> **Selected: B**

**Q2: What is the narrowest user-facing pain we should optimize for first?**
- A) Researchers cannot see the real application structure for a selected call.
- B) Call authors are forced to abuse `node_expectations` to make sections visible.
- C) Review outputs are semantically misleading because hidden sections are ignored.
> Recommendation: A — It is the clearest MVP pain and easiest to falsify. B matters but is more of an authoring/maintainer pain. C may be true, but it overcommits to downstream behavioral claims before the contract split is nailed down.
> **Selected: A**

**Q3: For this WF, how universal should the problem statement be?**
- A) MSCA-specific fix framed around `MSCA-PF-2025`.
- B) Universal contract problem using `MSCA-PF-2025` as the proof example.
- C) Broad multi-agency review-model overhaul.
> Recommendation: B — Narrow proof target, universal contract framing. A is too local and would likely produce an overfit patch. C is too broad for a repo-safe workflow and invites unbounded scope.
> **Selected: B**

**Q4: What should count as “wrong” in the current behavior?**
- A) Hiding any official narrative/supporting node from UI is wrong.
- B) Hiding only nodes that materially affect interpretation/completeness is wrong.
- C) Current behavior is acceptable as long as primary scored nodes are shown.
> Recommendation: B — More defensible than “everything visible,” but stricter than current behavior. A may force visibility promises for nodes that should remain conditional or internal. C preserves the defect you are trying to correct.
> **Selected: B**

**Q5: What is the strongest boundary we should state now?**
- A) This WF will not invent new evaluation criteria/elements mappings for unsupported nodes.
- B) This WF will not change scoring behavior at all.
- C) This WF will not touch backend contracts, only UI behavior.
> Recommendation: A — It preserves source-grounded evaluation fidelity without overconstraining the eventual slice. B might be too rigid if context-aware handling requires small contract adjustments. C is too implementation-prescriptive this early and likely false if the root problem is contractual.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: What should be the clearest success state after this WF?**
- A) Official visible/supporting nodes appear in the UI without fake expectations.
- B) Supporting nodes appear and also influence primary review generation.
- C) All nodes appear and all can receive review cards.
> Recommendation: A — It is the cleanest first success state and preserves evaluation fidelity. B may be a future benefit but should not be promised yet. C would collapse the distinction this WF exists to protect.
> **Selected: A**

**Q2: What should become easier for call authors after this WF?**
- A) Author full official structure without abusing `node_expectations`.
- B) Encode cross-node influence directly in YAML for every supporting node.
- C) Skip structural nodes entirely unless scored.
> Recommendation: A — It removes the current pressure to mis-model calls. B is too advanced for the first move. C preserves the current structural fidelity defect.
> **Selected: A**

**Q3: What should become easier for researchers after this WF?**
- A) See and draft the real proposal structure in one place.
- B) Get feedback on every visible section immediately.
- C) Ignore section distinctions and paste everything into one generalized flow.
> Recommendation: A — It matches the proven pain and keeps the claim precise. B overpromises review coverage. C contradicts the structured-call direction.
> **Selected: A**

**Q4: What product capability should become possible, but not fully solved yet?**
- A) Later use of supporting nodes for context/compliance without redefining primary review semantics.
- B) Automatic rescoring of B1 based on B2 content.
- C) Agency-specific custom review engines per node type.
> Recommendation: A — It preserves the forward path without turning this WF into engine redesign. B is speculative. C is far too broad for this stage.
> **Selected: A**

**Q5: What is “good enough” for MVP success in this WF?**
- A) A universal contract direction is defined and one proof call can represent visible-but-non-primary nodes safely.
- B) Every existing structured call is migrated to the new model immediately.
- C) The final universal engine semantics for context-aware review are fully designed.
> Recommendation: A — It is repo-safe and testable. B is too large. C is too abstract and premature.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary actor for this WF?**
- A) Researchers using the universal submit flow for real structured calls.
- B) Internal maintainers authoring call YAML.
- C) Review admins validating call onboarding.
> Recommendation: A — Researcher-facing structural correctness is the clearest user problem. B and C matter, but they are secondary beneficiaries.
> **Selected: A**

**Q2: How should maintainers be treated in this WF framing?**
- A) Secondary actor who benefits from cleaner authoring semantics.
- B) Equal primary actor with researchers.
- C) Out of scope entirely.
> Recommendation: A — Maintainer relief is real, but the WF should stay anchored on the researcher-facing defect. B dilutes the problem statement. C ignores a meaningful contract-quality benefit.
> **Selected: A**

**Q3: What is the current researcher behavior we are correcting?**
- A) They select a call and assume the UI reflects the real application structure.
- B) They already know the UI is partial and work around it externally.
- C) They mostly submit one section at a time and do not care about full structure.
> Recommendation: A — This is the most useful problem framing for product correctness. B may happen, but it normalizes the defect. C understates the structural trust issue.
> **Selected: A**

**Q4: What is the main frustration for authors/maintainers?**
- A) They must choose between structural fidelity and semantic fidelity.
- B) They lack enough criteria to score every node.
- C) They need more custom frontend forms per call.
> Recommendation: A — That is the real modeling trap. B is a symptom. C is less central to this WF.
> **Selected: A**

**Q5: What user scope should MVP exclude?**
- A) Internal-only admin workflows.
- B) External researchers on structured calls.
- C) Maintainers authoring new real calls.
> Recommendation: A — This WF is about the universal researcher-facing path, not admin tooling. Excluding B or C would remove the main value.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction this brainstorm should lean toward?**
- A) Separate node roles so official nodes can be visible without all being primary reviewed nodes.
- B) Keep one node model and infer different roles indirectly from `node_expectations`.
- C) Add expectations broadly and soften their meaning in prompts/UI.
> Recommendation: A — It addresses the root contract problem cleanly. B preserves ambiguity. C corrupts authoring semantics.
> **Selected: A**

**Q2: What should be the first proof target?**
- A) `MSCA-PF-2025` only, as the proof call.
- B) MSCA plus ERC in the same WF.
- C) All currently structured calls at once.
> Recommendation: A — It keeps scope tight and grounded. B and C are larger migration exercises.
> **Selected: A**

**Q3: How should this WF treat supporting nodes initially?**
- A) Visible and representable now; richer behavioral use can follow later.
- B) Fully context-aware in the first slice.
- C) Visible only through separate per-call hacks.
> Recommendation: A — It preserves forward progress without overcommitting. B is too large. C breaks the universal-contract goal.
> **Selected: A**

**Q4: What should happen to primary review semantics?**
- A) Preserve strict source-grounded criteria-linked review for primary nodes.
- B) Relax semantics so any visible node can be reviewed similarly.
- C) Revisit all criteria mappings as part of this WF.
> Recommendation: A — This is the core safety boundary. B and C invite speculative semantics and scope creep.
> **Selected: A**

**Q5: What should this brainstorm explicitly avoid?**
- A) Full engine redesign and multi-call migration promises.
- B) Any discussion of future extensibility.
- C) Any contract framing beyond the immediate MSCA symptom.
> Recommendation: A — It keeps the WF honest while still allowing a universal direction. B is too restrictive. C overfits the solution to one call.
> **Selected: A**

## Section 5 — Constraints

**Q1: What is the main scope constraint?**
- A) Keep the WF repo-safe and narrow.
- B) Solve the whole universal review model while the issue is visible.
- C) Rework all structured-call assumptions at once.
> Recommendation: A — It is the only realistic path for a safe workflow. B and C are planning traps.
> **Selected: A**

**Q2: What backward-compatibility stance should guide planning?**
- A) Preserve existing behavior where feasible and isolate the proof change carefully.
- B) Accept broad breaking changes to simplify the new model.
- C) Avoid any contract change even if the root problem remains.
> Recommendation: A — It balances realism with safety. B is too risky. C blocks the needed correction.
> **Selected: A**

**Q3: What data-authoring constraint is non-negotiable?**
- A) No speculative criteria/elements mappings for non-primary nodes.
- B) Every visible node must get at least one expectation.
- C) Supporting nodes can be mapped heuristically if the UX is better.
> Recommendation: A — This preserves source-grounded integrity. B and C would undermine the model.
> **Selected: A**

**Q4: What migration constraint should we state?**
- A) No bulk multi-call reauthoring in the first slice.
- B) Update all canonical YAMLs immediately to stay consistent.
- C) Ignore existing calls and prototype in isolation.
> Recommendation: A — It is the right MVP discipline. B is too broad. C reduces practical value.
> **Selected: A**

**Q5: What delivery constraint matters most?**
- A) First slice must be small enough to validate quickly on one proof call.
- B) First slice must include final engine semantics.
- C) First slice must solve every review-detail implication.
> Recommendation: A — It preserves momentum and proof quality. B and C are too large.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the most fragile assumption?**
- A) Visibility can be separated from reviewability without deeper downstream consequences.
- B) Users only care about missing sections in MSCA.
- C) Existing tests will adapt with minimal changes automatically.
> Recommendation: A — This is the core architectural unknown. B is too local. C is optimistic and unproven.
> **Selected: A**

**Q2: What rework risk is highest?**
- A) The team overdesigns the universal engine before proving the minimal contract split.
- B) The MSCA YAML needs minor wording updates.
- C) The issue disappears once more expectations are added.
> Recommendation: A — This is the classic way the effort can bloat and stall. B is not the main risk. C is exactly the anti-pattern being rejected.
> **Selected: A**

**Q3: What semantic risk must be guarded against?**
- A) Supporting nodes accidentally being treated as primary scored review nodes.
- B) Researchers wanting too many fields visible.
- C) Calls remaining agency-specific.
> Recommendation: A — This is the key fidelity risk. B is manageable. C is not the main semantic threat in this WF.
> **Selected: A**

**Q4: What operational risk is likely?**
- A) Hidden coupling across submit, compliance, and review-detail paths.
- B) The branch name being too long.
- C) The MSCA source files being unavailable.
> Recommendation: A — The current repo already couples these paths. B is irrelevant. C is not the present blocker.
> **Selected: A**

**Q5: What must Phase 1 validate early?**
- A) Exact contract boundaries and compatibility strategy for visible-but-non-primary nodes.
- B) Full prompt design for context-aware review.
- C) Migration plan for every existing call.
> Recommendation: A — It is the highest-value validation. B and C are later-stage concerns.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: If limited to 2-3 days, what must exist?**
- A) A safe universal contract direction and one proof call that can represent visible-but-non-primary nodes.
- B) Full context-aware review behavior for supporting nodes.
- C) Complete migration of all structured calls.
> Recommendation: A — It is the smallest functional slice worth shipping. B and C are too large.
> **Selected: A**

**Q2: What primary behavior must remain strict in MVP?**
- A) Criteria-grounded review for primary nodes only.
- B) Review cards for every visible node.
- C) One flattened scoring model across node types.
> Recommendation: A — It preserves evaluation fidelity. B and C break the intended distinction.
> **Selected: A**

**Q3: What should MVP explicitly exclude?**
- A) Broad multi-call migration and final engine semantics.
- B) Any future extensibility path.
- C) Any proof-call demonstration.
> Recommendation: A — It is the right scope cut. B is too defensive. C would make the WF hard to validate.
> **Selected: A**

**Q4: What should MVP prove about authoring?**
- A) Full official structure can be represented without fake expectations.
- B) Any node can be reviewed if it exists in YAML.
- C) Supporting nodes need no explicit role distinction.
> Recommendation: A — This is the central authoring proof. B and C contradict the workflow’s thesis.
> **Selected: A**

**Q5: What should MVP prove about the product?**
- A) Researchers can see the real structure for the proof call without semantic corruption.
- B) Researchers can get equal-depth review on every section.
- C) Researchers no longer need structured submit.
> Recommendation: A — This is the direct user-facing proof. B and C are false targets.
> **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: What tempting product promise must be postponed?**
- A) Feedback cards for every visible node.
- B) Showing any supporting node at all.
- C) Preserving source-grounded review semantics.
> Recommendation: A — It is tempting but wrong for this WF. B would nullify the effort. C is mandatory, not deferrable.
> **Selected: A**

**Q2: What engineering scope must be postponed?**
- A) Full universal engine redesign for context-aware review.
- B) Any contract clarification.
- C) All MSCA-related work.
> Recommendation: A — It belongs later. B and C would undermine the workflow.
> **Selected: A**

**Q3: What migration ambition must be deferred?**
- A) Reauthoring many calls at once.
- B) Proving the model on one call.
- C) Preserving backward compatibility.
> Recommendation: A — It is too large for the first slice. B and C remain important.
> **Selected: A**

**Q4: What semantic shortcut must be ruled out?**
- A) Adding fake expectations to make nodes visible.
- B) Keeping all visibility tied to current expectations.
- C) Distinguishing primary and supporting nodes.
> Recommendation: A — This is the central anti-pattern to reject. B preserves the defect. C is part of the desired direction.
> **Selected: A**

**Q5: What agency-specific nuance should definitely wait?**
- A) Solving every conditional/non-MSCA supporting-node policy in the first slice.
- B) Using `MSCA-PF-2025` as proof target.
- C) Preserving strict primary review semantics.
> Recommendation: A — It keeps the WF controlled. B and C are core to the workflow.
> **Selected: A**
