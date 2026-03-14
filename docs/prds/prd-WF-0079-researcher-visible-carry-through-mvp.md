<!-- docs/prds/prd-WF-0079-researcher-visible-carry-through-mvp.md -->
# WF-0079 — Researcher-Visible Carry-Through MVP

Artifact: prd
Version: v0.3
Status: Ready for Tasks
Last Updated: 2026-03-13

Type: feature

## 0. User Stories (MVP)

- US1: As a researcher reading a structured review at `/app/reviews/[reviewId]`, I want deterministic review feedback to remain visible and an accepted synthesized companion to appear only when it was durably persisted for that card, so that I can use added guidance without losing trust in the baseline review.
- US2: As a maintainer, I want accepted additive synthesis to be persisted during review generation and carried through the repository, API/BFF, and detail-page render path as an optional card-level companion, so that researcher-visible behavior is truthful and durable rather than recomputed on read.
- US3: As a maintainer protecting deterministic trust, I want `pipeline_v1` and deterministic `feedback_text` to remain the authoritative baseline/fallback while additive synthesis stays separate and fails closed per card, so that malformed, rejected, or missing companion data never weakens deterministic review truth.
- US4: As a product owner shipping the narrowest safe MVP, I want scope limited to the structured review detail page contract, including the page-local copy/export action on that page, so that we can ship one honest end-to-end slice without widening into history/list surfaces or legacy redesign.

## Deferred Stories (Not in MVP)

- As a researcher, I want additive synthesized companion text to appear in review history/list pages.
- As a researcher, I want exports or download flows outside `/app/reviews/[reviewId]` to include additive companion text.
- As a maintainer, I want legacy `/reviews` paths redesigned around the additive contract.
- As a maintainer, I want whole-review synthesis, read-time recomputation, or generalized AI-coach behavior.

## 1. In Scope

- Persist an optional accepted synthesized companion on structured `ReviewCard` rows during the review-generation write path, without mutating deterministic `feedback_text`. `(US1) (US2) (US3)`
- Keep nullable card-level companion storage backward compatible for reviews/cards that predate WF-0079 or have no accepted synthesis. `(US1) (US2) (US3)`
- Carry the optional companion through repository reads, review detail API contracts, and the BFF/detail consumer path for `/reviews/{review_id}`. `(US1) (US2)`
- Render deterministic feedback as the primary baseline on `/app/reviews/[reviewId]` and render a clearly labeled additive synthesized companion only when present for that card. `(US1) (US3) (US4)`
- Keep the page-local copy/export action on `/app/reviews/[reviewId]` intentionally deterministic-only in MVP, with aligned labeling and ship claims. `(US1) (US4)`
- Preserve per-card fail-closed behavior so missing/rejected/invalid companion data degrades only the affected card to deterministic-only rendering. `(US1) (US3)`
- Keep `ERC-2026-PoC` as the only approved synthesis-eligible scope and keep `pipeline_v1` as deterministic SSOT. `(US2) (US3)`

## 2. Out of Scope

- Review history/list surfaces and any claim that they expose additive synthesized companion text. `(US4)`
- Exports/download/copy flows outside the `/app/reviews/[reviewId]` page-local action. `(US4)`
- Legacy `/reviews` path redesign or contract harmonization. `(US4)`
- Whole-review synthesis, generalized AI writing coach behavior, or scope expansion beyond already approved synthesis eligibility. `(US3) (US4)`
- Recomputing, backfilling, or lazily generating synthesized companion text during detail reads. `(US2) (US3)`
- Overloading deterministic `feedback_text` with additive content or exposing internal rejection taxonomy in the public card contract. `(US1) (US3)`

## 3. User / System Flow

- Happy path
  - A structured `ERC-2026-PoC` review is generated, `pipeline_v1` produces deterministic cards, and accepted additive synthesis is available for some cards at the post-pipeline seam. `(US1) (US2) (US3)`
  - The review-generation write path persists deterministic card fields plus the optional accepted synthesized companion on the same card row when that companion passed validation. `(US1) (US2) (US3)`
  - A researcher opens `/app/reviews/[reviewId]`, the repository/API/BFF read contract returns deterministic `feedback_text` and any optional companion field per card, and the frontend renders deterministic feedback first with the additive companion shown only where present. `(US1) (US2) (US3) (US4)`
  - The page-local copy/export action remains deterministic-only and labels that scope clearly enough to avoid implying additive carry-through. `(US1) (US4)`
