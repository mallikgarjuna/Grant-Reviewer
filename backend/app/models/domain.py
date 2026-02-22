"""
Domain models for Grant Reviewer MVP.

11 SQLModel tables following the finalized schema from Stage 1.
"""

import enum
from datetime import UTC, datetime, timedelta
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
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


class AssessmentStatus(enum.StrEnum):
    ASSESSED = "ASSESSED"
    NOT_ASSESSABLE = "NOT_ASSESSABLE"


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
    call_definition: Optional["CallDefinition"] = Relationship(back_populates="call")
    nodes: list["ProposalNode"] = Relationship(back_populates="call")
    criteria: list["EvaluationCriterion"] = Relationship(back_populates="call")


# 3. CallDefinition
class CallDefinition(SQLModel, table=True):
    """Canonical source document (YAML/JSON) for a single funding call."""

    __tablename__ = "call_definitions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_call_id: UUID = Field(
        foreign_key="funding_calls.id",
        unique=True,
        description="Owning call (1:1 with FundingCall)",
    )
    schema_version: str = Field(description="Version of call-definition schema")
    checksum: str = Field(
        description="Deterministic semantic checksum of canonical JSON"
    )
    raw_yaml: str | None = Field(
        default=None,
        description="Original YAML payload as ingested",
    )
    canonical_json: dict[str, Any] = Field(
        sa_column=Column(
            JSON().with_variant(JSONB, "postgresql"),
            nullable=False,
        ),
        description="Canonical parsed representation of call definition",
    )
    source_path: str = Field(description="Source path used during ingestion")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    call: FundingCall | None = Relationship(back_populates="call_definition")


# 4. ProposalNode
class ProposalNode(SQLModel, table=True):
    """Structural section or subsection of a proposal for anchoring reviews."""

    __tablename__ = "proposal_nodes"

    __table_args__ = (
        UniqueConstraint(
            "funding_call_id",
            "logical_id",
            name="uq_proposal_nodes_call_logical_id",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_call_id: UUID = Field(
        foreign_key="funding_calls.id",
        description="Owning call",
    )
    logical_id: str | None = Field(
        default=None,
        description="Stable logical identifier from call definition",
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
    archived_at: datetime | None = Field(
        default=None,
        description="Soft-delete timestamp; NULL means active",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    call: FundingCall | None = Relationship(back_populates="nodes")
    expectations: list["NodeExpectation"] = Relationship(back_populates="node")


# 5. EvaluationCriterion
class EvaluationCriterion(SQLModel, table=True):
    """Top-level assessment dimension (e.g., Excellence, Impact) for a call."""

    __tablename__ = "evaluation_criteria"

    __table_args__ = (
        UniqueConstraint(
            "funding_call_id",
            "logical_id",
            name="uq_evaluation_criteria_call_logical_id",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    funding_call_id: UUID = Field(
        foreign_key="funding_calls.id",
        description="Owning call",
    )
    logical_id: str | None = Field(
        default=None,
        description="Stable logical identifier from call definition",
    )
    name: str = Field(description="Name of the assessment dimension")
    description: str | None = Field(
        default=None,
        description="Brief explanation of the criterion",
    )
    order_index: int = Field(default=0, description="Display order for the rubric")
    archived_at: datetime | None = Field(
        default=None,
        description="Soft-delete timestamp; NULL means active",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    call: FundingCall | None = Relationship(back_populates="criteria")
    elements: list["EvaluationElement"] = Relationship(back_populates="criterion")


# 6. EvaluationElement
class EvaluationElement(SQLModel, table=True):
    """Atomic reviewable concern explicitly evaluated within a criterion."""

    __tablename__ = "evaluation_elements"

    __table_args__ = (
        UniqueConstraint(
            "evaluation_criterion_id",
            "logical_id",
            name="uq_evaluation_elements_criterion_logical_id",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    evaluation_criterion_id: UUID = Field(
        foreign_key="evaluation_criteria.id",
        description="Owning criterion",
    )
    logical_id: str | None = Field(
        default=None,
        description="Stable logical identifier from call definition",
    )
    name: str = Field(description="Name of the specific reviewable concern")
    description: str | None = Field(
        default=None,
        description="What the element explicitly evaluates",
    )
    archived_at: datetime | None = Field(
        default=None,
        description="Soft-delete timestamp; NULL means active",
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
    __table_args__ = (
        UniqueConstraint(
            "external_user_id",
            "idempotency_key",
            name="uq_review_external_idempotency",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    proposal_snippet_id: UUID | None = Field(
        default=None,
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
    # LLM traceability fields (Task 6.0)
    prompt_sent: str | None = Field(
        default=None,
        description="Full prompt sent to LLM for debugging",
    )
    raw_llm_response: str | None = Field(
        default=None,
        description="Raw LLM response before parsing",
    )
    llm_model: str | None = Field(
        default=None,
        description="Model identifier used (e.g., gpt-4o-mini)",
    )
    external_user_id: str | None = Field(
        default=None,
        index=True,
        description="External auth identifier used for ownership checks",
    )
    idempotency_key: str | None = Field(
        default=None,
        description="Client-provided key to deduplicate retries",
    )
    request_payload_sha256: str | None = Field(
        default=None,
        description="Hash of canonical request payload used for mismatch checks",
    )
    idempotency_expires_at: datetime | None = Field(
        default=None,
        description="Expiry timestamp after which the idempotency key can be reused",
    )
    review_type: str = Field(
        default="single",
        description="Review type: single or structured",
    )
    structured_payload: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(
            JSON().with_variant(JSONB, "postgresql"),
            nullable=True,
        ),
        description="Raw structured submission payload for multi-node reviews",
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
    assessment_status: AssessmentStatus = Field(
        default=AssessmentStatus.ASSESSED,
        description="Whether this card was assessed by the LLM or marked not assessable",
    )
    not_assessable_reason: str | None = Field(
        default=None,
        description="Reason for NOT_ASSESSABLE cards",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    review: Review | None = Relationship(back_populates="cards")
    expectation: NodeExpectation | None = Relationship(back_populates="review_cards")
