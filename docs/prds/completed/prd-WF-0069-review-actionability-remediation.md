<!-- docs/prds/completed/prd-WF-0069-review-actionability-remediation.md -->
# WF-0069 — Review Actionability Remediation

Artifact: prd
Version: v0.3
Status: Completed
Last Updated: 2026-03-09

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher reviewing a snippet inside the locked NWO/ERC/MSCA wedge, I want review output to tell me the most important next revision move first, so that I can act on the feedback rather than decode flat status text.
- US2: As a maintainer closing the WF-0068 follow-on, I want the remediation scope locked to the repeated `actionability_prioritization_stress` failure only, so that this WF does not widen into trust-surface, launch-floor, extraction, or broader quality work.
- US3: As an engineer implementing the fix, I want the minimum backend/output contract that can carry actionable and prioritized revision guidance, so that Phase 2 can localize changes to the narrowest defensible seam.
- US4: As a release owner deciding whether the remediation is complete, I want deterministic replay evidence against the exact WF-0068 stress items plus fail-closed guards, so that closure is based on repeated proof rather than improved-looking prose.

## Deferred Stories (Not in MVP)

- DS1: Broader review-quality improvements outside the repeated actionability/prioritization failure.
- DS2: Launch-floor operations, rollout telemetry, or generalized launch-readiness proof.
- DS3: Broader trust-surface/review-detail work beyond the minimum exposure needed to render already-approved remediation semantics truthfully.
- DS4: Assisted extraction, broader context capture, wider call coverage, or repo-wide prompt tuning.

## 1. In Scope

- Remediate only the repeated WF-0068 `actionability_prioritization_stress` failure pattern across `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`. (US1, US2, US4)
- Define the minimum engine-to-output contract changes needed for review output to express a concrete revision move and defensible priority ordering for a reviewed snippet. (US1, US3)
- Keep scope centered on the most likely backend seams already implicated by the brainstorm repo snapshot, especially evaluator/card-mapping/pipeline contract surfaces, with prompt or downstream exposure changes allowed only if proven necessary to carry the new semantics truthfully. (US2, US3)
- Reuse the existing WF-0068 evidence bundle and named item IDs as the primary remediation verification path. (US2, US4)
- Require fail-closed behavior for missing-context and insufficient-evidence states so remediation never fabricates advice. (US1, US4)

## 2. Out of Scope

- Reopening WF-0067 trust-surface goals as an independent workstream or broadening into general review-detail polish. (DS3)
- Launch-floor operations, rollout readiness, continuous monitoring, or generalized ship criteria beyond the narrow remediation gate. (DS2)
- Assisted extraction, broader proposal-context capture, submit-flow redesign, or wider review-system UX work. (DS4)
- New funding-program support or expansion beyond the locked NWO/ERC/MSCA wedge. (DS4)
- Generic prompt tuning, model swapping, or repo-wide wording cleanup divorced from the bounded actionability contract failure. (DS1, DS4)

## 3. User / System Flow

### Happy path

1. A researcher submits or views a snippet review for one of the locked NWO/ERC/MSCA calls, and the review pipeline produces finding-level semantics strong enough to express a concrete next revision move for that snippet. (US1, US3)
2. The remediation seam preserves at least one explicit actionable revision directive plus enough relative priority semantics to identify which revision move should be addressed first. (US1, US3)
3. The compatibility/output mapping layer converts those semantics into researcher-facing review cards without collapsing them back into flat `NOTE` or status-like text. (US1, US3)
4. If the evidence supports multiple revision moves for the same snippet, the highest-priority move is surfaced ahead of lower-value comments in a way that remains traceable to the same reviewed content. (US1, US3)
5. If the system lacks enough context to support actionable advice, the output remains explicitly fail-closed instead of inventing unsupported guidance. (US1, US4)
6. Maintainers replay the exact three WF-0068 stress items and confirm both `revision_actionability` and `prioritization_quality` now pass under one frozen remediation baseline while the locked wedge and fail-closed guards remain intact. (US2, US4)

### Failure path A — wording improves but no real next move

1. The remediation produces longer or more polished feedback, but the card still does not tell the researcher what to revise next. (US1, US4)
2. The WF-0068 stress items would continue to fail `revision_actionability` even if prose looks better. (US1, US4)
3. The workflow remains blocked because verbosity is not an acceptable substitute for actionable revision guidance. (US1, US4)

### Failure path B — advice exists but ordering is still weak

1. A snippet receives multiple plausible revision suggestions, but the contract does not preserve which issue should be fixed first. (US1, US3, US4)
2. The output may contain actionable text while still failing the WF-0068 prioritization boundary. (US1, US4)
3. The workflow remains blocked until priority semantics survive through the changed output seam. (US1, US3, US4)

