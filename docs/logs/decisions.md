<!-- docs/logs/decisions.md -->
# Architectural Decisions

## Date: 2026-04-03 (WF-0082: codex-usage-optimization)

### AD 82.1: WF-0082 defines default context by repo trigger posture and optimizes entrypoints before deeper archive work
- **WF ID**: WF-0082
- **Context**: The approved brainstorm identified that the repo's main problem is not total documentation volume, but broad default entrypoints that encourage large files such as `docs/index.md` to be opened too early. The workflow also needs to preserve safety, traceability, and researcher-facing terminology while improving day-to-day Codex performance.
- **Decision**: Define `default context` as files the repo explicitly encourages opening early or for most tasks. Prioritize cleanup of the heaviest likely default entrypoints first, especially `docs/index.md` and any overly broad `AGENTS.md` triggers. Treat deeper memory/history refactors as secondary work only after the entrypoint cleanup is complete or proven insufficient.
- **Why**: This keeps the optimization tied to likely agent behavior instead of aesthetic file trimming and creates the highest chance of meaningful context reduction with the smallest safe edits.
- **Tradeoff**: Some large historical files may remain in the repo untouched during MVP if they are no longer default entrypoints; broader archival cleanup can follow later if the first-pass reduction is not enough.
- **Status**: Approved.

## Date: 2026-03-14 (WF-0081: atomic-findings-structured-review)

### AD 81.1: WF-0081 keeps diagnostic findings as the upstream truth and assigns one canonical `ReviewFinding` write owner
- **WF ID**: WF-0081
- **Context**: The approved brainstorm is explicit that the current engine already produces diagnostic findings before collapsing them into `ReviewCard`, and the main Phase 1 risk is creating competing truths between cards and findings during rollout.
- **Decision**: Preserve the current diagnostic-finding engine as upstream truth for MVP and introduce one bounded backend mapping seam as the only canonical owner of `ReviewFinding` persistence for new atomic reviews.
- **Why**: This keeps the workflow grounded in existing engine behavior, avoids reopening engine redesign scope, and gives Phase 2 one clear ownership seam to test and harden.
- **Tradeoff**: The mapper becomes a critical contract boundary that later tasks must prove carefully instead of spreading transformation logic across repositories, serializers, and frontend adapters.
- **Status**: Approved.

### AD 81.2: WF-0081 review detail exposes one explicit per-review mode with truthful same-page behavior
- **WF ID**: WF-0081
- **Context**: The approved brainstorm requires backward-compatible legacy `ReviewCard` reads plus a new findings-based detail shape grouped under reviewed nodes, while repo memory requires same-page review-detail actions to remain truthful when visible content changes.
- **Decision**: Require review-detail responses to declare one explicit `detail_mode` per review: `legacy_cards` for legacy reviews and `reviewed_node_findings` for new atomic reviews. Treat that mode as the sole researcher-visible read truth for that review, and require same-page actions such as copy/export to stay aligned with the rendered mode or surface a bounded limitation explicitly.
- **Why**: This prevents heuristic client branching, avoids mixed-mode ambiguity, and keeps the researcher-visible surface honest during rollout.
- **Tradeoff**: Later implementation must prove both render modes and any same-page action behavior explicitly rather than assuming the page-only render closes the contract by itself.
- **Status**: Approved.

## Date: 2026-03-14 (WF-0080: production-mvp-launch-wedge)

### AD 80.2: WF-0080 keeps review-detail prioritization as one backend projection contract with explicit ranking semantics
- **WF ID**: WF-0080
- **Context**: The approved brainstorm required one bounded review-detail projection seam and an action-first top-3 reading model, but the initial PRD draft still left the exact positive-state threshold and rank precedence partly implicit.
- **Decision**: Keep the only new reading-model contract at `GET /reviews/{review_id}` response assembly in `backend/main.py` as additive `detail_projection` metadata. Compute ranking from existing card truth using `NOT_ASSESSABLE` before `ASSESSED`, then `CRITICAL` -> `WARNING` -> `NOTE` -> `SUCCESS`, then existing call/node order. Set `headline_state = no_critical_blockers` only when every card is `ASSESSED` and rated `NOTE` or `SUCCESS`.
- **Why**: This makes the wedge verifiable without inventing new persistence or letting BFF/frontend code reinterpret trust semantics locally.
- **Tradeoff**: The backend response contract becomes slightly richer, so Phase 2 must prove passthrough discipline and keep the projection additive-only.
- **Status**: Approved.

### AD 80.3: WF-0080 usefulness evidence is optional when no cohort exists yet
- **WF ID**: WF-0080
- **Context**: The original WF-0080 plan assumed a real launch cohort with attributable researcher sessions, but the product is shipping without cohort onboarding and without usefulness ratings at this stage.
- **Decision**: Keep the walkthrough `Usefulness Evidence Log` as an optional evidence artifact for later, but do not block merge/ship on achieving a minimum count of useful sessions when no cohort exists yet.
- **Why**: Prevents a documentation-only gate from blocking shipping when the cohort mechanism and usefulness-rating loop are not in use.
- **Tradeoff**: Early shipping may proceed without structured usefulness evidence; a later WF can reinstate an evidence gate once cohort sessions exist.
- **Status**: Approved.

### AD 80.4: WF-0080 review detail renders findings grouped by section with deterministic bullets, optional LLM companion, and no supporting-evidence drawer
- **WF ID**: WF-0080
- **Context**: Manual verification found the action-first top-3 split plus per-card “supporting evidence” drawer added scan friction and hid the most important thing: multiple findings per proposal section/node.
- **Decision**: Render findings grouped by reviewed section/node on `/app/reviews/[reviewId]`. Keep deterministic `feedback_text` as the primary guidance, render it as a bullet list for readability, and show additive `synthesized_companion_text` only when present as optional LLM companion guidance. Remove the “Top actions” / “Other findings” buckets and remove the “Supporting evidence” drawer entirely.
- **Why**: Improves researcher scanability and keeps the page focused on actionable deterministic guidance while still allowing additive LLM help when available.
- **Tradeoff**: The page no longer provides a separate “top actions” prioritization bucket; prioritization remains available only as backend `detail_projection` headline context.
- **Status**: Approved.

### AD 80.1: WF-0080 locks the launch wedge to one `ERC-2026-PoC` cohort with an action-first review-detail model
- **WF ID**: WF-0080
- **Context**: The approved Phase 0 brainstorm rejects architecture-first planning and requires one explicit launch wedge, one happy-path submit-to-detail flow, one review-detail reading model, and 5-10 researcher-session usefulness evidence.
- **Decision**: Lock WF-0080 to `ERC-2026-PoC`, use an authenticated cohort allowlist at the BFF with a mirrored backend fail-closed reject, and define the review-detail reading model as at most the top 3 actionable cards above the fold ordered by existing card assessment status, then lowest rating, then existing call/node order. Capture usefulness closure in a walkthrough appendix `Usefulness Evidence Log` with attributable session rows.
- **Why**: This turns the Phase 0 wedge into a concrete planning boundary instead of a launch-readiness theme, and it keeps Phase 1 from relitigating the exact call, cohort gate, or evidence artifact.
- **Tradeoff**: The wedge is intentionally narrow and may require a separate follow-on WF for broader launch infrastructure, cross-call rollout, or richer export/admin surfaces.
- **Status**: Superseded by AD 80.4.

## Date: 2026-03-13 (WF-0079: researcher-visible-carry-through-mvp)

### AD 79.1: WF-0079 exposes the narrowest safe public card contract as nullable companion text on review detail only
- **WF ID**: WF-0079
- **Context**: The approved brainstorm requires one end-to-end detail-page MVP, explicit backward compatibility for reviews with no companion data, and optimization for the narrowest safe public card contract.
- **Decision**: Keep deterministic `feedback_text` unchanged and expose one nullable card-level `synthesized_companion_text` field through the review detail contract. Treat `null` as the valid value for legacy reviews, out-of-scope cards, and cards without accepted persisted synthesis. Do not expose rejection taxonomy or add extra public provenance fields unless later implementation planning proves they are strictly required.
- **Why**: This preserves deterministic truth, keeps the public surface additive and backward compatible, and minimizes serializer/frontend coupling.
- **Tradeoff**: The public contract carries less provenance detail, so deeper diagnostics stay internal unless a later workflow re-approves broader exposure.
- **Status**: Approved.

### AD 79.2: WF-0079 keeps page-local copy/export deterministic-only in MVP
- **WF ID**: WF-0079
- **Context**: The brainstorm treats `/app/reviews/[reviewId]` as the first researcher-visible seam and flags the existing page-local copy/export action as a same-page truthfulness coupling that cannot be ignored.
- **Decision**: Keep the page-local copy/export action deterministic-only for MVP, and require user-facing wording to make that limitation explicit even when additive companion text renders on the page.
- **Why**: This is the narrowest honest closure that avoids widening the MVP into broader export work while still closing the same-page truth gap safely.
- **Tradeoff**: Researchers may see more on the page than in copied/exported output until a later workflow explicitly widens export scope.
- **Status**: Approved.

### AD 79.3: WF-0079 readiness stays fail-closed and must prove scope-gate safety explicitly
- **WF ID**: WF-0079
- **Context**: The approved brainstorm requires explicit pass/fail proceed evidence, closure of all justified findings, and `ERC-2026-PoC`-only carry-through. The first finalized PRD draft kept the verification matrix but softened those guarantees by omitting the proceed-gate prose, the audit ledger, and a dedicated proof row for non-targeted calls/cards.
- **Decision**: Require the PRD, task plan, and any implementation-ready recommendation to retain explicit proceed-gate language, an audit disposition ledger, and a dedicated verification obligation proving non-targeted calls/cards do not persist or expose additive companion data.
- **Why**: This keeps WF-0079 fail-closed against hallucinated readiness and silent cross-call scope drift.
- **Tradeoff**: Later phases must carry slightly more closure bookkeeping and one extra deterministic proof seam before claiming readiness.
- **Status**: Approved.

## Date: 2026-03-13 (WF-0078: structured-review-grounded-llm-synthesis)

### AD 78.1: WF-0078 MVP stays downstream of `pipeline_v1` and closes first as backend seam proof
- **WF ID**: WF-0078
- **Context**: The approved brainstorm locks `pipeline_v1` as deterministic SSOT, rejects `ReviewExecutionCore` and frontend-only rewriting as the first seam, and flags response carry-through as an explicit Phase 1 decision rather than an implied rollout.
- **Decision**: Keep MVP synthesis per card and downstream of `pipeline_v1` in `StructuredReviewerService` or a helper owned by that seam. Close the first PRD at backend seam proof only, with persistence/API/review-detail/export/frontend carry-through deferred to a separate dependent slice if broader rollout is later required.
- **Why**: This is the smallest honest boundary that preserves rollback to WF-0077 deterministic guidance, respects the 3-file task-slice rule, and avoids hiding wider contract work inside a backend-first proof.
- **Tradeoff**: The first implementation may prove the synthesis contract without immediately changing every user-visible read surface, so a broader rollout claim must wait for an explicit follow-on task plan.
- **Status**: Approved.

### AD 78.2: WF-0078 keeps additive synthesis seam-scoped first and forbids non-targeted synthesis attempts
- **WF ID**: WF-0078
- **Context**: The brainstorm locks raw machine `reason` as audit-only, requires fail-closed fallback to WF-0077 deterministic guidance, and says additive-field/provenance carry-through must be an explicit Phase 2 decision rather than an implied first-slice rollout.
- **Decision**: Preserve deterministic `feedback_text` as the stable fallback surface, add only an optional synthesized companion plus a seam-scoped synthesis outcome marker for targeted in-scope cards, and defer any public/API/frontend provenance carry-through to a separate dependent slice. Non-targeted calls/cards must not invoke synthesis at all and must keep their current deterministic contract unchanged.
- **Why**: This removes the hidden contradiction between backend-only seam proof and public-contract widening while also preventing silent cost/coupling drift outside the approved `ERC-2026-PoC` slice.
- **Tradeoff**: The first implementation may validate synthesis behavior mostly at the service seam, so broader user-visible rollout still needs explicit follow-on planning and proof.
- **Status**: Approved.

## Date: 2026-03-13 (WF-0077: structured-review-deterministic-researcher-guidance)

### AD 77.1: WF-0077 MVP stays at the structured-review service seam with `ERC-2026-PoC` only
- **WF ID**: WF-0077
- **Context**: The approved brainstorm and repo snapshot show that `backend/app/services/structured_reviewer_service.py` already owns the call-scoped presentation seam, while evaluator and compatibility-mapper layers carry machine/audit semantics that would widen behavior across calls if edited for researcher-facing guidance.
- **Decision**: Lock MVP to an additive deterministic guidance transform in `StructuredReviewerService` for `ERC-2026-PoC` only. Preserve raw machine `reason`, keep evaluator/mapper/legacy review paths out of the primary slice, and treat frontend work as conditional-only follow-on scope.
- **Why**: This is the smallest honest seam that can improve researcher-facing `feedback_text` without reopening WF-0074/WF-0075/WF-0076 boundaries or broadening cross-call behavior.
- **Tradeoff**: Immediate benefit remains intentionally narrow, so broader structured-call reuse and UI polish are deferred until later artifacts prove they are needed.
- **Status**: Approved.

### AD 77.2: WF-0077 Phase 2 must stay backend-first and task-atomic
- **WF ID**: WF-0077
- **Context**: The brainstorm and current runner invocation both require a bounded implementation plan: `ERC-2026-PoC` first, backend-only MVP preferred, and a 3-file task limit to prevent the guidance work from silently widening into frontend or cross-layer refactors.
- **Decision**: Require Phase 2 to decompose WF-0077 into backend-first tasks that prefer no more than three touched files each, with `backend/app/services/structured_reviewer_service.py` and `backend/tests/test_structured_reviewer_service.py` as the default first implementation slice. Any frontend work must be planned as a separate conditional follow-on only after backend proof shows a real render-truth gap.
- **Why**: This keeps the implementation plan aligned with the approved seam and makes scope drift visible before Phase 3 starts.
- **Tradeoff**: Planning may produce more than one small dependent task instead of one broader convenience slice, but that preserves auditability and rollback safety.
- **Status**: Approved.

### AD 77.3: WF-0077 closes at the verified backend seam with no frontend follow-on
- **WF ID**: WF-0077
- **Context**: Phase 3 implemented the deterministic guidance rewrite and fail-closed fallback handling entirely inside `StructuredReviewerService`, with service-level proof for actionable guidance, machine-reason passthrough, weak-source fallback, and non-targeted-call safety. The conditional Task 3 check then re-verified that `frontend/src/app/app/reviews/[reviewId]/page.tsx` still renders `card.feedback_text` directly.
- **Decision**: Close WF-0077 as a backend-only completion. Do not open a frontend follow-on workflow from this closeout because the current review page already reflects the improved backend contract without additional UI work.
- **Why**: This preserves the smallest honest closure claim: deterministic researcher guidance improved at the approved service seam, fail-closed behavior remains intact, and there is no remaining render-truth gap that justifies widening scope.
- **Tradeoff**: The deterministic phrasing remains intentionally tied to the current `ERC-2026-PoC` subordinate-prompt seam; broader call rollout or richer phrasing stays deferred to a separately justified workflow.
- **Status**: Approved.

## Date: 2026-03-12 (WF-0076: subordinate-prompt-runtime-consumption)

### AD 76.2: WF-0076 MVP must source prompts from canonical call JSON and prove effect through evaluator reason output
- **WF ID**: WF-0076
- **Context**: Phase 1 audit of the WF-0076 PRD against live code found two hidden-coupling risks. The active runtime path already has `CallDefinition.canonical_json` available in `backend/app/services/structured_reviewer_service.py`, but subordinate prompts are not present on `NodeExpectation` rows. The active `pipeline_v1` path delegates live expectation evaluation to `backend/app/engine/findings/evaluator.py`, which emits finding `reason`; by contrast, `extract_observations` depends on snapshot `proposal_nodes`, a surface the structured-review activation path does not currently populate.
- **Decision**: Lock MVP to derive subordinate prompts from the existing canonical call-definition JSON through current expectation/evaluation-element identity, with no new persistence or authoring seam. Lock the first runtime-effect proof to evaluator-produced finding `reason` output on the active `pipeline_v1` path. Treat observation-detail and prompt-builder-first proof as out of MVP unless a later workflow proves the active runtime actually routes through them.
- **Why**: This preserves the smallest honest runtime seam and the narrowest deterministic proof slice while avoiding hidden expansion into inactive or broader runtime surfaces.
- **Tradeoff**: MVP proof stays tightly constrained to one active artifact and one data-source seam, so broader proof surfaces remain deferred even if they look attractive for future extensibility.
- **Status**: Approved.

### AD 76.1: WF-0076 must land through one activated-expectation seam and one ERC PoC proof path first
- **WF ID**: WF-0076
- **Context**: The approved brainstorm locks this workflow to runtime consumption, not authoring/governance or proof-call completeness. Repo inspection shows the active discard seam in `backend/app/services/structured_reviewer_service.py`, while the live execution path is `backend/app/engine/pipeline_v1.py`.
- **Decision**: Plan WF-0076 around one additive activated-expectation `subordinate_prompts` payload and one first proof path under ERC PoC `poc_idea_innovation`, preferring evaluator-produced finding detail as the first deterministic runtime-effect artifact. Broader ERC PoC coverage remains a regression obligation, not the first implementation slice.
- **Why**: This is the smallest seam that can honestly move subordinate prompts from canonical storage into active runtime behavior without reopening WF-0074/WF-0075 scope or forcing broad engine redesign.
- **Tradeoff**: The first implementation will prove runtime consumption narrowly before any broader call or artifact expansion, so universal benefit claims remain explicitly deferred.
- **Status**: Approved.

## Date: 2026-03-12 (WF-0075: erc-poc-proof-call-fidelity-completion)

### AD 75.2: WF-0075 closes at proof-call fidelity completion with no immediate follow-on backlog promotion
- **WF ID**: WF-0075
- **Context**: Phase 3 verification re-proved page-43-complete subordinate-prompt coverage for the real ERC PoC proof-call, preserved the expectations-only runtime boundary, and closed the stale workflow-state audit gap in active status surfaces.
- **Decision**: Close WF-0075 once the targeted coverage, dry-run, and runtime-boundary proofs pass and the active workflow artifacts are aligned. Do not promote an immediate follow-on backlog item from this closeout. Any future work must be separately scoped and justified either as broader canonical-call migration or as explicit runtime-consumption widening beyond the current expectations-only seam.
- **Why**: WF-0075 exists to finish one real proof-call honestly and fail closed, not to reopen WF-0074 governance or imply a broader runtime/product commitment.
- **Tradeoff**: The repo now has one fidelity-complete ERC PoC proof-call with executable closure evidence, but broader subordinate-prompt rollout and runtime use remain intentionally deferred.
- **Status**: Approved.

### AD 75.1: WF-0075 PRD must preserve the fail-closed closure matrix as a first-class contract
- **WF ID**: WF-0075
- **Context**: PRD v0.1 captured the need for page-43-complete ERC PoC subordinate-prompt coverage and three-state proof semantics, but the Part B audit found that it had compressed the brainstorm's explicit verification matrix and audit-disposition closure gate into prose requirements.
- **Decision**: Keep the PRD closure contract explicit: Phase 2 and later phases must inherit a row-based verification matrix with `pass`/`fail`/`skipped` results, explicit evidence references, and a named audit-disposition artifact covering proof-call completion, source-to-YAML coverage, partial-vs-complete failure, absent/complete/partial distinction, compatibility-posture preservation, baseline-anchored scope proof, and runtime-boundary honesty.
- **Why**: WF-0075 is an SSOT-bound fidelity-closure workflow. If the matrix is softened into prose at PRD time, later phases can appear complete while silently dropping the fail-closed proof object that distinguishes honest completion from partial encoding.
- **Tradeoff**: The PRD carries a slightly heavier closure section, but Tasks and implementation inherit a deterministic, reviewable gate instead of reconstructing it ad hoc.
- **Status**: Approved.

## Date: 2026-03-11 (WF-0074: canonical-funding-call-fidelity-hardening closeout)

### AD 74.4: WF-0074 closes at authoring-fidelity hardening with no automatic runtime follow-on
- **WF ID**: WF-0074
- **Context**: Phase 3.2 found that the initial Part C1 fix incorrectly blocked non-dry-run ingest of `erc_poc_2026_full.yaml`, even though V2 persistence already preserves the full canonical JSON including `subordinate_prompts`. The repaired closeout re-proved DB persistence and separately proved that the structured-review runtime snapshot remains expectations-only.
- **Decision**: Close WF-0074 as complete once schema/template/docs/governance hardening and the narrowed persistence/runtime-boundary proofs pass. Do not create an automatic follow-on WF from this closeout. Any future work to make subordinate-prompt fidelity influence structured-review runtime behavior must be a separately scoped WF with an explicit runtime contract, proof surface, and launch-value rationale.
- **Why**: This preserves the actual achievement of WF-0074 without overclaiming runtime impact, and it avoids turning a narrow authoring/governance workflow into implicit runtime roadmap debt.
- **Tradeoff**: Canonical call fidelity is now preserved durably and truthfully, but the structured-review engine still consumes only the existing expectations snapshot unless a later WF widens that seam on purpose.
- **Follow-on boundary rationale**: No immediate backlog promotion is required for launch readiness. Only promote a follow-on if product needs clearly justify subordinate-prompt-aware runtime behavior beyond the current expectations-only boundary.
- **Status**: Approved.

## Date: 2026-03-11 (WF-0074: canonical-funding-call-fidelity-hardening)

