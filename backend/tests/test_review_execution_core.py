"""Focused tests for shared review execution core."""

from __future__ import annotations

import json
import re
import time
from uuid import uuid4

import pytest

from app.models.domain import EvaluationIntent, ExpectationStrength, NodeExpectation, NodeType, ProposalNode
from app.services.review_execution_core import (
    ExecutionFailureCategory,
    ReviewExecutionCore,
)
from app.services.reviewer_policy import ReviewerPolicyRule

pytestmark = pytest.mark.no_db


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


class TimeoutLLMClient(EchoExpectationLLMClient):
    def generate(self, prompt: str) -> str:
        time.sleep(0.1)
        return super().generate(prompt)


class PolicyTermLLMClient:
    def __init__(self, feedback: str) -> None:
        self._feedback = feedback

    def generate(self, prompt: str) -> str:
        expectation_ids = re.findall(r"ID:\s*([0-9a-fA-F-]{36})", prompt)
        return json.dumps(
            {
                "feedbacks": [
                    {
                        "node_expectation_id": expectation_ids[0],
                        "feedback": self._feedback,
                    }
                ]
            }
        )

    def get_model_name(self) -> str:
        return "policy-term-model"


def _build_node() -> ProposalNode:
    return ProposalNode(
        id=uuid4(),
        funding_call_id=uuid4(),
        logical_id="research_idea",
        node_type=NodeType.SECTION,
        title="Research idea",
        order_index=1,
    )


def _build_expectations(count: int = 1) -> list[NodeExpectation]:
    expectations: list[NodeExpectation] = []
    for order in range(1, count + 1):
        expectations.append(
            NodeExpectation(
                id=uuid4(),
                proposal_node_id=uuid4(),
                evaluation_element_id=uuid4(),
                expectation_strength=ExpectationStrength.MANDATORY,
                evaluation_intent=EvaluationIntent.QUALITY,
                guidance_note="guidance",
                order_index=order,
            )
        )
    return expectations


def test_core_success_result() -> None:
    core = ReviewExecutionCore(llm_client=EchoExpectationLLMClient(), timeout_seconds=0.5)
    node = _build_node()
    expectations = _build_expectations(count=2)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
    )

    assert result.failure is None
    assert len(result.feedbacks) == 2
    assert result.raw_response is not None
    assert result.prompt
    assert result.warning_violations == []


def test_core_timeout_classification() -> None:
    core = ReviewExecutionCore(llm_client=TimeoutLLMClient(), timeout_seconds=0.01)
    node = _build_node()
    expectations = _build_expectations(count=1)

    result = core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[],
    )

    assert result.failure is not None
    assert result.failure.category == ExecutionFailureCategory.TIMEOUT
    assert result.feedbacks == []
    assert result.raw_response is None


def test_core_policy_postcheck_classification() -> None:
    rule_post_check = ReviewerPolicyRule(
        id="pol_warn",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="stage_scope",
        instruction="Warn on maybe wording",
        severity="WARNING",
        enforcement_mode="POST_CHECK",
        forbidden_terms=("maybe",),
    )
    rule_blocking = ReviewerPolicyRule(
        id="pol_block",
        applies_to_stage="STEP_1",
        applies_to_node_ids=(),
        rule_type="criterion_scope",
        instruction="Block budget assessment",
        severity="WARNING",
        enforcement_mode="BLOCKING",
        forbidden_terms=("insufficient budget",),
    )

    node = _build_node()
    expectations = _build_expectations(count=1)

    warning_core = ReviewExecutionCore(
        llm_client=PolicyTermLLMClient("This is maybe acceptable."),
        timeout_seconds=0.5,
    )
    warning_result = warning_core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[rule_post_check],
    )
    assert warning_result.failure is None
    assert len(warning_result.warning_violations) == 1
    assert "pol_warn" in warning_result.warning_violations[0]

    blocking_core = ReviewExecutionCore(
        llm_client=PolicyTermLLMClient("The proposal has insufficient budget."),
        timeout_seconds=0.5,
    )
    blocking_result = blocking_core.execute_assessable_node(
        node=node,
        snippet_text="Some snippet text",
        expectations=expectations,
        reviewer_policy_rules=[rule_blocking],
    )
    assert blocking_result.failure is not None
    assert blocking_result.failure.category == ExecutionFailureCategory.POLICY_BLOCKING
    assert "pol_block" in blocking_result.failure.message
