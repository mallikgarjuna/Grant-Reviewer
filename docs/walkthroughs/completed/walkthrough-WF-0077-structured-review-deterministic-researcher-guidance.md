<!-- docs/walkthroughs/completed/walkthrough-WF-0077-structured-review-deterministic-researcher-guidance.md -->
# WF-0077 — Structured Review Deterministic Researcher Guidance

Artifact: walkthrough
Version: v0.1
Status: Done (Phase 3 closeout complete; user-gated ship)
Last Updated: 2026-03-13

## 1) Scope + Baseline Anchor

- WF: `WF-0077/structured-review-deterministic-researcher-guidance`
- Locked implementation boundary: `ERC-2026-PoC` only, `StructuredReviewerService` plus service-level tests, no evaluator/mapper/legacy-review/frontend implementation widening
- Implementation baseline range (scope proof anchor): `99eb344...12ee6f9`
  - Task 1 commit: `99eb344` (`WF-0077: structured-review-deterministic-researcher-guidance — Task 1 — rewrite ERC PoC guidance`)
  - Task 2 commit: `12ee6f9` (`WF-0077: structured-review-deterministic-researcher-guidance — Task 2 — fail closed on weak source surfaces`)

## 2) What Changed

- `backend/app/services/structured_reviewer_service.py`
  - Added an `ERC-2026-PoC`-only deterministic guidance rewrite for fully resolved subordinate-prompt feedback.
  - Preserved existing raw machine feedback handling outside the researcher-facing `feedback_text` rewrite seam.
  - Hardened the same seam to fail closed when prompt source surfaces are missing, unresolved, or duplicated into an unusable source surface.
- `backend/tests/test_structured_reviewer_service.py`
  - Added RED/GREEN Task 1 regressions for actionable ERC PoC guidance and machine-reason passthrough.
  - Added Task 2 regressions for non-targeted passthrough plus missing-source, unresolved-ID, and duplicate-source fallback honesty.
  - Updated the adjacent WF-0076 runtime-snapshot assertion so it still proves live canonical prompt carriage without forcing the superseded prompt-list presentation contract.

## 3) Verification Commands + Results

Commands run:

```bash
cd backend && uv run ruff check app/services/structured_reviewer_service.py tests/test_structured_reviewer_service.py
cd backend && uv run ruff format --check app/services/structured_reviewer_service.py tests/test_structured_reviewer_service.py
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_actionable_guidance"
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0077_contract_erc_poc_reason_passthrough"
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0077_contract_non_targeted_passthrough or wf0077_contract_erc_poc_fallback_missing_source or wf0077_contract_erc_poc_fallback_unresolved_prompt or wf0077_contract_erc_poc_fallback_duplicate_source"
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0076 or wf0077_contract_"
cd backend && ./scripts/reset_test_db.sh
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py
rg -n "feedback_text" frontend/src/app/app/reviews/[reviewId]/page.tsx
git diff --name-only main...HEAD
```

Results:

- `ruff check`: pass
- `ruff format --check`: pass
- Task 1 guidance selector: RED captured `1 failed, 29 deselected`, then GREEN rerun passed
- Task 1 reason passthrough selector: pass
- Task 2 fallback selector bundle: `4 passed, 30 deselected`
- WF-0076/WF-0077 local seam bundle: `9 passed, 25 deselected`
- Full `tests/test_structured_reviewer_service.py`: `34 passed`
- Frontend necessity check: `frontend/src/app/app/reviews/[reviewId]/page.tsx` still renders `card.feedback_text` directly at lines `110` and `1044`

## 4) Scope Proof

`git diff --name-only 99eb344...12ee6f9`:

- `backend/app/services/structured_reviewer_service.py`
- `backend/tests/test_structured_reviewer_service.py`
- `docs/memory/tools/testing.md`

No evaluator, compatibility mapper, legacy-review service, API schema, or frontend implementation files changed for the WF-0077 behavior slice.

## 5) Audit-Disposition Ledger

### Blocking findings

| Finding ID | Source | Disposition | Rationale |
| :--- | :--- | :--- | :--- |
| WF0077-B-001 | Phase 3.1 RED proof | `closed` | Added `test_wf0077_contract_erc_poc_actionable_guidance` and captured the pre-fix WF-0076-style prompt-list output before implementing the deterministic rewrite. |
| WF0077-B-002 | Phase 3.2 technical audit | `closed` | The final service path now emits deterministic guidance only for fully usable `ERC-2026-PoC` prompt surfaces and otherwise falls back to WF-0076-style rendering. |

### Non-blocking findings/comments

| Finding ID | Source | Disposition | Rationale |
| :--- | :--- | :--- | :--- |
| WF0077-NB-001 | Task execution note | `closed` | Added a memory note after one accidental parallel DB-backed pytest run produced invalid `UndefinedTable`/duplicate-enum evidence; final verification was rerun serially after `reset_test_db.sh`. |
| WF0077-NB-002 | Task 3 conditional check | `closed` | No frontend follow-on is needed because the live page still renders `card.feedback_text` directly. |

## 6) Recommendation State

- Proceed recommendation (Phase 3 closeout): `pass`
- Ship recommendation: `pass_pending_user_ship_it`
  - Reason: implementation, fail-closed fallback proof, non-targeted-call safety, and explicit frontend-no-op verification are complete; the remaining gate is explicit user approval before `ship it`.
