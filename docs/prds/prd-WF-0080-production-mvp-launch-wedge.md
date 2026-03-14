<!-- docs/prds/prd-WF-0080-production-mvp-launch-wedge.md -->
# WF-0080 — Production MVP Launch Wedge

Artifact: prd
Version: v0.2
Status: Ready for Tasks
Last Updated: 2026-03-14

Type: feature

## 0. User Stories (MVP)

- US1: As an invited `ERC-2026-PoC` researcher, I want to submit one proposal snippet and reach one review-detail page safely, so that I can decide my next revision step without support intervention.
- US2: As an invited `ERC-2026-PoC` researcher, I want the review-detail page to show the top 1-3 issues first with expandable supporting evidence, so that I can understand what to revise next without reading the whole review as a spreadsheet.
- US3: As a maintainer running a 5-10 person launch cohort, I want out-of-cohort or over-limit traffic blocked before downstream review execution and one failed session traceable end to end, so that the wedge stays safe enough to operate without heroics.
- US4: As a product owner, I want WF-0080 closure to require attributable usefulness evidence and explicit pass/fail proof rows, so that launch claims stay bounded to this wedge and are verifiable in Phase 2/3.

## Deferred Stories (Not in MVP)

- As a researcher, I want this launch flow to work for calls beyond `ERC-2026-PoC`.
- As a researcher, I want review history/list redesign or broader export redesign.
- As an operator, I want a generalized admin console, onboarding system, or replay platform.
- As a product owner, I want whole-review reinterpretation or a new persistence hierarchy for review-detail prioritization.

## 1. In Scope

- One authenticated `ERC-2026-PoC` happy-path submit-to-detail flow through the existing `/api/bff/structured-review` -> `POST /api/structured-review` -> review-detail page path. `(US1) (US3)`
- One explicit launch-cohort allowlist gate at the BFF submit entrypoint with a mirrored backend fail-closed rejection for direct signed API access. `(US1) (US3)`
- One bounded review-detail projection seam at `GET /reviews/{review_id}` response assembly in `backend/main.py`, reusing persisted `ReviewCard` truth and existing call ordering rather than replacing review storage. `(US2) (US3)`
- One action-first review-detail reading model: at most 3 prioritized cards above the fold, explicit `no critical blockers found` state, and per-card evidence expansion on demand. `(US1) (US2)`
- Honest pending, timeout, failure, quota, and retry states on the submit-to-detail journey for this wedge only. `(US1) (US3)`
- One narrow support/trace seam sufficient to explain a failed or disputed cohort session. `(US3)`
- One walkthrough-based `Usefulness Evidence Log` with 5-10 attributable session rows as a required closure artifact. `(US4)`
- One explicit privacy/retention rule for the launch cohort: launch-session inputs/outputs remain only in existing review storage and support traces, with access limited to designated maintainers supporting the cohort and usefulness review. `(US3) (US4)`
- Truthful treatment of the existing page-local review export/copy behavior on `/app/reviews/[reviewId]`. `(US2) (US4)`

## 2. Out of Scope

- Any call beyond `ERC-2026-PoC`, unless Phase 2 proves this wedge cannot ship honestly without broadening. `(US4)`
- Any new review persistence hierarchy, whole-review re-scorer, or generic prioritization engine. `(US2) (US4)`
- Review history/list redesign, generalized exports, or cross-surface review presentation changes beyond the target detail page and its page-local copy/export behavior. `(US2) (US4)`
- A broad operator/admin product, generalized cohort onboarding flow, or privacy platform. `(US3) (US4)`
- Changes to `DiagnosticFinding v1` as engine truth or replacement of `ReviewCard` as the compatibility surface. `(US2) (US4)`
- Generic orchestration, multi-call launch infrastructure, or product claims not backed by Phase 2/3 verification evidence. `(US3) (US4)`

## 3. User / System Flow

