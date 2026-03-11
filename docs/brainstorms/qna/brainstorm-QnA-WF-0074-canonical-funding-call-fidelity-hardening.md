<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md -->
# WF-0074 — Canonical Funding Call Fidelity Hardening

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-11

## Preflight Step 1 — Long-Form Problem Intake

**User-provided narrative adopted as baseline problem framing**

PeerLens currently treats canonical funding call YAML authoring as minimal valid config authoring rather than high-fidelity source representation. That is a quality defect, not just a documentation gap. A YAML can pass dry-run, ingest, and runtime seams while still failing to encode the actual evaluative contract used by the funding call.

The concrete problem is that when official source documents contain a hierarchy like criterion -> evaluation elements -> detailed assessment questions/prompts, our current YAML authoring process often stops at the middle layer. We encode the criterion and the top-level evaluation elements, but we flatten or omit the subordinate assessment prompts. The ERC PoC 2026 example exposed this clearly: page 43 of the work programme contains one criterion, three evaluation elements, and multiple detailed questions under each element, but the YAML preserved only the three element headings as broad descriptions.

This harms PeerLens' primary trust promise. Researchers are supposed to receive evaluation-criteria-grounded feedback that is traceable to funding-call expectations. If detailed assessment prompts are omitted, the model has to infer what those expectations probably mean. That increases generic feedback, reduces coverage discipline, weakens source traceability, and makes outputs less actionable.

High-fidelity canonical representation in PeerLens should mean that the canonical YAML preserves the funder's evaluative structure at the level needed to drive rigorous, source-grounded review outputs. If the official source gives subordinate evaluative prompts, those prompts should be represented explicitly as structured sub-elements or reviewer prompts, not compressed into one summary sentence.

The main output change needed is not just richer stored data; it is better review behavior. PeerLens should produce review output that is more specific, more complete against the official source, more traceable to exact evaluative expectations, more actionable for applicants, and more reliable across runs because less is left to model inference.

The likely root cause is that the current schema and docs reward minimum ingestable YAML instead of maximum faithful evaluative encoding. The schema does not make detailed assessment prompts first-class structured data, the template does not model them, and the docs/checklists do not fail closed when multiple official prompts are flattened into one evaluation element description.

The goal of this workflow is to harden the canonical authoring contract so future funding call YAMLs are authored for fidelity and review quality, not just validation success. That likely requires a combination of schema changes, template changes, authoring-workflow updates, checklist gates, decision-log policy, and tests. The constraint is that this should not expand into a generic ontology project or broad runtime redesign.

## Preflight Step 2 — Repo Reality Snapshot

- `backend/app/schemas/call_definitions_v2.py` supports only flat evaluation elements.
- `backend/data/calls/templates/call_definition_v2_template.yaml` teaches flat-element authoring by default.
- `docs/call-yaml/authoring-workflow.md` requires atomic elements but does not require preserving subordinate official prompts.
- `docs/tasks/task-WF-0073-erc-poc-2026-call-onboarding.md` explicitly optimized for the smallest/minimal YAML that passes dry-run.
- Existing canonical YAMLs across agencies use the same flat evaluation-element pattern, implying cross-call compatibility pressure if the contract changes.

## Section 1 — Problem Statement

**Q1: What is the primary defect WF-0074 should treat as the root problem?**
- A) Missing schema expressiveness for detailed official evaluative prompts.
- B) Weak authoring guidance only.
- C) Runtime review quality only.
  > Recommendation: A — docs can tighten behavior, but as long as the schema only supports flat elements, flattening remains a legal and likely outcome. B is incomplete because it leaves the contract underpowered. C is downstream of the authoring contract and would treat symptoms before the root cause.
  > **Selected: A**

**Q2: Who is the primary actor harmed by the current defect?**
- A) Researchers consuming PeerLens review output.
- B) Internal call authors only.
- C) Both equally.
  > Recommendation: A — the contract should be judged by user-facing review quality first. B understates the product risk. C is directionally true but weakens prioritization and could justify internal convenience over trustworthiness.
  > **Selected: A**

