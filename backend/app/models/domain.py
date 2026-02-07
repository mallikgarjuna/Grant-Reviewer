"""
Domain models for Grant Reviewer MVP.

11 SQLModel tables following the finalized schema from Stage 1.
"""

import enum
from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


# Enums
class NodeType(enum.StrEnum):
    SECTION = "SECTION"
    SUBSECTION = "SUBSECTION"


class ExpectationStrength(enum.StrEnum):
    MANDATORY = "MANDATORY"
    IMPORTANT = "IMPORTANT"
    OPTIONAL = "OPTIONAL"


class EvaluationIntent(enum.StrEnum):
    COMPLIANCE = "COMPLIANCE"
    QUALITY = "QUALITY"
    RISK = "RISK"
    STRATEGIC_FIT = "STRATEGIC_FIT"


class ReviewRating(enum.StrEnum):
    CRITICAL = "CRITICAL"  # Red
    WARNING = "WARNING"    # Orange
    SUCCESS = "SUCCESS"    # Green
    NOTE = "NOTE"          # Blue


# 1. FundingAgency
class FundingAgency(SQLModel, table=True):
    __tablename__ = "funding_agencies"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    short_name: str = Field(unique=True)
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    calls: list["FundingCall"] = Relationship(back_populates="agency")


# 2. FundingCall
class FundingCall(SQLModel, table=True):
    __tablename__ = "funding_calls"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_agency_id: UUID = Field(foreign_key="funding_agencies.id")
    name: str
    code: str
    aim_objectives: str | None = None
    scope: str | None = None
    general_guidelines: str | None = None
    call_year: int
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    agency: FundingAgency | None = Relationship(back_populates="calls")
    nodes: list["ProposalNode"] = Relationship(back_populates="call")
    criteria: list["EvaluationCriterion"] = Relationship(back_populates="call")


# 3. ProposalNode
class ProposalNode(SQLModel, table=True):
    __tablename__ = "proposal_nodes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_call_id: UUID = Field(foreign_key="funding_calls.id")
    parent_node_id: UUID | None = Field(
        default=None,
        foreign_key="proposal_nodes.id",
    )
    node_type: NodeType
    title: str
    order_index: int = 0
    guidance_text: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    call: FundingCall | None = Relationship(back_populates="nodes")
    expectations: list["NodeExpectation"] = Relationship(back_populates="node")


# 4. EvaluationCriterion
class EvaluationCriterion(SQLModel, table=True):
    __tablename__ = "evaluation_criteria"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_call_id: UUID = Field(foreign_key="funding_calls.id")
    name: str
    description: str | None = None
    order_index: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    call: FundingCall | None = Relationship(back_populates="criteria")
    elements: list["EvaluationElement"] = Relationship(back_populates="criterion")


# 5. EvaluationElement
class EvaluationElement(SQLModel, table=True):
    __tablename__ = "evaluation_elements"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    evaluation_criterion_id: UUID = Field(foreign_key="evaluation_criteria.id")
    name: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    criterion: EvaluationCriterion | None = Relationship(back_populates="elements")
    expectations: list["NodeExpectation"] = Relationship(back_populates="element")


# 6. NodeExpectation (Intelligence Layer)
class NodeExpectation(SQLModel, table=True):
    __tablename__ = "node_expectations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    proposal_node_id: UUID = Field(foreign_key="proposal_nodes.id")
    evaluation_element_id: UUID = Field(foreign_key="evaluation_elements.id")
    expectation_strength: ExpectationStrength
    evaluation_intent: EvaluationIntent
    guidance_note: str | None = None
    order_index: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    node: ProposalNode | None = Relationship(back_populates="expectations")
    element: EvaluationElement | None = Relationship(back_populates="expectations")
    review_cards: list["ReviewCard"] = Relationship(back_populates="expectation")


# 7. User
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str | None = None
    is_anonymous: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    snippets: list["ProposalSnippet"] = Relationship(back_populates="user")


# 8. ProposalSnippet
class ProposalSnippet(SQLModel, table=True):
    __tablename__ = "proposal_snippets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    funding_call_id: UUID = Field(foreign_key="funding_calls.id")
    proposal_node_id: UUID = Field(foreign_key="proposal_nodes.id")
    pasted_text: str
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(hours=24),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    user: User | None = Relationship(back_populates="snippets")
    review: Optional["Review"] = Relationship(back_populates="snippet")


# 9. PromptTemplate
class PromptTemplate(SQLModel, table=True):
    __tablename__ = "prompt_templates"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    version: int = 1
    template_text: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    reviews: list["Review"] = Relationship(back_populates="template")


# 10. Review
class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    proposal_snippet_id: UUID = Field(foreign_key="proposal_snippets.id")
    prompt_template_id: UUID = Field(foreign_key="prompt_templates.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    snippet: ProposalSnippet | None = Relationship(back_populates="review")
    template: PromptTemplate | None = Relationship(back_populates="reviews")
    cards: list["ReviewCard"] = Relationship(back_populates="review")


# 11. ReviewCard
class ReviewCard(SQLModel, table=True):
    __tablename__ = "review_cards"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    review_id: UUID = Field(foreign_key="reviews.id")
    node_expectation_id: UUID = Field(foreign_key="node_expectations.id")
    rating: ReviewRating
    feedback_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    review: Review | None = Relationship(back_populates="cards")
    expectation: NodeExpectation | None = Relationship(back_populates="review_cards")
