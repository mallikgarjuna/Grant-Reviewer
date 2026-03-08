<!-- docs/prds/prd-WF-0068-review-quality-evaluation-loop.md -->
# WF-0068 — Review Quality Evaluation Loop

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-08

Type: feature

## 0. User Stories (MVP)

- US1: As the repo owner deciding whether PeerLens is mission-credible in the locked wedge, I want a mission-anchored evaluation framework for `snippet -> review output` pairs, so that usefulness is judged against the actual product promise instead of vague quality impressions.
- US2: As a maintainer running a quality pass, I want a representative, failure-seeking snippet-set strategy across `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`, so that evidence cannot be built from convenience-sampled easy examples.
- US3: As a maintainer executing the evaluation, I want a deterministic review procedure with a frozen baseline, fixed failure taxonomy, and standard evidence record, so that different batches stay comparable and failures can be traced to official call materials.
- US4: As a maintainer deciding the next WF, I want explicit pass/fail and follow-on-WF boundaries, so that this workflow ends with a bounded proceed, do-not-proceed, or more-evidence-required decision rather than hidden remediation scope.

## Deferred Stories (Not in MVP)

- DS1: As a maintainer, I want to tune prompts, swap models, or change engine logic based on WF-0068 findings.
- DS2: As a researcher, I want UI trust-surface or review-detail presentation changes driven by WF-0068 findings.
- DS3: As an operator, I want automated continuous quality monitoring, scoring dashboards, or production alerting for review quality.
- DS4: As a planner, I want to expand proof scope beyond the locked representative wedge.

## 1. In Scope

