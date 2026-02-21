# PRD: Admin Ingestion (Call Definition as Code)

**Version**: 1.1 (Revised)
**Status**: Pending Review
**Task ID**: 5.0

## 1. Goal
Empower technical admins to define a complete Funding Call structure (metadata, rubric, proposal hierarchy, and evaluation logic) in a single version-controlled YAML file, which is then ingested idempotently into the database.

## 2. Problem Statement
The Grant Reviewer domain model relies on deep, recursive relationships and strict referential integrity between `ProposaNodes` and `EvaluationElements` via `NodeExpectations`. Manually managing these ~50-100 interrelated records via SQL or generic UIs is error-prone. A "Configuration-as-Code" approach is required for the MVP.

## 3. Solution: YAML Ingestion Pipeline
A CLI script (`scripts/ingest_call.py`) that reads a YAML file mapped 1:1 to the database schema and performs an atomic, idempotent upsert.

## 4. User Stories
*   **US 5.1 (Define)**: As an Admin, I can define a Funding Call using a YAML schema that mirrors the database tables (`funding_agency`, `funding_call`, `evaluation_criteria`, `proposal_nodes`), ensuring terminology consistency.
*   **US 5.2 (Validate)**: As an Admin, I receive immediate validation errors for:
    *   Broken references (e.g., `node_expectation` linking to a non-existent `evaluation_element`).
    *   Cyclic recursion in `proposal_nodes`.
    *   Orphaned subsections.
*   **US 5.3 (Ingest)**: As an Admin, I can run `uv run scripts/ingest_call.py call.yaml` to upsert the call without duplicating data.
*   **US 5.4 (Version)**: As an Admin, I can commit the YAML to Git, enabling version history for rubrics and prompts.

## 5. Technical Specifications

### 5.1 YAML Schema Definition (`app/schemas/ingestion.py`)
The YAML structure must align 1:1 with DB models to reduce cognitive load.

**Schema Overview:**
```yaml
# 1. Funding Agency & Call (Metadata)
funding_agency:
  name: "European Research Council"
  short_name: "ERC"

funding_call:
  name: "Consolidator Grant 2026"
  code: "COG-2026"  # Unique business key
  year: 2026
  # Optional: prompt_template_id: "erc_v1" (Future scope / MVP comment)

# 2. Rubric Definition (EvaluationCriterion -> EvaluationElement)
evaluation_criteria:
  - id: "crit_excellence"  # Logical ID (mapped to UUID)
    name: "1. Excellence"
    evaluation_elements:
      - id: "elem_novelty"  # Logical ID (mapped to UUID)
        name: "Novelty/Groundbreaking nature"
        description: "To what extent..."

# 3. Proposal Structure (ProposalNode -> Children)
proposal_nodes:
  - title: "Part B1"
    node_type: "SECTION"  # Enum: SECTION | SUBSECTION
    children:
      - title: "Section a: State of the art"
        node_type: "SUBSECTION"
        guidance_text: "Describe the state of the art..."  # Mapped to ProposalNode.guidance_text

        # 4. Expectations (NodeExpectation -> EvaluationElement)
        node_expectations:
           - evaluation_element_id: "elem_novelty" # MUST match evaluation_elements.id
             expectation_strength: "MANDATORY"     # Enum: MANDATORY | IMPORTANT | OPTIONAL
             evaluation_intent: "QUALITY"          # Enum: COMPLIANCE | QUALITY | RISK
             guidance_note: "Check if the PI..."   # Mapped to NodeExpectation.guidance_note
```

### 5.2 Data Relationships & Validation
The system must enforce strict integrity rules during ingestion:

```mermaid
graph TD
    FC[FundingCall] --> FA[FundingAgency]
    FC --> EC[EvaluationCriterion]
    EC --> EE[EvaluationElement]
    FC --> PN[ProposalNode (Root)]
    PN --> PN2[ProposalNode (Child)]
    PN2 --> NE[NodeExpectation]
    NE -. Ref .-> EE
```

**Validation Rules:**
1.  **Referential Integrity**: Every `evaluation_element_id` used in `node_expectations` MUST exist in `evaluation_criteria`.
2.  **Enum Validation**: `node_type`, `expectation_strength`, `evaluation_intent` must match `models/domain.py` Enums.
3.  **Recursion Check**: Provide a depth limit (e.g., 5) and detect cycles in `proposal_nodes`.
4.  **Orphans**: Warn if any `evaluation_element` defined in the rubric is never used in any `node_expectation`.

### 5.3 Ingestion Logic (`scripts/ingest_call.py`)
1.  **Load & Parse**: Use `pydantic` models to validate structure and types.
2.  **ID Mapping**:
    *   Create a mapping registry: `{"crit_excellence": UUID(...), "elem_novelty": UUID(...)}`.
    *   Use these UUIDs when creating `NodeExpectation` records.
3.  **Atomic Transaction**:
    *   **Agency/Call**: Find by natural key (`short_name`, `code`) or Create. Update metadata.
    *   **Rubric**: Upsert Criteria and Elements using the Call ID.
    *   **Nodes**: Recursive upsert. Maintain `parent_node_id`.
    *   **Expectations**: Delete existing expectations for the node (to allow removal) and insert strictly from YAML.
    *   **No deletion of Nodes/Elements**: Do not delete existing Nodes/Elements to prevent data loss for existing reviews (Soft delete or ignore).

## 6. Success Criteria
*   [ ] **1:1 Mapping**: YAML keys match `models/domain.py` table names exactly (snake_case).
*   [ ] **Reference Handling**: Ingestion fails with a clear error if `evaluation_element_id: "unknown"` is used.
*   [ ] **Idempotency**: Running `ingest_call.py` twice results in **zero** change to row count.
*   [ ] **Verification**: `run_review.py` executes successfully using the ingested Call ID.
