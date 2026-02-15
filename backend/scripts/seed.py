"""Seed script - populates database with ERC-2024-STG sample data from Stage 2.

NOTE: This script is idempotent - it will skip entities that already exist
and only create missing ones. Safe to run multiple times.
"""

import sys
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

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


def get_or_create_agency_and_call(
    session: Session,
) -> tuple[FundingAgency, FundingCall]:
    """Get or create agency and call."""
    # Check if agency exists
    agency = session.exec(
        select(FundingAgency).where(FundingAgency.short_name == "ERC")
    ).first()

    if not agency:
        print("  Creating agency: ERC")
        agency = FundingAgency(
            name="European Research Council",
            short_name="ERC",
            description="EU funding body for frontier research",
        )
        session.add(agency)
        session.commit()
        session.refresh(agency)
    else:
        print("  Agency 'ERC' already exists, skipping")

    # Check if call exists
    call = session.exec(
        select(FundingCall).where(FundingCall.code == "ERC-2024-STG")
    ).first()

    if not call:
        print("  Creating call: ERC-2024-STG")
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
    else:
        print("  Call 'ERC-2024-STG' already exists, skipping")

    return agency, call


def get_or_create_nodes(
    session: Session, call_id: UUID
) -> tuple[ProposalNode, ProposalNode]:
    """Get or create proposal nodes."""
    # Check if Part B1 exists
    part_b1 = session.exec(
        select(ProposalNode).where(
            ProposalNode.funding_call_id == call_id,
            ProposalNode.title == "Part B1",
            ProposalNode.parent_node_id.is_(None),
        )
    ).first()

    if not part_b1:
        print("  Creating node: Part B1")
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
    else:
        print("  Node 'Part B1' already exists, skipping")

    # Check if Section 1 exists
    sec_1 = session.exec(
        select(ProposalNode).where(
            ProposalNode.funding_call_id == call_id,
            ProposalNode.title == "Section 1: Extended Synopsis",
        )
    ).first()

    if not sec_1:
        print("  Creating node: Section 1")
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
    else:
        print("  Node 'Section 1' already exists, skipping")

    # Check if Section 2 exists
    sec_2 = session.exec(
        select(ProposalNode).where(
            ProposalNode.funding_call_id == call_id,
            ProposalNode.title == "Section 2: Scientific Proposal",
        )
    ).first()

    if not sec_2:
        print("  Creating node: Section 2")
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
    else:
        print("  Node 'Section 2' already exists, skipping")

    return sec_1, sec_2


def get_or_create_expectations(session: Session, call_id: UUID, node_id: UUID) -> None:
    """Get or create criteria, elements and expectations."""
    # Check if criteria already exist for this call
    existing_criteria = session.exec(
        select(EvaluationCriterion).where(
            EvaluationCriterion.funding_call_id == call_id
        )
    ).first()

    if existing_criteria:
        print("  Criteria already exist for this call, skipping rubric creation")
        return

    print("  Creating criteria and elements...")

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


def get_or_create_template(session: Session) -> PromptTemplate:
    """Get or create prompt template."""
    template = session.exec(
        select(PromptTemplate).where(PromptTemplate.name == "ERC Review Template")
    ).first()

    if not template:
        print("  Creating prompt template")
        template = PromptTemplate(
            name="ERC Review Template",
            template_text="Review snippet: {snippet}",
            is_active=True,
        )
        session.add(template)
        session.commit()
        session.refresh(template)
    else:
        print("  Prompt template already exists, skipping")

    return template


def seed_database() -> dict[str, Any]:
    """Seed database with sample data (idempotent)."""
    create_db_and_tables()
    session = get_session()

    agency, call = get_or_create_agency_and_call(session)
    sec_1, sec_2 = get_or_create_nodes(session, call.id)
    get_or_create_expectations(session, call.id, sec_1.id)
    template = get_or_create_template(session)

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
    print("Seeding database...")
    ids = seed_database()
    print("\nDatabase seeded successfully!")
    print(f"  Call ID: {ids['call_id']}")
    print(f"  Section 1 ID: {ids['section_1_id']}")
