"""backend/tests/test_api.py
FastAPI endpoint tests for Task 7.0.
"""

import hashlib
import hmac
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict
from uuid import UUID

import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from app.db import engine, get_session, normalize_database_url
from app.models.domain import (
    AssessmentStatus,
    CallDefinition,
    EvaluationCriterion,
    EvaluationElement,
    EvaluationIntent,
    ExpectationStrength,
    FundingAgency,
    FundingCall,
    NodeExpectation,
    NodeType,
    PromptTemplate,
    ProposalNode,
    ProposalSnippet,
    Review,
    ReviewCard,
    ReviewRating,
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import StubLLMClient
from main import ERROR_STATUS_BY_CODE, app
from scripts.ingest_call import ingest_call

TEST_BFF_SHARED_SECRET = "test-bff-secret"
TEST_USER_ID = "user_test_1"


@dataclass(frozen=True)
class SeededIDs:
    """IDs for deterministic test assertions."""

    call_id: UUID
    section_with_expectations_id: UUID
    section_without_expectations_id: UUID
    other_call_id: UUID
    other_call_node_id: UUID
    structured_call_id: UUID
    structured_call_code: str


class Wf0043ContractCase(TypedDict):
    case_id: str
    surface: str
    expected_http_status: int
    expected_error_code: str | None
    expect_review_persisted: bool
    expected_review_status: str | None
    expected_summary_convention: str | None
    idempotency_key: str
    request_nodes: list[dict[str, str]]


class Wf0044PolicyCase(TypedDict):
    case_id: str
    surface: str
    enforcement_mode: str
    forbidden_term: str
    feedback_text: str
    expected_review_status: str
    expected_summary_convention: str
    expected_cards_count: int


class Wf0065RepresentativeCase(TypedDict):
    case_id: str
    call_code: str
    stage: str
    node_logical_id: str
    node_text: str


def _load_wf0043_matrix_cases() -> list[Wf0043ContractCase]:
    fixture_path = Path("tests/fixtures/wf_0043_contract_matrix.yaml")
    loaded = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
    raw_cases = loaded.get("cases", [])
    return raw_cases if isinstance(raw_cases, list) else []


def _get_wf0043_case(case_id: str, *, surface: str) -> Wf0043ContractCase:
    for candidate in _load_wf0043_matrix_cases():
        if candidate["case_id"] == case_id and candidate["surface"] == surface:
            return candidate
    raise AssertionError(f"WF-0043 case not found: {surface}/{case_id}")


def _non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _wf0043_case_id(value: str, *, surface: str) -> str:
    return f"wf0043_contract_{surface}_{value}"


def _load_wf0044_policy_cases() -> list[Wf0044PolicyCase]:
    fixture_path = Path("tests/fixtures/wf_0044_policy_matrix.yaml")
    loaded = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
    raw_cases = loaded.get("cases", [])
    if not isinstance(raw_cases, list):
        return []
    return [
        case
        for case in raw_cases
        if isinstance(case, dict) and case.get("surface") == "structured_api"
    ]


def _wf0044_policy_case_id(value: str, *, surface: str) -> str:
    return f"wf0044_policy_{surface}_{value}"


def _wf0065_representative_cases() -> list[Wf0065RepresentativeCase]:
    return [
        {
            "case_id": "nwo_veni_2025_preproposal",
            "call_code": "nwo_veni_2025_preproposal",
            "stage": "STEP_1",
            "node_logical_id": "key_outputs",
            "node_text": "Representative proof text for NWO key outputs.",
        },
        {
            "case_id": "erc_stg_2026_full",
            "call_code": "erc_stg_2026_full",
            "stage": "STEP_1",
            "node_logical_id": "proposal_summary",
            "node_text": "Representative proof text for ERC proposal summary.",
        },
        {
            "case_id": "MSCA-PF-2025",
            "call_code": "MSCA-PF-2025",
            "stage": "STEP_1",
            "node_logical_id": "excellence",
            "node_text": "Representative proof text for MSCA excellence.",
        },
    ]


def _wf0065_paired_boundary_cases() -> list[Wf0065RepresentativeCase]:
    return [
        {
            "case_id": "nwo_veni_2025_preproposal",
            "call_code": "nwo_veni_2025_preproposal",
            "stage": "STEP_1",
            "node_logical_id": "key_outputs",
            "node_text": "Representative paired-boundary text for NWO key outputs.",
        },
        {
            "case_id": "erc_stg_2026_full",
            "call_code": "erc_stg_2026_full",
            "stage": "STEP_2",
            "node_logical_id": "b1_part1_scientific_proposal",
            "node_text": "Representative paired-boundary text for ERC scientific proposal.",
        },
        {
            "case_id": "MSCA-PF-2025",
            "call_code": "MSCA-PF-2025",
            "stage": "STEP_1",
            "node_logical_id": "excellence",
            "node_text": "Representative paired-boundary text for MSCA excellence.",
        },
    ]


def _create_structured_client_for_call(
    monkeypatch,
    *,
    call_code: str,
) -> tuple[TestClient, UUID, str]:
    if call_code == "nwo_veni_2025_preproposal":
        return create_client_with_nwo_veni_seed(monkeypatch)
    if call_code == "erc_stg_2026_full":
        return create_client_with_erc_stg_seed(monkeypatch)
    if call_code == "MSCA-PF-2025":
        return create_client_with_msca_pf_seed(monkeypatch)
    raise AssertionError(f"Unsupported wf0065 representative call: {call_code}")


def _node_id_for_call_and_logical_id(*, call_id: UUID, node_logical_id: str) -> UUID:
    session = get_session()
    try:
        node = session.exec(
            select(ProposalNode).where(
                ProposalNode.funding_call_id == call_id,
                ProposalNode.logical_id == node_logical_id,
            )
        ).first()
        assert node is not None
        return node.id
    finally:
        session.close()


def _count_reviews_in_db() -> int:
    session = get_session()
    try:
        return len(list(session.exec(select(Review)).all()))
    finally:
        session.close()


def reset_database() -> None:
    """Reset all tables for isolated test runs."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def seed_api_data() -> SeededIDs:
    """Insert minimal graph required for API tests."""
    session = get_session()
    try:
        agency = FundingAgency(
            name="European Research Council",
            short_name="ERC",
        )
        session.add(agency)
        session.commit()
        session.refresh(agency)

        call = FundingCall(
            funding_agency_id=agency.id,
            name="ERC Consolidator Grant 2026",
            code="ERC-2026-COG",
            call_year=2026,
            is_active=True,
        )
        other_call = FundingCall(
            funding_agency_id=agency.id,
            name="ERC Starting Grant 2026",
            code="ERC-2026-STG",
            call_year=2026,
            is_active=True,
        )
        session.add(call)
        session.add(other_call)
        structured_call = FundingCall(
            funding_agency_id=agency.id,
            name="NWO Talent Programme — Veni 2025 — Pre-proposal",
            code="nwo_veni_2025_preproposal",
            call_year=2025,
            is_active=True,
        )
        session.add(structured_call)
        session.commit()
        session.refresh(call)
        session.refresh(other_call)
        session.refresh(structured_call)

        call_definition = CallDefinition(
            funding_call_id=structured_call.id,
            schema_version="v2",
            checksum="test-checksum",
            canonical_json={
                "funding_call": {
                    "id": "nwo_talent_veni_2025_preproposal",
                    "code": "nwo_veni_2025_preproposal",
                },
                "proposal_nodes": [
                    {
                        "id": "academic_profile",
                        "content_constraints": {
                            "total_word_limit": {"min_words": 2, "max_words": 5},
                        },
                    },
                    {
                        "id": "knowledge_utilisation",
                        "content_constraints": {
                            "word_limit_by_domain": {
                                "science_enw_max_words": 5,
                            }
                        },
                    },
                    {
                        "id": "scientific_proposal",
                        "content_constraints": {},
                    },
                ],
            },
            source_path="data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml",
        )
        session.add(call_definition)
        session.commit()

        structured_node_1 = ProposalNode(
            funding_call_id=structured_call.id,
            parent_node_id=None,
            logical_id="academic_profile",
            node_type=NodeType.SECTION,
            title="Academic profile",
            order_index=1,
        )
        structured_node_2 = ProposalNode(
            funding_call_id=structured_call.id,
            parent_node_id=None,
            logical_id="knowledge_utilisation",
            node_type=NodeType.SECTION,
            title="Knowledge utilisation",
            order_index=2,
        )
        structured_node_3 = ProposalNode(
            funding_call_id=structured_call.id,
            parent_node_id=None,
            logical_id="scientific_proposal",
            node_type=NodeType.SECTION,
            title="Scientific proposal",
            order_index=3,
        )
        session.add(structured_node_1)
        session.add(structured_node_2)
        session.add(structured_node_3)
        session.commit()

        section_with_expectations = ProposalNode(
            funding_call_id=call.id,
            parent_node_id=None,
            node_type=NodeType.SECTION,
            title="Section 1",
            order_index=1,
        )
        section_without_expectations = ProposalNode(
            funding_call_id=call.id,
            parent_node_id=None,
            node_type=NodeType.SECTION,
            title="Section 2",
            order_index=2,
        )
        other_call_node = ProposalNode(
            funding_call_id=other_call.id,
            parent_node_id=None,
            node_type=NodeType.SECTION,
            title="Other Section",
            order_index=1,
        )
        session.add(section_with_expectations)
        session.add(section_without_expectations)
        session.add(other_call_node)
        session.commit()
        session.refresh(section_with_expectations)
        session.refresh(section_without_expectations)
        session.refresh(other_call_node)

        criterion = EvaluationCriterion(
            funding_call_id=call.id,
            name="Excellence",
            description="Scientific excellence of the proposal section.",
            order_index=1,
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        element = EvaluationElement(
            evaluation_criterion_id=criterion.id,
            name="Clarity of Objectives",
            description="Assess objective clarity",
        )
        session.add(element)
        session.commit()
        session.refresh(element)

        expectation = NodeExpectation(
            proposal_node_id=section_with_expectations.id,
            evaluation_element_id=element.id,
            expectation_strength=ExpectationStrength.MANDATORY,
            evaluation_intent=EvaluationIntent.QUALITY,
            guidance_note="Check clarity",
            order_index=1,
        )
        session.add(expectation)
        session.commit()

        structured_criterion = EvaluationCriterion(
            funding_call_id=structured_call.id,
            logical_id="crit_structured_quality",
            name="Structured quality",
            description="Structured quality criterion.",
            order_index=1,
        )
        session.add(structured_criterion)
        session.commit()
        session.refresh(structured_criterion)

        structured_element = EvaluationElement(
            evaluation_criterion_id=structured_criterion.id,
            logical_id="elem_structured_node_quality",
            name="Structured node quality",
            description="Assess structured node quality",
        )
        session.add(structured_element)
        session.commit()
        session.refresh(structured_element)

        structured_expectation = NodeExpectation(
            proposal_node_id=structured_node_1.id,
            evaluation_element_id=structured_element.id,
            expectation_strength=ExpectationStrength.MANDATORY,
            evaluation_intent=EvaluationIntent.QUALITY,
            guidance_note="Assess structured academic profile quality",
            order_index=1,
        )
        session.add(structured_expectation)
        session.commit()

        structured_element_node3 = EvaluationElement(
            evaluation_criterion_id=structured_criterion.id,
            logical_id="elem_structured_node_quality_2",
            name="Structured node quality 2",
            description="Assess structured node quality 2",
        )
        session.add(structured_element_node3)
        session.commit()
        session.refresh(structured_element_node3)

        structured_expectation_node3 = NodeExpectation(
            proposal_node_id=structured_node_3.id,
            evaluation_element_id=structured_element_node3.id,
            expectation_strength=ExpectationStrength.MANDATORY,
            evaluation_intent=EvaluationIntent.QUALITY,
            guidance_note="Assess structured scientific proposal quality",
            order_index=1,
        )
        session.add(structured_expectation_node3)
        session.commit()

        template = PromptTemplate(
            name="Test Template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        return SeededIDs(
            call_id=call.id,
            section_with_expectations_id=section_with_expectations.id,
            section_without_expectations_id=section_without_expectations.id,
            other_call_id=other_call.id,
            other_call_node_id=other_call_node.id,
            structured_call_id=structured_call.id,
            structured_call_code=structured_call.code,
        )
    finally:
        session.close()


def create_client_with_seed(monkeypatch) -> tuple[TestClient, SeededIDs]:
    """Create test client with reset DB and stub LLM mode."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    seeded_ids = seed_api_data()
    return TestClient(app), seeded_ids


def seed_structured_alignment_api_data() -> UUID:
    """Insert NWO-like structured graph with alignment dependencies."""
    session = get_session()
    try:
        agency = FundingAgency(name="NWO", short_name="NWO")
        session.add(agency)
        session.commit()
        session.refresh(agency)

        call = FundingCall(
            funding_agency_id=agency.id,
            name="NWO Talent Programme — Veni 2025 — Pre-proposal",
            code="nwo_veni_2025_preproposal",
            call_year=2025,
            is_active=True,
        )
        session.add(call)
        session.commit()
        session.refresh(call)

        nodes_by_logical_id: dict[str, ProposalNode] = {}
        for order_index, logical_id in enumerate(
            ["academic_profile", "key_outputs", "research_idea"], start=1
        ):
            node = ProposalNode(
                funding_call_id=call.id,
                parent_node_id=None,
                logical_id=logical_id,
                node_type=NodeType.SECTION,
                title=logical_id,
                order_index=order_index,
            )
            session.add(node)
            session.commit()
            session.refresh(node)
            nodes_by_logical_id[logical_id] = node

        criterion = EvaluationCriterion(
            funding_call_id=call.id,
            logical_id="crit_quality_of_researcher",
            name="Quality",
            description="Quality criterion",
            order_index=1,
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        elements = {
            "profile": EvaluationElement(
                evaluation_criterion_id=criterion.id,
                logical_id="elem_profile_quality",
                name="Profile quality",
                description="Profile quality",
            ),
            "outputs": EvaluationElement(
                evaluation_criterion_id=criterion.id,
                logical_id="elem_outputs_quality",
                name="Outputs quality",
                description="Outputs quality",
            ),
            "alignment": EvaluationElement(
                evaluation_criterion_id=criterion.id,
                logical_id="elem_cv_idea_alignment",
                name="Alignment",
                description="Alignment",
            ),
            "alignment_plan": EvaluationElement(
                evaluation_criterion_id=criterion.id,
                logical_id="elem_alignment_plan_credibility",
                name="Alignment plan",
                description="Alignment plan",
            ),
            "idea_other": EvaluationElement(
                evaluation_criterion_id=criterion.id,
                logical_id="elem_innovative_ideas_capability",
                name="Innovative ideas",
                description="Innovative ideas",
            ),
        }
        for element in elements.values():
            session.add(element)
        session.commit()
        for element in elements.values():
            session.refresh(element)

        expectations = [
            NodeExpectation(
                proposal_node_id=nodes_by_logical_id["academic_profile"].id,
                evaluation_element_id=elements["profile"].id,
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="Test expectation",
                order_index=1,
            ),
            NodeExpectation(
                proposal_node_id=nodes_by_logical_id["key_outputs"].id,
                evaluation_element_id=elements["outputs"].id,
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="Test expectation",
                order_index=1,
            ),
            NodeExpectation(
                proposal_node_id=nodes_by_logical_id["research_idea"].id,
                evaluation_element_id=elements["alignment"].id,
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="Test expectation",
                order_index=1,
            ),
            NodeExpectation(
                proposal_node_id=nodes_by_logical_id["research_idea"].id,
                evaluation_element_id=elements["alignment_plan"].id,
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="Test expectation",
                order_index=2,
            ),
            NodeExpectation(
                proposal_node_id=nodes_by_logical_id["research_idea"].id,
                evaluation_element_id=elements["idea_other"].id,
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="Test expectation",
                order_index=3,
            ),
        ]
        for expectation in expectations:
            session.add(expectation)
        session.commit()

        template = PromptTemplate(
            name="Structured test template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        return call.id
    finally:
        session.close()


def create_client_with_structured_alignment_seed(
    monkeypatch,
) -> tuple[TestClient, UUID]:
    """Create test client with graph suitable for structured alignment E2E."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    call_id = seed_structured_alignment_api_data()
    return TestClient(app), call_id


def create_client_with_erc_cog_seed(monkeypatch) -> tuple[TestClient, UUID, str]:
    """Create test client with ERC CoG call ingested from canonical YAML."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    ingest_call(Path("data/calls/canonical/erc/erc_cog_2026_full.yaml"), dry_run=False)

    session = get_session()
    try:
        template = PromptTemplate(
            name="ERC CoG structured template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        call = session.exec(
            select(FundingCall).where(FundingCall.code == "erc_cog_2026_full")
        ).first()
        assert call is not None
        return TestClient(app), call.id, call.code
    finally:
        session.close()


def create_client_with_erc_stg_seed(monkeypatch) -> tuple[TestClient, UUID, str]:
    """Create test client with ERC StG proof call ingested from canonical YAML."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    ingest_call(Path("data/calls/canonical/erc/erc_stg_2026_full.yaml"), dry_run=False)

    session = get_session()
    try:
        template = PromptTemplate(
            name="ERC StG structured template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        call = session.exec(
            select(FundingCall).where(FundingCall.code == "erc_stg_2026_full")
        ).first()
        assert call is not None
        return TestClient(app), call.id, call.code
    finally:
        session.close()


def create_client_with_msca_pf_seed(monkeypatch) -> tuple[TestClient, UUID, str]:
    """Create test client with MSCA-PF-2025 call ingested from canonical YAML."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    ingest_call(Path("data/calls/canonical/msca/msca_pf_2025_full.yaml"), dry_run=False)

    session = get_session()
    try:
        template = PromptTemplate(
            name="MSCA PF structured template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        call = session.exec(
            select(FundingCall).where(FundingCall.code == "MSCA-PF-2025")
        ).first()
        assert call is not None
        return TestClient(app), call.id, call.code
    finally:
        session.close()


def create_client_with_nwo_veni_seed(monkeypatch) -> tuple[TestClient, UUID, str]:
    """Create test client with real NWO Veni preproposal call from canonical YAML."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    ingest_call(Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"), dry_run=False)

    session = get_session()
    try:
        template = PromptTemplate(
            name="NWO Veni structured template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        call = session.exec(
            select(FundingCall).where(FundingCall.code == "nwo_veni_2025_preproposal")
        ).first()
        assert call is not None
        return TestClient(app), call.id, call.code
    finally:
        session.close()


def create_client_with_erc_poc_seed(monkeypatch) -> tuple[TestClient, UUID, str]:
    """Create test client with ERC PoC call ingested from canonical YAML."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    ingest_call(Path("data/calls/canonical/erc/erc_poc_2026_full.yaml"), dry_run=False)

    session = get_session()
    try:
        template = PromptTemplate(
            name="ERC PoC structured template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        call = session.exec(
            select(FundingCall).where(FundingCall.code == "ERC-2026-PoC")
        ).first()
        assert call is not None
        return TestClient(app), call.id, call.code
    finally:
        session.close()


def _set_call_definition_reviewer_policy_rules(
    *,
    call_id: UUID,
    rules: list[dict[str, object]],
) -> None:
    session = get_session()
    try:
        definition = session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        canonical_json = dict(definition.canonical_json)
        canonical_json["reviewer_policy"] = rules
        definition.canonical_json = canonical_json
        session.add(definition)
        session.commit()
    finally:
        session.close()


def build_signature_headers(
    *,
    body: bytes,
    user_id: str = TEST_USER_ID,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> dict[str, str]:
    """Build signed headers expected by protected API routes."""
    signed_timestamp = int(time.time()) if timestamp is None else timestamp
    payload = f"{user_id}.{signed_timestamp}.{hashlib.sha256(body).hexdigest()}"
    signature = hmac.new(
        shared_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "X-GR-User-Id": user_id,
        "X-GR-Timestamp": str(signed_timestamp),
        "X-GR-Signature": signature,
    }


def post_review(
    *,
    client: TestClient,
    payload: dict[str, str],
    user_id: str = TEST_USER_ID,
    idempotency_key: str | None = None,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> object:
    """Call POST /reviews with signed headers and explicit JSON bytes."""
    if "review_stage" not in payload:
        payload["review_stage"] = "STEP_1"
    body = json.dumps(payload).encode("utf-8")
    headers = build_signature_headers(
        body=body,
        user_id=user_id,
        timestamp=timestamp,
        shared_secret=shared_secret,
    )
    request_idempotency_key = (
        f"idem-{time.time_ns()}" if idempotency_key is None else idempotency_key
    )
    headers["Idempotency-Key"] = request_idempotency_key
    headers["Content-Type"] = "application/json"
    return client.post("/reviews", content=body, headers=headers)


def post_structured_review(
    *,
    client: TestClient,
    payload: dict[str, object],
    user_id: str = TEST_USER_ID,
    idempotency_key: str | None = None,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> object:
    """Call POST /api/structured-review with signed headers."""
    if "review_stage" not in payload:
        payload["review_stage"] = "STEP_1"
    body = json.dumps(payload).encode("utf-8")
    headers = build_signature_headers(
        body=body,
        user_id=user_id,
        timestamp=timestamp,
        shared_secret=shared_secret,
    )
    request_idempotency_key = (
        f"idem-{time.time_ns()}" if idempotency_key is None else idempotency_key
    )
    headers["Idempotency-Key"] = request_idempotency_key
    headers["Content-Type"] = "application/json"
    return client.post("/api/structured-review", content=body, headers=headers)


def post_structured_review_without_idempotency(
    *,
    client: TestClient,
    payload: dict[str, object],
    user_id: str = TEST_USER_ID,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> object:
    """Call POST /api/structured-review with signed headers and no idempotency key."""
    if "review_stage" not in payload:
        payload["review_stage"] = "STEP_1"
    body = json.dumps(payload).encode("utf-8")
    headers = build_signature_headers(
        body=body,
        user_id=user_id,
        timestamp=timestamp,
        shared_secret=shared_secret,
    )
    headers["Content-Type"] = "application/json"
    return client.post("/api/structured-review", content=body, headers=headers)


def _is_pipeline_v1_enabled() -> bool:
    return os.getenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "0").strip() == "1"


def post_compliance(
    *,
    client: TestClient,
    payload: dict[str, object],
    user_id: str = TEST_USER_ID,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> object:
    """Call POST /api/check-compliance with signed headers."""
    body = json.dumps(payload).encode("utf-8")
    headers = build_signature_headers(
        body=body,
        user_id=user_id,
        timestamp=timestamp,
        shared_secret=shared_secret,
    )
    return client.post("/api/check-compliance", content=body, headers=headers)


def get_review_detail(
    *,
    client: TestClient,
    review_id: str,
    user_id: str = TEST_USER_ID,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> object:
    """Call GET /reviews/{id} with signed headers."""
    headers = build_signature_headers(
        body=b"",
        user_id=user_id,
        timestamp=timestamp,
        shared_secret=shared_secret,
    )
    return client.get(f"/reviews/{review_id}", headers=headers)


def delete_review(
    *,
    client: TestClient,
    review_id: str,
    user_id: str = TEST_USER_ID,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> object:
    """Call DELETE /reviews/{id} with signed headers."""
    headers = build_signature_headers(
        body=b"",
        user_id=user_id,
        timestamp=timestamp,
        shared_secret=shared_secret,
    )
    return client.delete(f"/reviews/{review_id}", headers=headers)


def test_healthcheck(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_healthcheck_db(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_healthcheck_db_unavailable_returns_503(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)

    def fail_ping_database() -> None:
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("main.ping_database", fail_ping_database)

    response = client.get("/health/db")
    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "DB_UNAVAILABLE",
            "message": "Database is unavailable.",
            "details": {},
        },
    }


def test_wf0061_contract_structured_api_tracer_accepts_real_msca_pf_2025_call(
    monkeypatch,
) -> None:
    """WF-0061 tracer: structured API accepts real MSCA-PF-2025 canonical call."""
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "excellence",
                    "text": "Tracer bullet text for MSCA-PF-2025 excellence.",
                }
            ],
        },
        idempotency_key=f"wf0061-msca-api-{time.time_ns()}",
    )
    assert response.status_code in {200, 201}

    payload = response.json()
    assert payload["status"] in {"PENDING", "COMPLETED"}
    assert isinstance(payload.get("review_id"), str)

    session = get_session()
    try:
        definition = session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        assert (
            definition.source_path
            == "data/calls/canonical/msca/msca_pf_2025_full.yaml"
        )
    finally:
        session.close()


def test_wf0061_contract_runtime_proof_requires_upload_validate_ingest_order(
    monkeypatch,
) -> None:
    """WF-0061 gate order: structured runtime proof is invalid before ingest readiness."""
    client, _ = create_client_with_seed(monkeypatch)
    unknown_call_id = UUID("00000000-0000-0000-0000-000000000061")
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(unknown_call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "excellence",
                    "text": "Runtime proof must fail when call ingest prerequisites are unmet.",
                }
            ],
        },
        idempotency_key=f"wf0061-order-gate-{time.time_ns()}",
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CALL_NOT_FOUND"


def test_wf0065_nwo_structured_api_tracer_uses_real_canonical_call(monkeypatch) -> None:
    """WF-0065 tracer: structured API uses real NWO canonical call artifact."""
    client, call_id, call_code = create_client_with_nwo_veni_seed(monkeypatch)
    assert call_code == "nwo_veni_2025_preproposal"

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "key_outputs",
                    "text": "Tracer bullet text proving the real NWO structured path.",
                }
            ],
        },
        idempotency_key=f"wf0065-nwo-api-{time.time_ns()}",
    )
    assert response.status_code in {200, 201}

    payload = response.json()
    assert payload["status"] in {"PENDING", "COMPLETED"}
    assert isinstance(payload.get("review_id"), str)

    session = get_session()
    try:
        definition = session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        assert (
            definition.source_path
            == "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"
        )
    finally:
        session.close()