### AD 74.3: WF-0074 subordinate-prompt fidelity rule and closure gate are durable governance
- **WF ID**: WF-0074
- **Context**: Phase 3 implementation adds a typed subordinate-prompt authoring contract, one real proof-call in `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`, and fail-closed workflow/checklist wording, but those rules would remain too transient if they lived only in the task artifact or chat log.
- **Decision**: Preserve the subordinate-prompt fidelity rule as durable governance: official subordinate prompts/questions must be preserved explicitly for new or re-authored calls when the source includes them; existing flat canonical YAMLs remain temporarily compatible only as a bounded MVP compatibility posture; `erc_poc_2026_full.yaml` remains the real proof-call example for this WF; and no runtime-consumption claim is allowed while the activated snapshot seam remains expectations-only.
- **Why**: This keeps the fidelity hardening policy, compatibility posture, proof-call policy, and seam-boundary honesty stable beyond one implementation session.
- **Tradeoff**: Governance text is slightly more explicit, but it prevents later closeout from overstating what the runtime currently consumes.
- **Status**: Approved.

## Date: 2026-03-11 (WF-0074: canonical-funding-call-fidelity-hardening)

### AD 74.2: WF-0074 must preserve durable governance surfaces and fail-closed evidence gates in the PRD
- **WF ID**: WF-0074
- **Context**: The approved brainstorm made `decision/memory guidance` and a row-level fail-closed verification matrix part of the MVP contract, but the PRD draft initially compressed those into softer prose and testing notes.
- **Decision**: Keep decision-log/memory guidance as an explicit MVP surface in the PRD, require typed subordinate-prompt items with stable identity plus source traceability, and require a verification evidence matrix plus audit-disposition ledger before any proceed or ship recommendation.
- **Why**: This prevents Phase 2/3 from satisfying WF-0074 with only schema/template/docs changes, blocks anonymous-string prompt shapes that would weaken traceability, and preserves explicit pass/fail evidence discipline for closure.
- **Tradeoff**: The planning artifact and final walkthrough carry a bit more structure, but the closure contract stays replayable and cannot silently drift from the approved brainstorm.
- **Status**: Approved.

## Date: 2026-03-11 (WF-0074: canonical-funding-call-fidelity-hardening)

### AD 74.1: WF-0074 is authoring-contract hardening first, with explicit checklist and proof-call seams
- **WF ID**: WF-0074
- **Context**: The brainstorm required a narrow slice across schema, template, authoring docs/checklist, tests, and one proof-call example, while also requiring explicit inspection of the activated snapshot / engine contract seam before making runtime-impact claims.
- **Decision**: Keep WF-0074 scoped to authoring-contract hardening in MVP. Use `docs/call-yaml/onboarding-checklist.md` as the checklist seam, default the proof-call surface to `backend/data/calls/canonical/erc/erc_poc_2026_full.yaml`, and require compatibility proof against at least one existing real flat canonical YAML. Treat the current `structured_reviewer_service.py` snapshot seam as a claim boundary: no runtime-consumption claim in this WF unless a later task adds and proves the narrowest necessary snapshot change.
- **Why**: This preserves the smallest defensible cross-call slice, keeps the contract concrete on real repo surfaces, and avoids overclaiming review-quality impact while the runtime snapshot still carries only `schema_version` plus `expectations`.
- **Tradeoff**: The MVP improves representability, defaults, and governance now, but a later WF is still required if the product needs subordinate prompt fidelity to flow into the structured-review engine itself.
- **Status**: Approved.

## Date: 2026-03-11 (WF-0073: erc-poc-2026-call-onboarding closeout)

### AD 73.2: Close WF-0073 with backend-only proof and call-local manifest-gate hardening
- **WF ID**: WF-0073
- **Context**: Phase 3 technical audit found one blocking fail-closed defect in the ERC PoC source-manifest gate: one manifest entry could satisfy both required source classes.
- **Decision**: Close WF-0073 using the existing backend seams only (manifest gate, dry-run, DB ingest, `/calls`, node metadata, structured-review smoke) and accept only a call-local compatibility fix in `backend/scripts/ingest_call.py` requiring distinct compliant source entries for structure vs evaluation criteria/elements.
- **Why**: Preserves one-call scope, prevents source-traceability false passes, and avoids broad ERC runtime changes without evidence of need.
- **Follow-on boundary rationale**: No automatic follow-on WF is required for launch readiness; any future work must be separately scoped for non-WF-0073 surfaces (full-suite regression expansion, frontend/BFF/browser proof, or broader ERC generalization).
- **Status**: Approved.

## Date: 2026-03-11 (WF-0073: erc-poc-2026-call-onboarding)

### AD 73.1: ERC PoC onboarding prefers call-local activation seams and keeps submission dependencies non-reviewable
- **WF ID**: WF-0073
- **Context**: PRD v0.1 locked `ERC-2026-PoC` to one-call onboarding with backend structured-review proof, but the audit found two remaining drift risks: Phase 2 could widen compatibility work into broader ERC runtime edits too early, and it could model the Host Institution Support Letter or Ethics Issues Table as reviewable proposal nodes.
- **Decision**: For `ERC-2026-PoC`, prefer call-local config or activation fixes before any broader ERC runtime changes. Treat the Host Institution Support Letter and Ethics Issues Table as submission dependencies represented through guidance or compliance metadata, not as reviewable proposal nodes.
- **Why**: This keeps the least-risk path aligned to the 2026-03-17 deadline, avoids unnecessary cross-call regression surface, and preserves the authoring boundary that proposal nodes should model evaluable narrative content only.
- **Tradeoff**: If the repo cannot support the call through narrow seams, a later task may still need a broader ERC runtime fix, but only after the narrower path is disproven.
- **Status**: Approved.

## Date: 2026-03-10 (WF-0072: e2e trust proof nwo erc msca)

### AD 72.3: Policy-blocking closure requires the user-facing block on the exercised seam, not API evidence alone
- **WF ID**: WF-0072
- **Context**: The approved brainstorm requires policy-blocking proof to pair researcher-visible blocking semantics with zero downstream side-effect evidence, but the stabilized PRD risked reducing that requirement to API/runtime evidence only.
- **Decision**: Treat policy-blocking proof as incomplete unless it includes the visible block on the exercised user-facing seam for that proof item, or narrows the claim explicitly to a lower-level seam instead of presenting it as end-to-end proof.
- **Why**: This prevents Phase 2 from overclaiming end-to-end trust proof from backend-only evidence when the user-facing boundary is part of the launch claim.
- **Tradeoff**: Some strongest no-side-effect checks will need paired browser/app or BFF evidence instead of a single API-only row.
- **Status**: Approved.

### AD 72.4: Evidence references must be replayable, not just attributable
- **WF ID**: WF-0072
- **Context**: The brainstorm locks exact commands/selectors/results as part of the MVP verification output, but the PRD matrix contract had only required an `evidence_ref`, which left room for opaque screenshots/logs that another maintainer could not rerun deterministically.
- **Decision**: Require every trust-proof evidence reference to resolve to deterministic replay metadata: the exact command or test ID, the exact selector/assertion or manual checklist step, and the expected outcome/result for that proof item.
- **Why**: This keeps the verification matrix auditable and rerunnable instead of turning evidence into detached artifacts with hidden operational knowledge.
- **Tradeoff**: Evidence artifacts and walkthrough rows become slightly heavier, but they stay reproducible and reviewable.
- **Status**: Approved.

### AD 72.1: Verification rows are the authoritative trust-proof object
- **WF ID**: WF-0072
- **Context**: The brainstorm locked a one-row-per-proof-item verification matrix, but the initial PRD draft still left room for Phase 2 to treat seam labeling and same-family versus alternate-family negative-case coverage as informal notes instead of required row data.
- **Decision**: Treat each verification-matrix row as the authoritative proof object for WF-0072. Every row must include the exact exercised entrypoint/boundary, deterministic `evidence_ref`, and a scope note stating whether the scenario is proven on the same representative family or intentionally on a different representative.
- **Why**: This prevents traceability drift across browser, BFF, and API evidence and keeps negative-case claims auditable without hidden assumptions.
- **Tradeoff**: Phase 2 and later walkthrough artifacts must carry slightly more structured metadata for every proof item.
- **Status**: Approved.

### AD 72.2: Fail-closed negative proof is one paired claim, not separate UX and backend checks
- **WF ID**: WF-0072
- **Context**: The bounded WF scope requires visible fail-closed behavior plus zero side effects for ERC stage mismatch, missing mandatory input, and policy-blocking. Without an explicit pairing rule, Phase 2 could overclaim closure from a visible block or an API assertion alone.
- **Decision**: Treat each negative-case proof item as one paired claim: the user-facing blocking result and the matched no-side-effect assertion must pass together, and protected app/BFF proofs must also carry an explicit auth-lane plan.
- **Why**: This keeps the trust claim honest across user-visible and backend-invariant layers and preserves the fail-closed bar defined in the brainstorm.
- **Tradeoff**: Some proof items will require paired browser and backend evidence rather than a single-lane shortcut.
- **Status**: Approved.

## Date: 2026-03-10 (WF-0071: node hierarchy selector)

### AD 71.1: Breadcrumb context derives from existing React context, not prop drilling or backend expansion
- **WF ID**: WF-0071
- **Context**: PRD v0.1 required `ReviewCard.tsx` (or its equivalent wrapper) to display ancestor breadcrumbs by looking up `node_id` in `callConfig`. The Phase 1.2 risk audit flagged this as a potential hidden coupling or prop-drilling risk if `callConfig` availability wasn't explicitly routed.
- **Decision**: Rely on existing React context (e.g., `CallContext` or similar) to supply `callConfig` to the breadcrumb renderer. Do not expand the backend review payload to include ancestor strings, and do not introduce deep prop drilling to pass `callConfig` down to every leaf card.
- **Why**: Keeps the backend payload flat and decoupled from UI display concerns while avoiding brittle frontend prop drilling.
- **Tradeoff**: The component rendering the breadcrumb must be rendered within the appropriate React context provider.
- **Status**: Approved.

### AD 71.2: Close WF-0071 with 1-level hierarchy UI; defer deep recursion and backend expansion
- **WF ID**: WF-0071
- **Context**: Phase 3 implementation shipped 1-level node grouping in the submit form, leaf-only submit semantics, an orphan "Uncategorized" fallback, and ancestor breadcrumbs on review cards. Targeted frontend verification passes (vitest selectors for the touched test surfaces).
- **Decision**: Close WF-0071 as complete for the MVP wedge: 1-level visual grouping + unselectable container headers + breadcrumb context derived from `callConfig` on the client.
- **Why**: This closes the user-facing trust gap (structural context) without requiring backend schema changes or a recursive UI surface that would broaden both implementation and proof obligations.
- **Follow-on boundary**: Any future work to support N-deep trees, multi-level submit chunking, or server-projected ancestor strings must be a new WF with an explicit contract + verification plan. Also treat the task-template mismatch (`npm test` vs repo scripts) as a workflow tooling follow-on, not part of this WF’s feature scope.
- **Status**: Approved.

## Date: 2026-03-09 (WF-0070: erc structured review step gating)

### AD 70.1: ERC structured review stage truth is authored at the proposal-surface stage-scope contract
- **WF ID**: WF-0070
- **Context**: The brainstorm and Phase 1 audit identified the current split-brain defect: evaluation-element stage metadata can still collapse `b2_part2_scientific_proposal` into an effective `BOTH` surface, while UI visibility, validation, and runtime activation need one authority for official ERC Step 1 vs Step 2 surface truth.
- **Decision**: Treat the authored proposal-surface stage-scope contract in canonical ERC call configuration as the sole authoritative stage-truth source for ERC structured review. Any node metadata, validation snapshot, runtime activation input, or evidence projection must be derived from that contract rather than authored as a peer authority.
- **Why**: This resolves the current surface-truth drift at the level researchers actually submit and review, keeps Phase 2 localized to one coherent contract, and avoids evaluator-wide ERC specialization.
- **Tradeoff**: Existing generated node metadata and mixed element-stage assumptions must be updated to become derived outputs, which may invalidate tests or fixtures that currently rely on `BOTH` drift.
- **Status**: Approved.

### AD 70.2: Inspectable ERC stage evidence persists a review-time scope snapshot
- **WF ID**: WF-0070
- **Context**: The brainstorm required Phase 1 to resolve whether existing persisted `review_stage` plus `submitted_leaf_ids` and stage-aware review-detail buckets were sufficient, or whether one additional evidence field was necessary to prove what actually ran for a completed ERC structured review.
- **Decision**: Extend the existing structured payload evidence seam with one derived review-time stage-scope snapshot field capturing the in-scope ERC leaf set for the completed review, and require review-detail stage-aware boundary buckets to be projected from that persisted evidence.
- **Why**: This keeps the evidence inspectable and replayable even if authored call configuration changes later, and it prevents review detail from silently recomputing scope from a newer config state.
- **Tradeoff**: Adds one persisted derived field to maintain, but avoids a disconnected provenance system and keeps the proof path honest.
- **Status**: Approved.

### AD 70.3: WF-0070 proceed claims require baseline-anchored scope proof and audit disposition
- **WF ID**: WF-0070
- **Context**: The finalized PRD still required concrete verification evidence, but it left room for a future proceed or implementation-ready claim to rely on passing tests alone without an explicit scope proof or explicit closure of justified review findings.
- **Decision**: Require every proceed, implementation-ready, or ship recommendation for WF-0070 to include both a baseline-SHA or explicit commit-range-anchored scope proof and an audit-disposition ledger that closes every blocking finding while closing or explicitly rejecting each justified non-blocking finding with rationale.
- **Why**: This keeps the trust-closure claim fail-closed and prevents false readiness based on partial evidence or unresolved review debt.
- **Tradeoff**: Closure evidence is heavier, and later phases must preserve explicit bookkeeping for scope and finding disposition.
- **Status**: Approved.

