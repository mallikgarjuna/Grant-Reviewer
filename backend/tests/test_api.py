"""FastAPI endpoint tests for Task 7.0."""

import hashlib
import hmac
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

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
            source_path="data/calls/nwo/nwo_veni_2025_preproposal.yaml",
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


def test_get_call_config_returns_structured_mode(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)

    response = client.get(
        f"/api/public/calls/{seeded_ids.structured_call_code}/config"
    )

    assert response.status_code == 200
    assert response.json() == {
        "call_logical_id": "nwo_veni_2025_preproposal",
        "config_version": "1",
        "ui_mode": "structured_nodes",
        "expected_nodes": [
            "academic_profile",
            "knowledge_utilisation",
            "scientific_proposal",
        ],
    }
    assert set(response.json().keys()) == {
        "call_logical_id",
        "config_version",
        "ui_mode",
        "expected_nodes",
    }


def test_get_call_config_legacy_omits_expected_nodes(monkeypatch) -> None:
    client, _ = create_client_with_seed(monkeypatch)

    response = client.get("/api/public/calls/ERC-2026-COG/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["call_logical_id"] == "ERC-2026-COG"
    assert payload["config_version"] == "1"
    assert payload["ui_mode"] == "legacy_single_snippet"
    assert "expected_nodes" not in payload
    assert set(payload.keys()) == {"call_logical_id", "config_version", "ui_mode"}


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
        }
        if _is_pipeline_v1_enabled():
            expected_payload["engine_path"] = "pipeline_v1"
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
    if _is_pipeline_v1_enabled():
        assert response.json()["status"] == "COMPLETED"
        return
    assert response.json()["status"] == "FAILED"

    detail = get_review_detail(client=client, review_id=response.json()["review_id"])
    assert detail.status_code == 200
    cards = detail.json()["cards"]
    assert cards
    assert cards[0]["assessment_status"] == "ASSESSED"
    assert cards[0]["not_assessable_reason"] is None


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

    calls = {"pipeline_v1": 0, "legacy": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1
    original_legacy = StructuredReviewerService.generate_structured_review

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    def traced_legacy(self, **kwargs):
        calls["legacy"] += 1
        return original_legacy(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )
    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review",
        traced_legacy,
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
    assert calls["legacy"] == 0


def test_create_structured_review_uses_legacy_when_feature_disabled(monkeypatch) -> None:
    monkeypatch.setenv("STRUCTURED_REVIEW_PIPELINE_V1_ENABLED", "0")
    client, seeded_ids = create_client_with_seed(monkeypatch)

    from app.services.structured_reviewer_service import StructuredReviewerService

    calls = {"pipeline_v1": 0, "legacy": 0}
    original_pipeline = StructuredReviewerService.generate_structured_review_pipeline_v1
    original_legacy = StructuredReviewerService.generate_structured_review

    def traced_pipeline_v1(self, **kwargs):
        calls["pipeline_v1"] += 1
        return original_pipeline(self, **kwargs)

    def traced_legacy(self, **kwargs):
        calls["legacy"] += 1
        return original_legacy(self, **kwargs)

    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review_pipeline_v1",
        traced_pipeline_v1,
    )
    monkeypatch.setattr(
        StructuredReviewerService,
        "generate_structured_review",
        traced_legacy,
    )

    response = post_structured_review(
        client=client,
        payload={
            "call_id": str(seeded_ids.structured_call_id),
            "nodes": [{"node_logical_id": "academic_profile", "text": "profile text"}],
        },
    )
    assert response.status_code == 200
    assert calls["legacy"] == 1
    assert calls["pipeline_v1"] == 0


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
