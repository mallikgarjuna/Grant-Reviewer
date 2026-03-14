"""backend/tests/test_structured_reviewer_service.py
Structured reviewer service tests for pipeline_v1-only runtime.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from uuid import UUID

import pytest
from sqlmodel import SQLModel, select

from app.db import engine, get_session
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
    ReviewCard,
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import LLMClientError
from app.services.structured_review_synthesis_service import (
    StructuredReviewSynthesisAcceptedResult,
    StructuredReviewSynthesisRejectedResult,
)
from app.services.structured_reviewer_service import StructuredReviewerService
from scripts.ingest_call import ingest_call


def _reset_database() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def _serialize_snapshot_for_assertions(snapshot: dict[str, object]) -> str:
    return json.dumps(snapshot, sort_keys=True, default=str)


def _seed_structured_service_graph() -> UUID:
    session = get_session()
    try:
        agency = FundingAgency(name="NWO", short_name="NWO")
        session.add(agency)
        session.commit()
        session.refresh(agency)

        call = FundingCall(
            funding_agency_id=agency.id,
            name="NWO Veni 2025",
            code="nwo_veni_2025_preproposal",
            call_year=2025,
            is_active=True,
        )
        session.add(call)
        session.commit()
        session.refresh(call)

        nodes_by_logical_id: dict[str, ProposalNode] = {}
        for order_index, logical_id in enumerate(
            ["academic_profile", "key_outputs", "research_idea"],
            start=1,
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

        element_profile = EvaluationElement(
            evaluation_criterion_id=criterion.id,
            logical_id="elem_profile_quality",
            name="Profile quality",
            description="Profile quality",
        )
        element_outputs = EvaluationElement(
            evaluation_criterion_id=criterion.id,
            logical_id="elem_outputs_quality",
            name="Outputs quality",
            description="Outputs quality",
        )
        element_alignment = EvaluationElement(
            evaluation_criterion_id=criterion.id,
            logical_id="elem_cv_idea_alignment",
            name="Alignment",
            description="Alignment",
        )
        element_alignment_plan = EvaluationElement(
            evaluation_criterion_id=criterion.id,
            logical_id="elem_alignment_plan_credibility",
            name="Alignment plan",
            description="Alignment plan",
        )
        element_idea_other = EvaluationElement(
            evaluation_criterion_id=criterion.id,
            logical_id="elem_innovative_ideas_capability",
            name="Innovative ideas",
            description="Innovative ideas",
        )
        session.add(element_profile)
        session.add(element_outputs)
        session.add(element_alignment)
        session.add(element_alignment_plan)
        session.add(element_idea_other)
        session.commit()
        session.refresh(element_profile)
        session.refresh(element_outputs)
        session.refresh(element_alignment)
        session.refresh(element_alignment_plan)
        session.refresh(element_idea_other)

        expectations = [
            NodeExpectation(
                proposal_node_id=node_by_id_obj.id,
                evaluation_element_id=element_id,
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="Test expectation",
                order_index=order_index,
            )
            for node_by_id_obj, element_id, order_index in [
                (nodes_by_logical_id["academic_profile"], element_profile.id, 1),
                (nodes_by_logical_id["key_outputs"], element_outputs.id, 1),
                (nodes_by_logical_id["research_idea"], element_alignment.id, 1),
                (nodes_by_logical_id["research_idea"], element_alignment_plan.id, 2),
                (nodes_by_logical_id["research_idea"], element_idea_other.id, 3),
            ]
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
        session.refresh(template)

        return call.id
    finally:
        session.close()


def _seed_wf0060_erc_graph() -> UUID:
    session = get_session()
    try:
        agency = FundingAgency(name="ERC", short_name="ERC")
        session.add(agency)
        session.commit()
        session.refresh(agency)

        call = FundingCall(
            funding_agency_id=agency.id,
            name="ERC Starting Grant 2026",
            code="erc_stg_2026_full",
            call_year=2026,
            is_active=True,
        )
        session.add(call)
        session.commit()
        session.refresh(call)

        node_b1 = ProposalNode(
            funding_call_id=call.id,
            parent_node_id=None,
            logical_id="b1",
            node_type=NodeType.SECTION,
            title="Part B1",
            order_index=1,
        )
        session.add(node_b1)
        session.commit()
        session.refresh(node_b1)

        node_b1_part1 = ProposalNode(
            funding_call_id=call.id,
            parent_node_id=node_b1.id,
            logical_id="b1_part1_scientific_proposal",
            node_type=NodeType.SUBSECTION,
            title="Part I Scientific Proposal",
            order_index=2,
        )
        session.add(node_b1_part1)
        session.commit()
        session.refresh(node_b1_part1)

        criterion = EvaluationCriterion(
            funding_call_id=call.id,
            logical_id="crit_excellence",
            name="Excellence",
            description="Excellence criterion",
            order_index=1,
        )
        session.add(criterion)
        session.commit()
        session.refresh(criterion)

        element = EvaluationElement(
            evaluation_criterion_id=criterion.id,
            logical_id="elem_project_importance_questions",
            name="Research questions",
            description="Research questions quality",
        )
        session.add(element)
        session.commit()
        session.refresh(element)

        expectation = NodeExpectation(
            proposal_node_id=node_b1_part1.id,
            evaluation_element_id=element.id,
            expectation_strength=ExpectationStrength.MANDATORY,
            evaluation_intent=EvaluationIntent.QUALITY,
            guidance_note="Assess scientific quality",
            order_index=1,
        )
        session.add(expectation)
        session.commit()

        definition = CallDefinition(
            funding_call_id=call.id,
            schema_version="v2",
            checksum="wf0060-erc-checksum",
            canonical_json={"reviewer_policy": []},
            source_path="tests/fixtures/wf0060-erc.yaml",
        )
        session.add(definition)
        session.commit()

        template = PromptTemplate(
            name="WF0060 ERC template",
            template_text="Template",
            is_active=True,
        )
        session.add(template)
        session.commit()

        return call.id
    finally:
        session.close()


class EchoExpectationLLMClient:
    def generate(self, prompt: str) -> str:
        expectation_ids = re.findall(r"ID:\s*([0-9a-fA-F-]{36})", prompt)
        payload = {
            "feedbacks": [
                {
                    "node_expectation_id": expectation_id,
                    "feedback": f"Feedback for {expectation_id}",
                }
                for expectation_id in expectation_ids
            ]
        }
        return json.dumps(payload)

    def get_model_name(self) -> str:
        return "echo-test-model"


class StaticJSONLLMClient:
    """backend/tests/test_structured_reviewer_service.py
    Deterministic JSON-returning client for synthesis seam tests.
    """

    def __init__(self, response_text: str) -> None:
        self.response_text = response_text

    def generate(self, prompt: str) -> str:
        return self.response_text

    def get_model_name(self) -> str:
        return "static-json-test-model"


class TimeoutJSONLLMClient:
    """backend/tests/test_structured_reviewer_service.py
    Deterministic timeout client for synthesis fallback tests.
    """

    def generate(self, prompt: str) -> str:
        raise TimeoutError("WF-0078 synthesis timeout")

    def get_model_name(self) -> str:
        return "timeout-json-test-model"


class ErrorJSONLLMClient:
    """backend/tests/test_structured_reviewer_service.py
    Deterministic client-error client for synthesis fallback tests.
    """

    def generate(self, prompt: str) -> str:
        raise LLMClientError("WF-0078 synthesis client error")

    def get_model_name(self) -> str:
        return "error-json-test-model"


class UnexpectedErrorJSONLLMClient:
    """backend/tests/test_structured_reviewer_service.py
    Deterministic unexpected-error client for synthesis fallback tests.
    """

    def generate(self, prompt: str) -> str:
        raise RuntimeError("WF-0078 unexpected synthesis failure")

    def get_model_name(self) -> str:
        return "unexpected-error-json-test-model"


class RecordingJSONLLMClient:
    """backend/tests/test_structured_reviewer_service.py
    Deterministic JSON client that captures prompts for seam assertions.
    """

    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response_text

    def get_model_name(self) -> str:
        return "recording-json-test-model"


def _build_service(monkeypatch):
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    call_id = _seed_structured_service_graph()
    session = get_session()
    repository = ReviewRepository(session)
    service = StructuredReviewerService(
        repository=repository,
        llm_client=EchoExpectationLLMClient(),
    )
    return service, call_id


def _build_erc_stg_service(monkeypatch):
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    ingest_call(Path("data/calls/canonical/erc/erc_stg_2026_full.yaml"), dry_run=False)
    session = get_session()
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

    repository = ReviewRepository(session)
    service = StructuredReviewerService(
        repository=repository,
        llm_client=EchoExpectationLLMClient(),
    )
    return service, call.id


def _build_msca_pf_service(monkeypatch):
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    ingest_call(Path("data/calls/canonical/msca/msca_pf_2025_full.yaml"), dry_run=False)
    session = get_session()
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

    repository = ReviewRepository(session)
    service = StructuredReviewerService(
        repository=repository,
        llm_client=EchoExpectationLLMClient(),
    )
    return service, call.id


def _build_erc_poc_service(monkeypatch):
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    ingest_call(Path("data/calls/canonical/erc/erc_poc_2026_full.yaml"), dry_run=False)
    session = get_session()
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

    repository = ReviewRepository(session)
    service = StructuredReviewerService(
        repository=repository,
        llm_client=EchoExpectationLLMClient(),
    )
    return service, call.id


def _build_nwo_veni_service(monkeypatch):
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    ingest_call(
        Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"), dry_run=False
    )
    session = get_session()
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

    repository = ReviewRepository(session)
    service = StructuredReviewerService(
        repository=repository,
        llm_client=EchoExpectationLLMClient(),
    )
    return service, call.id


def _build_erc_service(monkeypatch):
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    call_id = _seed_wf0060_erc_graph()
    session = get_session()

    repository = ReviewRepository(session)
    service = StructuredReviewerService(
        repository=repository,
        llm_client=EchoExpectationLLMClient(),
    )
    return service, call_id


def _get_expectation_id_for_node(
    service: StructuredReviewerService,
    *,
    call_id: UUID,
    node_logical_id: str,
) -> str:
    call_nodes = service.repository.get_nodes_for_call(call_id)
    node = next(node for node, _ in call_nodes if node.logical_id == node_logical_id)
    return str(service.repository.get_expectations_for_node(node.id)[0].id)


def _set_call_definition_reviewer_policy(
    service: StructuredReviewerService,
    *,
    call_id: UUID,
    rules: list[dict[str, object]],
) -> None:
    definition = CallDefinition(
        funding_call_id=call_id,
        schema_version="v2",
        checksum="wf0044-test-checksum",
        canonical_json={"reviewer_policy": rules},
        source_path="tests/fixtures/wf0044-policy-test.yaml",
    )
    service.repository.session.add(definition)
    service.repository.session.commit()


def _wf0065_representative_cases() -> list[dict[str, str]]:
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


def _wf0069_stress_case_nwo() -> dict[str, str]:
    return {
        "item_id": "wf0068_nwo_actionability_prioritization_stress",
        "call_code": "nwo_veni_2025_preproposal",
        "stage": "STEP_1",
        "node_logical_id": "key_outputs",
        "node_text": "Representative paired-boundary text for NWO key outputs.",
    }


def _wf0069_actionability_stress_cases() -> list[dict[str, str]]:
    return [
        _wf0069_stress_case_nwo(),
        {
            "item_id": "wf0068_erc_actionability_prioritization_stress",
            "call_code": "erc_stg_2026_full",
            "stage": "STEP_2",
            "node_logical_id": "b1_part1_scientific_proposal",
            "node_text": "Representative paired-boundary text for ERC scientific proposal.",
        },
        {
            "item_id": "wf0068_msca_actionability_prioritization_stress",
            "call_code": "MSCA-PF-2025",
            "stage": "STEP_1",
            "node_logical_id": "excellence",
            "node_text": "Representative paired-boundary text for MSCA excellence.",
        },
    ]


def _wf0069_baseline_cases() -> list[dict[str, str]]:
    return [
        {
            "item_id": "wf0068_nwo_baseline_representative",
            "call_code": "nwo_veni_2025_preproposal",
            "stage": "STEP_1",
            "node_logical_id": "key_outputs",
            "node_text": "Representative proof text for NWO key outputs.",
        },
        {
            "item_id": "wf0068_erc_baseline_representative",
            "call_code": "erc_stg_2026_full",
            "stage": "STEP_1",
            "node_logical_id": "proposal_summary",
            "node_text": "Representative proof text for ERC proposal summary.",
        },
        {
            "item_id": "wf0068_msca_baseline_representative",
            "call_code": "MSCA-PF-2025",
            "stage": "STEP_1",
            "node_logical_id": "excellence",
            "node_text": "Representative proof text for MSCA excellence.",
        },
    ]


def _build_service_for_wf0065_representative_call(
    monkeypatch,
    *,
    call_code: str,
):
    if call_code == "nwo_veni_2025_preproposal":
        return _build_nwo_veni_service(monkeypatch)
    if call_code == "erc_stg_2026_full":
        return _build_erc_stg_service(monkeypatch)
    if call_code == "MSCA-PF-2025":
        return _build_msca_pf_service(monkeypatch)
    raise AssertionError(f"Unsupported wf0065 representative call: {call_code}")


def test_wf0069_wf0068_nwo_actionability_prioritization_stress_proves_narrowest_actionable_seam(
    monkeypatch,
) -> None:
    case = _wf0069_stress_case_nwo()
    service, call_id = _build_nwo_veni_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage=case["stage"],
            call_id=call_id,
            nodes=[(case["node_logical_id"], case["node_text"])],
            external_user_id=f"wf0069-{case['item_id']}",
            idempotency_key=f"wf0069-{case['item_id']}",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert cards

        assessed_cards = [
            card
            for card in cards
            if card.assessment_status == AssessmentStatus.ASSESSED
        ]
        assert assessed_cards
        assert any(
            card.feedback_text.startswith("Revise ")
            and "content_evaluated" not in card.feedback_text
            for card in assessed_cards
        )

        # Missing-context fail-closed behavior is guarded by
        # test_structured_pipeline_v1_not_assessable_cards_for_missing_context.
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_happy_path(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="user-pipeline-v1",
            idempotency_key="pipeline-v1-happy",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].assessment_status == AssessmentStatus.ASSESSED
    finally:
        service.repository.session.close()


@pytest.mark.parametrize(
    "case",
    [
        item
        for item in _wf0069_actionability_stress_cases()
        if item["call_code"] == "erc_stg_2026_full"
    ],
    ids=lambda case: f"wf0069_erc_actionability_{case['item_id']}",
)
def test_wf0069_erc_actionability_stress_cases_emit_actionable_assessed_feedback(
    monkeypatch,
    case: dict[str, str],
) -> None:
    service, call_id = _build_service_for_wf0065_representative_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage=case["stage"],
            call_id=call_id,
            nodes=[(case["node_logical_id"], case["node_text"])],
            external_user_id=f"wf0069-{case['item_id']}",
            idempotency_key=f"wf0069-{case['item_id']}",
        )
        assert review.status == ReviewStatus.COMPLETED
        assessed_cards = [
            card
            for card in cards
            if card.assessment_status == AssessmentStatus.ASSESSED
        ]
        assert assessed_cards
        assert any(
            card.feedback_text.startswith("Revise ")
            and "content_evaluated" not in card.feedback_text
            for card in assessed_cards
        )
    finally:
        service.repository.session.close()


@pytest.mark.parametrize(
    "case",
    [
        item
        for item in _wf0069_actionability_stress_cases()
        if item["call_code"] == "MSCA-PF-2025"
    ],
    ids=lambda case: f"wf0069_msca_actionability_{case['item_id']}",
)
def test_wf0069_msca_actionability_stress_cases_emit_actionable_assessed_feedback(
    monkeypatch,
    case: dict[str, str],
) -> None:
    service, call_id = _build_service_for_wf0065_representative_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage=case["stage"],
            call_id=call_id,
            nodes=[(case["node_logical_id"], case["node_text"])],
            external_user_id=f"wf0069-{case['item_id']}",
            idempotency_key=f"wf0069-{case['item_id']}",
        )
        assert review.status == ReviewStatus.COMPLETED
        assessed_cards = [
            card
            for card in cards
            if card.assessment_status == AssessmentStatus.ASSESSED
        ]
        assert assessed_cards
        assert any(
            card.feedback_text.startswith("Revise ")
            and "content_evaluated" not in card.feedback_text
            for card in assessed_cards
        )
    finally:
        service.repository.session.close()


@pytest.mark.parametrize(
    "case",
    _wf0069_baseline_cases(),
    ids=lambda case: f"wf0069_baseline_non_regression_{case['item_id']}",
)
def test_wf0069_baseline_non_regression_paths_stay_completed_with_cards(
    monkeypatch,
    case: dict[str, str],
) -> None:
    service, call_id = _build_service_for_wf0065_representative_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage=case["stage"],
            call_id=call_id,
            nodes=[(case["node_logical_id"], case["node_text"])],
            external_user_id=f"wf0069-{case['item_id']}",
            idempotency_key=f"wf0069-{case['item_id']}",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert cards
    finally:
        service.repository.session.close()


def test_wf0059_structured_payload_normalization_contract(monkeypatch) -> None:
    service, call_id = _build_erc_stg_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("proposal_summary", "Proposal summary"),
                ("b1_cv_track_record", "Track record narrative"),
            ],
            external_user_id="wf0059-structured-service",
            idempotency_key="wf0059-structured-service",
        )
        assert review.structured_payload is not None
        assert review.structured_payload["submitted_leaf_ids"] == [
            "proposal_summary",
            "b1_cv_track_record",
        ]
        assert list(review.structured_payload["nodes"].keys()) == [
            "proposal_summary",
            "b1_cv_track_record",
        ]
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_not_assessable_cards_for_missing_context(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("research_idea", "Research idea text only")],
            external_user_id="user-pipeline-v1-not-assessable",
            idempotency_key="pipeline-v1-not-assessable",
        )
        assert review.status == ReviewStatus.COMPLETED
        assessed_cards = [
            card
            for card in cards
            if card.assessment_status == AssessmentStatus.ASSESSED
        ]
        not_assessable_cards = [
            card
            for card in cards
            if card.assessment_status == AssessmentStatus.NOT_ASSESSABLE
        ]
        assert len(assessed_cards) == 1
        assert len(not_assessable_cards) == 2
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_contract_error_digest_mismatch(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="user-contract-error",
            idempotency_key="pipeline-v1-digest-mismatch",
            call_config_digest_override="sha256:deadbeef",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert "CALL_CONFIG_DIGEST_MISMATCH" in review.overall_summary
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_contract_error_expectation_unresolvable(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    academic_profile_node = next(
        node for node, _ in call_nodes if node.logical_id == "academic_profile"
    )
    valid_expectation_id = str(
        service.repository.get_expectations_for_node(academic_profile_node.id)[0].id
    )

    class TamperedResult:
        def __init__(self) -> None:
            from app.engine.contracts import (
                DiagnosticFindingV1,
                PipelineResult,
                ReviewCard,
                SubjectRef,
            )

            self.value = PipelineResult(
                request_id="tampered-request",
                pipeline_status="SUCCESS",
                failure_code=None,
                diagnostics=[],
                compatibility_output={},
                findings=[
                    DiagnosticFindingV1(
                        finding_id="tampered",
                        primary_expectation_ref=valid_expectation_id,
                        subject_ref=SubjectRef(node_logical_id="academic_profile"),
                        check_id=f"check.presence.{valid_expectation_id}",
                        finding_kind="MISSING_CONTENT",
                        severity="ERROR",
                        assessment_status="ASSESSED",
                        reason="tampered",
                    )
                ],
                review_cards=[
                    ReviewCard(
                        node_logical_id="academic_profile",
                        expectation_id="exp-missing",
                        rating="WARNING",
                        feedback="tampered",
                    )
                ],
                telemetry={},
            )

    tampered = TamperedResult()
    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        lambda request: tampered.value,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="user-contract-error-unresolvable",
            idempotency_key="pipeline-v1-unresolvable",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert "EXPECTATION_REF_UNRESOLVABLE" in review.overall_summary
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_timeout_error_contract(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch)
    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        lambda request: (_ for _ in ()).throw(TimeoutError()),
    )
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="user-timeout-contract",
            idempotency_key="pipeline-v1-timeout-contract",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert review.overall_summary.startswith("TIMEOUT:")
        assert "timed out" in review.overall_summary.lower()
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_contract_error_unknown_node_logical_id(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("unknown_node", "text")],
            external_user_id="user-contract-error-unknown-node",
            idempotency_key="pipeline-v1-unknown-node",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert "MALFORMED_REVIEW_REQUEST" in review.overall_summary
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_review_request_snapshot_stays_contract_compliant(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch)
    _set_call_definition_reviewer_policy(
        service,
        call_id=call_id,
        rules=[
            {
                "id": "pol_global_prompt",
                "applies_to_stage": "BOTH",
                "applies_to_node_ids": [],
                "rule_type": "criterion_scope",
                "instruction": "Global prompt rule.",
                "severity": "WARNING",
                "enforcement_mode": "PROMPT_ONLY",
                "forbidden_terms": [],
            },
            {
                "id": "pol_step1_academic_prompt",
                "applies_to_stage": "STEP_1",
                "applies_to_node_ids": ["academic_profile"],
                "rule_type": "stage_scope",
                "instruction": "Academic profile rule.",
                "severity": "WARNING",
                "enforcement_mode": "PROMPT_ONLY",
                "forbidden_terms": [],
            },
            {
                "id": "pol_step2_prompt",
                "applies_to_stage": "STEP_2",
                "applies_to_node_ids": [],
                "rule_type": "stage_scope",
                "instruction": "Step2-only rule.",
                "severity": "WARNING",
                "enforcement_mode": "PROMPT_ONLY",
                "forbidden_terms": [],
            },
            {
                "id": "pol_step1_other_node",
                "applies_to_stage": "STEP_1",
                "applies_to_node_ids": ["research_idea"],
                "rule_type": "scope_guardrail",
                "instruction": "Other node rule.",
                "severity": "WARNING",
                "enforcement_mode": "PROMPT_ONLY",
                "forbidden_terms": [],
            },
        ],
    )
    captured_snapshot: dict[str, object] = {}

    def capture_run_review_pipeline(review_request):
        captured_snapshot.update(
            review_request.call_config_snapshot.to_canonical_payload()
        )
        from app.engine.pipeline_v1 import run_review_pipeline as original_pipeline

        return original_pipeline(review_request)

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        capture_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="wf0044-reviewer-policy-scope",
            idempotency_key="wf0044-reviewer-policy-scope",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert cards

        assert captured_snapshot.get("schema_version") == "v1"
        expectations_obj = captured_snapshot.get("expectations")
        assert isinstance(expectations_obj, list)
        assert len(expectations_obj) == 1
        expectation = expectations_obj[0]
        assert isinstance(expectation, dict)
        assert set(expectation.keys()) == {
            "expectation_id",
            "node_logical_id",
            "required",
        }
        assert captured_snapshot.get("reviewer_policy_prompt_by_node") is None
    finally:
        service.repository.session.close()


def test_wf0060_structured_review_rejects_erc_container_submission_ids(
    monkeypatch,
) -> None:
    service, call_id = _build_erc_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("b1", "container text should be rejected")],
            external_user_id="user-wf0060-container-reject",
            idempotency_key="wf0060-container-reject",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert "MALFORMED_REVIEW_REQUEST" in review.overall_summary
        assert "not submittable" in review.overall_summary
    finally:
        service.repository.session.close()


def test_structured_pipeline_v1_reviewer_policy_prompt_only_has_no_side_effects(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch)
    _set_call_definition_reviewer_policy(
        service,
        call_id=call_id,
        rules=[
            {
                "id": "pol_prompt_only_forbidden_term",
                "applies_to_stage": "STEP_1",
                "applies_to_node_ids": ["academic_profile"],
                "rule_type": "criterion_scope",
                "instruction": "Prompt-only rule with forbidden term metadata.",
                "severity": "WARNING",
                "enforcement_mode": "PROMPT_ONLY",
                "forbidden_terms": ["insufficient budget"],
            },
        ],
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "academic_profile",
                    "This text includes insufficient budget wording for test coverage.",
                )
            ],
            external_user_id="wf0044-reviewer-policy-prompt-only",
            idempotency_key="wf0044-reviewer-policy-prompt-only",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert cards
        assert review.overall_summary is not None
        assert "policy" not in review.overall_summary.lower()
        assert all(
            card.assessment_status == AssessmentStatus.ASSESSED for card in cards
        )
    finally:
        service.repository.session.close()


def test_wf0061_contract_structured_service_uses_real_msca_pf_2025_snapshot(
    monkeypatch,
) -> None:
    """WF-0061 tracer: structured service uses ingested real MSCA-PF-2025 snapshot."""
    service, call_id = _build_msca_pf_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("excellence", "Tracer bullet text for MSCA-PF-2025 excellence.")],
            external_user_id="wf0061-msca-service",
            idempotency_key="wf0061-msca-service",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) >= 1

        definition = service.repository.session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        assert (
            definition.source_path == "data/calls/canonical/msca/msca_pf_2025_full.yaml"
        )
    finally:
        service.repository.session.close()


def test_wf0061_contract_msca_backend_compatibility_stays_single_seam(
    monkeypatch,
) -> None:
    """WF-0061 no-fix regression: MSCA works without widening backend compatibility seams."""
    msca_service, msca_call_id = _build_msca_pf_service(monkeypatch)
    try:
        review, cards = msca_service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=msca_call_id,
            nodes=[("excellence", "MSCA compatibility seam regression text.")],
            external_user_id="wf0061-msca-single-seam",
            idempotency_key="wf0061-msca-single-seam",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) >= 1
    finally:
        msca_service.repository.session.close()

    erc_service, erc_call_id = _build_erc_stg_service(monkeypatch)
    try:
        review, cards = erc_service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=erc_call_id,
            nodes=[("b1", "container text should be rejected")],
            external_user_id="wf0061-erc-guardrail",
            idempotency_key="wf0061-erc-guardrail",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert "MALFORMED_REVIEW_REQUEST" in review.overall_summary
    finally:
        erc_service.repository.session.close()


def test_wf0061_contract_multisurface_proof_candidate_stops_for_rescope(
    monkeypatch,
) -> None:
    """WF-0061 blocker boundary: unknown cross-surface node IDs fail closed."""
    service, call_id = _build_msca_pf_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("excellence", "Valid MSCA structured node text."),
                (
                    "frontend_universal_submit_surface",
                    "Cross-surface payload should trigger blocker handling.",
                ),
            ],
            external_user_id="wf0061-multisurface-blocker",
            idempotency_key="wf0061-multisurface-blocker",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert "MALFORMED_REVIEW_REQUEST" in review.overall_summary
        assert "Unknown node_logical_id" in review.overall_summary
    finally:
        service.repository.session.close()


def test_wf0073_contract_structured_service_resolves_erc_poc_2026_snapshot(
    monkeypatch,
) -> None:
    """WF-0073: structured service resolves real ERC PoC snapshot."""
    service, call_id = _build_erc_poc_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "WF-0073 service tracer for PoC idea and innovation.",
                )
            ],
            external_user_id="wf0073-erc-poc-service",
            idempotency_key="wf0073-erc-poc-service",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) >= 1

        definition = service.repository.session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        assert (
            definition.source_path == "data/calls/canonical/erc/erc_poc_2026_full.yaml"
        )
    finally:
        service.repository.session.close()


def test_wf0073_contract_structured_service_keeps_erc_poc_2026_single_step_activation(
    monkeypatch,
) -> None:
    """WF-0073: PoC service path should not require staged ERC semantics."""
    service, call_id = _build_erc_poc_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_pi_strategic_leadership",
                    "Single-step activation proof for PI strategic leadership/project management.",
                )
            ],
            external_user_id="wf0073-erc-poc-single-step",
            idempotency_key="wf0073-erc-poc-single-step",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) >= 1
        assert review.overall_summary is not None
        assert "MALFORMED_REVIEW_REQUEST" not in review.overall_summary

        definition = service.repository.session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        assert definition.canonical_json["funding_call"]["stage"] == "single-step"
    finally:
        service.repository.session.close()


def test_wf0076_contract_erc_poc_runtime_snapshot_carries_live_canonical_subordinate_prompts(
    monkeypatch,
) -> None:
    """WF-0076: ERC PoC runtime snapshot carries expectation-level subordinate prompts."""
    service, call_id = _build_erc_poc_service(monkeypatch)
    captured_snapshot: dict[str, object] = {}

    def capture_run_review_pipeline(review_request):
        captured_snapshot.update(
            review_request.call_config_snapshot.to_canonical_payload()
        )
        from app.engine.pipeline_v1 import run_review_pipeline as original_pipeline

        return original_pipeline(review_request)

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        capture_run_review_pipeline,
    )

    try:
        definition = service.repository.session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        canonical_json = json.loads(json.dumps(definition.canonical_json))
        evaluation_elements = canonical_json["evaluation_criteria"][0][
            "evaluation_elements"
        ]
        assert evaluation_elements[0]["id"] == "elem_breakthrough_innovation_potential"
        evaluation_elements[0]["subordinate_prompts"][0]["id"] = (
            "prompt_wf0076_source_mutation"
        )
        evaluation_elements[0]["subordinate_prompts"][0]["prompt"] = (
            "WF-0076 source perturbation: runtime must follow active call definition."
        )
        definition.canonical_json = canonical_json
        service.repository.session.add(definition)
        service.repository.session.commit()

        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "Proof text for ERC PoC innovation and breakthrough potential.",
                )
            ],
            external_user_id="wf0074-erc-poc-runtime-boundary",
            idempotency_key="wf0074-erc-poc-runtime-boundary",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) >= 1
        assert any(
            card.feedback_text.startswith(
                "Revise poc_idea_innovation to strengthen breakthrough innovation potential by "
            )
            for card in cards
        )
        assert all(
            "subordinate_prompt_ids=" not in card.feedback_text for card in cards
        )
        assert all(
            "prompt_wf0076_source_mutation" not in card.feedback_text for card in cards
        )

        assert set(captured_snapshot) == {"schema_version", "expectations"}
        assert captured_snapshot["schema_version"] == "v1"
        assert isinstance(captured_snapshot["expectations"], list)
        assert captured_snapshot["expectations"]

        innovation_expectations = [
            expectation
            for expectation in captured_snapshot["expectations"]
            if isinstance(expectation, dict)
            and expectation.get("node_logical_id") == "poc_idea_innovation"
        ]
        assert innovation_expectations

        expectations_with_subordinate_prompts = [
            expectation
            for expectation in innovation_expectations
            if isinstance(expectation.get("subordinate_prompts"), list)
            and expectation["subordinate_prompts"]
        ]
        assert expectations_with_subordinate_prompts

        serialized_snapshot = _serialize_snapshot_for_assertions(
            {"expectations": expectations_with_subordinate_prompts}
        )
        assert "subordinate_prompts" in serialized_snapshot
        assert "prompt_wf0076_source_mutation" in serialized_snapshot
        assert (
            "WF-0076 source perturbation: runtime must follow active call definition."
            in serialized_snapshot
        )
    finally:
        service.repository.session.close()


def test_wf0076_contract_erc_poc_feedback_mapping_orders_prompts_and_falls_back_for_missing_ids(
    monkeypatch,
) -> None:
    """WF-0076: ERC PoC cards render subordinate prompt text in stable ID order with fallback."""
    from app.engine.contracts import (
        DiagnosticFindingV1,
        PipelineResult,
        SubjectRef,
    )
    from app.engine.contracts import (
        ReviewCard as EngineReviewCard,
    )

    service, call_id = _build_erc_poc_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_wf0076_missing,"
        "prompt_expected_outcomes_distinctiveness,prompt_high_risk_high_gain"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0076-feedback-mapping-order",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0076-feedback-mapping-order",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "WF-0076 deterministic subordinate prompt presentation mapping.",
                )
            ],
            external_user_id="wf0076-feedback-mapping-order",
            idempotency_key="wf0076-feedback-mapping-order",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1

        rendered_feedback = cards[0].feedback_text
        assert "subordinate_prompt_ids=" not in rendered_feedback
        assert (
            "Is the idea high risk and with a potential high gain?" in rendered_feedback
        )
        assert (
            "Are the expected outcomes innovative or distinctive compared to existing solutions?"
            in rendered_feedback
        )
        assert (
            "Unresolved subordinate prompt ID: prompt_wf0076_missing."
            in rendered_feedback
        )
        assert rendered_feedback.index(
            "Is the idea high risk and with a potential high gain?"
        ) < (
            rendered_feedback.index(
                "Are the expected outcomes innovative or distinctive compared to existing solutions?"
            )
        )
    finally:
        service.repository.session.close()


def test_wf0076_contract_non_erc_poc_calls_keep_machine_feedback_unchanged(
    monkeypatch,
) -> None:
    """WF-0076 regression guard: non-ERC-PoC calls keep pre-existing feedback behavior."""
    from app.engine.contracts import (
        DiagnosticFindingV1,
        PipelineResult,
        SubjectRef,
    )
    from app.engine.contracts import (
        ReviewCard as EngineReviewCard,
    )

    service, call_id = _build_nwo_veni_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    key_outputs_node = next(
        node for node, _ in call_nodes if node.logical_id == "key_outputs"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(key_outputs_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids=prompt_non_erc_passthrough"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0076-non-erc-passthrough",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0076-non-erc-passthrough",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="key_outputs"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="key_outputs",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("key_outputs", "WF-0076 non-ERC passthrough regression guard.")],
            external_user_id="wf0076-non-erc-passthrough",
            idempotency_key="wf0076-non-erc-passthrough",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text == machine_feedback
    finally:
        service.repository.session.close()


def test_wf0077_contract_erc_poc_actionable_guidance(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0077: ERC PoC assessed cards should become deterministic revision guidance.
    """
    from app.engine.contracts import (
        DiagnosticFindingV1,
        PipelineResult,
        SubjectRef,
    )
    from app.engine.contracts import (
        ReviewCard as EngineReviewCard,
    )

    service, call_id = _build_erc_poc_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0077-erc-poc-guidance",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0077-erc-poc-guidance",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "WF-0077 deterministic researcher guidance tracer bullet.",
                )
            ],
            external_user_id="wf0077-erc-poc-guidance",
            idempotency_key="wf0077-erc-poc-guidance",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1

        rendered_feedback = cards[0].feedback_text
        assert rendered_feedback.startswith("Revise poc_idea_innovation to strengthen ")
        assert "breakthrough innovation potential" in rendered_feedback
        assert (
            "how the idea is high risk and has potential high gain" in rendered_feedback
        )
        assert (
            "how the expected outcomes are innovative or distinctive compared to existing solutions"
            in rendered_feedback
        )
        assert (
            "Address the following evaluation element prompts:" not in rendered_feedback
        )
        assert (
            "Is the idea high risk and with a potential high gain?"
            not in rendered_feedback
        )
    finally:
        service.repository.session.close()


