<!-- docs/memory/tools/frontend.md -->
# Frontend Tooling

- **NVM requirements:** Use `nvm use` (which uses `.nvmrc`) before running `npm` or `npx`. If there is no `nvm`, scaffold/build locally and commit the generated `frontend/` directory.

- **2026-03-06:** Submit form now has two selects (`Funding Call`, `Review Stage`); tests must query by label instead of generic `getByRole("combobox")` to avoid ambiguity after stage-aware UI changes.

- **2026-03-06:** Review-stage options should be derived from explicit metadata stage signals (`review_stage` values), not shown unconditionally. Why: single-stage calls (e.g., Veni) must not offer `Step 2` in UI.

- **2026-03-06:** On call switch, review-stage state must fail closed to `STEP_1` before metadata resolves; otherwise metadata failures can leak stale `STEP_2` options from the previously selected call.

- **2026-03-08:** The 2026-03-06 "hierarchical calls are still client-blocked" note is stale after WF-0063. Current remaining gap is narrower: opted-in calls such as `MSCA-PF-2025` already render split-role hierarchical nodes, but supporting nodes are still editable while being excluded from compliance/submit payloads, cleared on successful submit, and omitted from review-detail supporting-context coverage. Why: future sessions should treat the main issue as proof-path contract/UX closure, not renderer unblocking.

- **2026-03-08:** Added safe dev/test auth bypass for protected `/app` and `/api/bff/*`: `AUTH_MODE=test_bypass` with signed `gr_test_auth` token, hard-blocked in production, and secret-required (`TEST_AUTH_SECRET`). Why: enables deterministic Playwright/agentic browser validation without Clerk sign-in UI while preserving fail-closed defaults.

- **2026-03-08:** In `AUTH_MODE=test_bypass`, `/sign-in` now server-redirects straight to requested `/app*` target when `TEST_AUTH_DEFAULT_USER_ID` is configured. Why: avoids local blank/sign-in stalls during agentic browser validation while staying fail-closed if bypass config is invalid.

- **2026-03-08:** New Playwright auth E2E lane uses `playwright.config.ts` with port `3000` default and `reuseExistingServer` outside CI. Why: local runs should reuse the active `npm run dev` server to avoid Next.js `.next/dev/lock` conflicts.

- **2026-03-08:** Review-detail boundary arrays (`visible_not_reviewed_node_logical_ids`, `no_generated_cards_node_logical_ids`) must be treated as authoritative when present, even if empty; empty arrays are explicit "none", not a signal to fall back to WF-0064 inference. Why: fallback-on-empty reintroduces hidden coupling and violates fail-closed trust-surface behavior.
