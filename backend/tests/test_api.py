"""FastAPI endpoint tests for Task 7.0."""

from dataclasses import dataclass
from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, select

from app.db import engine, get_session
from app.models.domain import (
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
    Review,
    ReviewCard,
    ReviewStatus,
)
from app.services.llm_client import StubLLMClient
from main import ERROR_STATUS_BY_CODE, app


@dataclass(frozen=True)
class SeededIDs:
    """IDs for deterministic test assertions."""

    call_id: UUID
    section_with_expectations_id: UUID
    section_without_expectations_id: UUID
    other_call_id: UUID
    other_call_node_id: UUID


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
        session.commit()
        session.refresh(call)
        session.refresh(other_call)

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
        )
    finally:
        session.close()


def create_client_with_seed(monkeypatch) -> tuple[TestClient, SeededIDs]:
    """Create test client with reset DB and stub LLM mode."""
    monkeypatch.setenv("LLM_MODE", "stub")
    reset_database()
    seeded_ids = seed_api_data()
    return TestClient(app), seeded_ids


def test_healthcheck(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_list_calls_returns_active_calls(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = client.get("/calls")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["calls"]) == 2
    assert {call["code"] for call in payload["calls"]} == {"ERC-2026-COG", "ERC-2026-STG"}


def test_list_nodes_includes_has_expectations(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.get(f"/calls/{seeded_ids.call_id}/nodes")
    assert response.status_code == 200
    payload = response.json()
    by_id = {UUID(node["id"]): node for node in payload["nodes"]}
    assert by_id[seeded_ids.section_with_expectations_id]["has_expectations"] is True
    assert by_id[seeded_ids.section_without_expectations_id]["has_expectations"] is False


def test_create_review_success_with_stub_mode(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.post(
        "/reviews",
        json={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Test snippet for section one.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "COMPLETED"

    detail_response = client.get(f"/reviews/{payload['review_id']}")
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["review"]["status"] == "COMPLETED"
    assert len(detail_payload["cards"]) == 1
    assert detail_payload["cards"][0]["rating"] == "NOTE"


def test_snippet_too_long_returns_domain_error(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.post(
        "/reviews",
        json={
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
    response = client.post(
        "/reviews",
        json={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.other_call_node_id),
            "snippet_text": "Mismatch test",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NODE_NOT_IN_CALL"


def test_no_expectations_returns_domain_error(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.post(
        "/reviews",
        json={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_without_expectations_id),
            "snippet_text": "Section without mapped criteria.",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NO_EXPECTATIONS"


def test_schema_validation_error_shape(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)
    response = client.post(
        "/reviews",
        json={"call_id": "not-a-uuid", "node_id": "also-not-a-uuid"},
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
    response = client.post(
        "/reviews",
        json={
            "call_id": str(seeded_ids.call_id),
            "node_id": str(seeded_ids.section_with_expectations_id),
            "snippet_text": "Trigger invalid JSON path",
        },
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "LLM_INVALID_RESPONSE"

    session = get_session()
    try:
        reviews = list(session.exec(select(Review)).all())
        cards = list(session.exec(select(ReviewCard)).all())
    finally:
        session.close()

    assert len(reviews) == 1
    assert reviews[0].status == ReviewStatus.FAILED
    assert len(cards) == 0


def test_error_code_status_mapping_is_consistent() -> None:
    expected = {
        "CALL_NOT_FOUND": 404,
        "NODE_NOT_FOUND": 404,
        "REVIEW_NOT_FOUND": 404,
        "NO_EXPECTATIONS": 400,
        "NODE_NOT_IN_CALL": 400,
        "SNIPPET_TOO_LONG": 400,
        "VALIDATION_ERROR": 400,
        "LLM_FAILED": 502,
        "LLM_INVALID_RESPONSE": 502,
        "INTERNAL_ERROR": 500,
    }
    assert ERROR_STATUS_BY_CODE == expected
