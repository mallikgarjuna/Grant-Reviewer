<!-- docs/brainstorms/brainstorm-WF-0078-structured-review-grounded-llm-synthesis.md -->
# WF-0078 — Structured Review Grounded LLM Synthesis

Artifact: brainstorm
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-13

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for scope, boundaries, and implementation direction for WF-0078.
- The Q&A transcript is rationale only; it must not become the only place where seam choice, fallback rules, or task-splitting constraints live.
- `pipeline_v1` remains the deterministic source of truth for structural validation, expectation evaluation, cross-node alignment, finding generation, and machine traceability.
- Raw machine `reason` remains preserved for audit and traceability; any LLM output in this WF must be additive presentation/synthesis layered on top of deterministic findings.
- WF-0075, WF-0076, and WF-0077 boundaries remain prior truth and are not reopened by this workflow.

## Long-Form Problem Intake

The active researcher-facing `/app` review flow is the structured path: `/app` calls `/api/bff/structured-review`, which reaches backend `/api/structured-review`, `StructuredReviewerService`, and `pipeline_v1`. That path is deterministic and does not call OpenAI today. Even after WF-0077, the structured-review user experience is still deterministic guidance rather than true LLM-backed critique of the proposal text the researcher submitted.

WF-0075 completed ERC PoC proof-call fidelity so the canonical call data now contains the official subordinate prompts. WF-0076 carried those subordinate prompts into the structured-review runtime and removed raw machine output such as `content_evaluated;subordinate_prompt_ids=...` from researcher-facing ERC PoC cards. WF-0077 added deterministic researcher guidance on top of that structured path, using the existing presentation seam and preserving fail-closed fallback to WF-0076-style prompt rendering when the source surface is weak or unusable.

The remaining product gap is now narrower and more dangerous: the structured `/app` path still lacks a bounded LLM synthesis layer that can turn deterministic findings into stronger researcher-facing proposal-improvement feedback without weakening deterministic traceability. This workflow therefore needs to design the narrowest safe seam for an LLM-backed synthesis/explanation layer that runs after deterministic findings are produced, stays grounded in structured findings plus canonical context, preserves the raw deterministic evidence for audit/debug, and fails closed or falls back deterministically if the LLM fails or returns malformed output.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Preflight Step 1)

Contract Notes / Non-obvious constraints:
- The problem is not missing deterministic inputs; the structured path already has findings, evaluation elements, and canonical subordinate-prompt context.
- The problem is not in `pipeline_v1`; the deterministic engine must remain the source of truth rather than becoming an LLM-first engine.
- The product risk is a trust regression if synthesized text outruns the deterministic findings or obscures the raw machine traceability surfaces.

## Repo Reality Snapshot (Read-Only)

