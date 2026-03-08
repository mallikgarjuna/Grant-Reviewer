<!-- docs/tasks/task-WF-0067-review-trust-surface-closure.md -->
# WF-0067 — Review Trust Surface Closure

Artifact: task
Version: v0.1
Status: Draft
Last Updated: 2026-03-08

Type: feature

## Task Breakdown (Sequential Order)

### [ ] Task 1 — Backend trust contract for card-level source basis and reviewed section

Goal:
Expose the minimum card-level trust fields on the backend review-detail seam so the UI can render evaluation criterion/element, reviewed section context, and authoritative source-basis state without frontend inference.
Slice: backend-contract
User Stories: US1, US3, US4
PRD Requirements: FR1, FR2, FR3, FR4, FR8, FR9, FR10, FR12, FR13
Depends on: none
Enables: 2, 4, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/main.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_api.py`
May touch files:
- `backend/app/repositories/review_repository.py`
Out of scope: frontend rendering, positive supporting-context labels, non-review-detail APIs, new call definitions
Stop if: authoritative `source_hint` data is not reachable from the review-detail assembly seam without introducing new persistence or call-authoring work
Session boundary after: no
Acceptance Criteria:
- `GET /reviews/{review_id}` returns card-level `source_basis_label` and `source_basis_state` with backend precedence `evaluation element source_hint` -> `criterion source_hint` -> explicit unavailable state.
- The backend contract preserves existing reviewed section context (`node_title` / ordered node label path) and keeps `NOT_ASSESSABLE` fields explicit.
- Representative backend coverage exists for `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- Backend fail-closed coverage proves unavailable and `legacy_fallback` card states without synthesizing basis text.
TDD Plan: RED in `backend/tests/test_api.py` for representative review-detail responses missing the new source-basis contract; GREEN in `backend/main.py` and, only if needed, `backend/app/repositories/review_repository.py`; REFACTOR in `backend/app/schemas/api.py` to keep the response model strict and readable.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0067 or source_basis or review_detail"`
- `cd backend && uv run pytest tests/test_api.py -k "nwo_veni_2025_preproposal or erc_stg_2026_full or MSCA-PF-2025"`
Risks (if any): The source-basis precedence may be implemented too far from the response seam, leaving Phase 3 with schema-only proof instead of public-contract proof.

### [ ] Task 2 — Tracer bullet: preserve trust fields through the BFF review-detail route

Goal:
Prove an end-to-end MVP path for one representative review detail by carrying the backend trust contract through the BFF route without inventing stronger semantics.
Slice: tracer-bullet
User Stories: US1, US3, US4
PRD Requirements: FR3, FR4, FR8, FR9, FR10, FR12, FR13
Depends on: 1
Enables: 3, 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`
- `frontend/src/lib/bff/types.ts`
- `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts`
May touch files:
- `frontend/src/lib/bff/adapter.ts`
Out of scope: page copy changes, review-card styling, broad frontend refactors, parallel fetch redesign
Stop if: the BFF needs to guess `source_basis_state`, supporting-context roles, or boundary semantics that are absent from the backend response
Session boundary after: no
Acceptance Criteria:
- The BFF preserves card-level `source_basis_label` and `source_basis_state` exactly as supplied by the backend.
- The BFF preserves explicit fail-closed states needed downstream, including `legacy_fallback`, unavailable source basis, and empty supporting-context role data.
- A dedicated BFF route test proves the representative end-to-end tracer bullet for at least one supported call and one unavailable-basis fallback card.
TDD Plan: RED in new `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts` for dropped or synthesized trust fields; GREEN in `route.ts`; REFACTOR in `frontend/src/lib/bff/types.ts` to keep the normalized client contract aligned.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts'`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' -t "wf0067"`
Risks (if any): If the BFF continues to derive trust semantics locally, the frontend can pass tests while violating the PRD’s seam-proof requirement.

### [ ] Task 3 — Render card-level trust metadata in the primary reading flow

Goal:
Make each review card truthfully display the mapped evaluation criterion/element, reviewed section context, official source basis when available, and explicit `NOT_ASSESSABLE` state in the main reading flow.
Slice: card-render
User Stories: US1, US2
PRD Requirements: FR1, FR2, FR3, FR4, FR5, FR7, FR10, FR12
Depends on: 2
Enables: 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/components/review/ReviewCard.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `frontend/src/components/review/ScoreBadge.tsx`
Out of scope: richer explanatory prose, export/history redesign, submit-flow education, generic explainability affordances
Stop if: meeting the card-level trust requirement requires redesigning the page shell or introducing new layout primitives outside the review-detail reading flow
Session boundary after: no
Acceptance Criteria:
- Each rendered card shows the evaluation criterion, evaluation element, reviewed section label, and source-basis line or explicit unavailable/legacy limitation copy.
- `NOT_ASSESSABLE` cards remain visibly distinct and do not read like normal assessed findings.
- The page-level tests cover at least one card with available source basis and one card with unavailable source basis within the same review detail.
TDD Plan: RED in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx` for missing card-level trust metadata; GREEN in `ReviewCard.tsx` and `page.tsx`; REFACTOR by removing duplicated label assembly in the render path if it appears during implementation.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "source basis|Not assessable|Reviewed section"`
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0067"`
Risks (if any): Card-level copy can accidentally drift into polished explanation text that obscures the launch-blocking trust facts.

### [ ] Task 4 — Backend boundary metadata for fail-closed reviewed vs visible-but-not-reviewed vs no-card states

