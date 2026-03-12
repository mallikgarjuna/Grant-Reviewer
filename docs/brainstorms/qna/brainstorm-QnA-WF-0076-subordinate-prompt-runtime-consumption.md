<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md -->
# WF-0076 — Subordinate Prompt Runtime Consumption

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-12

## Preflight Step 1 — User Narrative Intake

Source: user-provided workflow brief in chat on 2026-03-12.

- WF-0074 is already complete for authoring/governance fidelity.
- WF-0075 is already complete for ERC PoC proof-call fidelity.
- The remaining unresolved defect is runtime non-consumption of already-authored subordinate prompts.
- The new workflow must investigate the narrowest runtime seam, the smallest honest runtime contract change, the exact operational success criteria, and deterministic proof that subordinate prompts influence runtime behavior.
- The workflow must preserve the expectations-only boundary until evidence justifies widening it and must fail closed if runtime-improvement claims cannot be proven tightly.

## Preflight Step 2 — Repo Reality Snapshot

- `backend/app/services/structured_reviewer_service.py` currently emits `call_config_snapshot` with only `schema_version` plus `expectations`.
- `backend/app/engine/contracts.py` can represent richer activated snapshot fields, but the live structured-review path does not populate them today.
- `backend/app/services/prompt_builder.py` currently formats prompts from flat expectation and element description data only.
- `backend/tests/test_structured_reviewer_service.py` explicitly proves the runtime snapshot remains expectations-only after WF-0075.
- `backend/tests/test_call_subordinate_prompt_coverage.py` explicitly proves the ERC PoC proof-call is already fully encoded, so runtime consumption is the remaining gap.

## Section 1 — Problem Statement

**Q1: What exact defect should WF-0076 name as the root problem?**
- A) The runtime activation seam strips subordinate prompts before structured-review execution, so stored canonical fidelity has no proven runtime effect.
- B) The main issue is generic prompt quality, and subordinate prompts are only one possible improvement lever.
- C) The main issue is that the engine architecture is outdated and needs broader redesign.
> Recommendation: A — it matches the verified seam in `structured_reviewer_service.py`, preserves the distinction from WF-0074 and WF-0075, and keeps the workflow falsifiable. B is too vague and would hide the concrete defect inside general quality language. C overreaches into redesign without evidence that redesign is required.
> **Selected: A**

**Q2: What should be the initial proof surface for defining the problem?**
- A) ERC PoC only, because it is the fully encoded proof-call and already has fail-closed fidelity evidence.
- B) All calls that use V2 YAML, to avoid call-specific thinking from the start.
- C) A synthetic fixture, so the problem statement stays implementation-neutral.
> Recommendation: A — ERC PoC is already the strongest approved truth anchor, so it minimizes uncertainty while still proving the runtime seam. B broadens scope before one proof surface is stable. C weakens honesty because it would skip the real proof-call that already exists.
> **Selected: A**

**Q3: Who is the primary actor for the problem statement?**
- A) The runtime owner or maintainer who needs subordinate-prompt fidelity to become executable, with researchers as the downstream beneficiary.
- B) The researcher alone, framed as a UX wording problem.
- C) The YAML author alone, framed as a data-model problem.
> Recommendation: A — the unresolved work is runtime execution, not authoring or copy. B hides the actual code seam, and C incorrectly reopens the already-solved authoring layer.
> **Selected: A**

**Q4: What boundary should the problem statement lock immediately?**
- A) Solve only the smallest runtime-consumption seam that can materially and provably change review behavior.
- B) Redesign prompt construction and expectation modeling broadly so subordinate prompts become a first-class engine concept everywhere.
- C) Start with docs or governance clarification and decide later whether runtime changes are needed.
> Recommendation: A — it keeps the workflow narrow and evidence-driven. B is premature redesign. C repeats the mistake of producing governance without product effect.
> **Selected: A**