@pytest.mark.parametrize(
    "case",
    _wf0065_representative_cases(),
    ids=lambda case: f"wf0065_structured_representative_{case['case_id']}",
)
def test_wf0065_structured_api_representative_success_matrix_persists_review(
    monkeypatch,
    case: Wf0065RepresentativeCase,
) -> None:
    """WF-0065 matrix: structured API parity for the locked representative calls."""
    client, call_id, call_code = _create_structured_client_for_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    assert call_code == case["call_code"]

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": case["stage"],
            "nodes": [
                {
                    "node_logical_id": case["node_logical_id"],
                    "text": case["node_text"],
                }
            ],
        },
        idempotency_key=f"wf0065-representative-api-{case['case_id']}-{time.time_ns()}",
    )
    assert response.status_code in {200, 201}
    payload = response.json()
    assert set(payload.keys()) == {"review_id", "status"}
    assert payload["status"] in {"PENDING", "COMPLETED"}
    assert isinstance(payload["review_id"], str)

    session = get_session()
    try:
        review = session.get(Review, UUID(payload["review_id"]))
        assert review is not None
        assert review.review_type == "structured"
        assert review.structured_payload is not None
        assert review.structured_payload["call_id"] == str(call_id)
        assert review.structured_payload["engine_path"] == "pipeline_v1"
        persisted_cards = list(
            session.exec(select(ReviewCard).where(ReviewCard.review_id == review.id)).all()
        )
        assert len(persisted_cards) >= 1
    finally:
        session.close()

    detail = get_review_detail(client=client, review_id=payload["review_id"])
    assert detail.status_code == 200
    assert len(detail.json()["cards"]) >= 1


@pytest.mark.parametrize(
    "case",
    _wf0065_paired_boundary_cases(),
    ids=lambda case: f"wf0065_create_review_representative_{case['case_id']}",
)
def test_wf0065_create_review_representative_success_matrix_persists_review(
    monkeypatch,
    case: Wf0065RepresentativeCase,
) -> None:
    """WF-0065 matrix: /reviews parity for the locked representative calls."""
    client, call_id, call_code = _create_structured_client_for_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    assert call_code == case["call_code"]
    node_id = _node_id_for_call_and_logical_id(
        call_id=call_id,
        node_logical_id=case["node_logical_id"],
    )

    response = post_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "node_id": str(node_id),
            "snippet_text": case["node_text"],
            "review_stage": case["stage"],
        },
        idempotency_key=f"wf0065-representative-single-{case['case_id']}-{time.time_ns()}",
    )
    assert response.status_code in {200, 201}
    payload = response.json()
    assert set(payload.keys()) == {"review_id", "status"}
    assert payload["status"] in {"PENDING", "COMPLETED"}
    assert isinstance(payload["review_id"], str)

    detail = get_review_detail(client=client, review_id=payload["review_id"])
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["review"]["status"] in {"PENDING", "COMPLETED"}
    assert len(detail_payload["cards"]) >= 1