Goal:
Close the backend proof gap around review-detail boundary honesty so the frontend can distinguish reviewed sections, visible-but-not-reviewed sections, and sections with no generated cards without heuristics.
Slice: boundary-contract
User Stories: US2, US3, US4
PRD Requirements: FR5, FR6, FR7, FR8, FR9, FR10, FR12, FR13, FR15
Depends on: 1
Enables: 5, 6
Parallelizable: no
Files to modify:
Must touch files:
- `backend/main.py`
- `backend/app/repositories/review_repository.py`
- `backend/tests/test_api.py`
May touch files:
- `backend/app/schemas/api.py`
Out of scope: positive supporting-context expansion, submit-time supporting-node capture, generic coverage telemetry
Stop if: distinguishing `visible but not reviewed` from `no generated cards` requires new database schema, new review engine output, or inferred supporting semantics
Session boundary after: no
Acceptance Criteria:
- The backend review-detail seam exposes enough explicit boundary metadata to keep `visible but not reviewed` distinct from `no generated cards`.
- Supporting-context labels remain fail-closed: empty or absent authoritative role metadata does not become a positive `supporting context` claim.
- Backend tests cover representative fail-closed cases, including zero positive supporting-context labels and a zero-card visible-section scenario.
TDD Plan: RED in `backend/tests/test_api.py` for collapsed non-reviewed states and inferred supporting labels; GREEN in `backend/main.py` and `backend/app/repositories/review_repository.py`; REFACTOR by consolidating boundary derivation helpers instead of duplicating state mapping.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "visible and not reviewed or zero_card or supporting_context"`
- `cd backend && uv run pytest tests/test_api.py -k "legacy_fallback or mixed_version_review"`
Risks (if any): Boundary logic can accidentally overfit one representative call and fail the locked three-call wedge.

### [ ] Task 5 — Frontend boundary and limitation surfaces stay truthful without positive supporting inference

Goal:
Render page-level coverage and limitation surfaces that stay honest about reviewed, visible-but-not-reviewed, no-card, and legacy/fallback states while keeping positive supporting labels optional.
Slice: boundary-render
User Stories: US2, US3
PRD Requirements: FR5, FR6, FR7, FR10, FR11, FR12, FR15
Depends on: 3, 4
Enables: 6
Parallelizable: no
Files to modify:
Must touch files:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
- `frontend/src/lib/submit/renderModel.ts`
May touch files:
- `frontend/src/components/review/ReviewSummary.tsx`
Out of scope: non-blocking explainer polish, new summary widgets, generic design-system cleanup
Stop if: truthful boundary rendering cannot be achieved without widening the page contract or changing submission-time semantics
Session boundary after: no
Acceptance Criteria:
- The page distinguishes reviewed sections, visible-but-not-reviewed sections, and sections with no generated cards when the contract distinguishes them.
- The page shows explicit limitation copy for unavailable basis, `legacy_fallback`, and mixed-version states in the main review-detail reading flow.
- The UI passes when representative fixtures provide zero positive supporting-context labels and never fabricates one.
TDD Plan: RED in `frontend/src/app/app/reviews/[reviewId]/page.test.tsx` for collapsed non-reviewed states or inferred supporting labels; GREEN in `page.tsx` and `frontend/src/lib/submit/renderModel.ts`; REFACTOR by tightening the page view-model helpers after the new states are green.
Verification Steps:
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "Not reviewed sections|legacy fallback|mixed-version|supporting context"`
- `cd frontend && npm test -- --runInBand 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "no generated cards|visible but not reviewed"`
Risks (if any): The page can accidentally hide an important limitation in a summary-only block, which would fail the PRD even if the raw state exists.

### [ ] Task 6 — Representative proof closure for the launch-blocking trust surfaces only

Goal:
Finish WF-0067 with deterministic proof across the locked representative calls and fail-closed states, without widening into non-blocking trust polish or adjacent platform work.
Slice: proof-closure
User Stories: US3, US4
PRD Requirements: FR8, FR9, FR10, FR11, FR14, FR15
Depends on: 4, 5
Enables: none
Parallelizable: no
Files to modify:
Must touch files:
- `backend/tests/test_api.py`
- `frontend/src/app/api/bff/reviews/[reviewId]/route.test.ts`
- `frontend/src/app/app/reviews/[reviewId]/page.test.tsx`
May touch files:
- `docs/walkthroughs/walkthrough-WF-0067-review-trust-surface-closure.md`
Out of scope: additional calls, assisted extraction, supporting-context semantics expansion, export/history work, generic trust-platform work
Stop if: a required proof surface is missing for one of the three locked calls or the only path to green is broadening scope beyond review detail
Session boundary after: yes
Acceptance Criteria:
- Automated proof covers exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025` for the launch-blocking trust surfaces.
- Automated proof covers fail-closed unavailable source basis, `legacy_fallback`, mixed per-card basis availability, zero positive supporting-context labels, and the distinct no-card boundary.
- No task adds scope for non-blocking trust improvements beyond what is required to make the blocking surfaces truthful and testable.
TDD Plan: RED by adding missing representative proof cases at backend, BFF, and render seams; GREEN by applying the smallest code fixes left from Tasks 1-5; REFACTOR by deleting any temporary test scaffolding that overstates semantics after the proof matrix is green.
Verification Steps:
- `cd backend && uv run pytest tests/test_api.py -k "wf0067 or nwo_veni_2025_preproposal or erc_stg_2026_full or MSCA-PF-2025"`
- `cd frontend && npm test -- --runInBand 'src/app/api/bff/reviews/[reviewId]/route.test.ts' 'src/app/app/reviews/[reviewId]/page.test.tsx'`
- `git diff --name-only HEAD~ -- backend frontend | rg -v '(^backend/|^frontend/)'`
Risks (if any): If proof is summarized only in prose instead of seam-specific passing tests, WF-0067 could be declared ready while a trust-surface regression remains unproven.

## Changelog

- v0.1 (2026-03-08): Initial task breakdown from PRD.