**Q5: What should count as “problem still unresolved” even if code changes land?**
- A) Subordinate prompts remain absent from the activated runtime surface that actually drives review behavior, or tests prove only persistence instead of runtime influence.
- B) The snapshot contract changes, even if no deterministic review effect is shown.
- C) The output seems better in a few examples, even without deterministic proof.
> Recommendation: A — it is the fail-closed definition. B would allow symbolic change without product effect. C is intuition-driven and not auditable.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: What is the core success condition for WF-0076?**
- A) A minimal runtime seam change makes subordinate prompts reachable to live structured-review execution and proves runtime influence deterministically.
- B) The activated snapshot starts storing subordinate prompts, even if no downstream behavior changes yet.
- C) PeerLens output generally feels more specific in ad hoc testing.
> Recommendation: A — this is the smallest honest success definition aligned to the defect. B is still storage-only one layer later. C is not fail-closed.
> **Selected: A**

**Q2: How broad should the first success claim be?**
- A) ERC PoC proof-call only, with a reusable seam but no universal product-effect claim.
- B) All V2 calls benefit equally once the seam exists.
- C) All future calls with subordinate prompts benefit equally immediately.
> Recommendation: A — it preserves honesty and uses the existing proof-call. B and C overclaim beyond available evidence.
> **Selected: A**

**Q3: What should “improved output” mean operationally in MVP?**
- A) More complete coverage of official concerns, more specific/source-grounded runtime instructions, and reduced omission of encoded sub-issues, proven by deterministic assertions.
- B) Higher subjective reviewer preference in manual spot checks.
- C) More verbose review cards.
> Recommendation: A — it is operational, close to the real product promise, and testable. B is weak evidence. C confuses length with quality.
> **Selected: A**

**Q4: What is the acceptable contract effect size?**
- A) The smallest explicit runtime contract widening needed for subordinate-prompt consumption.
- B) A broader snapshot redesign to future-proof many possible runtime enrichments.
- C) No contract change; rely on existing flat expectations and smarter prompt wording.
> Recommendation: A — minimal widening is the right bar. B adds unproven design debt. C likely cannot solve the verified discard seam honestly.
> **Selected: A**

**Q5: What should not count as desired outcome?**
- A) More schema/docs/storage surface without executable runtime proof.
- B) A deterministic ERC PoC runtime proof.
- C) A narrow reusable seam that later calls might adopt.
> Recommendation: A — it is explicitly insufficient. B and C are acceptable if bounded honestly.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary implementation actor?**
- A) Backend runtime maintainer or coding agent working on structured-review activation and tests.
- B) Call-YAML author maintaining canonical data.
- C) Researcher interacting with the product UI.
> Recommendation: A — the live seam is backend runtime code. B was the actor for WF-0074 and WF-0075, not this remaining defect. C is the beneficiary, not the implementer.
> **Selected: A**

**Q2: Who is the primary beneficiary?**
- A) Researchers receiving structured reviews that should better reflect official concerns already encoded in the call.
- B) Only maintainers, because runtime change is invisible to end users.
- C) Only internal ops, because this is mostly a workflow artifact issue.
> Recommendation: A — product value is downstream researcher-facing, even if implementation is internal. B and C understate the reason to do the work.
> **Selected: A**

**Q3: How should the actor framing preserve scope?**
- A) Internal backend change with bounded researcher-facing claims proven through runtime artifacts.
- B) Researcher-experience overhaul.
- C) YAML-author education improvement.
> Recommendation: A — it aligns actor and proof surface without drifting into broader UX or authoring work. B and C reopen unrelated layers.
> **Selected: A**

**Q4: What call scope should actor/beneficiary framing assume?**
- A) ERC PoC first, with no assumption that every call benefits equally.
- B) All calls with any evaluation elements.
- C) All future calls only.
> Recommendation: A — it matches available evidence. B and C are speculative.
> **Selected: A**

**Q5: What misconception should be rejected in this section?**
- A) That the primary actor is still the canonical YAML author.
- B) That researchers benefit from better runtime consumption.
- C) That maintainers need deterministic tests.
> Recommendation: A — the authoring layer is solved already. B and C are true and should remain in scope.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the preferred implementation direction to explore in Phase 1?**
- A) Carry subordinate prompts through the activated runtime representation and consume them at the nearest prompt-building or expectation-expansion seam that can change behavior.
- B) Build a new parallel subordinate-prompt engine path beside the current structured-review path.
- C) Keep the snapshot unchanged and hope existing element descriptions are enough.
> Recommendation: A — it is the narrowest plausible path from stored fidelity to runtime effect. B creates duplicated architecture. C ignores the proven discard seam.
> **Selected: A**