### AD 70.4: Single-node `/api/reviews` stays deferred unless structured-path honesty proves otherwise
- **WF ID**: WF-0070
- **Context**: The brainstorm required Phase 1 to decide whether deferring single-node review would undermine the structured ERC trust claim. Repo reality shows `POST /api/reviews` runs through `ReviewerService.generate_review`, while the WF target is the structured path through `POST /api/structured-review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, and structured review-detail evidence.
- **Decision**: Keep `/api/reviews` out of MVP scope for WF-0070 and treat it as a blocker or follow-on only if a later phase proves that the structured ERC trust claim cannot remain honest while the single-node path stays untouched.
- **Why**: This preserves the locked structured-review scope and avoids widening implementation into a separate service path without repo-grounded necessity.
- **Tradeoff**: The repo may temporarily carry different stage-hardening maturity across the two review entrypoints, so later phases must watch for contradictory semantics instead of assuming parity.
- **Status**: Approved.

### AD 70.5: WF-0070 closure is approved and relies on authoritative stage-truth contract
- **WF ID**: WF-0070
- **Context**: Verification in Phase 3 passes cleanly with explicit test coverage for stage validation.
- **Decision**: Close WF-0070 with no immediate follow-on workflow bounds. The trust-closure constraints are met using the proposal-surface contract.
- **Why**: All blockers are addressed, the boundary stays cleanly separated, and deterministic scope proofs are preserved.
- **Tradeoff**: Single-node logic remains disjointed and may require separate hardening if future workflows rely on it.
- **Status**: Approved.

## Date: 2026-03-09 (WF-0069: review actionability remediation)

### AD 69.1: WF-0069 closes a coupled actionability-plus-priority contract, not wording polish alone
- **WF ID**: WF-0069
- **Context**: WF-0068 closed with a repeated `actionability_cluster` boundary across the locked NWO/ERC/MSCA wedge, and the observed failing outputs were mostly flat `content_evaluated` or `NOTE`-style cards that did not tell the researcher what to revise first.
- **Decision**: Treat actionability and prioritization as one coupled remediation contract for WF-0069. The minimum successful seam must preserve an explicit revision move, a defensible highest-priority-versus-lower-priority distinction for the same snippet, and an explicit fail-closed non-actionable state when evidence is insufficient.
- **Why**: This keeps the follow-on WF anchored to the repeated WF-0068 failure pattern and prevents false closure through longer prose or single-dimension fixes that still leave researchers without defensible next-step ordering.
- **Tradeoff**: The implementation cannot rely on generic text polishing alone; it may need a slightly richer structured contract or mapper behavior than the current flat output path.
- **Status**: Approved.

### AD 69.2: WF-0069 verification reuses WF-0068 evidence and blocks generic-scope remediation
- **WF ID**: WF-0069
- **Context**: The brainstorm and AD 68.5 lock this WF to a narrow remediation follow-on, but without an explicit closure rule Phase 2 could broaden into trust-surface, launch-floor, prompt-tuning, or wider quality work under the banner of “helpfulness.”
- **Decision**: Reuse the exact WF-0068 stress and baseline item IDs as the primary closure evidence for WF-0069, require deterministic replay plus fail-closed and regression guards, and treat broader trust-surface, launch-floor, assisted-extraction, call-expansion, or generic prompt-tuning work as out of scope unless proven to be a hard dependency of the minimum contract.
- **Why**: This keeps remediation fail-closed, replayable, and bounded to the approved repeated failure instead of letting Phase 2 convert a narrow follow-on into a general review-quality initiative.
- **Tradeoff**: Some adjacent improvements that might help overall feedback quality remain deferred even if they are tempting to implement alongside the narrow fix.
- **Status**: Approved.

### AD 69.3: WF-0069 closure requires explicit audit disposition and baseline-anchored scope proof
- **WF ID**: WF-0069
- **Context**: Replay of the WF-0068 stress items is necessary but not sufficient for safe closure. Without stricter closure rules, a future ship/proceed recommendation could rely on nondeterministic worktree-only file listings or leave justified non-blocking audit findings unresolved without recording why.
- **Decision**: Require WF-0069 closure artifacts to include a scope proof anchored to the frozen remediation baseline SHA or explicit commit range, plus an audit-disposition ledger that closes every blocking finding and either closes or explicitly rejects each justified non-blocking finding with rationale. If the chosen remediation contract allows equal-priority revision moves, deterministic tie-handling regression coverage is also mandatory.
- **Why**: This keeps closure fail-closed, replayable, and explicit about what review concerns were actually resolved versus consciously rejected.
- **Tradeoff**: Closure evidence becomes slightly heavier and Phase 2/3 must preserve a small amount of additional bookkeeping.
- **Status**: Approved.

### AD 69.4: WF-0069 replay evaluator must validate required item role mappings fail-closed
- **WF ID**: WF-0069
- **Context**: The evaluator already enforced exact `item_id -> call_id` mapping, but still trusted mutable batch `role` values during stress-gate evaluation.
- **Decision**: Enforce exact `item_id -> role` mapping (`actionability_prioritization_stress` vs `baseline_representative`) for all required replay items and fail closed on mismatch before scoring.
- **Why**: Prevents false closure where a mislabeled stress item could bypass stress gating and still produce an `overall_pass` artifact.
- **Tradeoff**: Replay input is stricter and rejects malformed batches earlier, requiring item metadata discipline in fixtures/manifests.
- **Status**: Approved.

### AD 69.5: WF-0069 closure is approved with a strict no-follow-on boundary
- **WF ID**: WF-0069
- **Context**: Phase 3 closeout reran deterministic replay and targeted service/API selectors serially on isolated test DB after hardening evaluator invariants for `item_id -> call_id` and `item_id -> role`.
- **Decision**: Mark WF-0069 as closure-ready and user-gated for ship, with no automatic follow-on workflow. Preserve the boundary at repeated actionability/prioritization remediation for the locked NWO/ERC/MSCA wedge only.
- **Why**: All blocking findings were closed with reproducible pass evidence, and no unresolved trust-surface, launch-floor, assisted-extraction, broader call-coverage, or generic prompt-tuning work is required for this WF's closure contract.
- **Tradeoff**: Adjacent quality opportunities remain intentionally deferred and must be raised as separate, explicitly scoped WFs if needed.
- **Status**: Approved.

## Date: 2026-03-08 (WF-0068: review quality evaluation loop)

### AD 68.1: Representative proof batch is fixed at 9 snippets with a per-call role matrix
- **WF ID**: WF-0068
- **Context**: PRD v0.1 required representative, failure-seeking coverage across the locked NWO/ERC/MSCA wedge, but it left the minimum batch shape and per-call distribution underspecified.
- **Decision**: Lock the minimum MVP batch to 9 snippets total: exactly 3 snippets per locked call, with one `baseline representative`, one `traceability/specificity stress`, and one `actionability/prioritization stress` snippet per call.
- **Why**: This keeps the loop small enough to run repeatedly while making convenience sampling and silent call omission auditable and fail-closed.
- **Tradeoff**: The evaluator must source and maintain a fuller snippet inventory up front, and one under-supplied call now blocks a proceed recommendation instead of being masked by stronger coverage elsewhere.
- **Status**: Approved.

### AD 68.2: Evaluation outcomes separate mission result from follow-on decision, and follow-on labels stay failure-pattern-based
- **WF ID**: WF-0068
- **Context**: PRD v0.1 described bounded follow-on classes, but solution-type labels like prompt/UI/engine candidates would bias the workflow toward remediation surfaces before the evidence proved which failure pattern actually mattered.
- **Decision**: Use one shared 4-state dimension scale (`pass`, `weak`, `fail`, `insufficient_evidence`), separate batch-level `mission_result` from `follow_on_decision`, and constrain follow-on boundaries to repeated failure patterns or tightly related clusters rather than preselected solution types.
- **Why**: This preserves the evaluation-first contract, prevents hidden prompt/engine/UI planning inside WF-0068, and keeps any next WF grounded in repeated evidence rather than implementation guesses.
- **Tradeoff**: The workflow produces slightly more abstract outputs, so a later remediation WF still needs one extra translation step from failure pattern to implementation surface.
- **Status**: Approved.

### AD 68.3: Proceed recommendations require repeated snippet evidence, and single-call patterns stay call-specific
- **WF ID**: WF-0068
- **Context**: PRD v0.2 tightened follow-on boundaries, but it left the minimum proof for a proceed recommendation implicit enough that Phase 2 could treat a single convincing failure as sufficient evidence for a wedge-level implementation WF.
- **Decision**: Allow `proceed_to_narrow_follow_on_wf` only when the same categorized failure pattern appears in at least 2 reviewed snippets inside the named verification evidence bundle. If that repeated pattern appears only within 1 locked call, the recommended follow-on boundary must be explicitly labeled call-specific and must not claim cross-wedge generality.
- **Why**: This closes the fake-readiness gap between “repeated evidence” and “one persuasive example,” while preserving the narrow locked-wedge proof contract.
- **Tradeoff**: Some plausible follow-on ideas will now resolve to `more_evidence_required` until the batch shows repetition beyond a single anecdotal item.
- **Status**: Approved.

### AD 68.4: Evidence provenance stays replayable, and per-item severity is fixed but subordinate to mission result
- **WF ID**: WF-0068
- **Context**: PRD v0.2 required severity and locator fields, but it did not yet fix the severity scale or make baseline/locator provenance precise enough to prevent Phase 2 from inventing inconsistent evidence semantics or relying on derived labels.
- **Decision**: Record both `app_commit_sha` and `app_branch_ref` in the frozen baseline, require each evidence record to cite a replayable official-call locator rather than a derived label alone, and fix per-item severity to `high`, `medium`, or `low`. This item-level severity captures mission impact for that reviewed pair only and does not replace the batch-level `mission_result`.
- **Why**: This keeps evidence replayable across runs, reduces hidden coupling to prior trust-surface metadata, and prevents task planning from improvising a severity model.
- **Tradeoff**: Reviewers must capture slightly more provenance per record, and future artifacts must preserve the distinction between item severity and batch conclusion.
- **Status**: Approved.

### AD 68.5: WF-0068 closure is evaluation-complete with a bounded follow-on boundary
- **WF ID**: WF-0068
- **Context**: Phase 3 captured and validated the locked-batch evidence bundle, then finalized mission/follow-on decision closure under fail-closed checks.
- **Decision**: Close WF-0068 as evaluation-complete (`mission_result=fail`) with `follow_on_decision=proceed_to_narrow_follow_on_wf` bounded to `actionability_cluster`, preserving the evaluation-only boundary and deferring remediation implementation to a separate WF.
- **Why**: Repeated categorized failures met proceed threshold while staying within the locked NWO/ERC/MSCA wedge and consistent baseline evidence.
- **Tradeoff**: WF-0068 intentionally stops before solution implementation; a follow-on WF is required to convert the boundary into concrete remediation work.
- **Status**: Approved.

## Date: 2026-03-08 (WF-0067: review trust surface closure)

### AD 67.1: Card-level source basis is one backend-resolved official-call label with fail-closed state
- **WF ID**: WF-0067
- **Context**: The brainstorm and PRD require source-basis visibility as a launch-blocking trust surface, but leaving criterion-vs-element precedence unresolved would let Phase 2 produce inconsistent per-call rendering and non-deterministic tests.
- **Decision**: Expose one canonical card-level source-basis surface on review detail: resolve `evaluation element source_hint` first, fall back to `criterion source_hint`, and otherwise return an explicit unavailable or legacy-fallback state rather than synthesized text.
- **Why**: Keeps the trust surface deterministic, authoritative, and testable across the locked representative call set.
- **Tradeoff**: Some lower-priority official context may be hidden when both levels have source hints, but the UI stays concise and Phase 2 avoids per-call branching.
- **Status**: Approved.

### AD 67.2: Supporting-context closure is fail-closed non-inference, not positive-label expansion
- **WF ID**: WF-0067
- **Context**: The current review-detail path still resolves `supporting_context_node_logical_ids` to an empty list, so requiring positive supporting-context labels for MVP would widen Phase 2 into supporting-context semantics expansion.
- **Decision**: Treat positive `supporting context` labels as optional and non-blocking for WF-0067. MVP closure requires only that the UI never infers supporting-context semantics when authoritative metadata is absent and that reviewed/not-reviewed boundaries remain truthful.
- **Why**: Preserves the approved review-detail trust scope and prevents schema/UI polish work from reopening WF-0063/WF-0064 semantics.
- **Tradeoff**: Some representative reviews may ship without a positive supporting-context affordance, but they remain honest about that limitation.
- **Status**: Approved.

### AD 67.3: Boundary-state ownership stays backend-authoritative across BFF and UI seams
- **WF ID**: WF-0067
- **Context**: Audit closure found two drift risks: explicit empty boundary arrays could be treated as "absent" in UI fallback logic, and BFF could recompute `detail_state` instead of preserving backend semantics.
- **Decision**: Treat boundary arrays (`visible_not_reviewed_node_logical_ids`, `no_generated_cards_node_logical_ids`) as authoritative whenever present, including empty arrays; preserve backend `detail_state` verbatim at the BFF seam when supplied, and infer only when absent.
- **Why**: Keeps trust-surface semantics fail-closed and prevents hidden coupling between legacy inference paths and newly explicit backend contract fields.
- **Tradeoff**: Requires stricter seam discipline and explicit regression tests to avoid reintroducing fallback behavior.
- **Status**: Approved.

## Date: 2026-03-08 (WF-0066: peerlens scope lock to NWO/ERC/MSCA)

### AD 66.1: NWO/ERC/MSCA is the permanent product-scope wedge; broader promised-program expansion is not deferred
- **WF ID**: WF-0066
- **Context**: Live planning docs still imply ZonMw or equivalent broader coverage remains planned or launch-critical, while the approved WF-0066 brainstorm locks PeerLens to NWO/ERC/MSCA only and explicitly rejects a "deferred for later" reframing.
- **Decision**: Treat NWO/ERC/MSCA as the permanent product-scope wedge for active planning/docs purposes. Active SSOT, backlog, and memory artifacts must not describe ZonMw or equivalent broader expansion as planned, deferred, or required for launch. Historical artifacts keep their original wording unless they still function as current SSOT.
- **Why**: Prevents future planning from inheriting fake breadth commitments and keeps launch-readiness logic anchored to truthfulness and usefulness within the chosen wedge.
- **Tradeoff**: Older completed artifacts and historical logs will continue to contain broader-coverage language, so live-doc boundaries must stay explicit to avoid provenance cleanup turning into scope drift.
- **Status**: Approved.

## Date: 2026-03-08 (WF-0065: cross-call contract hardening of base review semantics)

### AD 65.1: WF-0065 proof scope is locked to one representative real call per active family
- **WF ID**: WF-0065
- **Context**: The remaining trust gap is not broad feature coverage; it is missing deterministic evidence that base review semantics hold across supported call families without relying on single-call slices or synthetic stand-ins.
- **Decision**: Lock WF-0065 MVP proof scope to exactly three representative calls: `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`. Any widening beyond this 3-call proof set requires an explicit blocker showing the locked representatives are insufficient to expose a material semantic variance.
- **Why**: Preserves the approved narrow trust-hardening scope while still forcing cross-family proof coverage.
- **Tradeoff**: Leaves broader promised-program breadth deferred and requires the chosen representatives to carry a stronger evidence burden.
- **Status**: Approved.

### AD 65.2: Paired boundary parity is semantic and fail-closed, not endpoint-unification work
- **WF ID**: WF-0065
- **Context**: The brainstorm requires proof across `POST /reviews`, `POST /api/structured-review`, `StructuredReviewerService.generate_structured_review_pipeline_v1`, and `pipeline_v1`, but broad interpretation could incorrectly turn Phase 2 into endpoint convergence or force parity where one endpoint does not expose the same contract surface.
- **Decision**: Require semantic parity only for the overlapping base-review contract surfaces that the two endpoints expose today, while also proving service/engine fail-closed invariants. Preserve current DTO/routing differences, and require `QUOTA_EXCEEDED` plus `REVIEWS_DISABLED` to show zero review creation, zero partial persistence, and zero pipeline execution.
- **Why**: Keeps WF-0065 focused on dependable trust-surface semantics instead of broad API redesign, while still preventing fail-open drift from hiding behind boundary responses.
- **Tradeoff**: Phase 2 must be precise about what counts as overlapping semantics per endpoint, and coverage gaps cannot be papered over by treating unmatched surfaces as equivalent.
- **Status**: Approved.

### AD 65.3: WF-0065 proof must follow the actual two-path runtime split, and named gates are API-boundary invariants
- **WF ID**: WF-0065
- **Context**: Phase 1 PRD v0.2 still described `/reviews` as if it shared the structured service seam, and it described `QUOTA_EXCEEDED` / `REVIEWS_DISABLED` as if they existed at a service-entry boundary. In repo reality, `/reviews` flows through `ReviewerService.generate_review`, `/api/structured-review` flows through `StructuredReviewerService.generate_structured_review_pipeline_v1` and `pipeline_v1`, and the named gates live in `backend/main.py` before either service path is invoked.
- **Decision**: Make the runtime proof contract path-specific: prove `/reviews` against `ReviewerService.generate_review`, prove `/api/structured-review` against `StructuredReviewerService.generate_structured_review_pipeline_v1` plus `pipeline_v1`, and attach `QUOTA_EXCEEDED` / `REVIEWS_DISABLED` proof to the API boundary with explicit non-invocation assertions for both downstream service paths.
- **Why**: Removes a planning-layer hallucination, keeps Phase 2 aligned to the actual architecture, and preserves fail-closed evidence requirements without inventing a service gate that the code does not implement.
- **Tradeoff**: Phase 2 must cover one extra explicit service seam and cannot claim gate closure from service tests alone.
- **Status**: Approved.

## Date: 2026-03-08 (WF-0064: opted-in hierarchical submit proof closure)

### AD 64.1: WF-0064 stays fail-closed and primary-only for the MSCA proof path
- **WF ID**: WF-0064
- **Context**: WF-0063 made supporting nodes visible on the opted-in proof path, but that left an unsafe gap: supporting nodes could be edited even though the primary submit/compliance boundary and backend validation intentionally excluded them.
- **Decision**: For WF-0064 MVP, keep supporting nodes visible but non-editable on `MSCA-PF-2025`, do not persist supporting-node answers or add a separate supporting-context request branch, keep `supporting_context_node_logical_ids` empty, and preserve backend primary-path rejection semantics including `SUPPORTING_NODE_NOT_ALLOWED`.
- **Why**: Removes the silent clear-loss trap without broadening persistence or review semantics beyond the approved proof-path scope.
- **Tradeoff**: Researchers cannot author supporting sections in this path yet, but the product remains honest and fail-closed.
- **Status**: Approved.

### AD 64.2: Review-detail honesty derives from visible non-container eligibility, not expectations-only leaves
- **WF ID**: WF-0064
- **Context**: The proof path can still mislead users if review detail derives coverage from `has_expectations` leaves or page-local heuristics, because visible supporting nodes such as `abstract` would disappear or look implicitly reviewed.
- **Decision**: Require review-detail coverage and `Visible but not part of this review` labeling to derive from one authoritative stage-eligible visible non-container classification source shared across the proof path; do not populate `supporting_context_node_logical_ids` in this WF.
- **Why**: Preserves truthful review-detail output while preventing hidden coupling between submit semantics and review-detail rendering.
- **Tradeoff**: Implementation must thread one explicit classification seam instead of letting the page compute its own fallback logic.
- **Status**: Approved.

### AD 64.3: WF-0064 must reuse existing proof-path seams and stay evidence-gated
- **WF ID**: WF-0064
- **Context**: The Phase 1 audit found the PRD correctly required a single authoritative classification source, but the wording still left room for Phase 2 to introduce a new generalized cross-layer abstraction or to treat readiness as implicit rather than evidence-backed.
- **Decision**: Satisfy WF-0064's single-source classification requirement by reusing an existing resolver or normalized BFF output where possible, and do not widen the workflow into a new generalized classification framework. Phase 2 or ship readiness may be recommended only with explicit passing evidence for every required automated check, zero unresolved blocking findings, and closure of non-blocking findings unless explicitly rejected with rationale.
- **Why**: Preserves the narrow `MSCA-PF-2025` proof-path scope and keeps the fail-closed contract enforceable through explicit evidence instead of optimistic interpretation.
- **Tradeoff**: Implementation flexibility is narrower, and readiness claims require a stricter documented evidence bundle.
- **Status**: Approved.

## Date: 2026-03-08 (WF-0063: universal node visibility reviewability)

### AD 63.1: Universal node-role split is opt-in at the call/runtime level for MVP
- **WF ID**: WF-0063
- **Context**: The contract correction needs a new `PRIMARY` versus `SUPPORTING` node-role split, but broad runtime activation would violate the proof-call-first constraint and could silently change behavior for existing expectation-backed calls.
- **Decision**: Add `node_role` to the canonical node contract, but activate split visibility behavior only through an explicit call-level or runtime opt-in seam in MVP. `MSCA-PF-2025` is the proof call; non-opted-in calls preserve current behavior until explicitly migrated.
- **Why**: Preserves repo safety and compatibility boundaries while allowing one real proof call to validate the new contract.
- **Tradeoff**: Introduces one extra rollout seam to manage, but avoids accidental universal behavior flips.
- **Status**: Approved.

### AD 63.2: First-path UI distinguishes structural containers from supporting content
- **WF ID**: WF-0063
- **Context**: Showing all official nodes is necessary for structural fidelity, but a naive “render all supporting nodes as editable” approach could incorrectly turn section containers into answer fields.
- **Decision**: In the first path, structural container nodes remain visible/grouping-only and never editable or submittable. Supporting content nodes may be read/write in draft state, but they remain non-submittable for primary review in MVP.
- **Why**: Preserves official proposal structure in the UI without corrupting submission semantics or confusing containers with content-bearing sections.
- **Tradeoff**: The UI model becomes slightly more explicit, but the resulting semantics are safer and clearer.
- **Status**: Approved.

## Date: 2026-03-07 (WF-0061: real call data expansion single call)

### AD 61.1: WF-0061 must freeze exactly one MVP proof seam for MSCA-PF-2025
- **WF ID**: WF-0061
- **Context**: The brainstorm locked scope to one promised canonical call with one minimal runtime proof, but PRD v0.1 still left the runtime proof surface implicit enough that Phase 2 could broaden into multiple seams.
- **Decision**: Phase 2 must lock exactly one existing product-path seam as the MVP runtime proof surface for `MSCA-PF-2025`. If no single narrow seam is viable without broad redesign, the workflow stops and surfaces that blocker instead of widening scope.
- **Why**: Preserves the one-call/one-proof contract and prevents task generation from turning "operationally real" into cross-surface expansion.
- **Tradeoff**: The selected proof seam may not represent every product surface, but it gives a defensible minimal proof for this WF.
- **Status**: Approved.

### AD 61.2: Ambiguous single-document source coverage fails closed for MSCA-PF-2025
- **WF ID**: WF-0061
- **Context**: The workflow allows planning before uploads, but Phase 3 authoring must remain source-grounded. A nominally comprehensive single document could otherwise be used to weaken the hard upload gate by interpretation.
- **Decision**: Treat the default intake contract as two official source classes for `MSCA-PF-2025` and fail closed whenever one document does not ground both structure and evaluation criteria/elements unambiguously; require supplemental official evidence before substantive authoring continues.
- **Why**: Keeps the upload gate strict in practice, not just in wording, and prevents speculative YAML authoring from slipping through ambiguity.
- **Tradeoff**: May require one extra official source upload even when a single document appears close, but the traceability bar stays defensible.
- **Status**: Approved.

### AD 61.3: Runtime proof must remain ordered-gate and single-surface biased
- **WF ID**: WF-0061
- **Context**: PRD v0.2 locked one proof seam, but it still left room for Phase 2 to treat a wider multi-surface proof path as normal MVP scope or to count proof evidence before earlier gates had passed.
- **Decision**: Require ordered proof gating (`upload -> validate -> ingest -> runtime proof`) for the same canonical artifact, require a minimal proof-evidence bundle, and treat proof seams spanning more than one major product surface as blocker candidates unless proven to be the minimum direct fix for `MSCA-PF-2025`.
- **Why**: Prevents fake progress through out-of-order proof claims or quiet broadening into frontend/backend expansion while preserving a defensible one-call proof bar.
- **Tradeoff**: Narrows acceptable implementation routes further and may force earlier re-scope if the current product path is broader than expected.
- **Status**: Approved.

## Date: 2026-03-06 (WF-0060: ERC StG 2026 contract/UI model correction)

### AD 60.1: ERC StG 2026 canonical contract is leaf-reviewable and container-structural
- **WF ID**: WF-0060
- **Context**: The existing ERC proof-call shape treated `b1` and `b2` as expectation-bearing/editable surfaces even though the official application form presents them as document containers and places `resources_time_commitment` under Part A / Budget.
- **Decision**: Treat `part_a`, `budget`, `part_b`, `b1`, and `b2` as structural-only containers in the canonical ERC StG 2026 contract; only the approved leaf nodes remain input-bearing/reviewable.
- **Why**: Restores source-first correctness and prevents submit, persistence, and review-detail behavior from inheriting container-as-surface distortions.
- **Tradeoff**: Downstream ingestion/runtime, submit, review-detail, and tests must now carry explicit container semantics instead of relying on the simpler WF-0059 proof-call assumptions.
- **Status**: Approved.

### AD 60.2: Legacy WF-0059 container submissions remain ambiguous evidence, not proven leaf coverage
- **WF ID**: WF-0060
- **Context**: Existing reviews may persist deprecated container submitted-node IDs such as `b1` or `b2`, but those IDs do not prove which corrected leaf nodes were actually submitted or reviewed.
- **Decision**: Preserve compatibility for legacy records by rendering explicit compatibility-state semantics, but never auto-expand deprecated container IDs into reviewed leaf coverage without companion proof. In mixed-version records, corrected leaf IDs take precedence for proven coverage.
- **Why**: Avoids false-positive reviewed coverage while keeping legacy review detail readable and traceable during the correction rollout.
- **Tradeoff**: Some historical reviews will show compatibility ambiguity instead of optimistic reviewed coverage, which is stricter but more defensible.
- **Status**: Approved.

## Date: 2026-03-06 (workflow execution contract)

### AD W.1: Phase 2 tasks remain the canonical planning and commit unit; no separate execution-slice artifact
- **Context**: The workflow already enforced atomic Phase 2 tasks, dependency metadata, TDD, and commit-per-task discipline, but Phase 3 still implicitly encouraged one long session to consume the entire task queue.
- **Decision**: Keep the existing phase model and treat the task file as the single authoritative planning artifact. Do not add a new Phase 2.5 or a second "execution slice" artifact type.
- **Why**: Preserves traceability and keeps planning vocabulary stable while addressing the real reliability issue in execution semantics.
- **Tradeoff**: Phase 2 tasks must carry a bit more execution-boundary metadata when long-running implementation risk is material.
- **Status**: Approved.

### AD W.2: Phase 3 continues across tasks by default; only context-bloat/context-drift can auto-stop the run
- **Context**: The previous Phase 3 contract treated several task-level risk signals as automatic stops, but users may reasonably prefer uninterrupted execution in the same chat while those risks remain manageable.
- **Decision**: Phase 3 should continue sequentially across completed tasks by default. Task-plan mismatch, file-surface spillover, verification instability, and `Session boundary after` remain required continuation-risk signals to report, but they do not automatically stop the run. Automatic stop is reserved for material context-bloat or context-drift risk that threatens reasoning quality.
- **Why**: Preserves long-run momentum while still keeping explicit warnings and traceable per-task checkpoints.
- **Tradeoff**: The agent may continue further into a run before stepping back to planning, so warnings must be explicit and concrete to avoid silent drift.
- **Status**: Approved.

### AD W.3: Context-bloat/context-drift stops must warn and hand off with a resume prompt
- **Context**: If context risk is the only automatic stop reason, the stop contract must cover both token-bloat and reasoning-drift cases explicitly.
- **Decision**: When stopping for context-bloat or context-drift risk, the agent must warn explicitly in chat, state whether downstream review/ship steps are blocked, identify the next unfinished task, and print a copy-pasteable resume prompt for a fresh chat/session. Non-stop continuation risks must still be reported as warnings/recommendations in the same chat.
- **Why**: Keeps the runner decisive about the one class of stop that directly threatens output quality while preserving transparency about lesser risks.
- **Tradeoff**: Longer in-chat warning summaries during execution, but fewer unnecessary handoffs.
- **Status**: Approved.

## Date: 2026-03-05 (WF-0056: platform policy live rehearsal)

### AD 56.1: Rehearse apply/rollback on a dedicated branch; verify targets main
- **WF ID**: WF-0056
- **Context**: Apply/rollback mutation is risky if exercised directly on `main` protections; however, live verification of `main` is still required to prove enforcement.
- **Decision**: For MVP, run live `verify` against `main`, but run controlled `apply`/`rollback` rehearsal against a dedicated rehearsal branch (same expected policy surface, branch-specific), with explicit snapshot and evidence artifacts.
- **Why**: Proves the mutation + rollback path end-to-end while minimizing the probability of weakening `main` protections.
- **Tradeoff**: Rehearsal branch semantics may differ slightly from `main` (e.g., required checks event scope), so the walkthrough must explicitly justify parity and note residual risk.
- **Status**: Approved.

### AD 56.2: "Live rehearsal" requires real GitHub mutation, real check-context discovery, and durable evidence
- **WF ID**: WF-0056
- **Context**: Current `apply`/`rollback` flows are static stubs; they can produce evidence JSON without mutating GitHub. Apply preflight also cannot validate check contexts against GitHub today. CI verify does not yet persist evidence as a durable artifact.
- **Decision**: WF-0056 scope explicitly includes implementing live mutation support for apply/rollback (rulesets and/or branch protection), implementing required-check-context discovery for apply preflight (fail-closed), and producing durable evidence artifacts (workflow artifacts preferred).
- **Why**: Without these, "operationalize WF-0055 in the real repo" cannot be proven and governance remains theoretical.
- **Tradeoff**: Increases engineering scope beyond documentation-only operationalization; must be decomposed into safe, reviewable tasks.
- **Status**: Approved.

### AD 56.3: Durable evidence must carry immutable workflow/commit linkage
- **WF ID**: WF-0056
- **Context**: Evidence files without immutable workflow run/job and commit references are hard to audit later and can be disputed as non-live.
- **Decision**: Require `workflow_run_id`, `workflow_job_name`, and `commit_sha` in verify/apply/rollback evidence schema; include `snapshot_id` when mutation/rollback is involved.
- **Why**: Makes the proof chain durable, replayable, and attributable to an exact live run context.
- **Tradeoff**: Slightly tighter schema contract and additional metadata plumbing in evidence generation.
- **Status**: Approved.

### AD 56.4: Apply preflight uses live PR check-run discovery and fails closed
- **WF ID**: WF-0056
- **Context**: Required-check enforcement can deadlock if expected check contexts are not actually emitted as check runs for the rehearsal surface.
- **Decision**: Apply preflight must derive available required-check contexts from live GitHub check-run data and fail with deterministic `missing_required_checks` when any expected context is absent.
- **Why**: Prevents false-success apply rehearsals and avoids introducing unreachable enforcement states.
- **Tradeoff**: Adds dependency on check-run discovery behavior and requires deterministic selection logic.
- **Status**: Approved.

## Date: 2026-03-05 (WF-0055: platform policy enforcement)

### AD 55.1: Enforcement mechanism prefers rulesets with classic branch-protection fallback
- **WF ID**: WF-0055
- **Context**: GitHub rulesets are the preferred modern control surface, but plan gating may forbid rulesets/branch-protection APIs on private repos.
- **Decision**: Implement read/apply using rulesets first; if unavailable/forbidden, fall back to classic branch protection. Evidence must always record which mechanism was used.
- **Why**: Maximizes compatibility while keeping enforcement deterministic and auditable.
- **Tradeoff**: Two policy surfaces must be normalized into one expected representation.
- **Status**: Approved.

### AD 55.2: CI is verify-only; apply/rollback are controlled and non-CI by default
- **WF ID**: WF-0055
- **Context**: CI tokens typically lack admin permissions; auto-mutation is risky and can violate least-privilege.
- **Decision**: Provide verify-only drift detection in CI; controlled apply/rollback are invoked explicitly by an admin (local command as primary surface; optional workflow_dispatch later).
- **Why**: Preserves least-privilege and prevents accidental policy mutation.
- **Tradeoff**: Enforcement requires an explicit admin action when desired state changes or drift occurs.
- **Status**: Approved.

### AD 55.3: Rollback is snapshot-based with in-repo evidence artifacts
- **WF ID**: WF-0055
- **Context**: Safe enforcement needs a deterministic restore path if required checks or toggles block shipping.
- **Decision**: Controlled apply must capture a raw live-policy snapshot sufficient to restore; both verify/apply/rollback write machine-verifiable evidence JSON artifacts in-repo.
- **Why**: Makes rollback operationally straightforward and auditable without UI click paths.
- **Tradeoff**: Evidence artifacts may grow; raw payloads must avoid secrets and remain response-body only.
- **Status**: Approved.

## Date: 2026-03-06 (WF-0057: ops evidence debt closure)

### AD 57.1: "Done" status must be evidence-backed; placeholders are a closure defect
- **WF ID**: WF-0057
- **Context**: The repo can claim workflows are Done in `docs/index.md` while walkthrough evidence remains waived or contains `<pending live run>` placeholders. WF-0056 is marked Done but its walkthrough still has placeholders even though it states stub/static evidence is invalid.
- **Decision**: Treat placeholder or waived runtime evidence as a closure defect. During WF-0057, re-align WF statuses so any workflow with required evidence placeholders is not marked Done until real live-run evidence is recorded, or an explicit waiver is documented with updated constraints and owner sign-off.
- **Why**: Preserves governance traceability; prevents "fake-done" sequencing; makes auditability and operational readiness claims defensible.
- **Tradeoff**: May temporarily downgrade previously "Done" items, which can be uncomfortable but reflects reality and reduces risk.
- **Status**: Approved.

### AD 57.2: WF-0040 evidence debt closes via strict dual-path contract
- **WF ID**: WF-0057
- **Context**: WF-0040 has unresolved runtime-evidence gates (staging/prod observation windows and per-call counts) that may remain unavailable in a given execution environment.
- **Decision**: Close each unresolved WF-0040 gate using one of two explicit paths only: (1) real evidence backfill with reproducible source links/query steps, or (2) refreshed waiver record containing date, waived gates, exact constraint, residual risk, and owner sign-off reference.
- **Why**: Eliminates ambiguous closure claims and keeps evidence-vs-waiver state auditable in docs-only review.
- **Tradeoff**: Adds documentation rigor and can delay closure if owner sign-off metadata is incomplete.
- **Status**: Approved.

### AD 57.3: WF-0040 path selection for this run is waiver refresh with explicit sign-off trace
- **WF ID**: WF-0057
- **Context**: WF-0057 execution requires a single explicit closure mode for WF-0040 before index status semantics can be finalized.
- **Decision**: Select `waiver refresh` for WF-0040 in this run (instead of runtime evidence backfill) and record owner sign-off trace directly in WF-0040 walkthrough + this decision log.
- **Why**: Current execution environment does not provide deterministic staging/prod telemetry windows or reproducible per-call production counts that can be linked from repo docs alone.
- **Tradeoff**: Runtime gates remain waived and must stay visible as residual risk until a dedicated backfill workflow provides reproducible live evidence.
- **Owner sign-off**: Repo owner (chat approval), reference captured in `docs/walkthroughs/completed/walkthrough-WF-0040-structured-pipeline-v1-legacy-retirement.md`.
- **Sign-off date**: 2026-03-06.
- **Alternative not selected**: Runtime evidence backfill was not chosen because telemetry/query access needed to produce reproducible observation-window counts is unavailable in this run context.
- **Status**: Approved.

### AD 57.4: WF-0040 waiver refresh is finalized with explicit waived-gate inventory
- **WF ID**: WF-0057
- **Context**: Task execution now requires WF-0040 runtime gate ambiguity to be fully removed using the selected closure path.
- **Decision**: Finalize WF-0040 as `waiver refresh` with exactly three waived gates recorded: staging runtime window, production runtime window, and per-call minimum production counts.
- **Constraint**: No deterministic telemetry access in this run context for observation-window or production-count extraction.
- **Residual risk**: Runtime gating defects may persist undetected until a dedicated telemetry backfill workflow is completed.
- **Owner sign-off**: Repo owner (chat approval), linked from WF-0040 walkthrough waiver record section.
- **Sign-off date**: 2026-03-06.
- **Status**: Approved.

### AD 57.5: WF-0057 docs-only closure audit is accepted
- **WF ID**: WF-0057
- **Context**: Final task requires a deterministic closure audit proving evidence/waiver/status alignment without tribal knowledge.
- **Decision**: Accept WF-0057 closure audit as `PASS` based on three checks: WF-0056 placeholder removal, WF-0040 single-path runtime gate closure, and docs index status alignment.
- **Reviewer**: Codex (GPT-5) workflow runner.
- **Audit date**: 2026-03-06.
- **Status**: Approved.

### AD 57.6: WF-0056 closure semantics are downgraded to waiver-backed
- **WF ID**: WF-0057
- **Context**: WF-0056 verify/apply evidence is live-linked, but rollback evidence remains failure-state metadata due artifact download/upload path failure.
- **Decision**: Mark WF-0056 as `Done (Waiver-backed)` instead of evidence-backed, with explicit rollback waiver record and residual risk in the WF-0056 walkthrough.
- **Why**: Prevents false-positive closure semantics while preserving traceable live metadata for successful verify/apply runs.
- **Owner sign-off**: Repo owner (chat approval), referenced in WF-0056 rollback waiver record.
- **Sign-off date**: 2026-03-06.
- **Status**: Approved.

## Date: 2026-03-04 (WF-0053: contract boundary governance enforcement)

### AD 53.1: Boundary-governance trigger inventory is explicit and path-mapped
- **WF ID**: WF-0053
- **Context**: Governance coupling can drift if boundary-change detection is heuristic or under-specified.
- **Decision**: Freeze MVP trigger classes to explicit path-mapped surfaces: request-boundary contracts/validators, contract-gate selector/marker surfaces, CI contract-gate wiring, and WF traceability artifacts.
- **Why**: Ensures deterministic trigger behavior and reduces false-negative bypass risk.
- **Tradeoff**: Trigger inventory needs deliberate maintenance when boundary surfaces expand.
- **Status**: Approved.

### AD 53.2: Evidence coupling is fail-closed with three mandatory bundle IDs
- **WF ID**: WF-0053
- **Context**: Boundary-affecting PRs currently rely on reviewer memory for evidence coupling.
- **Decision**: Require `contract_gate_evidence`, `artifact_traceability_evidence`, and `negative_smoke_evidence` for triggered classes; missing any bundle is a deterministic hard fail.
- **Why**: Converts governance policy from advisory practice to machine-checkable merge gate.
- **Tradeoff**: Contributors must supply additional bounded evidence in the same PR.
- **Status**: Approved.

### AD 53.3: Fail-closed semantics require assertion-safe negative CI smoke
- **WF ID**: WF-0053
- **Context**: Policy claims are weak unless a negative path is proven in CI without destabilizing normal runs.
- **Decision**: Use one deterministic assertion-style negative smoke that proves missing-coupling conditions fail with explicit reason codes/messages.
- **Why**: Demonstrates enforceability while keeping CI behavior predictable.
- **Tradeoff**: Adds small ongoing maintenance overhead for smoke fixture/check wiring.
- **Status**: Approved.

### AD 53.4: Governance enforcement scope is PR-gate only; main push remains health verification
- **WF ID**: WF-0053
- **Context**: Running PR-coupled governance evidence checks on `push` to `main` caused post-merge CI failures for follow-up hotfix commits that legitimately lacked same-PR workflow artifacts.
- **Decision**: Scope governance coupling and negative-smoke checks to `pull_request` events only. Keep lint/type/test/contract-marker checks on both PR and push so `main` still has strong health signals.
- **Why**: Preserves strict fail-closed merge gating while avoiding `main` deadlock from non-PR artifact expectations.
- **Tradeoff**: Governance coupling is no longer re-asserted on post-merge push runs; assurance depends on PR gate correctness and branch protection.
- **Status**: Implemented.

## Date: 2026-03-04 (WF-0049: strict snapshot nested schema hardening)

### AD 49.1: Nested request-boundary strictness is active-surface scoped and explicit
- **WF ID**: WF-0049
- **Context**: Top-level strictness exists, but nested extension surfaces still allow ambiguous loose shapes.
- **Decision**: Enforce strict nested models for active request-boundary surfaces (`evaluation_criteria`, `evaluation_elements`, `reviewer_policy`, `prompt_knobs`) and reject unknown nested fields at every modeled level.
- **Why**: Reduces producer drift risk while keeping hardening narrowly scoped to currently used nested surfaces.
- **Tradeoff**: Legacy producer payloads with undeclared nested keys will fail until aligned.
- **Status**: Approved.

### AD 49.2: Digest determinism uses schema-validated projection with explicit-vs-omitted equivalence checks
- **WF ID**: WF-0049
- **Context**: Nested strictness can cause digest drift if defaults/omissions are canonicalized inconsistently.
- **Decision**: Compute digest from schema-validated projection, exclude unset optional nested fields, avoid synthetic defaults, and require tests proving explicit-default vs omitted-optional equivalence where semantics are equivalent.
- **Why**: Preserves deterministic digest behavior and avoids false mismatch regressions for compatible producers.
- **Tradeoff**: Canonicalization constraints reduce flexibility in how nested defaults are introduced.
- **Status**: Approved.

### AD 49.3: Rollout gate is fail-closed with required producer compatibility matrix classes
- **WF ID**: WF-0049
- **Context**: Compatibility evidence without minimum fixture coverage can pass while missing high-risk producer classes.
- **Decision**: Release readiness requires CI pass on required fixture classes (`happy_valid_payload`, `legacy_extra_nested_key`, `nested_type_mismatch`, `omitted_optional_default_equivalence`) with deterministic expected outcomes; gate fails closed on missing/failing required classes.
- **Why**: Makes rollout risk explicit and prevents under-sampled compatibility sign-off.
- **Tradeoff**: Adds fixture maintenance overhead and can delay rollout when producer classes evolve.
- **Status**: Approved.

## Date: 2026-03-04 (WF-0048: Agency/call variability policy contract)

### AD 48.1: Engine boundary is strict `ActivatedCallConfigSnapshotV1` only
- **WF ID**: WF-0048
- **Context**: `call_config_snapshot` was an untyped dict boundary and allowed ad-hoc variability drift.
- **Decision**: Require strict typed `ActivatedCallConfigSnapshotV1` with `schema_version: "v1"` and unknown-field rejection at all levels.
- **Why**: Locks variability to declared surfaces and keeps core execution call-agnostic.
- **Tradeoff**: Existing producers with extra fields will fail until aligned.
- **Status**: Approved.

### AD 48.2: Contract-failure semantics are deterministic with schema-first precedence
- **WF ID**: WF-0048
- **Context**: Mixed schema/digest failures could produce ambiguous or unstable error behavior for integrators.
- **Decision**: Enforce validation order: strict schema first (`MALFORMED_REVIEW_REQUEST`), digest check second (`CALL_CONFIG_DIGEST_MISMATCH`) only after schema success; include stable JSON Pointer field paths and sorted field errors.
- **Why**: Preserves deterministic failure behavior and actionable BFF integration feedback.
- **Tradeoff**: Digest mismatch is intentionally suppressed when schema is invalid.
- **Status**: Approved.

### AD 48.3: Deterministic contract tests are mandatory and task slices are capped at 3 files
- **WF ID**: WF-0048
- **Context**: Contract hardening can sprawl and regress determinism if tests/slices are not constrained.
- **Decision**: Require deterministic contract tests for unknown-field rejection, schema-vs-digest precedence, and replay-stable `PipelineResult.to_dict()`; enforce Phase 3 slices of <=3 files with split dependencies when larger.
- **Why**: Keeps implementation auditable, incremental, and aligned with strict MVP scope.
- **Tradeoff**: More granular task decomposition overhead during implementation.
- **Status**: Approved.

## Date: 2026-03-03 (WF-0045: Base review pipeline v1 call-agnostic core)

### AD 45.1: Six-stage governance contract is locked and call-agnostic
- **WF ID**: WF-0045
- **Context**: The existing runtime has deterministic behavior, but stage boundaries were not frozen as one explicit product-level contract.
- **Decision**: Lock v1.0 base pipeline to six required stages with explicit entry/exit invariants; preserve call variability only through call configuration surfaces.
- **Why**: Prevents hidden call/funder-specific branching and keeps the core reusable across calls.
- **Tradeoff**: Limits near-term flexibility to add ad hoc core stages without starting a new workflow.
- **Status**: Approved.

### AD 45.2: Failure semantics are classed and compatibility-safe
- **WF ID**: WF-0045
- **Context**: Tightening stage governance can accidentally introduce ambiguous or partial failure behavior downstream.
- **Decision**: Freeze failure classes at stage boundaries (`contract-failure`, `execution-failure`) and require deterministic propagation through aggregation with stable compatibility-safe output behavior.
- **Why**: Preserves auditability and deterministic downstream behavior while contracts are formalized.
- **Tradeoff**: Some degraded/best-effort behavior is intentionally disallowed.
- **Status**: Approved.

### AD 45.3: Competitive analysis is explicit out-of-core for v1.0
- **WF ID**: WF-0045
- **Context**: Optional analyses can create scope creep and mutate core semantics if not clearly bounded.
- **Decision**: Keep competitive analysis and other optional modules out of the core v1.0 path; treat them as deferred extension work.
- **Why**: Protects MVP delivery and keeps the base pipeline minimal, deterministic, and call-agnostic.
- **Tradeoff**: Optional insights are deferred to a follow-on workflow.
- **Status**: Approved.

### AD 45.4: Base pipeline contract includes a minimal stable request/response envelope
- **WF ID**: WF-0045
- **Context**: Stage contracts and failure semantics were defined, but envelope-level IO constraints were implicit.
- **Decision**: Add a minimal mandatory request/response envelope contract (`request_id`, `call_config_ref`, `subject_ref`, `pipeline_status`, `failure_code`, ordered diagnostics, compatibility output).
- **Why**: Prevents API-surface drift and makes deterministic contract testing explicit before Phase 2 task breakdown.
- **Tradeoff**: Slightly tighter constraints on implementation flexibility for intermediate payload shaping.
- **Status**: Approved.

### AD 45.5: WF-0045 contract tests require deterministic selector naming
- **WF ID**: WF-0045
- **Context**: Adversarial review found risk of ambiguous/non-repeatable test targeting for core contract checks.
- **Decision**: Require at least one deterministic selector per contract surface using `wf0045_contract_<surface>_<case_id>`.
- **Why**: Keeps Phase 2/3 verification auditable and avoids brittle broad `-k` matching.
- **Tradeoff**: Adds naming discipline overhead during test authoring.
- **Status**: Approved.

## Date: 2026-03-01 (WF-0041: NWO Veni 2025 preproposal single-call MVP)

### AD 41.1: Review detail contract adds generic call identity
- **WF ID**: WF-0041
- **Context**: Review detail UI must remove Veni-only ordering/label hardcoding and order sections by call node `order_index`.
- **Decision**: Extend review detail response generically with `call_id` and `call_code`, then resolve ordered nodes via call metadata instead of per-call frontend constants.
- **Why**: Enables deterministic call-driven ordering/grouping with no per-call maps while keeping single-call MVP scope.
- **Tradeoff**: Adds a small API response expansion that downstream clients must tolerate.
- **Status**: Approved.

### AD 41.2: Domain UX is backend-driven via `domain_options[]`
- **WF ID**: WF-0041
- **Context**: Frontend domain options were maintained in per-call maps, violating no-hardcoding constraints.
- **Decision**: Treat backend metadata/config `domain_options[]` (possibly empty) as the only source for domain selector visibility/options.
- **Why**: Keeps domain behavior call-specific by declaration and removes frontend/backend per-call branching for domain labels/options.
- **Tradeoff**: Requires metadata availability/quality for each supported call context.
- **Status**: Approved.

### AD 41.3: Compliance honesty is deterministic-blocking only
- **WF ID**: WF-0041
- **Context**: Some call constraints are non-enforceable deterministically in plain text, but UX must remain trustworthy.
- **Decision**: Block only deterministic enforceable checks (presence + word limits + domain-aware word limits); show non-enforceable constraints as informational guidance.
- **Why**: Preserves trust by avoiding false-precision blocking while still enforcing clear deterministic constraints.
- **Tradeoff**: Some policy guidance remains advisory until richer parsing/structured inputs are introduced.
- **Status**: Approved.

## Date: 2026-03-01 (WF-0040: Structured pipeline v1 legacy retirement)

### AD 40.1: Legacy retirement scope is execution-path only
- **WF ID**: WF-0040
- **Context**: The codebase uses "legacy" terminology in both engine routing and call-config/UI naming, which risks scope creep.
- **Decision**: Define WF-0040 scope as retiring only the legacy structured-review execution path for `POST /api/structured-review`; non-blocking `legacy_*` naming cleanup is deferred.
- **Why**: Keeps the retirement program falsifiable and avoids accidental expansion into unrelated frontend/call-config refactors.
- **Tradeoff**: Naming ambiguity remains in-place temporarily and must be documented in the runbook/checklist.
- **Status**: Approved.

### AD 40.2: Legacy deletion is checklist-gated with explicit approval checkpoint
- **WF ID**: WF-0040
- **Context**: Deleting legacy code prematurely would remove the pre-deletion rollback option and increase production risk.
- **Decision**: Require a readiness checklist artifact in the WF walkthrough with replay/parity evidence, rollout-health outputs, API contract-test pass evidence, and explicit owner approval before deleting legacy path code.
- **Why**: Preserves reversibility before deletion and forces evidence-based progression to single-engine runtime truth.
- **Tradeoff**: Adds process overhead and can delay deletion if observability evidence is incomplete.
- **Status**: Approved.

### AD 40.3: Deletion gate defaults pin observation windows and production sample-size minimums
- **WF ID**: WF-0040
- **Context**: Open-ended gate durations and traffic-size expectations made readiness decisions ambiguous.
- **Decision**: Freeze MVP gate defaults to 24 consecutive green hours in staging and 7 consecutive green days in production, with minimum 50 completed requests per currently-supported call code before deletion approval.
- **Why**: Makes the retirement gate operationally unambiguous for Phase 2 task planning and execution.
- **Tradeoff**: Low-traffic calls may take longer to satisfy deletion readiness criteria.
- **Status**: Approved.

### AD 40.4: Rollout-health evaluator is the deletion-gate computation surface
- **WF ID**: WF-0040
- **Context**: Gate defaults are only reliable if evaluated by one deterministic computation path.
- **Decision**: Encode staging/prod observation-window and per-call sample-size checks in `backend/scripts/evaluate_rollout_health.py`; deletion readiness evidence must include evaluator output with explicit gate check booleans.
- **Why**: Prevents spreadsheet/manual interpretation drift and keeps approval evidence reproducible.
- **Tradeoff**: Artifact producers must include `retirement_gate` metadata for full gate evaluation.
- **Status**: Approved.

### AD 40.5: `check_id` remains stable taxonomy; validator uniqueness includes expectation identity
- **WF ID**: WF-0040
- **Context**: A temporary fix encoded `expectation_id` into `check_id`, which violated stable taxonomy expectations and downstream grouping assumptions.
- **Decision**: Keep `check_id` taxonomy stable (`check.presence`) and enforce request-snapshot uniqueness on (`expectation_id`, `node_logical_id`, `check_id`) in validator logic.
- **Why**: Preserves cross-call analytical stability while still preventing duplicate expectation identity rows in request snapshots.
- **Tradeoff**: Validator relies on expectation identity for uniqueness rather than `check_id` alone.
- **Status**: Approved.

## Date: 2026-03-01 (WF-0039: Structured pipeline v1 rollout)

### AD 39.1: Production empty-allowlist guardrail fails closed to legacy
- **WF ID**: WF-0039
- **Context**: Existing gating semantics can route all calls to `pipeline_v1` when global flag is on and allowlist is empty, which is unsafe for production rollout.
- **Decision**: In `APP_ENV=prod`, if `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1` and `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES` is empty, route fail-closed to legacy for all calls and emit loud misconfiguration telemetry/logging.
- **Why**: Prevents accidental all-call cutover while preserving service availability.
- **Tradeoff**: Misconfiguration may silently preserve legacy behavior unless alerts are monitored.
- **Status**: Approved.

### AD 39.2: Rollout parity gate is structural parity, not text parity
- **WF ID**: WF-0039
- **Context**: Textual output can vary from LLM non-determinism, but user-facing regressions are mostly structural in card shape and rating semantics.
- **Decision**: Rollout gate compares legacy vs `pipeline_v1` using structural parity only (`ReviewCard` count/order/rating), plus status/error-code stability checks.
- **Why**: Makes rollout verification deterministic and operationally actionable.
- **Tradeoff**: Text-quality regressions are not blocked by this gate and need separate quality checks.
- **Status**: Approved.

### AD 39.3: Minimum replay evidence gate is fixed at 2 payloads x 20 replays
- **WF ID**: WF-0039
- **Context**: Manual smoke checks are too weak for safe allowlist expansion decisions.
- **Decision**: Require automated replay evidence of at least two payload classes (happy + deterministic contract error), each replayed 20 times, with comparator outputs stored as deterministic JSON artifacts.
- **Why**: Provides repeatable evidence for canary expansion/rollback decisions.
- **Tradeoff**: Adds operational test runtime and artifact management overhead.
- **Status**: Approved.

## Date: 2026-02-28 (WF-0038: PeerLens review engine pipeline v1)

### AD 38.1: `DiagnosticFinding v1` schema is trace-first (required traceability/determinism)
- **WF ID**: WF-0038
- **Decision**: `DiagnosticFinding v1` must include required traceability/determinism fields (not optional metadata).
- **Constraints**:
  - Minimum required trace set: `criterion_ref`, `element_ref`, `primary_expectation_ref` (value is the call-defined `expectation_id`), `check_id`, `subject_ref`, plus `call_config_ref` and `engine_ref`.
  - Schema growth gate: add a new top-level field only if it is call-invariant AND cannot be derived from existing fields.
  - `finding_kind` is explicit and required (not inferred from `check_id`).
- **Why**: Researcher trust requires that every finding is defensible, deterministic, and expectation-grounded by construction.
- **Status**: Approved.

### AD 38.2: Interactive Q&A must include options + recommendation
- **WF ID**: WF-0038
- **Decision**: Every interactive Q&A question must include 2–4 explicit options and the assistant’s recommended option (with rationale).
- **Why**: Prevents hidden defaults and forces explicit tradeoffs before architectural commitments.
- **Status**: Approved.

### AD 38.3: WF-tagging discipline for architecture logs
- **WF ID**: WF-0038
- **Decision**: All entries added for this initiative in `docs/logs/decisions.md` and `docs/logs/qa_history.md` must include the WF id tag/header.
- **Why**: Provides a single trace spine and prevents rationale loss across chats.
- **Status**: Approved.

### AD 38.4: Adversarial critique standard is lifecycle-based and includes mitigations
- **WF ID**: WF-0038
- **Decision**: For each decision, adversarial critique must cover 3 risks across: (1) config authoring, (2) runtime execution, (3) downstream consumption/governance, and include a recommended mitigation/guardrail for each risk.
- **Why**: Ensures systematic stress-testing without missing failure modes or leaving risks unowned.
- **Status**: Approved.

### AD 38.5: Call-agnostic pipeline v1 uses a two-pass model
- **WF ID**: WF-0038
- **Decision**: Define pipeline v1 as two-pass: Pass 1 produces normalized observations; Pass 2 maps observations → `DiagnosticFinding v1` (trace-first).
- **Why**: Preserves call-agnostic purity by separating extraction/normalization from expectation-grounded diagnosis.
- **Status**: Approved.

### AD 38.6: Observation v1 is a strict catalog and requires anchors
- **WF ID**: WF-0038
- **Decision**: Pass 1 output (`Observation v1`) uses an engine-defined strict `observation_kind` catalog (no free-form payload-only observations in v1).
- **Constraint**: All observations require anchors (not only content-claim observations).
- **Why**: Enforces determinism and preserves trace-first mapping from observations → findings without silent context loss.
- **Status**: Approved.

### AD 38.7: Findings are single-primary; related refs are trace-only and same-kind
- **WF ID**: WF-0038
- **Decision**: Each `DiagnosticFinding v1` references exactly one `primary_expectation_ref`, with optional `related_expectation_refs[]`.
- **Constraints**:
  - Deterministic aggregation rule: one finding per (`primary_expectation_ref`, `subject_ref`, `check_id`).
  - Only `primary_expectation_ref` drives grouping/counting; related refs are trace-only.
  - `related_expectation_refs[]` must not cross `finding_kind` boundaries in v1.
- **Why**: Keeps findings atomic and defensible while still allowing bounded cross-links without semantic drift.
- **Status**: Approved.

### AD 38.8: `finding_kind` enum is frozen (v1) to call-invariant invariants
- **WF ID**: WF-0038
- **Decision**: Freeze `finding_kind` values (v1) to: `STRUCTURE`, `COMPLIANCE`, `EXPECTATION_SATISFACTION`, `EVIDENCE_SUFFICIENCY`, `ALIGNMENT`, `FEASIBILITY`.
- **Why**: Stable call-agnostic semantics for UI/analytics; prevents call-defined kind drift and pseudo-funder coupling.
- **Status**: Approved.

### AD 38.9: Expectation references are call-defined ids, scoped by `call_config_ref`
- **WF ID**: WF-0038
- **Decision**: Findings reference expectations via call-defined `expectation_id` (string) rather than runtime DB ids; each finding includes a required `call_config_ref`.
- **Constraint**: `call_config_ref` includes both human and digest forms (e.g., `{call_code}@{semver}` + `{digest}`).
- **Why**: Preserves WHAT vs HOW separation and keeps traceability stable-within-version across time.
- **Status**: Approved.

### AD 38.10: Severity + assessment status contract is explicit and non-numeric
- **WF ID**: WF-0038
- **Decision**: Freeze `severity` (v1) to `ERROR`, `WARNING`, `NOTE` (non-numeric); represent not-assessable outcomes per finding via `assessment_status`.
- **Constraint**: `assessment_status` is required (`ASSESSED` | `NOT_ASSESSABLE`); when `NOT_ASSESSABLE`, a reason is required.
- **Why**: Limits coupling/scoring pressure while preserving honest, expectation-grounded diagnostics under missing-context constraints.
- **Status**: Approved.

### AD 38.11: Anchors are typed and mandatory for all findings
- **WF ID**: WF-0038
- **Decision**: Require at least one anchor for every finding, including STRUCTURE/COMPLIANCE.
- **Constraint**: Anchor types include `TEXT_SPAN`, `STRUCTURAL_LOCATOR`, and `DERIVED` (derived anchors still point to a structural locator).
- **Why**: Ensures auditability and traceability even when failures are structural/non-textual.
- **Status**: Approved.

### AD 38.12: Modes are projection-only (filter-only) over a single canonical findings set
- **WF ID**: WF-0038
- **Context**: Modes risk semantic drift (“strict runs fewer checks”) which breaks call-agnostic determinism and auditability.
- **Decision**: Define modes as projection-only over the same computed `DiagnosticFinding v1[]` list:
  - `DIAGNOSTIC` returns the full ordered findings set.
  - `STRICT` returns a deterministic subset by fixed predicate (`severity == ERROR`).
- **Why**: Preserves a single canonical “truth set” per input and makes strict/diagnostic a deterministic view choice, not a different evaluation.
- **Tradeoff**: Strict cannot reduce runtime cost by skipping checks; it only changes what is surfaced downstream.
- **Status**: Approved.

### AD 38.13: `ReviewRequest v1` requires embedding `call_config_snapshot` for replayability
- **WF ID**: WF-0038
- **Context**: Pointer-only call-config references couple replayability to external storage availability and version drift.
- **Decision**: Require `call_config_snapshot` in every `ReviewRequest v1`, with `call_config_ref.digest` matching the snapshot.
- **Why**: Ensures deterministic replay/audit of findings across time with no hidden dependency on config storage state.
- **Tradeoff**: Request payloads are larger; config duplication is accepted for audit safety.
- **Status**: Approved.

### AD 38.14: Deterministic compatibility mapping groups findings into one `ReviewCard` per expectation per subject
- **WF ID**: WF-0038
- **Context**: Current product surface persists `ReviewCard` linked to an expectation; the new engine SSOT output is `DiagnosticFinding v1`.
- **Decision**: Freeze mapping cardinality to exactly one `ReviewCard` per (`subject_ref`, `primary_expectation_ref`), aggregating grouped findings deterministically.
- **Why**: Preserves stable UX and persistence semantics while keeping the engine atomic output trace-first and single-primary.
- **Tradeoff**: Some per-check granularity becomes internal to `feedback_text` rather than separate cards.
- **Status**: Approved.

### AD 38.15: `DiagnosticFinding v1` is the engine SSOT; `ReviewCard` is a compatibility surface (deprecable)
- **WF ID**: WF-0038
- **Context**: The repo currently persists and serves `ReviewCard`, but WF-0038’s universal pipeline is defined to produce `DiagnosticFinding v1` as the atomic output.
- **Decision**: Treat `DiagnosticFinding v1` as the canonical engine output and source of truth for evaluation semantics. Keep `DiagnosticFinding v1 → ReviewCard` mapping as an explicit compatibility adapter only, which may be deprecated in a follow-on workflow once UI/API can consume `DiagnosticFinding v1` directly.
- **Why**: Avoids letting legacy persistence/UI constraints shape the universal engine contracts while still enabling incremental adoption without a big-bang rewrite.
- **Tradeoff**: Temporarily maintains two representations (findings vs cards) and requires governance to prevent “card semantics” from leaking back into engine semantics.
- **Status**: Approved.

### AD 38.16: Contract failures are distinguished from execution failures (no partial results on contract failure)
- **WF ID**: WF-0038
- **Context**: Determinism and auditability collapse if malformed inputs or config mismatches yield partial/ambiguous outputs.
- **Decision**: Define explicit error categories:
  - Contract errors reject the request deterministically with no partial findings/cards (`CALL_CONFIG_DIGEST_MISMATCH`, `MALFORMED_REVIEW_REQUEST`, `EXPECTATION_REF_UNRESOLVABLE`).
  - Execution failures indicate the engine failed despite a valid contract (`ENGINE_EXECUTION_FAILED`, `TIMEOUT`).
- **Why**: Preserves replayability guarantees and prevents downstream consumers from treating partial output as authoritative.
- **Tradeoff**: Some failures become “hard stops” rather than degraded output; this is intentional for trust/audit safety.
- **Status**: Approved.

### AD 38.17: `call_config_ref.digest` canonicalization is `sha256` over canonical JSON of `call_config_snapshot`
- **WF ID**: WF-0038
- **Context**: Replayability depends on a stable, unambiguous digest algorithm.
- **Decision**: Define `call_config_ref.digest` as `sha256` of a canonical JSON serialization of `call_config_snapshot` (UTF-8, stable key ordering, stable list ordering).
- **Why**: Makes digest verification deterministic across environments and prevents “same config, different digest” drift.
- **Tradeoff**: Requires canonicalization discipline in tooling; payloads include snapshot to avoid storage coupling.
- **Status**: Approved.

### AD 38.18: Evidence-gap classification is encoded via engine-defined `check_id` taxonomy (not new finding fields)
- **WF ID**: WF-0038
- **Context**: We need consistent, deterministic classification of common issue types (evidence gaps, misalignment, overclaims, etc.) for downstream consumption and future scoring projection, without expanding the top-level `DiagnosticFinding v1` schema.
- **Decision**: Encode issue classification as an engine-defined, stable `check_id` taxonomy (`{DOMAIN}.{CODE}`), with a bounded starter set. `NOT_ASSESSABLE` remains represented only via `assessment_status` (must not be duplicated as a `check_id` gap code).
- **Why**: Preserves schema growth discipline, keeps semantics call-agnostic, and still provides stable tags for analytics/scoring projection.
- **Tradeoff**: Requires governance over the `check_id` catalog and tests to prevent free-form drift.
- **Status**: Approved.

## Date: 2026-02-28 (WF-0035: Universal form dynamic UI renderer)

### AD 35.1: Frontend render model composes flat nodes ordering + metadata enrichment
- **WF ID**: WF-0035
- **Context**: Existing backend contracts split ordering/identity (`GET /calls/{call_id}/nodes?view=flat`) from UI labels/constraints (`GET /api/public/calls/{call_logical_id}/nodes/metadata`).
- **Decision**: Define frontend render model as the composition of these two inputs; nodes ordering SSOT is flat nodes endpoint, while metadata enriches labels/constraints via `logical_id`.
- **Why**: Avoids adding new backend endpoints while preventing Veni-specific hardcoding in the renderer.
- **Tradeoff**: Frontend must own deterministic merge/fallback logic and handle partial metadata responses.
- **Status**: Approved.

### AD 35.2: Flat-only support hard-blocks nested and missing-logical-id calls in MVP
- **WF ID**: WF-0035
- **Context**: WF-0035 explicitly defers recursion; structured submit payloads require `node_logical_id`.
- **Decision**: Universal form supports a call only when all nodes are flat (`parent_node_id == null`) and have non-empty `logical_id`; otherwise the call is blocked with explicit unsupported/contract-error messaging.
- **Why**: Prevents silent partial rendering and malformed structured-review submissions.
- **Tradeoff**: Some structured calls remain unusable until recursive rendering and/or data-contract fixes ship.
- **Status**: Approved.

### AD 35.3: Keep existing call-gating API pattern with deterministic client guardrails
- **WF ID**: WF-0035
- **Context**: No new backend endpoint is in scope for filtering structured calls at source.
- **Decision**: Gate eligibility client-side using `GET /api/public/calls/{code}/config` per call, with fixed guardrails (max 4 concurrent requests, 4-second timeout, partial-results UX).
- **Why**: Preserves MVP scope while avoiding all-or-nothing failure as call count grows.
- **Tradeoff**: Introduces N+1 request cost and requires robust degraded-state UX.
- **Status**: Approved.

### AD 35.4: Domain handling remains compliance-scoped with interim per-call options mapping
- **WF ID**: WF-0035
- **Context**: Veni compliance depends on domain input, but domain options are not yet delivered via canonical call-definition UI contract.
- **Decision**: Add generic domain picker surface only where configured via interim per-call mapping; pass selected domain to compliance precheck, while keeping structured-review contract unchanged.
- **Why**: Preserves correctness for domain-gated compliance without expanding backend/API scope in WF-0035.
- **Tradeoff**: Domain options are temporarily maintained outside canonical metadata until a follow-on contract WF.
- **Status**: Approved.

## Date: 2026-02-26 (WF-0034: Unify review execution core)

### AD 34.1: Preserve separate external create contracts; share internal execution core
- **WF ID**: WF-0034
- **Context**: `POST /reviews` and `POST /api/structured-review` have different request shapes and persistence semantics but duplicate core execution concerns.
- **Decision**: Keep both external create endpoints stable and extract shared internal execution pipeline seams (policy injection/post-checks, LLM call seam, parse/validate, telemetry seam).
- **Why**: Reduces drift and duplicate fixes without forcing risky contract changes.
- **Tradeoff**: Two adapter/orchestration surfaces remain and require explicit parity tests.
- **Status**: Approved.

### AD 34.2: No-behavior-change parity is per-endpoint baseline, not cross-endpoint equivalence
- **WF ID**: WF-0034
- **Context**: “Shared core” can be misread as making both endpoints behave identically, which would break endpoint-specific semantics.
- **Decision**: Define parity against each endpoint’s existing baseline (error semantics, idempotency behavior, persistence side effects, card rules), not against each other.
- **Why**: Preserves existing client/API expectations while enabling safe internal refactor.
- **Tradeoff**: Shared core design must remain persistence-agnostic and avoid over-normalizing behavior.
- **Status**: Approved.

### AD 34.3: Incremental migration with structured-first adapter flip
- **WF ID**: WF-0034
- **Context**: Big-bang migration across both endpoints increases blast radius and rollback difficulty.
- **Decision**: Migrate incrementally: establish parity tests, introduce shared core seam, flip structured endpoint first, then single-node endpoint.
- **Why**: Structured path has higher complexity and better stress-tests shared-core boundaries first.
- **Tradeoff**: Temporary mixed architecture during migration window.
- **Status**: Approved.

## Date: 2026-02-26 (WF-0033: Data Contract foundation for hierarchical grants)

### AD 33.1: Universal node identity is `logical_id` + DB UUID
- **WF ID**: WF-0033
- **Context**: A universal renderer needs stable, environment-agnostic identifiers, while the backend persists nodes by UUID.
- **Decision**: Expose both `logical_id` (V2) and `id` (UUID) in UI-facing node DTOs. Frontend binds drafts/state by `logical_id`; backend uses UUID for persistence and joins.
- **Why**: Avoids program-specific code and prevents environment drift (UUIDs differ across DBs; `logical_id` is stable across ingest runs).
- **Tradeoff**: Slightly larger payloads and dual-identifier handling for clients.
- **Status**: Approved.

### AD 33.2: Nodes endpoint uses `view=flat|tree` with flat as default
- **WF ID**: WF-0033
- **Context**: Existing clients depend on a flat nodes list; the new universal renderer needs a tree.
- **Decision**: Keep `GET /calls/{call_id}/nodes` as the canonical endpoint and add `view=flat|tree` (default `flat`). Tree view returns roots with nested `children`.
- **Why**: Enables incremental migration while preserving backward compatibility.
- **Tradeoff**: Endpoint has two response shapes; API typing/docs must be explicit.
- **Status**: Approved.

### AD 33.5: Tree source-of-truth uses V2 `parent_logical_id` (canonical JSON) when available
- **WF ID**: WF-0033
- **Context**: The V2 call-definition schema expresses hierarchy via `proposal_nodes[].parent_logical_id` (not nested `children` lists).
- **Decision**: Build tree structure/order from V2 canonical JSON `proposal_nodes` using `id` + `parent_logical_id` and the list order for sibling ordering; use DB adjacency (`parent_node_id`) only as a fallback when no V2 definition is present/valid.
- **Why**: Keeps the hierarchy consistent with the authored call definition while allowing deterministic fallback for legacy calls.
- **Tradeoff**: Requires careful mismatch handling between canonical JSON logical IDs and active DB nodes.
- **Status**: Approved.

### AD 33.3: Metadata DTO is a bulk public route with optional filtering and partial-success semantics
- **WF ID**: WF-0033
- **Context**: UI needs node-specific constraints/rules without fetching heavy metadata up front, and must support lazy hydration.
- **Decision**: Add `GET /api/public/calls/{call_logical_id}/nodes/metadata` sourced from `CallDefinition.canonical_json`, support repeated `node_logical_ids` filters, and return partial success with `unknown_node_logical_ids` when filters include unknown IDs.
- **Why**: Minimizes API surface area while supporting both bulk and progressive loading patterns.
- **Tradeoff**: Consumers must handle a mixed "known + unknown" result set.
- **Status**: Approved.

### AD 33.4: Missing call definition is an explicit error for metadata requests
- **WF ID**: WF-0033
- **Context**: Legacy calls may not have V2 canonical JSON; metadata DTO depends on it.
- **Decision**: If a call lacks a V2 definition, metadata endpoint returns `CALL_DEFINITION_MISSING` (409). Clients should gate behavior via `/api/public/calls/{call_logical_id}/config`.
- **Why**: Prevents silent empty responses that mask configuration problems and simplifies debugging.
- **Tradeoff**: Client must respect the gating endpoint to avoid 409s.
- **Status**: Approved.

## Date: 2026-02-26 (WF-0032: ERC StG 2026 reviewer-policy hardening)

### AD 32.1: Reviewer policy is first-class call-definition data (`reviewer_policy`)
- **WF ID**: WF-0032
- **Context**: Reviewer guidance was captured as notes/compliance hints, but not modeled as enforceable runtime policy.
- **Decision**: Extend V2 call YAML/schema with `reviewer_policy` rules containing stage scope, node scope, enforcement mode, and source hints.
- **Why**: Each funding call has distinct reviewer-policy constraints that must be versioned with evaluation criteria/elements and consumed by runtime.
- **Tradeoff**: Slight schema complexity increase; authoring now requires structured policy fields.
- **Status**: Implemented.

### AD 32.2: Review stage must be explicit API input
- **WF ID**: WF-0032
- **Context**: Inferring Step 1 vs Step 2 from node ID can drift in mixed or future workflows.
- **Decision**: Require `review_stage` (`STEP_1`/`STEP_2`) in `/reviews` and `/api/structured-review`, and reject node/stage mismatches.
- **Why**: Prevents silent scope errors and makes policy enforcement deterministic at request time.
- **Tradeoff**: API clients must send one additional required field.
- **Status**: Implemented.

### AD 32.3: Critical ERC reviewer-policy rules are blocking
- **WF ID**: WF-0032
- **Context**: Warning-only checks allow policy-violating reviewer output to be persisted.
- **Decision**: Promote critical ERC rules (Excellence-only criterion scope, no Step-1 resource judgments) to `BLOCKING`.
- **Why**: These are hard guardrails from official reviewer guidance and should fail-fast instead of degrade silently.
- **Tradeoff**: Some reviews will fail and need regeneration/retry when outputs violate policy.
- **Status**: Implemented.

## Date: 2026-02-28 (WF-0037: NWO Vidi 2025 full proposal call definition)

### AD 37.1: Defer AES-only impact clause until domain gating exists
- **WF ID**: WF-0037
- **Context**: The Call PDF contains an AES-specific impact clause, but the app does not currently select a Vidi domain, so any AES-only element would be evaluated for all submissions.
- **Decision**: Exclude AES-only clause from canonical evaluation criteria/elements until domain selection/branching is introduced.
- **Why**: Prevents incorrect universal evaluation semantics and preserves source-grounded correctness.
- **Tradeoff**: AES-specific nuance is not evaluated until domain gating ships.
- **Status**: Approved.

## Date: 2026-02-28 (WF-0036 branch closure hygiene)

### AD 36.4: WF-0036 merged via direct main merge (no PR), then stale branch deleted
- **WF ID**: WF-0036
- **Context**: WF-0036 artifacts were already marked Done and commits were contained in `main`, but the old WF branch pointer remained on origin, causing closure ambiguity.
- **Decision**: Keep workflow state as Done (no content changes), record that merge path differed from current PR-first policy, and delete stale local/remote WF-0036 branch refs after ancestry verification.
- **Why**: Preserves audit clarity without rewriting history and prevents repeated confusion about whether WF-0036 is still open.
- **Status**: Approved.

### AD 37.2: Keep WF-0037 YAML-only; schema gaps require a follow-on WF
- **WF ID**: WF-0037
- **Context**: During planning we may discover schema needs (domain gating, separate non-evaluable guidance fields).
- **Decision**: No schema/contract changes in WF-0037; if a gap is discovered, stop and promote a dedicated follow-on WF.
- **Why**: Schema changes have high blast radius across ingestion/runtime/tests and must remain explicitly scoped and gated.
- **Tradeoff**: Some desired modeling fidelity is deferred.
- **Status**: Approved.

### AD 37.3: Deadlines store timezone verbatim from sources
- **WF ID**: WF-0037
- **Context**: Deadlines in the call sources use human labels like CET/CEST; conversion/normalization can introduce ambiguity.
- **Decision**: Store `funding_call.deadlines.*.timezone` verbatim as written in the authoritative source document; treat IANA normalization as a follow-on.
- **Why**: Avoids silent conversion errors and preserves legal defensibility.
- **Tradeoff**: Consumers may later need normalization logic.
- **Status**: Approved.

## Date: 2026-02-23 (WF-0030: Local QA/Test DB Isolation Hardening)

### AD 30.1: Dedicated test database is required for DB-backed backend tests
- **WF ID**: WF-0030
- **Context**: Running `backend/tests/test_api.py` against the same `DATABASE_URL` used by local app QA overwrote call-definition projection data, causing false UI regressions (e.g., `academic_profile` dropping to one expectation).
- **Decision**: Enforce a hard safety policy:
  - DB-backed tests must run only when `DATABASE_URL` points to a test database whose name includes `test`.
  - Add pytest guardrails in `backend/tests/conftest.py` to fail fast for unsafe DB URLs.
  - Keep DB-less tests explicitly marked (`@pytest.mark.no_db`) to bypass DB checks safely.
- **Why**: Prevents accidental mutation of the local QA dataset and removes a recurring source of workflow confusion.
- **Tradeoff**: Developers must set `DATABASE_URL` explicitly for backend test runs, which adds one setup step but avoids costly debugging.
- **Status**: Implemented.

### AD 30.2: Separate Docker stacks for dev DB and test DB
- **WF ID**: WF-0030
- **Context**: A single Postgres stack encouraged accidental sharing between manual app testing and test fixtures.
- **Decision**:
  - Keep `backend/docker-compose.dev.yml` for local app development (`grant_reviewer_dev`, port `5432`).
  - Add `backend/docker-compose.test.yml` for backend tests (`grant_reviewer_test`, port `5433`).
- **Why**: Environment-level separation is simpler and more reliable than relying on developer memory.
- **Tradeoff**: Slightly more local setup overhead (one extra compose file), but much safer operationally.
- **Status**: Implemented.

### AD 30.3: Standardized reset scripts for deterministic local state
- **WF ID**: WF-0030
- **Context**: Repeated manual reset sequences were error-prone and inconsistently applied.
- **Decision**:
  - Add `backend/scripts/reset_dev_db.sh` to reset dev DB + ensure active prompt template + ingest canonical Veni definition.
  - Add `backend/scripts/reset_test_db.sh` to reset isolated test DB with safety checks.
- **Why**: One-command recovery reduces mistakes and makes state transitions explicit before QA/test runs.
- **Tradeoff**: Local data is intentionally wiped during reset workflows; this is acceptable for deterministic development.
- **Status**: Implemented.

### AD 30.4: Carry-forward rule for future funding call workflows
- **WF ID**: WF-0030
- **Context**: Additional funding calls will amplify the risk of accidental fixture contamination.
- **Decision**: Treat DB isolation + reset scripts as mandatory preflight for every new funding-call WF before Phase 3 QA.
- **Why**: This preserves reproducibility as multi-call complexity increases.
- **Status**: Approved (always-on policy).

## Date: 2026-02-21 (WF-0021: NWO Veni 2025 preproposal WF-2)

### AD 21.1: 1:1 FundingCall to CallDefinition Relationship
- **WF ID**: WF-0021
- **Context**: The canonical JSONB document needs to link to existing funding calls in the system.
- **Decision**: Introduce a `CallDefinition` table with a 1:1 foreign key to `FundingCall` containing the canonical JSONB.
- **Why**: Keeps the new document storage cleanly separated from the high-level call metadata while enforcing exactly one canonical definition per call.
- **Tradeoff**: Requires an extra join if querying both simultaneously, but read service hydrates this efficiently.
- **Status**: Approved.

### AD 21.2: Mandatory `archived_at IS NULL` Query Filters
- **WF ID**: WF-0021
- **Context**: Re-ingesting calls with missing logical IDs soft-deletes the missing entities. Existing read queries would return these deleted entities and prompt them to the AI or UI.
- **Decision**: Enforce that all application read queries for nodes, criteria, and elements explicitly filter `archived_at IS NULL`.
- **Why**: Safest way to handle dropped YAML sections without destroying historical review data that might reference them (orphan handling).
- **Tradeoff**: High risk of bugs if a query forgets the filter; requires auditing all existing read paths.
- **Status**: Approved.

### AD 21.3: Derive criterion description text for V2 projection
- **WF ID**: WF-0021
- **Context**: V2 `evaluation_criteria` schema does not include a free-text `description`, while the relational projection table requires one.
- **Decision**: Persist a deterministic derived description in projection format: `stage=<stage>; weight_percent=<weight_percent>`.
- **Why**: Preserves V2 metadata in the existing table contract without schema-expansion of `EvaluationCriterion`.
- **Tradeoff**: This is synthesized text, not original narrative guidance; richer criterion-level prose can be added in a future schema revision.
- **Status**: Implemented.
## Date: 2026-02-21 (WF-0022: Workflow System Upgrade)

### AD 22.1: Consolidate Phase 1/2/3 Runners into Universal Parametric Runner
- **WF ID**: WF-0022
- **Context**: The Phase 1, Phase 2, and Phase 3 runners share 90% boilerplate (Part A/B/C logic, trace statements, gates). This causes maintenance debt and file sprawl.
- **Decision**: Replace `phase-1-run-spec.md`, `phase-2-run-prd.md`, and `phase-3-run-task.md` with a single `universal-phase-runner.md` that uses conditional variables for inputs/outputs based on the phase number.
- **Why**: Reduces file sprawl and centralizes the "Runners are Routers" logic so any future structural changes to a phase gate only need to be written once.
- **Tradeoff**: Relies on the AI agent's ability to correctly parse markdown tables/variables to substitute the correct input/output paths for the given phase.
- **Status**: Approved.

## Date: 2026-02-20 (Terminology)

### AD T.1: Standardize on “Evaluation criteria/elements” in product copy
- **Context**: Different funders use different labels (e.g., “Assessment criteria” vs “Evaluation criteria”), and “rubric” is less familiar to many researchers.
- **Decision**: Use **“Evaluation criteria”** and **“Evaluation elements”** consistently across all calls in user-facing copy to reduce confusion. Keep a private/internal note of funder-specific variations for reference only.
- **Notes (variations observed)**: NWO commonly uses “Assessment criteria”; Horizon Europe commonly uses “Evaluation criteria”; some people use “Review criteria”.
- **Status**: Approved.

## Date: 2026-02-21 (WF-0020: NWO Veni 2025 preproposal WF-1)

### AD 20.1: V1 vs V2 call-definition detection by `funding_agency` discriminant
- **WF ID**: WF-0020
- **Context**: Existing V1 call YAML uses `funding_agency.short_name`, while the NWO Veni V2 YAML uses `funding_agency.id`. V2 YAML does not currently declare an explicit schema version.
- **Decision**: Detect schema version via:
  - V1 if `funding_agency.short_name` exists
  - V2 if `funding_agency.id` exists
  - If both/neither exist: fail with a clear error (avoid silent precedence).
- **Why**: Deterministic routing is required to keep existing V1 ingest stable while enabling V2 validation for NWO.
- **Tradeoff**: This is a heuristic, not a formal version field; a future WF may add an explicit `schema_version` key if needed.
- **Status**: Approved.

### AD 20.2: `--dry-run` must run without `DATABASE_URL`
- **WF ID**: WF-0020
- **Context**: `backend/app/db.py` raises at import time if `DATABASE_URL` is unset. Today, `backend/scripts/ingest_call.py` imports DB code at module import time, which blocks dry-run validation on machines without DB configuration.
- **Decision**: Require that the dry-run path validates + prints a summary without importing/initializing DB connectivity code (defer DB imports until the non-dry-run path).
- **Why**: “Validate-only” should be safe, fast, and usable while authoring call YAML without provisioning Postgres.
- **Tradeoff**: Script structure must be slightly refactored (lazy imports) to avoid import-time DB resolution.
- **Status**: Approved.

### AD 20.3: Strict V2 schema (fail on unknown keys) + deterministic JSON summary output
- **WF ID**: WF-0020
- **Context**: Call-definition YAML authoring benefits from catching typos/unknown keys early. Dry-run output must be stable for repeated iteration and troubleshooting.
- **Decision**: Default to forbidding unknown keys in V2 validation, and print a self-describing, deterministic JSON summary in dry-run (include `schema_version` and `source_path`, stable ordering).
- **Why**: Reduces silent drift/typos in YAML and makes it easy to compare runs while editing.
- **Tradeoff**: Adding new YAML fields will require code/schema updates rather than being silently accepted.
- **Status**: Approved.

## Date: 2026-02-18 (WF-0019: Add Loading & Empty States)

### AD 19.1: Frontend-only state UX improvements
- **WF ID**: WF-0019
- **Context**: P1 launch-readiness issue is user confusion in loading/no-data moments, not backend correctness.
- **Decision**: Implement loading and empty-state improvements only in frontend route components and shared UI helpers; no backend/API changes.
- **Why**: Smallest change that addresses user-facing trust issues quickly.
- **Tradeoff**: Reuse of current fetch lifecycle means deeper async-state redesign is deferred.
- **Status**: Approved.

### AD 19.2: Deterministic empty-state CTA behavior
- **WF ID**: WF-0019
- **Context**: Empty states without explicit direction can stall first-time users.
- **Decision**: Every in-scope empty state includes a deterministic next-action CTA (for reviews-empty, CTA targets `/app` start flow).
- **Why**: Prevents dead-end UX and improves first-use onboarding clarity.
- **Tradeoff**: CTA destinations stay minimal; richer context-aware routing is deferred.
- **Status**: Approved.

## Date: 2026-02-18 (WF-0018: Harden Submit Flow UX)

### AD 18.1: Submit-flow hardening without backend/API expansion
- **WF ID**: WF-0018
- **Context**: Current submit-flow trust issues are UX/state-transition problems; adding new backend endpoints would increase scope/risk.
- **Decision**: Keep WF-0018 frontend-focused and reuse existing review/auth contracts with no API changes.
- **Why**: Fastest path to eliminate user confusion before real-user rollout.
- **Tradeoff**: Some observability and deeper state guarantees are deferred to future workflows.
- **Status**: Approved.

### AD 18.2: Canonical restart and redirect targets for submit continuity
- **WF ID**: WF-0018
- **Context**: Ambiguous restart/redirect targets cause dead-end navigation and inconsistent user recovery paths.
- **Decision**: Define deterministic targets for restart (`/app/review/new` or equivalent create-review route) and sign-out public return (`/` unless auth contract requires equivalent canonical public route).
- **Why**: Deterministic routing is required to validate no dead-end submit-flow states.
- **Tradeoff**: If current route contracts differ, task implementation must align names while preserving deterministic target behavior.
- **Status**: Approved.

## Date: 2026-02-18 (Workflow System)

### AD W.1: Add Phase 0 End-to-End Runner
- **Decision**: Introduce `docs/workflow/phase-0-run-start-and-brainstorm.md` to execute Phase `0.0` then `0.1` sequentially in one run.
- **Rationale**: Reduces phase-sequencing errors and makes `run phase 0` consistent with existing end-to-end runners for phases 1-3.
- **Status**: Approved.

## Date: 2026-02-06

### AD 0.1: Recursive Proposal Node Structure
- **Decision**: All hierarchical levels of a grant proposal (Part B, Section 1, Subsection 1.1) will be stored in a single `ProposalNode` table with a reflexive `parent_node_id` foreign key.
- **Rationale**: User confirmed preference for generic hierarchy. Simplifies querying for all children of a section or identifying the full path of a snippet.
- **Status**: Approved.

### AD 0.2: Anonymous User with TTL
- **Decision**: MVP uses `User` records with `is_anonymous = true` and `email = null`. Each record represents one logical session. Records are cascade-deleted after TTL (24-72h).
- **Rationale**: Allows tracking snippets/reviews per session without authentication. Explicit lifecycle for data cleanup.
- **Status**: Approved.

### AD 0.3: Call-Locked Evaluation Criteria
- **Decision**: `EvaluationCriterion` and `EvaluationElement` records are unique to a specific `FundingCall`.
- **Rationale**: Avoids complexity of sharing rubrics across calls where guidance might subtly differ.
- **Status**: Approved.

---

## Date: 2026-02-06 (Stage 1 Clarifications)

### AD 1.1: ReviewCard Links to NodeExpectation
- **Decision**: `ReviewCard.node_expectation_id` references `NodeExpectation`, not `EvaluationElement` directly.
- **Rationale**: Provides full traceability to the specific node+element+strength+intent context. The `NodeExpectation` row contains the `evaluation_intent` and `expectation_strength` that informed the review.
- **Status**: Approved.

### AD 1.2: Dual Guidance Fields
- **Decision**: Two distinct guidance fields exist:
  - `ProposalNode.guidance_text`: *"What the applicant is expected to write here."* (Proposal Context in prompt)
  - `NodeExpectation.guidance_note`: *"What the reviewer should actively look for."* (Evaluation Expectations in prompt)
- **Rationale**: Separates applicant-facing guidance from reviewer-internal criteria. Both feed the AI prompt in different sections.
- **Status**: Approved.

### AD 1.3: PromptTemplate Immutability
- **Decision**: Prompt templates are immutable. Updates create a new row with incremented `version` and `is_active = true`. Old templates are set to `is_active = false`.
- **Rationale**: Ensures every `Review` can be traced back to the exact prompt version used. Critical for auditability.
- **Status**: Approved.

### AD 1.4: Mandatory TTL on ProposalSnippet
- **Decision**: `ProposalSnippet.expires_at` is mandatory. Default TTL is 24 hours (configurable). A background job handles cleanup with cascade delete.
- **Rationale**: Ensures ephemeral data for anonymous MVP. Reduces storage and avoids stale data.
- **Status**: Approved.

---

## Date: 2026-02-06 (Stage 2 Validation)

### AD 2.1: Reject Nodes with Zero Expectations
- **Decision**: If a `ProposalNode` has zero `NodeExpectation` records, the system must reject the review request with error: *"No evaluation criteria defined for this section."*
- **Rationale**: A review without expectations is meaningless. Forces administrators to define criteria before enabling sections for review.
- **Status**: Approved.

### AD 3.1: Tech Stack
- **Decision**: Backend uses **SQLModel** (ORM), **UV** (package manager), **FastAPI** (API framework, for Stage 4+).
- **Rationale**: User preference. SQLModel integrates Pydantic + SQLAlchemy. FastAPI is performant and type-safe.
- **Status**: Approved.

---

## Date: 2026-02-07 (Stage 4 Interface Readiness)

### AD 4.1: Structured Rating on ReviewCards
- **Decision**: Added `ReviewCard.rating` using a `ReviewRating` enum (`CRITICAL`, `WARNING`, `SUCCESS`, `NOTE`).
- **Rationale**: Supports "Traffic Light" indicators in the UI without requiring clients to parse human-readable text. Provides a structured way to sort/filter findings by severity.
- **Status**: Implemented.

### AD 4.2: Async Status and Summaries for Reviews
- **Decision**: Added `Review.status` (`PENDING`, `COMPLETED`, `FAILED`), `Review.overall_summary`, and `Review.overall_rating`.
- **Rationale**: Prepare for asynchronous AI generation logic. The UI can poll for status and display an "Executive Summary" at the top of the review page before the detailed cards.
- **Status**: Implemented.

### AD 4.3: Aggregate Rating Calculation
- **Decision**: The `Review.overall_rating` is calculated as the "maximum severity" of its child `ReviewCard` ratings.
- **Ranking**: `CRITICAL (4) > WARNING (3) > SUCCESS (2) > NOTE (1)`.
- **Rationale**: Ensures the overall review status reflects the most urgent finding found by the AI.
- **Status**: Implemented.

---

## Date: 2026-02-07 (Phase 1: Admin Ingestion)

### AD 5.1: Call Definition as Code (YAML)
- **Decision**: Funding Calls, Rubrics, and Proposal Hierarchies will be defined in a version-controlled YAML file and ingested via a CLI script.
- **Rationale**: Matches the complex recursive structure of the domain. Easier to version and copy-paste than a UI.
- **Status**: Approved.

### AD 5.2: No Admin UI for MVP
- **Decision**: We will NOT build a web-based Admin Dashboard for creating calls/rubrics in the MVP.
- **Rationale**: High development cost for low frequency of use. YAML + CLI is sufficient for technical admins.
- **Status**: Approved.

---

## Date: 2026-02-07 (LLM Integration MVP Scope)

### AD 6.1: Single LLM Call per Review
- **Decision**: One LLM call generates feedback for ALL expectations in a review (not one call per expectation).
- **Rationale**: Simpler, cheaper. Full context in one prompt helps coherence.
- **Status**: Approved.

### AD 6.2: Structured JSON Output
- **Decision**: LLM returns structured JSON with `expectation_id` + `feedback` pairs. Validated via Pydantic schema.
- **Rationale**: Parseable, validatable, traceable to specific NodeExpectations.
- **Status**: Approved.

### AD 6.3: Feedback Only (No Rating from LLM)
- **Decision**: MVP LLM returns text feedback only. Ratings will be a Phase-2 concern.
- **Rationale**: Simplifies prompt design and output parsing for MVP. Rating logic can be added later.
- **Status**: Approved.

### AD 6.4: Static Prompt Template
- **Decision**: Use simple f-string template with variable substitution. No Jinja2, no versioning for MVP.
- **Rationale**: KISS principle. Fast iteration on prompts.
- **Status**: Approved.

### AD 6.5: Store Prompt and Raw Response
- **Decision**: Add `prompt_sent` and `raw_llm_response` fields to `Review` table for debugging.
- **Rationale**: Critical for prompt iteration and debugging malformed outputs.
- **Status**: Approved.

### AD 6.6: Failure Policy (MVP)
- **Decision**: If LLM call fails or returns invalid JSON → `Review.status = FAILED`. No partial ReviewCards. User retries manually.
- **Rationale**: Simple, safe. Production-grade resilience is Phase-2.
- **Status**: Approved.

### AD 6.7: Out of Scope for MVP
- Retries, backoff, rate-limit handling
- Partial results handling
- Cost optimization
- Async workers / horizontal scaling

---

## Date: 2026-02-08 (Task 7.0 FastAPI MVP)

### AD 7.1: Minimal Endpoint Surface
- **Decision**: FastAPI MVP exposes only `GET /health`, `GET /calls`, `GET /calls/{call_id}/nodes`, `POST /reviews`, and `GET /reviews/{review_id}`.
- **Rationale**: Delivers a complete client flow with minimal API area and lower maintenance risk.
- **Status**: Implemented.

### AD 7.2: Canonical API Error Contract
- **Decision**: All non-2xx responses use `{ "error": { "code", "message", "details" } }` with centralized code→status mapping.
- **Rationale**: Keeps frontend handling consistent and avoids semantic drift across handlers.
- **Status**: Implemented.

### AD 7.3: Stub LLM Mode for Verification
- **Decision**: Added `LLM_MODE=stub` for deterministic, schema-valid local reviews without OpenAI calls.
- **Rationale**: Enables frequent, low-cost API verification while preserving production code paths.
- **Status**: Implemented.

---

## Date: 2026-02-08 (Task 8.0 Frontend + Launch Architecture)

### AD 8.1: Next.js Frontend with BFF Pattern (Split Hosting)
- **Decision**: Build the UI and SEO site as a single Next.js app (TS/React) with MDX for articles, using a Backend-for-Frontend pattern: browser talks to Next.js routes; Next.js calls FastAPI server-to-server.
- **Rationale**: Strong SEO + app UX on one site, while keeping LLM-backed FastAPI isolated from browser traffic and simplifying auth (no cross-origin cookie/CORS complexity).
- **Status**: Approved (implementation pending).

### AD 8.2: Login Required + Magic Link Auth + Quotas-First
- **Decision**: Require login to submit reviews. Use magic-link email auth (initially) and enforce free-tier usage quotas before adding payments.
- **Rationale**: Minimizes abuse/cost exposure early while keeping onboarding low-friction and preserving a straightforward upgrade path to Stripe later.
- **Status**: Approved (implementation pending).

### AD 8.3: Managed Postgres for v1
- **Decision**: Use managed Postgres for production v1 (replacing SQLite for deployed environments), and host it close to the backend.
- **Rationale**: Supports auth/session storage, quotas, and future scaling/reliability needs better than SQLite, especially under concurrent LLM traffic and split hosting.
- **Status**: Approved (implementation pending).

### AD 8.4: Clerk for Authentication (MVP)
- **Decision**: Use Clerk for login (magic link) in MVP/v1.
- **Rationale**: Avoids building email delivery + token/session plumbing during MVP while keeping login-required abuse control and a smooth upgrade path to payments later.
- **Status**: Approved (implementation pending).

### AD 8.5: Render Managed Postgres (v1)
- **Decision**: Use Render’s managed Postgres for v1 production database.
- **Rationale**: Consolidates DB ops (backups/availability) and pairs naturally with hosting the FastAPI service on Render.
- **Status**: Superseded by AD 8.15 (Neon).

### AD 8.6: Split Hosting: Vercel (Next.js) + Render (FastAPI + Postgres)
- **Decision**: Host Next.js on Vercel (with Clerk) and host FastAPI + Postgres on Render.
- **Rationale**: Best-in-class DX/SEO for Next.js on Vercel, while isolating long-running LLM requests to a backend host suited for persistent services and managed databases.
- **Status**: Approved (implementation pending).

### AD 8.7: Backend BFF Contract Enforcement (8.0B)
- **Decision**: Protected review routes require a BFF signature (`X-GR-User-Id`, `X-GR-Timestamp`, `X-GR-Signature`) and `POST /reviews` requires `Idempotency-Key`.
- **Rationale**: Prevent direct browser abuse of review-generation endpoints, enforce ownership boundaries, and avoid duplicate LLM spend on retries.
- **Status**: Implemented.

### AD 8.8: Review Failure as Lifecycle State (not API error)
- **Decision**: LLM call/validation/timeout failures persist `Review(status=FAILED)` and return `200` with `{review_id, status:"FAILED"}` instead of 5xx LLM errors.
- **Rationale**: Keeps client behavior state-driven and retry-safe with idempotency while preserving observability in persisted review records.
- **Status**: Implemented.

---

## Date: 2026-02-10 (Task 8.0A Frontend UI)

### AD 8.9: Auto-load `backend/.env` on API startup (Dev Convenience)
- **Decision**: `backend/main.py` loads `backend/.env` on startup when present, without overriding already-set environment variables.
- **Rationale**: Removes a common footgun when running `uvicorn main:app --reload` locally (especially for `BFF_SHARED_SECRET` and `OPENAI_API_KEY`), while keeping production behavior safe (deployments inject env vars; `.env` is not shipped).
- **Status**: Implemented.

---

## Date: 2026-02-12 (Task 8.0C Deployment Wiring - Phase 3)

### AD 8.10: Normalize `DATABASE_URL` for Render Postgres
- **Decision**: Backend DB config normalizes `DATABASE_URL` for SQLAlchemy/psycopg compatibility:
  - `postgres://...` and `postgresql://...` are rewritten to `postgresql+psycopg://...`
  - default query params enforce `sslmode=require` and `connect_timeout=3` when missing
