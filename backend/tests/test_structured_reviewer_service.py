"""Unit tests for structured reviewer service."""

from __future__ import annotations

import json
import re
import time

from sqlmodel import SQLModel

from app.db import engine, get_session
from app.models.domain import (
    AssessmentStatus,
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
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import LLMClientError
from app.services.review_execution_core import (
    ExecutionTelemetryPayload,
    NodeExecutionResult,
    ReviewExecutionCore,
)
from app.schemas.llm_response import ExpectationFeedback
from app.services.structured_reviewer_service import StructuredReviewerService


def _reset_database() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def _seed_structured_service_graph():
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
                (
                    nodes_by_logical_id["academic_profile"],
                    element_profile.id,
                    1,
                ),
                (nodes_by_logical_id["key_outputs"], element_outputs.id, 1),
                (
                    nodes_by_logical_id["research_idea"],
                    element_alignment.id,
                    1,
                ),
                (
                    nodes_by_logical_id["research_idea"],
                    element_alignment_plan.id,
                    2,
                ),
                (
                    nodes_by_logical_id["research_idea"],
                    element_idea_other.id,
                    3,
                ),
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


class EchoExpectationLLMClient:
    """Returns one feedback per expectation ID found in prompt."""

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


class TimeoutOnSecondCallLLMClient(EchoExpectationLLMClient):
    """Sleeps during second call to force timeout."""

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str) -> str:
        self.calls += 1
        if self.calls == 2:
            time.sleep(0.1)
        return super().generate(prompt)


class InvalidJsonLLMClient(EchoExpectationLLMClient):
    def generate(self, prompt: str) -> str:
        del prompt
        return "not-json"


class FailingLLMClient(EchoExpectationLLMClient):
    def generate(self, prompt: str) -> str:
        del prompt
        raise LLMClientError("synthetic llm failure")


def _build_service(monkeypatch, llm_client, execution_core=None):
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    call_id = _seed_structured_service_graph()
    session = get_session()
    repository = ReviewRepository(session)
    service = StructuredReviewerService(
        repository=repository,
        llm_client=llm_client,
        execution_core=execution_core,
    )
    return service, call_id


class SpyExecutionCore:
    def __init__(self) -> None:
        self.calls = 0
        self.expectation_batches: list[list[str]] = []

    def execute_assessable_node(
        self,
        *,
        node,
        snippet_text: str,
        expectations,
        reviewer_policy_rules,
        cross_node_context=None,
    ) -> NodeExecutionResult:
        del node, reviewer_policy_rules, cross_node_context
        self.calls += 1
        self.expectation_batches.append([str(expectation.id) for expectation in expectations])
        return NodeExecutionResult(
            prompt=f"spy prompt: {snippet_text}",
            raw_response='{"feedbacks": []}',
            feedbacks=[
                ExpectationFeedback(
                    node_expectation_id=str(expectation.id),
                    feedback=f"Spy feedback for {expectation.id}",
                )
                for expectation in expectations
            ],
            warning_violations=[],
        )


class RecordingTelemetryHooks:
    def __init__(self) -> None:
        self.starts: list[ExecutionTelemetryPayload] = []
        self.completes: list[ExecutionTelemetryPayload] = []
        self.failures: list[ExecutionTelemetryPayload] = []

    def on_execution_start(self, payload: ExecutionTelemetryPayload) -> None:
        self.starts.append(payload)

    def on_execution_complete(self, payload: ExecutionTelemetryPayload) -> None:
        self.completes.append(payload)

    def on_execution_failure(self, payload: ExecutionTelemetryPayload) -> None:
        self.failures.append(payload)


def test_structured_reviewer_service_happy_path(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch, EchoExpectationLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("academic_profile", "Academic profile text"),
                ("key_outputs", "Key outputs text"),
                ("research_idea", "Research idea text"),
            ],
            external_user_id="user-1",
            idempotency_key="structured-happy-path",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert review.review_type == "structured"
        assert review.proposal_snippet_id is None
        assert len(cards) == 5
        assert all(card.assessment_status == AssessmentStatus.ASSESSED for card in cards)
    finally:
        service.repository.session.close()


