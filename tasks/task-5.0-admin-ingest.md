# Task 5.0: Admin Ingestion (Call Definition as Code)

**Status**: [/] In Progress
**PRD**: [tasks/prd-5.0-admin-ingest.md](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/tasks/prd-5.0-admin-ingest.md)

## 5.1 Define YAML Schemas (1:1 DB Mapping)
- [ ] Create `backend/app/schemas/call_definitions.py` (Renamed from ingestion.py) <!-- id: 8 -->
    - [ ] `FundingAgencyDefinition` (name, short_name)
    - [ ] `FundingCallDefinition` (name, code, year)
    - [ ] `EvaluationElementDefinition` (id, name, description)
    - [ ] `EvaluationCriterionDefinition` (id, name, elements: list[EvaluationElementDefinition])
    - [ ] `NodeExpectationDefinition` (element_id, strength, intent, guidance_note, optional: expectation_type)
    - [ ] `ProposalNodeDefinition` (title, node_type, guidance_text, children: list[ProposalNode], expectations: list[NodeExpectation])
    - [ ] `CallDefinition` (agency, call, rubrics: list[EvaluationCriterionDefinition], proposal_nodes: list[ProposalNodeDefinition])
    - [ ] Implement `check_references` validator (ensure expectation.element_id exists in rubric)
    - [ ] Implement `check_recursion` validator (prevent cycles)

## 5.2 Implement Ingestion Script
- [ ] Create `backend/scripts/ingest_call.py` <!-- id: 9 -->
    - [ ] `load_yaml(path) -> CallDefinition`
    - [ ] `resolve_logical_ids(call_def) -> dict[str, UUID]` (Maps YAML string IDs to DB UUIDs)
    - [ ] `ingest_agency_and_call(session, call_def)`
    - [ ] `ingest_rubric(session, call_id, rubric_def, id_map)`
    - [ ] `ingest_nodes_recursive(session, call_id, nodes, parent_id, id_map)` (Handle leaf nodes correctly)
    - [ ] Add CLI entrypoint with `--dry-run` flag (preview changes without commit)

## 5.3 Verification Data & Scripts
- [ ] Create `backend/data/calls/sample_erc_call.yaml` (Valid sample) <!-- id: 10 -->
- [ ] Create `backend/data/calls/invalid_ref.yaml` (Invalid sample for testing validation) <!-- id: 11 -->
- [ ] Create `backend/data/calls/edge_case_call.yaml` (Section-only, multiple expectations, multi-element refs) <!-- id: 16 -->

## 5.4 Verification
- [ ] **Test 1**: Verify Schema Validation (Run script with `invalid_ref.yaml` -> Expect Pydantic Error) <!-- id: 12 -->
- [ ] **Test 2**: Verify Dry Run (Run with `--dry-run` -> Expect Log Output, No DB Changes) <!-- id: 17 -->
- [ ] **Test 3**: Verify Successful Ingestion (Run script with `sample_erc_call.yaml` -> Expect Success) <!-- id: 13 -->
- [ ] **Test 4**: Verify Edge Cases (Run script with `edge_case_call.yaml` -> Check Hierarchy & Mappings) <!-- id: 18 -->
- [ ] **Test 5**: Verify Idempotency (Run script again -> Expect 0 new rows) <!-- id: 14 -->
- [ ] **Integration Test**: Run Review (Run `run_review.py` with the new call -> Expect Success) <!-- id: 15 -->
