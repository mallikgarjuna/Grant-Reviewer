<!-- docs/prds/prd-WF-0067-review-trust-surface-closure.md -->
# WF-0067 — Review Trust Surface Closure

Artifact: prd
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher reading a completed review, I want each review card to clearly show the mapped evaluation criterion/element, the reviewed proposal section, and the official call basis when available, so that I can judge whether the feedback is grounded enough to act on.
- US2: As a researcher scanning the review-detail page, I want reviewed, supporting, and not-reviewed boundaries to be explicit and truthful, so that I do not mistake visible context for evaluated content.
- US3: As a release owner deciding whether the locked NWO/ERC/MSCA wedge is launch-ready, I want deterministic proof that trust surfaces fail closed across representative review-detail responses, so that trust claims are backed by actual response seams and not optimistic UI copy.
- US4: As an engineer planning implementation, I want the scope locked to user-visible trust improvements on review detail only, so that Phase 2 does not widen into new calls, assisted extraction, supporting-context expansion, or generic platform work.

## Deferred Stories (Not in MVP)

- DS1: Add new funding calls or broaden representative proof beyond `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- DS2: Build assisted extraction, richer proposal-context capture, or submit-flow education beyond what is required for review-detail truthfulness.
- DS3: Expand supporting-context semantics beyond authoritative review-detail metadata already supplied on the response path.
- DS4: Introduce generic provenance, explainability, telemetry, export, history, or platform trust systems.

## 1. In Scope

- Improve the review-detail page so every review card surfaces the mapped evaluation criterion/element, the reviewed section context, and a concise official source-basis line when authoritative call metadata is available. (US1)
- Make page-level trust messaging explicit about what was reviewed, what was visible but not reviewed, what was not evaluated, and when the review detail is operating in a legacy or unavailable-basis state. (US1, US2, US3)
- Keep reviewed versus supporting versus not-reviewed labeling fail-closed: only claim `supporting context` when authoritative review-detail metadata explicitly provides that role; otherwise fall back to truthful `reviewed` versus `not reviewed` wording. (US2, US3)
- Define launch-blocking versus non-blocking trust surfaces and the exact evidence required before the workflow can be considered done. (US3, US4)
- Allow only the minimal backend/BFF contract work needed for these user-visible trust surfaces to reach the review-detail UI through the actual response-assembly seam and BFF normalization seam. (US1, US3, US4)

## 2. Out of Scope

- New funding-program support, broader cross-call expansion, or revisiting the product wedge locked by WF-0066. (DS1)
- New call authoring, new review engine semantics, or model/prompt tuning intended to improve feedback quality rather than trust legibility. (DS1, DS4)
- Assisted extraction, supporting-context authoring/persistence, or submit-flow redesign beyond review-detail truthfulness. (DS2, DS3)
- Generic explainability architecture, full provenance chains, telemetry/platform work, and unrelated export/history redesign. (DS4)

## 3. User / System Flow

### Happy path

1. The researcher opens a completed review-detail page for a supported NWO, ERC, or MSCA review. (US1, US2)
2. The backend review-detail response assembles the trust fields the page needs, including mapped evaluation criterion/element, reviewed node title/context, assessment state, limitation state, and authoritative source-basis metadata when available. (US1, US3)
3. The BFF review-detail route normalizes those trust fields without inventing missing semantics and passes them to the frontend render model. (US1, US3, US4)
4. Each review card displays the mapped evaluation criterion/element, the reviewed section, a concise official source-basis line when authoritative basis exists, and explicit `NOT_ASSESSABLE` or equivalent limitation labeling when the finding is not evaluable. (US1, US2)
5. The page-level coverage and boundary surfaces distinguish reviewed sections, visible-but-not-reviewed sections, and any trustworthy supporting-context labels only when the contract explicitly supplies them. (US2, US3)
6. If source basis is unavailable, legacy fallback linkage is in effect, or supporting-context semantics are not authoritative, the page uses explicit limitation copy instead of implying stronger trust than the contract supports. (US1, US2, US3)
7. Launch-readiness for this WF is claimed only after automated and manual evidence passes for the locked representative call set with no out-of-scope expansion. (US3, US4)

### Failure path A — polished card, ambiguous grounding

1. A review card still omits the reviewed section, official source basis, or mapped evaluation criterion/element in the reading flow. (US1)
2. The page may look polished, but a researcher cannot tell what the feedback is grounded in. (US1, US3)
3. The workflow remains blocked because card-level trust legibility is a launch-blocking surface. (US1, US3)

### Failure path B — supporting-context semantics are implied without proof

1. The UI labels content as `supporting context` even though the response contract did not explicitly provide that role. (US2, US3)
2. The page overstates what the system knows about reviewed versus supporting content. (US2, US3)
3. The workflow remains blocked until the label is backed by authoritative review-detail metadata or removed in favor of fail-closed wording. (US2, US3)

### Failure path C — trust copy exists but seam-level proof is missing

1. Frontend copy claims reviewed/not-reviewed boundaries or source-basis honesty, but the backend response-assembly seam or BFF normalization seam does not have deterministic proof for representative calls and fail-closed states. (US3, US4)
2. Launch claims would rest on UI text rather than actual contract behavior. (US3)
3. The workflow remains blocked until the required seam-level tests and representative evidence exist. (US3, US4)

## 4. Functional Requirements

- FR1 (US1): Every review card must display the mapped evaluation criterion and evaluation element using researcher-facing terminology, not `rubric`.
- FR2 (US1): Every review card must display the reviewed proposal section context from authoritative review-detail data.
- FR3 (US1, US3): Every review card must display a concise official source-basis line when authoritative call metadata is available for the mapped evaluation criterion/element.
- FR4 (US1, US3): If authoritative source-basis metadata is unavailable or the review detail is legacy/fallback-linked, the page must fail closed with explicit limitation copy instead of inferred or synthetic basis text.
- FR5 (US2, US3): The review-detail page must distinguish reviewed sections, visible-but-not-reviewed sections, and `NOT_ASSESSABLE` findings explicitly.
- FR6 (US2, US3): The UI may label content as `supporting context` only when authoritative review-detail metadata explicitly provides that role; otherwise it must use fail-closed reviewed/not-reviewed wording.
- FR7 (US2, US3): Page-level limitation/boundary copy must explicitly state what the review did not evaluate and must remain visible in the main review-detail reading flow.
- FR8 (US3, US4): Any trust field required by the UI must be proven across the actual backend review-detail response assembly seam and the BFF normalization seam, not just in schemas or frontend assumptions.
- FR9 (US3): Representative proof scope is locked to exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- FR10 (US3): Launch-blocking trust surfaces for WF-0067 are:
  - card-level evaluation criterion/element plus reviewed-section context,
  - official source-basis visibility or explicit fail-closed unavailability messaging,
  - truthful reviewed/supporting/not-reviewed boundary labeling,
  - explicit limitation copy for not-evaluated and legacy/fallback states,
  - deterministic seam-level proof for the representative call set and fail-closed states.
- FR11 (US3, US4): Non-blocking trust improvements for WF-0067 are:
  - richer explanatory prose beyond the minimum trust basis,
  - more polished score wording,
  - broader history/export improvements,
  - submit-flow education outside review detail.
- FR12 (US4): Phase 2 planning must stay localized to review detail, its render components, the BFF review-detail route, and the backend response path needed to expose those user-visible trust surfaces.
- FR13 (US4): Phase 2 planning must not widen into new calls, assisted extraction, supporting-context semantics expansion, or generic platform work unless a new blocker is explicitly logged and approved.
- FR14 (US3, US4): No readiness or ship recommendation is valid without explicit passing evidence for each launch-blocking trust surface and explicit proof that out-of-scope widening did not occur.

## 5. Data & API Contracts

### 5.1 Review-detail trust contract

- The review-detail response must carry the user-visible trust fields needed by the page, including:
  - mapped evaluation criterion and criterion description,
  - mapped evaluation element name,
  - reviewed node title or equivalent reviewed-section context,
  - assessment state and `not_assessable_reason` when applicable,
  - source-basis metadata derived from authoritative official-call definitions when available,
  - review-boundary metadata needed to distinguish reviewed versus visible-but-not-reviewed surfaces. (US1, US2, US3, FR1-FR8)
- The contract must not invent source basis from model output. Source-basis text in scope for WF-0067 means official call-basis metadata tied to the mapped evaluation criterion/element or equivalent authoritative review-detail metadata only. (US1, US3, FR3, FR4)
- If authoritative source basis or authoritative supporting-context role data is missing, the contract must surface an explicit unavailable/legacy limitation state rather than a guessed label. (US2, US3, FR4, FR6, FR7)

### 5.2 Backend response-assembly seam

- `backend/main.py` and the backend review-detail response assembly path are the public seam for any trust field exposed to the UI. Schema-only or repository-only changes do not satisfy this workflow. (US3, US4, FR8)
- If supporting-context role data is not authoritatively populated on the review-detail path, the backend must not imply it indirectly. (US2, US3, FR6, FR8)
- Fail-closed compatibility states that require proof include at least:
  - source basis unavailable,
  - `legacy_fallback` or equivalent legacy linkage state,
  - representative mixed-version review-detail records used to justify trust copy. (US3, FR4, FR8, FR14)

### 5.3 BFF normalization seam

- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` must normalize review-detail trust fields without synthesizing stronger semantics than the backend response provides. (US1, US3, US4, FR8, FR12)
- The BFF must preserve explicit fail-closed states needed for UI limitation copy, including unavailable source basis, legacy/fallback linkage, and absence of authoritative supporting-context labels. (US2, US3, FR4, FR6, FR7, FR8)