- Happy path
  - An authenticated launch-cohort researcher opens the existing review submission surface for `ERC-2026-PoC`, enters one in-scope snippet, and submits through `/api/bff/structured-review` with an idempotency key. `(US1) (US3)`
  - The BFF verifies auth plus cohort membership before proxying, and the backend re-validates the same cohort boundary before any review record or downstream review execution starts. `(US1) (US3)`
  - The existing structured-review pipeline creates the review, applies the current quota gate, and returns a review id for the pending-or-complete review. `(US1) (US3)`
  - The researcher reaches `/app/reviews/[reviewId]`, where polling/status handling remains honest until completion and then loads the review detail response with the bounded projection metadata from `GET /reviews/{review_id}`. `(US1) (US2) (US3)`
  - The detail page shows one headline state plus at most the top 3 prioritized cards above the fold, ordered by assessment status first, lowest rating next, and existing call/node order as the final tie-breaker; supporting evidence stays collapsed until opened per card. `(US1) (US2)`
  - The researcher uses the top issue and supporting evidence to decide one next revision step, and the session is later captured in the walkthrough `Usefulness Evidence Log`. `(US1) (US2) (US4)`
- Failure path 1
  - An authenticated user who is not on the launch allowlist submits to `/api/bff/structured-review`, receives a fail-closed cohort-access error before proxying, and no review is created. `(US1) (US3)`
- Failure path 2
  - An invited user exceeds the existing per-user review quota or reviews are globally disabled, receives the existing fail-closed product error, and no new downstream review execution starts. `(US1) (US3)`
- Failure path 3
  - A submitted review remains pending past the current page polling cap or resolves to a failed state, so `/app/reviews/[reviewId]` presents an honest still-processing-or-failed message with retry/return-later guidance and traceable support metadata instead of implying success. `(US1) (US3)`

## 4. Functional Requirements

- FR1 (US1) (US3): WF-0080 must stay locked to `ERC-2026-PoC` as the only production launch wedge and must not broaden to other calls without a new approved workflow.
- FR2 (US1) (US3): `/api/bff/structured-review` must enforce an authenticated launch-cohort allowlist before proxying review requests downstream.
- FR3 (US1) (US3): `POST /api/structured-review` must mirror the same cohort gate fail-closed for direct signed access and must reject before review creation or downstream execution when the caller is out of cohort.
- FR4 (US1) (US3): The existing per-user quota seam and `REVIEWS_DISABLED` gate remain the MVP cost/safety control unless Phase 2 proves a narrower existing cap is required.
- FR5 (US1) (US3): The submit-to-detail path must preserve honest pending, timeout, failure, and retry states on the current review-detail page and must not present a still-processing review as completed.
- FR6 (US1) (US2): The review-detail reading model must surface at most 3 prioritized actionable cards above the fold.
- FR7 (US1) (US2): Card prioritization must be computed from existing review-card truth in this order only: `assessment_status` priority `NOT_ASSESSABLE` before `ASSESSED`, then rating priority `CRITICAL` before `WARNING` before `NOTE` before `SUCCESS`, then existing call/node order last.
- FR8 (US1) (US2): The detail page must render an explicit `no critical blockers found` headline only when every card is `ASSESSED` and every card rating is `NOTE` or `SUCCESS`; any `NOT_ASSESSABLE`, `CRITICAL`, or `WARNING` card forces the headline state to `action_required`.
- FR9 (US1) (US2): Supporting evidence must stay collapsed by default and be expandable per card, except the first ranked card must still expose enough visible summary context to explain why it is ranked first.
- FR10 (US2) (US3): The only new reading-model contract for MVP must be one bounded projection seam at `GET /reviews/{review_id}` response assembly; the BFF may normalize/pass fields through but must not reinterpret ranking semantics.
- FR11 (US2) (US3): The bounded projection seam must reuse persisted `ReviewCardSummary` truth, existing detail response fields, and existing call-node order rather than introducing a new review persistence hierarchy or whole-review rewrite.
- FR12 (US2) (US4): The existing page-local review export/copy behavior on `/app/reviews/[reviewId]` must remain truthful about what it includes, and any mismatch with on-page additive guidance/projection must be explicit.
- FR13 (US3): Each wedge review/session must carry enough trace correlation across BFF, backend review creation, and review-detail retrieval to explain one failed or disputed cohort session.
- FR14 (US3) (US4): Launch-session inputs/outputs may remain only in existing review storage and support traces, and access to those records must be limited to designated maintainers supporting launch and usefulness review.
- FR15 (US4): Phase 2/3 closure must include a walkthrough `Usefulness Evidence Log` with 5-10 attributable session rows containing the approved fields from the brainstorm.
- FR16 (US4): No readiness recommendation is valid unless every required proof row remains explicit `pass`, `fail`, or approved `skipped` with evidence pointers and scope proof.

