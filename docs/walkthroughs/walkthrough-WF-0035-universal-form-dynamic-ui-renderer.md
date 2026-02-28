# WF-0035 — Universal Form: Dynamic UI renderer

Artifact: walkthrough
Version: v0.1
Status: Draft
Last Updated: 2026-02-28

## Scope Delivered

- Replaced route-level submit entrypoint with `UniversalSubmitForm` dynamic renderer.
- Added structured-call gating loader with deterministic timeout + concurrency defaults.
- Added render-model guards for nested nodes and missing `logical_id` contract breaks.
- Added metadata contract support (adapter + BFF metadata proxy route) and UI enrichment path.
- Added per-call domain selector bridge and compliance 422 hard-block UX.
- Added per-call draft isolation storage and active-call-only draft clear on successful submit.
- Restored warning bypass modal parity and added telemetry events for key transitions.
- Removed legacy `VeniSubmitForm` component/tests and switched UI test command to universal form.

## Verification Evidence (2026-02-28)

- Frontend universal submit suite:
  - `cd frontend && nvm use && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx`
  - Result: `14 passed`.
- Backend structured-review API subset (safe test DB):
  - `cd backend && docker compose -f docker-compose.test.yml up -d`
  - `export DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable'`
  - `PYTHONPATH=. uv run pytest tests/test_api.py -k "structured_review"`
  - Result: `14 passed, 45 deselected`.
- UI regression smoke:
  - `cd frontend && nvm use && npm run test:ui`
  - Result: `18 passed`.

## MVP Acceptance Matrix (Flat Structured Calls)

| Call | Dynamic render evidence | Compliance precheck evidence | Submit/create-review evidence | Status | Gaps |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Veni (`nwo_veni_2025_preproposal`) | `src/components/submit/UniversalSubmitForm.test.tsx` (`renders dynamic node fields from API order`, `uses metadata route labels when available`) | `src/components/submit/UniversalSubmitForm.test.tsx` (`submits selected domain and blocks on compliance 422`, `warning bypass modal gates submit until confirmation`) | `src/components/submit/UniversalSubmitForm.test.tsx` (`sends Idempotency-Key header during submit`, `emits telemetry...`) + backend `tests/test_api.py -k structured_review` | Pass | None found in current automated coverage. |
| Second flat structured call (`other_call` test fixture) | `src/components/submit/UniversalSubmitForm.test.tsx` (`shows domain selector only for calls with configured domain options`, `keeps draft values isolated per selected call`) | `src/components/submit/UniversalSubmitForm.test.tsx` (`clears only active call draft on submit success`, compliance path exercised with same universal flow and no domain selector) | `src/components/submit/UniversalSubmitForm.test.tsx` (`clears only active call draft on submit success`) | Pass | Test fixture call, not a production YAML-backed named program call yet. |

## Known Risks

- Telemetry currently emits via `console.info`; migration to centralized analytics sink is still pending.
- Domain options map is interim/static and must be kept in sync with call code evolution.
- Metadata enrichment is defensive, but schema drift can still reduce label quality (safe fallback remains).
