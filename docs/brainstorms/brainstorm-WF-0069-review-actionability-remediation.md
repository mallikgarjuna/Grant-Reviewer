<!-- docs/brainstorms/brainstorm-WF-0069-review-actionability-remediation.md -->
# WF-0069 — Review Actionability Remediation

Artifact: brainstorm
Version: v0.1
Status: Draft
Last Updated: 2026-03-09

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- If a Q&A block reveals a new contract or contradicts the brainstorm, **promote** the contract into this brainstorm and log it in `docs/logs/decisions.md`.
- For each major decision, add 1–3 “Contract Notes / Non-obvious constraints” bullets and link to the relevant Q&A section header.

## Repo Reality Snapshot (Read-Only)

Last Updated: 2026-03-09

- WF-0068 is completed and already closed with `mission_result=fail`, `follow_on_decision=proceed_to_narrow_follow_on_wf`, and `recommended_follow_on_boundary=actionability_cluster`.
- The repeated failure appears on all three `actionability_prioritization_stress` items in the locked NWO/ERC/MSCA wedge, not on a single anecdotal example.
- The failing outputs in the WF-0068 evidence bundle are mostly uniform `content_evaluated` or `missing_context:*` review cards with `NOTE` ratings, which do not express defensible next-step guidance or ordering.
- `backend/app/engine/findings/evaluator.py` and `backend/app/engine/compat/review_card_mapper.py` currently collapse pipeline findings into minimal review-card feedback strings, which is the strongest observed seam behind the repeated actionability/prioritization failure.
- A prompt-builder path still exists in the repo, but WF-0068’s frozen baseline used `pipeline_v1` with `LLM_MODE=stub`, so prompt tuning alone is not yet the best-supported primary problem statement.

---

## 1. Problem Statement

PeerLens review outputs repeatedly fail to give researchers defensible next revision moves in priority order for the proven `actionability_prioritization_stress` cases inside the locked NWO/ERC/MSCA wedge.

WF-0068 already established that this is not a single-call anecdote: the same `actionability_cluster` appeared across NWO, ERC, and MSCA in a consistent evidence bundle and closed with `mission_result=fail`.

The narrow problem for this WF is not “general prompt quality.” It is the bounded failure that current review-output generation and/or output contract seams are too weak to express concrete, prioritized revision guidance for the exact stress pattern WF-0068 exposed.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 1)

Contract Notes / Non-obvious constraints:

- Treat actionability and prioritization as one coupled failure boundary unless evidence later proves they can be safely separated without under-scoping the repeated defect. See Q&A Section 1.
- Anchor the problem statement to WF-0068 evidence only; do not upgrade this into a repo-wide “reviews feel weak” claim. See Q&A Section 1.
- Bias root-cause investigation toward engine/output-contract seams before prompt-only explanations because the failing WF-0068 baseline used `pipeline_v1` with stubbed LLM runtime. See Q&A Section 1.

## 2. Desired Outcome

After this WF, the review-output path should produce guidance that a researcher can use as a defensible next revision move, with the highest-priority revision surfaced ahead of lower-value comments for the same stress-case snippet.

The desired outcome is not broad launch proof. It is a fail-closed remediation closure: the exact WF-0068 stress pattern should stop failing on actionability and prioritization, while the locked wedge and adjacent trust surfaces remain unchanged.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 2)

Contract Notes / Non-obvious constraints:

- Success must be measured on the proven WF-0068 stress cases first, not on a new generalized quality score. See Q&A Section 2.
- The acceptance gate should require both concrete next moves and defensible ordering, not one without the other. See Q&A Section 2.
- This WF should close with remediation evidence, not with a broader launch-readiness claim. See Q&A Section 2.

## 3. Target User / Actor

Primary actor: researchers preparing proposal snippets inside the locked NWO/ERC/MSCA wedge who need to know what to revise next before submission.

Secondary actor: maintainers deciding whether the review-output seam is mission-credible on the proven actionability boundary. Internal evaluation convenience is not the primary target user story for this WF.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 3)

Contract Notes / Non-obvious constraints:

- Optimize for researcher revision usefulness, not for maintainer scoring ergonomics alone. See Q&A Section 3.
- Keep the user boundary on pre-submission snippet review inside NWO/ERC/MSCA only. See Q&A Section 3.
- Do not widen the actor model into admin, evaluator marketplace, or generalized AI-writing use cases. See Q&A Section 3.

## 4. Rough Idea (Unstructured Thinking)

The most credible remediation direction is to tighten the engine-to-review-card seam so outputs can express explicit revision moves and priority ordering, then allow a narrow prompt/policy adjustment only if the contract-level remediation alone cannot satisfy the acceptance gate.

The WF should inspect whether the current pipeline emits too little semantic structure for downstream cards to carry actionable guidance, whether the compatibility mapper collapses distinct finding signals into flat note text, and whether the persisted/output contract lacks fields needed to express “fix this first because X”.

