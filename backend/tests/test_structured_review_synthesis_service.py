"""backend/tests/test_structured_review_synthesis_service.py
Structured review synthesis helper tests.
"""

from __future__ import annotations

import pytest

from app.services.structured_review_synthesis_service import (
    StructuredReviewSynthesisRejectedResult,
    StructuredReviewSynthesisRequest,
    StructuredReviewSynthesisService,
)

pytestmark = pytest.mark.no_db


class StaticJSONLLMClient:
    """backend/tests/test_structured_review_synthesis_service.py
    Deterministic JSON client for helper validation tests.
    """

    def __init__(self, response_text: str) -> None:
        self.response_text = response_text

    def generate(self, prompt: str) -> str:
        return self.response_text

    def get_model_name(self) -> str:
        return "static-json-helper-test-model"


def _build_request() -> StructuredReviewSynthesisRequest:
    return StructuredReviewSynthesisRequest(
        expectation_id="exp-123",
        node_logical_id="poc_idea_innovation",
        evaluation_criterion_name="Excellence",
        evaluation_element_logical_id="elem_breakthrough_innovation_potential",
        evaluation_element_name="Breakthrough innovation potential",
        deterministic_feedback="Revise poc_idea_innovation to strengthen breakthrough innovation potential by showing how the idea is high risk and has potential high gain.",
        submitted_excerpt="This proposal advances a high-risk catalyst platform with a distinct translational route for market validation.",
        subordinate_prompt_context=(
            "Is the idea high risk and with a potential high gain?",
        ),
    )


def test_wf0078_contract_rejects_wrong_element_output() -> None:
    service = StructuredReviewSynthesisService(
        llm_client=StaticJSONLLMClient(
            """
            {
              "expectation_id": "exp-123",
              "node_logical_id": "poc_idea_innovation",
              "evaluation_element_logical_id": "elem_wrong_element",
              "synthesized_feedback": "Synthesis text.",
              "evidence_quotes": ["high-risk catalyst platform"]
            }
            """
        )
    )

    result = service.attempt_card_synthesis(_build_request())

    assert isinstance(result, StructuredReviewSynthesisRejectedResult)
    assert result.rejection_code == "wrong_element"
    assert not hasattr(result, "synthesized_feedback")


def test_wf0078_contract_rejects_ambiguous_or_mismatched_output() -> None:
    service = StructuredReviewSynthesisService(
        llm_client=StaticJSONLLMClient(
            """
            {
              "expectation_id": "exp-other",
              "node_logical_id": "poc_idea_innovation",
              "evaluation_element_logical_id": "elem_breakthrough_innovation_potential",
              "synthesized_feedback": "Synthesis text.",
              "evidence_quotes": ["high-risk catalyst platform"]
            }
            """
        )
    )

    result = service.attempt_card_synthesis(_build_request())

    assert isinstance(result, StructuredReviewSynthesisRejectedResult)
    assert result.rejection_code == "ambiguous_or_mismatched_output"
    assert not hasattr(result, "synthesized_feedback")


def test_wf0078_contract_rejects_malformed_output() -> None:
    service = StructuredReviewSynthesisService(
        llm_client=StaticJSONLLMClient("{not-json")
    )

    result = service.attempt_card_synthesis(_build_request())

    assert isinstance(result, StructuredReviewSynthesisRejectedResult)
    assert result.rejection_code == "malformed_output"
    assert not hasattr(result, "synthesized_feedback")
