<!-- docs/brainstorms/brainstorm-WF-0079-researcher-visible-carry-through-mvp.md -->
# WF-0079 — Researcher-Visible Carry-Through MVP

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-13

Type: feature
Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for scope, boundaries, and implementation direction for WF-0079.
- The Q&A transcript is rationale only; it must not become the only place where rollout boundaries, persistence decisions, or fail-closed fallback rules live.
- `pipeline_v1` remains the deterministic source of truth for findings, ratings, and traceability.
- Deterministic `ReviewCard.feedback_text` remains the fallback truth and must still render safely when additive synthesis is unavailable, rejected, or out of scope.
- Additive synthesis in this WF must stay downstream of deterministic card generation, clearly separated from deterministic feedback, and fail closed per card.
- WF-0075, WF-0076, WF-0077, and WF-0078 remain prior truth and are not reopened except where already-approved additive synthesis must be carried through truthfully to researcher-visible surfaces.

## Long-Form Problem Intake

WF-0077 made deterministic researcher-facing guidance the visible fallback surface for the structured `/app` review path. WF-0078 then added a bounded additive synthesis seam downstream of `pipeline_v1`, but intentionally closed as a backend-only seam proof. Today the only accepted synthesized companion output lives in-memory through `last_synthesis_requests` and `last_synthesis_results` inside `backend/app/services/structured_reviewer_service.py`.

The researcher-visible review detail flow still renders persisted deterministic `ReviewCard.feedback_text`, so the product remains effectively unchanged to researchers after WF-0078. That creates a truth gap: the system can accept grounded additive synthesis at the service seam, but the persisted/read/API/frontend carry-through needed for an honest user-visible rollout does not exist yet.

This workflow therefore needs to design the narrowest production-credible MVP that makes accepted synthesized companion output truthfully visible on `/app/reviews/[reviewId]` without weakening deterministic trust. The runtime invariants remain fixed: `pipeline_v1` is still deterministic SSOT, additive synthesis remains downstream only, deterministic `feedback_text` remains the fallback truth, and per-card fail-closed behavior remains mandatory.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Preflight Step 1)

Contract Notes / Non-obvious constraints:
- This is not a new synthesis-generation workflow; accepted synthesis already exists and the gap is truthful carry-through.
- Researcher-visible behavior cannot be claimed unless persistence, API/read path, and frontend rendering are all actually connected.
- Backward compatibility is a first-class requirement because most existing reviews will not have synthesized companion data.

## Repo Reality Snapshot (Read-Only)

- `backend/app/services/structured_reviewer_service.py` already attempts bounded `ERC-2026-PoC` synthesis after deterministic card generation and records seam-only proof via `last_synthesis_requests` / `last_synthesis_results`.
- `backend/app/services/structured_review_synthesis_service.py` already defines a typed accepted-vs-rejected per-card synthesis contract, including fail-closed rejection categories.
- `backend/app/repositories/review_repository.py#create_review_cards_batch` and the current write path still persist only deterministic `ReviewCard` fields; no migration or create-time persistence seam exists yet for accepted synthesized companion data.
- `backend/app/models/domain.py` persists only deterministic `ReviewCard.feedback_text`, `rating`, `assessment_status`, and `not_assessable_reason`; there is no stored synthesized companion or synthesis provenance field.
- `backend/app/repositories/review_repository.py`, `backend/app/schemas/api.py`, and `backend/main.py` read and expose only deterministic `feedback_text` on review cards for the detail response.
- `frontend/src/app/app/reviews/[reviewId]/page.tsx` renders only `card.feedback_text` and its page-local copy/export helper also serializes only `feedback_text`, so the current detail page has both a missing additive display seam and a same-page export coupling that cannot be ignored during rollout planning.

## Open Questions / Deferred

- MVP prefers nullable card-level persisted companion fields on `ReviewCard`; alternative persistence shapes are out unless Phase 1 proves this is unsafe.
- Whether review history/list surfaces should remain deterministic-only in MVP even if detail view carries the additive companion.
- Whether the page-local copy/export action on `/app/reviews/[reviewId]` should carry the additive companion in MVP or remain explicitly deterministic-only with matching product labeling and ship claims.

## 1. Problem Statement

- The current structured `/app` review detail page truthfully shows only deterministic `ReviewCard.feedback_text`, even when accepted additive synthesis existed earlier at the backend seam.
- The product gap is therefore not synthesis generation; it is missing researcher-visible carry-through of already-approved additive synthesis.
- The workflow must close that gap without overstating rollout or weakening trust: deterministic findings remain authoritative, deterministic `feedback_text` remains the fallback truth, and additive synthesis remains a separate companion surface.
- The first user-visible target is the structured review detail page at `/app/reviews/[reviewId]`, because that is where researchers actually read persisted review cards today.
- This should remain one WF for the detail-page MVP because persistence, repository reads, API detail response, and frontend rendering together define one truthful user-visible contract. Splitting earlier would risk a half-finished rollout that still cannot be claimed honestly.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Section 1)

