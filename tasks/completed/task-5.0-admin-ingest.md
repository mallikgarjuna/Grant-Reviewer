# Task 5.0: Admin Ingestion (Call Definition as Code)

**Status**: [x] Complete
**PRD**: [tasks/prd-5.0-admin-ingest.md](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/tasks/prd-5.0-admin-ingest.md)

## 5.1 Define YAML Schemas (1:1 DB Mapping)
- [x] Create `backend/app/schemas/call_definitions.py` (Renamed from ingestion.py) <!-- id: 8 -->
    - [x] `FundingAgencyDefinition` (name, short_name)
    - [x] `FundingCallDefinition` (name, code, year)
    - [x] `EvaluationElementDefinition` (id, name, description)
    - [x] `EvaluationCriterionDefinition` (id, name, elements: list[EvaluationElementDefinition])
    - [x] `NodeExpectationDefinition` (element_id, strength, intent, guidance_note, optional: expectation_type)
    - [x] `ProposalNodeDefinition` (title, node_type, guidance_text, children: list[ProposalNode], expectations: list[NodeExpectation])
    - [x] `CallDefinition` (agency, call, rubrics: list[EvaluationCriterionDefinition], proposal_nodes: list[ProposalNodeDefinition])
    - [x] Implement `check_references` validator (ensure expectation.element_id exists in rubric)
    - [x] Implement `check_recursion` validator (prevent cycles)

## 5.2 Implement Ingestion Script
- [x] Create `backend/scripts/ingest_call.py` <!-- id: 9 -->
    - [x] `load_yaml(path) -> CallDefinition`
    - [x] `resolve_logical_ids(call_def) -> dict[str, UUID]` (Maps YAML string IDs to DB UUIDs)
    - [x] `ingest_agency_and_call(session, call_def)`
    - [x] `ingest_rubric(session, call_id, rubric_def, id_map)`
    - [x] `ingest_nodes_recursive(session, call_id, nodes, parent_id, id_map)` (Handle leaf nodes correctly)
    - [x] Add CLI entrypoint with `--dry-run` flag (preview changes without commit)

## 5.3 Verification Data & Scripts
- [x] Create `backend/data/calls/sample_erc_call.yaml` (Valid sample) <!-- id: 10 -->
- [x] Create `backend/data/calls/invalid_ref.yaml` (Invalid sample for testing validation) <!-- id: 11 -->
- [x] Create `backend/data/calls/edge_case_call.yaml` (Section-only, multiple expectations, multi-element refs) <!-- id: 16 -->

## 5.4 Verification
- [x] **Test 1**: Verify Schema Validation (Run script with `invalid_ref.yaml` -> Expect Pydantic Error) <!-- id: 12 -->
- [x] **Test 2**: Verify Dry Run (Run with `--dry-run` -> Expect Log Output, No DB Changes) <!-- id: 17 -->
- [x] **Test 3**: Verify Successful Ingestion (Run script with `sample_erc_call.yaml` -> Expect Success) <!-- id: 13 -->
- [x] **Test 4**: Verify Edge Cases (Run script with `edge_case_call.yaml` -> Check Hierarchy & Mappings) <!-- id: 18 -->
- [x] **Test 5**: Verify Idempotency (Run script again -> Expect 0 new rows) <!-- id: 14 -->
- [x] **Integration Test**: Run Review (Run `run_review.py` with the new call -> Expect Success) <!-- id: 15 -->
