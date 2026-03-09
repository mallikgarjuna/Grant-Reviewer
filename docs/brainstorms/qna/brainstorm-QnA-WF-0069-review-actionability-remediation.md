<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0069-review-actionability-remediation.md -->
# WF-0069 — Review Actionability Remediation

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-09

---

## Brainstorm Q&A

### Section 1 — Problem Statement

**Q1: What exact failure should this WF treat as the primary problem?**
- A) Missing actionable next moves: outputs name issues but do not tell the researcher what to revise concretely.
- B) Bad prioritization only: outputs suggest revisions, but in the wrong order.
- C) Combined actionability + prioritization failure: outputs do not provide concrete next moves in defensible priority order.
> Recommendation: C — WF-0068 failed on both dimensions together across the repeated stress cases. A is too narrow and risks “more wording” fixes without ordering. B is too narrow and assumes actionable content already exists.
> **Selected: C**

**Q2: Where should the problem statement place the most likely root seam?**
- A) Engine/output-contract seam first: findings/cards cannot currently express enough revision guidance structure.
- B) Prompt seam first: the main problem is instruction quality.
- C) Mixed seam from the start: engine, prompt, UI, and ops all treated as equal suspects.
> Recommendation: A — current evidence shows the failing outputs collapse into minimal note/status strings, which makes the engine/card contract seam the strongest first suspect. B remains possible but is weakly evidenced. C would widen scope before proof.
> **Selected: A**

**Q3: What should count as the user-visible harm that makes this product-critical now?**
- A) Researchers cannot tell what to revise next, so review outputs do not reliably support real revision decisions.
- B) Internal evaluators cannot score review quality consistently.
- C) Launch readiness is blocked because operational proof is missing.
> Recommendation: A — this maps directly to the mission and MVP success criteria. B matters only secondarily. C would incorrectly reopen launch-floor work that this WF is explicitly not supposed to bundle.
> **Selected: A**

**Q4: How narrow should the problem boundary be across product surfaces?**
- A) Review-output remediation only: engine/card semantics needed to produce actionable, prioritized guidance.
- B) Review-output plus review-detail UI polish so the guidance reads better.
- C) General review quality improvement across prompts, engine, trust surfaces, and workflow ops.
> Recommendation: A — it directly matches the bounded follow-on decision from WF-0068. B and C both introduce extra surfaces before the failing output contract is fixed.
> **Selected: A**

**Q5: How should the problem statement describe the evidence basis?**
- A) Derived from WF-0068’s repeated stress-case failures only; no fresh speculative problem statement.
- B) Derived from WF-0068 plus a broader qualitative sense that reviews feel weak overall.
- C) Reframed as a new generic “prompt quality” problem for future flexibility.
> Recommendation: A — the workflow should stay traceable to the proven evidence bundle. B introduces unsupported generalization. C rewrites the failure boundary into a solution-shaped label.
> **Selected: A**

### Section 2 — Desired Outcome

**Q1: What measurable change should define success for this WF?**
- A) The three WF-0068 actionability/prioritization stress cases stop failing on both dimensions.
- B) Average review quality feels better in ad hoc spot checks.
- C) Researchers report subjective preference for the new wording.
> Recommendation: A — it is the narrowest, replayable closure target tied to the proven failure pattern. B and C are too soft for fail-closed scope control.
> **Selected: A**

**Q2: What behavior change should the output demonstrate?**
- A) It should identify issues more often.
- B) It should tell the researcher what to revise next and why that move comes first.
- C) It should produce longer, richer prose.
> Recommendation: B — actionability and prioritization are about decision support, not output length or issue count.
> **Selected: B**

**Q3: What should this WF explicitly not try to prove?**
- A) Full launch readiness inside the wedge.
- B) Any improvement whatsoever.
- C) That prompts are never involved.
> Recommendation: A — the WF should prove remediation closure only, not relitigate launch readiness. B is too weak. C is unnecessarily absolute.
> **Selected: A**

**Q4: What form should the acceptance gate take if a fresh evaluation step is needed?**
- A) A fail-closed rerun of the existing stress cases tied to the remediation seam.
- B) A brand-new broader evaluation batch across all dimensions.
- C) Manual eyeballing of a few sample outputs.
> Recommendation: A — it preserves traceability to WF-0068 and avoids scope drift into another evaluation initiative.
> **Selected: A**

**Q5: What should count as “good enough” for MVP?**
- A) The stress cases pass on actionability/prioritization and no obvious regression appears in baseline/fail-closed behavior.
- B) All known review-quality issues are resolved.
- C) The outputs look more polished than before.
> Recommendation: A — it is bounded, realistic, and evidence-backed. B is impossible within narrow scope. C is cosmetic.
> **Selected: A**

### Section 3 — Target User / Actor