### Failure path C — remediation widens beyond the approved boundary

1. Implementation planning starts bundling trust-surface expansion, assisted extraction, broader call support, or generic prompt tuning into the actionability fix. (US2, US3)
2. The WF would lose traceability to AD 68.5 and the approved brainstorm boundary. (US2, US4)
3. The workflow must fail closed and re-scope back to the smallest contract required for the repeated actionability/prioritization failure only. (US2, US3, US4)

## 4. Functional Requirements

- FR1 (US1, US3): The remediation must introduce or preserve a review-output contract that can represent at least one concrete next revision move for each targeted stress-case snippet.
- FR2 (US1, US3): The remediation contract must preserve defensible priority semantics across findings for the same snippet so the highest-value revision move can be surfaced ahead of lower-priority comments.
- FR3 (US1, US4): Missing-context, unsupported, or insufficient-evidence states must remain explicit and must not be converted into fabricated actionable advice.
- FR4 (US2, US3): Phase 2 planning must bias first toward evaluator/pipeline/review-card contract seams already implicated by the repo snapshot and may include prompt or downstream exposure changes only when the contract-level seam alone cannot satisfy FR1-FR3 truthfully.
- FR5 (US2): Scope remains locked to `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`; no broader call coverage may be introduced or implied.
- FR6 (US2): This WF must not bundle launch-floor operations, broader trust-surface work, assisted extraction, broader context capture, or generic prompt tuning.
- FR7 (US4): Closure requires deterministic replay of `wf0068_nwo_actionability_prioritization_stress`, `wf0068_erc_actionability_prioritization_stress`, and `wf0068_msca_actionability_prioritization_stress` under one frozen remediation baseline.
- FR8 (US4): Each targeted stress item must pass both `revision_actionability` and `prioritization_quality` before WF-0069 can recommend proceed or ship.
- FR9 (US4): Representative baseline items `wf0068_nwo_baseline_representative`, `wf0068_erc_baseline_representative`, and `wf0068_msca_baseline_representative` must not regress below their current WF-0068 `weak` judgments on the same two dimensions.
- FR10 (US4): Closure evidence must include a fail-closed guard proving missing-context and insufficient-evidence outputs remain truthful after remediation.
- FR11 (US2, US4): Closure evidence must include a scope proof anchored to the frozen remediation baseline SHA or explicit commit range, proving that only justified remediation seams changed and that the locked wedge remained NWO/ERC/MSCA only.
- FR12 (US3, US4): If downstream API/BFF/render seams are changed to expose the new semantics, matching contract/render regression tests become mandatory; otherwise those seams remain untouched.
- FR13 (US1, US3, US4): The minimum remediation contract must distinguish between `actionable highest-priority revision`, `actionable lower-priority revision`, and explicit fail-closed non-actionable states strongly enough that the targeted stress outputs cannot collapse back into generic `NOTE`/`content_evaluated`-style feedback without failing tests or replay checks.
- FR14 (US4): No ship, proceed, or phase-advance recommendation is valid unless every blocking finding is closed and every justified non-blocking finding is either closed or explicitly rejected with rationale in the closure artifact.

## 5. Data & API Contracts

### 5.1 Actionability remediation contract

- The minimum changed contract must preserve, for each targeted actionable finding or card:
  - a concrete revision move or equivalent actionable directive,
  - enough rationale or finding linkage to explain why that move is warranted,
  - enough priority semantics to distinguish the first fix from lower-priority comments for the same snippet. (US1, US3, FR1, FR2)
- The minimum changed contract must make three states testable at the chosen public seam:
  - actionable highest-priority revision guidance,
  - actionable lower-priority or deferred revision guidance,
  - fail-closed non-actionable output caused by missing context or insufficient evidence. (US1, US3, US4, FR1-FR3, FR13)
- The contract does not need to prescribe final field names in Phase 1, but it must be explicit that plain free-text summary strings alone are insufficient if they cannot reliably carry actionable move plus priority semantics through the chosen seam. (US3, FR1, FR2)
- Any fail-closed state must remain distinguishable from normal actionable output and must preserve why actionability could not be provided. (US1, US4, FR3, FR10)

### 5.2 Verification evidence contract

- The remediation closure bundle must name:
  - the frozen remediation baseline identifier,
  - the exact WF-0068 item IDs replayed,
  - the deterministic test and/or replay commands used,
  - per-item pass/fail on `revision_actionability` and `prioritization_quality`,
  - baseline-regression guard results,
  - fail-closed guard results,
  - a baseline-anchored scope-proof file list,
  - an audit-disposition ledger covering blocking and non-blocking findings/comments. (US4, FR7-FR14)