- Failure path 1
  - A review or card has no accepted synthesized companion because it predates WF-0079, is out of scope, or synthesis was rejected, so the persisted/read/render path returns deterministic-only card data and the detail page shows no empty companion shell. `(US1) (US2) (US3)`
- Failure path 2
  - A mixed-state review contains some cards with accepted companions and other cards without them, so each card renders independently and the missing companion on one card does not affect the others. `(US1) (US3)`
- Failure path 3
  - The page-local copy/export action cannot safely carry additive content in MVP, so it remains intentionally deterministic-only and must say so clearly enough that the ship claim does not imply otherwise. `(US1) (US4)`

## 4. Functional Requirements

- FR1 (US1) (US2) (US3): The system must persist accepted additive synthesis during the review-generation write path for eligible structured review cards; it must not generate or regenerate companion text during detail reads.
- FR2 (US2) (US3): `pipeline_v1` must remain unchanged as the deterministic source of findings, ratings, and traceability for WF-0079.
- FR3 (US1) (US3): Deterministic `ReviewCard.feedback_text` must remain unchanged as the baseline/fallback user-visible feedback for every card.
- FR4 (US1) (US2) (US3): The persisted additive contract must stay card-scoped, optional, and clearly separate from deterministic `feedback_text`.
- FR5 (US1) (US2) (US3): Existing reviews and cards with null companion fields must deserialize, load, and render successfully without backfill requirements or warning states.
- FR6 (US1) (US2): The repository read path and review detail API/BFF contract must carry the optional companion field per card without breaking deterministic-only consumers.
- FR7 (US1) (US3) (US4): The detail page must render deterministic feedback regardless of companion presence and render the additive companion only when the optional data is present for that card.
- FR8 (US1) (US3): Fail-closed behavior must remain per card: invalid, rejected, or absent companion data for one card must not remove or corrupt deterministic rendering for that card or any sibling card.
- FR9 (US1) (US4): The page-local copy/export action on `/app/reviews/[reviewId]` must remain deterministic-only in MVP, with explicit UI/product wording aligned to that limitation.
- FR10 (US2) (US3) (US4): The narrowest public card contract must expose only what the detail page needs for accepted companion visibility and must not expose internal rejection reasons or redesign unrelated review contracts.
- FR11 (US2) (US3): Non-targeted calls/cards must remain on the current deterministic contract and must not begin persisting or exposing additive companion fields accidentally.
- FR12 (US2) (US4): Phase 2 must plan implementation in topological order, beginning with data-contract/write-path safety, and keep tasks atomic with a preference for no more than three touched files each.

## 5. Data & API Contracts

- Persisted card contract `(US1) (US2) (US3) (FR1) (FR3) (FR4) (FR5)`
  - Deterministic fields remain authoritative and unchanged, including `feedback_text`, rating, and assessment status.
  - Add one nullable card-level field for accepted synthesized companion text; do not add a second public marker unless Phase 2 proves it is strictly required for implementation safety.
  - Validation rule: null companion data is a valid steady state for legacy cards, rejected synthesis, and out-of-scope cards.
- Write-path ownership contract `(US1) (US2) (US3) (FR1) (FR8)`
  - Companion persistence happens when review cards are created during structured review generation.
  - Only accepted validated synthesis may be written.
  - Rejected synthesis remains dropped/fail-closed rather than partially persisted.
- Detail read/API/BFF contract `(US1) (US2) (FR5) (FR6) (FR10)`
  - `/reviews/{review_id}` returns deterministic card data for all reviews.
  - The detail contract may include nullable `synthesized_companion_text` on any structured review card; `null` is the safe backward-compatible value for legacy reviews, out-of-scope cards, and cards without accepted persisted synthesis.
  - For cards with persisted accepted synthesis, the same response includes that nullable additive field with text for the originating card only.
  - The response must treat companion data as optional per card, not per review, and the BFF/type boundary must pass the field through without semantic rewriting.
- Frontend render contract `(US1) (US3) (US4) (FR7) (FR8) (FR9)`
  - Deterministic feedback renders first and always.
  - Additive companion text renders only when present and with labeling that marks it as additive guidance, not deterministic truth.
  - The page-local copy/export behavior remains deterministic-only and must say so in user-facing copy.
- Logical state transitions `(US1) (US2) (US3) (FR1) (FR5) (FR8)`
  - `deterministic_only`: card has no accepted companion persisted.
  - `deterministic_plus_companion`: card has accepted companion persisted and rendered additively on the detail path.
  - These are planning states only; they do not require a separate public enum/marker beyond the nullable companion field unless Phase 2 proves one is strictly required for implementation safety.
  - No public state may imply that rejected or malformed synthesis is part of the user-visible contract.