def test_wf0077_contract_erc_poc_reason_passthrough(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0077: service-local rewrite must not mutate the machine reason string.
    """
    from app.engine.contracts import (
        DiagnosticFindingV1,
        PipelineResult,
        SubjectRef,
    )
    from app.engine.contracts import (
        ReviewCard as EngineReviewCard,
    )

    service, call_id = _build_erc_poc_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )
    original_machine_feedback = machine_feedback

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0077-erc-poc-reason-passthrough",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0077-erc-poc-reason-passthrough",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "WF-0077 machine-reason passthrough guard.",
                )
            ],
            external_user_id="wf0077-erc-poc-reason-passthrough",
            idempotency_key="wf0077-erc-poc-reason-passthrough",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert machine_feedback == original_machine_feedback
        assert cards[0].feedback_text != machine_feedback
        assert not hasattr(cards[0], "reason")
    finally:
        service.repository.session.close()


def test_wf0077_contract_non_targeted_passthrough(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0077: non-targeted calls keep the pre-existing deterministic behavior.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_nwo_veni_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    key_outputs_node = next(
        node for node, _ in call_nodes if node.logical_id == "key_outputs"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(key_outputs_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids=prompt_non_erc_passthrough"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0077-non-targeted-passthrough",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0077-non-targeted-passthrough",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="key_outputs"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="key_outputs",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("key_outputs", "WF-0077 non-targeted passthrough guard.")],
            external_user_id="wf0077-non-targeted-passthrough",
            idempotency_key="wf0077-non-targeted-passthrough",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text == machine_feedback
    finally:
        service.repository.session.close()


def test_wf0077_contract_erc_poc_fallback_missing_source(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0077: missing source prompts must fail closed to WF-0076-style rendering.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )
    definition = service.repository.session.exec(
        select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
    ).first()
    assert definition is not None
    canonical_json = json.loads(json.dumps(definition.canonical_json))
    evaluation_elements = canonical_json["evaluation_criteria"][0][
        "evaluation_elements"
    ]
    evaluation_elements[0].pop("subordinate_prompts")
    definition.canonical_json = canonical_json
    service.repository.session.add(definition)
    service.repository.session.commit()

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0077-fallback-missing-source",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0077-fallback-missing-source",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("poc_idea_innovation", "WF-0077 missing source fallback.")],
            external_user_id="wf0077-fallback-missing-source",
            idempotency_key="wf0077-fallback-missing-source",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith(
            "Address the following evaluation element prompts:"
        )
        assert (
            "Unresolved subordinate prompt ID: prompt_high_risk_high_gain."
            in cards[0].feedback_text
        )
    finally:
        service.repository.session.close()


def test_wf0077_contract_erc_poc_fallback_unresolved_prompt(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0077: unresolved prompt IDs must fail closed to WF-0076-style rendering.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_wf0077_unresolved"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0077-fallback-unresolved",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0077-fallback-unresolved",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("poc_idea_innovation", "WF-0077 unresolved prompt fallback.")],
            external_user_id="wf0077-fallback-unresolved",
            idempotency_key="wf0077-fallback-unresolved",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith(
            "Address the following evaluation element prompts:"
        )
        assert (
            "Is the idea high risk and with a potential high gain?"
            in cards[0].feedback_text
        )
        assert (
            "Unresolved subordinate prompt ID: prompt_wf0077_unresolved."
            in cards[0].feedback_text
        )
    finally:
        service.repository.session.close()


def test_wf0077_contract_erc_poc_fallback_duplicate_source(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0077: duplicate prompt IDs in source must fail closed to WF-0076-style rendering.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )
    definition = service.repository.session.exec(
        select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
    ).first()
    assert definition is not None
    canonical_json = json.loads(json.dumps(definition.canonical_json))
    evaluation_elements = canonical_json["evaluation_criteria"][0][
        "evaluation_elements"
    ]
    evaluation_elements[0]["subordinate_prompts"] = [
        {
            "id": "prompt_high_risk_high_gain",
            "prompt": "Is the idea high risk and with a potential high gain?",
        },
        {
            "id": "prompt_high_risk_high_gain",
            "prompt": "Duplicate source surface should disable deterministic guidance.",
        },
    ]
    definition.canonical_json = canonical_json
    service.repository.session.add(definition)
    service.repository.session.commit()

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids=prompt_high_risk_high_gain"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0077-fallback-duplicate-source",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0077-fallback-duplicate-source",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("poc_idea_innovation", "WF-0077 duplicate source fallback.")],
            external_user_id="wf0077-fallback-duplicate-source",
            idempotency_key="wf0077-fallback-duplicate-source",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith(
            "Address the following evaluation element prompts:"
        )
        assert (
            "Unresolved subordinate prompt ID: prompt_high_risk_high_gain."
            in cards[0].feedback_text
        )
        assert not cards[0].feedback_text.startswith("Revise ")
    finally:
        service.repository.session.close()


def test_wf0078_contract_erc_poc_tracer_bullet_synthesis_acceptance(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: accepted additive synthesis can exist at the service/helper seam.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    synthesis_payload = json.dumps(
        {
            "expectation_id": "placeholder-filled-by-helper-validation",
            "node_logical_id": "poc_idea_innovation",
            "evaluation_element_logical_id": "elem_breakthrough_innovation_potential",
            "synthesized_feedback": "Synthesis: clarify why the proof-of-concept is high risk, high gain, and distinct from current alternatives.",
            "evidence_quotes": [
                "high-risk catalyst platform",
                "distinct translational route",
            ],
        }
    )
    service, call_id = _build_erc_poc_service(monkeypatch)
    service._llm_client = StaticJSONLLMClient(synthesis_payload)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-erc-poc-tracer-bullet",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-erc-poc-tracer-bullet",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )

    service._llm_client = StaticJSONLLMClient(
        synthesis_payload.replace(
            '"placeholder-filled-by-helper-validation"',
            f'"{expectation_id}"',
        )
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-erc-poc-tracer-bullet",
            idempotency_key="wf0078-erc-poc-tracer-bullet",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert len(service.last_synthesis_results) == 1
        accepted_result = service.last_synthesis_results[0]
        assert isinstance(accepted_result, StructuredReviewSynthesisAcceptedResult)
        assert accepted_result.expectation_id == expectation_id
        assert accepted_result.node_logical_id == "poc_idea_innovation"
        assert (
            accepted_result.synthesized_feedback
            == "Synthesis: clarify why the proof-of-concept is high risk, high gain, and distinct from current alternatives."
        )
    finally:
        service.repository.session.close()


def test_wf0078_contract_erc_poc_feedback_text_remains_deterministic(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: accepted synthesis must not replace persisted deterministic guidance.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    call_nodes = service.repository.get_nodes_for_call(call_id)
    innovation_node = next(
        node for node, _ in call_nodes if node.logical_id == "poc_idea_innovation"
    )
    expectation_id = str(
        service.repository.get_expectations_for_node(innovation_node.id)[0].id
    )

    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-erc-poc-feedback-surface",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-erc-poc-feedback-surface",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient(
        json.dumps(
            {
                "expectation_id": expectation_id,
                "node_logical_id": "poc_idea_innovation",
                "evaluation_element_logical_id": "elem_breakthrough_innovation_potential",
                "synthesized_feedback": "Synthesis: this should remain additive only.",
                "evidence_quotes": [
                    "high-risk catalyst platform",
                    "distinct translational route",
                ],
            }
        )
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-erc-poc-feedback-surface",
            idempotency_key="wf0078-erc-poc-feedback-surface",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith(
            "Revise poc_idea_innovation to strengthen breakthrough innovation potential by "
        )
        assert cards[0].feedback_text != "Synthesis: this should remain additive only."
        assert len(service.last_synthesis_results) == 1
        assert isinstance(
            service.last_synthesis_results[0],
            StructuredReviewSynthesisAcceptedResult,
        )
    finally:
        service.repository.session.close()


def test_wf0079_contract_erc_poc_persists_accepted_companion_text(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0079: accepted ERC PoC additive guidance persists without mutating deterministic feedback.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    deterministic_feedback = (
        "Revise poc_idea_innovation to strengthen breakthrough innovation potential by "
        "showing why the proof-of-concept is high risk, high gain, and distinct from current alternatives."
    )
    synthesized_companion_text = (
        "Synthesis: clarify why the proof-of-concept is high risk, high gain, and distinct from current alternatives."
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0079-erc-poc-persisted-companion",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0079-erc-poc-persisted-companion",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=deterministic_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=deterministic_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient(
        json.dumps(
            {
                "expectation_id": expectation_id,
                "node_logical_id": "poc_idea_innovation",
                "evaluation_element_logical_id": "elem_breakthrough_innovation_potential",
                "synthesized_feedback": synthesized_companion_text,
                "evidence_quotes": [
                    "high-risk catalyst platform",
                    "distinct translational route",
                ],
            }
        )
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0079-erc-poc-persisted-companion",
            idempotency_key="wf0079-erc-poc-persisted-companion",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text == deterministic_feedback
        assert cards[0].synthesized_companion_text == synthesized_companion_text

        persisted_cards = list(
            service.repository.session.exec(
                select(ReviewCard).where(ReviewCard.review_id == review.id)
            ).all()
        )
        assert len(persisted_cards) == 1
        assert persisted_cards[0].feedback_text == deterministic_feedback
        assert (
            persisted_cards[0].synthesized_companion_text
            == synthesized_companion_text
        )
    finally:
        service.repository.session.close()


def test_wf0079_contract_non_targeted_calls_do_not_persist_companion_text(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0079: non-targeted calls must not persist additive companion text.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    class UnexpectedSynthesisCallClient:
        def generate(self, prompt: str) -> str:
            raise AssertionError(f"Synthesis should not run for non-targeted calls: {prompt}")

        def get_model_name(self) -> str:
            return "unexpected-synthesis-call"

    service, call_id = _build_nwo_veni_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="academic_profile",
    )
    deterministic_feedback = "Deterministic NWO feedback remains unchanged."

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0079-non-targeted-no-companion",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0079-non-targeted-no-companion",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="academic_profile"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=deterministic_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="academic_profile",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=deterministic_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = UnexpectedSynthesisCallClient()

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Concise academic profile text.")],
            external_user_id="wf0079-non-targeted-no-companion",
            idempotency_key="wf0079-non-targeted-no-companion",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text == deterministic_feedback
        assert cards[0].synthesized_companion_text is None
        assert service.last_synthesis_results == ()

        persisted_cards = list(
            service.repository.session.exec(
                select(ReviewCard).where(ReviewCard.review_id == review.id)
            ).all()
        )
        assert len(persisted_cards) == 1
        assert persisted_cards[0].feedback_text == deterministic_feedback
        assert persisted_cards[0].synthesized_companion_text is None
    finally:
        service.repository.session.close()


def test_wf0078_contract_erc_poc_card_timeout_falls_back(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: one timed-out synthesis attempt falls back to deterministic guidance.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-timeout-fallback",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-timeout-fallback",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = TimeoutJSONLLMClient()

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-timeout-fallback",
            idempotency_key="wf0078-timeout-fallback",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith("Revise poc_idea_innovation")
        assert len(service.last_synthesis_results) == 1
        rejected_result = service.last_synthesis_results[0]
        assert isinstance(rejected_result, StructuredReviewSynthesisRejectedResult)
        assert rejected_result.rejection_code == "timeout"
    finally:
        service.repository.session.close()


def test_wf0078_contract_erc_poc_card_client_error_falls_back(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: client errors degrade one card back to deterministic guidance.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-client-error-fallback",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-client-error-fallback",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = ErrorJSONLLMClient()

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-client-error-fallback",
            idempotency_key="wf0078-client-error-fallback",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith("Revise poc_idea_innovation")
        assert len(service.last_synthesis_results) == 1
        rejected_result = service.last_synthesis_results[0]
        assert isinstance(rejected_result, StructuredReviewSynthesisRejectedResult)
        assert rejected_result.rejection_code == "client_error"
    finally:
        service.repository.session.close()


def test_wf0078_contract_erc_poc_card_malformed_output_falls_back(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: malformed synthesis output is dropped without affecting the card.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-malformed-fallback",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-malformed-fallback",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient("{not-json")

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-malformed-fallback",
            idempotency_key="wf0078-malformed-fallback",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith("Revise poc_idea_innovation")
        assert len(service.last_synthesis_results) == 1
        rejected_result = service.last_synthesis_results[0]
        assert isinstance(rejected_result, StructuredReviewSynthesisRejectedResult)
        assert rejected_result.rejection_code == "malformed_output"
    finally:
        service.repository.session.close()


def test_wf0078_contract_erc_poc_card_ungrounded_output_falls_back(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: ungrounded additive synthesis is rejected and the card stays deterministic.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-ungrounded-fallback",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-ungrounded-fallback",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient(
        json.dumps(
            {
                "expectation_id": expectation_id,
                "node_logical_id": "poc_idea_innovation",
                "evaluation_element_logical_id": "elem_breakthrough_innovation_potential",
                "synthesized_feedback": "Synthesis: this is not grounded in the submitted node.",
                "evidence_quotes": ["quote missing from the submitted excerpt"],
            }
        )
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-ungrounded-fallback",
            idempotency_key="wf0078-ungrounded-fallback",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith("Revise poc_idea_innovation")
        assert len(service.last_synthesis_results) == 1
        rejected_result = service.last_synthesis_results[0]
        assert isinstance(rejected_result, StructuredReviewSynthesisRejectedResult)
        assert rejected_result.rejection_code == "ungrounded_output"
    finally:
        service.repository.session.close()


def test_wf0078_contract_all_cards_rejected_review_still_completes(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: even when every additive attempt rejects, the deterministic review completes.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    innovation_expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    leadership_expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_pi_strategic_leadership",
    )
    innovation_machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )
    leadership_machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_pi_clear_vision_strategic_decisions_risk_contingency"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-all-cards-rejected",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-all-cards-rejected-innovation",
                    primary_expectation_ref=innovation_expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=innovation_machine_feedback,
                ),
                DiagnosticFindingV1(
                    finding_id="wf0078-all-cards-rejected-leadership",
                    primary_expectation_ref=leadership_expectation_id,
                    subject_ref=SubjectRef(
                        node_logical_id="poc_pi_strategic_leadership"
                    ),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=leadership_machine_feedback,
                ),
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=innovation_expectation_id,
                    rating="NOTE",
                    feedback=innovation_machine_feedback,
                ),
                EngineReviewCard(
                    node_logical_id="poc_pi_strategic_leadership",
                    expectation_id=leadership_expectation_id,
                    rating="NOTE",
                    feedback=leadership_machine_feedback,
                ),
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient("{not-json")

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                ),
                (
                    "poc_pi_strategic_leadership",
                    "The principal investigator led translational pilots and cross-functional commercialization planning.",
                ),
            ],
            external_user_id="wf0078-all-cards-rejected",
            idempotency_key="wf0078-all-cards-rejected",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 2
        assert all(card.feedback_text for card in cards)
        assert cards[0].feedback_text != innovation_machine_feedback
        assert cards[1].feedback_text != leadership_machine_feedback
        assert len(service.last_synthesis_results) == 2
        assert all(
            isinstance(result, StructuredReviewSynthesisRejectedResult)
            for result in service.last_synthesis_results
        )
    finally:
        service.repository.session.close()


def test_wf0078_contract_emitted_payload_excludes_raw_reason(monkeypatch) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: emitted synthesis request excludes audit-only raw machine reason.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )
    raw_reason = "audit_only_raw_reason_should_not_enter_synthesis_payload"

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-payload-excludes-raw-reason",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-payload-excludes-raw-reason",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=raw_reason,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient("{not-json")

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-payload-excludes-raw-reason",
            idempotency_key="wf0078-payload-excludes-raw-reason",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert len(service.last_synthesis_requests) == 1
        serialized_request = _serialize_snapshot_for_assertions(
            service.last_synthesis_requests[0].__dict__
        )
        assert raw_reason not in serialized_request
        assert machine_feedback not in serialized_request
        assert "Revise poc_idea_innovation" in serialized_request
    finally:
        service.repository.session.close()


def test_wf0078_contract_emitted_payload_uses_same_card_context_only(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: each emitted request is restricted to same-card context.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    innovation_expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    leadership_expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_pi_strategic_leadership",
    )
    innovation_machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )
    leadership_machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_pi_clear_vision_strategic_decisions_risk_contingency"
    )
    innovation_text = (
        "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation."
    )
    leadership_text = (
        "The principal investigator led translational pilots and cross-functional commercialization planning."
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-payload-same-card-only",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-payload-same-card-innovation",
                    primary_expectation_ref=innovation_expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason="audit-only-innovation-reason",
                ),
                DiagnosticFindingV1(
                    finding_id="wf0078-payload-same-card-leadership",
                    primary_expectation_ref=leadership_expectation_id,
                    subject_ref=SubjectRef(
                        node_logical_id="poc_pi_strategic_leadership"
                    ),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason="audit-only-leadership-reason",
                ),
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=innovation_expectation_id,
                    rating="NOTE",
                    feedback=innovation_machine_feedback,
                ),
                EngineReviewCard(
                    node_logical_id="poc_pi_strategic_leadership",
                    expectation_id=leadership_expectation_id,
                    rating="NOTE",
                    feedback=leadership_machine_feedback,
                ),
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient("{not-json")

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("poc_idea_innovation", innovation_text),
                ("poc_pi_strategic_leadership", leadership_text),
            ],
            external_user_id="wf0078-payload-same-card-only",
            idempotency_key="wf0078-payload-same-card-only",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 2
        assert len(service.last_synthesis_requests) == 2
        innovation_request = service.last_synthesis_requests[0]
        leadership_request = service.last_synthesis_requests[1]
        assert innovation_request.node_logical_id == "poc_idea_innovation"
        assert innovation_request.submitted_excerpt == innovation_text[:280]
        assert leadership_text not in innovation_request.submitted_excerpt
        assert leadership_request.node_logical_id == "poc_pi_strategic_leadership"
        assert leadership_request.submitted_excerpt == leadership_text[:280]
        assert innovation_text not in leadership_request.submitted_excerpt
    finally:
        service.repository.session.close()


def test_wf0078_contract_emitted_payload_includes_node_title_context(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: emitted synthesis request carries same-card node title context.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-node-title-context",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-node-title-context",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    recording_client = RecordingJSONLLMClient("{not-json")
    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = recording_client

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-node-title-context",
            idempotency_key="wf0078-node-title-context",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert len(service.last_synthesis_requests) == 1
        assert service.last_synthesis_requests[0].node_title == "PoC idea and innovation"
        assert len(recording_client.prompts) == 1
        assert "node_title: PoC idea and innovation" in recording_client.prompts[0]
    finally:
        service.repository.session.close()


def test_wf0078_contract_emitted_payload_excludes_full_call_and_legacy_artifacts(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: emitted synthesis request excludes full call-definition and legacy surfaces.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-payload-excludes-full-call",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-payload-excludes-full-call",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason="audit-only-full-call-exclusion",
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient("{not-json")

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-payload-excludes-full-call",
            idempotency_key="wf0078-payload-excludes-full-call",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        serialized_request = _serialize_snapshot_for_assertions(
            service.last_synthesis_requests[0].__dict__
        )
        assert "evaluation_criteria" not in serialized_request
        assert "schema_version" not in serialized_request
        assert "single-step" not in serialized_request
        assert "structured_payload" not in serialized_request
        assert "legacy" not in serialized_request
    finally:
        service.repository.session.close()


def test_wf0078_contract_non_guidance_cards_do_not_attempt_synthesis(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: ERC PoC cards without approved WF-0077 guidance must not attempt synthesis.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    raw_machine_feedback = "content_evaluated"

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-non-guidance-no-attempt",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-non-guidance-no-attempt",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=raw_machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=raw_machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient(
        json.dumps(
            {
                "expectation_id": expectation_id,
                "node_logical_id": "poc_idea_innovation",
                "evaluation_element_logical_id": "elem_breakthrough_innovation_potential",
                "synthesized_feedback": "This should never be attempted.",
                "evidence_quotes": ["high-risk catalyst platform"],
            }
        )
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-non-guidance-no-attempt",
            idempotency_key="wf0078-non-guidance-no-attempt",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text == "content_evaluated"
        assert service.last_synthesis_requests == ()
        assert service.last_synthesis_results == ()
    finally:
        service.repository.session.close()


def test_wf0078_contract_erc_poc_card_unexpected_error_falls_back(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: unexpected synthesis errors still fail closed with explicit classification.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_erc_poc_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="poc_idea_innovation",
    )
    machine_feedback = (
        "content_evaluated;subordinate_prompt_ids="
        "prompt_high_risk_high_gain,prompt_expected_outcomes_distinctiveness"
    )

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-unexpected-error-fallback",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-unexpected-error-fallback",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="poc_idea_innovation"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason=machine_feedback,
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="poc_idea_innovation",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = UnexpectedErrorJSONLLMClient()

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                (
                    "poc_idea_innovation",
                    "This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
                )
            ],
            external_user_id="wf0078-unexpected-error-fallback",
            idempotency_key="wf0078-unexpected-error-fallback",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert cards[0].feedback_text.startswith("Revise poc_idea_innovation")
        assert len(service.last_synthesis_results) == 1
        rejected_result = service.last_synthesis_results[0]
        assert isinstance(rejected_result, StructuredReviewSynthesisRejectedResult)
        assert rejected_result.rejection_code == "unexpected_error"
    finally:
        service.repository.session.close()


def test_wf0078_contract_non_targeted_calls_do_not_attempt_synthesis(
    monkeypatch,
) -> None:
    """backend/tests/test_structured_reviewer_service.py
    WF-0078: non-ERC-PoC calls never emit synthesis requests or results.
    """
    from app.engine.contracts import DiagnosticFindingV1, PipelineResult, SubjectRef
    from app.engine.contracts import ReviewCard as EngineReviewCard

    service, call_id = _build_nwo_veni_service(monkeypatch)
    expectation_id = _get_expectation_id_for_node(
        service,
        call_id=call_id,
        node_logical_id="key_outputs",
    )
    machine_feedback = "content_evaluated"

    def fake_run_review_pipeline(_request):
        return PipelineResult(
            request_id="wf0078-non-targeted-no-attempt",
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={},
            findings=[
                DiagnosticFindingV1(
                    finding_id="wf0078-non-targeted-no-attempt",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id="key_outputs"),
                    check_id="check.presence",
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="ASSESSED",
                    reason="audit-only-non-targeted-reason",
                )
            ],
            review_cards=[
                EngineReviewCard(
                    node_logical_id="key_outputs",
                    expectation_id=expectation_id,
                    rating="NOTE",
                    feedback=machine_feedback,
                )
            ],
            telemetry={},
        )

    monkeypatch.setattr(
        "app.services.structured_reviewer_service.run_review_pipeline",
        fake_run_review_pipeline,
    )
    service._llm_client = StaticJSONLLMClient(
        json.dumps(
            {
                "expectation_id": expectation_id,
                "node_logical_id": "key_outputs",
                "evaluation_element_logical_id": "elem_outputs_quality",
                "synthesized_feedback": "This should never be used.",
                "evidence_quotes": ["Representative proof text for NWO key outputs."],
            }
        )
    )

    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("key_outputs", "Representative proof text for NWO key outputs.")],
            external_user_id="wf0078-non-targeted-no-attempt",
            idempotency_key="wf0078-non-targeted-no-attempt",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 1
        assert service.last_synthesis_requests == ()
        assert service.last_synthesis_results == ()
    finally:
        service.repository.session.close()


def test_wf0065_nwo_structured_service_tracer_uses_real_canonical_call(
    monkeypatch,
) -> None:
    """WF-0065 tracer: structured service uses real NWO canonical snapshot."""
    service, call_id = _build_nwo_veni_service(monkeypatch)
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("key_outputs", "Tracer bullet text for NWO key outputs.")],
            external_user_id="wf0065-nwo-service",
            idempotency_key="wf0065-nwo-service",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) >= 1

        definition = service.repository.session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        assert definition is not None
        assert (
            definition.source_path
            == "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"
        )
    finally:
        service.repository.session.close()


@pytest.mark.parametrize(
    "case",
    _wf0065_representative_cases(),
    ids=lambda case: f"wf0065_structured_service_representative_{case['case_id']}",
)
def test_wf0065_structured_service_representative_success_matrix_persists_review(
    monkeypatch,
    case: dict[str, str],
) -> None:
    """WF-0065 matrix: structured service parity for locked representative calls."""
    service, call_id = _build_service_for_wf0065_representative_call(
        monkeypatch,
        call_code=case["call_code"],
    )
    try:
        review, cards = service.generate_structured_review_pipeline_v1(
            review_stage=case["stage"],
            call_id=call_id,
            nodes=[(case["node_logical_id"], case["node_text"])],
            external_user_id=f"wf0065-representative-service-{case['case_id']}",
            idempotency_key=f"wf0065-representative-service-{case['case_id']}",
        )
        assert review.status in {ReviewStatus.PENDING, ReviewStatus.COMPLETED}
        assert review.review_type == "structured"
        assert review.structured_payload is not None
        assert review.structured_payload["call_id"] == str(call_id)
        assert review.structured_payload["engine_path"] == "pipeline_v1"
        assert len(cards) >= 1

        persisted_cards = list(
            service.repository.session.exec(
                select(ReviewCard).where(ReviewCard.review_id == review.id)
            ).all()
        )
        assert len(persisted_cards) == len(cards)
    finally:
        service.repository.session.close()
