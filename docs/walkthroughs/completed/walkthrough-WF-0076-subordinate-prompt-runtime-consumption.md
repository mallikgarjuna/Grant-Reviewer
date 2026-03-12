<!-- docs/walkthroughs/completed/walkthrough-WF-0076-subordinate-prompt-runtime-consumption.md -->
# WF-0076 — Subordinate Prompt Runtime Consumption

Artifact: walkthrough
Version: v1.0
Status: Done
Last Updated: 2026-03-12

## Scope Closed

- Preserved prior truth boundaries: WF-0074 remains authoring/governance closure; WF-0075 remains ERC PoC proof-call completeness closure.
- Added the narrow runtime seam for WF-0076: expectation-level `subordinate_prompts` carriage from active `CallDefinition.canonical_json` into `call_config_snapshot.expectations`.
- Hardened the request contract and validator for additive subordinate-prompt payloads (including duplicate ID fail-closed checks).
- Added live runtime-consumption proof in evaluator output (`reason`) and output-level proof via surfaced review-card feedback.
- Skipped conditional Task 4 clarification because executable proof from Tasks 1-3 was unambiguous.

## Implementation Summary

- `backend/app/services/structured_reviewer_service.py`
  - Added canonical subordinate-prompt lookup keyed by existing identity (`NodeExpectation.element.logical_id` to canonical evaluation-element `id`).
  - Projected optional `subordinate_prompts` only where canonical prompts exist.
- `backend/app/engine/contracts.py`
  - Added additive `ActivatedSubordinatePromptV1`.
  - Extended `ActivatedExpectationV1` with optional `subordinate_prompts`.
- `backend/app/engine/review_request_validator.py`
  - Added fail-closed duplicate subordinate-prompt ID detection per expectation.
- `backend/app/engine/findings/evaluator.py`
  - Added deterministic subordinate-prompt runtime signal in `reason` for carried prompts.
- Tests
  - Service proof selector renamed to WF-0076 and strengthened with canonical source perturbation.
  - Contract tests added for valid additive carriage, malformed item rejection, duplicate-ID rejection, and no-carriage compatibility.
  - Pipeline tests added for positive/negative runtime-consumption behavior and output-level signal proof.

## Phase Evidence

### Part A (Execute)
- Task 1 commit: `b7800c6`
- Task 2 commit: `2f313c2`
- Task 3 commit: `0e62ddc`
- Task 4 (conditional skip) commit: `2033778`

### Part B (Technical Audit Gate)
- Diff range audited: `main...HEAD`
- Profile: `execution`
- Findings: none (no blocking/non-blocking fixes required before Part C2)

### Part C (Revise + Verify + Ship Gate)
- Part C1: no revisions required (Part B had no findings).
- Part C2 verification (all pass):
  - `pre-commit run --all-files`
  - `cd backend && uv run pytest tests/engine/test_review_request_contracts.py -k "subordinate_prompt or activated_expectation"`
  - `cd backend && uv run pytest tests/test_review_request_validator.py`
  - `cd backend && uv run pytest tests/test_review_engine_pipeline_v1.py -k "wf0076 or subordinate_prompt"`
  - `cd backend && DATABASE_URL='postgresql://grant:grant@localhost:5432/grant_reviewer_test?sslmode=disable' uv run pytest tests/test_structured_reviewer_service.py -k "wf0076"`
  - `cd backend && uv run pytest tests/test_call_subordinate_prompt_coverage.py -k "wf0075_real_erc_poc_page_43_proof_call_is_fully_encoded"`

## Risks / Follow-Ups

- Non-blocking future hardening: add a formatting/cap test if subordinate-prompt lists grow substantially and `reason` length becomes a downstream UX concern.

## Ship Gate Status

- Walkthrough drafted and verified.
- WF artifacts archived to `completed/` in this phase.
- `docs/index.md` updated to `Done` with completed artifact links.
- Ready for explicit user `ship it` decision.
