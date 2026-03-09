<!-- docs/brainstorms/brainstorm-WF-0068-review-quality-evaluation-loop.md -->
# WF-0068 — Review Quality Evaluation Loop

Artifact: brainstorm
Version: v0.4
Status: Draft Complete
Last Updated: 2026-03-08

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for WF-0068 scope and contract decisions.
- The Q&A transcript is rationale only; it must not introduce new evaluation contracts or scope.
- If later planning adds an evaluation rule, pass/fail threshold, or evidence requirement, promote it here and log it in `docs/logs/decisions.md`.

## Repo Reality Snapshot (Read-Only)

- `docs/mission.md` promises criteria-grounded, traceable, actionable feedback, but current live proof mostly covers contract correctness and trust-surface honesty rather than usefulness-of-feedback.
- WF-0066 correctly narrowed launch readiness to truthful usefulness inside the locked NWO/ERC/MSCA wedge, but it did not define a usefulness evaluation method.
- WF-0067 closed researcher-facing trust surfaces on review detail and explicitly did not treat model or feedback quality as solved.
- `docs/parking_lot.md` still contains a broad `Prompt quality tuning` item, which is too vague to serve as mission-grade evidence and risks jumping straight to fixes without a failure model.
- I do not see a deterministic review-quality evaluation loop artifact yet: no mission-anchored scoring framework, no locked snippet-set strategy, no reviewer procedure, and no evidence schema for recording failure patterns.

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 1)

PeerLens can now present reviews that are narrower and more honest, but it is still unproven whether those reviews actually help a researcher improve a real proposal snippet.

The remaining mission risk is fake readiness:
- feedback may be criteria-labeled but still generic
- feedback may sound concrete while overstating what the snippet or call materials support
- feedback may cite official structure weakly enough that a researcher still cannot trust the advice
- feedback may identify issues but fail to prioritize or suggest a usable revision move

This WF exists to decide, with evidence, whether PeerLens currently delivers mission-credible review quality for the locked representative wedge:
- `nwo_veni_2025_preproposal`
- `erc_stg_2026_full`
- `MSCA-PF-2025`

Contract Notes / Non-obvious constraints:
- This is an evaluation WF, not a prompt-tuning WF and not a generic QA program.
- The primary unit of proof is the `snippet -> review output` pair, scored at card level; review-level synthesis is secondary and exists only to judge prioritization quality across the same snippet.
- The decision target is whether feedback quality is mission-credible enough to justify follow-on implementation work, not whether the product is fully launch-ready.

## 2. Desired Outcome

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 2)

After this WF:
- PeerLens has a deterministic, repeatable review-quality evaluation loop for the locked representative set.
- The loop scores feedback against mission-anchored dimensions:
  - criteria-groundedness
  - traceability to official call materials
  - actionability for revision
  - specificity without false specificity
  - prioritization quality
- The loop records failures using a fixed taxonomy:
  - genericity
  - false specificity
  - weak traceability
  - bad prioritization
  - low actionability
  - criteria/element mismatch
- The output of this WF is an evidence-backed answer to: "what is broken, how often, and what exact follow-on implementation WF should exist, if any?"

Contract Notes / Non-obvious constraints:
- Success is a credible evaluation procedure and evidence format, not a list of speculative fixes.
- The result must be strong enough that a later implementation WF can be narrowly scoped from actual failure evidence.
- A clean result may still conclude that only a subset of quality defects is worth fixing next.

## 3. Target User / Actor

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 3)

Primary actors:
- repo owner deciding whether PeerLens review quality is mission-credible within the locked wedge
- maintainers who need a non-hand-wavy way to judge real review usefulness before more product work

Indirect beneficiary:
- the researcher, because this WF determines whether the current product can make defensible revision suggestions on real snippets

Current harmful behavior:
- a polished, traceable UI can be mistaken for useful feedback quality
- broad "prompt quality" language invites undisciplined tuning without proving what is failing
- future planning could optimize the wrong thing if failure evidence is not structured