- **Rationale**: Removes provider-specific URL footguns and forces secure, bounded connection behavior for MVP.
- **Status**: Implemented.

### AD 8.11: Readiness check endpoint at `GET /health/db`
- **Decision**: Keep `GET /health` as liveness and add `GET /health/db` that executes a minimal DB ping.
- **Rationale**: Deployment wiring needs a DB-aware health signal; liveness-only checks are insufficient for launch gating.
- **Status**: Implemented.

### AD 8.12: Production bootstrap requires active `PromptTemplate`
- **Decision**: Production bootstrap uses explicit commands:
  1) ensure active prompt template (`scripts/ensure_prompt_template.py`)
  2) ingest at least one real call YAML (`scripts/ingest_call.py ...`)
- **Rationale**: `POST /reviews` requires an active `PromptTemplate`; YAML ingestion alone does not create it.
- **Status**: Implemented.

### AD 8.13: Phase 3 execution order is strict (`8.0C.1` -> readiness hardening -> staged deploy checks)
- **Decision**: Next implementation round must run in this sequence:
  1) provider/env wiring (`8.0C.1`)
  2) readiness failure semantics hardening (explicit `503` on DB-unreachable readiness)
  3) deploy Stage 1 verification in `LLM_MODE=stub`
  4) deploy Stage 2 one-shot verification in `LLM_MODE=openai`