### 5.4 Frontend render contract

- `frontend/src/app/app/reviews/[reviewId]/page.tsx` and the review-card rendering path must place trust surfaces in the primary reading flow, not only in a distant summary block. (US1, US2, FR1-FR7)
- `frontend/src/components/review/ReviewCard.tsx` or its replacement seam must render only contract-backed trust labels and limitation states. (US1, US2, FR1-FR7)
- `NOT_ASSESSABLE` findings must remain explicitly labeled and must not be restyled into normal positive/negative findings. (US1, US2, FR5, FR7)

## 6. Components / Modules

- `backend/main.py`
  - Review-detail response assembly seam that must expose any new trust fields the UI depends on. (FR3-FR10)
- `backend/app/repositories/review_repository.py`
  - Current review-detail metadata source that may constrain truthful supporting-context labeling and legacy compatibility states; Phase 2 may touch it only if required to support user-visible trust surfaces honestly. (FR4-FR8, FR12, FR13)
- `backend/app/schemas/api.py`
  - Existing response-field contract source that documents trust-adjacent fields already available to the review-detail path. (FR1-FR8)
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
  - BFF normalization seam that must carry trust fields and fail-closed states to the frontend without invention. (FR4-FR10, FR12)
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Review-detail page boundary, coverage summary, and limitation/boundary copy surface. (FR4-FR10, FR12)
- `frontend/src/components/review/ReviewCard.tsx`
  - Card-level trust surface for evaluation criteria/elements, reviewed section context, source basis, and assessment-state labels. (FR1-FR7, FR10)