Contract Notes / Non-obvious constraints:
- Researcher-visible behavior is not real until persisted storage, read path, API, and frontend all agree.
- The workflow is about structured review detail truthfulness, not broader AI-writing-coach behavior.
- One WF does not mean one implementation task; Phase 2 must still split work into atomic tasks with no more than three touched files each.

## 2. Desired Outcome

- A researcher opening `/app/reviews/[reviewId]` for an in-scope structured review should see deterministic review feedback as the baseline/fallback and an accepted synthesized companion when one was persisted successfully.
- A researcher opening a review with no accepted synthesis should still see a coherent deterministic-only page without broken UI states or misleading empty synthesis placeholders.
- The page should make the separation explicit: deterministic feedback stays the authoritative baseline, while synthesized companion text is clearly labeled additive guidance tied to the same card.
- Success for MVP is a truthful end-to-end detail-page experience, not merely a backend seam or a UI mock.
- The narrowest honest ship claim is: structured review detail pages can display persisted additive synthesized companion output when available, while retaining deterministic feedback as fallback truth.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Section 2)

Contract Notes / Non-obvious constraints:
- Absence of synthesis is a supported state, not an error state.
- Deterministic feedback remains readable even when synthesis is present; the additive companion must not replace it.
- MVP success does not require broader export, review history, or list-page changes, but the existing page-local copy/export action still needs explicit closure because it already lives on the target detail surface.

## 3. Target User / Actor

- The primary user is a researcher reading structured `/app` review results to improve a proposal against evaluation criteria and elements.
- The secondary actor is the maintainer protecting deterministic traceability, fail-closed behavior, and honest rollout claims.
- The user pain is interpretation burden: deterministic guidance exists, but grounded additive synthesis that can help the researcher revise text is not actually visible on the persisted detail page.
- The maintainer pain is rollout honesty: accepted seam-only synthesis exists, but current persisted/read surfaces would make any researcher-visible claim misleading.
- Researcher-facing copy must continue to use evaluation criteria/elements terminology consistently.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Section 3)

Contract Notes / Non-obvious constraints:
- This WF serves the structured `/app` researcher journey, not the legacy review path.
- Internal observability matters only insofar as it supports truthful user-visible behavior and rollback.

## 4. Rough Idea (Unstructured Thinking)

- The narrowest production-credible path is to persist a nullable additive companion alongside each deterministic review card for in-scope structured reviews that accept synthesis.
- The persistence seam must include create-time write-path changes where accepted synthesis is attached to the saved `ReviewCard` row during review generation; recomputing or backfilling on detail read is out of scope for MVP.
- The read path should carry that optional companion through repository mapping and review detail API response without overloading deterministic `feedback_text`.
- The frontend should render deterministic feedback first and then, only when available, a clearly labeled synthesized companion block for the same card.
- The safest initial public contract shape is an additive nullable card field or fields on the detail response, not recomputation on read and not merging synthesis into deterministic text.
- Review history should stay out of MVP, while the existing page-local copy/export action requires an explicit truthfulness decision because it already lives on the review-detail surface.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Section 4)

Contract Notes / Non-obvious constraints:
- The workflow must prefer stable persisted reads over transient in-memory seams.
- A clear additive contract is safer than mutating or concatenating deterministic text.
- The detail response contract should remain backward compatible for reviews created before this WF.

## 5. Constraints

- `pipeline_v1` remains the deterministic SSOT for findings, ratings, and traceability; this WF must not move synthesis upstream or reopen execution-engine questions.
- WF-0079 carries through only the already-approved additive synthesis scope from WF-0078: `ERC-2026-PoC` structured review cards that already qualify for accepted synthesis.
- Deterministic `feedback_text` remains the fallback truth and must continue to render even when synthesis is absent, rejected, or out of scope.
- Additive synthesis must remain clearly separated from deterministic feedback in both persisted shape and rendered UI.
- Per-card fail-closed behavior remains mandatory: an invalid or missing companion for one card must degrade only that card to deterministic-only display.
- The carry-through must be backward compatible for existing reviews with no synthesized companion data.
- Accepted synthesis must be persisted at review-generation time rather than regenerated on read; otherwise the carry-through claim is not durable.
- MVP scope stays limited to the structured review detail page; exports, history/list surfaces, and broad redesign are deferred unless Phase 1 proves a blocker.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Section 5)

