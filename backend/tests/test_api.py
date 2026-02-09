"""FastAPI endpoint tests for Task 7.0."""

from dataclasses import dataclass
import hashlib
import hmac
import json
import time
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
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    seeded_ids = seed_api_data()
    return TestClient(app), seeded_ids


def build_signature_headers(
    *,
    body: bytes,
    user_id: str = TEST_USER_ID,
    timestamp: int | None = None,
    shared_secret: str = TEST_BFF_SHARED_SECRET,
) -> dict[str, str]:
    """Build signed headers expected by protected API routes."""
    signed_timestamp = int(time.time()) if timestamp is None else timestamp
    payload = (
        f"{user_id}.{signed_timestamp}.{hashlib.sha256(body).hexdigest()}"
    )
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
    assert detail_payload["cards"][0]["rating"] == "NOTE"


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


def test_missing_signature_headers_returns_unauthorized(monkeypatch) -> None:
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.post(
        "/reviews",
        json={
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
        "REVIEWS_DISABLED": 503,
        "SNIPPET_TOO_LONG": 400,
        "VALIDATION_ERROR": 400,
        "INTERNAL_ERROR": 500,
    }
    assert ERROR_STATUS_BY_CODE == expected
