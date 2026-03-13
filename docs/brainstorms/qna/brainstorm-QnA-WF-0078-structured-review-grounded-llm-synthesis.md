<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0078-structured-review-grounded-llm-synthesis.md -->
# WF-0078 — Structured Review Grounded LLM Synthesis

Artifact: brainstorm-qna
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-13

Type: feature

---

## Preflight Step 1 — Long-Form Problem Intake

Source: user-provided initiative brief in chat on 2026-03-13.

- The active `/app` structured-review flow is `/app -> /api/bff/structured-review -> backend /api/structured-review -> StructuredReviewerService -> pipeline_v1`.
- `pipeline_v1` is deterministic and does not call OpenAI.
- WF-0075 completed ERC PoC proof-call fidelity in canonical call data.
- WF-0076 connected subordinate prompts into the structured runtime and removed raw machine subordinate-prompt IDs from researcher-facing ERC PoC review cards.
- WF-0077 added deterministic researcher-facing guidance while preserving fail-closed fallback to WF-0076-style prompt rendering.
- The next major gap is a bounded LLM synthesis layer on top of deterministic structured findings.
- Non-goals include replacing `pipeline_v1`, weakening traceability, reopening WF-0075/0076/0077, or refactoring the legacy `/reviews` path unless absolutely required by the chosen seam.

## Preflight Step 2 — Repo Reality Snapshot

- `pipeline_v1` is deterministic and already emits findings/cards without an LLM call.
- `StructuredReviewerService` is the current call-scoped structured-review presentation seam and already owns deterministic feedback transformation.
- `ReviewExecutionCore` is the existing OpenAI execution seam for a different path; using it directly would widen scope.
- `llm_client.py` provides a reusable LLM client boundary but no structured-review synthesis contract yet.
- The review detail page renders `card.feedback_text` directly, so backend contract choice remains the first decision point.

## Section 1 — Problem Statement

**Q1: What is the primary user-facing gap this WF should solve first?**
- A) Stronger proposal-improvement feedback grounded in deterministic findings, while preserving existing traceability surfaces.
- B) A more human-sounding explanation layer, even if it adds new advice beyond deterministic findings.
- C) A broader conversational critique experience for the whole structured review.
> Recommendation: A — it directly targets the real product gap without letting the LLM outrun deterministic truth. B is rejected because “better sounding” is not enough if grounding weakens. C is rejected because it is materially broader than the current seam and would force scope creep.
> **Selected: A**

**Q2: Where should the first LLM seam live?**
- A) After `pipeline_v1` findings are produced, inside the existing structured-review presentation/service layer.
- B) Inside `pipeline_v1`, so findings and synthesis are produced together.
- C) In the frontend, by rewriting deterministic card text after the API response arrives.
> Recommendation: A — it preserves deterministic SSOT while improving the user-facing contract at the narrowest existing seam. B is rejected because it blurs deterministic truth with probabilistic synthesis. C is rejected because frontend-only rewriting cannot enforce grounding or fail-closed validation.
> **Selected: A**

**Q3: What should users see when LLM synthesis is unavailable or rejected?**
- A) Keep deterministic WF-0077-style guidance visible as the default fallback.
- B) Hide guidance entirely and show only a generic failure notice.
- C) Fall back to raw machine traceability text.
> Recommendation: A — it preserves a truthful, already-approved user experience and keeps the product usable in degraded mode. B is rejected because it weakens the user experience unnecessarily. C is rejected because raw machine text is not the correct researcher-facing fallback.
> **Selected: A**

**Q4: What is the smallest safe MVP scope?**
- A) `ERC-2026-PoC` only, on the current structured `/app` flow.
- B) All calls already using the structured-review path.
- C) Both the structured `/app` flow and the legacy OpenAI-backed review path.
> Recommendation: A — it uses the narrowest scope with the strongest prior proof surfaces from WF-0075 through WF-0077. B is rejected because it widens the rollout before the contract is proven. C is rejected because it combines two different architectures and would bury the seam question.
> **Selected: A**

