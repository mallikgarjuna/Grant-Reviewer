# WF-0009 — PeerLens Landing Page Tasks

Artifact: task
Version: v0.3
Status: Ready for Implementation
Last Updated: 2026-02-14

## Task Breakdown (Sequential Order)

### Task 1 — Add locked landing demo data module

Goal:
Create a single source of truth for the 3 static demo tabs (labels, snippet text, 4 cards, readiness score) matching the locked spec.

Files to modify:
- `frontend/src/lib/landing-demo.ts` (new)

Acceptance Criteria:
- Exports typed demo data for exactly 3 tabs: `NWO Veni`, `ERC Starting`, `MSCA PF`.
- Each tab includes snippet (80–120 words), 4 cards, and an example readiness score (0–100).
- No references to “rubric” terminology in demo content.

Verification Steps:
- `cd frontend && npm run lint`
- Confirm demo strings match the locked spec content.

Risks (if any):
- Copy drift between spec and code if demo text is duplicated elsewhere.

### Task 2 — Implement accessible demo tabs client component

Goal:
Implement the “static demo” tab switcher as a minimal `use client` component with good keyboard/screen reader behavior.

Files to modify:
- `frontend/src/app/_components/landing/demo-tabs.tsx` (new)
- `frontend/src/lib/landing-demo.ts` (imports)

Acceptance Criteria:
- Tabs are keyboard reachable and activatable; focus-visible is clear.
- Active tab state is local only (no URL state in MVP).
- No third-party tab library is introduced.

Verification Steps:
- `cd frontend && npm run lint`
- `cd frontend && npm run dev` then verify tab switching works with keyboard only.

Risks (if any):
- A11y regressions if roles/aria attributes are incorrect.

### Task 3 — Implement accessible FAQ accordion component

Goal:
Implement the landing FAQ accordion with correct semantics and keyboard support.

Files to modify:
- `frontend/src/app/_components/landing/faq-accordion.tsx` (new)

Acceptance Criteria:
- Accordion toggles are buttons with `aria-expanded` and stable ids.
- Keyboard navigation works; focus styling is visible.

Verification Steps:
- `cd frontend && npm run lint`
- `cd frontend && npm run dev` then verify accordion toggles with keyboard.

Risks (if any):
- Over-building the FAQ into a generic component system (avoid).

### Task 4 — Add minimal `/privacy` page

Goal:
Add a minimal privacy page with the required MVP statements.

Files to modify:
- `frontend/src/app/privacy/page.tsx` (new)

Acceptance Criteria:
- Route `/privacy` exists.
- Includes the required statements:
  - PeerLens does not use proposal snippets to train its models
  - Proposal snippets are retained until the user deletes them (self-serve deletion)
  - Minimal operational logs/backups may be retained up to 30 days

Verification Steps:
- `cd frontend && npm run lint`
- `cd frontend && npm run dev` then open `/privacy`.

Risks (if any):
- Legal wording drift; keep it minimal and consistent with decisions.

### Task 5 — Add MVP “Export your review” action (copy / .txt)

Goal:
Make the “Export your review” promise true with a simple export action on the signed-in review detail page.

Files to modify:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`

Acceptance Criteria:
- Provides “Copy as text” and “Download .txt” for the review content.
- Export includes review id + summary + all cards (criterion + feedback text) in a readable format.
- No PDF export is added in MVP.

Verification Steps:
- `cd frontend && npm run lint`
- Ensure local Clerk env is configured (see `frontend/.env.local.example`) so you can load `/app/reviews/[reviewId]`.
- Open a completed review and export via copy + download.

Risks (if any):
- Clipboard permissions vary by browser; provide a fallback UX if copy fails.

### Task 6 — Add backend delete review endpoint (hard delete) + tests

Goal:
Add an authenticated endpoint to hard-delete a review and its associated data (review cards + snippet) per deletion decisions.

Files to modify:
- `backend/main.py`
- `backend/app/repositories/review_repository.py`
- `backend/app/schemas/api.py` (if a response model is added)
- `backend/tests/test_api.py`

Acceptance Criteria:
- Adds `DELETE /reviews/{review_id}` protected by the existing BFF signature.
- Enforces ownership: only the review owner can delete; otherwise return `REVIEW_NOT_FOUND`.
- Performs hard delete of review + cards + snippet text (per AD 9.4).
- Returns `200` with JSON `{ "ok": true }` on success (simplifies BFF + UI handling in MVP).
- Includes tests covering: successful delete and non-owner delete behavior.

Verification Steps:
- `cd backend && uv run pytest -q`

Risks (if any):
- Cascade delete expectations depend on ORM relationships; ensure the intended rows are removed.

### Task 7 — Add BFF adapter + route support for delete review

Goal:
Expose delete review via the Next.js BFF so the browser never calls FastAPI directly.

Files to modify:
- `frontend/src/lib/bff/adapter.ts`
- `frontend/src/lib/bff/types.ts`
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts`

