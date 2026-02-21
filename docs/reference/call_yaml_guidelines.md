# Call YAML Guidelines (PeerLens / Grant Reviewer)

This project’s call YAML format is defined by:
- Validation schema: `backend/app/schemas/call_definitions.py`
- Ingestion logic: `backend/scripts/ingest_call.py`
- Target DB models: `backend/app/models/domain.py`

This document summarizes how to author YAML that validates, ingests cleanly, and links correctly to SQLModel rows.

## File Naming

Prefer the convention from `backend/data/calls/README.md`:

`{agency}_{program}_{year}_{stage}.yaml` where `stage` is `pre` or `full`.

## Top-Level Shape

Required keys:
- `funding_agency`
- `funding_call`
- `evaluation_criteria`
- `proposal_nodes`

Minimal skeleton:

```yaml
funding_agency:
  name: "Example Agency"
  short_name: "EX"
  description: "..."

funding_call:
  name: "Example Call 2026"
  code: "EX-2026"
  year: 2026
  aim_objectives: "..."
  scope: "..."
  general_guidelines: "..."

evaluation_criteria:
  - id: "crit_example"
    name: "Criterion Name"
    description: "..."
    evaluation_elements:
      - id: "elem_example"
        name: "Element Name"
        description: "..."

proposal_nodes:
  - title: "Top Level Section"
    node_type: "SECTION"
    children: []
    node_expectations: []
```

## ID Rules (Critical)

YAML uses *logical string IDs* for rubric items.

- `evaluation_criteria[*].id` must be unique across criteria.
- `evaluation_criteria[*].evaluation_elements[*].id` must be unique across *all* elements.
- `proposal_nodes[*].node_expectations[*].evaluation_element_id` must reference an existing element `id`.

Ingestion maps these logical IDs to UUIDs internally (see `resolve_logical_ids()` in `backend/scripts/ingest_call.py`).

## Proposal Node Tree

### Node fields

Each node supports:
- `title` (string)
- `node_type`: `"SECTION"` or `"SUBSECTION"`
- `guidance_text` (optional string)
- `children` (list of nodes)
- `node_expectations` (list of expectations)

### Recursion / Depth / Cycles

Validation enforces:
- Max depth of 5 levels
- Title-based cycle detection (heuristic): a repeated `title` along an ancestor path is treated as a potential cycle

Practical guidance:
- Keep `title` values unique *within an ancestor chain* (avoid reusing the same title under itself).
- For UI compatibility, prefer `SECTION -> SUBSECTION` for the first two levels, but deeper nesting is supported by the schema.

## Expectations (How Nodes Link to Rubric)

Each `node_expectations` item links the node to a rubric element and includes strictness/intent metadata:

```yaml
node_expectations:
  - evaluation_element_id: "elem_example"
    expectation_strength: "MANDATORY"  # or IMPORTANT / OPTIONAL
    evaluation_intent: "QUALITY"       # or COMPLIANCE / RISK / STRATEGIC_FIT
    guidance_note: "What the reviewer should look for."
```

Enums are validated in `backend/app/schemas/call_definitions.py`:
- `node_type`: `SECTION | SUBSECTION`
- `expectation_strength`: `MANDATORY | IMPORTANT | OPTIONAL`
- `evaluation_intent`: `COMPLIANCE | QUALITY | RISK | STRATEGIC_FIT`

## Mapping to SQLModel Tables (Conceptual)

During ingestion (`backend/scripts/ingest_call.py`):
- `funding_agency` -> `FundingAgency` (business key: `short_name`)
- `funding_call` -> `FundingCall` (business key: `code`; linked to agency)
- `evaluation_criteria` -> `EvaluationCriterion` rows
- `evaluation_elements` -> `EvaluationElement` rows (linked to criterion)
- `proposal_nodes` tree -> `ProposalNode` rows (linked to call; parent/child via `parent_node_id`)
- `node_expectations` -> `NodeExpectation` rows (linked to node + evaluation element; carries strength/intent/guidance_note)

## Authoring Checklist

1. Run dry-run validation:
   - `cd backend && uv run python scripts/ingest_call.py data/calls/<file>.yaml --dry-run`
2. Fix any `Unknown evaluation_element_id` errors by aligning IDs.
3. Avoid deep trees (>5) and title cycles.
4. Ensure nodes that should be reviewable have at least one `node_expectations` entry.

## Common Pitfalls

- Defining an element but never referencing it: allowed, but ingestion logs a warning for unused elements.
- Reusing the same `title` down a branch (cycle heuristic): validation can fail even if your intent is “same label in two places”.
- Treating “admin form PDFs” as proposal narrative structure: those documents often describe submission forms, not the snippet-review node tree. Use the narrative template/structure you want the user to select from in-app.