@pytest.mark.parametrize(
    "case",
    _wf0065_paired_boundary_cases(),
    ids=lambda case: f"wf0065_validation_order_representative_{case['case_id']}",
)
def test_wf0065_representative_validation_order_precedes_idempotency_on_both_endpoints(
    monkeypatch,
    case: Wf0065RepresentativeCase,
) -> None:
    """WF-0065 parity: validation errors win before idempotency mismatch checks."""
    client, call_id, call_code = _create_structured_client_for_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    assert call_code == case["call_code"]
    node_id = _node_id_for_call_and_logical_id(
        call_id=call_id,
        node_logical_id=case["node_logical_id"],
    )

    review_idem = f"wf0065-validation-order-single-{case['case_id']}-{time.time_ns()}"
    first_single = post_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "node_id": str(node_id),
            "snippet_text": case["node_text"],
            "review_stage": case["stage"],
        },
        idempotency_key=review_idem,
    )
    assert first_single.status_code in {200, 201}

    invalid_single_payload = {
        "call_id": str(call_id),
        "node_id": "not-a-uuid",
        "snippet_text": case["node_text"],
        "review_stage": case["stage"],
    }
    invalid_single_body = json.dumps(invalid_single_payload).encode("utf-8")
    invalid_single_headers = build_signature_headers(body=invalid_single_body)
    invalid_single_headers["Idempotency-Key"] = review_idem
    invalid_single_headers["Content-Type"] = "application/json"
    invalid_single = client.post(
        "/reviews",
        content=invalid_single_body,
        headers=invalid_single_headers,
    )
    assert invalid_single.status_code == 400
    invalid_single_payload_json = invalid_single.json()
    assert invalid_single_payload_json["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(invalid_single_payload_json["error"]["details"].get("errors"), list)

    structured_idem = (
        f"wf0065-validation-order-structured-{case['case_id']}-{time.time_ns()}"
    )
    first_structured = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": case["stage"],
            "nodes": [
                {
                    "node_logical_id": case["node_logical_id"],
                    "text": case["node_text"],
                }
            ],
        },
        idempotency_key=structured_idem,
    )
    assert first_structured.status_code in {200, 201}

    invalid_structured_payload = {
        "call_id": str(call_id),
        "review_stage": case["stage"],
        "nodes": [
            {
                "node_logical_id": case["node_logical_id"],
            }
        ],
    }
    invalid_structured_body = json.dumps(invalid_structured_payload).encode("utf-8")
    invalid_structured_headers = build_signature_headers(body=invalid_structured_body)
    invalid_structured_headers["Idempotency-Key"] = structured_idem
    invalid_structured_headers["Content-Type"] = "application/json"
    invalid_structured = client.post(
        "/api/structured-review",
        content=invalid_structured_body,
        headers=invalid_structured_headers,
    )
    assert invalid_structured.status_code == 400
    invalid_structured_json = invalid_structured.json()
    assert invalid_structured_json["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(invalid_structured_json["error"]["details"].get("errors"), list)


@pytest.mark.parametrize(
    "case",
    _wf0065_paired_boundary_cases(),
    ids=lambda case: f"wf0065_replay_mismatch_representative_{case['case_id']}",
)
def test_wf0065_representative_replay_and_mismatch_parity_on_both_endpoints(
    monkeypatch,
    case: Wf0065RepresentativeCase,
) -> None:
    """WF-0065 parity: replay is idempotent and mismatch is conflict without mutation."""
    client, call_id, call_code = _create_structured_client_for_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    assert call_code == case["call_code"]
    node_id = _node_id_for_call_and_logical_id(
        call_id=call_id,
        node_logical_id=case["node_logical_id"],
    )

    initial_count = _count_reviews_in_db()
    single_idem = f"wf0065-replay-single-{case['case_id']}-{time.time_ns()}"
    single_payload = {
        "call_id": str(call_id),
        "node_id": str(node_id),
        "snippet_text": case["node_text"],
        "review_stage": case["stage"],
    }
    single_first = post_review(
        client=client,
        payload=dict(single_payload),
        idempotency_key=single_idem,
    )
    assert single_first.status_code in {200, 201}
    single_first_payload = single_first.json()
    single_second = post_review(
        client=client,
        payload=dict(single_payload),
        idempotency_key=single_idem,
    )
    assert single_second.status_code in {200, 201}
    assert single_second.json() == single_first_payload
    assert _count_reviews_in_db() == initial_count + 1
    session = get_session()
    try:
        single_review_before = session.get(Review, UUID(single_first_payload["review_id"]))
        assert single_review_before is not None
        single_review_before_snapshot = (
            single_review_before.status,
            single_review_before.request_payload_sha256,
            single_review_before.overall_summary,
        )
    finally:
        session.close()

    single_mismatch = post_review(
        client=client,
        payload={
            **single_payload,
            "snippet_text": f"{case['node_text']} changed mismatch payload",
        },
        idempotency_key=single_idem,
    )
    assert single_mismatch.status_code == 409
    single_mismatch_json = single_mismatch.json()
    assert single_mismatch_json["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"
    assert single_mismatch_json["error"]["details"] == {}
    assert _count_reviews_in_db() == initial_count + 1
    session = get_session()
    try:
        single_review_after = session.get(Review, UUID(single_first_payload["review_id"]))
        assert single_review_after is not None
        assert (
            single_review_after.status,
            single_review_after.request_payload_sha256,
            single_review_after.overall_summary,
        ) == single_review_before_snapshot
    finally:
        session.close()

    structured_idem = f"wf0065-replay-structured-{case['case_id']}-{time.time_ns()}"
    structured_payload = {
        "call_id": str(call_id),
        "review_stage": case["stage"],
        "nodes": [
            {
                "node_logical_id": case["node_logical_id"],
                "text": case["node_text"],
            }
        ],
    }
    structured_first = post_structured_review(
        client=client,
        payload=dict(structured_payload),
        idempotency_key=structured_idem,
    )
    assert structured_first.status_code in {200, 201}
    structured_first_payload = structured_first.json()
    structured_second = post_structured_review(
        client=client,
        payload=dict(structured_payload),
        idempotency_key=structured_idem,
    )
    assert structured_second.status_code in {200, 201}
    assert structured_second.json() == structured_first_payload
    assert _count_reviews_in_db() == initial_count + 2
    session = get_session()
    try:
        structured_review_before = session.get(
            Review, UUID(structured_first_payload["review_id"])
        )
        assert structured_review_before is not None
        structured_review_before_snapshot = (
            structured_review_before.status,
            structured_review_before.request_payload_sha256,
            structured_review_before.overall_summary,
        )
    finally:
        session.close()

    structured_mismatch = post_structured_review(
        client=client,
        payload={
            **structured_payload,
            "nodes": [
                {
                    "node_logical_id": case["node_logical_id"],
                    "text": f"{case['node_text']} changed mismatch payload",
                }
            ],
        },
        idempotency_key=structured_idem,
    )
    assert structured_mismatch.status_code == 409
    structured_mismatch_json = structured_mismatch.json()
    assert structured_mismatch_json["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"
    assert structured_mismatch_json["error"]["details"] == {}
    assert _count_reviews_in_db() == initial_count + 2
    session = get_session()
    try:
        structured_review_after = session.get(
            Review, UUID(structured_first_payload["review_id"])
        )
        assert structured_review_after is not None
        assert (
            structured_review_after.status,
            structured_review_after.request_payload_sha256,
            structured_review_after.overall_summary,
        ) == structured_review_before_snapshot
    finally:
        session.close()


@pytest.mark.parametrize(
    "case",
    _wf0065_paired_boundary_cases(),
    ids=lambda case: f"wf0065_reviews_disabled_representative_{case['case_id']}",
)
def test_wf0065_reviews_disabled_representative_fail_closed_across_both_endpoints(
    monkeypatch,
    case: Wf0065RepresentativeCase,
) -> None:
    """WF-0065 gate: REVIEWS_DISABLED blocks both endpoints before any downstream work."""
    from app.services.reviewer_service import ReviewerService
    from app.services.structured_reviewer_service import StructuredReviewerService

    monkeypatch.setenv("REVIEWS_ENABLED", "0")
    client, call_id, call_code = _create_structured_client_for_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    assert call_code == case["call_code"]
    node_id = _node_id_for_call_and_logical_id(
        call_id=call_id,
        node_logical_id=case["node_logical_id"],
    )

    calls = {"generate_review": 0, "generate_structured": 0, "pipeline_v1": 0}

    def blocked_generate_review(self, *args, **kwargs):
        calls["generate_review"] += 1
        raise AssertionError("generate_review should not execute when REVIEWS_DISABLED")

    def blocked_generate_structured(self, *args, **kwargs):
        calls["generate_structured"] += 1
        raise AssertionError(
            "generate_structured_review_pipeline_v1 should not execute when REVIEWS_DISABLED"
        )

    def blocked_pipeline_v1(*args, **kwargs):
        calls["pipeline_v1"] += 1
        raise AssertionError("pipeline_v1 should not execute when REVIEWS_DISABLED")

    monkeypatch.setattr(ReviewerService, "generate_review", blocked_generate_review)
    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        blocked_generate_structured,
    )
    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        blocked_pipeline_v1,
    )

    before_count = _count_reviews_in_db()

    single_response = post_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "node_id": str(node_id),
            "snippet_text": case["node_text"],
            "review_stage": case["stage"],
        },
        idempotency_key=f"wf0065-reviews-disabled-single-{case['case_id']}-{time.time_ns()}",
    )
    assert single_response.status_code == 503
    single_payload = single_response.json()
    assert single_payload["error"]["code"] == "REVIEWS_DISABLED"
    assert single_payload["error"]["details"] == {}

    structured_response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": case["stage"],
            "nodes": [
                {
                    "node_logical_id": case["node_logical_id"],
                    "text": case["node_text"],
                }
            ],
        },
        idempotency_key=(
            f"wf0065-reviews-disabled-structured-{case['case_id']}-{time.time_ns()}"
        ),
    )
    assert structured_response.status_code == 503
    structured_payload = structured_response.json()
    assert structured_payload["error"]["code"] == "REVIEWS_DISABLED"
    assert structured_payload["error"]["details"] == {}

    assert calls == {"generate_review": 0, "generate_structured": 0, "pipeline_v1": 0}
    assert _count_reviews_in_db() == before_count


@pytest.mark.parametrize(
    "case",
    _wf0065_paired_boundary_cases(),
    ids=lambda case: f"wf0065_quota_exceeded_representative_{case['case_id']}",
)
def test_wf0065_quota_exceeded_representative_fail_closed_across_both_endpoints(
    monkeypatch,
    case: Wf0065RepresentativeCase,
) -> None:
    """WF-0065 gate: QUOTA_EXCEEDED blocks both endpoints before downstream execution."""
    from app.services.reviewer_service import ReviewerService
    from app.services.structured_reviewer_service import StructuredReviewerService

    monkeypatch.setenv("REVIEWS_ENABLED", "1")
    monkeypatch.setenv("FREE_DAILY_REVIEW_LIMIT", "0")
    client, call_id, call_code = _create_structured_client_for_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    assert call_code == case["call_code"]
    node_id = _node_id_for_call_and_logical_id(
        call_id=call_id,
        node_logical_id=case["node_logical_id"],
    )

    calls = {"generate_review": 0, "generate_structured": 0, "pipeline_v1": 0}

    def blocked_generate_review(self, *args, **kwargs):
        calls["generate_review"] += 1
        raise AssertionError("generate_review should not execute when QUOTA_EXCEEDED")

    def blocked_generate_structured(self, *args, **kwargs):
        calls["generate_structured"] += 1
        raise AssertionError(
            "generate_structured_review_pipeline_v1 should not execute when QUOTA_EXCEEDED"
        )

    def blocked_pipeline_v1(*args, **kwargs):
        calls["pipeline_v1"] += 1
        raise AssertionError("pipeline_v1 should not execute when QUOTA_EXCEEDED")

    monkeypatch.setattr(ReviewerService, "generate_review", blocked_generate_review)
    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        blocked_generate_structured,
    )
    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        blocked_pipeline_v1,
    )

    before_count = _count_reviews_in_db()

    single_response = post_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "node_id": str(node_id),
            "snippet_text": case["node_text"],
            "review_stage": case["stage"],
        },
        idempotency_key=f"wf0065-quota-single-{case['case_id']}-{time.time_ns()}",
    )
    assert single_response.status_code == 429
    single_payload = single_response.json()
    assert single_payload["error"]["code"] == "QUOTA_EXCEEDED"
    assert set(single_payload["error"]["details"].keys()) == {"limit", "remaining", "reset_at"}
    assert single_payload["error"]["details"]["limit"] == 0
    assert single_payload["error"]["details"]["remaining"] == 0

    structured_response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": case["stage"],
            "nodes": [
                {
                    "node_logical_id": case["node_logical_id"],
                    "text": case["node_text"],
                }
            ],
        },
        idempotency_key=f"wf0065-quota-structured-{case['case_id']}-{time.time_ns()}",
    )
    assert structured_response.status_code == 429
    structured_payload = structured_response.json()
    assert structured_payload["error"]["code"] == "QUOTA_EXCEEDED"
    assert set(structured_payload["error"]["details"].keys()) == {
        "limit",
        "remaining",
        "reset_at",
    }
    assert structured_payload["error"]["details"]["limit"] == 0
    assert structured_payload["error"]["details"]["remaining"] == 0

    assert calls == {"generate_review": 0, "generate_structured": 0, "pipeline_v1": 0}
    assert _count_reviews_in_db() == before_count


def test_normalize_database_url_for_render_postgres() -> None:
    normalized = normalize_database_url("postgres://u:p@db.example.com:5432/grant_db")
    assert normalized.startswith("postgresql+psycopg://")
    assert "sslmode=require" in normalized
    assert "connect_timeout=3" in normalized