## 5. Data & API Contracts

- Submit request contract `(US1) (US3) (FR2) (FR3) (FR4) (FR5)`
  - `POST /api/bff/structured-review` keeps the existing structured review request body and required `Idempotency-Key` header.
  - The BFF adds one launch-cohort membership check tied to the authenticated external user id before proxying to the backend.
  - Out-of-cohort requests return the standard API error envelope with a dedicated MVP code `COHORT_ACCESS_DENIED`; the response must be observable at the BFF surface and result in zero downstream review creation side effects.
- Backend submit gate contract `(US1) (US3) (FR3) (FR4)`
  - `POST /api/structured-review` keeps existing validation, quota, and review-disabled behavior.
  - Before review creation, the backend mirrors the cohort gate using the signed external user identity and returns the same `COHORT_ACCESS_DENIED` error code for direct signed requests that bypass the BFF.
  - Existing `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` errors remain unchanged and verifiable on the same surface.
- Review-detail projection contract `(US1) (US2) (US3) (FR6) (FR7) (FR8) (FR9) (FR10) (FR11)`
  - `GET /reviews/{review_id}` remains the single bounded projection seam and continues to return persisted review metadata plus card arrays.
  - Add one additive `detail_projection` object to `ReviewDetailResponse` with this exact MVP shape:
    - `version: "wf0080_launch_wedge_v1"`
    - `headline_state: "action_required" | "no_critical_blockers"`
    - `ordered_card_ids: list[UUID]`
    - `top_action_card_ids: list[UUID]` with length `0..3`
    - `ranking_basis: "assessment_status_then_rating_then_existing_order"`
  - `ordered_card_ids` and `top_action_card_ids` must be derived from existing persisted card truth plus existing call/node ordering only; no new persisted ranking table or whole-review synthesized summary object is allowed in MVP.
  - `headline_state = "no_critical_blockers"` only when every card is `ASSESSED` and has rating `NOTE` or `SUCCESS`; otherwise `headline_state = "action_required"`.
  - The BFF route at `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` may preserve and normalize the new object but must not recompute ranking or headline semantics locally.
- Detail page UI state contract `(US1) (US2) (FR5) (FR6) (FR8) (FR9) (FR12)`
  - `/app/reviews/[reviewId]` consumes `detail_projection` as the ranking/display contract for the wedge.
  - Only cards in `top_action_card_ids` render above the fold by default.
  - Additional cards remain available below the fold using existing review detail truth.
  - The first visible top-action card must display enough summary context without expansion to justify its rank; deeper evidence may expand per card on demand.
  - The existing page-local export/copy behavior must state whether it excludes additive companion guidance and projection-only framing.
