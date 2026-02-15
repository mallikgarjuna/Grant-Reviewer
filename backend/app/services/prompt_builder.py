"""
Prompt builder for grant proposal reviews.

Assembles the full prompt from node, snippet, and expectations.
Includes expectation_strength and evaluation_intent per PRD requirements.
"""

from app.models.domain import NodeExpectation, ProposalNode

REVIEW_PROMPT_TEMPLATE = """You are a grant proposal reviewer evaluating text against specific criteria.

## Proposal Section
Title: {node_title}
Guidance: {guidance_text}

## Submitted Text
{snippet_text}

## Evaluation Criteria
{expectations_block}

## Instructions
1. For EACH criterion listed above, provide constructive, specific feedback based on the Submitted Text.
2. Consider the 'Strength' (MANDATORY, IMPORTANT, OPTIONAL) and 'Intent' (QUALITY, COMPLIANCE, RISK, STRATEGIC_FIT) of each criterion in your assessment.
3. You MUST return exactly one feedback item for every ID provided. Do not skip any IDs. Do not add extra IDs.
4. Each feedback must be non-empty and actionable.
5. Return ONLY a valid JSON object in this exact format:
{{"feedbacks": [{{"node_expectation_id": "...", "feedback": "..."}}]}}
"""


def _format_expectation(exp: NodeExpectation, index: int) -> str:
    """Format a single expectation for the prompt."""
    element_name = exp.element.name if exp.element else "Unknown"
    element_desc = exp.element.description if exp.element and exp.element.description else "No description"

    return f"""
{index}. ID: {exp.id}
   Element: {element_name}
   Description: {element_desc}
   Strength: {exp.expectation_strength.value}
   Intent: {exp.evaluation_intent.value}
   Reviewer Guidance: {exp.guidance_note or "No specific guidance"}
"""


def build_review_prompt(
    node: ProposalNode,
    snippet_text: str,
    expectations: list[NodeExpectation],
) -> str:
    """
    Build the complete prompt for LLM review.

    Args:
        node: The ProposalNode being reviewed
        snippet_text: The researcher's submitted text
        expectations: List of NodeExpectations to evaluate against

    Returns:
        Complete prompt string ready to send to LLM
    """
    # Format expectations block
    expectations_lines = []
    for i, exp in enumerate(expectations, start=1):
        expectations_lines.append(_format_expectation(exp, i))

    expectations_block = "\n".join(expectations_lines)

    return REVIEW_PROMPT_TEMPLATE.format(
        node_title=node.title,
        guidance_text=node.guidance_text or "No guidance provided",
        snippet_text=snippet_text,
        expectations_block=expectations_block,
    )