- Define a mission-anchored evaluation framework derived from `docs/mission.md`, especially grounding in official call requirements, alignment to evaluation criteria/elements, traceability, and revision usefulness. (US1)
- Define a representative snippet-set strategy that is small, auditable, failure-seeking, and locked to exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`. (US2)
- Define one deterministic manual review procedure for evidence batches, including frozen evaluation baseline requirements, fixed review order, fail-closed insufficient-evidence handling, and stable reviewer instructions. (US3)
- Define one fixed failure taxonomy and severity model for classifying observed review-quality defects. (US3)
- Define one standard evidence record format that captures raw observed output, official-call traceability basis, structured judgments, and follow-on class. (US3, US4)
- Define one explicit pass/fail decision rule and boundary for any follow-on WF, including when the correct outcome is `do not proceed` or `more evidence required`. (US4)

## 2. Out of Scope

- Prompt tuning, prompt rewrites, model swaps, engine fixes, pipeline changes, or other remediation work. (DS1)
- UI trust-surface changes, review-detail redesign, or researcher-facing copy changes not required to describe the evaluation method itself. (DS2)
- Broad QA or monitoring infrastructure, score dashboards, or automated evaluators. (DS3)
- Adding calls beyond `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`, or weakening the locked wedge by collapsing to fewer calls. (DS4)
- Launch-readiness claims for the full product beyond the evaluated snippet set inside the locked wedge. (DS4)

## 3. User / System Flow

### Happy path

1. The maintainer selects the locked representative calls and assembles a predeclared snippet batch using the PRD’s snippet-set strategy, including per-snippet rationale showing why each item is representative and failure-seeking. (US2)
2. Before reviewing outputs, the maintainer freezes one evaluation baseline for the batch: app commit, prompt/model-runtime configuration, reviewer instructions, and evidence template version. (US3)
3. For each `snippet -> review output` pair in the fixed order, the maintainer judges the output against the mission-anchored framework using only official call materials already accepted in the repo plus the snippet context. (US1, US3)
4. The maintainer records one evidence record per reviewed item, including official-call locators, dimension judgments, taxonomy tags, severity, revision-action judgment, and any insufficient-evidence state. (US1, US3)
5. After the full batch is recorded, the maintainer summarizes batch-level pass/fail outcomes using the named verification evidence bundle and determines whether the correct next state is `proceed to one narrow follow-on WF`, `do not proceed`, or `more evidence required`. (US4)

### Failure path A — convenience sampling or wedge drift

1. The planned snippet set omits one of the locked calls, overuses polished examples, or lacks auditable selection rationale. (US2)
2. The batch cannot support a trustworthy wedge-level conclusion because representativeness is unproven. (US2, US4)
3. The run must fail closed as `more evidence required`; no follow-on implementation WF may be recommended from that batch. (US2, US4)

### Failure path B — non-deterministic review batch

1. The evaluated outputs come from mixed commits, mixed prompt/model-runtime configurations, or changed reviewer instructions/template mid-batch. (US3)
2. Evidence items are no longer comparable as one batch. (US3)
3. The run must be restarted or explicitly split into separate batches; no aggregate pass claim is valid for the mixed batch. (US3, US4)

### Failure path C — unsupported judgment or disguised remediation

1. A reviewer cannot justify a judgment from official call materials or snippet context, or the evidence summary jumps straight to prompt/engine/UI fixes. (US1, US3, US4)
2. The workflow loses mission traceability or crosses into implementation planning without proof. (US1, US4)
3. The item must be recorded as `insufficient evidence` or as a bounded follow-on class only; this WF cannot prescribe remediation details. (US3, US4)

## 4. Functional Requirements

- FR1 (US1): The evaluation framework must anchor every quality judgment to `docs/mission.md` language: grounded in official call requirements, aligned to evaluation criteria/elements, traceable enough to trust, and actionable enough to support real revision decisions.
- FR2 (US1): The primary proof object must be the `snippet -> review output` pair; review-level synthesis is allowed only for prioritization judgment across the same snippet.
- FR3 (US1, US3): The framework must define exactly five scored quality dimensions for each reviewed item: criteria-groundedness, official-call traceability, actionability for revision, specificity without false specificity, and prioritization quality.
- FR4 (US1, US3): The framework must require fail-closed handling when the reviewer cannot support a judgment from accepted official call materials or snippet context; unsupported judgments must be recorded as insufficient evidence, not inferred.
- FR5 (US2): The snippet-set strategy must stay locked to exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- FR6 (US2): The snippet-set strategy must ban convenience sampling and cherry-picked easy examples, and it must require auditable per-snippet inclusion rationale.
- FR7 (US2): The snippet-set strategy must require a minimum batch of 9 snippets total: exactly 3 snippets per locked call, with one `baseline representative` item, one `traceability/specificity stress` item, and one `actionability/prioritization stress` item per call.
- FR8 (US3): The review procedure must freeze one evaluation baseline per batch, including app commit/branch reference, prompt/model-runtime configuration, reviewer instructions, and evidence template version.
- FR9 (US3): The review procedure must define one stable item order and require that all items in a batch are evaluated with the same procedure before any aggregate conclusion is drawn.
- FR10 (US3): The review procedure must require the reviewer to cite the exact official-call locator used for each material judgment in the evidence record.
- FR11 (US3): The failure taxonomy must use one fixed tag set for this WF: `genericity`, `false_specificity`, `weak_traceability`, `bad_prioritization`, `low_actionability`, and `criteria_element_mismatch`.
- FR12 (US3): The evidence format must preserve both raw observed output and structured judgment so later follow-on work can trace failures back to the exact reviewed item.
- FR13 (US3): Every reviewed item must record severity and one bounded follow-on pattern class chosen from `none`, `evidence_gap`, `genericity_cluster`, `false_specificity_cluster`, `traceability_cluster`, `prioritization_cluster`, `actionability_cluster`, `criteria_element_alignment_cluster`, or `mixed_cluster`, without prescribing implementation details.
- FR14 (US4): The WF must define one named verification evidence bundle for any mission result or follow-on decision, containing at minimum representative snippet coverage across the locked calls, the frozen baseline, completed evidence records for all items including insufficient-evidence cases, and an explicit rationale tied to those records.
- FR15 (US4): The batch summary must separate `mission_result` from `follow_on_decision` so a completed batch can distinguish `pass/no follow-on`, `fail/proceed to one narrow follow-on WF`, and `inconclusive/more evidence required`.
- FR16 (US4): No proceed recommendation is valid unless the verification evidence bundle exists and shows one repeated, categorized failure pattern across at least 2 reviewed snippets; if the pattern appears in only 1 locked call, the recommended follow-on boundary must state that it is call-specific and must not make a cross-wedge claim. Otherwise the allowed follow-on outcomes are `no_follow_on_wf` or `more_evidence_required`.
- FR17 (US4): This WF must explicitly prohibit bundling prompt tuning, engine fixes, UI fixes, or scope expansion into its own implementation scope or its pass criteria.

## 5. Data & API Contracts

### 5.1 Evaluation framework contract

- The per-item scoring object must include:
  - `criteria_groundedness`
  - `official_traceability`
  - `revision_actionability`
  - `specificity_without_false_specificity`
  - `prioritization_quality`
- Each dimension must use one shared 4-state ordinal scale for the whole WF so evidence records stay comparable:
  - `pass`
  - `weak`
  - `fail`
  - `insufficient_evidence` (US1, US3, FR1-FR4)
- The framework must include dimension definitions tied back to mission language, not a generic external scoring standard. (US1, FR1)

### 5.2 Representative snippet-set contract

- The snippet inventory for each batch must record:
  - `call_id`
  - `snippet_id`
  - `proposal_section`
  - `snippet_role`
  - `selection_rationale`
  - `risk_target`
  - `expected_official_materials`
  - `batch_order`
- `snippet_role` is limited to `baseline_representative`, `traceability_specificity_stress`, or `actionability_prioritization_stress`, with each role appearing exactly once per locked call in the minimum 9-snippet batch. (US2, FR7)
- `selection_rationale` must explain why the item is both representative of the locked wedge and failure-seeking enough to test mission risk. (US2, FR5-FR7)
- `risk_target` should capture the primary failure mode the snippet is intended to expose without pre-judging the output result. (US2, FR6)
- If a locked call cannot supply enough approved snippet material, the batch-plan state must record `coverage_gap` and block a proceed recommendation until resolved. (US2, US4, FR7, FR15)

### 5.3 Deterministic review procedure contract

- Every evidence batch must record one frozen baseline object with:
  - `baseline_id`
  - `app_commit_sha`
  - `prompt_config_ref`
  - `model_runtime_ref`
  - `reviewer_instruction_ref`
  - `evidence_template_version`
  - `batch_started_at`
- The procedure must require:
  - fixed item order,
  - one completed evidence record per item,
  - explicit insufficient-evidence handling,
  - explicit restart/split behavior if the baseline changes mid-batch. (US3, FR8-FR10, FR14)

### 5.4 Failure taxonomy and evidence record contract

- Every evidence record must include:
  - `call_id`
  - `snippet_id`
  - `proposal_section`
  - `review_output_ref` or embedded raw output excerpt/reference
  - `criterion_or_element_target`
  - `official_locator_used`
  - `dimension_scores`
  - `failure_tags`
  - `severity`
  - `revision_action_judgment`
  - `insufficient_evidence_reason`
  - `follow_on_pattern_class`
  - `reviewer_rationale`
- `failure_tags` must be multi-select from the fixed taxonomy only. (US3, FR11)
- `revision_action_judgment` must state whether a researcher could take a defensible next revision move from the output and why. (US1, US3, FR3, FR12)
- `official_locator_used` must be specific enough to replay the judgment later, for example section heading, criterion label, or canonical source hint locator already present in repo materials. (US1, US3, FR10, FR12)

### 5.5 Pass/fail and follow-on boundary contract

- The batch summary object must include:
  - `batch_id`
  - `verification_evidence_bundle_ref`
  - `coverage_status`
  - `baseline_consistency_status`
  - `pattern_summary`
  - `mission_result`
  - `follow_on_decision`
  - `decision_rationale`
  - `recommended_follow_on_boundary`
- `mission_result` is limited to:
  - `pass`
  - `fail`
  - `inconclusive`
- `follow_on_decision` is limited to:
  - `no_follow_on_wf`
  - `proceed_to_narrow_follow_on_wf`
  - `more_evidence_required`
- `recommended_follow_on_boundary` may only name a narrow failure pattern or tightly related cluster justified by repeated evidence records; otherwise it must be `none`. (US4, FR14-FR17)

## 6. Components / Modules

- `docs/prds/prd-WF-0068-review-quality-evaluation-loop.md`
  - Phase 1 contract artifact defining the evaluation framework, batch strategy, deterministic procedure, taxonomy, evidence schema, and follow-on boundary. (FR1-FR17)
- `docs/tasks/task-WF-0068-review-quality-evaluation-loop.md`
  - Phase 2 planning target that should decompose the evaluation loop into atomic execution tasks without crossing into remediation work. (FR5-FR17)
- `docs/walkthroughs/walkthrough-WF-0068-review-quality-evaluation-loop.md`
  - Later evidence handoff artifact for the actual evaluation run and conclusion bundle. (FR14-FR16)
- Representative source materials already accepted in repo for:
  - `nwo_veni_2025_preproposal`
  - `erc_stg_2026_full`
  - `MSCA-PF-2025`
  - These are the only allowed grounding sources for mission judgments in MVP. (FR1, FR4-FR7, FR10)

Design tree / dependencies / ordering:
1. Lock the mission-anchored quality dimensions and the primary proof object before deciding any batch mechanics. (FR1-FR4)
2. Lock the representative snippet-set strategy for the three-call wedge before defining run logistics, so batch execution cannot backfill sampling logic later. (FR5-FR7)
3. Lock one deterministic batch procedure and evidence schema before any later execution planning. (FR8-FR14)
4. Lock pass/fail and follow-on boundaries only after the evidence bundle contract is explicit enough to fail closed. (FR14-FR17)

Deep module guidance:

- Keep the evidence loop human-reviewed and deterministic; do not add automation whose real effect is to hide judgment calls.
- Keep follow-on classes as planning labels, not remediation plans.
- Keep official grounding local to accepted repo call materials; do not import external benchmarks.
- Keep wedge coverage explicit; silence about one locked call counts as missing proof, not as flexibility.

Suggested file-path clusters (coarse only):

- planning artifacts under `docs/prds/`, `docs/tasks/`, and `docs/walkthroughs/`
- accepted official call materials already present under repo data/reference paths for the locked wedge
- optional future evidence templates or logs under `docs/` only if Phase 2 deems them necessary

## 7. Edge Cases

- A locked call can supply only two qualified snippets for the planned roles; the batch must record a `coverage_gap` and fail closed as `more evidence required` instead of borrowing a fourth snippet from another call. (US2, US4, FR4, FR7, FR15)
- A review output sounds concrete but cites details not supportable from the snippet or official materials; this must be tagged `false_specificity` even if the prose is otherwise polished. (US1, US3, FR3, FR11)
- A review card names the correct evaluation criterion/element but gives a generic revision suggestion; this should separate `criteria_groundedness` from `revision_actionability` rather than collapsing both into one score. (US1, US3, FR3, FR11)
- The first few snippets in a batch expose failures and the reviewer wants to start proposing fixes mid-run; the procedure must block that drift and continue recording evidence first. (US3, US4, FR9, FR17)
- The batch baseline changes after some items were reviewed; completed records may remain archived, but they cannot support one aggregate decision unless the batch is formally split or restarted. (US3, US4, FR8, FR9, FR14)
- One locked call has fewer snippets than the others; the strategy may vary counts by call, but it must still justify representativeness and cannot silently drop the call. (US2, FR5-FR7)
- An output is useful overall but prioritizes lower-value revisions ahead of a mission-critical issue in the same snippet; the evidence record must capture this as `bad_prioritization` without rewriting the whole output judgment as total failure. (US1, US3, FR3, FR11)

## 8. Testing Decisions (TDD)

- This WF defines planning for a behavior-evaluation process, not product remediation. Phase 2 should still plan deterministic verification around public documentation seams and evidence outputs. (US1-US4)
- Public seams under test in later phases should include:
  - the snippet-set selection artifact or template,
  - the frozen baseline record,
  - the evidence-record template or schema,
  - the batch-summary decision artifact. (US2-US4, FR6-FR15)
- Mock only external boundaries if Phase 3 introduces helpers or scripts; do not mock the classification logic encoded in the evidence template, the pass/fail rules, or the locked wedge membership rules. (US2-US4)
- Required minimum verification planning for Phase 2:
  - deterministic checks that the locked call set is exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`. (US2, FR5)
  - checks that convenience-sampling protections, per-snippet rationale fields, and the exact `3 snippets x 3 calls` role matrix are mandatory. (US2, FR6, FR7)
  - checks that the frozen baseline requires commit, prompt/model-runtime, reviewer instructions, template version, and a shared 4-state dimension scale. (US3, FR8)
  - checks that the evidence record requires official locators, failure tags from the fixed taxonomy, severity, revision-action judgment, follow-on pattern class, and insufficient-evidence handling. (US1, US3, FR10-FR13)
  - checks that batch-level summaries separate `mission_result` from `follow_on_decision` and cannot emit `proceed_to_narrow_follow_on_wf` without a named verification evidence bundle and a bounded recommended follow-on boundary. (US4, FR14-FR16)
  - checks that Phase 2/3 execution artifacts do not include prompt tuning, engine fixes, UI fixes, or wedge expansion under WF-0068 scope. (US4, FR17)

