<!-- docs/brainstorms/brainstorm-WF-0074-canonical-funding-call-fidelity-hardening.md -->
# WF-0074 — Canonical Funding Call Fidelity Hardening

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-03-11

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts and decisions for WF-0074.
- The Q&A transcript is rationale only; it must not become the only place where scope or contract decisions live.
- This WF is about hardening the canonical funding-call authoring contract, not just improving prose guidance.
- Any solution that relies only on agent carefulness or narrative docs, without enforceable schema/template/checklist changes, is insufficient.

## Long-Form Problem Intake

PeerLens currently treats canonical funding call YAML authoring as minimal valid config authoring rather than high-fidelity source representation. That is a quality defect, not just a documentation gap. A YAML can pass dry-run, ingest, and runtime seams while still failing to encode the actual evaluative contract used by the funding call.

The concrete problem is that when official source documents contain a hierarchy like criterion -> evaluation elements -> detailed assessment questions/prompts, our current YAML authoring process often stops at the middle layer. We encode the criterion and the top-level evaluation elements, but we flatten or omit the subordinate assessment prompts. The ERC PoC 2026 example exposed this clearly: page 43 of the work programme contains one criterion, three evaluation elements, and multiple detailed questions under each element, but the YAML preserved only the three element headings as broad descriptions.

This harms PeerLens' primary trust promise. Researchers are supposed to receive evaluation-criteria-grounded feedback that is traceable to funding-call expectations. If detailed assessment prompts are omitted, the model has to infer what those expectations probably mean. That increases generic feedback, reduces coverage discipline, weakens source traceability, and makes outputs less actionable.

High-fidelity canonical representation in PeerLens should mean that the canonical YAML preserves the funder's evaluative structure at the level needed to drive rigorous, source-grounded review outputs. If the official source gives subordinate evaluative prompts, those prompts should be represented explicitly as structured sub-elements or reviewer prompts, not compressed into one summary sentence.

The main output change needed is not just richer stored data; it is better review behavior. PeerLens should produce review output that is more specific, more complete against the official source, more traceable to exact evaluative expectations, more actionable for applicants, and more reliable across runs because less is left to model inference.

The likely root cause is that the current schema and docs reward minimum ingestable YAML instead of maximum faithful evaluative encoding. The schema does not make detailed assessment prompts first-class structured data, the template does not model them, and the docs/checklists do not fail closed when multiple official prompts are flattened into one evaluation element description.