- Usefulness evidence artifact contract `(US4) (FR15) (FR16)`
  - The walkthrough for WF-0080 must include a `Usefulness Evidence Log` appendix with one row per session containing: `session alias`, `date`, `researcher cohort/user`, `call code`, `snippet goal`, `completion outcome`, `top issue shown`, `usefulness rating`, `stated next revision action`, and `evidence/note reference`.
  - A session does not count as successful wedge evidence unless the row records both completion outcome and a stated next revision action or equivalent explicit usefulness failure.
  - The launch usefulness bar passes only if at least 5 logged cohort sessions have `completion outcome = completed`, `usefulness rating = useful`, and a non-empty `stated next revision action`; `mixed` and `not useful` rows remain valid evidence but do not count toward the pass threshold.
- Privacy/retention contract `(US3) (US4) (FR14)`
  - No new storage class is introduced for launch-session text.
  - Review inputs/outputs remain in the existing review storage plus narrow support traces only.
  - Access is restricted to designated maintainers for launch support and usefulness evaluation.

## 6. Components / Modules

- Submit gate seam
  - Likely areas: `frontend/src/app/api/bff/structured-review/route.ts`, `frontend/src/lib/bff/route-helpers.*`, `backend/main.py`.
  - Responsibility: authenticate, cohort-gate, preserve idempotency, and fail closed before downstream review execution.
- Structured review execution seam
  - Likely areas: `backend/main.py`, `backend/app/services/structured_reviewer_service.py`, existing repository review-creation helpers.
  - Responsibility: preserve the current `ERC-2026-PoC` structured-review path, quota checks, and review creation without turning WF-0080 into a new orchestration layer.
- Review-detail projection seam
  - Exact MVP seam: response assembly for `GET /reviews/{review_id}` in `backend/main.py`.
  - Responsibility: compute `detail_projection` from existing card truth and existing ordering signals only.
- BFF detail passthrough seam
  - Likely area: `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`.
  - Responsibility: preserve backend trust fields and the new `detail_projection` object without local ranking reinterpretation.
- Review-detail UI seam
  - Likely areas: `frontend/src/app/app/reviews/[reviewId]/page.tsx`, `frontend/src/components/review/ReviewCard.tsx`, and adjacent render helpers.
  - Responsibility: render the top-action-first reading model, explicit headline state, expandable evidence, honest pending/timeout/failure messaging, and truthful page-local export/copy copy.
- Support/closure evidence seam
  - Likely areas: existing BFF/backend logs and `docs/walkthroughs/walkthrough-WF-0080-production-mvp-launch-wedge.md`.
  - Responsibility: preserve one-session traceability and record closure evidence without introducing a new operations product.
- Design tree (dependencies + ordering)
  - 1. Lock the cohort gate contract and zero-side-effect rejection proof before UI polish. `(FR2) (FR3) (FR4)`
  - 2. Lock the bounded `detail_projection` contract at `GET /reviews/{review_id}` before frontend ranking/render work. `(FR6) (FR7) (FR10) (FR11)`
  - 3. Implement detail-page reading-model rendering and honest pending/timeout/failure states against that fixed contract. `(FR5) (FR6) (FR8) (FR9) (FR12)`
  - 4. Add trace correlation/support diagnostics and privacy/retention enforcement on the same wedge surfaces. `(FR13) (FR14)`
  - 5. Capture usefulness and fail-closed closure evidence in the walkthrough artifact only after executable proof exists. `(FR15) (FR16)`
- Deep module guidance
  - Keep ranking semantics in one backend projection seam, not spread across page components and BFF helpers.
  - Keep existing review persistence authoritative; the projection is additive and read-model-only.
  - Keep launch gates tied to existing auth/request seams rather than creating a new onboarding subsystem.

## 7. Edge Cases

- A direct signed backend request bypasses the BFF but uses a valid user signature for a non-cohort identity; the backend must still reject before creating a review. `(US3) (FR3)`
- A cohort member hits the daily quota; the product must block the new attempt clearly and preserve zero new review side effects. `(US1) (US3) (FR4)`
- A review remains `PENDING` after the current polling cap; the page must show honest still-processing guidance instead of implying completion. `(US1) (FR5)`
- A review completes with no blocking or clearly weak cards; the page must render `no critical blockers found` while still showing lower-priority cards below. `(US2) (FR8)`
- Multiple cards share the same assessment status and rating; the projection must fall back to existing call/node order rather than an unstable client-side sort. `(US2) (FR7) (FR10)`
- Existing page-local export/copy output remains deterministic-only while the page shows additive companion guidance or projection framing; the user-visible copy must make that limitation explicit. `(US2) (FR12)`
- A support investigation must explain one failed/disputed session without needing a new admin product or manual inference from unrelated logs. `(US3) (FR13)`