**Q2: What representation bias should the workflow prefer?**
- A) A narrow child payload attached to existing expectation or element context.
- B) A generic ontology with many new runtime abstractions.
- C) Free-text concatenation with no explicit structure.
> Recommendation: A — it preserves current mental models while adding only what is needed. B is over-engineered. C is too lossy and harder to test deterministically.
> **Selected: A**

**Q3: Which runtime surface should be treated as acceptable first proof target?**
- A) Prompt construction, expectation expansion, or another equivalently narrow runtime surface that demonstrably changes review behavior.
- B) Only final review-card prose quality judged manually.
- C) Only DB persistence and request validation.
> Recommendation: A — it stays close to execution and can still be deterministic. B is subjective. C is not runtime effect.
> **Selected: A**

**Q4: How should Phase 1 treat internal design freedom?**
- A) Compare narrow seams and choose the smallest one that yields deterministic product-effect proof.
- B) Pre-commit to a broad snapshot redesign now.
- C) Avoid any contract discussion until implementation starts.
> Recommendation: A — it preserves optionality without losing rigor. B is premature. C would defer the key planning question.
> **Selected: A**

**Q5: What should be rejected as the rough idea baseline?**
- A) Broad engine redesign as the default answer.
- B) Minimal explicit contract change.
- C) ERC PoC-first proof surface.
> Recommendation: A — redesign is not justified yet. B and C are consistent with the approved boundary.
> **Selected: A**

## Section 5 — Constraints

**Q1: Which prior truth must remain locked from WF-0074?**
- A) Temporary compatibility for existing flat canonical YAMLs unless explicitly re-approved otherwise.
- B) All calls must now be migrated in this workflow.
- C) Runtime-consumption claims were already solved there.
> Recommendation: A — that is the approved boundary. B is scope drift. C is false.
> **Selected: A**

**Q2: Which prior truth must remain locked from WF-0075?**
- A) ERC PoC proof-call completeness is already solved and must be preserved, not re-litigated.
- B) ERC PoC should be reopened as a fidelity-authoring task first.
- C) Runtime consumption was solved there too.
> Recommendation: A — that is the point of using ERC PoC as proof-call. B and C are both false.
> **Selected: A**

**Q3: What scope constraint should Phase 1 treat as non-negotiable?**
- A) Avoid broad engine redesign, ontology work, and multi-call migration unless strictly necessary.
- B) Leave scope broad so implementation can discover what it needs.
- C) Treat docs/governance changes as mandatory regardless of executable proof.
> Recommendation: A — this WF needs discipline. B invites drift. C reopens prior-truth governance unnecessarily.
> **Selected: A**

**Q4: What proof discipline constraint should be explicit?**
- A) No runtime-improvement claim without deterministic executable proof.
- B) Manual demos are enough if they look convincing.
- C) Contract changes imply product effect by default.
> Recommendation: A — it is the central honesty guard. B and C are fail-open.
> **Selected: A**

**Q5: What technical constraint should the brainstorm acknowledge?**
- A) Hidden coupling across activation, validator, pipeline, and prompt builder may limit how small the seam can be.
- B) The runtime path is isolated, so only one file is likely involved.
- C) The runtime contract can widen freely because tests already cover everything.
> Recommendation: A — this is the realistic code-level constraint surfaced by repo inspection. B and C are unsafe assumptions.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the biggest implementation risk?**
- A) Adding a richer runtime payload that still does not materially affect review behavior.
- B) Accidentally improving output too much and needing to tone it down.
- C) The ERC PoC YAML losing subordinate prompts during authoring.
> Recommendation: A — it is the core fail-open risk for this WF. B is not the real concern. C belongs to already-solved prior workflows.
> **Selected: A**

**Q2: What is the biggest proof risk?**
- A) Using weak or subjective evidence to claim “improved output.”
- B) Having too many deterministic assertions.
- C) Relying on ERC PoC as the first proof surface.
> Recommendation: A — the whole WF can overclaim without a tight proof object. B is not a real risk here. C is actually the best available starting point.
> **Selected: A**

**Q3: What hidden-coupling risk should later phases inspect?**
- A) Assumptions in validator, pipeline, and prompt surfaces that currently expect an expectations-only snapshot.
- B) Marketing copy drift.
- C) YAML template syntax drift.
> Recommendation: A — this is the likely technical coupling. B and C are irrelevant to the runtime seam.
> **Selected: A**

