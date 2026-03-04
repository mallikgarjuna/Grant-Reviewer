# WF-0050 — Extension Surface Strictness + CI Contract Gate PRD

Artifact: prd
Version: v1.0
Status: Completed
Last Updated: 2026-03-04

## User Stories
- As an engine maintainer, I want all extension surfaces in snapshot v1 to use strict typed models so unknown-field drift is rejected deterministically.
- As a release owner, I want explicit CI contract-gate checks so contract regressions cannot merge silently.

## Functional Requirements
- FR1: `compliance_rules` strict nested model at request boundary.
- FR2: `stage_gating`, `hierarchy`, `nesting` strict nested models at request boundary.
- FR3: Unknown nested keys for all above surfaces return deterministic malformed-request field errors.
- FR4: CI includes explicit contract gate for `wf0048_contract_*` + `wf0049_contract_*` selectors.
- FR5: CI backend test lane uses `pytest -m no_db`.

## Acceptance
- Contract tests for WF-0050 strict surfaces pass.
- Existing WF-0048/WF-0049 selectors remain green.
- `pytest -m no_db` remains green.
- CI workflow updated accordingly.
