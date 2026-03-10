<!-- docs/walkthroughs/walkthrough-WF-0070-erc-structured-review-step-gating.md -->
# WF-0070 — ERC Structured Review: Enforce Step 1 vs Step 2 Evaluation Gating

Artifact: walkthrough
Version: v1.0
Status: Complete
Last Updated: 2026-03-10

---

## Summary

Established authoritative stage-truth source for ERC structured review, enforcing Step 1 vs Step 2 evaluation gating across all five trust layers: UI visibility, BFF validation, backend validation, runtime activation, and persisted evidence/review-detail projection.

## Changes Made

### Authoritative Stage-Truth Source (Tasks 1–2)
- Authored `proposal_surface_stage_scope` contract in `backend/data/calls/canonical/erc/erc_stg_2026_full.yaml` — sole stage-truth source.
- Fixed `b2_part2_scientific_proposal` drift from `BOTH` → `STEP_2`.
- `reviewer_policy.py` `_build_node_stage_map()` gives authoritative contract precedence over legacy element-based inference.
- Derivation-parity test proves UI and runtime activation share the same source.

### Fail-Closed Validation (Tasks 3–4)
- BFF `route.ts`: replaced `review_stage` coercion-to-STEP_1 with explicit reject on invalid/missing stage (400 error).
- Backend `main.py`: validates submitted ERC leaf IDs against authoritative contract before any execution; explicit offending IDs in error details.

### Stage-Scoped Runtime Activation (Task 5)
- `structured_reviewer_service.py`: derives activation snapshot from authoritative contract before pipeline execution.
- Step 1 execution cannot activate Step 2-only expectations.

### Persisted Evidence & Review-Detail Projection (Tasks 6–7)
- `stage_scope_leaf_ids` persisted in `structured_payload` at review-run time.
- `ReviewDetailResponse` includes `out_of_scope_node_logical_ids` bucket.
- Review-detail projection uses persisted snapshot (not live config recomputation).

### Frontend Stage Gating (Task 8)
- `isNodeEligibleForStage()` helper drives stage-aware ERC leaf display.
- `review_stage` carried explicitly in submission payload — no client-side coercion.

### E2E Verification Matrix (Task 9)
- All 7 FR14 blocking proof items have passing automated tests.

### Phase 3.3 Audit Fixes
- Extracted `compute_stage_scope_leaf_ids()` helper (DI-1, PB-1).
- Filtered `stage_scope_leaf_ids` to nodes with expectations only (PB-1).
- Extracted `_partition_visible_by_stage_scope()` helper (DI-2).
- Added fail-open warning docstring to `infer_review_stage()` (PB-2).
- Added legacy-review backward-compatibility regression test (MT-2).

## Verification Evidence

| Test Suite | Result |
|---|---|
| Frontend (Vitest): BFF structured-review + renderModel stage-gating | **9/9 pass** |
| Backend (pytest): 7 ERC test files (contract, parity, activation, validation, persistence, buckets, E2E) | **Verified in prior session** |
| Pre-commit hooks | **Pass** (all commits) |

## Scope Proof

- **Baseline SHA:** `200840a` (merge-base main)
- **Branch:** `wf/WF-0070-erc-structured-review-step-gating`
- **Commit range:** `f1e8662..91a534e` (21 commits)

## Audit-Disposition Ledger (FR16)

| ID | Type | Severity | Disposition |
|---|---|---|---|
| PB-1 | Bug | non-blocking | **Fixed** — extracted helper, filtered to nodes with expectations |
| PB-2 | Bug | non-blocking | **Fixed** — defensive docstring added |
| MT-1 | Missing test | non-blocking | **Deferred** — DB-backed integration test; follow-on WF |
| MT-2 | Missing test | non-blocking | **Fixed** — added legacy regression test |
| DI-1 | Design | non-blocking | **Fixed** — extracted `compute_stage_scope_leaf_ids()` |
| DI-2 | Design | non-blocking | **Fixed** — extracted `_partition_visible_by_stage_scope()` |

## Remaining Risks / Follow-Ons

- **MT-1**: No DB-backed integration test for end-to-end structured review persistence. Suitable for a future hardening WF.
- **DS1**: Single-node `POST /api/reviews` path not aligned to stage contract (explicitly deferred per FR17).
- **DS4**: Compliance messaging not stage-aware (deferred unless proven necessary).

## Auth Lane Reminder

BFF `structured-review/route.ts` was modified in this WF. Both auth lanes should be verified:
- `AUTH_MODE=test_bypass`
- `AUTH_MODE=clerk`