- **Rationale**: Reduces thrash and isolates wiring risk/cost before real LLM verification.
- **Status**: Approved (implementation pending).

### AD 8.14: DB readiness failure should be explicit (`503`) for deploy probes
- **Decision**: Keep `GET /health` as liveness, but ensure DB readiness failures produce a stable `503` response instead of generic uncaught errors.
- **Rationale**: Improves operator signal quality and deployment diagnostics with minimal implementation overhead.
- **Status**: Implemented.

### AD 8.15: DB provider is Neon (not Render Postgres)
- **Decision**: Use Neon for managed Postgres; keep Render for hosting FastAPI.
- **Rationale**: Separates DB provider choice from backend hosting while preserving the existing `DATABASE_URL` integration (Task 8.0C).
- **Status**: Approved.

### AD 8.16: Production default `LLM_MODE=stub` until launch day
- **Decision**: Keep production running with `LLM_MODE=stub` by default until launch day; enable `LLM_MODE=openai` only for explicit verification runs.
- **Rationale**: Minimizes cost/blast radius while infra stabilizes; we already proved one real OpenAI end-to-end run fits within the timeout budget.
- **Status**: Approved.

---

## Date: 2026-02-14 (PeerLens Frontend MVP Decisions)

### AD 9.1: Product name is PeerLens (UI copy + metadata)
- **Decision**: Rename the user-facing product/app to **PeerLens** (keep “Grant Reviewer” as the repo/internal name if convenient).
- **Rationale**: Avoids repeated copy/SEO rework; aligns the MVP with the intended product brand early.
- **Status**: Approved.

