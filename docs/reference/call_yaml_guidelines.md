# Call YAML Guidelines (PeerLens / Grant Reviewer)

This repository uses `v2` call YAML for active onboarding and WF-0038 pipeline usage.

Primary references:
- Schema SSOT: `backend/app/schemas/call_definitions_v2.py`
- Ingestion runner: `backend/scripts/ingest_call.py`
- Authoring workflow: `docs/workflow/call-yaml-authoring-workflow.md`
- Starter template: `backend/data/calls/templates/call_definition_v2_template.yaml`

## File Naming

Use:
`{agency}_{program}_{year}_{stage}.yaml`

Examples:
- `erc_stg_2026_full.yaml`
- `nwo_veni_2025_preproposal.yaml`

## Required Top-Level Keys (v2)

- `funding_agency`
- `funding_call`
- `evaluation_criteria`
- `proposal_nodes`
- `reviewer_policy` (optional but recommended)
- `runtime_notes` (optional)

## Critical Data Rules

- `evaluation_criteria[*].id` must be unique.
- `evaluation_criteria[*].evaluation_elements[*].id` must be unique globally.
- Every `proposal_nodes[*].node_expectations[*].evaluation_element_id` must reference an existing evaluation element.
- `proposal_nodes[*].id` must be unique and stable across revisions.
- Use `parent_logical_id` to encode hierarchy; do not encode hierarchy in IDs.

## V2 Enums You Must Respect

- `expectation_strength`: `MANDATORY | IMPORTANT | OPTIONAL`
- `evaluation_intent`: `COMPLIANCE | QUALITY | RISK | STRATEGIC_FIT`
- `rule_severity`: `ERROR | WARNING`
- `evaluation_stage`: `STEP_1 | STEP_2 | BOTH`
- `reviewer_policy.enforcement_mode`: `PROMPT_ONLY | POST_CHECK | BLOCKING`

## Authoring Checklist (WF-0038 Compatible)

1. Start from the template:
   - `backend/data/calls/templates/call_definition_v2_template.yaml`
2. Author from official sources only:
   - proposal structure source
   - evaluation criteria/elements source
3. Keep scope limited to:
   - evaluable proposal structure
   - evaluation criteria/elements
   - enforceable content constraints
4. Validate with dry-run:
   - `cd backend && uv run python scripts/ingest_call.py data/calls/<agency>/<file>.yaml --dry-run`
5. Ensure `dry-run` output has:
   - expected proposal node count
   - expected evaluation element count
   - no reference/validation errors

## WF-0038 Readiness Gate

A call YAML is "WF-0038 ready" only if:
- it passes `--dry-run`,
- it ingests cleanly into DB,
- a structured review request for that call can run without `MALFORMED_REVIEW_REQUEST` from bad call config / expectation mapping.

## Common Mistakes

- Mixing old `v1` fields (`short_name`, recursive `children`) with `v2` shape.
- Encoding non-evaluable administrative content as proposal nodes.
- Over-mapping one evaluation element to too many unrelated nodes.
- Writing cross-node alignment expectations without clear source grounding.