## 8. Testing Decisions (TDD)

- RED first
  - Add a failing BFF/backend test pair proving out-of-cohort users are not yet rejected consistently before downstream review execution. `(US1) (US3) (FR2) (FR3)`
  - Add failing tests proving existing quota/review-disabled behavior stays intact while the cohort gate is added. `(US3) (FR4)`
  - Add failing backend/API tests proving `GET /reviews/{review_id}` does not yet emit the bounded `detail_projection` contract with the required ranking basis and top-3 limit. `(US2) (FR6) (FR7) (FR10)`
  - Add failing frontend tests proving `/app/reviews/[reviewId]` does not yet consume `detail_projection` into the approved headline, top-action ordering, expansion, and honest timeout/failure states. `(US1) (US2) (FR5) (FR8) (FR9)`
  - Add failing verification for page-local export/copy truthfulness and trace-correlation evidence on the wedge path. `(US2) (US3) (FR12) (FR13)`
- Test seams
  - Public BFF submit route and backend `/api/structured-review` submit gate.
  - Public backend `/reviews/{review_id}` response assembly seam.
  - Public BFF detail route and `/app/reviews/[reviewId]` page render path.
  - Walkthrough evidence artifact for usefulness and scope proof.
- What to mock
  - Mock only external dependencies outside the wedge boundary, such as upstream auth providers or external services.
  - Do not mock the review creation, detail response, or ranking seams whose contract WF-0080 exists to prove.
- Minimal test types
  - Backend route/repository integration-ish tests for cohort rejection, quota preservation, projection assembly, and zero-side-effect guarantees.
  - Frontend route/page tests for pending/timeout/failure honesty, top-3 ordering, explicit positive state, and export/copy truthfulness.
  - Walkthrough/manual verification rows for usefulness evidence, privacy/retention checks, scope proof, and support traceability.

## 9. Telemetry (Minimal)

- Minimal telemetry is limited to launch-operability evidence: cohort gate rejects, quota/review-disabled rejects, review id plus trace correlation, pending timeout/failure visibility, and enough identifiers to investigate one cohort session.
- New product analytics, generalized dashboards, and broad usage instrumentation are deferred.

## 10. Deferred / Not in MVP

- Multi-call rollout or generalized launch-platform work.
- Review history/list redesign.
- New persistence hierarchies, whole-review prioritization engines, or broad contract rewrites.
- Admin/operator console or generalized onboarding system.
- Broader export redesign beyond truthful same-page treatment on `/app/reviews/[reviewId]`.
- Usefulness claims that are not attributable to the locked launch cohort and call wedge.

## 11. Open Questions (if any)

none

## 12. Verification / Proceed Gate

- No proceed recommendation is valid unless Phase 2 names and preserves the exact bounded projection seam at `GET /reviews/{review_id}`, the BFF-plus-backend cohort gate, the walkthrough `Usefulness Evidence Log`, and the approved must-ship/deferred split.
- No proceed recommendation is valid if the detail ranking model requires new review persistence tables, whole-review reinterpretation, or BFF/frontend-local ranking semantics instead of the bounded backend projection seam.
- No proceed recommendation is valid if the launch gate happens after review creation or other downstream cost-bearing work begins.
- No implementation-ready or ship recommendation is valid without explicit pass/fail proof for the locked `ERC-2026-PoC` happy path, protected surfaces, timeout/degradation honesty, review-detail priority behavior, support traceability, usefulness evidence, privacy/retention rule, and scope proof.
- No implementation-ready or ship recommendation is valid if 5-10 researcher sessions are only described aspirationally rather than captured in the required evidence artifact.

