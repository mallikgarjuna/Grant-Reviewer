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
    WARNING = "WARNING"  # Orange
    SUCCESS = "SUCCESS"  # Green
    NOTE = "NOTE"  # Blue


class ReviewStatus(enum.StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# 1. FundingAgency
class FundingAgency(SQLModel, table=True):
    """Organization defining the rules, criteria, and philosophy for grant calls."""

    __tablename__ = "funding_agencies"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Full legal name of the funding agency")
    short_name: str = Field(
        unique=True,
        index=True,
        description="Commonly used acronym",
    )
    description: str | None = Field(
        default=None,
        description="General mission statement",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    calls: list["FundingCall"] = Relationship(back_populates="agency")


# 2. FundingCall
class FundingCall(SQLModel, table=True):
    """Specific grant program's aims, scope, and rubric context."""

    __tablename__ = "funding_calls"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_agency_id: UUID = Field(
        foreign_key="funding_agencies.id",
        description="Owning agency",
    )
    name: str = Field(description="Common name of the grant call")
    code: str = Field(index=True, description="Official call identifier code")
    aim_objectives: str | None = Field(
        default=None,
        description="The intended impact and goals of the call",
    )
    scope: str | None = Field(
        default=None,
        description="The thematic areas or boundaries of the call",
    )
    general_guidelines: str | None = Field(
        default=None,
        description="General instructions for applicants",
    )
    call_year: int = Field(description="The calendar year of the call")
    is_active: bool = Field(
        default=True,
        description="Whether this call is currently open or relevant",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    agency: FundingAgency | None = Relationship(back_populates="calls")
    nodes: list["ProposalNode"] = Relationship(back_populates="call")
    criteria: list["EvaluationCriterion"] = Relationship(back_populates="call")


# 3. ProposalNode
class ProposalNode(SQLModel, table=True):
    """Structural section or subsection of a proposal for anchoring reviews."""

    __tablename__ = "proposal_nodes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_call_id: UUID = Field(
        foreign_key="funding_calls.id",
        description="Owning call",
    )
    parent_node_id: UUID | None = Field(
        default=None,
        foreign_key="proposal_nodes.id",
        description="Parent section for hierarchical nesting",
    )
    node_type: NodeType = Field(description="Type of node: SECTION or SUBSECTION")
    title: str = Field(description="Display title of the section")
    order_index: int = Field(default=0, description="Sequential order in the document")
    guidance_text: str | None = Field(
        default=None,
        description="Guidance provided to the applicant",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    call: FundingCall | None = Relationship(back_populates="nodes")
    expectations: list["NodeExpectation"] = Relationship(back_populates="node")


# 4. EvaluationCriterion
class EvaluationCriterion(SQLModel, table=True):
    """Top-level assessment dimension (e.g., Excellence, Impact) for a call."""

    __tablename__ = "evaluation_criteria"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_call_id: UUID = Field(
        foreign_key="funding_calls.id",
        description="Owning call",
    )
    name: str = Field(description="Name of the assessment dimension")
    description: str | None = Field(
        default=None,
        description="Brief explanation of the criterion",
    )
    order_index: int = Field(default=0, description="Display order for the rubric")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    call: FundingCall | None = Relationship(back_populates="criteria")
    elements: list["EvaluationElement"] = Relationship(back_populates="criterion")


# 5. EvaluationElement
class EvaluationElement(SQLModel, table=True):
    """Atomic reviewable concern explicitly evaluated within a criterion."""

    __tablename__ = "evaluation_elements"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    evaluation_criterion_id: UUID = Field(
        foreign_key="evaluation_criteria.id",
        description="Owning criterion",
    )
    name: str = Field(description="Name of the specific reviewable concern")
    description: str | None = Field(
        default=None,
        description="What the element explicitly evaluates",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    criterion: EvaluationCriterion | None = Relationship(back_populates="elements")
    expectations: list["NodeExpectation"] = Relationship(back_populates="element")


# 6. NodeExpectation (Intelligence Layer)
class NodeExpectation(SQLModel, table=True):
    """Intersection of proposal node and rubric; defines strictness and intent."""

    __tablename__ = "node_expectations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    proposal_node_id: UUID = Field(
        foreign_key="proposal_nodes.id",
        description="Owning proposal node",
    )
    evaluation_element_id: UUID = Field(
        foreign_key="evaluation_elements.id",
        description="Specific rubric element",
    )
    expectation_strength: ExpectationStrength = Field(
        description="Priority/Strictness of the requirement",
    )
    evaluation_intent: EvaluationIntent = Field(
        description="Type of reviewer check (e.g., Quality, Risk)",
    )
    guidance_note: str | None = Field(
        default=None,
        description="Specific reviewer orientation",
    )
    order_index: int = Field(default=0, description="Display order within a card stack")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    node: ProposalNode | None = Relationship(back_populates="expectations")
    element: EvaluationElement | None = Relationship(back_populates="expectations")
    review_cards: list["ReviewCard"] = Relationship(back_populates="expectation")


# 7. User
class User(SQLModel, table=True):
    """Owner of snippets and reviews; supports anonymous research sessions."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str | None = Field(
        default=None,
        unique=True,
        description="Unique identifier for registered users",
    )
    is_anonymous: bool = Field(
        default=True,
        description="Whether the user is an unauthenticated guest",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    snippets: list["ProposalSnippet"] = Relationship(back_populates="user")


# 8. ProposalSnippet
class ProposalSnippet(SQLModel, table=True):
    """User-pasted proposal fragment to be evaluated in a precise context."""

    __tablename__ = "proposal_snippets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", description="Owning user")
    funding_call_id: UUID = Field(
        foreign_key="funding_calls.id",
        description="Selected call rubric",
    )
    proposal_node_id: UUID = Field(
        foreign_key="proposal_nodes.id",
        description="Selected proposal section",
    )
    pasted_text: str = Field(description="The actual snippet content to be reviewed")
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(hours=24),
        description="Temporal deadline for snippet TTL cleanup",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    user: User | None = Relationship(back_populates="snippets")
    review: Optional["Review"] = Relationship(back_populates="snippet")


# 9. PromptTemplate
class PromptTemplate(SQLModel, table=True):
    """Versioned AI reviewer logic for auditability and reproducibility."""

    __tablename__ = "prompt_templates"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Display name for the template")
    version: int = Field(default=1, description="Incrementing version number")
    template_text: str = Field(description="The primary Jinja2 or f-string prompt body")
    is_active: bool = Field(
        default=True,
        index=True,
        description="Whether this version is used for new reviews",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    reviews: list["Review"] = Relationship(back_populates="template")


# 10. Review
class Review(SQLModel, table=True):
    """Single reviewer assessment event triggered by evaluating one snippet."""

    __tablename__ = "reviews"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    proposal_snippet_id: UUID = Field(
        foreign_key="proposal_snippets.id",
        description="Evaluated text source",
    )
    prompt_template_id: UUID = Field(
        foreign_key="prompt_templates.id",
        description="Prompt version used",
    )
    status: ReviewStatus = Field(
        default=ReviewStatus.PENDING,
        description="Current workflow state",
    )
    overall_summary: str | None = Field(
        default=None,
        description="Aggregated markdown assessment",
    )
    overall_rating: ReviewRating | None = Field(
        default=None,
        description="Most severe rating among review cards",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    snippet: ProposalSnippet | None = Relationship(back_populates="review")
    template: PromptTemplate | None = Relationship(back_populates="reviews")
    cards: list["ReviewCard"] = Relationship(back_populates="review")


# 11. ReviewCard
class ReviewCard(SQLModel, table=True):
    """Individual structured reviewer comment for a specific expectation."""

    __tablename__ = "review_cards"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    review_id: UUID = Field(foreign_key="reviews.id", description="Owning review event")
    node_expectation_id: UUID = Field(
        foreign_key="node_expectations.id",
        description="Rubric requirement evaluated",
    )
    rating: ReviewRating = Field(
        description="Computed severity (e.g., SUCCESS, CRITICAL)",
    )
    feedback_text: str = Field(description="Markdown content of the AI assessment")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    review: Review | None = Relationship(back_populates="cards")
    expectation: NodeExpectation | None = Relationship(back_populates="review_cards")