Contract Notes / Non-obvious constraints:
- Backward compatibility is both a DB/read concern and a UI-state concern.
- No rollout claim is valid unless persistence + API/read path + frontend rendering all ship together.
- Phase 2 must split code changes into atomic tasks if implementation spans more than three files.

## 6. Risks / Unknowns

- The biggest hidden-coupling risk is choosing a persistence contract that looks small but forces larger repo-wide changes across repository, schema, API, and frontend surfaces.
- Another hidden-coupling risk is forgetting that the current detail page already has a copy/export action, which can create a user-visible deterministic-only side path on the same page even after additive companion rendering ships.
- The biggest product honesty risk is overloading `feedback_text` or rendering synthesis as if it were deterministic truth.
- The main backward-compatibility risk is creating a response/UI path that assumes synthesis exists for all cards or all reviews.
- The main scope-creep risk is quietly pulling exports or review-history surfaces into MVP without proving they are necessary for the detail-page ship claim.
- The main planning risk is treating this as “frontend only” or “backend only” when it is inherently one end-to-end read contract.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Section 6)

Contract Notes / Non-obvious constraints:
- The safest contract is the one that makes missing synthesis explicit and harmless.
- The first planning artifact must compare narrow persistence shapes instead of assuming them.
- Verification evidence must prove mixed states: some reviews/cards with synthesis, others without.

## 7. MVP Definition

- This should remain one WF: researcher-visible carry-through for the structured review detail page, with internal task splitting rather than a separate carry-through WF.
- Exact in-scope surfaces:
  - review-generation write path that persists optional accepted synthesized companion data onto structured review cards without mutating deterministic `feedback_text`;
  - persisted storage for optional accepted synthesized companion data on structured review cards;
  - repository/read path needed to hydrate that optional companion on review detail reads;
  - review detail API contract for `/reviews/{review_id}` and its BFF consumer path;
  - frontend rendering on `/app/reviews/[reviewId]` showing deterministic feedback as baseline plus additive synthesized companion when available.
- Exact out-of-scope surfaces:
  - exports/download/copy text outside the review-detail page;
  - review history/list pages;
  - legacy `/reviews` path redesign;
  - whole-review synthesis, generalized AI coach features, or cross-call expansion beyond already-approved synthesis scope.
- Exports/history are deferred by default. They are not part of MVP unless a later planning artifact proves the review-detail ship claim would otherwise be misleading.
- The existing page-local copy/export action on `/app/reviews/[reviewId]` is a conditional coupling seam, not an automatic deferment. Phase 1 must either:
  - carry the additive companion through that action truthfully; or
  - keep the action deterministic-only and explicitly align the UI label/help text and ship claim so researchers are not misled.
- Review history/list remain deterministic-only surfaces in MVP and must not claim additive companion visibility.
- Backward-compatibility plan:
  - existing reviews with no synthesis data must continue to deserialize, read, and render as deterministic-only cards;
  - migration/read behavior must preserve legacy reviews by treating new companion fields as nullable with no backfill requirement for MVP;
  - the detail response must treat synthesized companion data as optional per card;
  - the frontend must not show warnings or empty companion shells when the optional data is absent.
- Narrowest safe public contract shape:
  - keep `feedback_text` unchanged as deterministic baseline/fallback;
  - add optional additive fields scoped to the same card, likely `synthesized_companion_text` plus a minimal accepted-companion-present state marker without redefining deterministic truth;
  - do not expose internal rejection taxonomy in the user-visible contract.
