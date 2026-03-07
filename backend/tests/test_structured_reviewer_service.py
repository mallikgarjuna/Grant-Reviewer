"""backend/tests/test_structured_reviewer_service.py
Structured reviewer service tests for pipeline_v1-only runtime.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from uuid import UUID

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
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.services.structured_reviewer_service import StructuredReviewerService
from scripts.ingest_call import ingest_call


def _reset_database() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


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

    call = session.exec(select(FundingCall).where(FundingCall.code == "MSCA-PF-2025")).first()
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
        assessed_cards = [card for card in cards if card.assessment_status == AssessmentStatus.ASSESSED]
        not_assessable_cards = [
            card for card in cards if card.assessment_status == AssessmentStatus.NOT_ASSESSABLE
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
    academic_profile_node = next(node for node, _ in call_nodes if node.logical_id == "academic_profile")
    valid_expectation_id = str(service.repository.get_expectations_for_node(academic_profile_node.id)[0].id)

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
        captured_snapshot.update(review_request.call_config_snapshot.to_canonical_payload())
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
        assert (
            captured_snapshot.get("reviewer_policy_prompt_by_node") is None
        )
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
        assert all(card.assessment_status == AssessmentStatus.ASSESSED for card in cards)
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
            definition.source_path
            == "data/calls/canonical/msca/msca_pf_2025_full.yaml"
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