## 6. Components / Modules

- Persistence/model seam
  - Likely areas: `backend/app/models/domain.py` plus the migration seam that owns `ReviewCard` storage.
  - Responsibility: store the smallest nullable companion shape needed for durable carry-through.
- Review-generation write seam
  - Likely areas: `backend/app/repositories/review_repository.py` and the structured review service seam that hands accepted synthesis into card creation.
  - Responsibility: attach accepted per-card companion data during review generation, not at read time.
- Detail read/API seam
  - Likely areas: `backend/app/repositories/review_repository.py`, `backend/app/schemas/api.py`, `backend/main.py`, and any BFF type boundary used by the detail page.
  - Responsibility: hydrate and expose the narrow optional companion field safely for detail reads.
- Frontend detail seam
  - Likely area: `frontend/src/app/app/reviews/[reviewId]/page.tsx`
  - Responsibility: render deterministic-first card detail, optional additive companion blocks, and the chosen page-local copy/export behavior.
- Design tree (dependencies + ordering)
  - 1. Lock the persisted card contract and legacy-null compatibility rules before implementation. `(FR1) (FR4) (FR5) (FR10)`
  - 2. Add storage/migration support and write-path persistence for accepted companions during review generation. `(FR1) (FR8)`
  - 3. Carry the optional field through repository mapping and review detail API/BFF reads. `(FR5) (FR6)`
  - 4. Render deterministic-first detail cards with optional additive companion blocks. `(FR7) (FR8)`
  - 5. Close the page-local copy/export contract honestly on the same page. `(FR9)`
  - 6. Verify mixed-card, legacy-null, deterministic-only, and in-scope companion-present states end to end. `(FR5) (FR8) (FR11) (FR12)`
- Deep module guidance
  - Keep the public card contract minimal and additive.
  - Keep rejection taxonomy and synthesis internals behind the deterministic/public boundary.
  - Keep topological planning explicit so Phase 2 does not front-load UI work before storage/read contracts are stable.

## 7. Edge Cases

- A review created before WF-0079 has no companion data on any card and still renders clean deterministic-only output. `(US1) (US2) (US3)`
- One card in a review has accepted companion text while another card in the same review does not. `(US1) (US3)`
- A card is eligible for synthesis but the accepted companion was not persisted due to fail-closed rejection or absence, so the read contract must still behave identically to legacy deterministic-only cards. `(US1) (US2) (US3)`
- The frontend receives null companion data and must not render empty headings, spacing, or misleading placeholders. `(US1) (US4)`
- The page-local copy/export action remains deterministic-only in MVP, and the visible label/help text must not imply that copied/exported content matches the full on-page additive display. `(US1) (US4)`
- History/list pages and legacy `/reviews` paths remain deterministic-only and must not accidentally consume the new field or broaden their claims. `(US4)`

## 8. Testing Decisions (TDD)

- RED first
  - Add failing backend tests proving accepted companion data is not yet persisted through the structured review write path. `(US2) (US3) (FR1) (FR4)`
  - Add failing backend/API tests proving legacy-null and mixed-card reads are not yet carried through the repository -> API/BFF -> detail response contract. `(US1) (US2) (US3) (FR5) (FR6) (FR8)`
  - Add failing backend/API tests proving non-targeted calls/cards do not start persisting or exposing additive companion data outside the approved `ERC-2026-PoC` scope. `(US2) (US3) (FR10) (FR11)`
  - Add failing frontend tests proving the detail page does not yet render additive companions correctly or align the deterministic-only page-local copy/export behavior, labels, and help text with the chosen MVP rule. `(US1) (US4) (FR7) (FR9)`
- Test seams
  - Public review-generation service/repository seam that creates review cards.
  - Public `/reviews/{review_id}` detail response seam and its BFF typing boundary.
  - Detail-page rendering and the page-local copy/export behavior on `/app/reviews/[reviewId]`.
- What to mock
  - Mock only external or already-proven synthesis dependencies when isolating carry-through behavior.
  - Do not mock the persistence/read seams whose contract this WF exists to prove.
- Minimal test types
  - Targeted model/migration/repository/service tests for write-path persistence and legacy-null compatibility.
  - Targeted backend/API or integration-ish tests for detail response carry-through.
  - Targeted frontend render tests for deterministic-only, companion-present, mixed-card, and page-local copy/export states.

## 9. Telemetry (Minimal)

- Minimal telemetry is limited to existing operational evidence needed to debug whether companion data was accepted and persisted for a card.
- New product analytics are deferred unless implementation proves they are required to operate the fail-closed detail contract safely.