**Q3: What should “high-fidelity canonical representation” mean operationally in this WF?**
- A) Encode every official evaluative layer needed for rigorous review output, including subordinate prompts when present.
- B) Encode only top-level criteria/elements, but improve descriptions.
- C) Encode the full source document structure wherever possible.
  > Recommendation: A — it matches the trust promise without bloating scope. B preserves the current failure mode under better wording. C is too broad and risks modeling non-evaluable noise that does not improve review quality.
  > **Selected: A**

**Q4: What is the minimum success bar for this workflow?**
- A) New schema support plus docs/template/checklist hardening, with at least one proof-call example.
- B) Docs-only policy hardening.
- C) Full end-to-end runtime rollout across all calls.
  > Recommendation: A — this is the smallest defensible slice. B is governance theater because it leaves flattening structurally allowed. C is too large for a disciplined hardening workflow and would blur the contract problem with broader rollout work.
  > **Selected: A**

**Q5: How aggressive should the workflow be about existing canonical YAMLs that are already flat?**
- A) Fail closed for new/reauthored calls first; handle retrofits selectively in follow-up work.
- B) Migrate all existing calls in the same WF.
- C) Preserve backward compatibility completely and avoid any migration pressure.
  > Recommendation: A — it prevents new debt first without turning Phase 0 into a migration program. B is too large and likely to hide new bugs under broad edits. C risks landing optional fidelity that remains unused in practice.
  > **Selected: A**

## Section 2 — Desired Outcome

**Q1: What kind of outcome should Phase 1/2 optimize for?**
- A) A hardened cross-call authoring contract that changes future behavior by default.
- B) A one-off ERC PoC correction only.
- C) A broad review-engine redesign.
  > Recommendation: A — the defect is systemic, not PoC-specific, so the workflow should fix the authoring contract at its governing seams. B would leave the repo default broken. C is over-scoped and delays closure on the actual source-fidelity problem.
  > **Selected: A**

**Q2: How concrete must the outcome be?**
- A) It must include at least one proof-call artifact that exercises the new fidelity shape.
- B) Documentation and schema text are enough.
- C) Only runtime output proof matters.
  > Recommendation: A — without a proof-call artifact, the new contract stays too abstract and easy to dilute. B is too weak. C skips the upstream contract surfaces that create the defect in the first place.
  > **Selected: A**

**Q3: What should the contract change default toward?**
- A) Fail-closed fidelity when official sources include subordinate prompts.
- B) Optional prompt-level enrichment when time allows.
- C) Keep flattening as default but recommend richer authoring.
  > Recommendation: A — if prompt-level fidelity is optional, the repo will drift back to minimal YAML under schedule pressure. B and C both preserve the current incentive structure.
  > **Selected: A**

**Q4: Which surfaces must be in-scope for the desired outcome?**
- A) Schema, template, docs/checklist, and tests.
- B) Docs/checklist only.
- C) Schema only.
  > Recommendation: A — all four surfaces jointly define real authoring behavior. B leaves the contract unenforced. C leaves humans and future agents without the right default pattern or governance guardrails.
  > **Selected: A**

**Q5: What is the acceptable boundary for this WF’s outcome?**
- A) Narrow cross-call hardening with explicit proof and explicit deferrals.
- B) Universal retrofitting of the full canonical corpus.
- C) Local patching of one call only.
  > Recommendation: A — this creates durable leverage without overreaching. B is too large for a disciplined first slice. C would repeat the repo’s pattern of local fixes that do not change the default behavior.
  > **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary operator for this workflow’s direct changes?**
- A) Internal operator/developer authoring canonical funding calls.
- B) End-user researcher directly editing YAML.
- C) Reviewer consuming PeerLens results.
  > Recommendation: A — the direct change surface is canonical YAML authoring and governance. B is false in this product context. C is an important beneficiary, but not the direct operator.
  > **Selected: A**

**Q2: Who is the primary beneficiary whose needs should dominate tradeoffs?**
- A) Researchers receiving more specific, source-grounded feedback.
- B) Internal maintainers seeking lower authoring friction.
- C) Both equally.
  > Recommendation: A — the point of high-fidelity encoding is better review output. B matters but should not override trust. C again weakens prioritization at the exact place where the repo has already optimized too much for convenience.
  > **Selected: A**

