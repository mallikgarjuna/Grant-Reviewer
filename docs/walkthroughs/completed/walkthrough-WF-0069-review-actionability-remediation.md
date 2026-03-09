<!-- docs/walkthroughs/completed/walkthrough-WF-0069-review-actionability-remediation.md -->
# WF-0069 — Review Actionability Remediation

Artifact: walkthrough
Version: v0.3
Status: Done (Phase 3.2 + 3.3 Complete; User-Gated Ship)
Last Updated: 2026-03-09

## 1) Scope + Baseline Anchor

- WF: `WF-0069/review-actionability-remediation`
- Locked remediation boundary: repeated actionability/prioritization failure only, locked wedge `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, `MSCA-PF-2025`
- Implementation baseline range (scope proof anchor): `3247df5...3e60971`
  - baseline start commit: `3247df5` (`WF-0069: ... sync task v0.3 and workflow memory note`)
  - current implementation head: `3e60971` (`WF-0069: ... Part C1 — harden evaluator safety and ID mapping`)

## 2) What Changed

- Task 1 (single-seam tracer proof): service-seam actionable text rewrite for NWO stress path + tracer test
- Task 2 (locked wedge rollout): same service seam extended to ERC/MSCA only + cross-call stress/baseline guards
- Task 3 (review-detail ordering): verified-no-op implementation, added targeted ordering regression + untargeted legacy guard
- Task 4 (deterministic replay evaluator): new evaluator script + fixture-backed tests for pass/fail/tie-handling/fail-closed regression
- Task 5 (this artifact): closure evidence + scope proof + audit-disposition ledger + explicit recommendation state
- Part C1 (post-audit fixes): evaluator DB safety guard + strict item_id↔call_id mapping guard
- Part C1.1 (post-closeout hardening): strict required `item_id -> role` mapping guard to prevent stress-gate bypass via batch-role drift

## 3) Deterministic Replay Commands + Results

Commands run:

```bash
cd backend && ./scripts/reset_test_db.sh
cd backend && uv run pytest tests/test_evaluate_wf_0069_actionability.py
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run python scripts/evaluate_wf_0069_actionability.py --batch ../docs/walkthroughs/evidence/WF-0068/snippet-batch.json --baseline ../docs/walkthroughs/evidence/WF-0068/baseline.json --output /tmp/wf_0069_actionability_eval.json
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0069_wf0068_nwo_actionability_prioritization_stress_proves_narrowest_actionable_seam or wf0069_erc_actionability or wf0069_msca_actionability or wf0069_baseline_non_regression or structured_pipeline_v1_not_assessable_cards_for_missing_context"
cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_api.py -k "wf0069_review_detail_orders_assessed_cards_before_context_gaps or wf0069_review_detail_legacy_ordering_guard"
```

Result:

- Evaluator artifact: `/tmp/wf_0069_actionability_eval.json`
- `overall_pass: true`
- `stress_gate.pass: true`
- `baseline_floor_gate.pass: true`
- `fail_closed_guard.pass: true`
- `tests/test_evaluate_wf_0069_actionability.py`: `6 passed`
- `tests/test_structured_reviewer_service.py` WF-0069 selectors: `7 passed, 16 deselected`
- `tests/test_api.py` WF-0069 selectors: `4 passed, 142 deselected`

Per-item replay outcomes (exact required IDs):

- Stress IDs:
  - `wf0068_nwo_actionability_prioritization_stress`: `revision_actionability=pass`, `prioritization_quality=pass`
  - `wf0068_erc_actionability_prioritization_stress`: `revision_actionability=pass`, `prioritization_quality=pass`
  - `wf0068_msca_actionability_prioritization_stress`: `revision_actionability=pass`, `prioritization_quality=pass`
- Baseline IDs:
  - `wf0068_nwo_baseline_representative`: floor checks pass (`>= weak`)
  - `wf0068_erc_baseline_representative`: floor checks pass (`>= weak`)
  - `wf0068_msca_baseline_representative`: floor checks pass (`>= weak`)
- Fail-closed guard:
  - Not-assessable guard review generated `not_assessable_card_count=1` with explicit reason; guard passed.

## 4) Scope Proof

`git diff --name-only 3247df5...3e60971`:

- `backend/app/services/structured_reviewer_service.py` (Task 1/2 single primary seam; call-locked actionable rewrite)
- `backend/tests/test_structured_reviewer_service.py` (Task 1/2 tracer + wedge stress/baseline regressions)
- `backend/tests/test_api.py` (Task 3 targeted ordering + untargeted legacy guard)
- `backend/scripts/evaluate_wf_0069_actionability.py` (Task 4 deterministic replay evaluator)
- `backend/tests/test_evaluate_wf_0069_actionability.py` (Task 4 evaluator tests)
- `backend/tests/fixtures/wf_0069_actionability_cases.json` (Task 4 deterministic fixture matrix)
- `docs/tasks/completed/task-WF-0069-review-actionability-remediation.md` (Task completion checkboxes)

No launch-floor ops, broader trust-surface redesign, assisted extraction, broad call expansion, or generic prompt-tuning files were changed.

## 5) Audit-Disposition Ledger

### Blocking findings

| Finding ID | Source | Disposition | Rationale |
| :--- | :--- | :--- | :--- |
| WF0069-B-001 | Phase 3.2 technical audit | `closed` | `backend/scripts/evaluate_wf_0069_actionability.py` now fail-closes destructive DB reset unless `DATABASE_URL` targets a `test` database. |
| WF0069-B-002 | Phase 3.2 technical audit | `closed` | Evaluator now enforces exact required `item_id -> call_id` mapping to prevent false cross-call closure. |
| WF0069-B-003 | Phase 3 closeout technical audit | `closed` | Evaluator now enforces exact required `item_id -> role` mapping to prevent stress-gate bypass via role drift/mislabeled batch items. |

### Non-blocking findings/comments

| Finding ID | Source | Disposition | Rationale |
| :--- | :--- | :--- | :--- |
| WF0069-NB-001 | Task execution note | `closed` | DB-backed selector contention observed once due parallel invocation; closed by serial reruns on isolated test DB with deterministic pass evidence. |
| WF0069-NB-002 | Task execution note | `closed` | Transient Postgres startup timing issue immediately after DB reset; closed by rerun once container reached healthy state. |
| WF0069-NB-003 | Phase 3.2 technical audit | `rejected_with_rationale` | Tie-handling is represented at baseline-floor comparison (`_meets_floor`) and covered by tests; no additional priority-field contract change is required in this narrow remediation WF. |

## 6) Recommendation State

- Proceed recommendation (Phase 3 complete): `pass`
- Ship recommendation: `pass_pending_user_ship_it`
  - Reason: Replay pass, baseline-floor guard pass, fail-closed guard pass, and audit-disposition ledger fully resolved.
  - Final gate: explicit user `ship it` before push/PR/merge.