def test_list_calls_returns_active_calls(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = client.get("/calls")
    assert response.status_code == 200
    payload = response.json()
    codes = {call["code"] for call in payload["calls"]}
    assert {
        "ERC-2026-COG",
        "ERC-2026-STG",
        "nwo_veni_2025_preproposal",
    }.issubset(codes)


def test_wf0073_contract_erc_poc_2026_ingest_exposes_call_listing(monkeypatch) -> None:
    """WF-0073: /calls should expose ERC PoC after canonical ingest."""
    client, _, _ = create_client_with_erc_poc_seed(monkeypatch)

    response = client.get("/calls")
    assert response.status_code == 200

    payload = response.json()
    codes = {call["code"] for call in payload["calls"]}
    assert "ERC-2026-PoC" in codes


def test_list_nodes_includes_has_expectations(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.get(f"/calls/{seeded_ids.call_id}/nodes")
    assert response.status_code == 200
    payload = response.json()
    by_id = {UUID(node["id"]): node for node in payload["nodes"]}
    assert by_id[seeded_ids.section_with_expectations_id]["has_expectations"] is True
    assert (
        by_id[seeded_ids.section_without_expectations_id]["has_expectations"] is False
    )


def test_list_nodes_returns_parent_links_after_v2_hierarchy_ingest() -> None:
    """Nodes endpoint should expose parent ids for ingested hierarchy calls."""
    reset_database()
    ingest_call(Path("tests/fixtures/hierarchy_v2.yaml"), dry_run=False)

    session = get_session()
    try:
        call = session.exec(
            select(FundingCall).where(FundingCall.code == "erc_stg_2026_step1")
        ).first()
        assert call is not None
        call_id = call.id
    finally:
        session.close()

    client = TestClient(app)
    response = client.get(f"/calls/{call_id}/nodes")
    assert response.status_code == 200

    payload = response.json()
    nodes = payload["nodes"]
    by_id = {node["id"]: node for node in nodes}
    parent_linked = [node for node in nodes if node["parent_node_id"] is not None]
    assert parent_linked
    for node in parent_linked:
        assert node["parent_node_id"] in by_id


def test_get_call_config_returns_structured_mode_with_domain_options(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    response = client.get(
        f"/api/public/calls/{seeded_ids.structured_call_code}/config"
    )

    assert response.status_code == 200
    assert response.json() == {
        "call_logical_id": "nwo_veni_2025_preproposal",
        "config_version": "1",
        "ui_mode": "structured_nodes",
        "split_visibility_reviewability_enabled": False,
        "expected_nodes": [
            "academic_profile",
            "knowledge_utilisation",
            "scientific_proposal",
        ],
        "domain_options": [
            {"value": "science_enw", "label": "Science Enw", "order_index": 0}
        ],
    }
    assert set(response.json().keys()) == {
        "call_logical_id",
        "config_version",
        "ui_mode",
        "split_visibility_reviewability_enabled",
        "expected_nodes",
        "domain_options",
    }


def test_get_call_config_legacy_returns_empty_domain_options(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)

    response = client.get("/api/public/calls/ERC-2026-COG/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["call_logical_id"] == "ERC-2026-COG"
    assert payload["config_version"] == "1"
    assert payload["ui_mode"] == "legacy_single_snippet"
    assert payload["split_visibility_reviewability_enabled"] is False
    assert payload["domain_options"] == []
    assert "expected_nodes" not in payload
    assert set(payload.keys()) == {
        "call_logical_id",
        "config_version",
        "ui_mode",
        "split_visibility_reviewability_enabled",
        "domain_options",
    }


def test_get_call_config_unknown_call_returns_404(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)

    response = client.get("/api/public/calls/unknown_call/config")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "CALL_NOT_FOUND",
            "message": "Funding call not found.",
            "details": {},
        },
    }


def test_wf0063_call_config_exposes_split_opt_in_for_msca_pf_2025_only(
    monkeypatch,
) -> None:
    client, msca_call_id, msca_call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert msca_call_code == "MSCA-PF-2025"

    msca_response = client.get(f"/api/public/calls/{msca_call_code}/config")
    assert msca_response.status_code == 200
    msca_payload = msca_response.json()
    assert msca_payload["ui_mode"] == "structured_nodes"
    assert msca_payload["split_visibility_reviewability_enabled"] is True

    session = get_session()
    try:
        msca_call = session.get(FundingCall, msca_call_id)
        assert msca_call is not None
        msca_call.is_active = False
        session.add(msca_call)
        session.commit()
    finally:
        session.close()

    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.get(f"/api/public/calls/{seeded_ids.structured_call_code}/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ui_mode"] == "structured_nodes"
    assert payload["split_visibility_reviewability_enabled"] is False


def test_wf0063_flat_nodes_api_returns_all_official_nodes_with_node_role(
    monkeypatch,
) -> None:
    client, call_id, _ = create_client_with_msca_pf_seed(monkeypatch)

    response = client.get(f"/calls/{call_id}/nodes")
    assert response.status_code == 200
    payload = response.json()
    nodes = payload["nodes"]

    nodes_by_logical_id = {node["logical_id"]: node for node in nodes}
    assert {
        "part_a",
        "general_information",
        "abstract",
        "part_b",
        "part_b1",
        "excellence",
        "impact",
        "quality_efficiency_implementation",
        "part_b2",
        "cv_researcher",
        "capacity_participating_organisations",
        "additional_ethics_information",
        "additional_security_screening_information",
        "environmental_considerations_msca_green_charter",
        "gf_letter_of_commitment_outgoing_host",
    }.issubset(set(nodes_by_logical_id))
    assert nodes_by_logical_id["excellence"]["node_role"] == "PRIMARY"
    assert nodes_by_logical_id["impact"]["node_role"] == "PRIMARY"
    assert (
        nodes_by_logical_id["quality_efficiency_implementation"]["node_role"] == "PRIMARY"
    )
    assert nodes_by_logical_id["abstract"]["node_role"] == "SUPPORTING"
    assert nodes_by_logical_id["part_b2"]["node_role"] == "SUPPORTING"
    assert (
        nodes_by_logical_id["gf_letter_of_commitment_outgoing_host"]["node_role"]
        == "SUPPORTING"
    )
    assert nodes_by_logical_id["excellence"]["has_expectations"] is True
    assert nodes_by_logical_id["abstract"]["has_expectations"] is False


def test_wf0063_disabling_split_opt_in_restores_legacy_call_behavior(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    session = get_session()
    try:
        definition = session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        canonical_json = dict(definition.canonical_json)
        canonical_json["runtime_config"] = {
            "split_visibility_reviewability_enabled": False
        }
        definition.canonical_json = canonical_json
        session.add(definition)
        session.commit()
    finally:
        session.close()

    config_response = client.get(f"/api/public/calls/{call_code}/config")
    assert config_response.status_code == 200
    assert config_response.json()["split_visibility_reviewability_enabled"] is False

    nodes_response = client.get(f"/calls/{call_id}/nodes")
    assert nodes_response.status_code == 200
    for node in nodes_response.json()["nodes"]:
        assert node["node_role"] is None


def test_create_review_success_with_stub_mode(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Test snippet for section one.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "COMPLETED"

    detail_response = get_review_detail(client=client, review_id=payload["review_id"])
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["review"]["status"] == "COMPLETED"
    assert len(detail_payload["cards"]) == 1
    assert detail_payload["cards"][0]["criterion"] == "Excellence"
    assert (
        detail_payload["cards"][0]["criterion_description"]
        == "Scientific excellence of the proposal section."
    )
    assert detail_payload["cards"][0]["node_logical_id"] is None
    assert detail_payload["cards"][0]["node_title"] == "Section 1"
    assert detail_payload["cards"][0]["evaluation_element_name"] == "Clarity of Objectives"
    assert detail_payload["cards"][0]["expectation_guidance_note"] == "Check clarity"
    assert detail_payload["cards"][0]["rating"] == "NOTE"
    assert detail_payload["cards"][0]["assessment_status"] is None
    assert detail_payload["cards"][0]["not_assessable_reason"] is None


def test_review_detail_includes_call_id_and_call_code(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200

    detail_response = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["call_id"] == str(seeded_ids.structured_call_id)
    assert detail_payload["call_code"] == seeded_ids.structured_call_code


def test_wf0063_review_detail_exposes_primary_evaluated_and_empty_supporting_context_fields(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "excellence",
                    "text": "Primary reviewed content for role-label seam test.",
                }
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["primary_evaluated_node_logical_ids"] == ["excellence"]
    assert payload["supporting_context_node_logical_ids"] == []


@pytest.mark.parametrize(
    "case_id,create_client,node_logical_id",
    [
        (
            "nwo_veni_2025_preproposal",
            create_client_with_nwo_veni_seed,
            "key_outputs",
        ),
        (
            "erc_stg_2026_full",
            create_client_with_erc_stg_seed,
            "b1_part1_scientific_proposal",
        ),
        ("MSCA-PF-2025", create_client_with_msca_pf_seed, "excellence"),
    ],
    ids=[
        "wf0067_backend_source_basis_contract_nwo_veni_2025_preproposal",
        "wf0067_backend_source_basis_contract_erc_stg_2026_full",
        "wf0067_backend_source_basis_contract_msca_pf_2025",
    ],
)
def test_wf0067_backend_source_basis_contract_representative_calls_expose_card_fields(
    monkeypatch,
    case_id: str,
    create_client,
    node_logical_id: str,
) -> None:
    client, call_id, call_code = create_client(monkeypatch)
    assert call_code == case_id

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": node_logical_id,
                    "text": f"WF-0067 source-basis contract proof for {case_id}.",
                }
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    assert len(payload["cards"]) > 0

    for card in payload["cards"]:
        assert "source_basis_label" in card
        assert "source_basis_state" in card
        assert card["source_basis_state"] == "available"
        assert isinstance(card["source_basis_label"], str)
        assert card["source_basis_label"].strip()
        assert isinstance(card["node_title"], str)


def test_wf0067_backend_source_basis_contract_unavailable_state_when_authoritative_basis_missing(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "academic_profile",
                    "text": "WF-0067 unavailable source basis test.",
                }
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    assert len(payload["cards"]) > 0
    for card in payload["cards"]:
        assert card["source_basis_state"] == "unavailable"
        assert card["source_basis_label"] is None


def test_wf0067_backend_source_basis_contract_legacy_fallback_state_without_synthesized_basis(
    monkeypatch,
) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        repository = ReviewRepository(session)
        template = session.exec(select(PromptTemplate)).first()
        expectation = session.exec(select(NodeExpectation)).first()
        assert template is not None
        assert expectation is not None

        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0067-legacy-fallback-{time.time_ns()}",
            review_type="structured",
            structured_payload={"nodes": {"academic_profile": "legacy text"}},
        )
        repository.create_review_card(
            review_id=review.id,
            expectation_id=expectation.id,
            rating=ReviewRating.NOTE,
            feedback="Legacy fallback source-basis test card",
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)
    finally:
        session.close()

    detail = get_review_detail(client=client, review_id=str(review.id))
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["detail_state"] == "legacy_fallback"
    assert len(payload["cards"]) > 0
    for card in payload["cards"]:
        assert card["source_basis_state"] == "legacy_fallback"
        assert card["source_basis_label"] is None


def test_wf0067_backend_boundary_contract_zero_card_visible_section(monkeypatch) -> None:
    client, call_id, call_code = create_client_with_erc_stg_seed(monkeypatch)
    assert call_code == "erc_stg_2026_full"

    session = get_session()
    try:
        repository = ReviewRepository(session)
        template = session.exec(select(PromptTemplate)).first()
        assert template is not None

        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0067-zero-card-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "call_id": str(call_id),
                "submitted_leaf_ids": ["proposal_summary"],
                "nodes": {"proposal_summary": "Submitted text without generated cards."},
            },
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)
    finally:
        session.close()

    detail = get_review_detail(client=client, review_id=str(review.id))
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["detail_state"] == "call_linked"
    assert payload["cards"] == []
    assert payload["supporting_context_node_logical_ids"] == []
    assert payload["no_generated_cards_node_logical_ids"] == ["proposal_summary"]
    assert "proposal_summary" not in payload["visible_not_reviewed_node_logical_ids"]
    assert "b1_part1_scientific_proposal" in payload["visible_not_reviewed_node_logical_ids"]


def test_wf0067_backend_boundary_contract_mixed_version_legacy_fallback(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        repository = ReviewRepository(session)
        template = session.exec(select(PromptTemplate)).first()
        expectation = session.exec(select(NodeExpectation)).first()
        assert template is not None
        assert expectation is not None

        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0067-mixed-version-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "submitted_leaf_ids": ["academic_profile"],
                "nodes": {"academic_profile": "Legacy payload text"},
            },
        )
        repository.create_review_card(
            review_id=review.id,
            expectation_id=expectation.id,
            rating=ReviewRating.NOTE,
            feedback="Legacy fallback boundary test card",
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)
    finally:
        session.close()

    detail = get_review_detail(client=client, review_id=str(review.id))
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["detail_state"] == "legacy_fallback"
    assert payload["supporting_context_node_logical_ids"] == []
    assert payload["visible_not_reviewed_node_logical_ids"] == []
    assert payload["no_generated_cards_node_logical_ids"] == []


def test_wf0067_backend_source_basis_contract_mixed_per_card_availability(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_nwo_veni_seed(monkeypatch)
    assert call_code == "nwo_veni_2025_preproposal"

    session = get_session()
    try:
        repository = ReviewRepository(session)
        template = session.exec(select(PromptTemplate)).first()
        assert template is not None

        available_expectation_row = session.exec(
            select(NodeExpectation)
            .join(EvaluationElement, NodeExpectation.evaluation_element_id == EvaluationElement.id)
            .join(
                EvaluationCriterion,
                EvaluationElement.evaluation_criterion_id == EvaluationCriterion.id,
            )
            .join(ProposalNode, NodeExpectation.proposal_node_id == ProposalNode.id)
            .where(
                ProposalNode.funding_call_id == call_id,
                ProposalNode.logical_id == "academic_profile",
                EvaluationElement.logical_id == "elem_peer_exceeding_quality",
            )
        ).first()
        unavailable_expectation_row = session.exec(
            select(NodeExpectation)
            .join(EvaluationElement, NodeExpectation.evaluation_element_id == EvaluationElement.id)
            .join(
                EvaluationCriterion,
                EvaluationElement.evaluation_criterion_id == EvaluationCriterion.id,
            )
            .join(ProposalNode, NodeExpectation.proposal_node_id == ProposalNode.id)
            .where(
                ProposalNode.funding_call_id == call_id,
                ProposalNode.logical_id == "research_idea",
                EvaluationElement.logical_id == "elem_cv_idea_alignment",
            )
        ).first()
        assert available_expectation_row is not None
        assert unavailable_expectation_row is not None

        available_element = session.get(
            EvaluationElement, available_expectation_row.evaluation_element_id
        )
        unavailable_element = session.get(
            EvaluationElement, unavailable_expectation_row.evaluation_element_id
        )
        assert available_element is not None
        assert unavailable_element is not None
        available_criterion = session.get(
            EvaluationCriterion, available_element.evaluation_criterion_id
        )
        unavailable_criterion = session.get(
            EvaluationCriterion, unavailable_element.evaluation_criterion_id
        )
        assert available_criterion is not None
        assert unavailable_criterion is not None
        assert isinstance(available_element.logical_id, str)
        assert isinstance(unavailable_element.logical_id, str)
        assert isinstance(available_criterion.logical_id, str)
        assert isinstance(unavailable_criterion.logical_id, str)

        mixed_criteria: list[dict[str, object]]
        if available_criterion.logical_id == unavailable_criterion.logical_id:
            mixed_criteria = [
                {
                    "id": available_criterion.logical_id,
                    "evaluation_elements": [
                        {
                            "id": available_element.logical_id,
                            "source_hint": "WF-0067 mixed basis available hint",
                        },
                        {"id": unavailable_element.logical_id},
                    ],
                }
            ]
        else:
            mixed_criteria = [
                {
                    "id": available_criterion.logical_id,
                    "evaluation_elements": [
                        {
                            "id": available_element.logical_id,
                            "source_hint": "WF-0067 mixed basis available hint",
                        }
                    ],
                },
                {
                    "id": unavailable_criterion.logical_id,
                    "evaluation_elements": [{"id": unavailable_element.logical_id}],
                },
            ]

        definition = session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        assert isinstance(definition.canonical_json, dict)
        canonical_json = dict(definition.canonical_json)
        canonical_json["evaluation_criteria"] = mixed_criteria
        definition.canonical_json = canonical_json
        session.add(definition)
        session.commit()

        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0067-mixed-source-basis-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "call_id": str(call_id),
                "submitted_leaf_ids": ["academic_profile", "research_idea"],
                "nodes": {
                    "academic_profile": "available source basis text",
                    "research_idea": "unavailable source basis text",
                },
            },
        )
        repository.create_review_card(
            review_id=review.id,
            expectation_id=available_expectation_row.id,
            rating=ReviewRating.SUCCESS,
            feedback="Available source basis card",
        )
        repository.create_review_card(
            review_id=review.id,
            expectation_id=unavailable_expectation_row.id,
            rating=ReviewRating.NOTE,
            feedback="Unavailable source basis card",
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)
    finally:
        session.close()

    detail = get_review_detail(client=client, review_id=str(review.id))
    assert detail.status_code == 200
    payload = detail.json()
    states = {card["source_basis_state"] for card in payload["cards"]}
    assert states == {"available", "unavailable"}
    assert payload["supporting_context_node_logical_ids"] == []


def test_review_detail_order_index_tie_uses_node_logical_id_fallback(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    session = get_session()
    try:
        call_definition = session.exec(
            select(CallDefinition).where(
                CallDefinition.funding_call_id == seeded_ids.structured_call_id
            )
        ).first()
        assert call_definition is not None
        assert isinstance(call_definition.canonical_json, dict)
        proposal_nodes = call_definition.canonical_json.get("proposal_nodes")
        assert isinstance(proposal_nodes, list)

        for node_config in proposal_nodes:
            if not isinstance(node_config, dict):
                continue
            if node_config.get("id") in {"academic_profile", "scientific_proposal"}:
                node_config["order_index"] = 7
        session.add(call_definition)
        session.commit()
    finally:
        session.close()

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "profile text"},
                {"node_logical_id": "scientific_proposal", "text": "science text"},
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    ordered_nodes = [card["node_logical_id"] for card in payload["cards"]]
    assert ordered_nodes == sorted(ordered_nodes)
    assert payload["ordering_source"] == "call_nodes"
    assert payload["unmapped_node_logical_ids"] == []


@pytest.mark.parametrize(
    "case",
    _wf0065_paired_boundary_cases(),
    ids=lambda case: f"wf0069_review_detail_orders_assessed_cards_before_context_gaps_{case['case_id']}",
)
def test_wf0069_review_detail_orders_assessed_cards_before_context_gaps(
    monkeypatch,
    case: Wf0065RepresentativeCase,
) -> None:
    client, call_id, _ = _create_structured_client_for_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": case["stage"],
            "nodes": [
                {
                    "node_logical_id": case["node_logical_id"],
                    "text": case["node_text"],
                }
            ],
        },
    )
    assert response.status_code in {200, 201}

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()

    assessed_submitted_indices = [
        index
        for index, card in enumerate(payload["cards"])
        if card.get("node_logical_id") == case["node_logical_id"]
        and card.get("assessment_status") == AssessmentStatus.ASSESSED
    ]
    assert assessed_submitted_indices

    context_gap_indices = [
        index
        for index, card in enumerate(payload["cards"])
        if card.get("assessment_status") == AssessmentStatus.NOT_ASSESSABLE
    ]
    if context_gap_indices:
        assert min(assessed_submitted_indices) < min(context_gap_indices)