- Topological task order:
  - decide and harden the persistence contract first, including nullable-field legacy-read behavior and create-time write-path ownership;
  - then add the migration plus write-path persistence needed to save accepted companion data during review generation;
  - then carry it through repository and API detail reads;
  - then render it on the detail page with deterministic-first fallback behavior;
  - then close the page-local copy/export decision in the same detail surface honestly;
  - then run end-to-end verification covering old reviews, accepted-companion reviews, mixed-card reviews, deterministic-only fallback reviews, and the chosen page-local export/copy behavior.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0079-researcher-visible-carry-through-mvp.md` (Section 7)

Contract Notes / Non-obvious constraints:
- One WF is recommended because the user-visible truth contract spans all four layers.
- The contract should express acceptance/presence, not internal failure mechanics.
- A mixed-state review is valid: some cards may have companions while others remain deterministic-only.

## 8. Explicit Non-Goals

- Replacing or weakening `pipeline_v1` as deterministic SSOT.
- Replacing deterministic `feedback_text` with synthesized text as the only visible researcher-facing content.
- Reopening WF-0075, WF-0076, WF-0077, or WF-0078 beyond the already-approved additive synthesis carry-through required for truthful detail-page visibility.
- Broadening MVP to exports, history/list, legacy path redesign, or generalized AI coaching.
- Introducing non-additive whole-review synthesis or refactoring unrelated review contracts.

## Verification / Proceed Gate

- No proceed recommendation is valid unless the artifact proves a durable carry-through path from accepted synthesis at review generation through persisted review cards, detail reads, and researcher-visible rendering.
- No ship recommendation is valid unless verification evidence is recorded explicitly as `pass`, `fail`, or approved `skipped` with rationale for every required proof item below.
- No ship recommendation is valid if the page-local copy/export action on `/app/reviews/[reviewId]` remains ambiguous about whether it is additive-aware or intentionally deterministic-only.
- No ship recommendation is valid if the implementation overloads deterministic `feedback_text`, re-synthesizes on read, or assumes synthesis exists for all legacy reviews/cards.

### Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Deterministic SSOT boundary proof | Phase 1/2 artifacts + targeted backend tests | `fail` (default until executed) | required | must prove `pipeline_v1` remains unchanged as the source of findings, ratings, and traceability |
| Write-path persistence proof | targeted model/repository/service tests + migration artifact | `fail` (default until executed) | required | must prove accepted synthesis is saved during review generation rather than recomputed on read |
| Legacy review compatibility proof | targeted backend tests over pre-WF-0079 review data | `fail` (default until executed) | required | must prove reviews/cards with null companion data still deserialize, read, and render cleanly |
| Detail read/API/BFF carry-through proof | repository, schema, backend response, and BFF type evidence | `fail` (default until executed) | required | must prove the optional additive field survives the read contract without breaking existing consumers |
| Detail-page render proof | targeted frontend tests or deterministic UI proof | `fail` (default until executed) | required | must prove deterministic feedback remains primary and additive companion renders only when present |
| Mixed-card fail-closed proof | targeted backend/frontend tests | `fail` (default until executed) | required | must prove one card can show an accepted companion while another card in the same review remains deterministic-only |
| Page-local copy/export proof | targeted frontend tests plus product copy evidence | `fail` (default until executed) | required | must prove the existing detail-page copy/export action is either additive-aware or explicitly deterministic-only with matching labels/ship claim |
| Out-of-scope surface proof | targeted checks for review history/list and legacy `/reviews` | `fail` (default until executed) | required | must prove deferred surfaces remain deterministic-only and are not overclaimed |
| Honest non-determinism test strategy | Phase 2 task plan + verification selectors | `fail` (default until executed) | required | must avoid brittle live-model exact-string assertions while still proving grounded carry-through behavior |
| Audit disposition | findings-closure ledger | `fail` (default until executed) | required | must close all blocking findings and either close or justify non-blocking findings |

## Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Continuation adversarial brainstorm review | The MVP contract treated persistence and detail reads as in scope but did not explicitly name the review-generation write path or migration seam needed to save accepted companion data durably | blocking | add the write-path persistence seam, migration ownership, and write-path verification rows to the brainstorm | closed | prevents a fake "persisted carry-through" plan that never states how data reaches storage |
| Continuation adversarial brainstorm review | The brainstorm deferred exports too broadly even though the current detail page already includes a page-local copy/export action that serializes deterministic-only `feedback_text` | blocking | make the detail-page copy/export action an explicit conditional coupling seam with its own closure rule and verification row | closed | prevents a same-page truth gap after additive rendering ships |
| Continuation adversarial brainstorm review | The brainstorm required explicit pass/fail ship evidence in prose but lacked a fail-closed verification matrix and audit ledger comparable to the approved WF-0078 artifacts | non-blocking | add a verification/proceed gate matrix plus an audit disposition ledger to preserve fail-closed closure semantics | closed | keeps later PRD/task phases from softening ship evidence requirements |

## Changelog

- v0.1 (2026-03-13): Captured the initial Phase 0 scope for a one-WF researcher-visible carry-through MVP on structured review detail.
- v0.2 (2026-03-13): Applied the Phase 0 risk audit by locking MVP to nullable card-level persistence, restating the `ERC-2026-PoC` scope gate, making exports/history explicitly deterministic-only deferred surfaces, and tightening legacy-read/public-contract constraints.
- v0.3 (2026-03-13): Closed the continuation adversarial review by naming the missing write-path persistence seam, forcing an explicit decision on the existing detail-page copy/export action, and adding a fail-closed verification matrix plus audit disposition ledger before any ship claim.
