# WF-0028 — NWO Veni 2025 preproposal Compliance Engine Walkthrough

Artifact: walkthrough
Version: v0.1
Status: Done
Last Updated: 2026-02-22

## Summary

Implemented deterministic compliance checking for structured proposal node submissions before AI review submission.

## What Was Built

- Added compliance request/response schemas in `backend/app/schemas/compliance.py`.
- Added a pure deterministic engine in `backend/app/services/compliance_engine.py`:
  - mandatory presence checks based on `total_word_limit.min_words`
  - min/max word limit checks
  - domain-aware max word limit resolution with fallback handling
- Added `POST /api/check-compliance` in `backend/main.py`:
  - BFF-auth protected
  - unknown/duplicate node validation
  - domain-required/domain-invalid validation
  - latency warning log when evaluation takes >500ms
- Added unit tests in `backend/tests/test_compliance_engine.py`.
- Added endpoint integration tests in `backend/tests/test_api.py` for compliance scenarios.

## Files Created

- `backend/app/schemas/compliance.py`
- `backend/app/services/compliance_engine.py`
- `backend/tests/test_compliance_engine.py`

## Files Modified

- `backend/main.py`
- `backend/tests/test_api.py`
- `docs/tasks/task-WF-0028-compliance-engine.md`

## Verification Evidence

- Unit tests (`backend/tests/test_compliance_engine.py`): 10 passed.
- Compliance endpoint integration tests (`backend/tests/test_api.py -k compliance`): 6 passed.
- Full API tests (`backend/tests/test_api.py`): 36 passed.
- Full backend suite (`backend/tests`): 51 passed.
- Lint checks passed for touched files and `pre-commit run --all-files`.

## Known Limitations (MVP)

- `warnings[]` is always empty; MVP emits deterministic blocking/non-blocking findings only in `errors[]` where implemented.
- Word counting is whitespace-token based and does not apply semantic exclusions such as references/URLs/output types.
- Complex free-text compliance rule parsing (`compliance_rules`) remains deferred.

## Next Steps

- Add deterministic warning-level rules (near-limit threshold, optional completeness hints).
- Add integration coverage using real ingested NWO fixture data for domain limit variants.