Contract Notes / Non-obvious constraints:
- This WF optimizes for product-truthfulness and planning quality first, not end-user UI polish.
- Human review is allowed and required; trying to automate judgment away would weaken the evidence.

## 4. Rough Idea (Unstructured Thinking)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 4)

Use a narrow, deterministic manual evaluation loop on representative real snippets, with evidence captured in a fixed template and follow-on work explicitly deferred.

Preferred direction:
- define a mission-anchored scoring framework before looking for fixes
- sample a small, representative, and failure-seeking snippet set across the locked three-call wedge; Phase 1 must explicitly prevent convenience sampling and cherry-picked "easy" examples
- evaluate outputs using a fixed human-review procedure with stable ordering and a frozen evaluation baseline:
  - same app commit / branch baseline
  - same prompt + model/runtime configuration for the evaluated batch
  - same reviewer instructions and evidence template
- record findings in a structured evidence format that separates:
  - representative call + snippet identifier
  - observed output
  - criterion/element mapping
  - official source basis used to judge it, including the exact call-material locator used by the reviewer
  - failure taxonomy tags
  - severity and suggested follow-on class
  - revision-action judgment and rationale
- require explicit recording of any insufficient-evidence case rather than omitting it from the batch
- end this WF with a bounded recommendation:
  - no follow-on WF needed,
  - one narrow implementation WF,
  - or more evidence required

Contract Notes / Non-obvious constraints:
- This WF must not bundle remediation.
- The evaluation loop should be small enough to run repeatedly, but not so small that it overfits one polished example.
- Determinism here means stable procedure and evidence recording, not exact textual output equality from the model.
- If the frozen evaluation baseline changes mid-run, the batch is no longer comparable and should be restarted or split explicitly.
- Phase 1 must make the snippet-selection rationale auditable per included item so later phases can prove the batch was representative and failure-seeking rather than convenience-sampled.

## 5. Constraints

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 5)