## 10. Deferred / Not in MVP

- Review history/list additive visibility.
- Export/download flows outside the detail-page-local action.
- Legacy `/reviews` redesign.
- Read-time synthesis generation or backfill jobs.
- Broader public provenance or rejection-taxonomy exposure than the minimal accepted-companion contract needs.

## 11. Open Questions (if any)

none

## 12. Verification / Proceed Gate

- No implementation-ready recommendation is valid unless the artifact records explicit `pass`, `fail`, or approved `skipped` evidence with rationale for every required proof item below.
- No implementation-ready recommendation is valid unless all blocking findings are closed and every justified non-blocking finding is either closed or explicitly rejected with rationale in the audit disposition ledger.
- No implementation-ready recommendation is valid if the implementation overloads deterministic `feedback_text`, re-synthesizes on read, or assumes synthesis exists for all legacy reviews/cards.
- No implementation-ready recommendation is valid if non-targeted calls/cards can begin persisting or exposing additive companion data without an explicit new workflow approval.
- No implementation-ready recommendation is valid if the page-local copy/export action on `/app/reviews/[reviewId]` is still ambiguous about its deterministic-only MVP behavior and user-facing wording.

## 13. Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Deterministic SSOT boundary proof | targeted backend tests + Phase 2/3 artifacts | `fail` (default until executed) | required | must prove `pipeline_v1` remains unchanged as the source of findings, ratings, and traceability |
| Write-path persistence proof | targeted model/repository/service tests + migration artifact | `fail` (default until executed) | required | must prove accepted companion data is persisted during review generation rather than generated on read |
| Legacy review compatibility proof | targeted repository/API/frontend tests using null companion data | `fail` (default until executed) | required | must prove legacy reviews/cards render and deserialize cleanly with nullable companion fields |
| Eligibility scope-gate proof | targeted backend/API tests for non-`ERC-2026-PoC` calls/cards | `fail` (default until executed) | required | must prove non-targeted calls/cards do not start persisting or exposing additive companion data accidentally |
| Detail read/API/BFF carry-through proof | repository mapping, API schema, BFF type, and detail-page evidence | `fail` (default until executed) | required | must prove nullable `synthesized_companion_text` survives the detail read contract without semantic drift |
| Detail-page render proof | targeted frontend tests or deterministic UI proof | `fail` (default until executed) | required | must prove deterministic feedback remains primary and additive companion text appears only when present |
| Mixed-card fail-closed proof | targeted backend/frontend tests | `fail` (default until executed) | required | must prove one card can show companion text while another card in the same review remains deterministic-only |
| Page-local copy/export proof | targeted frontend tests plus product copy evidence | `fail` (default until executed) | required | must prove page-local copy/export remains deterministic-only in MVP with matching user-facing wording |
| Out-of-scope surface proof | targeted checks for history/list and legacy `/reviews` | `fail` (default until executed) | required | must prove deferred surfaces remain deterministic-only and are not overclaimed |
| Honest non-determinism test strategy | Phase 2 task plan + verification selectors | `fail` (default until executed) | required | must avoid brittle exact-string assertions against live-model output while still proving carry-through behavior |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close all blocking findings and either close or justify non-blocking findings |

## 14. Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Fail-closed adversarial PRD review | The finalized PRD dropped the brainstorm's explicit verification/proceed gate prose and audit disposition ledger even though its own matrix still required audit-disposition closure evidence | blocking | restore the proceed gate and a PRD-local audit disposition ledger so readiness cannot drift into implicit approval | closed | prevents implementation-ready claims without explicit pass/fail proof and finding closure bookkeeping |
| Fail-closed adversarial PRD review | The PRD preserved the `ERC-2026-PoC` scope lock in requirements but did not make non-targeted call/card safety a dedicated verification obligation | blocking | add explicit RED tests and a verification-matrix row proving non-targeted calls/cards do not persist or expose additive companion data | closed | prevents silent cross-call scope drift while still passing legacy-null or detail-page proofs |

## 15. Changelog

- v0.1 (2026-03-13): Initial PRD from brainstorm.
- v0.2 (2026-03-13): Applied the Phase 1 risk audit by locking the nullable public companion contract, fixing the page-local copy/export scope to deterministic-only, and carrying fail-closed verification obligations into the PRD.
- v0.3 (2026-03-13): Restored the fail-closed proceed gate and audit ledger from the approved brainstorm, clarified state transitions as planning-only, and added explicit scope-gate test/proof requirements for non-targeted calls/cards.