## 13. Verification Evidence Matrix (Fail-Closed)

| Verification item | Command/test/artifact | Result (`pass`/`fail`/`skipped`) | Evidence pointer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| End-to-end happy-path wedge proof | Phase 2/3 tests plus walkthrough evidence | `fail` (default until executed) | required | invited in-scope researcher can access, submit, wait safely, and open detail |
| Cohort-gate fail-closed proof | targeted BFF/backend gate tests | `fail` (default until executed) | required | out-of-cohort users are blocked before downstream review execution on both entrypoints |
| Quota/reviews-disabled preservation proof | targeted backend/BFF tests | `fail` (default until executed) | required | existing `QUOTA_EXCEEDED` and `REVIEWS_DISABLED` behavior still works inside the wedge |
| Review-detail projection proof | targeted backend tests for `detail_projection` | `fail` (default until executed) | required | `headline_state`, `ordered_card_ids`, `top_action_card_ids`, and ranking basis match contract |
| Top-action render proof | targeted frontend tests or deterministic UI evidence | `fail` (default until executed) | required | top 1-3 actionable cards render above the fold in the approved order |
| Positive-state proof | targeted frontend/API evidence | `fail` (default until executed) | required | explicit `no critical blockers found` renders only when all cards are `ASSESSED` and rated `NOTE` or `SUCCESS` |
| Timeout/degradation honesty proof | targeted pending/failure UI verification | `fail` (default until executed) | required | user sees honest still-processing/failed guidance and retry-or-return-later behavior |
| Export/copy truthfulness proof | targeted frontend tests and copy evidence | `fail` (default until executed) | required | page-local export/copy behavior does not overclaim additive or projection content |
| Support trace proof | trace-correlation test/evidence plus walkthrough note | `fail` (default until executed) | required | one failed or disputed session can be explained from bounded support evidence |
| Privacy/retention proof | walkthrough/manual verification plus code/config evidence | `fail` (default until executed) | required | launch-session inputs/outputs remain only in approved storage/traces with limited access |
| Usefulness gate proof | walkthrough `Usefulness Evidence Log` | `fail` (default until executed) | required | at least 5 logged sessions must be completed, rated `useful`, and record a next revision action |
| Scope proof | baseline-SHA/commit-range diff plus deferred-surface check | `fail` (default until executed) | required | deferred surfaces remain unchanged unless explicitly approved |
| Audit disposition proof | findings-closure ledger | `fail` (default until executed) | required | blocking findings are closed and justified non-blocking findings are closed or rejected with rationale |

## 14. Audit Disposition Ledger

| Review source | Finding | Severity | Planned closure | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Phase 1.2 PRD risk audit | Ranking order and positive-state threshold were not yet explicit enough to be Phase 2-verifiable because `assessment_status` precedence and rating order were implied rather than named | non-blocking | lock the exact `NOT_ASSESSABLE`/`ASSESSED` precedence, the `CRITICAL` -> `WARNING` -> `NOTE` -> `SUCCESS` order, and the exact `no_critical_blockers` rule in the PRD contract | closed | keeps the projection seam bounded and testable without inventing new review state |
| Phase 1.2 PRD risk audit | The usefulness artifact captured rows but did not yet encode the quantitative launch pass threshold from the brainstorm desired outcome | non-blocking | require at least 5 completed `useful` sessions with a stated next revision action for the usefulness gate to pass | closed | preserves the approved wedge closure bar as a Phase 2/3 verification target |

## 15. Changelog

- v0.1 (2026-03-14): Initial PRD from brainstorm.
- v0.2 (2026-03-14): Applied the Phase 1 risk audit by locking exact ranking/headline semantics and the quantitative usefulness pass threshold, then marked the PRD ready for task planning.
