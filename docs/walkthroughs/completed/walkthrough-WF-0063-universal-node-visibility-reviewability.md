<!-- docs/walkthroughs/completed/walkthrough-WF-0063-universal-node-visibility-reviewability.md -->
# WF-0063 — Universal Node Visibility Reviewability

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-08

Type: feature

## Scope

WF-0063 completed the proof-call-first split between structural visibility and primary reviewability for `MSCA-PF-2025`, while preserving legacy behavior for non-opted-in calls.

## What Changed

1. Added canonical split-role contract support:
   - `proposal_nodes[*].node_role` now distinguishes `PRIMARY` from `SUPPORTING`.
   - `runtime_config.split_visibility_reviewability_enabled` gates rollout explicitly.
2. Applied source-grounded proof-call authoring to `MSCA-PF-2025` without inventing evaluation criteria/elements for supporting nodes.
3. Exposed role-aware completeness through config, flat nodes, and tree APIs while preserving compatibility fields such as `has_expectations`.
4. Centralized backend/frontend role derivation so render, submit, and review-detail behavior does not fork into call-specific allowlists.
5. Updated universal submit behavior so supporting nodes can stay visible in the proof call while primary review/compliance payloads remain primary-only.
6. Added fail-closed backend guards and review-detail labeling so supporting nodes do not silently participate in primary review outputs.
7. Closed the workflow with proof-call parity and rollback coverage proving that disabling the opt-in seam restores legacy behavior without YAML re-authoring.

## Verification Evidence

- Commit history shows the full WF task sequence landed and merged to `main`, ending at merge commit `d48b507` for `WF-0063`.
- `cd backend && DATABASE_URL='postgresql://grant:grant@127.0.0.1:5433/grant_reviewer_test?sslmode=disable' LLM_MODE=stub uv run pytest tests/test_api.py -k "wf0063_proof_call_parity_holds_across_api_submit_and_review_detail or wf0063_non_opted_in_calls_preserve_legacy_behavior or wf0063_proof_call_opt_in_rollback_restores_legacy_behavior"` -> PASS
- `cd frontend && npx vitest run src/components/submit/UniversalSubmitForm.test.tsx -t "wf0063_proof_call_parity_holds_across_api_submit_and_review_detail"` -> PASS
- `cd frontend && npx vitest run 'src/app/app/reviews/[reviewId]/page.test.tsx' -t "wf0063_non_opted_in_calls_preserve_legacy_behavior"` -> PASS

## Outcome

WF-0063 is complete as a proof-call contract correction, not as a full supporting-context review model. The repo inconsistency was documentary: task execution and merge evidence existed, but the walkthrough and index status had not been closed.