**Q5: What fail-closed standard should define success for this WF?**
- A) The LLM may only synthesize from deterministic findings plus approved canonical context, and any timeout/malformed/ungrounded result must fall back to deterministic guidance.
- B) The LLM may infer beyond deterministic findings if the output is useful.
- C) A failed LLM call should fail the whole review rather than degrade gracefully.
> Recommendation: A — it matches the project’s trust model and keeps the deterministic layer authoritative. B is rejected because usefulness without grounding would create a trust regression. C is rejected because the system already has a truthful deterministic fallback and should remain usable under degradation.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: What should success feel like for the researcher?**
- A) The review reads like grounded proposal-improvement synthesis tied to evaluation elements and deterministic findings.
- B) The review mainly feels more conversational, regardless of traceability clarity.
- C) The review surfaces much more text, even if it becomes harder to audit.
> Recommendation: A — it improves usefulness without sacrificing trust. B is rejected because tone alone does not solve the product gap. C is rejected because more text is not the same as better guidance and can weaken auditability.
> **Selected: A**

**Q2: What should the LLM be allowed to add?**
- A) Explanation and synthesis that restate deterministic findings in stronger researcher-facing language.
- B) New critique points inferred from the proposal text even when deterministic findings do not support them.
- C) Generic grant-writing tips not tied to the current finding.
> Recommendation: A — it keeps the output grounded and bounded. B is rejected because it creates unsupported findings. C is rejected because generic tips dilute the evaluation-criteria-grounded review contract.
> **Selected: A**

**Q3: How should the product behave when synthesis is unavailable?**
- A) Stay fully usable through deterministic guidance fallback.
- B) Show partial/possibly malformed synthesis if it seems mostly fine.
- C) Block the result until the LLM call succeeds.
> Recommendation: A — it preserves usability and trust. B is rejected because “mostly fine” is not an honest fail-closed standard. C is rejected because it turns the deterministic path into an unnecessary availability dependency on the LLM.
> **Selected: A**

**Q4: What should remain stable after this WF ships?**
- A) Deterministic findings, raw machine reasons, and rollback to WF-0077 behavior.
- B) Only the visible card layout.
- C) Nothing; the LLM layer can redefine the structured-review contract.
> Recommendation: A — it preserves the core invariants and rollback boundary. B is rejected because the visual surface is not the critical contract. C is rejected because this WF is explicitly additive, not a redesign of the structured-review contract.
> **Selected: A**

**Q5: What is the right product claim for MVP?**
- A) Bounded grounded synthesis layered on deterministic findings for the structured ERC PoC path.
- B) AI critique for all structured reviews.
- C) A universal proposal coach.
> Recommendation: A — it is the narrowest honest claim. B and C are rejected because they overstate scope and would encourage premature generalization.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary user for this workflow?**
- A) Researchers reading structured `/app` review results for proposal improvement.
- B) Internal admins validating backend machinery.
- C) Legacy-path review users.
> Recommendation: A — this is the user directly affected by the current product gap. B is secondary and C is out of scope for the current seam.
> **Selected: A**

**Q2: Who is the secondary actor we must protect through the design?**
- A) Maintainers responsible for deterministic traceability and fail-closed behavior.
- B) Marketing stakeholders focused on feature breadth.
- C) Prompt writers seeking maximum model freedom.
> Recommendation: A — maintainers guard the trust and rollback boundaries this WF depends on. B and C are rejected because they do not define the system’s safety contract.
> **Selected: A**

**Q3: What cognitive burden are we trying to reduce for the researcher?**
- A) Translating deterministic findings/guidance into stronger revision actions.
- B) Learning how the entire backend pipeline works.
- C) Comparing multiple unrelated reviews across calls.
> Recommendation: A — it is the direct user pain in the current product. B and C are broader and not the immediate problem.
> **Selected: A**

**Q4: What trust burden are we trying to reduce for maintainers?**
- A) Fear that LLM output will outrun deterministic findings or hide audit surfaces.
- B) Fear that the UI colors are too plain.
- C) Fear that the repo has too few abstractions.
> Recommendation: A — it is the core system-level risk. B and C are not the problem this WF is meant to solve.
> **Selected: A**

**Q5: What terminology constraint matters in researcher-facing text?**
- A) Use evaluation criteria/elements terminology consistently.
- B) Reuse any prior “rubric” phrasing if it sounds simpler.
- C) Let the model choose terminology dynamically.
> Recommendation: A — it aligns with canonical product language and avoids drift. B and C are rejected because they would reintroduce terminology inconsistency.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the leading architecture direction?**
- A) Add a bounded synthesis collaborator after deterministic findings at the structured-review service seam.
- B) Replace the deterministic path with an LLM-first engine.
- C) Rewrite card text only in the frontend.
> Recommendation: A — it is the narrowest safe additive seam. B is rejected because it violates the deterministic SSOT requirement. C is rejected because it cannot validate grounding or enforce fail-closed behavior.
> **Selected: A**