- The approved evidence sources remain the WF-0068 artifacts:
  - `docs/walkthroughs/evidence/WF-0068/batch-summary.json`
  - `docs/walkthroughs/evidence/WF-0068/evidence-records.json`
  - `docs/walkthroughs/evidence/WF-0068/raw-review-outputs.json` when raw-output replay is needed. (US2, US4, FR7-FR11)

### 5.3 Validation rules

- A candidate remediation is invalid if it only improves wording polish without making the next revision move materially clearer for the targeted items. (US1, US4, FR1, FR8)
- A candidate remediation is invalid if it produces actionable text but still cannot defend the ordering of multiple revision moves for the same snippet. (US1, US3, US4, FR2, FR8)
- A candidate remediation is invalid if it replaces `missing_context:*`, insufficient-evidence, or equivalent fail-closed states with invented advice. (US1, US4, FR3, FR10)
- A candidate remediation is invalid if the implementation or evidence bundle widens into broader trust-surface, launch-floor, assisted-extraction, or call-expansion work. (US2, US4, FR5, FR6, FR11)
- A candidate remediation is invalid if the targeted stress outputs still flatten into generic `NOTE`, `content_evaluated`, or equivalent status-like output shapes that do not encode explicit revision move plus priority state. (US1, US3, US4, FR1, FR2, FR13)

### 5.4 State transitions

- `Draft` means the PRD defines the bounded remediation problem, minimum contract, and closure proof shape, but has not yet absorbed audit hardening. (US2, US4)
- `Ready for Tasks` means the PRD locks the minimum remediation contract, fail-closed scope boundary, and deterministic closure evidence strongly enough that Phase 2 can decompose work without reopening scope. (US2, US3, US4, FR1-FR14)

## 6. Components / Modules

- `backend/app/engine/findings/evaluator.py`
  - Primary suspected seam for preserving richer finding semantics that can support actionable revision guidance and priority ordering. (FR1, FR2, FR4)
- `backend/app/engine/compat/review_card_mapper.py`
  - Primary compatibility seam at risk of collapsing richer findings back into flat review-card text. (FR1, FR2, FR4)
- `backend/app/engine/pipeline_v1.py`
  - Frozen baseline execution path implicated by WF-0068; likely orchestration seam for preserving the remediation contract through pipeline assembly. (FR4, FR7)
- `backend/app/engine/contracts.py`
  - Likely contract-definition seam if explicit actionability/prioritization fields are required. (FR1, FR2, FR4)
- `backend/app/services/structured_reviewer_service.py`
  - Secondary service seam if structured review assembly currently drops or flattens the needed semantics. (FR1, FR2, FR4)
- Conditional-only seams:
  - `backend/app/services/prompt_builder.py` or equivalent reviewer-policy path, only if backend contract tightening alone cannot satisfy FR1-FR3. (FR4)
  - downstream API/BFF/render seams, only if changed semantics cannot otherwise reach the researcher truthfully. (FR12)

Design tree / dependencies / ordering:
1. Lock the repeated failure boundary to the three named WF-0068 stress items before selecting an implementation seam. (FR5, FR7, FR8)
2. Identify the narrowest backend/output seam that can preserve actionable move plus priority semantics without fabricating unsupported advice. (FR1-FR4)
3. Add the minimum regression and replay proof needed to demonstrate the chosen seam closes the repeated failure and preserves fail-closed behavior. (FR7-FR10)
4. Only if the semantics cannot reach the user truthfully through existing downstream surfaces, add the smallest required exposure seam plus matching tests. (FR4, FR12)
5. Prove no broader wedge or workflow scope was bundled into the remediation slice. (FR5, FR6, FR11)

Deep module guidance:

- Treat actionability and prioritization as a coupled contract unless implementation evidence proves they can be separated without weakening closure.
- Prefer structured semantics over richer prose if prose-only improvements cannot be validated deterministically.
- Keep fail-closed states first-class; absence of enough evidence is an allowed truthful result.
- Preserve compatibility behavior only insofar as it does not erase the new actionable/prioritized semantics.
- Keep the public remediation seam small and traceable; Phase 2 should not depend on broad UI or operational work to close this WF.

Suggested file-path clusters (coarse only):

- backend finding/pipeline contract seams under `backend/app/engine/`
- structured review assembly under `backend/app/services/`
- optional downstream exposure seams only if contract truth requires them
- regression/replay test seams near the changed backend or downstream public interfaces

## 7. Edge Cases