## 8.1 Readiness Gate

- WF-0068 is not ready for Tasks unless the PRD fully defines:
  - the mission-anchored evaluation framework,
  - the locked representative snippet-set strategy,
  - the deterministic review procedure,
  - the fixed failure taxonomy,
  - the evidence record contract,
  - the pass/fail and follow-on boundary. (US1-US4)
- WF-0068 is not ready for implementation-phase evaluation work unless the later task plan preserves the strict scope boundary against prompt tuning, engine fixes, UI fixes, and wedge expansion. (US4, FR16, FR17)
- No later runner may claim success for this WF from a persuasive sample output alone; the named verification evidence bundle is mandatory. (US4, FR14, FR15)

## 9. Telemetry (Minimal)

- No product telemetry is required for MVP.
- Minimal run metadata inside the evidence bundle is allowed only to preserve replayable evaluation provenance for the frozen batch baseline.

## 10. Deferred / Not in MVP

- Any follow-on prompt, engine, UI, or data fixes identified by the evidence.
- Any automated evaluator, dashboard, or continuous quality-monitoring system.
- Any expansion to additional calls or broader launch-readiness programs.
- Any attempt to define product-wide “AI quality” beyond this narrow review-quality loop.

## 11. Open Questions (if any)

- Phase 2 may decide whether disagreement handling needs a second reviewer path, but the default MVP assumption is one constrained reviewer procedure unless evidence says otherwise.

## 12. Changelog

- v0.1 (2026-03-08): Initial PRD from brainstorm.
- v0.2 (2026-03-08): Applied risk-audit edits to lock the 9-snippet representative batch, formalize the 4-state scoring scale, and separate mission result from follow-on decision.