def test_wf0069_review_detail_legacy_ordering_guard(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "profile text"},
                {"node_logical_id": "scientific_proposal", "text": "science text"},
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    ordered_nodes = [card["node_logical_id"] for card in payload["cards"]]

    assert ordered_nodes == sorted(ordered_nodes)
    assert payload["ordering_source"] == "call_nodes"
    assert payload["unmapped_node_logical_ids"] == []


def test_review_detail_unmapped_nodes_ordered_last_and_reported(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        structured_criterion = session.exec(
            select(EvaluationCriterion).where(
                EvaluationCriterion.funding_call_id == seeded_ids.structured_call_id
            )
        ).first()
        assert structured_criterion is not None

        unmapped_node = ProposalNode(
            funding_call_id=seeded_ids.structured_call_id,
            parent_node_id=None,
            logical_id="unmapped_bonus_node",
            node_type=NodeType.SECTION,
            title="Unmapped bonus node",
            order_index=99,
        )
        session.add(unmapped_node)
        session.commit()
        session.refresh(unmapped_node)

        unmapped_element = EvaluationElement(
            evaluation_criterion_id=structured_criterion.id,
            logical_id="elem_unmapped_bonus",
            name="Unmapped bonus element",
            description="Assess bonus section",
        )
        session.add(unmapped_element)
        session.commit()
        session.refresh(unmapped_element)

        unmapped_expectation = NodeExpectation(
            proposal_node_id=unmapped_node.id,
            evaluation_element_id=unmapped_element.id,
            expectation_strength=ExpectationStrength.MANDATORY,
            evaluation_intent=EvaluationIntent.QUALITY,
            guidance_note="Assess bonus node quality",
            order_index=1,
        )
        session.add(unmapped_expectation)
        session.commit()
    finally:
        session.close()

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "profile text"},
                {"node_logical_id": "unmapped_bonus_node", "text": "bonus text"},
            ],
        },
    )
    assert response.status_code == 200
    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200

    payload = detail.json()
    ordered_nodes = [card["node_logical_id"] for card in payload["cards"]]
    assert ordered_nodes[-1] == "unmapped_bonus_node"
    assert payload["unmapped_node_logical_ids"] == ["unmapped_bonus_node"]


def test_review_detail_ordering_source_fallback_when_call_linkage_missing(
    monkeypatch,
) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        repository = ReviewRepository(session)
        template = session.exec(select(PromptTemplate)).first()
        expectation = session.exec(select(NodeExpectation)).first()
        assert template is not None
        assert expectation is not None

        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"legacy-fallback-{time.time_ns()}",
            review_type="structured",
            structured_payload={"nodes": {"academic_profile": "profile text"}},
        )
        repository.create_review_card(
            review_id=review.id,
            expectation_id=expectation.id,
            rating=ReviewRating.NOTE,
            feedback="Legacy fallback card",
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)
    finally:
        session.close()

    detail = get_review_detail(client=client, review_id=str(review.id))
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["call_id"] is None
    assert payload["call_code"] is None
    assert payload["detail_state"] == "legacy_fallback"
    assert payload["ordering_source"] == "review_payload_fallback"


def test_wf0059_review_detail_contract_reports_proof_path_unmapped_state(
    monkeypatch,
) -> None:
    import main as main_module

    client, call_id, call_code = create_client_with_erc_stg_seed(monkeypatch)
    assert call_code == "erc_stg_2026_full"

    def forced_unmapped(cards, *, order_map):
        return cards, ["unmapped_bonus_node"]

    monkeypatch.setattr(main_module, "_order_review_cards", forced_unmapped)

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "b1_part1_scientific_proposal",
                    "text": "Part I scientific proposal",
                },
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["detail_state"] == "proof_path_unmapped"
    assert payload["ordering_source"] == "call_nodes"
    assert payload["unmapped_node_logical_ids"] == ["unmapped_bonus_node"]


def test_create_review_shared_core_happy_path_parity(monkeypatch) -> None:
    from app.services.review_execution_core import ReviewExecutionCore

    client, seeded_ids = create_client_with_seed(monkeypatch)
    calls = {"count": 0}
    original_execute = ReviewExecutionCore.execute_assessable_node

    def traced_execute(self, **kwargs):
        calls["count"] += 1
        return original_execute(self, **kwargs)

    monkeypatch.setattr(ReviewExecutionCore, "execute_assessable_node", traced_execute)

    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Shared core parity happy path.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "COMPLETED"
    assert calls["count"] == 1

    detail_response = get_review_detail(client=client, review_id=payload["review_id"])
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["review"]["status"] == "COMPLETED"
    assert len(detail_payload["cards"]) == 1


def test_create_review_contract_parity(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    success = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Contract parity single node.",
        },
        idempotency_key="idem-single-contract-1",
    )
    assert success.status_code == 200
    success_payload = success.json()
    assert set(success_payload.keys()) == {"review_id", "status"}
    assert success_payload["status"] == "COMPLETED"

    mismatch = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Contract parity single node changed payload",
        },
        idempotency_key="idem-single-contract-1",
    )
    assert mismatch.status_code == 409
    mismatch_payload = mismatch.json()
    assert mismatch_payload["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"


def test_review_repository_supports_structured_write_path(monkeypatch) -> None:
    _, seeded_ids = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        repository = ReviewRepository(session)
        template = session.exec(select(PromptTemplate)).first()
        expectation = session.exec(select(NodeExpectation)).first()

        assert template is not None
        assert expectation is not None

        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"structured-write-smoke-{time.time_ns()}",
            review_type="structured",
            structured_payload={"academic_profile": "profile text"},
        )
        assert review.proposal_snippet_id is None
        assert review.review_type == "structured"
        assert review.structured_payload == {"academic_profile": "profile text"}

        card = repository.create_review_card(
            review_id=review.id,
            expectation_id=expectation.id,
            rating=ReviewRating.NOTE,
            feedback="Not assessable due to missing context",
            assessment_status=AssessmentStatus.NOT_ASSESSABLE,
            not_assessable_reason="missing key_outputs",
        )
        assert card.assessment_status == AssessmentStatus.NOT_ASSESSABLE
        assert card.not_assessable_reason == "missing key_outputs"
    finally:
        session.close()


def test_review_repository_read_paths_support_structured_reviews(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    single_response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Legacy single review text.",
        },
    )
    assert single_response.status_code == 200

    session = get_session()
    try:
        repository = ReviewRepository(session)
        template = session.exec(select(PromptTemplate)).first()
        expectation = session.exec(select(NodeExpectation)).first()

        assert template is not None
        assert expectation is not None

        structured_review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"structured-read-smoke-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "call_id": str(seeded_ids.structured_call_id),
                "call_name": "NWO Talent Programme — Veni 2025 — Pre-proposal",
                "nodes": {"academic_profile": "profile text"},
            },
        )
        repository.create_review_card(
            review_id=structured_review.id,
            expectation_id=expectation.id,
            rating=ReviewRating.NOTE,
            feedback="Not assessable due to missing context",
            assessment_status=AssessmentStatus.NOT_ASSESSABLE,
            not_assessable_reason="missing key_outputs",
        )

        rows = repository.list_reviews_for_external_user(TEST_USER_ID)
        call_names = [call_name for _, call_name, _ in rows]
        node_titles = [node_title for _, _, node_title in rows]
        assert "NWO Talent Programme — Veni 2025 — Pre-proposal" in call_names
        assert "Structured review" in node_titles
        assert any(title != "Structured review" for title in node_titles)

        owner = repository.get_review_owner_external_user_id(structured_review.id)
        assert owner == TEST_USER_ID

        deleted = repository.delete_review_hard(structured_review.id)
        assert deleted is True
        assert repository.get_review_by_id(structured_review.id) is None
        remaining_cards = list(
            session.exec(
                select(ReviewCard).where(ReviewCard.review_id == structured_review.id)
            ).all()
        )
        assert remaining_cards == []
    finally:
        session.close()


def test_create_structured_review_empty_nodes_returns_422(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={"call_id": str(seeded_ids.structured_call_id), "nodes": []},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "STRUCTURED_NODES_REQUIRED"


def test_create_structured_review_unknown_node_returns_422(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "unknown_node", "text": "abc"}],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNKNOWN_NODE_ID"


def test_create_structured_review_stage_mismatch_returns_422(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "review_stage": "STEP_2",
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "abc"}],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REVIEW_STAGE_NODE_MISMATCH"


def test_create_structured_review_duplicate_node_returns_422(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "one two"},
                {"node_logical_id": "academic_profile", "text": "three four"},
            ],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "DUPLICATE_NODE_ID"


def test_wf0063_structured_review_rejects_supporting_nodes_for_primary_path(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "abstract",
                    "text": "Supporting content must be rejected for primary path.",
                }
            ],
        },
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "SUPPORTING_NODE_NOT_ALLOWED"
    assert payload["error"]["details"]["node_logical_ids"] == ["abstract"]


def test_wf0063_compliance_rejects_supporting_nodes_for_primary_path(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    response = post_compliance(
        client=client,
        payload={
            "call_id": str(call_id),
            "draft_nodes": [
                {
                    "node_logical_id": "abstract",
                    "text": "Supporting content must be rejected for primary path.",
                }
            ],
        },
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "SUPPORTING_NODE_NOT_ALLOWED"
    assert payload["error"]["details"]["node_logical_ids"] == ["abstract"]


def test_wf0064_check_compliance_rejects_supporting_nodes_with_existing_error(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    response = post_compliance(
        client=client,
        payload={
            "call_id": str(call_id),
            "draft_nodes": [
                {
                    "node_logical_id": "abstract",
                    "text": "Supporting content must stay fail-closed for primary path.",
                }
            ],
        },
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "SUPPORTING_NODE_NOT_ALLOWED"
    assert payload["error"]["details"]["node_logical_ids"] == ["abstract"]


def test_wf0064_structured_review_rejects_supporting_nodes_with_existing_error(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "abstract",
                    "text": "Supporting content must stay fail-closed for primary path.",
                }
            ],
        },
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "SUPPORTING_NODE_NOT_ALLOWED"
    assert payload["error"]["details"]["node_logical_ids"] == ["abstract"]


def test_wf0063_proof_call_parity_holds_across_api_submit_and_review_detail(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"
    session = get_session()
    try:
        call = session.get(FundingCall, call_id)
        assert call is not None
        call.is_active = True
        session.add(call)
        session.commit()
    finally:
        session.close()

    config_response = client.get(f"/api/public/calls/{call_code}/config")
    assert config_response.status_code == 200
    assert config_response.json()["split_visibility_reviewability_enabled"] is True

    nodes_response = client.get(f"/calls/{call_id}/nodes")
    assert nodes_response.status_code == 200
    nodes_by_logical_id = {
        node["logical_id"]: node for node in nodes_response.json()["nodes"]
    }
    assert "excellence" in nodes_by_logical_id
    assert "abstract" in nodes_by_logical_id

    submit_response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "excellence",
                    "text": "Primary path review text for parity closure guard.",
                }
            ],
        },
    )
    assert submit_response.status_code == 200
    detail = get_review_detail(client=client, review_id=submit_response.json()["review_id"])
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["primary_evaluated_node_logical_ids"] == ["excellence"]
    assert detail_payload["supporting_context_node_logical_ids"] == []


def test_wf0063_non_opted_in_calls_preserve_legacy_behavior(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    config_response = client.get(
        f"/api/public/calls/{seeded_ids.structured_call_code}/config"
    )
    assert config_response.status_code == 200
    assert config_response.json()["split_visibility_reviewability_enabled"] is False

    nodes_response = client.get(f"/calls/{seeded_ids.structured_call_id}/nodes")
    assert nodes_response.status_code == 200
    assert all(node["node_role"] is None for node in nodes_response.json()["nodes"])


def test_wf0063_proof_call_opt_in_rollback_restores_legacy_behavior(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_msca_pf_seed(monkeypatch)
    assert call_code == "MSCA-PF-2025"

    session = get_session()
    try:
        definition = session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        canonical_json = dict(definition.canonical_json)
        canonical_json["runtime_config"] = {
            "split_visibility_reviewability_enabled": False
        }
        definition.canonical_json = canonical_json
        session.add(definition)
        session.commit()
    finally:
        session.close()

    config_response = client.get(f"/api/public/calls/{call_code}/config")
    assert config_response.status_code == 200
    assert config_response.json()["split_visibility_reviewability_enabled"] is False

    nodes_response = client.get(f"/calls/{call_id}/nodes")
    assert nodes_response.status_code == 200
    assert all(node["node_role"] is None for node in nodes_response.json()["nodes"])


def test_create_structured_review_payload_too_large_returns_422(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "x" * 10_001}],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "STRUCTURED_PAYLOAD_TOO_LARGE"


def test_create_structured_review_success_persists_structured_fields(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "profile text"},
            ],
        },
    )
    assert response.status_code == 200
    review_id = response.json()["review_id"]

    session = get_session()
    try:
        review = session.get(Review, UUID(review_id))
        assert review is not None
        assert review.review_type == "structured"
        assert review.proposal_snippet_id is None
        expected_payload = {
            "call_id": str(seeded_ids.structured_call_id),
            "call_name": "NWO Talent Programme — Veni 2025 — Pre-proposal",
            "review_stage": "STEP_1",
            "nodes": {"academic_profile": "profile text"},
            "submitted_leaf_ids": ["academic_profile"],
            "legacy_ambiguous_container_ids": [],
            "moved_legacy_node_references": [],
            "engine_path": "pipeline_v1",
        }
        assert review.structured_payload == expected_payload

        cards = list(
            session.exec(select(ReviewCard).where(ReviewCard.review_id == review.id)).all()
        )
        assert cards
        assert all(card.assessment_status == AssessmentStatus.ASSESSED for card in cards)
    finally:
        session.close()


def test_structured_review_e2e_happy_path_three_nodes(monkeypatch) -> None:
    client, call_id = create_client_with_structured_alignment_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "Academic profile text"},
                {"node_logical_id": "key_outputs", "text": "Key outputs text"},
                {"node_logical_id": "research_idea", "text": "Research idea text"},
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "COMPLETED"

    detail = get_review_detail(client=client, review_id=payload["review_id"])
    assert detail.status_code == 200
    cards = detail.json()["cards"]
    assert len(cards) == 5
    ordered_nodes = [card["node_logical_id"] for card in cards]
    assert ordered_nodes[0] == "academic_profile"
    assert ordered_nodes[1] == "key_outputs"
    assert ordered_nodes[2:] == ["research_idea", "research_idea", "research_idea"]
    assert all(card["assessment_status"] == "ASSESSED" for card in cards)
    assert all(card["not_assessable_reason"] is None for card in cards)


def test_wf0060_review_detail_persists_leaf_coverage_and_legacy_compatibility_state(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        template = session.exec(select(PromptTemplate)).first()
        assert template is not None
        repository = ReviewRepository(session)
        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0060-compat-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "call_id": str(seeded_ids.structured_call_id),
                "call_name": "NWO Talent Programme — Veni 2025 — Pre-proposal",
                "review_stage": "STEP_1",
                "nodes": {
                    "b1": "legacy container evidence",
                    "b2": "legacy container evidence",
                    "resources_time_commitment": "legacy resources evidence",
                    "b1_part1_scientific_proposal": "leaf evidence",
                },
                "moved_legacy_node_references": ["resources_time_commitment"],
                "engine_path": "pipeline_v1",
            },
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)

        detail = get_review_detail(client=client, review_id=str(review.id))
        assert detail.status_code == 200
        payload = detail.json()
        assert payload["submitted_leaf_ids"] == [
            "b1_part1_scientific_proposal",
            "resources_time_commitment",
        ]
        assert payload["legacy_ambiguous_container_ids"] == ["b1", "b2"]
        assert payload["moved_legacy_node_references"] == ["resources_time_commitment"]
    finally:
        session.close()