The goal of this workflow is to harden the canonical authoring contract so future funding call YAMLs are authored for fidelity and review quality, not just validation success. That likely requires a combination of schema changes, template changes, authoring-workflow updates, checklist gates, decision-log policy, and tests. The constraint is that this should not expand into a generic ontology project or broad runtime redesign.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md` (Preflight Step 1)

Contract Notes / Non-obvious constraints:
- The failure mode is semantic loss under a technically valid YAML, not just missing fields.
- "High fidelity" must be defined in terms of downstream review quality and source traceability, not document completeness for its own sake.
- A docs-only fix is considered insufficient because the current schema and template still legalize flattening.

## Repo Reality Snapshot (Read-Only)

- `backend/app/schemas/call_definitions_v2.py` supports only flat evaluation elements (`id`, `name`, `description`, `source_hint`, `stage`); there is no first-class field for subordinate evaluative prompts.
- `backend/data/calls/templates/call_definition_v2_template.yaml` models one flat example element and therefore teaches flattening by default.
- `docs/call-yaml/authoring-workflow.md` says to break criteria into atomic evaluation elements, but it does not require preservation of detailed official prompts when the source includes them.
- `docs/tasks/task-WF-0073-erc-poc-2026-call-onboarding.md` and adjacent workflow language explicitly rewarded the "smallest" and "minimal" source-grounded YAML needed to pass dry-run, which is consistent with the lossy ERC PoC result.
- Existing canonical call YAMLs across ERC, NWO, and MSCA consistently encode evaluation elements as flat objects, so any fidelity hardening must address compatibility and migration risk explicitly rather than pretending this is an isolated PoC mistake.

## 1. Problem Statement

Baseline direction:
- The core defect is that PeerLens can claim source-grounded call support while silently flattening or omitting official detailed evaluative prompts.
- The immediate stakeholder harmed is the researcher consuming review output that appears grounded but is less specific and less complete than the funder's real evaluative contract.
- The current repo default optimizes for validation success and onboarding speed more than review fidelity.
- This matters now because the repo has started onboarding real calls whose official sources expose more detailed evaluative structure than the current contract can represent faithfully.

Open questions / deferred:
- Should prompt-level fidelity be mandatory for all new calls only, or also required retroactively for selected existing canonical calls?
- How much runtime wiring is required in this WF to avoid "stored but unused" structured prompts?
- What compatibility posture is acceptable for existing call YAMLs that currently encode only flat evaluation elements?

## 2. Desired Outcome

- A future new or re-authored funding call YAML can represent official detailed evaluative prompts as first-class structured data when the source includes them.
- The canonical authoring defaults change from "minimum ingestable YAML" to "fail-closed fidelity for review-relevant evaluative structure."
- The contract hardening lands in the smallest cross-call surfaces that actually govern authoring behavior:
  - schema,
  - starter template,
  - authoring workflow docs,
  - onboarding checklist,
  - decision/memory guidance,
  - targeted tests.
- At least one proof-call example demonstrates the new fidelity shape so the contract is concrete, not abstract.
- The workflow stays bounded: it does not promise a universal retrofit of all historical YAMLs or a broad runtime redesign in the same slice.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md` (Section 2)

Contract Notes / Non-obvious constraints:
- "Desired outcome" is defined by safer future authoring and better review specificity, not by number of files changed.
- The success bar must include at least one concrete proof-call example; otherwise the contract remains too easy to interpret loosely.
- The workflow must distinguish between representability, default authoring behavior, and runtime consumption.

## 3. Target User / Actor

- Primary actor: the internal operator/developer authoring or re-authoring canonical funding call YAMLs.
- Primary beneficiary: the researcher receiving review output that should be specific, source-grounded, and actionable.
- Secondary actor: future coding agents following repo docs/templates/checklists who need an unambiguous authoring contract.
- The workflow should optimize for researcher-facing review quality first, while still making the authoring path explicit and repeatable for internal operators.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md` (Section 3)

Contract Notes / Non-obvious constraints:
- Internal author ergonomics matter, but they are subordinate to trustworthiness of review output.
- This WF is about call-authoring and review-trust surfaces, not a general knowledge-modeling exercise.

## 4. Rough Idea (Unstructured Thinking)

- Treat detailed official assessment prompts as part of the canonical evaluative contract, not optional prose.
- Add an explicit structured field for prompt-level or sub-element-level fidelity.
- Tighten docs, template, checklist, memory, and tests so flattening becomes a visible contract violation instead of an acceptable shortcut.
- Keep the first implementation slice narrow:
  - extend schema to represent subordinate prompts,
  - show the shape in the template,
  - harden docs/checklists,
  - add fail-closed tests,
  - prove the pattern on one representative call artifact.
- Preserve backward-compatibility awareness explicitly; if existing YAMLs remain flat temporarily, the workflow must document how that is tolerated or migrated rather than leaving silent ambiguity.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md` (Section 4)

## 5. Constraints

- Avoid a broad runtime redesign in the same workflow.
- Avoid inventing evaluative structure that is not present in official sources.
- Respect repo workflow discipline and keep execution slices small.
- Keep each execution task within the repo's 3-file planning discipline wherever feasible.
- Do not let optionality become an escape hatch; if prompt-level fidelity is in scope, the contract should define when it is required versus absent by source.
- Any compatibility posture for existing YAMLs must be explicit and testable.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md` (Section 5)

Contract Notes / Non-obvious constraints:
- A docs-only or memory-only fix is out of bounds because it does not change the real default behavior.
- A schema-only fix is also insufficient if authoring guidance and tests still allow flattening.

## 6. Risks / Unknowns

- Schema expansion may create stored-but-unused detail if runtime seams are not updated enough to consume it.
- Strict fidelity rules may expose that multiple existing canonical YAMLs are semantically lossy, creating migration pressure.
- Over-generalizing too early could turn a tractable hardening workflow into an unfocused cross-call redesign.
- The most important unknown is the minimum runtime or snapshot consumption seam required so the new structure changes review quality rather than just stored metadata.
- Another key risk is under-specifying the proof-call requirement and ending with a contract that is still too abstract to police.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md` (Section 6)

