# WF-0052 — Producer Compatibility Stress (Real Snapshots)

Artifact: brainstorm
Version: v0.1
Status: Ready for PRD
Last Updated: 2026-03-04

## Problem
WF-0049/WF-0050 hardened strict nested request-boundary contracts. Existing compatibility evidence is strong but still mostly fixture-driven and can miss producer-shape drift in real activated snapshots.

## Goal
Prove strict request-boundary compatibility and digest determinism against real activated call-config snapshots from key call families, not only synthetic cases.

## In Scope
- Build compatibility matrix inputs from real activated snapshots already used by the backend.
- Validate strict parse behavior for each matrix class.
- Validate digest determinism for omitted-vs-explicit default equivalence classes.
- Keep work limited to request-boundary contract validation and deterministic digest behavior.

## Out of Scope
- Product feature expansion.
- UI changes.
- Pipeline behavior changes outside request validation.

## Critical Risks
- False confidence from synthetic fixtures that do not reflect producer payload reality.
- Silent regressions when new call definitions introduce undeclared nested keys.
- Digest mismatch churn if canonicalization is validated against raw rather than schema-projected data.

## Initial Success Criteria
- Deterministic matrix cases cover at least:
  - `happy_valid_payload_real_snapshot`
  - `legacy_extra_nested_key_real_snapshot`
  - `nested_type_mismatch_real_snapshot`
  - `omitted_optional_default_equivalence_real_snapshot`
- Contract gate includes explicit deterministic selectors/marker for WF-0052 cases.
- `pytest -m no_db` remains green.
