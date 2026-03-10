<!-- docs/walkthroughs/walkthrough-WF-0072-e2e-trust-proof-nwo-erc-msca.md -->
# WF-0072 — E2E Trust Proof for Representative NWO/ERC/MSCA Flows

Artifact: walkthrough
Version: v1.0
Status: Completed
Last Updated: 2026-03-10

## Summary

WF-0072 implemented and verified the representative trust-proof bundle for:
- `nwo_veni_2025_preproposal`
- `erc_stg_2026_full`
- `MSCA-PF-2025`

Coverage includes protected happy paths, protected fail-closed negatives, policy blocking at user surface plus backend zero-side-effect pairing, and closure-gate validator enforcement.

## Baseline SHA Or Commit Range

- baseline sha for Phase 3 implementation: `2e089df`
- commit range for the WF-0072 implementation claim: `2e089df..af45a1f`
- branch: `wf/WF-0072-e2e-trust-proof-nwo-erc-msca`
- matrix closure source: `docs/walkthroughs/evidence/WF-0072/verification-matrix.json`

## Verification Evidence

- Matrix validator (closure + protected-lane parity):
  - `cd backend && uv run python scripts/validate_wf_0072_bundle.py --matrix ../docs/walkthroughs/evidence/WF-0072/verification-matrix.json --require-protected-lanes --require-closure`
- Representative protected NWO happy path:
  - `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-nwo-happy-path.spec.ts --project=chromium`
- Representative protected MSCA happy path:
  - `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-msca-happy-path.spec.ts --project=chromium`
- Protected missing `key_outputs` fail-closed:
  - `cd frontend && AUTH_MODE=test_bypass TEST_AUTH_SECRET=test-secret-key-32-chars-minimum-a npx playwright test e2e/wf-0072-protected-submit.spec.ts --project=chromium`
- Policy-blocking backend zero-side-effect pairing:
  - `cd backend && ./scripts/reset_test_db.sh && DATABASE_URL=postgresql://grant:grant@localhost:5433/grant_reviewer_test?sslmode=disable uv run pytest tests/test_api.py -k "wf0072 and (quota or reviews_disabled)" -v`

## Matrix Closure Status

- representative lock: enforced (`nwo_veni_2025_preproposal`, `erc_stg_2026_full`, `MSCA-PF-2025`)
- protected-row lane parity: enforced
- closure artifacts references: present in matrix
- row summary:
  - `pass`: 7
  - `skip` (explicit rationale): 4
  - `fail`: 0

## Audit Disposition Ledger

- Finding: Protected-lane parity could be faked by omission.
  - Disposition: Closed by explicit Clerk lane rows or explicit skip rationale for each protected proof item.
- Finding: Policy-blocking could over-claim based only on user-surface error.
  - Disposition: Closed by backend zero-side-effect evidence (`no_review_creation`, `no_pipeline_execution`, `no_partial_persistence`) and promotion of the representative row to `pass`.
- Finding: Closure readiness could drift if baseline scope or audit disposition references are absent/non-replayable.
  - Disposition: Closed by validator enforcement of replayable closure refs and `--require-closure` gate.
- Finding: Negative-case semantics could drift from visible block to hidden side effects.
  - Disposition: Closed by matrix contract requiring explicit `visible_block_asserted` + `no_side_effect_asserted` pairing for negative scenarios.

## Remaining Risks

- Clerk lanes are explicitly skipped due missing credentialed local login setup. This remains non-blocking only while skip rationale is explicit and closure gate stays fail-closed.