**Q1: Who is the primary actor for this WF?**
- A) Researchers revising proposal snippets before submission.
- B) Internal maintainers tuning evaluation workflows.
- C) Admin users managing call definitions.
> Recommendation: A — the mission harm is that researchers cannot act on the review outputs. B is secondary. C is irrelevant to this failure.
> **Selected: A**

**Q2: Which user segment should define the scope boundary?**
- A) Anyone receiving a review in the locked NWO/ERC/MSCA wedge.
- B) Only one call family where failures looked strongest.
- C) Future broader agencies and programs.
> Recommendation: A — WF-0068 already proved repetition across the locked wedge, so the remediation WF should stay there without broadening further.
> **Selected: A**

**Q3: What current user behavior is failing?**
- A) Users cannot trust source basis labels.
- B) Users cannot decide what concrete revision to do first from the review output.
- C) Users cannot upload their snippets.
> Recommendation: B — that is the precise user-visible harm for this WF. A was covered by WF-0067. C is unrelated.
> **Selected: B**

**Q4: What secondary actor matters for acceptance?**
- A) Maintainers who need deterministic proof the actionability seam is remediated.
- B) Marketing stakeholders who need broader positioning proof.
- C) Operators who need rollout telemetry.
> Recommendation: A — they own the fail-closed evidence gate. B and C would widen scope.
> **Selected: A**

**Q5: What actor should this WF explicitly not optimize for?**
- A) Internal scoring convenience if it conflicts with researcher usefulness.
- B) Researchers using the product inside the locked wedge.
- C) Maintainers reading deterministic evidence.
> Recommendation: A — maintainers matter, but not at the cost of failing the mission-facing user outcome.
> **Selected: A**

### Section 4 — Rough Idea Exploration

**Q1: What is the simplest credible remediation direction?**
- A) Tighten the engine-to-card contract so outputs can encode actionable, prioritized revision moves.
- B) Rewrite prompts broadly and hope the current contract is sufficient.
- C) Redesign the review-detail UI first.
> Recommendation: A — the strongest evidence points at thin engine/card semantics. B may help later but is not the best first move. C is downstream and unsupported as the primary fix.
> **Selected: A**

**Q2: How should prompt work be treated in this WF?**
- A) Deferred unless needed after contract/engine inspection.
- B) Treated as co-primary with engine changes from the start.
- C) Declared the sole remediation path.
> Recommendation: A — this keeps the WF evidence-led and narrow.
> **Selected: A**

**Q3: What should happen if the current contract cannot express priority ordering cleanly?**
- A) Introduce the smallest contract extension needed for truthful prioritized guidance.
- B) Keep the contract frozen and encode everything into free text.
- C) Drop prioritization from scope.
> Recommendation: A — free text alone is exactly the weak seam risk, and dropping prioritization would contradict WF-0068.
> **Selected: A**

**Q4: How should missing-context situations be handled during remediation?**
- A) Preserve fail-closed limits and avoid inventing advice unsupported by the snippet/context.
- B) Fill in plausible advice heuristically so outputs feel more helpful.
- C) Ignore missing-context conditions for actionability stress cases.
> Recommendation: A — the product must stay defensible; helpful-sounding fabrication would be a regression.
> **Selected: A**

**Q5: What adjacent surface is acceptable only if strictly necessary?**
- A) A minimal downstream contract/render touch to expose truthful actionability semantics.
- B) Full review-detail redesign.
- C) Ops and telemetry instrumentation.
> Recommendation: A — only if the backend remediation cannot otherwise reach the user truthfully.
> **Selected: A**

### Section 5 — Constraints

**Q1: What is the dominant scope constraint?**
- A) Stay bounded to the WF-0068 `actionability_cluster` inside NWO/ERC/MSCA.
- B) Improve as many review-quality issues as possible while touching the same area.
- C) Use this WF to clean up all adjacent backlog items.
> Recommendation: A — this is the core scope lock.
> **Selected: A**

**Q2: What verification constraint should shape implementation planning?**
- A) Reuse named WF-0068 stress evidence as the primary closure gate.
- B) Create a new broad evaluation framework.
- C) Rely on manual subjective review only.
> Recommendation: A — it is the narrowest and most traceable path.
> **Selected: A**

**Q3: What engineering constraint should apply to behavior changes?**
- A) TDD with a failing repro first, then the minimal fix.
- B) Direct implementation first, tests later.
- C) Docs-only planning with no tests because the evidence already exists.
> Recommendation: A — AGENTS explicitly requires TDD for behavior changes.
> **Selected: A**

**Q4: What product areas must stay out of scope even if nearby?**
- A) Trust-surface polish, broader ops, call expansion, assisted extraction.
- B) Only UI changes.
- C) Nothing; adjacent fixes can come along if convenient.
> Recommendation: A — this is the explicit scope wall from the user request and prior WFs.
> **Selected: A**

**Q5: What should happen if remediation appears to require more than a narrow seam cluster?**
- A) Stop and rescope rather than silently widening the WF.
- B) Continue if the broader work seems valuable.
- C) Split scope later during implementation if it gets messy.
> Recommendation: A — fail closed early instead of accumulating mixed scope debt.
> **Selected: A**

