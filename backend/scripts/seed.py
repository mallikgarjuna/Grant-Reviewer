"""Seed script - populates database with ERC-2024-STG sample data from Stage 2."""

import sys
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlmodel import Session

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


def create_agency_and_call(session: Session) -> tuple[FundingAgency, FundingCall]:
    """Create basic agency and call."""
    agency = FundingAgency(
        name="European Research Council",
        short_name="ERC",
        description="EU funding body for frontier research",
    )
    session.add(agency)
    session.commit()
    session.refresh(agency)

    call = FundingCall(
        funding_agency_id=agency.id,
        name="ERC Starting Grant 2024",
        code="ERC-2024-STG",
        aim_objectives="Support excellent PIs at the career stage.",
        call_year=2024,
        is_active=True,
    )
    session.add(call)
    session.commit()
    session.refresh(call)
    return agency, call


def create_nodes(session: Session, call_id: UUID) -> tuple[ProposalNode, ProposalNode]:
    """Create proposal nodes."""
    part_b1 = ProposalNode(
        funding_call_id=call_id,
        parent_node_id=None,
        node_type=NodeType.SECTION,
        title="Part B1",
        order_index=1,
    )
    session.add(part_b1)
    session.commit()
    session.refresh(part_b1)

    sec_1 = ProposalNode(
        funding_call_id=call_id,
        parent_node_id=part_b1.id,
        node_type=NodeType.SUBSECTION,
        title="Section 1: Extended Synopsis",
        order_index=1,
        guidance_text="Summary addressing state-of-the-art...",
    )
    session.add(sec_1)
    session.commit()
    session.refresh(sec_1)

    sec_2 = ProposalNode(
        funding_call_id=call_id,
        parent_node_id=part_b1.id,
        node_type=NodeType.SUBSECTION,
        title="Section 2: Scientific Proposal",
        order_index=2,
    )
    session.add(sec_2)
    session.commit()
    session.refresh(sec_2)
    return sec_1, sec_2


def create_expectations(session: Session, call_id: UUID, node_id: UUID) -> None:
    """Create criteria, elements and expectations."""
    # Excellence Criterion
    crit_ex = EvaluationCriterion(
        funding_call_id=call_id,
        name="Excellence",
        order_index=1,
    )
    session.add(crit_ex)

    # Impact Criterion
    crit_im = EvaluationCriterion(
        funding_call_id=call_id,
        name="Impact",
        order_index=2,
    )
    session.add(crit_im)
    session.commit()
    session.refresh(crit_ex)
    session.refresh(crit_im)

    # Elements
    el_obj = EvaluationElement(
        evaluation_criterion_id=crit_ex.id,
        name="Clarity of Objectives",
    )
    el_meth = EvaluationElement(
        evaluation_criterion_id=crit_ex.id,
        name="Soundness of Methodology",
    )
    el_break = EvaluationElement(
        evaluation_criterion_id=crit_im.id,
        name="Potential Breakthrough",
    )
    session.add(el_obj)
    session.add(el_meth)
    session.add(el_break)
    session.commit()
    session.refresh(el_obj)
    session.refresh(el_meth)
    session.refresh(el_break)

    # Expectations
    session.add(
        NodeExpectation(
            proposal_node_id=node_id,
            evaluation_element_id=el_obj.id,
            expectation_strength=ExpectationStrength.MANDATORY,
            evaluation_intent=EvaluationIntent.COMPLIANCE,
            guidance_note="Verify objectives.",
            order_index=1,
        ),
    )
    session.add(
        NodeExpectation(
            proposal_node_id=node_id,
            evaluation_element_id=el_meth.id,
            expectation_strength=ExpectationStrength.IMPORTANT,
            evaluation_intent=EvaluationIntent.QUALITY,
            guidance_note="Assess methodology.",
            order_index=2,
        ),
    )
    session.add(
        NodeExpectation(
            proposal_node_id=node_id,
            evaluation_element_id=el_break.id,
            expectation_strength=ExpectationStrength.OPTIONAL,
            evaluation_intent=EvaluationIntent.STRATEGIC_FIT,
            guidance_note="Look for breakthroughs.",
            order_index=3,
        ),
    )
    session.commit()


def seed_database() -> dict[str, Any]:
    """Seed database with sample data."""
    create_db_and_tables()
    session = get_session()

    agency, call = create_agency_and_call(session)
    sec_1, sec_2 = create_nodes(session, call.id)
    create_expectations(session, call.id, sec_1.id)

    template = PromptTemplate(
        name="ERC Review Template",
        template_text="Review snippet: {snippet}",
        is_active=True,
    )
    session.add(template)
    session.commit()
    session.refresh(template)

    result = {
        "agency_id": agency.id,
        "call_id": call.id,
        "section_1_id": sec_1.id,
        "section_2_id": sec_2.id,
        "template_id": template.id,
    }
    session.close()
    return result


if __name__ == "__main__":
    ids = seed_database()
    print("Database seeded successfully!")