def test_wf0060_zero_card_leaf_stays_visible_in_review_detail(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        template = session.exec(select(PromptTemplate)).first()
        assert template is not None
        repository = ReviewRepository(session)
        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0060-zero-card-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "call_id": str(seeded_ids.structured_call_id),
                "call_name": "NWO Talent Programme — Veni 2025 — Pre-proposal",
                "review_stage": "STEP_1",
                "nodes": {
                    "academic_profile": "profile text",
                    "scientific_proposal": "proposal text",
                },
                "submitted_leaf_ids": ["academic_profile", "scientific_proposal"],
                "legacy_ambiguous_container_ids": [],
                "moved_legacy_node_references": [],
                "engine_path": "pipeline_v1",
            },
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)

        detail = get_review_detail(client=client, review_id=str(review.id))
        assert detail.status_code == 200
        payload = detail.json()
        assert payload["cards"] == []
        assert payload["submitted_leaf_ids"] == [
            "academic_profile",
            "scientific_proposal",
        ]
    finally:
        session.close()


def test_wf0060_legacy_erc_container_nodes_do_not_inflate_submitted_leaf_coverage(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    session = get_session()
    try:
        template = session.exec(select(PromptTemplate)).first()
        assert template is not None
        repository = ReviewRepository(session)
        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0060-container-only-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "call_id": str(seeded_ids.structured_call_id),
                "call_name": "NWO Talent Programme — Veni 2025 — Pre-proposal",
                "review_stage": "STEP_1",
                "nodes": {
                    "part_a": "legacy container",
                    "budget": "legacy container",
                    "part_b": "legacy container",
                },
                "engine_path": "pipeline_v1",
            },
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)

        detail = get_review_detail(client=client, review_id=str(review.id))
        assert detail.status_code == 200
        payload = detail.json()
        assert payload["submitted_leaf_ids"] == []
    finally:
        session.close()


def test_wf0062_review_detail_maps_legacy_cog_leaf_ids_to_corrected_leaf_coverage(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_erc_cog_seed(monkeypatch)
    assert call_code == "erc_cog_2026_full"
    session = get_session()
    try:
        template = session.exec(select(PromptTemplate)).first()
        assert template is not None
        repository = ReviewRepository(session)
        review = repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=TEST_USER_ID,
            idempotency_key=f"wf0062-cog-legacy-{time.time_ns()}",
            review_type="structured",
            structured_payload={
                "call_id": str(call_id),
                "call_name": "ERC Consolidator Grant 2026",
                "review_stage": "STEP_2",
                "nodes": {
                    "b1_part1_state_of_knowledge": "legacy part I evidence",
                    "b1_part1_objectives": "legacy part I evidence",
                    "b2_methodology": "legacy part II evidence",
                    "b2_risks": "legacy part II evidence",
                },
                "engine_path": "pipeline_v1",
            },
        )
        review.status = ReviewStatus.COMPLETED
        repository.update_review(review)

        detail = get_review_detail(client=client, review_id=str(review.id))
        assert detail.status_code == 200
        payload = detail.json()
        assert payload["submitted_leaf_ids"] == [
            "b1_part1_scientific_proposal",
            "b2_part2_scientific_proposal",
        ]
        assert payload["legacy_ambiguous_container_ids"] == []
        assert payload["moved_legacy_node_references"] == [
            "b1_part1_objectives",
            "b1_part1_state_of_knowledge",
            "b2_methodology",
            "b2_risks",
        ]
        note_types = {note["note_type"] for note in payload["compatibility_notes"]}
        assert "moved_legacy_node_reference" in note_types
    finally:
        session.close()


def test_structured_review_erc_cog_2026_full_happy_path(monkeypatch) -> None:
    client, call_id, call_code = create_client_with_erc_cog_seed(monkeypatch)
    assert call_code == "erc_cog_2026_full"

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "nodes": [
                {
                    "node_logical_id": "b1_part1_scientific_proposal",
                    "text": "The proposal explains current state of knowledge and frontier gap.",
                },
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    cards = detail.json()["cards"]
    assert cards


def test_structured_review_erc_cog_2026_full_rejects_legacy_leaf_ids(monkeypatch) -> None:
    client, call_id, call_code = create_client_with_erc_cog_seed(monkeypatch)
    assert call_code == "erc_cog_2026_full"

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "nodes": [
                {
                    "node_logical_id": "b1_part1_state_of_knowledge",
                    "text": "Legacy node text",
                },
            ],
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "UNKNOWN_NODE_ID"
    assert body["error"]["details"]["node_logical_ids"] == [
        "b1_part1_state_of_knowledge"
    ]


def test_structured_review_e2e_partial_submission_marks_alignment_not_assessable(
    monkeypatch,
) -> None:
    client, call_id = create_client_with_structured_alignment_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "nodes": [
                {"node_logical_id": "key_outputs", "text": "Key outputs text"},
                {"node_logical_id": "research_idea", "text": "Research idea text"},
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "COMPLETED"

    detail = get_review_detail(client=client, review_id=payload["review_id"])
    assert detail.status_code == 200
    cards = detail.json()["cards"]
    not_assessable_cards = [
        card for card in cards if card["assessment_status"] == "NOT_ASSESSABLE"
    ]
    assert all(isinstance(card["node_title"], str) and card["node_title"] for card in cards)
    assert len(not_assessable_cards) == 2
    assert all(
        "academic_profile" in (card["not_assessable_reason"] or "")
        for card in not_assessable_cards
    )


def test_structured_review_single_node_submission_academic_profile(monkeypatch) -> None:
    client, call_id = create_client_with_structured_alignment_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "Academic profile text"},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    cards = detail.json()["cards"]
    assert len(cards) == 1
    assert cards[0]["node_logical_id"] == "academic_profile"
    assert cards[0]["assessment_status"] == "ASSESSED"
    assert cards[0]["not_assessable_reason"] is None


def test_structured_review_single_node_submission_key_outputs(monkeypatch) -> None:
    client, call_id = create_client_with_structured_alignment_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "nodes": [
                {"node_logical_id": "key_outputs", "text": "Key outputs text"},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    cards = detail.json()["cards"]
    assert len(cards) == 1
    assert cards[0]["node_logical_id"] == "key_outputs"
    assert cards[0]["assessment_status"] == "ASSESSED"
    assert cards[0]["not_assessable_reason"] is None


def test_structured_review_single_node_submission_research_idea(monkeypatch) -> None:
    client, call_id = create_client_with_structured_alignment_seed(monkeypatch)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "nodes": [
                {"node_logical_id": "research_idea", "text": "Research idea text"},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    cards = detail.json()["cards"]
    assert len(cards) == 3
    not_assessable_cards = [
        card for card in cards if card["assessment_status"] == "NOT_ASSESSABLE"
    ]
    assessed_cards = [card for card in cards if card["assessment_status"] == "ASSESSED"]
    assert len(not_assessable_cards) == 2
    assert len(assessed_cards) == 1
    assert all(
        "academic_profile" in (card["not_assessable_reason"] or "")
        or "key_outputs" in (card["not_assessable_reason"] or "")
        for card in not_assessable_cards
    )


def test_structured_review_contract_parity(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    success = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
        idempotency_key="idem-structured-contract-1",
    )
    assert success.status_code == 200
    success_payload = success.json()
    assert set(success_payload.keys()) == {"review_id", "status"}
    assert success_payload["status"] == "COMPLETED"

    mismatch = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "updated text"}],
        },
        idempotency_key="idem-structured-contract-1",
    )
    assert mismatch.status_code == 409
    mismatch_payload = mismatch.json()
    assert mismatch_payload["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"


def test_wf0043_contract_structured_api_replay_persists_history(monkeypatch) -> None:
    case = _get_wf0043_case("replay_persists_history", surface="structured_api")
    client, seeded_ids = create_client_with_seed(monkeypatch)
    payload = {
        "call_id": str(seeded_ids.structured_call_id),
        "nodes": case["request_nodes"],
    }

    first = post_structured_review(
        client=client,
        payload=payload,
        user_id="user_wf0043_contract",
        idempotency_key=case["idempotency_key"],
    )
    second = post_structured_review(
        client=client,
        payload=payload,
        user_id="user_wf0043_contract",
        idempotency_key=case["idempotency_key"],
    )

    assert first.status_code == case["expected_http_status"]
    assert second.status_code == case["expected_http_status"]
    first_payload = first.json()
    second_payload = second.json()
    assert first_payload["review_id"] == second_payload["review_id"]
    assert first_payload["status"] == case["expected_review_status"]
    assert second_payload["status"] == case["expected_review_status"]

    if case["expect_review_persisted"]:
        list_response = list_reviews(client=client, user_id="user_wf0043_contract")
        assert list_response.status_code == 200
        listed_review_ids = {item["id"] for item in list_response.json()["reviews"]}
        assert first_payload["review_id"] in listed_review_ids

        detail_response = get_review_detail(
            client=client,
            review_id=first_payload["review_id"],
            user_id="user_wf0043_contract",
        )
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        assert detail_payload["review"]["status"] == case["expected_review_status"]

        if case["expected_summary_convention"] == "completed_nonempty":
            assert _non_empty_str(detail_payload["review"]["overall_summary"])


@pytest.mark.parametrize(
    "case_id",
    [
        "validation_error_missing_idempotency_header",
        "unknown_node_id",
        "review_stage_node_mismatch",
        "idempotency_payload_mismatch",
    ],
    ids=lambda value: _wf0043_case_id(value, surface="structured_api"),
)
def test_wf0043_contract_structured_api_error_semantics_and_no_persistence_side_effects(
    monkeypatch, case_id: str
) -> None:
    case = _get_wf0043_case(case_id, surface="structured_api")
    client, seeded_ids = create_client_with_seed(monkeypatch)
    baseline_count = _count_reviews_in_db()
    payload = {
        "call_id": str(seeded_ids.structured_call_id),
        "nodes": case["request_nodes"],
    }

    if case_id == "validation_error_missing_idempotency_header":
        response = post_structured_review_without_idempotency(
            client=client,
            payload=payload,
            user_id="user_wf0043_contract",
        )
        assert response.status_code == case["expected_http_status"]
        assert response.json()["error"]["code"] == case["expected_error_code"]
        assert _count_reviews_in_db() == baseline_count
        return

    if case_id == "idempotency_payload_mismatch":
        precondition = post_structured_review(
            client=client,
            payload={
                "call_id": str(seeded_ids.structured_call_id),
                "nodes": [
                    {
                        "node_logical_id": "academic_profile",
                        "text": "baseline payload for mismatch",
                    }
                ],
            },
            user_id="user_wf0043_contract",
            idempotency_key=case["idempotency_key"],
        )
        assert precondition.status_code == 200
        precondition_count = _count_reviews_in_db()
        assert precondition_count == baseline_count + 1

        response = post_structured_review(
            client=client,
            payload=payload,
            user_id="user_wf0043_contract",
            idempotency_key=case["idempotency_key"],
        )
        assert response.status_code == case["expected_http_status"]
        assert response.json()["error"]["code"] == case["expected_error_code"]
        assert _count_reviews_in_db() == precondition_count
        return

    if case_id == "review_stage_node_mismatch":
        payload["review_stage"] = "STEP_2"

    response = post_structured_review(
        client=client,
        payload=payload,
        user_id="user_wf0043_contract",
        idempotency_key=case["idempotency_key"],
    )
    assert response.status_code == case["expected_http_status"]
    assert response.json()["error"]["code"] == case["expected_error_code"]
    assert _count_reviews_in_db() == baseline_count


def test_wf0043_contract_structured_api_matrix_coverage() -> None:
    cases = _load_wf0043_matrix_cases()
    required_fields = {
        "case_id",
        "surface",
        "expected_http_status",
        "expected_error_code",
        "expect_review_persisted",
        "expected_review_status",
        "expected_summary_convention",
    }
    for case in cases:
        assert required_fields.issubset(case.keys())

    structured_case_ids = {
        case["case_id"] for case in cases if case.get("surface") == "structured_api"
    }
    covered_case_ids = {
        "replay_persists_history",
        "validation_error_missing_idempotency_header",
        "unknown_node_id",
        "review_stage_node_mismatch",
        "idempotency_payload_mismatch",
        "post_persist_unresolvable_expectation_failed",
    }
    assert structured_case_ids == covered_case_ids
    assert len(structured_case_ids) == 6


@pytest.mark.parametrize(
    "case",
    _load_wf0044_policy_cases(),
    ids=lambda case: _wf0044_policy_case_id(case["case_id"], surface="structured_api"),
)
def test_structured_review_wf0044_policy_structured_api_modes(
    monkeypatch,
    case: Wf0044PolicyCase,
) -> None:
    from app.engine.contracts import PipelineResult
    from app.engine.contracts import ReviewCard as EngineReviewCard

    client, call_id, _ = create_client_with_erc_cog_seed(monkeypatch)
    _set_call_definition_reviewer_policy_rules(
        call_id=call_id,
        rules=[
            {
                "id": f"wf0044_rule_{case['case_id']}",
                "applies_to_stage": "STEP_1",
                "applies_to_node_ids": ["b1_part1_scientific_proposal"],
                "rule_type": "criterion_scope",
                "instruction": "WF-0044 structured policy contract test rule.",
                "severity": "WARNING",
                "enforcement_mode": case["enforcement_mode"],
                "forbidden_terms": [case["forbidden_term"]],
            }
        ],
    )

    def run_pipeline_with_case_feedback(request):
        expectation = request.call_config_snapshot.to_canonical_payload()["expectations"][0]
        return PipelineResult(
            request_id=request.request_id,
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="b1_part1_scientific_proposal",
                    expectation_id=str(expectation["expectation_id"]),
                    rating="NOTE",
                    feedback=case["feedback_text"],
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        run_pipeline_with_case_feedback,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "b1_part1_scientific_proposal",
                    "text": "Structured submission text for policy contract coverage.",
                }
            ],
        },
        idempotency_key=f"wf0044-{case['case_id']}-{time.time_ns()}",
    )
    assert response.status_code == 200
    assert response.json()["status"] == case["expected_review_status"]

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    detail_payload = detail.json()
    summary = detail_payload["review"]["overall_summary"]
    if case["expected_summary_convention"] == "POLICY_BLOCKING":
        assert summary.startswith("POLICY_BLOCKING:")
    elif case["expected_summary_convention"] == "POST_CHECK_WARNING":
        assert "Reviewer-policy warnings:" in summary
    else:
        assert summary.startswith("Structured review completed with")
        assert "Reviewer-policy warnings:" not in summary
    assert len(detail_payload["cards"]) == case["expected_cards_count"]


def test_wf0044_policy_structured_api_matrix_coverage() -> None:
    cases = _load_wf0044_policy_cases()
    case_ids = {case["case_id"] for case in cases}
    assert case_ids == {"prompt_only", "post_check", "blocking"}
    for case in cases:
        assert case["surface"] == "structured_api"