**Q3: Which secondary actor must the workflow also support?**
- A) Future coding agents following repo docs/templates/checklists.
- B) Marketing/site-copy authors.
- C) External peer reviewers using the product directly.
  > Recommendation: A — a major reason to harden the contract is to stop future agents from legally authoring lossy YAML. B and C are outside the immediate contract surface.
  > **Selected: A**

**Q4: What should the actor model explicitly avoid?**
- A) Treating this as an abstract data-modeling exercise detached from review quality.
- B) Treating this as a frontend UX problem.
- C) Treating this as a one-call-only ingestion bug.
  > Recommendation: A — this is the easiest way for the workflow to become intellectually neat but product-weak. B and C are also wrong, but A is the most dangerous because it can still look sophisticated while missing the user impact.
  > **Selected: A**

**Q5: What tradeoff stance should govern actor priorities?**
- A) Researcher-facing trust first; internal authoring clarity second.
- B) Internal authoring speed first; trust later.
- C) Perfect balance with no explicit prioritization.
  > Recommendation: A — the repo already skewed toward authoring speed/minimal validity. B would repeat the mistake. C sounds fair but tends to preserve the status quo.
  > **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest credible implementation direction?**
- A) Add first-class structured subordinate prompt support and harden the authoring contract around it.
- B) Keep the schema flat and enrich descriptions manually.
- C) Build a fully generic multi-level evaluation ontology.
  > Recommendation: A — it directly addresses the gap with minimal extra abstraction. B leaves fidelity implicit. C is a likely overreaction that expands scope without guaranteed product value.
  > **Selected: A**

**Q2: What should the first proof pattern be?**
- A) One representative proof-call example exercising the new shape.
- B) Broadly update all examples at once.
- C) No example until runtime wiring is complete.
  > Recommendation: A — one proof artifact keeps the contract concrete and reviewable. B is risky and noisy. C delays learning until too late.
  > **Selected: A**

**Q3: How should docs participate?**
- A) Docs should codify the new mandatory behavior and explain when subordinate prompts are required.
- B) Docs should stay general and defer specifics to engineers.
- C) Docs should be the main enforcement mechanism.
  > Recommendation: A — docs need specificity, but not as the only enforcement layer. B is too weak. C overstates prose as a control surface.
  > **Selected: A**

**Q4: How should template behavior change?**
- A) The template should demonstrate the structured prompt shape so authors copy the right pattern by default.
- B) Leave the template minimal and rely on docs.
- C) Remove the template to force deliberate authoring.
  > Recommendation: A — templates drive real behavior more than prose. B keeps the wrong default alive. C adds friction without guidance.
  > **Selected: A**

**Q5: How should compatibility be handled in the idea phase?**
- A) Make compatibility posture explicit and testable, even if some migration is deferred.
- B) Ignore compatibility until implementation.
- C) Avoid any contract change that pressures existing YAMLs.
  > Recommendation: A — compatibility ambiguity is a known risk and must be surfaced early. B hides a predictable problem. C would neuter the workflow into optional metadata.
  > **Selected: A**

## Section 5 — Constraints

**Q1: What is the hardest scope boundary?**
- A) No broad runtime redesign in this workflow.
- B) No docs changes.
- C) No schema changes.
  > Recommendation: A — runtime redesign would overwhelm the contract-hardening goal. B and C would block the very surfaces that need fixing.
  > **Selected: A**

**Q2: What source-grounding rule must remain strict?**
- A) Never invent subordinate evaluative prompts that are not present in official sources.
- B) Infer likely prompts when a call seems similar to another.
- C) Normalize all agencies into a common invented prompt taxonomy.
  > Recommendation: A — fidelity means preserving source-grounded structure, not manufacturing it. B and C would undermine defensibility immediately.
  > **Selected: A**

**Q3: What planning discipline should constrain implementation shape later?**
- A) Keep execution slices small and aligned with the repo’s 3-file task discipline where feasible.
- B) Allow one large refactor since this is cross-call work.
- C) Decide later.
  > Recommendation: A — without explicit small-slice discipline, this workflow could sprawl quickly. B is high-risk. C is too vague for a known multi-surface change.
  > **Selected: A**