**Q4: What product-boundary risk should closure language guard against?**
- A) ERC PoC runtime proof being mistaken for universal cross-call product benefit.
- B) Understating that YAML exists.
- C) Researchers noticing more specific output.
> Recommendation: A — this is the main honesty risk at closeout. B is trivial. C is not a defect.
> **Selected: A**

**Q5: How should the workflow react if deterministic proof is weaker than expected?**
- A) Fail closed and narrow the claim or the seam.
- B) Ship the runtime change and describe proof as future work.
- C) Recast the outcome as general prompt-quality exploration.
> Recommendation: A — it preserves integrity. B and C both hide failure behind softer wording.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: What is the smallest functional slice for MVP?**
- A) One narrow runtime seam that makes ERC PoC subordinate prompts reachable to structured-review execution plus deterministic proof that they influence runtime behavior.
- B) A broad runtime redesign that future-proofs all call fidelity work.
- C) Only a new activated snapshot field with no downstream consumption.
> Recommendation: A — it matches the defect and preserves scope. B is too broad. C is insufficient.
> **Selected: A**

**Q2: What should the first deterministic proof object emphasize?**
- A) Runtime artifact change tied to official subordinate concerns, such as prompt content, expanded expectation units, or equivalent execution-surface coverage.
- B) Manual comparison of final review prose only.
- C) Ingest and persistence snapshots only.
> Recommendation: A — it is the tightest proof of runtime consumption. B is too subjective. C stops before runtime effect.
> **Selected: A**

**Q3: What should count as MVP output improvement?**
- A) More explicit coverage of official sub-issues and lower omission risk in the runtime review surface, proven deterministically.
- B) Longer prompts.
- C) Any visible output difference.
> Recommendation: A — it stays tied to the encoded source concerns. B and C are too weak.
> **Selected: A**

**Q4: What should MVP explicitly exclude?**
- A) Broad quality-evaluation loops, multi-call migration, and universal product claims.
- B) ERC PoC proof entirely.
- C) Deterministic tests.
> Recommendation: A — these are valid exclusions. B and C would remove the core proof.
> **Selected: A**

**Q5: What should happen if the smallest seam cannot support a strong enough claim?**
- A) Narrow the claim to the strongest honest intermediate runtime effect and reject broader product-language.
- B) Keep the broader claim but weaken the evidence requirement.
- C) Expand scope until a convincing story appears.
> Recommendation: A — fail-closed narrowing is the right behavior. B and C are unsafe.
> **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: Which already-solved area must stay out of scope?**
- A) WF-0074 authoring/governance hardening.
- B) The runtime seam itself.
- C) Deterministic testing.
> Recommendation: A — it is explicitly prior truth. B and C are central to this WF.
> **Selected: A**

**Q2: Which proof-call task must stay out of scope?**
- A) Re-solving ERC PoC page-43 completeness already delivered by WF-0075.
- B) Using ERC PoC as the first runtime proof surface.
- C) Preserving ERC PoC completeness during runtime work.
> Recommendation: A — completeness is solved already. B and C remain necessary.
> **Selected: A**

**Q3: Which architecture direction is a non-goal?**
- A) Broad engine redesign or generic ontology work.
- B) Minimal explicit contract widening.
- C) Narrow prompt-building or expectation-expansion consumption.
> Recommendation: A — that is exactly what this WF should avoid by default. B and C are viable means, not non-goals.
> **Selected: A**

**Q4: Which product claim is a non-goal?**
- A) Claiming all calls now benefit equally from subordinate-prompt runtime consumption.
- B) Claiming ERC PoC has bounded proof only.
- C) Claiming deterministic runtime influence for the implemented seam once tests prove it.
> Recommendation: A — universal benefit is not proven. B and C are acceptable when supported.
> **Selected: A**

**Q5: Which proof style is a non-goal?**
- A) Intuition-driven or manual-demo-only proof of improved output.
- B) Deterministic runtime artifact assertions.
- C) Explicit fail-closed verification matrix rows.
> Recommendation: A — this is the exact proof style the workflow must reject. B and C are required forms of rigor.
> **Selected: A**