### AD 9.2: Signed-out landing demo is static and pre-generated (no backend calls)
- **Decision**: The landing page demo is a **static example switcher** (no user-provided text, no calls to `POST /reviews`).
  - Examples to showcase: `NWO-Veni`, `ERC-Starting`, `MSCA-PF`.
- **Rationale**: Preserves the “login + quotas + BFF boundary” cost-control posture and avoids exposing review generation on the highest-traffic route.
- **Status**: Approved.

### AD 9.3: Data retention promise is “until user deletes” with self-serve deletion
- **Decision**: MVP promise: user proposal snippets are retained **until the user deletes them**, and deletion is **self-serve in the UI**.
- **Rationale**: Matches researcher expectations and reduces reluctance to paste sensitive proposal content.
- **Status**: Approved.

### AD 9.4: Deletion semantics (hard delete review + cards + snippet; no quota refund; no rerun)
- **Decision**: “Delete review” performs a **hard delete** of:
  - the `Review`
  - its `ReviewCard`s
  - the associated proposal snippet text
  - Deletion does **not** refund quota, and deletion ends the results flow (no “rerun from results”).
- **Rationale**: Keeps abuse/cost controls intact and makes the retention promise truthful.
- **Status**: Approved.

### AD 9.5: Review Library is local-only in MVP (device-scoped)
- **Decision**: `/app/reviews` is “Recent reviews on this device” (local storage) and is not account-wide in MVP.
- **Rationale**: Avoids new backend API surface and keeps the MVP focused on the submit → results loop.
- **Status**: Approved.

