# WF-0045 — Base Review Pipeline v1.0 (call-agnostic core)

Artifact: walkthrough
Version: v0.1
Status: Draft
Last Updated: 2026-03-03

## Verification Bundle

- `cd backend && uv run pytest tests/test_review_execution_core.py -k wf0045_contract_`
Expected: matrix coverage and execution selectors pass (`wf0045_contract_*`), including call-agnostic guardrail parity.

- `cd backend && uv run pytest -k wf0045_contract_`
Expected: all WF-0045 contract selectors pass across pipeline, telemetry, validator, evaluator, extractor, mapper, aggregation, and execution-core surfaces.

- `rg -n "wf0045_contract_" docs/walkthroughs/walkthrough-WF-0045-base-review-pipeline-v1-call-agnostic.md`
Expected: walkthrough contains deterministic verification selector references for WF-0045 handoff.