- Frontend/backend test seams for review detail
  - Must cover representative calls and fail-closed trust states at the backend seam, BFF seam, and render seam. (FR8-FR10, FR14)

Design tree / dependencies / ordering:
1. Freeze the review-detail trust contract and launch-blocking surfaces before any UI polish work. (FR8-FR14)
2. Prove what the backend response seam and BFF seam can supply today, including fail-closed states and supporting-context limitations. (FR4-FR8)
3. Render the minimum trustworthy card-level and page-level trust surfaces in the frontend reading flow. (FR1-FR7, FR10)
4. Add deterministic representative-call and fail-closed tests at backend, BFF, and frontend seams. (FR8-FR10, FR14)
5. Only after blocking trust surfaces are closed, consider non-blocking copy/polish improvements that stay inside review detail. (FR11-FR13)

Deep module guidance:

- Keep `source basis` narrow: official call metadata only, never generic model provenance.
- Keep `supporting context` fail-closed: no label without authoritative role data.
- Keep scope local to the review-detail experience and the seams needed to render it honestly.
- Treat launch-blocking trust surfaces as evidence-backed contracts, not just UX intentions.
- Prefer reuse of existing review-detail fields and call-definition metadata over inventing new explanation systems.

Suggested file-path clusters (coarse only):

- backend review-detail response path under `backend/`
- BFF normalization and review-detail UI under `frontend/src/app/`
- review-card presentation under `frontend/src/components/review/`
- review-detail contract/render tests under backend and frontend test trees

## 7. Edge Cases