- Scope stays inside the locked wedge: `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, `MSCA-PF-2025`.
- Do not reopen scope expansion, trust-surface polish, generic platform work, or extraction work unless a real blocker is proven.
- This WF evaluates usefulness-of-feedback only; it does not solve bookkeeping, contracts, or call-authoring gaps unless they directly block the evaluation procedure.
- Evidence must stay grounded in official call materials already accepted in the repo; do not invent external scoring standards.
- The procedure must be repeatable by a future maintainer without relying on private intuition.
- Keep later implementation boundaries explicit: evaluation artifacts may recommend a follow-on WF, but may not silently contain implementation scope.
- If any representative call lacks enough approved snippet material to support the planned proof set, Phase 1 must treat that as a snippet-set planning gap inside this WF rather than widening to extra calls.
- No proceed recommendation is valid without an explicit verification evidence bundle captured in the WF artifacts; missing evidence must resolve to `do not proceed` or `more evidence required`, never an optimistic pass.

Contract Notes / Non-obvious constraints:
- The evaluation framework must anchor to `docs/mission.md` language, not an ad hoc "rubric."
- The procedure must fail closed when a judgment cannot be supported by official call materials or the snippet context.
- A weakness found in one call cannot automatically justify a cross-product fix unless the evidence format shows the pattern repeats.

## 6. Risks / Unknowns

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 6)

- The WF could collapse into vague prompt-tuning language if the scoring framework is not explicit enough.
- A tiny sample can produce false confidence if it includes only "easy" snippets.
- Reviewers may over-credit polished wording unless the procedure forces traceability and revision-action checks.
- Different failure types may get conflated unless the taxonomy distinguishes genericity, false specificity, weak traceability, bad prioritization, low actionability, and criteria/element mismatch.
- If the evidence format does not separate evaluation findings from proposed fixes, the follow-on WF boundary will blur.

Contract Notes / Non-obvious constraints:
- Human judgment variance is acceptable only if the procedure and evidence fields constrain it tightly.
- This WF should prefer "insufficient evidence" over premature pass claims.
- The strongest fake-readiness pattern to avoid is declaring quality "good enough" from one convincing demo output.

## Open Questions / Deferred

- Part C decision: Phase 1 locks one shared 4-state scale for each mission dimension: `pass`, `weak`, `fail`, `insufficient_evidence`.
- Part C decision: Phase 1 locks a minimum representative batch of 9 snippets total: exactly 3 snippets per locked call, with one `baseline representative`, one `traceability/specificity stress`, and one `actionability/prioritization stress` snippet per call.
- Part C decision: Phase 1 locks per-item evidence severity to `high`, `medium`, or `low`; this item-level severity describes mission impact for that reviewed pair only and does not replace the batch-level `mission_result`.
- Part C decision: Phase 1 locks proceed recommendations to repeated categorized failure patterns appearing in at least 2 reviewed snippets; if repetition appears only within 1 locked call, any recommended follow-on boundary must be labeled call-specific rather than cross-wedge.
- Part C decision: Phase 1 requires the frozen evaluation baseline to record both app commit SHA and app branch ref, and requires each evidence record to cite a replayable official-call locator rather than a derived label alone.
- Whether a second reviewer pass is required for disagreement cases is deferred to Phase 2 task planning.
- Any prompt, engine, UI, or contract changes suggested by the evidence are explicitly deferred to a follow-on implementation WF.
- Any broader continuous quality-monitoring system is deferred and out of scope.

## 7. MVP Definition

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 7)

Smallest successful slice:
- one WF that defines the review-quality evaluation loop for the locked three-call representative wedge
- an evaluation framework anchored to `docs/mission.md`
- a representative snippet-set strategy
- a deterministic human review procedure
- a fixed failure taxonomy
- a standard evidence record format
- explicit pass/fail or proceed/do-not-proceed logic for any follow-on implementation WF

Minimum acceptable proof:
- enough evaluated snippets to expose whether failures are isolated or patterned
- evidence records that show exact findings and their official-call traceability basis
- one frozen evaluation baseline per evidence batch, captured explicitly so later comparisons are not hand-wavy
- a pass/fail summary that cites the verification evidence bundle used to support the conclusion
- a conclusion that names the next narrow move, if any, without jumping into fixes here

Explicitly excluded:
- implementing prompt or engine changes
- changing UI trust surfaces
- broad automated evaluation infrastructure
- new call onboarding
- product-wide launch claims beyond the locked wedge and evaluated snippet set

Contract Notes / Non-obvious constraints:
- The evaluation must focus on snippet usefulness, not whole-proposal completeness.
- The evidence format must preserve raw observed output plus structured judgment, so later fix WFs can trace back to concrete failures.
- This WF is complete only when the boundary between evaluation and remediation is explicit enough to prevent a disguised implementation phase.
- The verification evidence bundle for any proceed/do-not-proceed recommendation must include, at minimum: representative snippet coverage across the locked calls, the frozen evaluation baseline, completed evidence records for all reviewed items including insufficient-evidence cases, and an explicit pass/fail rationale tied to those records.
- Part C decision: the evaluation summary must separate `mission result` from `follow-on decision`, and any follow-on boundary must be phrased as a repeated failure pattern rather than a pre-chosen solution type.

## 8. Explicit Non-Goals

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0068-review-quality-evaluation-loop.md` (Section 8)

- No prompt tuning, model swaps, or engine rewrites in this WF.
- No new trust-surface or UX polish work unless the evaluation procedure itself is blocked without it.
- No expansion beyond the locked NWO/ERC/MSCA representative wedge.
- No generic "AI quality" program or production monitoring system.
- No launch recommendation based on aesthetics, contract correctness, or one-off demos alone.

Contract Notes / Non-obvious constraints:
- If an issue can be described only as "the output feels weak," the evidence design is not tight enough yet.
- If a proposed next step cannot point to repeated evidence records, it should not become the next implementation WF.