### AD 9.6: Add minimal `/privacy` page (MVP)
- **Decision**: Ship a minimal `/privacy` page in MVP that states:
  - PeerLens does not use proposal snippets to train its models.
  - Proposal snippets are retained until the user deletes them (self-serve deletion).
  - Minimal operational logs/backups may be retained for up to **30 days**.
- **Rationale**: Researchers expect explicit privacy posture before pasting sensitive proposal text; this keeps copy truthful while allowing operational reality.
- **Status**: Approved.

### AD 9.7: Landing page: remove “Watch Demo”, use text-only trust, privacy-only footer
- **Decision**: The landing page MVP:
  - Removes the secondary “Watch Demo” CTA (single primary CTA only).
  - Uses text-only “Supported calls” (no funder logos).
  - Uses a privacy-only footer (no Terms link in MVP scope).
  - Avoids making detailed privacy/training claims on the landing page; links to `/privacy` for specifics.
- **Rationale**: Reduces implied scope (extra routes/assets) and avoids accidental over-claims while preserving the conversion goal (sign-in).
- **Status**: Approved.

### AD 9.8: Landing demo content is fixed (micro-rewrites + export promise + ERC label)
- **Decision**: Lock the landing page static demo content for MVP:
  - Each tab includes micro-rewrite examples inside suggested fixes (not a separate before/after block).
  - Landing may promise “Export your review” (app feature).
  - Use the label “ERC Starting” (not “StG”).
- **Rationale**: Prevents copy/UI thrash during PRD/tasks and keeps the demo aligned with the sign-in funnel.
- **Status**: Approved.

### AD 9.9: Landing demo tabs use a minimal client component (no vendor deps)
- **Decision**: Implement the landing demo tab switcher as a small `use client` component with local state (no URL state, no third-party tab library).
- **Rationale**: Keeps the landing interactive enough to communicate value while avoiding dependency bloat and reducing performance/accessibility risk.
- **Status**: Approved.

### AD 9.10: MVP “Export your review” means copy/download text (no PDF)
- **Decision**: For MVP, “Export your review” is satisfied by providing a user-visible export action that supports “Copy as text” and/or “Download .txt”. PDF export is explicitly not required for MVP.
- **Rationale**: Keeps the landing copy truthful with minimal implementation effort and low UX risk.
- **Status**: Approved.

### AD 9.11: Delete review endpoint returns `200 { ok: true }` (MVP)
- **Decision**: `DELETE /reviews/{review_id}` returns `200` with JSON `{ "ok": true }` on successful deletion.
- **Rationale**: Simplifies Next.js BFF + UI handling and avoids special-casing `204` parsing behavior in the adapter.
- **Status**: Approved.

---

## Date: 2026-02-15 (Documentation Alignment)

### AD 10.1: Documentation Convergence (Phase 0-4 Alignment)
- **Decision**:
    1.  **Single Source of Truth**: `AGENTS.md` and `docs/workflow/README.md` are the SSOT for Process/Workflow/Git. `GEMINI.md` is restricted to Behavioral Guidelines only.
    2.  **Pipeline Alignment**: All docs now agree on: Phase 0 (Brainstorm) -> Phase 1 (Spec) -> Phase 2 (PRD) -> Phase 3 (Tasks) -> Phase 4 (Impl).
    3.  **Naming Convention**: Enforced `task-` (Singular) filename prefix inside `docs/tasks/` folder.
    4.  **Skills**: Consolidated local project skills into global `~/.agents/skills` and removed `agent-operating-protocol.md`.
- **Rationale**: Eliminates drift between agent instructions and actual workflow rules. Supports parallel agent usage (Antigravity/Codex).
- **Status**: Implemented.

### AD 10.2: “Check Skills First” Habit
- **Decision**: Before starting a new category of work, the agent should check for an existing skill in `~/.agents/skills` (or ask the user to run `ls ~/.agents/skills`) and follow the most relevant `SKILL.md`.
- **Rationale**: Reuses battle-tested workflows and reduces “reinventing” patterns (migrations, a11y, API usage).
- **Status**: Implemented (`AGENTS.md` + Codex/Copilot instructions updated).

### AD 10.3: Tool-Specific Instruction Adapters Live Alongside `AGENTS.md`
- **Decision**: Keep `AGENTS.md` as the SSOT, and allow tool-specific instruction files (like `.github/copilot-instructions.md`) to exist as *adapters* that point tools back to `AGENTS.md`.
- **Rationale**: Different agent tools auto-discover different filenames/locations. Adapters reduce drift by centralizing real rules in `AGENTS.md` while still satisfying each tool’s discovery mechanism.
- **Status**: Implemented (added rationale header to `.github/copilot-instructions.md` and documented the pattern in `docs/reference/README_agent_instructions.md`).

## Date: 2026-02-15 (WF-0010: PeerLens Landing Design Refresh)

### AD 10.4: PeerLens Landing Visual Direction + Palette
- **Decision**: PeerLens landing should feel like a clean journal/institutional site (“ink on paper”), not a startup SaaS.
- **Palette (Ink + Parchment)**:
  - `--background`: `#FCFBF7` (paper)
  - `--foreground`: `#0B1F3B` (ink navy)
  - `--muted-foreground`: `#4B5563`
  - `--surface`: `#F4F2EC`
  - `--surface-muted`: `#EEEAE2`
  - `--border`: `#D6D3C8`
  - `--primary`: `#1F4E79` (institutional blue)
  - `--primary-foreground`: `#FFFFFF`
  - Optional accent (very sparing): `--accent`: `#0F766E` (deep teal) **or** `#A35D2A` (copper)
- **Rules**:
  - Primary color only for clickable actions/links.
  - Accent never for body text; use for small badges/markers only.
  - Maintain WCAG AA contrast for text/controls.
- **Scope**: WF-0010 may tweak landing copy and will update `docs/reference/brand_guidelines.md` to match.
- **Status**: Approved.

### AD 10.5: Backend Ruff MVP Baseline Scope (Task 8.1)
- **Decision**: Adopt a safe backend Ruff baseline in `backend/pyproject.toml` with:
  - `select = ["E4", "E7", "E9", "F", "I", "B", "UP"]`
  - per-file ignore: `"scripts/run_review.py" = ["E402"]`
- **Rationale**: Enables a reliable lint signal with low behavior-change risk by focusing on correctness/import hygiene and avoiding broad strictness families during MVP.
- **Scope note**: CI diff-gating is intentionally deferred to the next guardrails slice (Task 8.2) to keep 8.1 low-risk and mergeable.
- **Status**: Implemented.