- `backend/app/engine/pipeline_v1.py` is deterministic end-to-end today: it validates the request, evaluates expectations and observations, aggregates findings, and maps them into review cards without calling OpenAI.
- `backend/app/services/structured_reviewer_service.py` is the current post-pipeline presentation seam for the active structured path. It already rewrites deterministic `feedback_text` for WF-0069/WF-0076/WF-0077 while preserving the underlying machine-oriented flow.
- `backend/app/services/review_execution_core.py` is still the legacy OpenAI-backed node-execution seam. Pulling it into the structured path would widen the change from post-finding synthesis into execution-engine substitution.
- `backend/app/services/llm_client.py` already exposes a narrow client protocol plus stub client, which makes it a plausible dependency for a new synthesis collaborator, but its current default model/config surface is generic and not yet scoped to structured-review synthesis contracts.
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` still renders `card.feedback_text` directly and exports it verbatim, so frontend changes are not the narrowest starting seam for this workflow.

## Open Questions / Deferred

- Whether the first user-facing rollout needs a minimal UI/provenance affordance once the additive synthesis response field exists, or whether backend/API contract proof will show the current rendering path can expose it honestly without extra design work.
- Whether broader call rollout beyond `ERC-2026-PoC` should happen by call-family wedges or only after a generic synthesis contract is proven on the first slice.
- Whether later phases should add internal telemetry for synthesis rejection categories beyond the minimum fail-closed runtime handling required for MVP.

## 1. Problem Statement

- The primary product gap is not missing review findings; it is that the active structured `/app` flow still lacks stronger researcher-facing proposal-improvement feedback on top of deterministic structured findings.
- The first responsibility of this WF is to improve researcher-facing synthesis while preserving the existing trust contract: deterministic findings stay authoritative and raw machine `reason` remains intact for audit/traceability.
- The narrowest safe seam is after deterministic findings are produced and before the response is finalized for the structured-review path, because that is where the product can improve language without turning the engine into an LLM-first executor.
- If the LLM layer fails, times out, or produces malformed/ungrounded output, the system must fail closed to deterministic guidance rather than degrade into raw machine strings or unsupported advice.
- The first approved scope is `ERC-2026-PoC` only on the current structured `/app` flow so the workflow stays bounded to the strongest existing proof surface.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Section 1)

Contract Notes / Non-obvious constraints:
- The problem is a presentation/synthesis gap, not a finding-generation gap.
- The seam must stay downstream of `pipeline_v1` to preserve deterministic SSOT.
- Fallback must preserve WF-0077 deterministic guidance as the default user-visible degraded mode.

## 2. Desired Outcome

- Researchers using the structured `/app` path for `ERC-2026-PoC` should receive stronger proposal-improvement feedback that reads like grounded synthesis of the deterministic findings rather than only deterministic guidance primitives.
- The LLM output should explain what to improve, why it matters for the relevant evaluation element, and how the deterministic finding supports that advice, without inventing new findings or unsupported claims.
- Success for MVP is not “there is an LLM call”; success is that the structured-review path returns bounded, grounded synthesized feedback while deterministic findings and traceability surfaces remain preserved and inspectable.
- When synthesis is unavailable, the product should remain fully usable by showing deterministic guidance rather than a hard failure or raw machine trace text.
- The desired architecture outcome is an additive synthesis layer that can be audited, disabled, or rolled back without disturbing the deterministic review engine.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Section 2)

Contract Notes / Non-obvious constraints:
- “Stronger feedback” means grounded synthesis over deterministic findings, not free-form critique.
- MVP should preserve a deterministic-only usable experience even when synthesis is unavailable.
- The synthesis layer must be narrow enough that rollback returns the product cleanly to WF-0077 behavior.

## 3. Target User / Actor

- Primary user: researchers reading structured-review results in `/app` and trying to improve their submitted proposal text.
- Secondary actor: maintainers who need to preserve deterministic traceability, fail-closed behavior, and prior WF boundaries while introducing a bounded LLM dependency.
- This WF is not primarily for internal admins, prompt engineers, or users of the legacy `ReviewerService` path.
- The primary user pain is cognitive translation: today the product exposes deterministic guidance, but the researcher still has to perform too much of the synthesis themselves.
- The maintainer pain is trust risk: any LLM layer that outruns the deterministic findings would create hidden coupling and weaken auditability.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Section 3)

Contract Notes / Non-obvious constraints:
- User-facing language must say evaluation criteria/elements, never “rubric.”
- The researcher-facing UX can improve only if the backend contract remains honest about deterministic versus synthesized surfaces.
- This WF should not assume a separate actor workflow in the legacy review path.

## 4. Rough Idea Exploration

- The leading direction is a bounded synthesis collaborator invoked by the structured-review service after `pipeline_v1` produces deterministic findings/cards and before the final response is assembled.
- The synthesis unit for MVP should be per-card, not whole-review and not whole-node, so fallback can degrade one card at a time without converting LLM availability into whole-review availability.
- The LLM input should be tightly scoped to deterministic findings, evaluation element metadata, canonical subordinate-prompt or guidance context, and a bounded excerpt from the same node text already present in the structured flow; this WF should explicitly exclude full-submission and full-call-definition prompting.
- The LLM output contract should be structured and narrow: a validated optional synthesized companion payload tied to the existing card/finding identity, plus a small provenance/source enum that allows malformed or ungrounded output to be rejected before user exposure.
- The safest first task split is likely:
  1. define the backend synthesis contract, input boundary, and deterministic fallback behavior at the structured-review service seam,
  2. add the narrow backend synthesis collaborator and tests at that seam within a three-file slice,
  3. add any minimal API/frontend exposure only if the additive synthesis field or provenance indicator is required for honest user-facing exposure.
- This WF should prefer adding a new additive synthesis layer over replacing current deterministic guidance logic, because replacement would collapse the rollback boundary and weaken fail-closed safety.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Section 4)

Contract Notes / Non-obvious constraints:
- `StructuredReviewerService` is the recommended orchestration seam; `pipeline_v1` remains unchanged as SSOT.
- `ReviewExecutionCore` is too deep and semantically wrong for the first slice because it is an execution seam, not a post-finding synthesis seam.
- Frontend-only rewriting is too late to enforce grounding or fail-closed output validation.
- The recommended MVP contract is additive: preserve deterministic `feedback_text` as the stable fallback surface and introduce an optional synthesized companion surface rather than silently overwriting provenance.

## 5. Constraints

- `pipeline_v1` must remain the deterministic source of truth for validation, expectation evaluation, cross-node alignment, finding generation, and machine traceability.
- Raw machine `reason` must remain preserved for audit/debug/traceability and must not be overwritten or hidden by the LLM layer.
- The LLM layer must be grounded in deterministic findings plus approved canonical context; it must not become a free-floating critique engine over the full submission.
- If OpenAI fails, times out, or returns malformed output, the system must explicitly fail closed to deterministic guidance or another approved deterministic fallback rather than failing open.
- Respect prior boundaries from WF-0075, WF-0076, and WF-0077, keep scope to `ERC-2026-PoC` first, follow the 3-file task-slice rule during execution planning, and require TDD with explicit pass/fail verification evidence for behavior changes.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Section 5)

Contract Notes / Non-obvious constraints:
- The LLM layer may be new, but the user-visible degraded mode must stay deterministic and truthful.
- Any first task that needs more than three files should be split before implementation starts.
- The workflow must not quietly widen into the legacy `/reviews` path.

## Approved LLM Input Boundary

- Allowed inputs for MVP per-card synthesis are:
  - deterministic card/finding identity already produced by the structured path,
  - node logical/title context for the same card,
  - evaluation criterion/element labels relevant to that card,
  - deterministic WF-0077-style guidance for that card,
  - approved canonical subordinate-prompt/guidance context already attached to the same evaluation element,
  - a bounded excerpt from the same submitted node text under review.
- Explicit exclusions for MVP are:
  - full proposal text outside the current card/node scope,
  - full call definitions or unrelated evaluation elements,
  - raw machine `reason` strings as prompt material,
  - unrelated node findings,
  - legacy-path prompts or reviewer-service execution artifacts.

Contract Notes / Non-obvious constraints:
- The model should receive enough basis to explain a finding, but not enough scope to invent a new review.
- Raw machine `reason` stays audit-only unless a later artifact explicitly proves a need to expose or transform it, which is not approved here.

## Approved Output Contract

- MVP should prefer a per-card additive output contract with:
  - the existing deterministic card identity unchanged,
  - the existing deterministic `feedback_text` preserved as the stable fallback/user-visible deterministic guidance surface,
  - an optional synthesized companion field for grounded LLM explanation,
  - a small synthesis source/provenance enum indicating `synthesized` or `deterministic_fallback`,
  - rejection semantics that drop the synthesized companion field if validation or grounding checks fail.
- The workflow should not assume this additive field is immediately exposed in the UI; Phase 1 must decide whether API/frontend exposure is necessary for honest researcher-facing rollout or whether the current response/rendering path can consume it safely.

Contract Notes / Non-obvious constraints:
- Per-card synthesis keeps degradation granular and avoids whole-review availability coupling.
- Additive output is safer than overloading `feedback_text` because it preserves backward-compatible deterministic meaning until later phases explicitly change presentation.

## Fail-Closed Runtime Contract

- Synthesis is attempted per card after deterministic findings/guidance already exist.
- If the LLM client times out, errors, returns malformed output, or returns schema-valid output that fails grounding checks, the affected card must drop synthesis and remain on deterministic WF-0077 guidance.
- A synthesis failure for one card must not fail the entire review if deterministic card output remains available.
- The overall structured review may still complete successfully in deterministic mode even when all synthesis attempts are rejected, because the deterministic path remains the authoritative product baseline.
- Later phases may choose whether degraded-mode provenance is surfaced to researchers, but they may not expose rejected synthesis content.

Contract Notes / Non-obvious constraints:
- “Fail closed” here means rejected synthesis never outranks deterministic truth.
- Grounding rejection must cover unsupported evaluation elements, advice not supported by provided basis, and any output shape that cannot be unambiguously attached to the originating card.

## 6. Risks / Unknowns

- The biggest risk is hallucinated or overconfident advice that goes beyond what deterministic findings and canonical context actually support.
- A second major risk is seam drift: moving synthesis into `pipeline_v1` or `ReviewExecutionCore` would blur the boundary between deterministic truth and probabilistic explanation.
- Another risk is contract ambiguity: if synthesized text reuses `feedback_text` without a clear fallback or provenance rule, later phases may accidentally hide deterministic guidance or make audit/debug harder.
- Honest testing is a real unknown because the LLM layer is non-deterministic; the proof strategy will need contract validation, stubbed malformed/failure cases, and bounded assertion style rather than brittle exact-string expectations for live model output.
- There is also a scope risk that this WF grows into frontend redesign, cross-call rollout, or legacy-path integration before the first bounded structured-path seam is proven.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Section 6)

Contract Notes / Non-obvious constraints:
- Fail-closed validation of LLM output is a product requirement, not just a testing nicety.
- The contract must distinguish deterministic source truth from synthesized explanation clearly enough to support debugging.
- Non-determinism means the first proof surface should emphasize shape, grounding, and fallback semantics over prose exactness.

## 7. MVP Definition

- The smallest safe WF is: add a bounded LLM synthesis layer to the structured-review backend path for `ERC-2026-PoC`, downstream of `pipeline_v1`, with deterministic findings remaining SSOT and WF-0077 deterministic guidance preserved as fallback.
- The narrowest recommended architecture seam is `StructuredReviewerService`, potentially with a dedicated helper/collaborator that receives deterministic findings plus approved context and returns a validated synthesis payload or a fallback signal.
- The smallest safe implementation split should begin with a backend-only contract slice that touches no more than three files: the structured-review service seam, one synthesis helper/collaborator seam if needed, and backend tests. Any API/frontend exposure should become a dependent follow-on slice if the additive output field is required for honest rollout.
- A safe MVP can close backend-only if the existing structured response contract can carry honest synthesized text plus deterministic fallback without hiding raw traceability from audit/debug surfaces.
- MVP explicitly excludes replacing `pipeline_v1`, moving synthesis into the execution core, broadening beyond `ERC-2026-PoC`, or refactoring the legacy `ReviewerService` path.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md` (Section 7)