- A targeted snippet legitimately lacks enough proposal context to justify a concrete revision move; the system must preserve that limitation explicitly instead of guessing. (US1, US4, FR3, FR10)
- A review output contains one strong fix and several weaker comments; if ordering is absent or unstable, the item still fails the prioritization boundary even when one comment is actionable. (US1, US3, US4, FR2, FR8)
- Two revision moves may be equally urgent for the same snippet; if the contract allows ties, it must expose that tie explicitly and deterministically rather than silently dropping one move or inventing a false strict order. (US1, US3, FR2, FR13)
- A remediation makes the stress items pass but weakens the representative baseline items below their current WF-0068 judgments; the workflow still fails because closure cannot trade one narrow fix for broader regression. (US4, FR9)
- A downstream UI/BFF seam needs a tiny exposure update to preserve truthful ordering semantics; that is allowed only if Phase 2 documents it as a hard dependency rather than convenient polish. (US2, US3, FR4, FR12)
- The chosen seam can express actionability for one call family but not the other two locked calls; this fails wedge closure and cannot be presented as full WF-0069 success. (US2, US4, FR5, FR8)
- The remediation adds more detailed critique but still maps every card to the same generic `NOTE` shape; that does not satisfy the minimum contract if the stress items remain non-actionable in practice. (US1, US3, US4, FR1, FR2)
- The chosen contract allows equal-priority revision moves, but the implementation hides ties by emitting unstable order or dropping one move; this still fails the prioritization boundary because the contract is no longer truthful or deterministic. (US1, US3, US4, FR2, FR13)

## 8. Testing Decisions (TDD)

- WF-0069 is a behavior-change remediation workflow. Phase 3 must follow RED -> GREEN -> REFACTOR at the narrowest changed public seam. (US1-US4)
- Start with RED tests that reproduce the current actionability/prioritization failure at the smallest seam likely to change, preferably evaluator/card-contract/pipeline behavior before implementation. (US3, US4, FR1, FR2, FR7, FR8)
- GREEN tests must prove:
  - actionable revision guidance survives through the changed seam,
  - priority semantics survive through the changed seam,
  - fail-closed states remain explicit,
  - targeted stress outputs cannot regress back to generic `NOTE`/status-like shapes at the chosen seam,
  - equal-priority revision ties remain explicit and deterministic when the chosen contract supports ties,
  - the three named stress items pass,
  - the three named baseline items do not regress below current `weak` judgments. (US1, US3, US4, FR1-FR3, FR7-FR10)
- Mock only external boundaries. Do not mock the logic that determines actionable guidance content, priority preservation, or fail-closed state mapping within the chosen remediation seam. (US3, US4)
- If downstream API/BFF/render seams change, add matching contract/render regression tests there; otherwise keep testing local to backend/output seams plus deterministic replay evidence. (US3, US4, FR12)
- Required closure evidence must include deterministic replay commands or fixture-backed equivalents tied to the exact WF-0068 item IDs. (US4, FR7-FR11)
- Required closure evidence must include a disposition ledger for every justified review finding/comment, with any rejected non-blocking item carrying an explicit rationale. (US4, FR14)
- Phase 2 should require one explicit regression assertion at the mapper/output seam that the targeted items no longer serialize as flat `NOTE`/status-only review cards when the upstream contract carries actionable priority semantics. (US3, US4, FR12, FR13)

## 9. Telemetry (Minimal)

- No new product telemetry is required for MVP.
- Minimal diagnostic evidence is allowed only if needed to capture deterministic replay or pass/fail proof for the narrow remediation gate.

## 10. Deferred / Not in MVP

- Generic feedback-quality polish outside the bounded actionability/prioritization failure.
- Launch-readiness, rollout, or ongoing monitoring work.
- Broader trust-surface or review-detail improvements not required to expose approved remediation semantics truthfully.
- Additional call onboarding or wedge expansion.
- Prompt-only experimentation that is not justified as a hard dependency of the chosen remediation seam.

## 11. Open Questions (if any)

- Whether the smallest viable contract should be explicit per-card priority fields, review-level ordering metadata, or a smaller structured finding change.
- Whether a narrow prompt/policy adjustment becomes necessary after backend contract tightening, or remains unnecessary scope.
- Whether truthful researcher-facing exposure can remain backend-local or needs one small downstream contract/render change.

## 12. Changelog

- v0.1 (2026-03-09): Initial PRD from brainstorm.
- v0.2 (2026-03-09): Applied risk-audit hardening to make the minimum actionability/priority states explicit, add anti-flattening regression guards, and mark the PRD Ready for Tasks.
- v0.3 (2026-03-09): Added fail-closed audit-disposition closure requirements, baseline-anchored scope proof, and deterministic tie-handling regression coverage.
