"""
Seed script - populates database with ERC-2024-STG sample data from Stage 2.
"""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import create_db_and_tables, get_session
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
)


def seed_database() -> dict:
    """
    Seed database with ERC-2024-STG sample data.

    Returns dict with created entity IDs for use in scripts.
    """
    create_db_and_tables()
    session = get_session()

    # 1. FundingAgency
    agency = FundingAgency(
        name="European Research Council",
        short_name="ERC",
        description="EU funding body for frontier research",
    )
    session.add(agency)
    session.commit()
    session.refresh(agency)

    # 2. FundingCall
    call = FundingCall(
        funding_agency_id=agency.id,
        name="ERC Starting Grant 2024",
        code="ERC-2024-STG",
        aim_objectives="Support excellent PIs at the career stage at which they are starting their own independent research team.",
        call_year=2024,
        is_active=True,
    )
    session.add(call)
    session.commit()
    session.refresh(call)

    # 3. ProposalNodes (hierarchy)
    part_b1 = ProposalNode(
        funding_call_id=call.id,
        parent_node_id=None,
        node_type=NodeType.SECTION,
        title="Part B1",
        order_index=1,
    )
    session.add(part_b1)
    session.commit()
    session.refresh(part_b1)

    section_1 = ProposalNode(
        funding_call_id=call.id,
        parent_node_id=part_b1.id,
        node_type=NodeType.SUBSECTION,
        title="Section 1: Extended Synopsis",
        order_index=1,
        guidance_text="The extended synopsis should give a summary of the proposal, addressing: state-of-the-art and objectives, methodology, and the ground-breaking nature/impact.",
    )
    session.add(section_1)
    session.commit()
    session.refresh(section_1)

    section_2 = ProposalNode(
        funding_call_id=call.id,
        parent_node_id=part_b1.id,
        node_type=NodeType.SUBSECTION,
        title="Section 2: Scientific Proposal",
        order_index=2,
    )
    session.add(section_2)
    session.commit()
    session.refresh(section_2)

    # 4. EvaluationCriteria
    crit_excellence = EvaluationCriterion(
        funding_call_id=call.id,
        name="Excellence",
        description="Scientific quality and innovation",
        order_index=1,
    )
    session.add(crit_excellence)
    session.commit()
    session.refresh(crit_excellence)

    crit_impact = EvaluationCriterion(
        funding_call_id=call.id,
        name="Impact",
        description="Potential breakthrough and wider effects",
        order_index=2,
    )
    session.add(crit_impact)
    session.commit()
    session.refresh(crit_impact)

    # 5. EvaluationElements
    elem_clarity = EvaluationElement(
        evaluation_criterion_id=crit_excellence.id,
        name="Clarity of Objectives",
        description="Are objectives clearly stated and measurable?",
    )
    session.add(elem_clarity)
    session.commit()
    session.refresh(elem_clarity)

    elem_methodology = EvaluationElement(
        evaluation_criterion_id=crit_excellence.id,
        name="Soundness of Methodology",
        description="Is the proposed methodology appropriate?",
    )
    session.add(elem_methodology)
    session.commit()
    session.refresh(elem_methodology)

    elem_breakthrough = EvaluationElement(
        evaluation_criterion_id=crit_impact.id,
        name="Potential Breakthrough",
        description="Does it represent a paradigm shift?",
    )
    session.add(elem_breakthrough)
    session.commit()
    session.refresh(elem_breakthrough)

    # 6. NodeExpectations (Intelligence Layer for section_1)
    expect_1 = NodeExpectation(
        proposal_node_id=section_1.id,
        evaluation_element_id=elem_clarity.id,
        expectation_strength=ExpectationStrength.MANDATORY,
        evaluation_intent=EvaluationIntent.COMPLIANCE,
        guidance_note="Verify that objectives are explicitly stated and measurable.",
        order_index=1,
    )
    session.add(expect_1)
    session.commit()
    session.refresh(expect_1)

    expect_2 = NodeExpectation(
        proposal_node_id=section_1.id,
        evaluation_element_id=elem_methodology.id,
        expectation_strength=ExpectationStrength.IMPORTANT,
        evaluation_intent=EvaluationIntent.QUALITY,
        guidance_note="Assess whether the proposed methodology is appropriate for the stated objectives.",
        order_index=2,
    )
    session.add(expect_2)
    session.commit()
    session.refresh(expect_2)

    expect_3 = NodeExpectation(
        proposal_node_id=section_1.id,
        evaluation_element_id=elem_breakthrough.id,
        expectation_strength=ExpectationStrength.OPTIONAL,
        evaluation_intent=EvaluationIntent.STRATEGIC_FIT,
        guidance_note="Look for claims of novelty or paradigm shift.",
        order_index=3,
    )
    session.add(expect_3)
    session.commit()
    session.refresh(expect_3)

    # 7. PromptTemplate
    template = PromptTemplate(
        name="ERC Review Template",
        version=1,
        template_text="""You are an expert ERC panel reviewer. Review the following proposal snippet.

## Proposal Context
{proposal_context}

## Evaluation Expectations
{expectations}

## Submitted Text
{snippet}

Provide critical, reviewer-style feedback for each expectation.""",
        is_active=True,
    )
    session.add(template)
    session.commit()
    session.refresh(template)

    # Capture IDs before closing session
    result = {
        "agency_id": agency.id,
        "call_id": call.id,
        "section_1_id": section_1.id,
        "section_2_id": section_2.id,
        "template_id": template.id,
    }

    session.close()

    return result


if __name__ == "__main__":
    ids = seed_database()
    print("Database seeded successfully!")
    print(f"Call ID: {ids['call_id']}")
    print(f"Section 1 ID: {ids['section_1_id']} (has 3 expectations)")
    print(f"Section 2 ID: {ids['section_2_id']} (has 0 expectations)")