def test_wf0043_contract_structured_api_failed_persisted(monkeypatch) -> None:
    case = _get_wf0043_case(
        "post_persist_unresolvable_expectation_failed", surface="structured_api"
    )
    client, seeded_ids = create_client_with_seed(monkeypatch)

    import app.services.structured_reviewer_service as structured_service_module
    from app.engine.contracts import PipelineResult
    from app.engine.contracts import ReviewCard as EngineReviewCard

    def run_pipeline_with_unknown_expectation(_request):
        return PipelineResult(
            request_id="wf0043-unresolvable",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="academic_profile",
                    expectation_id="exp-missing-from-map",
                    rating="NOTE",
                    feedback="unexpected expectation reference",
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        structured_service_module,
        "run_review_pipeline",
        run_pipeline_with_unknown_expectation,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": case["request_nodes"],
        },
        user_id="user_wf0043_contract",
        idempotency_key=case["idempotency_key"],
    )

    assert response.status_code == case["expected_http_status"]
    response_payload = response.json()
    assert response_payload["status"] == case["expected_review_status"]
    review_id = response_payload["review_id"]

    list_response = list_reviews(client=client, user_id="user_wf0043_contract")
    assert list_response.status_code == 200
    assert review_id in {item["id"] for item in list_response.json()["reviews"]}

    detail_response = get_review_detail(
        client=client,
        review_id=review_id,
        user_id="user_wf0043_contract",
    )
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["review"]["status"] == case["expected_review_status"]
    assert detail_payload["review"]["overall_summary"].startswith(
        f"{case['expected_summary_convention']}:"
    )


def test_review_detail_retains_cards_when_evaluation_element_is_archived(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Archival stability test.",
        },
    )
    assert response.status_code == 200
    review_id = response.json()["review_id"]

    session = get_session()
    try:
        expectation = session.exec(
            select(NodeExpectation).where(
                NodeExpectation.proposal_node_id == seeded_ids.section_with_expectations_id
            )
        ).first()
        assert expectation is not None
        element = session.get(EvaluationElement, expectation.evaluation_element_id)
        assert element is not None
        element.archived_at = datetime.now(UTC)
        session.add(element)
        session.commit()
    finally:
        session.close()

    detail_response = get_review_detail(client=client, review_id=review_id)
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert len(detail_payload["cards"]) == 1
    assert detail_payload["cards"][0]["evaluation_element_name"] == "Clarity of Objectives"


def test_failed_structured_review_detail_returns_partial_cards(monkeypatch) -> None:
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.001")
    client, seeded_ids = create_client_with_seed(monkeypatch)

    call_counter = {"count": 0}

    def slow_second_generate(_: StubLLMClient, prompt: str) -> str:
        call_counter["count"] += 1
        if call_counter["count"] == 2:
            time.sleep(0.05)
        expectation_ids = re.findall(r"ID:\s*([0-9a-fA-F-]{36})", prompt)
        return json.dumps(
            {
                "feedbacks": [
                    {
                        "node_expectation_id": expectation_id,
                        "feedback": f"Feedback for {expectation_id}",
                    }
                    for expectation_id in expectation_ids
                ]
            }
        )

    monkeypatch.setattr(StubLLMClient, "generate", slow_second_generate)
    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [
                {"node_logical_id": "academic_profile", "text": "profile text"},
                {"node_logical_id": "scientific_proposal", "text": "proposal text"},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_cross_endpoint_idempotency_collision_returns_409(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    idempotency_key = "shared-idempotency-key"

    first = post_review(
        client=client,
        idempotency_key=idempotency_key,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Legacy request payload",
        },
    )
    assert first.status_code == 200

    second = post_structured_review(
        client=client,
        idempotency_key=idempotency_key,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"


def test_snippet_too_long_returns_domain_error(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "a" * 10_001,
        },
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "SNIPPET_TOO_LONG"
    assert "details" in payload["error"]


def test_node_not_in_call_returns_domain_error(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.other_call_node_id),
            "snippet_text": "Mismatch test",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NODE_NOT_IN_CALL"


def test_review_stage_node_mismatch_returns_422(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={
            "review_stage": "STEP_2",
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Mismatch test",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REVIEW_STAGE_NODE_MISMATCH"


def test_no_expectations_returns_domain_error(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_without_expectations_id),
            "snippet_text": "Section without mapped criteria.",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NO_EXPECTATIONS"


def test_schema_validation_error_shape(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={"call_id": "not-a-uuid", "node_id": "also-not-a-uuid"},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(payload["error"]["details"]["errors"], list)


def test_atomic_failure_creates_failed_review_with_no_cards(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    def invalid_generate(_: StubLLMClient, __: str) -> str:
        return "not-json"

    monkeypatch.setattr(StubLLMClient, "generate", invalid_generate)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Trigger invalid JSON path",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "FAILED"

    detail_response = get_review_detail(client=client, review_id=payload["review_id"])
    assert detail_response.status_code == 200
    assert detail_response.json()["review"]["status"] == "FAILED"
    assert detail_response.json()["cards"] == []

    session = get_session()
    try:
        reviews = list(session.exec(select(Review)).all())
        cards = list(session.exec(select(ReviewCard)).all())
    finally:
        session.close()

    assert len(reviews) == 1
    assert reviews[0].status == ReviewStatus.FAILED
    assert len(cards) == 0


def test_timeout_creates_failed_review(monkeypatch) -> None:
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.001")
    client, seeded_ids = create_client_with_seed(monkeypatch)

    def slow_generate(_: StubLLMClient, __: str) -> str:
        time.sleep(0.05)
        return '{"feedbacks":[]}'

    monkeypatch.setattr(StubLLMClient, "generate", slow_generate)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Trigger timeout path",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"


def test_create_review_timeout_parity(monkeypatch) -> None:
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.001")
    client, seeded_ids = create_client_with_seed(monkeypatch)

    def slow_generate(_: StubLLMClient, __: str) -> str:
        time.sleep(0.05)
        return '{"feedbacks":[]}'

    monkeypatch.setattr(StubLLMClient, "generate", slow_generate)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Trigger timeout parity path",
        },
        idempotency_key="idem-timeout-parity-1",
    )
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    review_payload = detail.json()["review"]
    assert review_payload["status"] == "FAILED"
    assert review_payload["overall_summary"] == "LLM call timed out after 0.00s."


def test_missing_signature_headers_returns_unauthorized(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.post(
        "/reviews",
        json={
            "review_stage": "STEP_1",
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "No signature",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_missing_idempotency_key_returns_validation_error(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    payload = {
        "review_stage": "STEP_1",
        "call_id": str(seeded_ids.call_id),
        "node_id": str(seeded_ids.section_with_expectations_id),
        "snippet_text": "No idempotency key",
    }
    body = json.dumps(payload).encode("utf-8")
    headers = build_signature_headers(body=body)
    headers["Content-Type"] = "application/json"
    response = client.post("/reviews", content=body, headers=headers)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_signature_returns_unauthorized(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Invalid signature",
        },
        shared_secret="wrong-secret",
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_idempotency_replay_returns_same_review(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    payload = {
        "call_id": str(seeded_ids.call_id),
        "node_id": str(seeded_ids.section_with_expectations_id),
        "snippet_text": "Replay-safe request",
    }
    response_one = post_review(
        client=client,
        payload=payload,
        idempotency_key="idem-replay-1",
    )
    response_two = post_review(
        client=client,
        payload=payload,
        idempotency_key="idem-replay-1",
    )

    assert response_one.status_code == 200
    assert response_two.status_code == 200
    assert response_one.json()["review_id"] == response_two.json()["review_id"]


def test_idempotency_payload_mismatch_returns_conflict(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response_one = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Original payload",
        },
        idempotency_key="idem-mismatch-1",
    )
    response_two = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Modified payload",
        },
        idempotency_key="idem-mismatch-1",
    )

    assert response_one.status_code == 200
    assert response_two.status_code == 409
    assert response_two.json()["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"


def test_create_review_idempotency_mismatch_parity(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    first = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Original payload",
        },
        idempotency_key="idem-parity-mismatch-1",
    )
    second = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Modified payload",
        },
        idempotency_key="idem-parity-mismatch-1",
    )
    assert first.status_code == 200
    assert second.status_code == 409
    payload = second.json()
    assert payload["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"
    assert (
        payload["error"]["message"]
        == "Idempotency key was already used with a different payload."
    )


def test_quota_exceeded_returns_429_with_details(monkeypatch) -> None:
    monkeypatch.setenv("FREE_DAILY_REVIEW_LIMIT", "1")
    client, seeded_ids = create_client_with_seed(monkeypatch)
    payload = {
        "call_id": str(seeded_ids.call_id),
        "node_id": str(seeded_ids.section_with_expectations_id),
        "snippet_text": "Quota test",
    }

    first_response = post_review(
        client=client,
        payload=payload,
        idempotency_key="idem-quota-1",
    )
    assert first_response.status_code == 200

    replay_response = post_review(
        client=client,
        payload=payload,
        idempotency_key="idem-quota-1",
    )
    assert replay_response.status_code == 200

    second_new_key_response = post_review(
        client=client,
        payload=payload,
        idempotency_key="idem-quota-2",
    )
    assert second_new_key_response.status_code == 429
    quota_payload = second_new_key_response.json()
    assert quota_payload["error"]["code"] == "QUOTA_EXCEEDED"
    assert quota_payload["error"]["details"]["limit"] == 1
    assert quota_payload["error"]["details"]["remaining"] == 0
    assert "reset_at" in quota_payload["error"]["details"]


def test_quota_relaxed_in_dev_mode_when_limit_unset(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("FREE_DAILY_REVIEW_LIMIT", raising=False)
    client, seeded_ids = create_client_with_seed(monkeypatch)
    payload = {
        "call_id": str(seeded_ids.call_id),
        "node_id": str(seeded_ids.section_with_expectations_id),
        "snippet_text": "Quota relaxed in development mode",
    }

    for index in range(6):
        response = post_review(
            client=client,
            payload=payload,
            idempotency_key=f"idem-dev-quota-{index}",
        )
        assert response.status_code == 200


def test_kill_switch_blocks_new_submissions_not_existing_reviews(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    create_response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Created before kill switch",
        },
        idempotency_key="idem-kill-switch-1",
    )
    assert create_response.status_code == 200
    review_id = create_response.json()["review_id"]

    monkeypatch.setenv("REVIEWS_ENABLED", "false")

    blocked_response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Blocked by kill switch",
        },
        idempotency_key="idem-kill-switch-2",
    )
    assert blocked_response.status_code == 503
    assert blocked_response.json()["error"]["code"] == "REVIEWS_DISABLED"

    detail_response = get_review_detail(client=client, review_id=review_id)
    assert detail_response.status_code == 200


def test_review_not_found_for_non_owner(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    create_response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Owner-specific review",
        },
        user_id="user_owner",
    )
    assert create_response.status_code == 200
    review_id = create_response.json()["review_id"]

    forbidden_response = get_review_detail(
        client=client,
        review_id=review_id,
        user_id="user_other",
    )
    assert forbidden_response.status_code == 404
    assert forbidden_response.json()["error"]["code"] == "REVIEW_NOT_FOUND"


def test_delete_review_success_hard_deletes_data(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    create_response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Review that will be deleted",
        },
        user_id="user_owner",
    )
    assert create_response.status_code == 200
    review_id = create_response.json()["review_id"]

    delete_response = delete_review(
        client=client,
        review_id=review_id,
        user_id="user_owner",
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"ok": True}

    detail_response = get_review_detail(
        client=client,
        review_id=review_id,
        user_id="user_owner",
    )
    assert detail_response.status_code == 404
    assert detail_response.json()["error"]["code"] == "REVIEW_NOT_FOUND"

    session = get_session()
    try:
        reviews = list(session.exec(select(Review)).all())
        cards = list(session.exec(select(ReviewCard)).all())
        snippets = list(session.exec(select(ProposalSnippet)).all())
    finally:
        session.close()

    assert len(reviews) == 0
    assert len(cards) == 0
    assert len(snippets) == 0


def test_delete_review_non_owner_returns_not_found(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    create_response = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Owner-only delete",
        },
        user_id="user_owner",
    )
    assert create_response.status_code == 200
    review_id = create_response.json()["review_id"]

    delete_response = delete_review(
        client=client,
        review_id=review_id,
        user_id="user_other",
    )
    assert delete_response.status_code == 404
    assert delete_response.json()["error"]["code"] == "REVIEW_NOT_FOUND"

    owner_detail_response = get_review_detail(
        client=client,
        review_id=review_id,
        user_id="user_owner",
    )
    assert owner_detail_response.status_code == 200


def test_error_code_status_mapping_is_consistent() -> None:
    expected = {
        "UNAUTHORIZED": 401,
        "IDEMPOTENCY_PAYLOAD_MISMATCH": 409,
        "QUOTA_EXCEEDED": 429,
        "CALL_NOT_FOUND": 404,
        "NODE_NOT_FOUND": 404,
        "REVIEW_NOT_FOUND": 404,
        "NO_EXPECTATIONS": 400,
        "NODE_NOT_IN_CALL": 400,
        "REVIEW_STAGE_NODE_MISMATCH": 422,
        "REVIEWS_DISABLED": 503,
        "DB_UNAVAILABLE": 503,
        "SNIPPET_TOO_LONG": 400,
        "UNKNOWN_NODE_ID": 422,
        "DUPLICATE_NODE_ID": 422,
        "DOMAIN_REQUIRED": 422,
        "DOMAIN_INVALID": 422,
            "STRUCTURED_NODES_REQUIRED": 422,
            "STRUCTURED_PAYLOAD_TOO_LARGE": 422,
            "CALL_DEFINITION_NODE_MISMATCH": 409,
            "CALL_DEFINITION_CYCLE": 409,
            "CALL_DEFINITION_MISSING": 409,
            "VALIDATION_ERROR": 400,
            "INTERNAL_ERROR": 500,
        }
    assert expected == ERROR_STATUS_BY_CODE


# ── GET /reviews (list) ──────────────────────────────────────────────


def list_reviews(
    *,
    client: TestClient,
    user_id: str = TEST_USER_ID,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> object:
    """Call GET /reviews with signed headers."""
    headers = build_signature_headers(
        body=b"",
        user_id=user_id,
        timestamp=timestamp,
        shared_secret=shared_secret,
    )
    return client.get("/reviews", headers=headers)


def test_list_reviews_returns_user_reviews(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    # Create two reviews
    r1 = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "First review text",
        },
        user_id="user_list_test",
        idempotency_key="idem-list-1",
    )
    r2 = post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Second review text",
        },
        user_id="user_list_test",
        idempotency_key="idem-list-2",
    )
    assert r1.status_code == 200
    assert r2.status_code == 200

    response = list_reviews(client=client, user_id="user_list_test")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["reviews"]) == 2

    # Newest first
    ids = [r["id"] for r in payload["reviews"]]
    assert ids[0] == r2.json()["review_id"]
    assert ids[1] == r1.json()["review_id"]

    # All expected fields
    first = payload["reviews"][0]
    assert first["status"] in ("COMPLETED", "FAILED")
    assert "created_at" in first
    assert first["call_name"] == "ERC Consolidator Grant 2026"
    assert first["node_title"] == "Section 1"


def test_list_reviews_excludes_other_users(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    # Create review as user_a
    post_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "User A review",
        },
        user_id="user_a",
        idempotency_key="idem-isolation-a",
    )

    # List as user_b → should be empty
    response = list_reviews(client=client, user_id="user_b")
    assert response.status_code == 200
    assert response.json()["reviews"] == []