Acceptance Criteria:
- Adds DELETE support in BFF adapter (currently GET/POST only).
- Adds DELETE handler in `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` that calls FastAPI `DELETE /reviews/{review_id}`.
- Expects backend success response `200 { ok: true }` and treats it as success.
- Returns canonical API errors consistent with existing BFF patterns.

Verification Steps:
- `cd frontend && npm run lint`
- `cd frontend && npm run check:bff`

Risks (if any):
- Keep adapter changes minimal to avoid breaking existing GET/POST flows.

### Task 8 — Add “Delete review” UI on review detail page

Goal:
Add self-serve deletion UX on the review detail page to satisfy the “Delete your data anytime” promise.

Files to modify:
- `frontend/src/app/app/reviews/[reviewId]/page.tsx`
- `frontend/src/lib/review-attempt.ts` (only if needed to clear local draft after deletion)

Acceptance Criteria:
- Shows a “Delete review” action with a simple confirmation step.
- On success, redirects user back to `/app` (results flow ends).
- If delete fails, shows a clear error message without exposing raw internals.

Verification Steps:
- `cd frontend && npm run lint`
- Ensure local Clerk env is configured (see `frontend/.env.local.example`) so you can load `/app/reviews/[reviewId]`.
- Create a review, delete it, then refresh the old review URL and confirm it behaves as “not found”.

Risks (if any):
- Accidental deletes; keep confirmation minimal but explicit.

### Task 9 — Rewrite `/` landing page to PeerLens PRD

Goal:
Replace the current homepage with the conversion-focused PeerLens landing page per PRD (nav, hero, problem, demo, benefits, how-it-works, FAQ, final CTA, footer).

Files to modify:
- `frontend/src/app/page.tsx`
- (Optional) `frontend/src/app/layout.tsx` (metadata/product name only)
- `frontend/src/app/_components/landing/demo-tabs.tsx`
- `frontend/src/app/_components/landing/faq-accordion.tsx`
- `frontend/src/lib/landing-demo.ts`

Acceptance Criteria:
- Nav includes: PeerLens wordmark, `Privacy`, and `Sign In`.
- Primary CTA “Check My Draft Now” routes to `/sign-in`.
- Supported calls are text-only: `NWO Veni · ERC Starting · MSCA PF` (no logos).
- Demo includes the exact label copy:
  - “Examples only. Sign in to get feedback on your proposal text.”
  - “Export your review. Delete your data anytime. See Privacy.”
- Footer is privacy-only.
- No “rubric” terminology appears anywhere on `/`.
- Add telemetry hooks: `data-pl="cta-primary"`, `data-pl="demo-tab"`, `data-pl="faq-toggle"`.

Verification Steps:
- `cd frontend && npm run lint`
- `cd frontend && npm run check:seo`
- `cd frontend && npm run build`
- `cd frontend && npm run dev` then visually verify required sections + links, and verify mobile layout.

Risks (if any):
- Copy over-claims (keep claims conservative and aligned to `/privacy`).

### Task 10 — End-to-end truthfulness smoke test

Goal:
Ensure the landing page promises (“Export… Delete… See Privacy.”) are true end-to-end before considering the landing shippable.

Files to modify:
- None (verification-only)

Acceptance Criteria:
- `/privacy` exists and contains the required statements.
- Review detail page supports export (copy + .txt).
- Review detail page supports delete review (hard delete) and the deleted review becomes inaccessible.
- Landing `/` uses “review criteria” wording (no “rubric”).

Verification Steps:
- `cd backend && uv run pytest -q`
- `cd frontend && npm run lint && npm run check:bff && npm run check:seo && npm run build`
- Ensure local Clerk env is configured (see `frontend/.env.local.example`) for `/sign-in` and authenticated `/app/*` routes.
- Manual: navigate `/` → `/privacy` → create review → `/app/reviews/[id]` export → delete → confirm 404/not-found on refresh.

## Changelog

- v0.1 (2026-02-14): Initial task breakdown from PRD.
- v0.2 (2026-02-14): Re-ordered tasks around landing preconditions; added explicit verification commands; marked Ready for Implementation.
- v0.3 (2026-02-14): Specify delete success response shape; clarify Clerk-dependent verification steps.
