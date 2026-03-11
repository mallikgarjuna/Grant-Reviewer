<!-- docs/brainstorms/brainstorm-WF-0075-erc-poc-proof-call-fidelity-completion.md -->
# WF-0075 — ERC PoC Proof-Call Fidelity Completion

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-11

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts and decisions for WF-0075.
- The Q&A transcript is rationale only; it must not become the only place where scope, closure rules, or fidelity claims live.
- WF-0074 is prior truth for this workflow: subordinate-prompt authoring mechanism, template default, docs/checklist hardening, governance updates, and compatibility posture are already implemented.
- WF-0075 exists because the real ERC PoC proof-call is still only partially encoded against the official page-43 subordinate prompts.
- This workflow must not broaden into structured-review runtime consumption, multi-call migration, or generic schema/ontology redesign unless explicitly re-approved.

## Long-Form Problem Intake

WF-0074 successfully solved the mechanism and governance layer for subordinate-prompt fidelity. The repository can now represent typed subordinate prompts, the starter template demonstrates the shape, the authoring docs and checklist fail closed when official subordinate prompts exist, and the durable governance surfaces preserve that rule. Those parts are not the open defect anymore.

The remaining defect is narrower and more concrete: the real proof-call `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` still encodes subordinate prompts only for ERC PoC evaluation element `1.a Breakthrough Innovation Potential`. The same canonical call still does not encode the detailed official subordinate prompts for `1.b Approach and Methodology` and `1.c Principal Investigator - Strategic Leadership and Project Management`, even though page 43 of `wp_horizon-erc-2026_en.pdf` includes them.

That means the repo currently has a mechanism for high-fidelity subordinate-prompt authoring, but the flagship proof-call used to demonstrate that fidelity is still only partially encoded. As long as that partial state can still be treated as "fidelity complete," the canonical-fidelity claim is not fail-closed. A real proof-call should not pass as complete when it preserves only a subset of the official page-43 subordinate prompts.

This matters because the ERC PoC proof-call is the concrete repository artifact that should prove PeerLens can preserve official evaluation criteria/elements faithfully at the level required for source-grounded review authoring. If `1.a` is fully encoded but `1.b` and `1.c` remain flattened, the mechanism exists but the canonical proof is still incomplete.

The goal of WF-0075 is therefore not to redesign runtime review consumption. It is to complete the ERC PoC proof-call so all official subordinate prompts on page 43 are encoded across `1.a`, `1.b`, and `1.c`, and to add fail-closed coverage proof so partial subordinate-prompt encoding in a real proof-call cannot be mistaken for full canonical fidelity.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Preflight Step 1)

Contract Notes / Non-obvious constraints:
- The defect is no longer "the repo cannot represent subordinate prompts"; it is "the real proof-call still does not fully use that capability."
- Partial subordinate-prompt encoding in a real proof-call is explicitly insufficient for any fidelity-complete claim.
- Runtime-consumption work remains intentionally out of scope unless separately re-approved.

## Repo Reality Snapshot (Read-Only)

- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` currently carries subordinate prompts only under `elem_breakthrough_innovation_potential` (`1.a`) and leaves `elem_approach_methodology` (`1.b`) plus `elem_pi_strategic_leadership` (`1.c`) as flat evaluation elements.
- `backend/app/schemas/call_definitions_v2.py` already supports typed `subordinate_prompts`, so representability is no longer the main gap.
- `docs/call-yaml/authoring-workflow.md` and `docs/call-yaml/onboarding-checklist.md` already encode the WF-0074 fail-closed authoring rule: when subordinate prompts exist in source material, they must be preserved explicitly.
- `docs/logs/decisions.md` and `docs/memory/domain/project_docs.md` already preserve WF-0074's governance posture, proof-call policy, and runtime-boundary honesty.
- The unresolved gap is closure proof: the current repo still lacks a fail-closed way to distinguish three states for a real proof-call: no subordinate prompts by source, subordinate prompts fully encoded, and subordinate prompts present in source but only partially encoded.

## 1. Problem Statement

- WF-0075 treats the root defect as proof-call incompleteness, not mechanism incompleteness.
- `1.a` proves the subordinate-prompt authoring mechanism works, but the ERC PoC proof-call remains fidelity-incomplete until `1.b` and `1.c` also preserve their official page-43 subordinate prompts.
- "Fidelity complete" means all official subordinate prompts on page 43 are encoded across `1.a`, `1.b`, and `1.c`, or an absence is explicitly justified by source.
- The critical fail-open behavior is that a real proof-call can currently look compliant while preserving only part of the official subordinate-prompt structure.
- Scope boundary: this WF is about proof-call fidelity completion plus fail-closed coverage proof; runtime consumption remains out of scope unless explicitly re-approved.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Section 1)

Contract Notes / Non-obvious constraints:
- The workflow must preserve the distinction between "mechanism/governance already landed" and "proof-call still incomplete."
- The official source anchor is page 43 of `wp_horizon-erc-2026_en.pdf`; a vague "improve fidelity" restatement is insufficient.

## 2. Desired Outcome

- `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` becomes a genuinely fidelity-complete proof-call for page 43 by encoding the official subordinate prompts across `1.a`, `1.b`, and `1.c`.
- The workflow adds fail-closed coverage proof so a real proof-call cannot pass as "fidelity complete" when official subordinate prompts are only partially encoded.
- Any required tightening distinguishes three states cleanly:
  - no subordinate prompts by source,
  - subordinate prompts present and fully encoded,
  - subordinate prompts present but only partially encoded.
- The smallest acceptable scope change is proof-call completion plus the narrowest test/doc/checklist tightening needed to enforce that distinction.
- The workflow does not claim runtime review-quality improvement from subordinate-prompt consumption unless a later, separately approved WF widens the expectations-only runtime seam.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Section 2)

Contract Notes / Non-obvious constraints:
- Success is defined by honest proof-call completeness and closure evidence, not by reopening already-complete WF-0074 infrastructure.
- The target artifact is the real canonical proof-call, not only a fixture or synthetic example.

## 3. Target User / Actor

- Primary actor: the maintainer or coding agent updating and verifying canonical funding call YAMLs and their closure evidence.
- Primary beneficiary: researchers and future maintainers who need the ERC PoC proof-call fidelity claim to be honest, source-grounded, and fail closed.
- Secondary actor: future maintainers and agents who need an unambiguous closure rule for when a real proof-call is truly fidelity-complete versus only partially encoded.
- The actor model is repository-governance-first, not researcher-UI-first; the work happens in canonical YAML plus verification surfaces.
- Tradeoff priority: truthfulness of canonical proof and fail-closed closure logic comes before minimizing incremental authoring effort.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Section 3)

Contract Notes / Non-obvious constraints:
- This WF protects downstream trust primarily by hardening the canonical source artifact and its closure proof, not by changing user-facing runtime behavior.

## 4. Rough Idea (Unstructured Thinking)

- Re-author the ERC PoC proof-call so `1.b` and `1.c` preserve their official subordinate prompts using the already-landed typed subordinate-prompt structure.
- Add the narrowest executable or contract-level proof that fails closed when a real proof-call has only partial subordinate-prompt coverage relative to the official source.
- Prefer proof surfaces tied directly to the real canonical artifact and its source-grounded expectations over generic schema redesign or repo-wide migration work.
- Tighten docs/checklist/tests only where necessary to distinguish "absent by source" from "present but incomplete by source."
- Keep any additional governance edits corrective and minimal; do not relitigate WF-0074's already-approved mechanism/governance scope unless a narrow correction is required for fail-closed closure.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Section 4)

## 5. Constraints

- Preserve WF-0074 as prior truth; do not reopen the subordinate-prompt mechanism, template-default posture, or general governance work unless a narrow correction is required.
- Preserve traceability to `wp_horizon-erc-2026_en.pdf` page 43 for every fidelity-completion claim.
- Keep runtime review consumption out of scope unless explicitly re-approved.
- Do not widen into multi-call migration, generic ontology redesign, or broader structured-review engine work.
- Keep implementation slices small and prefer the minimal set of proof surfaces needed to distinguish absent, complete, and partial subordinate-prompt states fail closed.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Section 5)

Contract Notes / Non-obvious constraints:
- A "just add the missing prompts" patch is insufficient if the closure evidence still cannot distinguish partial encoding from full completion.
- A generic cross-call redesign is out of scope even if it looks cleaner technically.

## 6. Risks / Unknowns

- The biggest product/process risk is falsely treating the ERC PoC proof-call as fidelity-complete after only a subset of official subordinate prompts is encoded.
- The main implementation risk is choosing a proof surface that checks schema validity but still misses semantic coverage against the official source.
- Another risk is accidental scope drift back into runtime consumption or generic contract redesign because those surfaces already exist nearby from WF-0074.
- The highest-value unknown is the smallest reliable seam that can prove page-43 completeness versus partiality for a real proof-call.
- A secondary unknown is whether a narrow doc/checklist correction is needed to make the three-state distinction explicit outside tests.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Section 6)

Contract Notes / Non-obvious constraints:
- Schema validity alone is not enough evidence for proof-call completeness.
- The audit must challenge any closure path that cannot prove why `1.b` and `1.c` are complete relative to page 43.

## Open Questions / Deferred

- What is the smallest fail-closed proof seam: source-grounded tests only, tests plus checklist language, or another narrowly scoped contract surface?
- Does any WF-0074 governance text need a narrow corrective clarification so "partial subordinate-prompt encoding" is explicitly insufficient for a real proof-call, without reopening the broader mechanism/governance scope?
- What exact verification artifact should become the closure anchor for page-43 completeness in later phases?

## 7. MVP Definition

- Smallest defensible slice:
  - complete `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` so all official page-43 subordinate prompts are encoded across `1.a`, `1.b`, and `1.c`,
  - add fail-closed proof that partial subordinate-prompt encoding in a real proof-call does not qualify as fidelity complete,
  - apply only the narrowest test/doc/checklist/governance tightening required to distinguish absent-by-source, fully encoded, and partially encoded states.
- MVP proof must include at least one negative case where an official `1.b` or `1.c` subordinate prompt is intentionally omitted and closure fails.
- Reusing the existing typed subordinate-prompt structure is mandatory; inventing a new mechanism is out of scope.
- Runtime-consumption work is explicitly not part of MVP.
- Multi-call retrofit work is explicitly not part of MVP.
- Any extra documentation changes must serve the proof-call completion and fail-closed coverage goal directly.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0075-erc-poc-proof-call-fidelity-completion.md` (Section 7)