**Q2: What exact input family should the LLM receive first?**
- A) Deterministic finding/card payloads plus evaluation element labels and approved canonical subordinate-prompt/guidance context.
- B) The full call definition and entire proposal text with minimal filtering.
- C) Only the current `feedback_text` string.
> Recommendation: A — it provides the needed grounding while minimizing freedom to hallucinate. B is rejected because it is too broad and risky. C is rejected because it is too thin and would encourage shallow rephrasing without real grounding.
> **Selected: A**

**Q3: What output contract should the first MVP prefer?**
- A) A narrow structured synthesis payload tied to existing card/finding identities and validated before user exposure.
- B) Unstructured prose accepted as-is from the model.
- C) A review-wide essay with no per-card traceability.
> Recommendation: A — it supports validation, traceability, and deterministic fallback. B and C are rejected because they make fail-closed validation much weaker.
> **Selected: A**

**Q4: What is the smallest safe task split direction?**
- A) Backend contract + tests first, synthesis seam second, frontend/API follow-on only if truly needed.
- B) Backend, API, and frontend all at once to avoid multiple phases.
- C) Frontend prototype first, backend hardening later.
> Recommendation: A — it keeps the first proof slice narrow and honest. B is rejected because it widens too quickly. C is rejected because it would decide UX before the grounded contract is settled.
> **Selected: A**

**Q5: What should happen if the existing response shape cannot carry honest synthesized output cleanly?**
- A) Open a bounded follow-on decision in planning for a new additive field or provenance indicator.
- B) Force the synthesis into the existing field no matter what.
- C) Drop deterministic guidance entirely.
> Recommendation: A — it keeps the system honest and avoids overloading a contract prematurely. B and C are rejected because they either hide ambiguity or break fallback safety.
> **Selected: A**

## Section 5 — Constraints

**Q1: What system must remain the source of truth?**
- A) `pipeline_v1` deterministic findings and machine traceability.
- B) The LLM synthesis layer once it is added.
- C) The frontend presentation layer.
> Recommendation: A — it is the central architectural invariant. B and C are rejected because they would invert the trust model.
> **Selected: A**

**Q2: What must happen to raw machine `reason`?**
- A) It must remain preserved for audit/debug/traceability.
- B) It can be replaced by synthesized text for simplicity.
- C) It can be dropped from consideration if users do not see it directly.
> Recommendation: A — it preserves the audit and debugging contract. B and C are rejected because they weaken traceability.
> **Selected: A**

**Q3: What must happen on timeout, OpenAI failure, or malformed output?**
- A) The system must fail closed to deterministic guidance or another approved deterministic fallback.
- B) The system can show best-effort synthesis if it seems close enough.
- C) The whole review should fail hard for the researcher.
> Recommendation: A — it preserves both trust and availability. B is rejected because it is not fail-closed. C is rejected because the deterministic system already provides a truthful fallback.
> **Selected: A**

**Q4: What is the approved first-call scope?**
- A) `ERC-2026-PoC` only.
- B) Any call that already has subordinate prompts.
- C) All present and future structured calls.
> Recommendation: A — it keeps the first slice bounded to the strongest existing workflow lineage. B and C are rejected because they generalize before the seam is proven.
> **Selected: A**

**Q5: What planning/execution discipline must later phases obey?**
- A) 3-file task slices, TDD for behavior change, and explicit pass/fail verification evidence.
- B) Favor speed over verification because the model behavior is inherently fuzzy.
- C) Skip RED tests if the seam feels obviously correct.
> Recommendation: A — it is the only path that keeps this non-deterministic addition honest. B and C are rejected because they create false confidence.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the primary product risk?**
- A) Hallucinated or unsupported advice beyond deterministic findings.
- B) The synthesis being too short.
- C) The code becoming slightly more modular.
> Recommendation: A — it is the main trust failure mode. B and C are not core risks by comparison.
> **Selected: A**