Contract Notes / Non-obvious constraints:
- The workflow should stop if the first bounded slice needs to touch more than three files before the task plan is split.
- A new additive field may be safer than overloading `feedback_text`, but that remains open until Phase 1 hardens the contract.
- The first planning artifact should force explicit decisions on input shape, output contract, and degraded-mode visibility.

## Verification / Proceed Gate

- No proceed recommendation is valid if `pipeline_v1` stops being the deterministic source of truth for findings or if the LLM layer becomes the primary evaluator.
- No proceed recommendation is valid if raw machine `reason` is mutated, suppressed, or made inaccessible for audit/debug/traceability.
- No proceed recommendation is valid if the seam choice defaults to `ReviewExecutionCore`, frontend-only rewriting, or legacy-path reuse without explicit new approval.
- No proceed recommendation is valid if malformed, timed-out, or ungrounded synthesis can reach the user without deterministic fallback.
- No proceed recommendation is valid if the first implementation slice cannot be proven within an honest TDD contract and explicit pass/fail verification evidence.

### Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Deterministic SSOT boundary proof | Phase 1/2 artifact + code seam citations | `fail` (default until executed) | required | must prove `pipeline_v1` remains unchanged as source of truth for findings |
| Narrow seam proof | Phase 1/2 artifact + targeted backend tests | `fail` (default until executed) | required | must prove synthesis is added after deterministic findings at the structured-review service seam |
| Raw machine reason preservation | targeted backend test/assertion | `fail` (default until executed) | required | must prove audit/debug surfaces still preserve raw machine `reason` |
| Grounding contract proof | synthesis input/output contract tests | `fail` (default until executed) | required | must prove LLM inputs are bounded to deterministic findings plus approved canonical context |
| Malformed/failure fallback proof | targeted backend tests for timeout, client error, malformed output | `fail` (default until executed) | required | must prove deterministic fallback behavior remains user-visible and truthful |
| Partial-card degradation proof | targeted backend tests | `fail` (default until executed) | required | must prove one rejected synthesis payload does not fail the whole review and only degrades the affected card to deterministic guidance |
| Whole-review deterministic success proof | targeted backend tests | `fail` (default until executed) | required | must prove the review still completes truthfully when all synthesis attempts are rejected and deterministic guidance remains available |
| Honest non-determinism test strategy | Phase 1/2 task plan + verification selectors | `fail` (default until executed) | required | must prove live-model brittleness is avoided while still testing grounded behavior honestly |
| Scope-boundary proof | `main...HEAD` review + artifact citations | `fail` (default until executed) | required | must prove no widening into legacy `/reviews`, LLM-first pipeline design, or reopened WF-0075/76/77 scope |
| Optional frontend necessity check | artifact decision or targeted UI proof | `fail` (default until executed) | required | acceptable closure is an explicit backend-only rationale if no new user-visible field/provenance surface is needed |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close all blocking findings and either close or justify non-blocking findings |

## 8. Explicit Non-Goals

- Replacing `pipeline_v1` with an LLM-first engine.
- Removing or weakening raw machine traceability or audit/debug access to deterministic findings/reasons.
- Reopening WF-0075, WF-0076, or WF-0077 scope.
- Refactoring the legacy `/reviews` or `ReviewerService` path unless a later artifact explicitly proves that the chosen seam cannot work without it.
- Broad multi-call rollout, frontend redesign, or generic AI-writing-coach scope before the first bounded `ERC-2026-PoC` structured-path seam is proven.

## Changelog

- v0.1 (2026-03-13): Captured the long-form problem intake, read-only repo snapshot, recommended bounded scope (`ERC-2026-PoC` structured path), and the narrowest candidate architecture seam (`StructuredReviewerService` post-pipeline synthesis layer) while preserving deterministic SSOT and fail-closed fallback requirements.
- v0.2 (2026-03-13): Applied the Part B audit by locking the per-card additive synthesis contract, specifying the approved LLM input boundary and fail-closed runtime behavior, and tightening the smallest-safe backend-first task split so later phases cannot widen the seam implicitly.