def test_structured_shared_core_tracer_happy_path(monkeypatch) -> None:
    spy_core = SpyExecutionCore()
    service, call_id = _build_service(
        monkeypatch,
        EchoExpectationLLMClient(),
        execution_core=spy_core,
    )
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("academic_profile", "Academic profile text"),
                ("key_outputs", "Key outputs text"),
                ("research_idea", "Research idea text"),
            ],
            external_user_id="user-shared-core-tracer",
            idempotency_key="structured-shared-core-tracer",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 5
        assert all(card.assessment_status == AssessmentStatus.ASSESSED for card in cards)
        assert spy_core.calls == 3
    finally:
        service.repository.session.close()


def test_structured_reviewer_marks_alignment_not_assessable_when_missing_academic_profile(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch, EchoExpectationLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("key_outputs", "Key outputs text"),
                ("research_idea", "Research idea text"),
            ],
            external_user_id="user-2",
            idempotency_key="missing-academic",
        )
        assert review.status == ReviewStatus.COMPLETED
        not_assessable_cards = [
            card for card in cards if card.assessment_status == AssessmentStatus.NOT_ASSESSABLE
        ]
        assert len(not_assessable_cards) == 2
        assert all(
            card.not_assessable_reason and "academic_profile" in card.not_assessable_reason
            for card in not_assessable_cards
        )
    finally:
        service.repository.session.close()


def test_structured_reviewer_marks_alignment_not_assessable_when_missing_key_outputs(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch, EchoExpectationLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("academic_profile", "Academic profile text"),
                ("research_idea", "Research idea text"),
            ],
            external_user_id="user-3",
            idempotency_key="missing-key-outputs",
        )
        assert review.status == ReviewStatus.COMPLETED
        not_assessable_cards = [
            card for card in cards if card.assessment_status == AssessmentStatus.NOT_ASSESSABLE
        ]
        assert len(not_assessable_cards) == 2
        assert all(
            card.not_assessable_reason and "key_outputs" in card.not_assessable_reason
            for card in not_assessable_cards
        )
    finally:
        service.repository.session.close()


def test_structured_reviewer_service_sets_failed_on_llm_timeout_with_partial_cards(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch, TimeoutOnSecondCallLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("academic_profile", "Academic profile text"),
                ("key_outputs", "Key outputs text"),
            ],
            external_user_id="user-4",
            idempotency_key="timeout-case",
        )
        assert review.status == ReviewStatus.FAILED
        assert len(cards) >= 1
        assert "key_outputs" in (review.overall_summary or "")
    finally:
        service.repository.session.close()


def test_structured_shared_core_timeout_parity(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch, TimeoutOnSecondCallLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("academic_profile", "Academic profile text"),
                ("key_outputs", "Key outputs text"),
            ],
            external_user_id="user-core-timeout",
            idempotency_key="core-timeout-case",
        )
        assert review.status == ReviewStatus.FAILED
        assert len(cards) >= 1
        assert (
            review.overall_summary
            == "Structured review failed: timeout while reviewing "
            "'key_outputs' after 0.02s."
        )
    finally:
        service.repository.session.close()


def test_structured_shared_core_validation_failure_parity(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch, InvalidJsonLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="user-core-validation",
            idempotency_key="core-validation-case",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert review.overall_summary is not None
        assert "Structured review validation failed for 'academic_profile'" in (
            review.overall_summary
        )
        assert "Invalid JSON from LLM:" in review.overall_summary
    finally:
        service.repository.session.close()


def test_structured_shared_core_llm_failure_parity(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch, FailingLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="user-core-llm",
            idempotency_key="core-llm-case",
        )
        assert review.status == ReviewStatus.FAILED
        assert cards == []
        assert (
            review.overall_summary
            == "Structured review failed for 'academic_profile': synthetic llm failure"
        )
    finally:
        service.repository.session.close()


def test_structured_reviewer_validates_cardinality_only_for_assessable_expectations(
    monkeypatch,
) -> None:
    service, call_id = _build_service(monkeypatch, EchoExpectationLLMClient())
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("research_idea", "Research idea text only")],
            external_user_id="user-5",
            idempotency_key="assessable-only",
        )
        assert review.status == ReviewStatus.COMPLETED
        assessed = [c for c in cards if c.assessment_status == AssessmentStatus.ASSESSED]
        not_assessed = [
            c for c in cards if c.assessment_status == AssessmentStatus.NOT_ASSESSABLE
        ]
        assert len(assessed) == 1
        assert len(not_assessed) == 2
    finally:
        service.repository.session.close()