**Q4: What contract rule should apply to optionality?**
- A) Optionality must not become an escape hatch that keeps flattening acceptable when sources provide prompts.
- B) Make the new structure optional forever.
- C) Let each author decide case by case.
  > Recommendation: A — otherwise the workflow does not actually change repo behavior. B and C preserve the current weakness under softer language.
  > **Selected: A**

**Q5: What compatibility constraint must be explicit?**
- A) Existing flat YAMLs may be tolerated temporarily, but only under an explicit documented posture.
- B) Existing YAMLs should block any contract hardening.
- C) Existing YAMLs can be ignored completely.
  > Recommendation: A — this keeps the workflow realistic without surrendering the contract change. B prevents progress. C is naive and likely to break trust in later phases.
  > **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the highest product risk if we harden only storage shape?**
- A) Stored-but-unused fidelity that does not actually improve or constrain review behavior.
- B) Slightly larger YAML files.
- C) More docs to maintain.
  > Recommendation: A — this is the core substantive risk. B and C are trivial by comparison.
  > **Selected: A**

**Q2: What is the highest repo/process risk?**
- A) Revealing broad backward-compatibility debt across existing canonical YAMLs.
- B) Having to update one template.
- C) Minor naming disputes.
  > Recommendation: A — cross-call compatibility pressure is already visible in the repo snapshot. B and C are noise-level concerns.
  > **Selected: A**

**Q3: What is the biggest workflow-shape risk?**
- A) Over-generalizing into a large redesign instead of a disciplined hardening slice.
- B) Being too narrow and updating one extra doc.
- C) Not enough brainstorming detail.
  > Recommendation: A — scope inflation is the clearest threat to execution success. B is manageable. C is not the main failure mode here.
  > **Selected: A**

**Q4: What proof risk must be called out early?**
- A) Failing to require a concrete proof-call artifact and ending with abstract contract language.
- B) Using too many headings in the brainstorm.
- C) Choosing the wrong slug.
  > Recommendation: A — without concrete proof, this WF can appear complete while still being soft and ambiguous. B and C are trivial.
  > **Selected: A**

**Q5: What key unknown should Phase 1 clarify first?**
- A) The minimum consumption/runtime seam required so new structured prompts are not merely stored metadata.
- B) Whether to rename all existing files immediately.
- C) Whether to add more agencies in the same WF.
  > Recommendation: A — this is the central unknown linking contract fidelity to actual review-quality impact. B and C are secondary or out of scope.
  > **Selected: A**

## Section 7 — MVP Definition

**Q1: What is the minimum schema outcome for MVP?**
- A) Schema can represent structured subordinate evaluative prompts safely.
- B) Schema remains unchanged.
- C) Schema redesigns all evaluation structures universally.
  > Recommendation: A — representability is the minimum missing capability. B leaves the defect intact. C is over-scoped.
  > **Selected: A**

**Q2: What is the minimum authoring-surface outcome for MVP?**
- A) Template plus docs/checklists make prompt-level fidelity the explicit default when sources provide it.
- B) Only the schema changes.
- C) Only docs change.
  > Recommendation: A — the authoring default is governed by more than schema. B and C each leave a major gap.
  > **Selected: A**

**Q3: What is the minimum proof requirement for MVP?**
- A) One proof-call artifact exercises the new structure and validation path.
- B) No proof artifact until all calls are migrated.
- C) A conceptual example in markdown only.
  > Recommendation: A — this is the smallest concrete proof. B delays validation too much. C is too weak to enforce anything.
  > **Selected: A**

**Q4: What should be explicitly excluded from the MVP?**
- A) Full-corpus retrofitting and broad runtime redesign.
- B) Any tests.
- C) Any schema changes.
  > Recommendation: A — that is the proper boundary. B and C would gut the workflow.
  > **Selected: A**

**Q5: What conditional item may still need inclusion in MVP if Phase 1 proves it necessary?**
- A) One narrow consumption/proof seam to avoid stored-but-unused ambiguity.
- B) A full frontend redesign.
- C) A generic ontology layer.
  > Recommendation: A — this is the only conditional runtime piece that directly supports the workflow’s success claim. B and C are clearly out of scope.
  > **Selected: A**
