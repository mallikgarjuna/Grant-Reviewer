<!-- docs/walkthroughs/completed/walkthrough-WF-0064-opted-in-hierarchical-submit-proof-closure.md -->
# WF-0064 — Opted-In Hierarchical Submit Proof Closure

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-08

Type: feature

## Scope

WF-0064 closed the proof-path contract for opted-in hierarchical submit behavior on `MSCA-PF-2025` only, fail-closed.

## What Changed

1. Submit UI now renders visible supporting nodes as read-only on the proof path while preserving editable parity for non-opted-in calls.
2. Draft handling blocks supporting-node writes for the proof path and avoids silent stale-supporting cleanup side effects.
3. Backend fail-closed behavior remains unchanged for crafted supporting-node primary payloads (`SUPPORTING_NODE_NOT_ALLOWED`).
4. Review-detail classification uses the shared role-aware seam (`nodeRoles` + `renderModel`) rather than page-local fallbacks.
5. Review detail surfaces visible supporting nodes under `Visible but not part of this review` and keeps `supporting_context_node_logical_ids` empty for this WF.
6. Rollback parity is proven: disabling the existing opt-in seam restores legacy behavior without a second activation mechanism.

## Verification Evidence

- `cd backend && uv run pytest -m no_db` -> PASS (`230 passed, 153 deselected`).
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx src/lib/submit/nodeRoles.test.ts src/lib/submit/renderModel.test.ts 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0064_"` -> PASS (`11 passed, 53 skipped`).
- `cd backend && DATABASE_URL=sqlite:///./wf0064_api_test.db uv run pytest tests/test_api.py -k "wf0064_check_compliance_rejects_supporting_nodes_with_existing_error or wf0064_structured_review_rejects_supporting_nodes_with_existing_error"` -> PASS.
- `pre-commit run --all-files` -> PASS.
- Agentic browser validation (local dev, bypass lane) confirms `/app` loads and protected flow remains reachable.

Auth-lane reporting (from Part C2 gate):
- `test_bypass` Playwright lane executed and passed.
- `clerk` Playwright lane credentialed-login flow was skipped in this run (no `E2E_CLERK_TEST_EMAIL`/`E2E_CLERK_TEST_PASSWORD` provided, and local single-worktree `next dev` lock prevented a parallel mode-isolated server spin-up).

## Outcome

WF-0064 is closed as an opted-in proof-path hardening workflow for `MSCA-PF-2025` with fail-closed backend behavior preserved and no supporting-context activation introduced.