def test_structured_not_assessable_cards_remain_deterministic(monkeypatch) -> None:
    spy_core = SpyExecutionCore()
    service, call_id = _build_service(
        monkeypatch,
        EchoExpectationLLMClient(),
        execution_core=spy_core,
    )
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("research_idea", "Research idea text only")],
            external_user_id="user-core-not-assessable",
            idempotency_key="core-not-assessable-case",
        )
        assert review.status == ReviewStatus.COMPLETED

        not_assessable_cards = [
            card for card in cards if card.assessment_status == AssessmentStatus.NOT_ASSESSABLE
        ]
        assert len(not_assessable_cards) == 2
        assert all(
            card.feedback_text == "Not assessable due to missing cross-node context."
            for card in not_assessable_cards
        )
        assert all(
            card.not_assessable_reason and "Missing required context from:" in card.not_assessable_reason
            for card in not_assessable_cards
        )

        assert spy_core.calls == 1
        assert len(spy_core.expectation_batches) == 1
        assert len(spy_core.expectation_batches[0]) == 1
    finally:
        service.repository.session.close()


def test_structured_path_telemetry_is_non_invasive(monkeypatch) -> None:
    hooks = RecordingTelemetryHooks()
    core = ReviewExecutionCore(
        llm_client=EchoExpectationLLMClient(),
        timeout_seconds=0.02,
        telemetry_hooks=hooks,
    )
    service, call_id = _build_service(
        monkeypatch,
        EchoExpectationLLMClient(),
        execution_core=core,
    )
    try:
        review, cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[
                ("academic_profile", "Academic profile text"),
                ("key_outputs", "Key outputs text"),
                ("research_idea", "Research idea text"),
            ],
            external_user_id="user-core-telemetry",
            idempotency_key="core-telemetry-case",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert len(cards) == 5
        assert all(card.assessment_status == AssessmentStatus.ASSESSED for card in cards)
        assert len(hooks.starts) == 3
        assert len(hooks.completes) == 3
        assert hooks.failures == []
    finally:
        service.repository.session.close()


def test_incremental_migration_does_not_cross_regress(monkeypatch) -> None:
    service, call_id = _build_service(monkeypatch, EchoExpectationLLMClient())
    try:
        first_review, first_cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("academic_profile", "Academic profile text")],
            external_user_id="user-cross-regress-1",
            idempotency_key="cross-regress-structured-1",
        )
        assert first_review.status == ReviewStatus.COMPLETED
        assert len(first_cards) == 1
        assert first_cards[0].assessment_status == AssessmentStatus.ASSESSED

        second_review, second_cards = service.generate_structured_review(
            review_stage="STEP_1",
            call_id=call_id,
            nodes=[("research_idea", "Research idea text only")],
            external_user_id="user-cross-regress-2",
            idempotency_key="cross-regress-structured-2",
        )
        assert second_review.status == ReviewStatus.COMPLETED
        assessed_cards = [
            card for card in second_cards if card.assessment_status == AssessmentStatus.ASSESSED
        ]
        not_assessable_cards = [
            card
            for card in second_cards
            if card.assessment_status == AssessmentStatus.NOT_ASSESSABLE
        ]
        assert len(assessed_cards) == 1
        assert len(not_assessable_cards) == 2
    finally:
        service.repository.session.close()