Contract Notes / Non-obvious constraints:
- Compatibility risk must be surfaced early in Phase 1 and turned into explicit PRD requirements rather than deferred implicitly.
- This WF should fail closed if it cannot show how the new fidelity data improves or constrains review behavior in at least one proof seam.

## Open Questions / Deferred

- Should proof-call runtime consumption in this WF stop at one narrow backend/snapshot seam, or must it extend into full structured-review behavior?
- Which existing canonical call should be the proof-call example if ERC PoC is used only as the motivating defect case?
- Should migration of already-flat canonical YAMLs be represented as explicit deferred stories in Phase 1?

## 7. MVP Definition

- Smallest defensible slice:
  - schema support for structured subordinate evaluative prompts,
  - starter template updated to demonstrate the shape,
  - authoring workflow docs/checklists hardened to require prompt-level fidelity when official sources provide it,
  - decision/memory policy updated so future sessions inherit the rule,
  - targeted tests that fail closed on unsupported or missing structured prompt encoding for proof-call scenarios,
  - one proof-call example showing the new contract in a real canonical YAML or equivalent fixture.
- Migration of the whole existing corpus is explicitly out of the MVP.
- Broad runtime redesign is explicitly out of the MVP, but one narrow consumption/proof seam may be required if Phase 1 determines that otherwise the new structure is stored but unused.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0074-canonical-funding-call-fidelity-hardening.md` (Section 7)

## Verification / Proceed Gate

- No proceed recommendation is valid if the workflow hardens docs without making fidelity representable in the schema and visible in the template.
- No proceed recommendation is valid if the workflow adds schema surface but leaves authoring guidance and tests permissive enough that flattening remains an acceptable default.
- At least one proof-call artifact must exercise the new shape; theoretical contract text alone is insufficient.
- Compatibility posture for existing flat YAMLs must be explicit: either tolerated temporarily with boundaries, migrated in-scope, or deferred with rationale.
- If runtime consumption is left unchanged, the workflow must justify why the chosen proof seam is still sufficient to improve or constrain review quality.

### Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Schema representability | targeted schema/model test(s) | `fail` (default until executed) | required | must prove structured prompt field validates and rejects malformed shapes |
| Template fidelity default | template diff / lint / doc check | `fail` (default until executed) | required | must show new starter template teaches prompt-level fidelity |
| Authoring contract hardening | docs/checklist diff + any contract tests | `fail` (default until executed) | required | must show flattening is no longer the documented default |
| Proof-call example | real YAML or equivalent fixture validation | `fail` (default until executed) | required | must exercise subordinate evaluative prompt encoding |
| Consumption/proof seam | targeted runtime/snapshot/test proof if required | `fail` (default until executed) | required | must avoid stored-but-unused ambiguity |

- Proceed recommendation remains blocked unless every required row above is `pass`, or explicitly `skipped` with a documented rationale accepted during review.

## 8. Explicit Non-Goals

- Re-author every existing call inside the same workflow unless explicitly planned after contract hardening lands.
- Invent evaluative sub-elements that are not grounded in official sources.
- Redesign the entire review engine before the call-definition contract is tightened.
- Universal retrofitting of every canonical YAML in the repo as part of the first implementation slice.
- Turning call YAML into a generic ontology or knowledge-graph project.

## Changelog

- v0.1 (2026-03-11): Captured long-form defect framing, repo reality snapshot, and initial recommended contracts for high-fidelity canonical call authoring.