The rough idea is deliberately not a UI or ops initiative. The smallest useful slice is likely backend-first with regression tests and a narrow evidence replay gate using the existing WF-0068 stress artifacts.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 4)

Contract Notes / Non-obvious constraints:

- Start with no-behavior-claim inspection of engine/card seams before expanding into prompt changes. See Q&A Section 4.
- UI changes are optional only if the backend contract produces the right semantics and a minimal display seam is strictly required to expose them truthfully. See Q&A Section 4.
- Preserve fail-closed handling for missing context; do not “fake actionability” by inventing unsupported advice. See Q&A Section 4.

## 5. Constraints

This WF must stay locked to the NWO/ERC/MSCA wedge and to the bounded `actionability_cluster` proven by WF-0068.

It must not bundle launch-floor ops, broader trust-surface work, call expansion, assisted extraction, or generic prompt tuning. Changes should stay minimal and traceable, with TDD for any behavior change.

The acceptance gate should reuse the existing WF-0068 actionability/prioritization stress evidence as the primary verification path rather than inventing a new launch-proof workflow.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 5)

Contract Notes / Non-obvious constraints:

- Keep file and seam scope narrow enough that this WF does not turn into “review quality overhaul.” See Q&A Section 5.
- Prefer reuse of existing evidence artifacts and stress cases over creating a parallel evaluation framework. See Q&A Section 5.
- Any new verification must be fail-closed remediation proof only, not product launch proof. See Q&A Section 5.

## 6. Risks / Unknowns

The largest risk is misdiagnosing the failure as prompt wording when the stronger current evidence points to a thinner engine/card contract that cannot represent actionable prioritization well in the first place.

Another risk is false closure: outputs may become longer or more polished without becoming more decision-useful. This WF should reject verbosity that does not improve defensible next-step guidance and ordering.

There is also a boundary risk that actionability remediation may depend on a small amount of traceability or cross-node context work. If that happens, the dependency must be documented as narrowly as possible rather than silently widening the WF.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 6)

Contract Notes / Non-obvious constraints:

- Treat “longer feedback” and “better actionability” as different things. See Q&A Section 6.
- Document any dependency on adjacent seams explicitly before implementation; do not let it creep in as accidental mixed scope. See Q&A Section 6.
- Preserve unsupported or insufficient-evidence states instead of replacing them with fabricated advice. See Q&A Section 6.

## Open Questions / Deferred

- Whether the minimum successful contract needs explicit per-card priority fields, review-level ordering metadata, or a smaller representational change.
- Whether a narrow prompt/policy change is needed after engine/card contract tightening, or whether that would be unnecessary scope.
- Whether remediation can stay fully backend-contract-local or requires a small downstream API/render exposure change to preserve truthful researcher-facing behavior.
- Any broader traceability, specificity, or launch-proof work beyond what is strictly required to close the proven actionability failure.

## 7. MVP Definition

Smallest functional slice: remediate the review-output path so the three WF-0068 `actionability_prioritization_stress` cases no longer fail on `revision_actionability` and `prioritization_quality`, with regression protection that prevents reversion to flat `NOTE`/status-like guidance.

This MVP should include only the minimal seam changes needed to express and preserve actionable, prioritized revision guidance, plus deterministic tests and a fail-closed evidence replay gate.

Explicitly excluded from MVP: new call support, broader review-detail polish, operational launch proof, generic quality dashboards, and cross-dimension prompt tuning.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 7)

Contract Notes / Non-obvious constraints:

- MVP closure should be stress-case based and bounded, not a blanket claim that all review quality issues are solved. See Q&A Section 7.
- Keep verification deterministic and replayable against named evidence inputs. See Q&A Section 7.
- Regression checks should ensure the fix does not silently degrade the representative baseline items or fail-closed states. See Q&A Section 7.

## 8. Explicit Non-Goals

- Reopening broader call coverage beyond NWO/ERC/MSCA.
- Bundling launch-floor ops work, rollout monitoring, or general launch-readiness proof.
- Generic trust-surface polish unrelated to the specific actionability/prioritization failure.
- Assisted extraction, submit-flow redesign, or broader proposal-context capture.
- Repo-wide prompt tuning or generalized review-quality rewriting across all dimensions.
- Reframing WF-0069 as a new evaluation workflow instead of a remediation workflow.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md` (Section 8)

Contract Notes / Non-obvious constraints:

- “Not in MVP” here means explicitly excluded from this WF, not soft follow-on work bundled into implementation if convenient. See Q&A Section 8.
- Adjacent improvements are allowed only if they are proven hard dependencies for actionability closure and documented as such. See Q&A Section 8.
- The parked “prompt quality tuning” idea remains too broad unless reduced to this exact remediation boundary. See Q&A Section 8.
