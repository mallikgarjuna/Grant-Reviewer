---
path: "docs/call-yaml/onboarding-checklist.md"
title: "Call YAML Onboarding Checklist"
version: "1.0"
status: "Active"
updated: "2026-03-08"
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
- If `runtime_config.split_visibility_reviewability_enabled` is true:
  - every supporting node is `node_role: SUPPORTING` and has no expectations,
  - all official nodes remain present in YAML,
  - runtime opt-in was explicitly approved for this call (proof-call-first policy).

## 4. Ingestion

- Ingest succeeds in target environment DB.
- Call appears in calls listing APIs and node metadata APIs.

## 5. WF-0038 Runtime Readiness

- Runtime uses v1-only structured-review execution for `POST /api/structured-review`.
- At least one `POST /api/structured-review` smoke request succeeds for this call.

## 6. WF-0063 Split-Mode Safety (Only for Opted-In Calls)

- `GET /api/public/calls/{call_code}/config` returns `split_visibility_reviewability_enabled: true`.
- Flat/tree nodes APIs keep structural completeness and include role metadata.
- Primary-path submit/compliance rejects supporting node IDs fail-closed.
- Review detail exposes `primary_evaluated_node_logical_ids` and reserved `supporting_context_node_logical_ids`.
- Disabling opt-in restores legacy behavior without YAML re-authoring.

## 7. Ship Gate

Mark the call as ready only after all checklist sections pass.