## Verification / Proceed Gate

- No proceed recommendation is valid if `erc_poc_2026_full.yaml` still lacks the official subordinate prompts for either `1.b` or `1.c`.
- No proceed recommendation is valid if closure evidence can prove schema validity but cannot prove page-43 completeness versus partiality.
- No proceed recommendation is valid if the workflow blurs together the three required states:
  - no subordinate prompts by source,
  - subordinate prompts present and fully encoded,
  - subordinate prompts present but only partially encoded.
- No proceed recommendation is valid if the workflow overclaims runtime review consumption or review-quality improvement beyond the expectations-only boundary already documented by WF-0074.
- Any narrow correction to docs/checklist/governance must preserve the exact prior truth that WF-0074 already landed the mechanism/governance layer successfully.

### Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| ERC PoC proof-call completion | targeted call validation against `erc_poc_2026_full.yaml` | `fail` (default until executed) | required | must prove all official page-43 subordinate prompts are encoded across `1.a`, `1.b`, and `1.c` |
| Source-to-YAML prompt coverage | replayable source ledger or equivalent targeted proof | `fail` (default until executed) | required | must map every official page-43 subordinate prompt for `1.a`, `1.b`, and `1.c` to an exact YAML prompt ID/path |
| Partial-vs-complete coverage proof | targeted fail-closed test or equivalent contract check | `fail` (default until executed) | required | must fail if a real proof-call encodes only a subset of official subordinate prompts |
| Absent/complete/partial distinction | test and/or doc-check evidence | `fail` (default until executed) | required | must distinguish no subordinate prompts by source from incomplete encoding |
| Runtime-boundary honesty | targeted seam proof or contract citation | `fail` (default until executed) | required | must preserve expectations-only runtime boundary unless separately re-approved |
| Audit disposition | finding-closure ledger | `fail` (default until executed) | required | must close every blocking finding and close or reject justified non-blocking findings with rationale |

- Proceed recommendation remains blocked unless every required row above is `pass`, or explicitly `skipped` with accepted rationale during review.

## 8. Explicit Non-Goals

- Rebuilding or redesigning the subordinate-prompt mechanism already delivered by WF-0074.
- Redesigning the structured-review runtime to consume subordinate prompts.
- Broadening into multi-call canonical migration.
- Turning the call-definition contract into a generic ontology or broader schema redesign.
- Treating partial subordinate-prompt encoding as "good enough" proof-call fidelity.

## Changelog

- v0.1 (2026-03-11): Captured the exact WF-0075 defect as ERC PoC proof-call incompleteness relative to page 43, locked runtime consumption out of scope, and required fail-closed proof that partial subordinate-prompt encoding cannot pass as fidelity complete.
- v0.2 (2026-03-11): Tightened source-rigorous completeness wording, restored researcher-facing trust as the primary beneficiary, added an explicit negative proof requirement, and added a replayable source-to-YAML coverage row to the verification matrix.