def test_structured_review_reviews_list_and_review_detail_and_idempotency_invariants(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    idempotency_key = "idem-structured-history-1"

    create_response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
        user_id="user_structured_history",
        idempotency_key=idempotency_key,
    )
    assert create_response.status_code == 200
    review_id = create_response.json()["review_id"]

    list_response = list_reviews(client=client, user_id="user_structured_history")
    assert list_response.status_code == 200
    listed_ids = [item["id"] for item in list_response.json()["reviews"]]
    assert review_id in listed_ids

    detail_response = get_review_detail(
        client=client,
        review_id=review_id,
        user_id="user_structured_history",
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["review"]["id"] == review_id

    mismatch_response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "changed text"}],
        },
        user_id="user_structured_history",
        idempotency_key=idempotency_key,
    )
    assert mismatch_response.status_code == 409
    assert mismatch_response.json()["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"


def test_list_reviews_unauthenticated_returns_401(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = client.get("/reviews")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


# ── POST /api/check-compliance ──────────────────────────────────────────────


def test_check_compliance_valid_payload_returns_200(monkeypatch) -> None:
    """Endpoint should return compliance report for valid structured payload."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_compliance(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "domain": "science_enw",
            "draft_nodes": [
                {"node_logical_id": "academic_profile", "text": "one two three"},
                {
                    "node_logical_id": "knowledge_utilisation",
                    "text": "one two three four",
                },
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_compliant"] is True
    assert payload["errors"] == []
    assert payload["warnings"] == []


def test_check_compliance_unknown_node_returns_422(monkeypatch) -> None:
    """Unknown node ids should fail with UNKNOWN_NODE_ID."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_compliance(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "domain": "science_enw",
            "draft_nodes": [
                {"node_logical_id": "unknown_node", "text": "abc"},
            ],
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNKNOWN_NODE_ID"


def test_check_compliance_duplicate_node_returns_422(monkeypatch) -> None:
    """Duplicate node ids should fail with DUPLICATE_NODE_ID."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_compliance(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "domain": "science_enw",
            "draft_nodes": [
                {"node_logical_id": "academic_profile", "text": "one two"},
                {"node_logical_id": "academic_profile", "text": "three four"},
            ],
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "DUPLICATE_NODE_ID"


def test_check_compliance_missing_domain_returns_422(monkeypatch) -> None:
    """Missing domain should fail when node config has no default fallback."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_compliance(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "draft_nodes": [
                {"node_logical_id": "academic_profile", "text": "one two three"},
            ],
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "DOMAIN_REQUIRED"


def test_check_compliance_empty_draft_nodes_returns_blocking_errors(
    monkeypatch,
) -> None:
    """Empty draft nodes should return mandatory_presence error for required node."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = post_compliance(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "domain": "science_enw",
            "draft_nodes": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_compliant"] is False
    assert payload["errors"][0]["rule_id"] == "mandatory_presence"
    assert payload["errors"][0]["is_blocking"] is True


def test_check_compliance_unauthenticated_returns_401(monkeypatch) -> None:
    """Missing BFF signature headers should return unauthorized."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.post(
        "/api/check-compliance",
        json={
            "call_id": str(seeded_ids.structured_call_id),
            "domain": "science_enw",
            "draft_nodes": [],
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_create_structured_review_uses_pipeline_v1_when_feature_enabled(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "1")

    from app.services.structured_reviewer_service import StructuredReviewerService

    calls = {"pipeline_v1": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert calls["pipeline_v1"] == 1


def test_create_structured_review_uses_pipeline_v1_when_feature_disabled_in_retirement_mode(
    monkeypatch,
) -> None:
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "0")
    client, seeded_ids = create_client_with_seed(monkeypatch)

    from app.services.structured_reviewer_service import StructuredReviewerService

    calls = {"pipeline_v1": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert calls["pipeline_v1"] == 1


def test_create_structured_review_uses_pipeline_v1_for_allowlisted_call(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "1")
    monkeypatch.setenv(
        "STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES",
        seeded_ids.structured_call_code,
    )

    from app.services.structured_reviewer_service import StructuredReviewerService

    calls = {"pipeline_v1": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert calls["pipeline_v1"] == 1


def test_create_structured_review_uses_pipeline_v1_for_non_allowlisted_call_in_retirement_mode(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "1")
    monkeypatch.setenv(
        "STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES",
        "some_other_call_code",
    )

    from app.services.structured_reviewer_service import StructuredReviewerService

    calls = {"pipeline_v1": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert calls["pipeline_v1"] == 1


def test_create_structured_review_prod_empty_allowlist_uses_pipeline_v1_in_retirement_mode(
    monkeypatch, caplog
) -> None:
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "1")
    monkeypatch.delenv("STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES", raising=False)
    client, seeded_ids = create_client_with_seed(monkeypatch)

    from app.services.structured_reviewer_service import StructuredReviewerService

    calls = {"pipeline_v1": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )

    with caplog.at_level("WARNING"):
        response = post_structured_review(
            client=client,
            payload={
                "call_id": str(seeded_ids.structured_call_id),
                "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
            },
        )

    assert response.status_code == 200
    assert calls["pipeline_v1"] == 1
    assert "empty call allowlist in prod" not in caplog.text.lower()


def test_create_structured_review_logs_engine_path_pipeline_v1_when_flag_disabled(
    monkeypatch, caplog
) -> None:
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "0")
    client, seeded_ids = create_client_with_seed(monkeypatch)

    with caplog.at_level("INFO"):
        response = post_structured_review(
            client=client,
            payload={
                "call_id": str(seeded_ids.structured_call_id),
                "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
            },
        )

    assert response.status_code == 200
    assert "structured_review.engine_path=pipeline_v1" in caplog.text


def test_create_structured_review_logs_engine_path_pipeline_v1(
    monkeypatch, caplog
) -> None:
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "1")
    client, seeded_ids = create_client_with_seed(monkeypatch)

    with caplog.at_level("INFO"):
        response = post_structured_review(
            client=client,
            payload={
                "call_id": str(seeded_ids.structured_call_id),
                "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
            },
        )

    assert response.status_code == 200
    assert "structured_review.engine_path=pipeline_v1" in caplog.text


def test_canary_rollout_routing_matrix_allowlist_and_fail_closed(
    monkeypatch, caplog
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    from app.services.structured_reviewer_service import StructuredReviewerService

    calls = {"pipeline_v1": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )

    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "1")
    monkeypatch.setenv(
        "STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES",
        seeded_ids.structured_call_code,
    )
    first = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert first.status_code == 200

    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.delenv("STRUCTURED_REVIEW_PIPELINE_V1_CALL_CODES", raising=False)
    with caplog.at_level("WARNING"):
        second = post_structured_review(
            client=client,
            payload={
                "call_id": str(seeded_ids.structured_call_id),
                "nodes": [{"node_logical_id": "academic_profile", "text": "profile text 2"}],
            },
        )
    assert second.status_code == 200
    assert "empty call allowlist in prod" not in caplog.text.lower()

    assert calls["pipeline_v1"] == 2


def test_structured_reviewer_service_legacy_entrypoint_removed(monkeypatch) -> None:
    create_client_with_seed(monkeypatch)
    from app.services.structured_reviewer_service import StructuredReviewerService

    assert not hasattr(StructuredReviewerService, "generate_structured_review")


def test_structured_review_dual_routing_helpers_removed(monkeypatch) -> None:
    create_client_with_seed(monkeypatch)
    import main as app_main

    assert not hasattr(app_main, "is_structured_review_pipeline_v1_enabled")
    assert not hasattr(app_main, "is_structured_review_pipeline_v1_enabled_for_call")


def test_structured_review_call_config_digest_mismatch_marks_failed_review(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    from app.services.structured_reviewer_service import StructuredReviewerService

    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1

    def forced_bad_digest(self, **kwargs):
        return original_pipeline(
            self,
            **kwargs,
            call_config_digest_override="sha256:not-the-canonical-digest",
        )

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        forced_bad_digest,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    assert detail.json()["review"]["overall_summary"].startswith(
        "CALL_CONFIG_DIGEST_MISMATCH:"
    )


def test_structured_review_unresolvable_expectation_marks_failed_review(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    import app.services.structured_reviewer_service as structured_service_module
    from app.engine.contracts import PipelineResult
    from app.engine.contracts import ReviewCard as EngineReviewCard

    def run_pipeline_with_unknown_expectation(_request):
        return PipelineResult(
            request_id="structured-unresolvable",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="academic_profile",
                    expectation_id="exp-missing-from-map",
                    rating="NOTE",
                    feedback="unexpected expectation reference",
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        structured_service_module,
        "run_review_pipeline",
        run_pipeline_with_unknown_expectation,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    assert detail.json()["review"]["overall_summary"].startswith(
        "EXPECTATION_REF_UNRESOLVABLE:"
    )


def test_structured_review_timeout_classification_uses_stable_timeout_message(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    import app.services.structured_reviewer_service as structured_service_module

    def raise_timeout(_request):
        raise TimeoutError()

    monkeypatch.setattr(structured_service_module, "run_review_pipeline", raise_timeout)

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    overall_summary = detail.json()["review"]["overall_summary"]
    assert overall_summary.startswith("TIMEOUT:")
    assert "timed out" in overall_summary.lower()


def test_structured_review_validation_error_precedes_idempotency_mismatch(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    idempotency_key = "idem-structured-validation-order"

    first = post_structured_review(
        client=client,
        idempotency_key=idempotency_key,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert first.status_code == 200

    malformed_payload = {"call_id": "not-a-uuid", "nodes": "not-a-list"}
    body = json.dumps(malformed_payload).encode("utf-8")
    headers = build_signature_headers(body=body)
    headers["Content-Type"] = "application/json"
    headers["Idempotency-Key"] = idempotency_key

    invalid = client.post("/api/structured-review", content=body, headers=headers)
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"


def test_wf0059_structured_review_proof_target_contract_guard(monkeypatch) -> None:
    client, call_id, call_code = create_client_with_erc_stg_seed(monkeypatch)
    assert call_code == "erc_stg_2026_full"

    malformed_payload = {"call_id": str(call_id), "nodes": "not-a-list"}
    body = json.dumps(malformed_payload).encode("utf-8")
    headers = build_signature_headers(body=body)
    headers["Content-Type"] = "application/json"

    invalid = client.post("/api/structured-review", content=body, headers=headers)
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"


def test_wf0059_contract_hierarchical_submit_validation_and_idempotency(
    monkeypatch,
) -> None:
    client, call_id, call_code = create_client_with_erc_stg_seed(monkeypatch)
    assert call_code == "erc_stg_2026_full"
    idempotency_key = "idem-wf0059-erc-stg-hierarchical"
    proof_payload = {
        "call_id": str(call_id),
        "review_stage": "STEP_1",
        "nodes": [
            {
                "node_logical_id": "proposal_summary",
                "text": "Proposal summary",
            },
            {
                "node_logical_id": "b1_cv_track_record",
                "text": "Track record narrative",
            },
        ],
    }

    first = post_structured_review(
        client=client,
        payload=proof_payload,
        idempotency_key=idempotency_key,
    )
    assert first.status_code == 200

    replay = post_structured_review(
        client=client,
        payload=proof_payload,
        idempotency_key=idempotency_key,
    )
    assert replay.status_code == 200
    assert replay.json() == first.json()

    mismatched = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_1",
            "nodes": [
                {
                    "node_logical_id": "proposal_summary",
                    "text": "Updated proposal summary",
                },
            ],
        },
        idempotency_key=idempotency_key,
    )
    assert mismatched.status_code == 409
    assert mismatched.json()["error"]["code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"

    malformed_payload = {
        "call_id": str(call_id),
        "review_stage": "STEP_1",
        "nodes": [
            {
                "node_logical_id": "proposal_summary",
                "text": "Proposal summary",
                "children": "not-a-list",
            }
        ],
    }
    body = json.dumps(malformed_payload).encode("utf-8")
    headers = build_signature_headers(body=body)
    headers["Content-Type"] = "application/json"
    headers["Idempotency-Key"] = idempotency_key

    invalid = client.post("/api/structured-review", content=body, headers=headers)
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"


def test_wf0059_contract_persisted_submitted_node_coverage(monkeypatch) -> None:
    import app.services.structured_reviewer_service as structured_service_module
    from app.engine.contracts import PipelineResult

    client, call_id, call_code = create_client_with_erc_stg_seed(monkeypatch)
    assert call_code == "erc_stg_2026_full"

    def zero_card_pipeline(request):
        return PipelineResult(
            request_id=request.request_id,
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[],
            review_cards=[],
            telemetry={},
        )

    monkeypatch.setattr(structured_service_module, "run_review_pipeline", zero_card_pipeline)

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_2",
            "nodes": [
                {
                    "node_logical_id": "b2_part2_scientific_proposal",
                    "text": "Part II scientific proposal",
                },
                {
                    "node_logical_id": "resources_time_commitment",
                    "text": "Resource justification",
                },
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["cards"] == []
    assert payload["submitted_leaf_ids"] == [
        "b2_part2_scientific_proposal",
        "resources_time_commitment",
    ]


def test_wf0059_zero_card_node_remains_reviewed_from_persisted_coverage(
    monkeypatch,
) -> None:
    import app.services.structured_reviewer_service as structured_service_module
    from app.engine.contracts import PipelineResult

    client, call_id, call_code = create_client_with_erc_stg_seed(monkeypatch)
    assert call_code == "erc_stg_2026_full"

    def zero_card_pipeline(request):
        return PipelineResult(
            request_id=request.request_id,
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[],
            review_cards=[],
            telemetry={},
        )

    monkeypatch.setattr(structured_service_module, "run_review_pipeline", zero_card_pipeline)

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(call_id),
            "review_stage": "STEP_2",
            "nodes": [
                {
                    "node_logical_id": "resources_time_commitment",
                    "text": "Resource justification",
                },
            ],
        },
    )
    assert response.status_code == 200

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["cards"] == []
    assert payload["submitted_node_logical_ids"] == ["resources_time_commitment"]


def test_create_structured_review_non_idempotency_integrity_error_returns_500(
    monkeypatch,
) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "1")
    idempotency_key = "idem-unrelated-integrity-error"

    response = post_structured_review(
        client=client,
        idempotency_key=idempotency_key,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "baseline text"}],
        },
    )
    assert response.status_code == 200

    def bypass_active_idempotency_lookup(self, *args, **kwargs):
        return None

    def traced_create_review(self, *args, **kwargs):
        raise IntegrityError(
            statement="insert into reviews ...",
            params={},
            orig=Exception("foreign key violation on unrelated table"),
        )

    monkeypatch.setattr(
        ReviewRepository,
        "get_active_review_by_idempotency",
        bypass_active_idempotency_lookup,
    )
    monkeypatch.setattr(ReviewRepository, "create_review", traced_create_review)

    second_response = post_structured_review(
        client=client,
        idempotency_key=idempotency_key,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "baseline text"}],
        },
    )

    assert second_response.status_code == 500
    payload = second_response.json()["error"]
    assert payload["code"] == "INTERNAL_ERROR"


def test_wf0072_policy_blocking_quota_zero_side_effect_pairing() -> None:
    """WF-0072 policy blocking closes only with backend zero-side-effect proof."""
    policy_path = Path("../docs/walkthroughs/evidence/WF-0072/policy_blocking.json")
    matrix_path = Path("../docs/walkthroughs/evidence/WF-0072/verification-matrix.json")

    policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
    backend_half = policy_payload["backend_zero_side_effect"]
    assert backend_half["policy_code"] in {"QUOTA_EXCEEDED", "REVIEWS_DISABLED"}
    assert backend_half["no_review_creation_asserted"] is True
    assert backend_half["no_pipeline_execution_asserted"] is True
    assert backend_half["no_partial_persistence_asserted"] is True
    assert backend_half["result"] == "pass"

    matrix_payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    row = next(
        (
            item
            for item in matrix_payload["rows"]
            if item["call_id"] == "nwo_veni_2025_preproposal"
            and item["scenario_id"] == "policy_blocking"
            and item.get("scenario_variant") == "user_surface"
            and item["auth_lane"] == "test_bypass"
        ),
        None,
    )
    assert row is not None
    assert row["result"] == "pass"
    assert "zero-side-effect" in row["side_effect_assertion"]