**Q2: What is the primary seam risk?**
- A) Accidentally moving synthesis into `pipeline_v1` or `ReviewExecutionCore`.
- B) Keeping the seam in the structured-review service.
- C) Reusing current deterministic guidance as fallback.
> Recommendation: A — it would blur the deterministic/probabilistic boundary. B and C are protective choices, not the risk.
> **Selected: A**

**Q3: What is the primary contract ambiguity risk?**
- A) Hiding provenance/fallback semantics if synthesized text simply overwrites existing surfaces.
- B) Having too many tests.
- C) Naming the helper too specifically.
> Recommendation: A — contract ambiguity is how trust regressions become invisible. B and C are secondary implementation details.
> **Selected: A**

**Q4: What is the primary verification risk?**
- A) Using brittle exact-string assertions for live model output instead of bounded contract/fallback tests.
- B) Mocking OpenAI failures.
- C) Requiring deterministic selectors.
> Recommendation: A — brittle assertions would make the test strategy dishonest or unstable. B and C are necessary parts of a realistic proof plan.
> **Selected: A**

**Q5: What is the primary scope risk?**
- A) Expanding into frontend redesign, cross-call rollout, or legacy-path integration before the seam is proven.
- B) Keeping the first slice backend-first.
- C) Deferring broader reuse decisions.
> Recommendation: A — it would break the bounded workflow contract. B and C are exactly how we control that risk.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: What is the smallest safe WF to plan?**
- A) Bounded LLM synthesis layered onto `ERC-2026-PoC` structured-review results, downstream of deterministic findings.
- B) LLM synthesis for every structured-review call.
- C) A unified LLM redesign across structured and legacy review paths.
> Recommendation: A — it matches the narrowest safe seam and the strongest existing lineage. B and C are rejected because they widen scope prematurely.
> **Selected: A**

**Q2: What is the recommended first implementation seam?**
- A) `StructuredReviewerService`, potentially via a dedicated synthesis helper/collaborator.
- B) `pipeline_v1`.
- C) `review_execution_core`.
> Recommendation: A — it is the existing post-finding presentation seam and keeps the deterministic engine unchanged. B and C are rejected because they are execution/engine seams, not the intended bounded synthesis layer.
> **Selected: A**

**Q3: What should the first task family prove before anything else?**
- A) Input/output contract, grounding rules, and deterministic fallback behavior at the backend seam.
- B) Frontend polish for new text presentation.
- C) Broad model prompt tuning for every edge case.
> Recommendation: A — it defines the system’s truth boundary first. B and C are later concerns once the contract is safe.
> **Selected: A**

**Q4: When should frontend work enter scope?**
- A) Only if planning proves the existing response shape cannot carry honest synthesized output or provenance cleanly.
- B) Immediately, because visible AI features should always change the UI.
- C) Never, even if the response shape becomes ambiguous.
> Recommendation: A — it keeps frontend work conditional and evidence-driven. B is rejected because it assumes UI work before the contract is known. C is rejected because a proven ambiguity would still need to be solved somewhere.
> **Selected: A**

**Q5: What remains explicitly out of MVP?**
- A) Replacing the deterministic engine, broad multi-call rollout, and legacy-path refactors.
- B) Deterministic fallback behavior.
- C) Audit/debug traceability.
> Recommendation: A — it preserves the bounded WF promise. B and C are rejected because they are essential, not optional.
> **Selected: A**

## Part B Audit Resolution Notes

- Recommended resolution applied: the MVP synthesis unit is per-card, not per-node and not whole-review, so degradation can fail closed card-by-card.
- Recommended resolution applied: the MVP output contract is additive, preserving deterministic `feedback_text` as fallback and introducing an optional synthesized companion surface plus provenance/source signaling.
- Recommended resolution applied: raw machine `reason` remains audit-only and is explicitly excluded from the approved LLM prompt boundary.
- Recommended resolution applied: timeout, client error, malformed output, and grounding rejection all degrade to deterministic WF-0077 guidance for the affected card without failing the whole review.
- Recommended resolution applied: the first implementation slice is explicitly backend-first and must remain within a three-file boundary before any API/frontend follow-on is opened.
- Recommended resolution applied: a backend-only seam proof is not automatically a ship-ready rollout because the current persisted/API review-detail contract still centers on `feedback_text`; any synthesized companion/provenance carry-through must be made explicit in planning before researcher-facing rollout is claimed.