### Section 6 — Risks / Unknowns

**Q1: What is the most fragile assumption right now?**
- A) That the dominant failure is in engine/output-contract seams rather than prompt wording.
- B) That NWO/ERC/MSCA is still the active wedge.
- C) That WF-0068 actually failed.
> Recommendation: A — B and C are already decided and evidenced.
> **Selected: A**

**Q2: What could cause the most misleading false success?**
- A) Outputs become longer or nicer-sounding without becoming more decision-useful.
- B) Tests run faster.
- C) The branch stays small.
> Recommendation: A — verbosity masquerading as usefulness is the main risk here.
> **Selected: A**

**Q3: What dependency risk should stay explicit?**
- A) A narrow need for adjacent traceability/context semantics might surface during remediation.
- B) Full launch-floor ops work might be needed after all.
- C) Broader call coverage may need reopening.
> Recommendation: A — it is plausible and should be handled explicitly if it appears. B and C contradict current scope.
> **Selected: A**

**Q4: What safety rule should apply if evidence stays ambiguous during implementation planning?**
- A) Keep unsupported judgments as insufficient evidence and do not fabricate actionability.
- B) Choose the most plausible explanation and proceed.
- C) Broaden the WF until something looks like a solution.
> Recommendation: A — fail-closed behavior is required.
> **Selected: A**

**Q5: What risk should Part B audit be expected to challenge hardest?**
- A) Hidden prompt/general-quality scope creep.
- B) Whether the WF title sounds strong enough.
- C) Whether more docs should be rewritten.
> Recommendation: A — that is the most likely way this brainstorm could drift.
> **Selected: A**

### Section 7 — MVP Definition

**Q1: What is the smallest functional slice?**
- A) Fix the output path so the three WF-0068 actionability stress cases pass on actionability/prioritization.
- B) Rework all review-quality dimensions across the representative batch.
- C) Ship a broader review UX refresh.
> Recommendation: A — smallest slice that directly closes the proven failure.
> **Selected: A**

**Q2: What verification scope should MVP require beyond those three stress cases?**
- A) Narrow regression checks on representative baseline/fail-closed behavior only.
- B) Full wedge-wide launch proof.
- C) No regression checks at all.
> Recommendation: A — enough to avoid regressions without widening into a new launch gate.
> **Selected: A**

**Q3: What output change should MVP preserve explicitly?**
- A) Truthful fail-closed handling when the system lacks enough context to make defensible advice.
- B) None; helpfulness should override strictness.
- C) Only UI readability.
> Recommendation: A — the product’s trust standard still applies.
> **Selected: A**

**Q4: What should MVP exclude even if tempting?**
- A) New calls, broader polish, dashboards, generic prompt tuning.
- B) Backend tests.
- C) Review-output changes.
> Recommendation: A — these are explicit non-goals. B and C would break the WF.
> **Selected: A**

**Q5: What should count as closure language for MVP?**
- A) “The bounded actionability/prioritization failure is remediated on the proven stress cases.”
- B) “Review quality is now solved.”
- C) “PeerLens is launch-ready.”
> Recommendation: A — precise, defensible, and scope-safe.
> **Selected: A**

### Section 8 — Explicit Non-Goals

**Q1: Which adjacent initiative should remain explicitly excluded?**
- A) Launch-floor ops and broader launch-readiness proof.
- B) No adjacent initiative at all.
- C) Only telemetry work.
> Recommendation: A — this was explicitly excluded in the user request.
> **Selected: A**

**Q2: How should broader prompt work be classified?**
- A) Out of scope unless reduced to the exact actionability remediation seam.
- B) In scope because prompt quality is always relevant.
- C) Deferred but silently allowed if implementation touches prompts.
> Recommendation: A — this prevents “prompt tuning” scope creep while leaving room for a truly necessary narrow change.
> **Selected: A**

**Q3: How should broader product expansion be treated?**
- A) Explicit non-goal; do not reopen broader call coverage or new user segments.
- B) Keep it loosely deferred in case this WF goes well.
- C) Bundle a small expansion since the same area is being touched.
> Recommendation: A — WF-0066 already locked the wedge.
> **Selected: A**

**Q4: How should trust-surface work be handled?**
- A) Out of scope except for the minimum downstream exposure needed to preserve truthful actionability semantics.
- B) Reopened because actionability is user-visible.
- C) Folded in if frontend files must change anyway.
> Recommendation: A — WF-0067 already closed the trust-surface WF, and this one should only touch it if strictly necessary.
> **Selected: A**

**Q5: What should this WF explicitly not become?**
- A) A new generic review-quality or evaluation-loop initiative.
- B) A narrow remediation WF.
- C) A follow-on to WF-0068.
> Recommendation: A — this WF exists to convert a proven failure boundary into a remediation slice, not to restart evaluation planning.
> **Selected: A**
