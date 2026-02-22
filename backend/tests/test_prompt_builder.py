"""Tests for prompt builder cross-node context support."""

from uuid import uuid4

from app.models.domain import (
    EvaluationIntent,
    ExpectationStrength,
    NodeExpectation,
    ProposalNode,
)
from app.services.prompt_builder import build_review_prompt


def _build_node() -> ProposalNode:
    return ProposalNode(
        id=uuid4(),
        funding_call_id=uuid4(),
        logical_id="research_idea",
        parent_node_id=None,
        node_type="SECTION",
        title="Research idea",
        order_index=1,
        guidance_text="Keep concise.",
    )


def _build_expectation() -> NodeExpectation:
    return NodeExpectation(
        id=uuid4(),
        proposal_node_id=uuid4(),
        evaluation_element_id=uuid4(),
        expectation_strength=ExpectationStrength.MANDATORY,
        evaluation_intent=EvaluationIntent.QUALITY,
        guidance_note="Be specific.",
        order_index=1,
    )


def test_build_review_prompt_omits_cross_node_context_when_none() -> None:
    prompt = build_review_prompt(
        node=_build_node(),
        snippet_text="Idea text",
        expectations=[_build_expectation()],
    )

    assert "## Cross-Node Context" not in prompt
    assert "## Submitted Text" in prompt
    assert "Idea text" in prompt


def test_build_review_prompt_includes_cross_node_context_when_provided() -> None:
    prompt = build_review_prompt(
        node=_build_node(),
        snippet_text="Idea text",
        expectations=[_build_expectation()],
        cross_node_context={
            "academic_profile": "Profile summary",
            "key_outputs": "Output evidence",
        },
    )

    assert "## Cross-Node Context" in prompt
    assert "- academic_profile:" in prompt
    assert "Profile summary" in prompt
    assert "- key_outputs:" in prompt
    assert "Output evidence" in prompt
