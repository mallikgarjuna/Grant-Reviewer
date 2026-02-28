---
title: "Call YAML Onboarding Checklist"
version: "1.0"
status: "Active"
updated: "2026-02-28"
---

# Call YAML Onboarding Checklist

Use this checklist when onboarding any new funding call YAML.

## 1. Authoring Inputs

- Official proposal-structure source is available.
- Official evaluation-criteria source is available.
- Stage and year are explicitly confirmed.

## 2. Authoring Output

- YAML is authored using `CallDefinitionV2` shape.
- Source traceability manifest exists under `backend/data/calls/sources/`.
- Scope includes only evaluable narrative structure, evaluation criteria/elements, and enforceable constraints.

## 3. Validation

- Dry-run passes:
  - `cd backend && uv run python scripts/ingest_call.py data/calls/canonical/<agency>/<file>.yaml --dry-run`
- Dry-run summary node and element counts match expectations.
- No unresolved expectation references.

## 4. Ingestion

- Ingest succeeds in target environment DB.
- Call appears in calls listing APIs and node metadata APIs.

## 5. WF-0038 Runtime Readiness

- Pipeline-v1 is enabled only for target call code:
  - `STRUCTURED_REVIEW_PIPELINE_V1_ENABLED=1`
  - `STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES=<call_code>`
- At least one `POST /api/structured-review` smoke request succeeds for this call.

## 6. Ship Gate

Mark the call as ready only after all checklist sections pass.
