# Brainstorming Log: Database Architecture (Phase 0)

## Confirmed Architectural Decisions

### 1. Hierarchy & Nodes
- **Generic Proposal Nodes**: Use a single table for Sections and Subsections with a `parent_id` recursive relationship. This allows for arbitrary depth (though usually 1-2 levels for grants).
- **Evaluation Elements**: Linked directly to a `ProposalNode`.

### 2. Lifespan & Persistence
- **Anonymous MVP**: Reviews are not tied to persistent User accounts. They are session-based (e.g., stored in LocalStorage or transiently in DB without auth).
- **Cleanup**: Data can be treated as ephemeral if necessary, but DB should support unique session IDs for identifying results.

### 3. Criterion Scoping
- **Strictly Per-Call**: Evaluation elements are not shared across calls in the MVP. This simplifies the schema and avoids complex inheritance logic at this stage.

### 4. Deterministic State
- **Auditability Lite**: We will NOT store the full prompt/model state for every request in the MVP. Focus instead on linking feedback cards to the specific rubric IDs.

## Entities (Refined)

### Metadata (Read-Only in UI)
- `agencies`: name, description.
- `calls`: agency_id, name, year, deadline.
- `proposal_nodes`: call_id, parent_id, title, type (section/subsection).
- `evaluation_elements`: node_id, title, description, guidance_text.

### Transactions (Create-Only in UI)
- `review_sessions`: session_id, timestamp, language_code, user_snippet_text.
- `review_cards`: session_id, evaluation_element_id, content (the markdown feedback).