### AD 10.6: WF-0010 PRD Execution Guardrails (Landing-Only + Explicit Verification Gate)
- **Decision**: WF-0010 PRD is constrained to landing-surface work only (`/`, landing components, `globals.css`, brand guideline updates) with no backend/auth or `/app/*` behavior changes.
- **Verification Gate**: PRD requires this bundle before implementation close:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run check:seo`
  - `cd frontend && npx next build --webpack`
  - manual keyboard + mobile readability pass on `/`
- **Why**: Keeps the refresh MVP-fast while preserving functional stability and quality.
- **Tradeoff**: Defers conversion instrumentation and proof-asset expansion to a follow-up WF.
- **Status**: Approved.

### AD 10.7: Introduce Serif Heading Layer Alongside Inter
- **Decision**: Introduce a serif heading layer (`Lora`) alongside `Inter` to convey academic authority while preserving UI clarity and readability for dense research content.
- **Typography Architecture**:
  - `Lora` (`600`) for primary large headings and editorial titles.
  - `Inter` for body, navigation, controls, forms, and dense UI.
  - No serif usage in forms, tables, buttons, or long body paragraphs.
- **Scale Update (Lora + Inter pairing)**:
  - `H1` (editorial): `clamp(2.2rem, 3.6vw, 2.95rem)`, `line-height: 1.22`, `600`
  - `H2` (editorial): `clamp(1.55rem, 2.1vw, 1.95rem)`, `line-height: 1.28`, `600`
  - `H3` (default): `clamp(1.2rem, 1.45vw, 1.32rem)`, `line-height: 1.36`, Lora `600`
  - `Body`: Inter `16px`, `line-height: 1.6`
- **Exception Rule**:
  - Dense UI headings may explicitly opt into Inter (`font-sans`) to preserve compact readability.
- **Implementation Notes**:
  - Load both fonts via `next/font/google` and expose CSS variables in `frontend/src/app/layout.tsx`.
  - Map variables in `frontend/src/app/globals.css` and apply heading/body scale from `docs/reference/brand_typography_system.md`.
- **Rationale**: Adds scholarly tone on marketing surfaces without harming legibility or interaction clarity.
- **Status**: Approved.

## Date: 2026-02-15 (WF-0011: Local Postgres Dev DB)

### AD 11.1: Local Postgres blessed path is Docker Compose (`backend/docker-compose.dev.yml`)
- **WF ID**: WF-0011
- **Context**: Local development needs a single reproducible startup contract to reduce SQLite/Postgres drift and onboarding variance.
- **Decision**: Define one blessed local DB startup path using `backend/docker-compose.dev.yml` with `postgres` service, local bind on `localhost:5432`, and local dev persistence volume.
- **Why**: One standard path minimizes setup ambiguity and support overhead while staying MVP-fast.
- **Tradeoff**: Developers without Docker get only brief fallback notes in this WF (no full native setup playbooks).
- **Status**: Approved.

### AD 11.2: Local env safety contract defaults to localhost Postgres (`sslmode=disable`)
- **WF ID**: WF-0011
- **Context**: Current backend normalizer adds Postgres SSL defaults appropriate for hosted providers; local dev needs explicit local connection semantics and protection against accidental Neon usage.
- **Decision**: Local docs/env contract must default `DATABASE_URL` to localhost Postgres with `sslmode=disable`; Neon URLs are explicit opt-in only for local debugging.
- **Why**: Prevents accidental writes to hosted environments and keeps local startup predictable.
- **Tradeoff**: Requires stricter env-profile discipline in local onboarding docs.
- **Status**: Approved.

### AD 11.3: PRD verification gate requires minimum seed thresholds + terminal stub review flow
- **WF ID**: WF-0011
- **Context**: DB connectivity alone is insufficient; local workflow must prove functional readiness for review generation.
- **Decision**: Define readiness as: required seed thresholds met (`prompt_templates >= 1 active`, `funding_calls >= 1`, `proposal_nodes >= 1`) plus one local stub review submission reaching terminal status.
- **Why**: Ensures local Postgres setup is actually usable for app flows, not just reachable.
- **Tradeoff**: Adds a small verification step to local setup before development can proceed.
- **Status**: Approved.

## Date: 2026-02-16 (WF-0011 Follow-up: Postgres-only Runtime)

### AD 11.4: Remove SQLite fallback and require PostgreSQL `DATABASE_URL`
- **WF ID**: WF-0011 (follow-up policy hardening)
- **Context**: Mixed local DB modes (SQLite fallback vs local Postgres) caused confusing count mismatches and reduced confidence in development verification.
- **Decision**: Backend runtime is now PostgreSQL-only. `DATABASE_URL` is required; SQLite fallback behavior has been removed from `backend/app/db.py`.
- **Why**: Single-engine development and production parity reduces ambiguity and speeds iteration/debugging.
- **Tradeoff**: Local startup now depends on Postgres availability; missing `DATABASE_URL` fails fast at app startup.
- **Status**: Implemented.

## Date: 2026-02-16 (WF-0012: Alembic Migration Baseline)

### AD 12.1: Postgres-only Alembic baseline contract with a single root revision
- **WF ID**: WF-0012
- **Context**: The backend needs versioned schema evolution, but currently lacks a migration chain anchor.
- **Decision**: Initialize Alembic for Postgres-only runtime and create exactly one baseline root revision (`down_revision = None`) representing current SQLModel schema state.
- **Why**: Establishes a deterministic migration starting point for all future schema changes.
- **Tradeoff**: Baseline quality depends on careful review of autogenerated migration output before application.
- **Status**: Approved.

### AD 12.2: Baseline immutability + local-only drift recovery guidance
- **WF ID**: WF-0012
- **Context**: Existing developer DBs may drift from baseline assumptions and create confusion during first migration runs.
- **Decision**: Treat committed baseline migration as immutable; for local drift, document recovery via local reset or `alembic stamp` guidance in runbooks (no production automation in this WF).
- **Why**: Keeps migration history trustworthy and avoids rewriting applied revisions.
- **Tradeoff**: Some local environments may require manual cleanup before converging to the baseline.
- **Status**: Approved.

### AD 12.3: Explicit enum type cleanup in baseline downgrade for re-upgrade safety
- **WF ID**: WF-0012
- **Context**: Baseline downgrade left PostgreSQL enum types behind, causing re-upgrade failure (`DuplicateObject` on enum creation).
- **Decision**: Add explicit `DROP TYPE IF EXISTS` statements for workflow enums in baseline migration downgrade.
- **Why**: Ensures baseline migration remains reversible on local Postgres verification cycles.
- **Tradeoff**: Downgrade now assumes enum types are owned by this schema/migration path, which is valid for this baseline.
- **Status**: Implemented.

---

## Date: 2026-02-16 (WF-0014: Review History)

### AD 14.1: Simple Pagination for Reviews List
- **Decision**: `GET /reviews` uses a simple `limit` parameter (default 50, max 100) and no cursor/offset for MVP.
- **Rationale**: User volume is low; complex pagination is premature optimization.
- **Status**: Implemented.

### AD 14.2: Reviews are Server-Side (Overturns AD 9.5)
- **Decision**: "My Reviews" (`/app/reviews`) is backed by a server-side `GET /reviews` endpoint, making history available across devices for authenticated users.
- **Rationale**: User feedback and implementation reality favor persistent, accessible history over device-scoped MVP limitations.
- **Status**: Implemented.

---

## Date: 2026-02-17 (WF-0015: Practices Upgrade)

### AD 15.1: Strict Linting on Legacy Code
- **Decision**: Enforce strict `ruff` + `mypy` on *new* code, but use `per-file-ignores` or configuration excludes for existing legacy violations.
- **Rationale**: Blocking the upgrade on fixing 100% of legacy debt is impractical.
- **Status**: Proposed.

### AD 15.2: CI/CD Tooling Selection
- **Decision**: Use GitHub Actions for CI, `uv` for python management, and `npm` for frontend.
- **Rationale**: Standard, modern stack with excellent caching support. `uv` is significantly faster than pip/poetry.
- **Status**: Proposed.

---

## Date: 2026-02-18 (WF-0017: Auto Polling for Processing Reviews)

### AD 17.1: Bounded client polling with no backend contract changes
- **WF ID**: WF-0017
- **Context**: Users currently need manual refresh while reviews are in `PROCESSING`, but introducing new transport/API surface would expand MVP scope.
- **Decision**: Implement client-side polling every 3 seconds with a 90-second cap using existing review status contracts (`PROCESSING`, `COMPLETED`, `FAILED`) and no backend API changes.
- **Why**: Fastest low-risk path to improve user trust in wait-state behavior before real-user rollout.
- **Tradeoff**: Long-running reviews may still require manual follow-up after the polling cap, and this does not provide real-time push semantics.
- **Status**: Approved.

## Date: 2026-02-22 (WF-0028: Compliance Engine)

### AD 28.1: Deterministic Mandatory Field Definition
- **WF ID**: WF-0028
- **Context**: The V2 DB schema lacks an explicit `mandatory: boolean` flag on proposal nodes. The compliance engine needs a deterministic way to flag missing required text.
- **Decision**: A node is considered mandatory if its `CallDefinition` canonical JSON `content_constraints` block contains a `word_limit` (min or max) OR an explicit `mandatory: true` flag.
- **Why**: Safest heuristic given the current schema. Future YAML ingestion can simply add `mandatory: true` to bypass word-limit heuristics if needed.
- **Tradeoff**: Heuristics are loose; if a real mandatory field has no word limit and no explicit flag in the YAML, it won't be blocked.
- **Status**: Approved.

### AD 28.2: Phase 1.2 Risk Audit Feedback on PRD v0.3
- **WF ID**: WF-0028
- **Context**: Codex adversarial review flagged high risks in the v0.2 PRD draft regarding schema alignment, domain constraints, input structure, and router placement.
- **Decision**:
  1. Removed `mandatory: true` and `word_limit` flat fields, aligning F4 to use V2 schema (`total_word_limit.min_words` or Expectation `MANDATORY` strength).
  2. Made `domain` optional in request payload, enforcing it via 422 only when a call config defines `word_limit_by_domain`.
  3. Added explicit 422 handling for unknown `node_logical_id`s and missing mandatory nodes.
  4. Dropped `max_items` entirely from MVP scope to avoid NLP/fragile parsing heuristics on plain text input.
  5. Affirmed single tokenization strategy for MVP, explicitly ignoring semantic exclusions (e.g. "excludes references").
  6. Clarified routing placement in `main.py` (or explicit refactor action) to prevent architectural drift.
- **Why**: Protects MVP delivery speed by strictly aligning the PRD with database/JSON reality and stripping under-defined parsing heuristics.
- **Tradeoff**: Word counts remain approximate (ignoring semantic rules like "exclude references"); users must manually verify exact lengths against Funder PDFs.
- **Status**: Implemented in PRD v0.3.

## Date: 2026-02-22 (WF-0030: Frontend Structured Form)

### AD 30.1: Universal Form Over Hardcoded Routes
- **WF ID**: WF-0030
- **Context**: The frontend needs to support Veni's 3-node structure, but hardcoding `/app/submit/veni` reduces extensibility for future schemas (like ERC).
- **Decision**: The submit route `/app/submit` dynamically fetches the call schema and renders flat `<textarea>` elements mapped to `ProposalNode`s. Non-text nodes degrade visibly to "Unsupported Input Type". Nested nodes are explicitly unsupported in MVP.
- **Why**: Proves the value of a data-driven UI without over-engineering recursive structure rendering.
- **Tradeoff**: Less custom UI polish per funder, but radically faster ingestion of new calls.
- **Status**: Implemented in PRD v0.2.

### AD 30.2: Purely Local Word Counting
- **WF ID**: WF-0030
- **Context**: Real-time compliance feedback is needed, but bouncing every keystroke to `/api/check-compliance` is wasteful.
- **Decision**: Frontend implements a local JS equivalent of backend's `\s+` regex tokenization for zero-latency UI word counts.
- **Why**: Fastest, cheapest UX.
- **Tradeoff**: Requires developers to keep the JS and Python tokenization logic in perfect sync.
- **Status**: Implemented in PRD v0.2.

### AD 30.3: Client-Side Idempotency via UUID v4
- **WF ID**: WF-0030
- **Context**: Double-clicks during 90-second evaluations waste expensive LLM tokens.
- **Decision**: Frontend generates a UUID v4 session identifier and passes it as `Idempotency-Key` header on submission.
- **Why**: Explicitly maps to the backend draft deduplication contract.
- **Tradeoff**: None. Safe and standard pattern.
- **Status**: Implemented in PRD v0.2.

### AD 30.4: Universal Form + Fail Fast on Nested Nodes
- **WF ID**: WF-0030
- **Context**: PRD v0.2 excluded recursive rendering but kept a dynamic universal form. Actual test fixtures (e.g. ERC) have nested structures.
- **Decision**: Keep the universal dynamic renderer, but strictly fail-fast on any call with nested nodes, presenting a blocking error that the call is unsupported in the current MVP rather than rendering a broken form.
- **Why**: Protects the MVP delivery timeline while still proving the dynamic concept on flat schemas (like Veni).
- **Tradeoff**: Calls with nested structures cannot be supported until P2.
- **Status**: Implemented in PRD v0.3.

### AD 30.5: Backend Node Metadata DTO (`GET /calls/{id}/form-schema`)
- **WF ID**: WF-0030
- **Context**: `/calls/{call_id}/nodes` does not serve `logical_id`, labels, or constraints required to accurately render a dynamic UI form, making frontend logic impossible without hardcoding.
- **Decision**: Add a minimal DTO route for `/calls/{call_id}/form-schema` to serve `logical_id`, labels, and constraints explicitly for form rendering.
- **Why**: Establishes a clean API contract for dynamic UIs rather than forcing the frontend to read raw canonical JSON documents.
- **Tradeoff**: Expands the backend scope slightly to build the new route.
- **Status**: Implemented in PRD v0.3.

### AD 30.6: Enforce Domain String on Client
- **WF ID**: WF-0030
- **Context**: The NWO Veni call has an ENW/Science "pilot" altering word counts.
- **Decision**: The "ENW Toggle" directly specifies the exact backend domain string required by `/api/check-compliance`. The domain is persisted in the local draft and passed explicitly in proxy requests.
- **Why**: Prevents split-brain validation where the client interface counts 500 words, but the backend rejects over 100.
- **Tradeoff**: Minimal constraint mapping required in the Next.js client.
- **Status**: Implemented in PRD v0.3.

### AD 30.7: Revert Universal Form Pivot (Veni-Only Scope)
- **WF ID**: WF-0030
- **Context**: Second Codex adversarial review flagged the "Universal Form" + "New Node Metadata DTO" as high-risk platform work that expands the MVP scope unsafely.
- **Decision**: Revert AD 30.1 and AD 30.5. The WF-0030 MVP will be a hardcoded 3-node Veni form. No dynamic schema fetch. No backend DTO route.
- **Why**: Protects the delivery timeline and guarantees we ship the end-to-end V2 experience quickly. Universal rendering will be tackled in a future, dedicated workflow.
- **Tradeoff**: Adding the next funding call (e.g., ERC) will require a new React component until the universal form is built.
- **Status**: Implemented in PRD v0.4.

### AD 30.8: Explicit 422 Hard Block for Form Submission
- **WF ID**: WF-0030
- **Context**: The "Submit Anyway" bypass modal is designed for 200 OK `errors[]` (compliance warnings). If the payload is completely malformed (e.g., missing mandatory nodes, unknown IDs), the backend returns a 422.
- **Decision**: The frontend must explicitly differentiate handling: Trap 422s to hard-block submission and show the exact error message WITHOUT the bypass modal. Trap 200 `errors[]` to show the bypass modal.
- **Why**: Avoids invalid bypass UX and confusing retry loops.
- **Tradeoff**: None. Strict compliance with backend API design.
- **Status**: Implemented in PRD v0.4.

- Date: 2026-02-25
- WF ID: WF-0031
- Context: PRD generation and risk audit for accessibility pass.
- Decision: Defer automated a11y testing (Playwright) and rely on manual VoiceOver/keyboard verification for MVP.
- Why: Keeps scope tight and focused strictly on the most critical user flows (submission and reviewing results) for launch blocker resolution.
- Tradeoff: Risk of future regressions without automated regression tests, but significantly speeds up time-to-market for the required fix.

## Date: 2026-02-25 (WF-0032: ERC 2026 STG YAML & Hierarchical Ingestion)

### AD 32.1: Hierarchical Modeling via `parent_logical_id` in YAML
- **WF ID**: WF-0032
- **Context**: The ERC 2026 StG call has deep nesting (Parts B1, B2, CV) which our current V2 schema does not map to the database `proposal_node` hierarchy.
- **Decision**: Update `CallDefinitionV2` to support `parent_logical_id` (str) on nodes, which the ingestion script resolves to the DB's `parent_node_id` (UUID). `max_pages` will be stored in `canonical_json` as UI guidance without a DB column schema change.
- **Why**: Keeps the ingestion payload simple and avoids Alembic migration thrash while correctly expanding the schema for hierarchical data.
- **Tradeoff**: Ingestion script must perform topological sorting/two-pass insertion to construct the tree and defend against cycle loops.
- **Status**: Approved in PRD v0.2.

## Date: 2026-03-01 (WF-0040: Structured Pipeline v1 Legacy Retirement)

### AD 40.6: Waiver-Based Workflow Closure for Missing Runtime Evidence
- **WF ID**: WF-0040
- **Context**: WF-0040 implementation and automated verification are complete, but required staging/production observation-window evidence, per-call production counts, and formal owner sign-off artifacts are unavailable in current environment/session.
- **Decision**: Close WF-0040 as a documented waiver-based closure (`Done`) with explicit residual risks, record owner chat approval, and park a mandatory follow-up item to collect real runtime evidence before public-launch hardening/scale commitments.
- **Why**: Preserves delivery momentum while keeping risk/accountability explicit instead of falsely marking unavailable evidence as complete.
- **Tradeoff**: Runtime retirement safety is not fully evidenced yet; this risk remains open until follow-up evidence is captured and reviewed.
- **Status**: Approved (waiver recorded in walkthrough + index closure + parking-lot follow-up).

## Date: 2026-03-01 (WF-0043: NWO Veni 2025 Preproposal Single-Call MVP Hardening)

### AD 43.1: Preserve persistence semantics via explicit failure-boundary split
- **WF ID**: WF-0043
- **Context**: The hardening scope must preserve API error semantics/idempotency and `/app/reviews` persistence behavior without behavior changes.
- **Decision**: Freeze a two-boundary contract:
  - endpoint request/validation errors return API errors and do not persist `Review`
  - post-persistence execution failures keep persisted `ReviewStatus=FAILED` semantics with stable summary conventions
- **Why**: Prevents accidental contract drift while strengthening trust-critical regression coverage.
- **Tradeoff**: Requires explicit fixture/assertion mapping per boundary case.
- **Status**: Approved.

### AD 43.2: Primary hardening surface is structured endpoint; policy seam hardening remains single-snippet
- **WF ID**: WF-0043
- **Context**: Brainstorm scope anchors on `POST /api/structured-review`, but reviewer-policy mode semantics are enforced in the single-snippet seam.
- **Decision**: Keep primary hardening target as `POST /api/structured-review` for call `nwo_veni_2025_preproposal`, and include minimal deterministic policy-mode regression tests in single-snippet seam (`BLOCKING`/`POST_CHECK`/`PROMPT_ONLY`) without changing runtime behavior.
- **Why**: Preserves atomic scope while covering the trust-critical policy regression surface.
- **Tradeoff**: Hardening spans two seams and needs clear fixture partitioning to avoid confusion.
- **Status**: Approved.

### AD 43.3: Use a compact fixture matrix as the canonical WF-0043 regression contract source
- **WF ID**: WF-0043
- **Context**: Existing tests are broad but do not provide a single WF-specific deterministic contract suite.
- **Decision**: Introduce a small fixture matrix (`8-12` cases) as the canonical source for WF-0043 assertions and map each case to HTTP semantics, persistence expectation, and status/summary convention.
- **Why**: Creates a repeatable, fast verification bundle without adding new tooling.
- **Tradeoff**: Case curation is strict; additional long-tail scenarios remain deferred.
- **Status**: Approved.

### AD 43.4: Focused-run contract suite must be explicitly selectable
- **WF ID**: WF-0043
- **Context**: Verification bundle value depends on maintainers being able to run only WF-0043 contract checks quickly and deterministically.
- **Decision**: Require a stable focused-run selection convention (marker/name pattern) for WF-0043 tests, and document it in verification docs.
- **Why**: Keeps pre-merge trust checks fast and reproducible without new tooling.
- **Tradeoff**: Test naming/marker discipline becomes part of maintenance burden.
- **Status**: Approved.

## Date: 2026-03-02 (WF-0044: Source-Gated Call YAML Re-Authoring + ERC CoG Canonical v2 Migration)

### AD 44.1: Enforce call-definition reviewer_policy in structured pipeline v1
- **WF ID**: WF-0044
- **Context**: Call/agency-specific `reviewer_policy` rules are encoded in v2 YAML and are applied in the single-snippet flow (prompt injection + deterministic forbidden-term post-checks). Structured pipeline v1 is currently driven primarily by DB expectations and the engine request snapshot, and does not automatically enforce reviewer_policy.
- **Decision**: Wire call-definition `reviewer_policy` into structured pipeline v1 so structured review outputs honor call/agency-specific reviewer constraints. Apply at least prompt-level guidance, and deterministic enforcement when rules are `POST_CHECK`/`BLOCKING` and have `forbidden_terms`, without breaking existing runtime contracts.
- **Why**: Prevents “policy drift” where agency-specific reviewer instructions exist in YAML but are silently ignored in structured outputs.
- **Tradeoff**: Expands structured pipeline surface; requires careful contract tests to avoid regressions and false blocking.
- **Status**: Approved (Phase 0 decision; implement in Phase 3).

### AD 44.2: Source traceability policy is dual-path + hash with gitignored binaries
- **WF ID**: WF-0044
- **Context**: Official source documents are required for defensible call authoring, but storing binaries in git is out of scope for this workflow.
- **Decision**: For each scoped call, manifests must record both original/external provenance and local copied path under `backend/data/calls/source_files/WF-0044/<call_code>/...`, plus SHA256 and usage metadata; source binaries remain gitignored.
- **Why**: Preserves auditability and reproducibility without adding binary artifacts to repo history.
- **Tradeoff**: Reproduction depends on local/secure artifact retention outside git.
- **Status**: Approved.

### AD 44.3: Structured BLOCKING policy failures are deterministic and no-partial-card
- **WF ID**: WF-0044
- **Context**: Structured pipeline policy wiring requires a contract-safe failure rule when `reviewer_policy` enforcement mode is `BLOCKING`.
- **Decision**: `BLOCKING` violations in structured flow must return a stable failure category and no partial cards; `POST_CHECK` remains warning-only and `PROMPT_ONLY` remains non-blocking prompt guidance.
- **Why**: Keeps trust-critical behavior deterministic and testable across policy modes.
- **Tradeoff**: Strict blocking may reduce degraded-success behavior in violation scenarios.
- **Status**: Approved.

### AD 44.4: Source-file retention lifecycle is temporary-local with hash-first durability
- **WF ID**: WF-0044
- **Context**: Dual-path traceability requires local source copies during authoring, but indefinite local retention is ambiguous.
- **Decision**: Treat `backend/data/calls/source_files/WF-0044/...` as temporary workflow storage: keep through WF completion/review, then move to approved secure storage or purge local copies once manifest hashes/provenance are verified.
- **Why**: Clarifies operational hygiene while preserving reproducible traceability through manifest hashes.
- **Tradeoff**: Future reproductions require secure-storage access when local copies are purged.
- **Status**: Approved.

### AD 44.5: Node-ID changes require explicit governance artifacts
- **WF ID**: WF-0044
- **Context**: Minimal-change re-authoring allows rare `proposal_nodes[*].id` changes when source contradictions force correction, which can break downstream assumptions.
- **Decision**: Any node-ID change must include a WF decision-log reference and explicit old→new ID mapping note in implementation artifacts before merge.
- **Why**: Prevents silent identifier drift and preserves migration traceability for runtime/UI contracts.
- **Tradeoff**: Adds process overhead to rare correction cases.
- **Status**: Approved.

### AD 44.6: WF-0044 policy tests require deterministic selector namespace
- **WF ID**: WF-0044
- **Context**: Contract verification becomes brittle when policy tests are not easily selectable by a stable naming convention.
- **Decision**: Reserve selector namespace `wf0044_policy_<surface>_<case_id>` for WF-0044 policy-contract tests, including no-partial-card assertions for blocking failures.
- **Why**: Keeps verification repeatable and fast for pre-merge checks.
- **Tradeoff**: Requires disciplined naming upkeep in tests.
- **Status**: Approved.

## Date: 2026-03-05 (WF-0054: repo-side CI policy hardening)

### AD 54.1: PR-dependent governance remains pull_request-scoped only
- **WF ID**: WF-0054
- **Context**: Governance checks that rely on PR context/evidence can fail incorrectly on `push` to `main` and deadlock post-merge health runs.
- **Decision**: Keep PR-dependent governance checks explicitly gated to `pull_request`; `push` runs remain limited to push-safe checks.
- **Why**: Preserves deterministic merge-gate enforcement while preventing false failures outside PR context.
- **Tradeoff**: Governance coupling is not re-evaluated on post-merge push runs and depends on PR gate correctness.
- **Status**: Approved.

### AD 54.2: CI policy verification is AST-first with stable governed-step IDs
- **WF ID**: WF-0054
- **Context**: String-level policy assertions are brittle when workflow formatting changes, and renamed steps can silently weaken policy checks.
- **Decision**: Enforce event-scope policy with structural YAML assertions and an explicit governed-step identity inventory; missing/renamed IDs fail deterministically.
- **Why**: Keeps CI-policy tests robust against formatting drift while preserving strict governance traceability.
- **Tradeoff**: Inventory updates require explicit maintenance when governed checks are intentionally renamed or split.
- **Status**: Approved.

### AD 54.3: Branch-protection enforcement stays out of scope with explicit handoff mapping
- **WF ID**: WF-0054
- **Context**: Repo-side CI hardening and GitHub branch protection admin enforcement are related but operationally distinct concerns.
- **Decision**: Keep this WF repo-only and require an explicit check-to-required-check mapping artifact for a follow-on branch-protection WF, without changing admin settings here.
- **Why**: Ships deterministic policy hardening now while preserving a clean boundary for platform-admin enforcement work.
- **Tradeoff**: Full required-check enforcement is deferred until the follow-on WF is completed.
- **Status**: Approved.

## Date: 2026-03-06 (WF-0059: multi-call UX unblocker)

### AD 59.1: WF-0059 scope is locked to one ERC hierarchical proof call
- **WF ID**: WF-0059
- **Context**: The workflow can easily sprawl into universal multi-call redesign if the proof target and acceptance boundary are not fixed early.
- **Decision**: Lock implementation and proof scope to `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml`, preserving Veni parity while limiting in-scope changes to the submit unblocker, review-create invariants, and call-aware review-detail seams required by that path.
- **Why**: Keeps the workflow falsifiable and aligned to the finalized brainstorm's proof obligation.
- **Tradeoff**: Broader multi-call hardening remains deferred after this workflow.
- **Status**: Approved.

### AD 59.2: Proof-path review detail uses explicit call-linked source precedence with no silent fallback
- **WF ID**: WF-0059
- **Context**: Review detail already has partial call-aware seams, but the proof path fails credibility if partially missing linkage silently falls back to Veni-shaped ordering or `submitted_nodes` query-param behavior.
- **Decision**: For proof-call reviews, use stored review node linkage as the source of truth, enrich with fetched call-node metadata for ordering/grouping/labels, and allow legacy fallback only for older or mixed-version reviews with absent call-linked metadata.
- **Why**: Protects traceability and prevents a false-positive "multi-call works" result caused by silent fallback behavior.
- **Tradeoff**: Requires explicit unmapped-state handling and tests instead of relying on permissive fallback behavior.
- **Status**: Approved.

### AD 59.3: WF-0059 submit boundary is the structured-review path, not flat `POST /reviews`
- **WF ID**: WF-0059
- **Context**: The repo's hierarchical submit flow already goes through `/api/bff/structured-review` to `/api/structured-review`, while flat `POST /reviews` remains the legacy single-snippet path.
- **Decision**: Define WF-0059 review-create invariants against the structured-review boundary and preserve that path's idempotency, validation ordering, persistence, and history behavior.
- **Why**: Prevents task planning from targeting the wrong transport and hiding the real integration seam.
- **Tradeoff**: The PRD must distinguish structured-review invariants from legacy flat-review invariants instead of collapsing them into one generic boundary.
- **Status**: Approved.

### AD 59.4: Proof-path coverage summary requires persisted submitted-node coverage data
- **WF ID**: WF-0059
- **Context**: Current review detail coverage summary still depends on the `submitted_nodes` URL query param, and cards-only inference is insufficient because some submitted nodes can legitimately yield zero review cards.
- **Decision**: Require the structured-review flow to persist submitted node logical IDs, or an equivalent persisted review-linked coverage source, and require review detail to compute reviewed/not-reviewed coverage from that persisted source plus call metadata.
- **Why**: Makes proof-path coverage trustworthy and removes closure dependence on URL parameters or card-count assumptions.
- **Tradeoff**: Adds a small persistence/detail-contract expansion that legacy reviews will not have, so explicit fallback handling remains necessary.
- **Status**: Approved.