- A representative call has evaluation criterion/element mapping but no authoritative `source_hint`; the UI must say the official source basis is unavailable rather than inventing one. (US1, US3, FR3, FR4, FR9)
- A legacy review record can still render cards, but its call linkage is fallback-only; the page must show limitation copy rather than implying full trust closure. (US1, US3, FR4, FR7, FR14)
- `supporting_context_node_logical_ids` remains empty or absent even when visible supporting nodes exist; the UI must not infer supporting semantics from page-local heuristics. (US2, US3, FR6, FR8)
- A card is `NOT_ASSESSABLE`; the page must keep that label explicit while still showing the mapped evaluation criterion/element and reviewed section context if available. (US1, US2, FR1, FR2, FR5, FR7)
- Page-level summary copy is accurate, but trust context remains absent inside the card reading flow; this is still launch-blocking because researchers decide at the card level. (US1, US3, FR10)
- Tests pass for one polished call only; this does not satisfy WF-0067 because representative proof is locked to three calls. (US3, FR9, FR10, FR14)

## 8. Testing Decisions (TDD)

- This WF is a user-visible behavior change and trust-contract hardening workflow. Phase 3 must follow RED -> GREEN -> REFACTOR. (US1, US2, US3, US4)
- Public seams under test must include:
  - backend review-detail response assembly,
  - BFF review-detail normalization,
  - review-detail page rendering,
  - review-card rendering for representative trust states. (US1, US2, US3, FR8-FR10, FR14)
- Mock only external boundaries. Do not mock the trust-field assembly, fail-closed state mapping, or render logic that determines whether a trust label appears. (US1, US2, US3)
- Required automated coverage:
  - backend contract tests proving representative review-detail responses expose the trust fields the UI depends on for exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`. (US3, FR8-FR10, FR14)
  - BFF tests proving normalization preserves trust fields and fail-closed states for those same representative calls. (US3, FR4-FR10, FR14)
  - frontend tests proving review cards show mapped evaluation criterion/element plus reviewed-section context. (US1, FR1, FR2, FR10)
  - frontend tests proving source-basis visibility renders correctly when authoritative basis exists and fails closed when it does not or when review detail is legacy/fallback-linked. (US1, US3, FR3, FR4, FR10)
  - frontend tests proving reviewed/supporting/not-reviewed labeling is truthful and never infers `supporting context` when the contract does not provide it. (US2, US3, FR5, FR6, FR10)
  - frontend tests proving limitation copy appears for required unavailable/legacy/`NOT_ASSESSABLE` states. (US1, US2, US3, FR5, FR7, FR10)
  - fixture-backed or automated compatibility tests covering fail-closed limitation states at the backend and BFF seams, including `legacy_fallback`, unavailable source basis, and any mixed-version case used to justify trust copy. (US3, FR4, FR8, FR10, FR14)

## 8.1 Readiness Gate

- WF-0067 is not ready for implementation or ship claims unless every launch-blocking trust surface in FR10 has an explicit planned verification seam and no unresolved blocking scope questions remain. (US3, US4)
- WF-0067 is not done unless passing evidence exists for every automated check in Section 8, manual or fixture-backed review evidence exists for the exact representative calls, and there is explicit proof that no out-of-scope expansion occurred. (US3, US4)
- Non-blocking trust improvements in FR11 may remain deferred only if all launch-blocking surfaces are closed and the deferral is explicitly documented. (US3, FR10, FR11, FR14)

## 9. Telemetry (Minimal)

- No new product telemetry is required for MVP.
- A narrow diagnostic field or fixture helper is acceptable only if it is required to prove fail-closed review-detail states at the backend or BFF seam.

## 10. Deferred / Not in MVP

- Review-history/export redesign tied to trust presentation.
- Additional source explanations beyond concise official call-basis disclosure.
- Broader submit-flow education or onboarding changes.
- New-call onboarding, supporting-context expansion, or generic explainability infrastructure.

## 11. Open Questions (if any)

- Whether the card-level official source-basis line should prefer criterion-level or evaluation-element-level `source_hint` when both exist, as long as the result stays authoritative and concise.
- Exact visual treatment of the page-level `How to read this review` or equivalent trust explainer, if one is needed after the minimum inline labels are specified.

## 12. Changelog

- v0.1 (2026-03-08): Initial PRD from brainstorm.
