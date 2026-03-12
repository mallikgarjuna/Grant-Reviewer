<!-- docs/brainstorms/brainstorm-WF-0076-subordinate-prompt-runtime-consumption.md -->
# WF-0076 — Subordinate Prompt Runtime Consumption

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-12

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for contracts and decisions for WF-0076.
- The Q&A transcript is rationale only; it must not become the only place where runtime-scope, success criteria, or closure rules live.
- WF-0074 is prior truth for authoring/governance: typed `subordinate_prompts`, template default, fail-closed authoring workflow/checklist, durable governance, and temporary compatibility posture for existing flat canonical YAMLs are already solved.
- WF-0075 is prior truth for proof-call fidelity: `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml` is already page-43 complete across `1.a`, `1.b`, and `1.c`, with fail-closed proof for `absent_by_source`, `partially_encoded`, and `fully_encoded`.
- WF-0076 exists because runtime consumption is still unsolved: structured-review activation still exposes only `schema_version` plus `expectations`, so no honest runtime-improvement claim is valid yet.

## Long-Form Problem Intake

WF-0074 and WF-0075 together solved canonical fidelity, not runtime effect. PeerLens can now store high-fidelity subordinate prompts in canonical call data, and the ERC PoC proof-call fully encodes the official page-43 subordinate prompts across `1.a`, `1.b`, and `1.c`. That prior truth must remain intact.

The remaining defect is narrower: the structured-review runtime still does not consume that subordinate-prompt fidelity. The product therefore still risks generating review output that is less specific, less source-grounded, and less complete than the encoded call data now allows. The unresolved problem is not "missing schema" or "missing proof-call authoring"; it is runtime non-consumption of already-authored subordinate prompts.

This workflow must focus on the smallest runtime seam that currently discards subordinate prompts and the smallest honest contract change that makes them reachable to structured-review execution. The change must create a real product effect, not a paper effect. Success is not more docs, more schema, or more stored JSON; success is a proven change in runtime behavior with explicit boundaries.

The preferred proof surface is the ERC PoC proof-call because WF-0075 already established it as the fully encoded, fail-closed proof-call. Any claim that subordinate prompts improve review specificity, completeness, actionability, or reliability must be backed by deterministic executable proof. If such proof cannot be made tight, the workflow must fail closed and narrow scope rather than overclaim.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Preflight Step 1)

Contract Notes / Non-obvious constraints:
- This workflow is downstream of canonical fidelity; it must not reopen the authoring/governance scope already solved in WF-0074.
- This workflow is downstream of proof-call completeness; it must not restate the WF-0075 problem as if the ERC PoC call were still only partially encoded.
- Runtime impact claims are invalid unless the new seam is exercised by deterministic tests that prove subordinate prompts influence execution behavior.

## Repo Reality Snapshot (Read-Only)

- `backend/app/schemas/call_definitions_v2.py` and the canonical ERC PoC YAML already preserve typed `subordinate_prompts`; representability is no longer the open gap.
- `backend/tests/test_call_subordinate_prompt_coverage.py` proves the ERC PoC proof-call is fully encoded across page-43 elements `1.a`, `1.b`, and `1.c`; proof-call completeness is no longer the open gap either.
- `backend/app/services/structured_reviewer_service.py` currently serializes `call_config_snapshot` as only `{\"schema_version\": \"v1\", \"expectations\": [...]}`. The snapshot-building seam discards subordinate prompts before validation and pipeline execution.
- `backend/app/engine/contracts.py`, `backend/app/engine/review_request_validator.py`, and `backend/app/engine/pipeline_v1.py` can represent richer snapshot fields in theory, but the live runtime path currently validates and executes only the expectations-only snapshot actually emitted by the service.
- `backend/app/services/prompt_builder.py` renders prompts from `NodeExpectation` plus flat `EvaluationElement` description text; there is no current runtime path that passes subordinate prompts into prompt construction or expectation expansion.

## Open Questions / Deferred

- Preferred default to validate in Phase 1: subordinate prompts should travel as a narrow child payload attached to existing activated expectation or evaluation-element context; if that seam proves too coupled, the fallback is the smallest equivalent runtime representation that still produces deterministic runtime-effect proof.
- What exact operational definition of "improved output" is tight enough to verify deterministically without overclaiming researcher-facing impact?
- Can the initial proof stay bounded to the ERC PoC proof-call without forcing multi-call runtime redesign?

## 1. Problem Statement

- The unresolved defect is runtime non-consumption of already-authored subordinate prompts, not missing schema, missing authoring guidance, or incomplete ERC PoC proof-call fidelity.
- The exact discard seam is the structured-review activation path in `backend/app/services/structured_reviewer_service.py`, which emits an expectations-only `call_config_snapshot` and strips subordinate-prompt fidelity before validation, pipeline execution, and prompt construction.
- The primary actor is the runtime owner or maintainer who needs canonical subordinate-prompt fidelity to become executable; the downstream beneficiary is the researcher who should receive more source-grounded review output.
- The initial proof surface is the ERC PoC proof-call because WF-0075 already made it the fully encoded, fail-closed proof-call.
- The problem remains unresolved unless subordinate prompts become part of the runtime path that actually influences review behavior and that influence is proven with deterministic tests.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Section 1)

