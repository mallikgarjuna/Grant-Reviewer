<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md -->
# WF-0068 — Review Quality Evaluation Loop

Artifact: brainstorm-qna
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

## Section 1 — Problem Statement

**Q1: What is the primary decision this WF must enable?**
- A) Decide whether PeerLens feedback is mission-credible for the locked wedge before more feature work.
- B) Find a few obvious prompt tweaks to improve examples quickly.
- C) Build a broader quality-monitoring system for future scale.
> Recommendation: A — this keeps the WF on the real mission risk. B jumps to fixes before evidence. C is broader infrastructure and would hide the core product question.
> **Selected: A**

**Q2: What should count as the core unit of evaluation?**
- A) Individual review cards against one proposal snippet at a time.
- B) Entire completed reviews only.
- C) Whole user sessions including submit UX and navigation.
> Recommendation: A — it is the smallest unit that still exposes usefulness defects precisely. B is too coarse for failure attribution. C reopens solved or out-of-scope UX surfaces.
> **Selected: A**

**Q3: What is the narrowest acceptable proof scope for this WF?**
- A) The locked 3-call representative set only: `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, `MSCA-PF-2025`.
- B) Start with one call only, expand later if it looks bad.
- C) Include any extra calls/examples already in the repo.
> Recommendation: A — it matches the locked wedge and avoids both under-proof and silent scope growth. B is too weak to support a wedge-level claim. C invites drift and inconsistent evidence.
> **Selected: A**

**Q4: What should this WF produce before any implementation follow-on is allowed?**
- A) A deterministic evaluation loop: scoring framework, snippet strategy, procedure, failure taxonomy, and evidence format.
- B) A prioritized list of suspected prompt/code fixes.
- C) A manual reviewer guide only.
> Recommendation: A — it gives a real gate for later work. B assumes the answer before evaluation. C lacks enough structure to constrain later planning.
> **Selected: A**

**Q5: What is the main anti-goal for this WF?**
- A) Avoid turning evaluation into another prompt-tuning or feature WF before failure evidence exists.
- B) Avoid any human judgment at all; rely only on automated checks.
- C) Avoid using the representative proof set if edge cases are hard.
> Recommendation: A — that is the main fake-readiness trap. B would force weak proxies for usefulness. C would evade the very proof set the wedge is anchored to.
> **Selected: A**

## Section 2 — Desired Outcome

**Q1: What outcome matters most at the end of this WF?**
- A) A credible answer to whether current feedback is useful enough to justify a targeted next implementation WF.
- B) A polished quality dashboard prototype.
- C) A repo-wide list of all possible quality concerns.
> Recommendation: A — the WF should end with a decision backed by evidence. B is tooling drift. C is too broad and non-prioritized.
> **Selected: A**

**Q2: Which success dimensions should be locked now?**
- A) Criteria-groundedness, official-call traceability, actionability, specificity without bluffing, and prioritization quality.
- B) Only actionability and tone.
- C) Whatever dimensions seem relevant per call.
> Recommendation: A — it mirrors the mission and the user’s explicit quality concerns. B is incomplete. C would make results incomparable.
> **Selected: A**

**Q3: How should failure evidence be used?**
- A) To bound any follow-on WF to repeated, categorized failures only.
- B) To inspire general prompt improvement ideas.
- C) To rank model vendors.
> Recommendation: A — it keeps the next move narrow and evidence-driven. B is too loose. C is outside the repo’s current product question.
> **Selected: A**

**Q4: What should a “pass” mean for this WF?**
- A) The evaluation loop is credible and the evidence supports a clear proceed / do-not-proceed conclusion for follow-on work.
- B) Most examples feel decent on first read.
- C) The outputs mention evaluation criteria consistently.
> Recommendation: A — the WF is about decision-quality, not vibes or one dimension alone. B is too subjective. C is necessary but far from sufficient.
> **Selected: A**

**Q5: What should a “fail” mean for this WF?**
- A) The procedure cannot distinguish good from bad output reliably enough to support a follow-on decision.
- B) A few examples look awkward.
- C) Reviewers disagree occasionally.
> Recommendation: A — procedure failure is the real blocker. B may reflect isolated defects. C can happen even in a valid evaluation system.
> **Selected: A**

## Section 3 — Target User / Actor

**Q1: Who is the primary actor for this workflow?**
- A) The repo owner / release decider judging whether PeerLens review quality is mission-credible inside the locked wedge.
- B) End researchers directly using a new UI in this WF.
- C) Admin/operators building a monitoring program.
> Recommendation: A — this WF is planning and evidence work. B is the eventual beneficiary but not the direct workflow actor. C is outside scope.
> **Selected: A**

**Q2: Who is the secondary actor?**
- A) Future maintainers who need repeatable evidence before making fixes.
- B) Marketing copy writers.
- C) New call-authors expanding coverage.
> Recommendation: A — they will reuse the loop and evidence. B and C are unrelated to the narrow mission-risk question.
> **Selected: A**

**Q3: What current harmful behavior should this WF stop?**
- A) Mistaking polished, traceable UI for genuinely useful feedback quality.
- B) Assuming all calls need identical snippet structures.
- C) Requiring too much manual setup for local dev.
> Recommendation: A — this is the exact fake-readiness pattern now. B is tangential. C is tooling noise here.
> **Selected: A**

**Q4: What kind of judgment is acceptable in this WF?**
- A) Structured human judgment constrained by official call materials and a fixed procedure.
- B) Purely automated scoring.
- C) Free-form expert impressions.
> Recommendation: A — usefulness requires human judgment, but it must be constrained. B is too weak for nuance. C is too loose to be repeatable.
> **Selected: A**

**Q5: What audience should the evidence format optimize for?**
- A) Maintainers deciding the next narrow implementation step.
- B) Public-facing launch communication.
- C) Generic research on LLM evaluation.
> Recommendation: A — the evidence should drive the next WF cleanly. B is premature. C is not the repo objective.
> **Selected: A**

## Section 4 — Rough Idea Exploration

**Q1: What is the simplest implementation direction for this WF itself?**
- A) Manual evaluation loop with fixed templates and deterministic procedure over a small representative snippet set.
- B) Build automated scoring infra first.
- C) Run informal ad hoc spot checks and summarize them in prose.
> Recommendation: A — it is the smallest credible approach. B is too large for Phase 0. C will not survive adversarial planning review.
> **Selected: A**

**Q2: How should snippet selection be framed?**
- A) Representative and failure-seeking, not convenience-sampled or cherry-picked.
- B) Use the easiest snippets first to stabilize the process.
- C) Let reviewers choose any examples that look interesting.
> Recommendation: A — the loop should expose mission risk, not flatter the product. B and C both invite false confidence.
> **Selected: A**

**Q3: What should be recorded per evidence item?**
- A) Snippet context, observed output, mapped criterion/element, official source basis, failure tags, severity, and revision-action judgment.
- B) Only a score and short comment.
- C) Only raw model output plus a pass/fail.
> Recommendation: A — it gives enough traceability to justify a later WF. B and C are too thin to explain what failed.
> **Selected: A**

**Q4: How should determinism be interpreted?**
- A) Stable procedure, stable evidence schema, and stable review order; not exact text equality.
- B) Exact output matching across reruns.
- C) Reviewer intuition should be enough even without explicit order.
> Recommendation: A — LLM output quality cannot be judged with brittle equality, but the procedure itself must be stable. B is unrealistic. C is too loose.
> **Selected: A**

**Q5: What should happen after the loop identifies failures?**
- A) The WF should recommend one narrow follow-on implementation boundary, or no follow-on if evidence is insufficient.
- B) Start fixing the highest-scoring issues immediately in the same WF.
- C) Add all observed weaknesses to the parking lot without synthesis.
> Recommendation: A — it preserves WF boundary hygiene. B mixes evaluation and remediation. C loses prioritization and decision quality.
> **Selected: A**

## Section 5 — Constraints

**Q1: What scope boundary must remain hard?**
- A) Stay inside the locked NWO/ERC/MSCA wedge and the named three-call proof set.
- B) Expand if another call seems useful for contrast.
- C) Leave the call set open until Phase 1.
> Recommendation: A — the wedge is already locked. B and C would reopen scope by habit rather than need.
> **Selected: A**

**Q2: What source material can ground the evaluation judgments?**
- A) Official call materials already accepted in the repo for those representative calls.
- B) Reviewer intuition plus general grant-writing best practices.
- C) External benchmark rubrics from unrelated programs.
> Recommendation: A — it matches mission traceability and avoids imported standards. B is too subjective. C weakens SSOT discipline.
> **Selected: A**

**Q3: How should follow-on implementation be handled?**
- A) Explicitly deferred to a separate WF unless the evaluation procedure itself is blocked.
- B) Allowed if the fix looks tiny.
- C) Decided ad hoc while writing the PRD.
> Recommendation: A — otherwise this becomes a disguised implementation WF. B and C both erode the boundary.
> **Selected: A**

**Q4: What should happen when a judgment cannot be supported by call materials or snippet context?**
- A) Fail closed and record insufficient evidence rather than improvising.
- B) Let the reviewer use best judgment and continue.
- C) Drop the case silently.
> Recommendation: A — this keeps the loop honest. B invents confidence. C hides ambiguity that should shape the procedure.
> **Selected: A**

**Q5: What wording discipline applies in researcher-facing framing inside this WF?**
- A) Use `evaluation criteria/elements`, not `rubric`.
- B) Either term is fine.
- C) Prefer broader generic AI-evaluation language.
> Recommendation: A — this follows repo terminology SSOT and avoids drift. B and C violate established language boundaries.
> **Selected: A**

## Section 6 — Risks / Unknowns

**Q1: What is the highest process risk in this WF?**
- A) It degrades into vague prompt-tuning talk without a concrete failure model.
- B) It produces too many screenshots.
- C) It takes slightly longer to run than expected.
> Recommendation: A — that is the main failure mode already visible in the backlog wording. B and C are secondary at most.
> **Selected: A**

**Q2: What sampling risk matters most?**
- A) Convenience or cherry-picked snippets create false confidence.
- B) The snippets are too short to read quickly.
- C) Reviewers prefer one call family over another.
> Recommendation: A — sample bias would corrupt the whole conclusion. B and C matter less than representativeness.
> **Selected: A**

**Q3: What evidence-design risk matters most?**
- A) Failure tags are too vague to distinguish different defect classes.
- B) The template has too many markdown headings.
- C) The final summary is longer than one page.
> Recommendation: A — without precise categories, later fixes cannot stay narrow. B and C are stylistic.
> **Selected: A**

**Q4: What reviewer-behavior risk matters most?**
- A) Reviewers may reward confident wording even when traceability or actionability is weak.
- B) Reviewers may disagree on punctuation.
- C) Reviewers may read the snippets out of order.
> Recommendation: A — polished prose can mask mission failure. B and C are minor compared with false trust.
> **Selected: A**

**Q5: What conclusion risk must be blocked explicitly?**
- A) Declaring quality “good enough” from one convincing demo or low-volume sample.
- B) Recording too many low-severity observations.
- C) Reusing existing call names in the evidence sheet.
> Recommendation: A — this is the central fake-readiness pattern. B and C are not existential risks to the WF.
> **Selected: A**

## Section 7 — MVP Definition

**Q1: What is the smallest functional slice that still answers the mission-risk question?**
- A) Define and document the evaluation loop, snippet strategy, procedure, taxonomy, evidence format, and follow-on boundary for the three-call wedge.
- B) Run a few sample evaluations without formalizing the process.
- C) Prototype a future automated evaluator.
> Recommendation: A — it is the minimum that can survive reuse and audit. B is too loose. C is too broad.
> **Selected: A**

**Q2: What proof level is minimally acceptable?**
- A) Enough evaluated snippets to distinguish patterned failure from isolated defects, with structured evidence records.
- B) One example per call.
- C) One especially difficult example total.
> Recommendation: A — B and C are too thin to justify a next WF safely.
> **Selected: A**

**Q3: What should the evidence bundle include?**
- A) Raw observed output, structured judgments, failure tags, official-call basis, and a bounded conclusion.
- B) Only scores and aggregate averages.
- C) Only narrative summaries.
> Recommendation: A — later planning needs the concrete trace back to the observed outputs. B and C lose important context.
> **Selected: A**

**Q4: What explicit exclusion is essential to keep MVP honest?**
- A) No prompt or engine fixes in this WF.
- B) No human review.
- C) No use of official call materials.
> Recommendation: A — it preserves the evaluation/remediation boundary. B and C would break the WF’s purpose.
> **Selected: A**

**Q5: What should Phase 1 primarily do after this brainstorm?**
- A) Translate this into a PRD for the evaluation loop only, not a remediation plan.
- B) Start drafting implementation tasks for likely prompt fixes.
- C) Merge evaluation and implementation planning to save time.
> Recommendation: A — Phase 1 should operationalize the evaluation WF cleanly. B and C jump the boundary.
> **Selected: A**

## Section 8 — Explicit Non-Goals

**Q1: What kind of work is definitely out of scope here?**
- A) Prompt tuning, model changes, engine rewrites, and trust-surface polish unless the evaluation loop itself is blocked.
- B) Any use of real outputs.
- C) Any documentation work at all.
> Recommendation: A — it keeps the WF focused while allowing minimal blocker handling if truly necessary. B and C contradict the point of the workflow.
> **Selected: A**

**Q2: What broader product move should this WF avoid reopening?**
- A) Scope expansion beyond the locked NWO/ERC/MSCA wedge.
- B) Use of the current representative calls.
- C) Mission wording stability.
> Recommendation: A — WF-0066 already closed that decision. B and C are not the open risk.
> **Selected: A**

**Q3: What false signal should not be treated as success?**
- A) Aesthetic polish, criteria labels, or one strong demo without broader evidence.
- B) Detailed markdown formatting.
- C) Fast local test runs.
> Recommendation: A — this directly targets fake readiness. B and C are incidental.
> **Selected: A**

**Q4: What kind of evaluation program is intentionally excluded?**
- A) A generic long-term AI quality monitoring platform.
- B) Any structured evidence recording.
- C) Any deterministic procedure.
> Recommendation: A — this WF needs a bounded evaluation loop, not a platform. B and C are required, not excluded.
> **Selected: A**

**Q5: What should not happen even if the evidence reveals clear failures?**
- A) Silent expansion into implementation work without a separately named follow-on WF.
- B) Recording the failures in structured form.
- C) Recommending a next move.
> Recommendation: A — the whole purpose is to make the next move explicit and narrow, not to smuggle it into this WF.
> **Selected: A**
