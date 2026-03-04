# WF-0050 — Extension Surface Strictness + CI Contract Gate

Artifact: brainstorm
Version: v1.0
Status: Draft Complete
Last Updated: 2026-03-04

## Problem
WF-0049 hardened active snapshot surfaces, but remaining extension surfaces (`stage_gating`, `hierarchy`, `nesting`, `compliance_rules`) and explicit merge-blocking CI contract gates still left regression risk.

## Decision
- Harden remaining extension surfaces in `ActivatedCallConfigSnapshotV1` using strict nested models.
- Add explicit CI contract-gate step for `wf0048_contract_*` and `wf0049_contract_*` selectors.
- Run backend verification on `pytest -m no_db` in CI.
- Add producer-realism validation coverage using stress fixture payload shapes.

## Outcome Summary
Implemented in WF-0050 branch and verified green.