Contract Notes / Non-obvious constraints:
- “Improve prompt quality” is too vague and is not an acceptable restatement of the problem.
- A snapshot-contract change without proven runtime influence does not solve the product defect.
- The workflow must preserve the distinction between canonical fidelity already solved and runtime consumption still unsolved.

## 2. Desired Outcome

- The smallest honest runtime change makes subordinate prompts reachable to structured-review execution in a way that can materially influence review behavior.
- The activated runtime contract is widened minimally and explicitly, only as far as needed to carry subordinate-prompt fidelity through the live execution path.
- Success is defined operationally by deterministic proof of runtime effect, not by richer stored JSON, more docs, or a broadened schema.
- The first proof target is bounded to ERC PoC and must not imply that all calls now benefit equally.
- The workflow should leave behind a reusable narrow seam for later calls, but any cross-call claim must stay limited to the seam itself unless broader evidence is added later.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Section 2)

Contract Notes / Non-obvious constraints:
- The desired outcome is a proven change in runtime behavior with honest boundaries.
- “Improved output” must be expressed in executable terms such as coverage, specificity, and omission reduction.
- A docs-only or storage-only outcome is explicitly insufficient.

## 3. Target User / Actor

- Primary actor: backend runtime maintainer or coding agent updating structured-review activation, prompt-building, and tests.
- Primary beneficiary: researcher receiving structured-review output that should better reflect official evaluation concerns already encoded in the call definition.
- Secondary beneficiary: future maintainers who need an honest runtime contract and repeatable proof rather than a folklore claim that subordinate prompts “probably help.”
- Initial actor scope is ERC PoC runtime proof only; do not broaden the beneficiary story into universal product coverage.
- The workflow remains internal/backend-facing in implementation while evaluating downstream product effect through deterministic runtime outputs.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Section 3)

Contract Notes / Non-obvious constraints:
- The user-facing beneficiary matters, but the implementation seam is internal and should be described that way.
- This is not an onboarding-authoring workflow; the affected actor is no longer primarily the YAML author.

## 4. Rough Idea (Unstructured Thinking)

- Preferred direction: widen the activated snapshot or equivalent runtime representation just enough to carry subordinate prompts alongside the existing expectation references, then consume that new detail at the nearest prompt-building or expectation-expansion seam that can alter review behavior.
- The initial design should prefer subordinate prompts as a narrow child payload attached to existing expectation/evaluation-element context, not as a broad engine redesign or ontology expansion.
- The first implementation should prove one concrete behavior change: runtime review instructions cover official subordinate concerns that were previously only implicit in flat element descriptions.
- The proof surface should stay close to the existing structured-review path: activation, request validation, prompt construction and/or expectation evaluation, and deterministic test assertions on resulting runtime artifacts.
- If the smallest viable seam turns out to be richer expectation expansion rather than raw snapshot passthrough, that is acceptable so long as the change remains narrow, explicit, and provable.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Section 4)

Contract Notes / Non-obvious constraints:
- The workflow should not commit prematurely to a specific internal shape before Phase 1 inspects the narrowest safe seam.
- Any representation chosen must preserve WF-0074 compatibility posture unless explicitly re-approved.
- The implementation target is the smallest equivalent runtime surface that can materially affect review behavior.

## 5. Constraints

- Preserve WF-0074’s temporary compatibility posture for existing flat canonical YAMLs unless a later phase proves and re-approves a narrower rule.
- Preserve WF-0075’s proof-call completeness and use ERC PoC as the first proof surface.
- Avoid broad engine redesign, generic ontology work, multi-call migration, or unbounded prompt-system refactors.
- Keep the runtime contract change minimal, explicit, and testable.
- Fail closed on product claims: no more specific, actionable, reliable, or source-grounded output claim is allowed without executable proof.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Section 5)

Contract Notes / Non-obvious constraints:
- Scope discipline is a first-class requirement, not a preference.
- The workflow may touch runtime code, but it must not use that as a license to redesign unrelated review-engine seams.

## 6. Risks / Unknowns

- The biggest risk is widening the snapshot contract without producing a real runtime effect, which would recreate the “stored but unused” defect one layer later.
- Another key risk is overclaiming product improvement from synthetic or weak evidence instead of deterministic proof tied to runtime artifacts.
- A narrow runtime seam may still be hidden-coupled to validator, pipeline, or prompt-builder assumptions that currently expect an expectations-only snapshot.
- There is a product-proof risk that “improved output” is defined too loosely; if success criteria are not falsifiable, the workflow can drift into intuition-driven claims.
- There is also a boundary risk that ERC PoC proof could be mistaken for universal benefit if closure language is not explicit.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Section 6)

Contract Notes / Non-obvious constraints:
- Deterministic proof should target runtime consumption first, and review-quality claims only to the extent that they can be operationalized.
- Hidden coupling across activation, validation, and pipeline serialization must be audited in Phase 1 before code changes are planned.

## 7. MVP Definition

- Smallest defensible slice:
  - identify the exact runtime seam that currently discards subordinate prompts,
  - add the smallest contract/runtime representation change needed to surface them to structured-review execution,
  - wire that detail into prompt construction, expectation expansion, or the smallest equivalent runtime surface that can change review behavior,
  - add deterministic tests proving subordinate prompts influence runtime behavior rather than merely persisting in canonical JSON,
  - use ERC PoC as the first proof-call and preserve explicit honesty that broader call benefit is unproven.
- “Improved output” for MVP means at least one deterministic runtime proof shows previously implicit official sub-issues are now explicitly carried into the runtime review surface, reducing omission risk and increasing source-grounded specificity.
- MVP does not require a broad quality-evaluation program across many snippets or calls, but it does require one fail-closed proof object stronger than “the payload now contains more fields.”
- If no tight deterministic proof of runtime effect is available, the MVP must narrow to the strongest honest intermediate seam and explicitly reject broader product-effect claims.
- MVP closure requires a row-based fail-closed verification matrix, not prose-only verification.

### Recommended First Proof Surface

- Start with ERC PoC and prove runtime consumption at the nearest deterministic artifact, in this order of preference:
  - activated snapshot / contract payload,
  - prompt-construction artifact,
  - expectation-expansion artifact,
  - review-card content or coverage assertions only if the earlier artifacts are insufficient to prove real runtime influence.
- The first proof should prefer exact carry-through of official subordinate concerns over subjective final-prose evaluation.
- If review-card assertions are used, they must remain deterministic and source-grounded rather than style-judgment-based.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0076-subordinate-prompt-runtime-consumption.md` (Section 7)

## Verification / Proceed Gate

- No proceed recommendation is valid if the planned change only preserves subordinate prompts in canonical storage or dry-run output without making them reachable to structured-review execution.
- No proceed recommendation is valid if the activated runtime contract changes but deterministic tests still cannot prove subordinate prompts influence runtime behavior.
- No proceed recommendation is valid if the workflow blurs together:
  - authoring/governance solved in WF-0074,
  - proof-call fidelity solved in WF-0075,
  - runtime consumption still unsolved before this WF.
- No proceed recommendation is valid if ERC PoC proof is used to imply equal product benefit for other calls without additional evidence.
- No proceed recommendation is valid if the proposed seam forces broad engine redesign or silently narrows WF-0074 compatibility posture without explicit proof and re-approval.

### Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Runtime discard seam proof | targeted activation/snapshot test | `fail` (default until executed) | required | must prove exactly where subordinate prompts are dropped today |
| Minimal contract widening | contract/snapshot validator test | `fail` (default until executed) | required | must prove the smallest new runtime shape is accepted and serialized deterministically |
| Runtime consumption proof | structured reviewer service test and at least one prompt-construction or expectation-expansion test | `fail` (default until executed) | required | must prove subordinate prompts influence runtime behavior, not just storage |
| Output-level improvement proof | deterministic prompt, expanded-expectation, and/or review-card coverage assertion | `fail` (default until executed) | required | must prove better official-concern coverage, specificity, or omission reduction in an operationalized way |
| ERC PoC proof-call preservation | targeted ERC PoC regression | `fail` (default until executed) | required | must preserve WF-0075 completeness while using ERC PoC as first proof surface |
| WF-0074 compatibility-posture preservation | regression and/or approved-artifact citation | `fail` (default until executed) | required | must preserve temporary compatibility for existing flat canonical YAMLs unless re-approved |
| Boundary honesty | review-range ledger plus artifact citations | `fail` (default until executed) | required | must preserve the distinction between solved fidelity and newly solved runtime consumption |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close every blocking finding and close or reject justified non-blocking findings with rationale |

- Proceed recommendation remains blocked unless every required row above is `pass`, or explicitly `skipped` with accepted rationale during review.

## 8. Explicit Non-Goals

- Re-solving schema support, template defaults, authoring workflow, or governance already landed in WF-0074.
- Re-solving ERC PoC page-43 proof-call completeness already landed in WF-0075.
- Broad review-engine redesign, generic ontology work, or multi-call subordinate-prompt migration.
- Claiming that all calls now produce better output equally once the ERC PoC runtime seam is proven.
- Using intuition, ad hoc examples, or manual demos as the primary proof that subordinate prompts improved runtime behavior.

## Changelog

- v0.1 (2026-03-12): Captured prior truth from WF-0074/WF-0075, verified the live runtime discard seam in `structured_reviewer_service.py`, and framed WF-0076 around the smallest honest runtime-consumption change plus deterministic product-effect proof.
- v0.2 (2026-03-12): Tightened the recommended representation bias, made the first deterministic proof surface explicit, and named concrete test categories for runtime-consumption and output-level proof.
