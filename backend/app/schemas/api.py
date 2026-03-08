"""backend/app/schemas/api.py
Pydantic models for FastAPI request/response contracts.
"""

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.domain import NodeType, ReviewRating, ReviewStatus


class APIErrorBody(BaseModel):
    """Canonical error payload details."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class APIErrorResponse(BaseModel):
    """Canonical non-2xx response shape."""

    error: APIErrorBody


class CallSummary(BaseModel):
    """Funding call summary for call picker UIs."""

    id: UUID
    code: str
    name: str
    year: int
    agency_short_name: str


class CallsResponse(BaseModel):
    """Response for GET /calls."""

    calls: list[CallSummary]


class NodeSummary(BaseModel):
    """Proposal node summary for section picker UIs."""

    id: UUID
    logical_id: str | None = None
    parent_node_id: UUID | None
    title: str
    node_type: NodeType
    order_index: int
    has_expectations: bool
    node_role: Literal["PRIMARY", "SUPPORTING"] | None = None


class NodesResponse(BaseModel):
    """Response for GET /calls/{call_id}/nodes."""

    nodes: list[NodeSummary]


class NodeTreeNode(BaseModel):
    """Tree node shape for nested proposal-node responses."""

    id: UUID
    logical_id: str | None = None
    parent_node_id: UUID | None
    title: str
    node_type: NodeType
    order_index: int
    has_expectations: bool
    node_role: Literal["PRIMARY", "SUPPORTING"] | None = None
    children: list["NodeTreeNode"] = Field(default_factory=list)


NodeTreeNode.model_rebuild()


class NodesTreeResponse(BaseModel):
    """Response for GET /calls/{call_id}/nodes?view=tree."""

    nodes: list[NodeTreeNode]


class NodeMetadataDTO(BaseModel):
    """UI-oriented metadata for one proposal node."""

    logical_id: str
    node_id: UUID | None = None
    label: str | None = None
    node_type: str | None = None
    parent_logical_id: str | None = None
    guidance_text: str | None = None
    review_stage: Literal["STEP_1", "STEP_2", "BOTH"] | None = None
    content_constraints: dict[str, Any] = Field(default_factory=dict)
    compliance_rules: list[dict[str, Any]] = Field(default_factory=list)
    source_section: str | None = None


class NodeMetadataResponse(BaseModel):
    """Response for GET /api/public/calls/{call_logical_id}/nodes/metadata."""

    call_logical_id: str
    config_version: str
    nodes: list[NodeMetadataDTO]
    unknown_node_logical_ids: list[str] | None = None


class DomainOptionDTO(BaseModel):
    """Backend-defined domain option for submit UX."""

    value: str
    label: str
    order_index: int


class CallConfigResponse(BaseModel):
    """Response for GET /api/public/calls/{call_logical_id}/config."""

    call_logical_id: str
    config_version: str
    ui_mode: Literal["legacy_single_snippet", "structured_nodes"]
    expected_nodes: list[str] | None = None
    domain_options: list[DomainOptionDTO] = Field(default_factory=list)
    split_visibility_reviewability_enabled: bool = False


class CreateReviewRequest(BaseModel):
    """Request payload for POST /reviews."""

    review_stage: Literal["STEP_1", "STEP_2"]
    call_id: UUID
    node_id: UUID
    snippet_text: str = Field(min_length=1)


class CreateReviewResponse(BaseModel):
    """Success payload for POST /reviews."""

    review_id: UUID
    status: ReviewStatus


class ReviewSummary(BaseModel):
    """Review metadata exposed to API consumers."""

    id: UUID
    status: ReviewStatus
    overall_rating: ReviewRating | None
    overall_summary: str | None


class ReviewCardSummary(BaseModel):
    """Review card payload exposed to API consumers."""

    id: UUID
    node_expectation_id: UUID
    node_logical_id: str | None
    node_title: str
    criterion: str
    criterion_description: str | None
    evaluation_element_name: str
    expectation_guidance_note: str | None
    rating: ReviewRating
    feedback_text: str
    assessment_status: str | None = None
    not_assessable_reason: str | None = None
    source_basis_label: str | None = None
    source_basis_state: Literal["available", "unavailable", "legacy_fallback"]


class ReviewCompatibilityNote(BaseModel):
    """Compatibility annotation for mixed-version review records."""

    note_type: Literal[
        "deprecated_container_submission",
        "moved_legacy_node_reference",
        "mixed_version_review",
    ]
    node_logical_ids: list[str] = Field(default_factory=list)
    message: str


class ReviewDetailResponse(BaseModel):
    """Response for GET /reviews/{review_id}."""

    call_id: UUID | None = None
    call_code: str | None = None
    submitted_node_logical_ids: list[str] = Field(default_factory=list)
    detail_state: Literal[
        "call_linked",
        "legacy_fallback",
        "proof_path_unmapped",
    ] = "call_linked"
    ordering_source: Literal["call_nodes", "review_payload_fallback"] = "call_nodes"
    unmapped_node_logical_ids: list[str] = Field(default_factory=list)
    submitted_leaf_ids: list[str] = Field(default_factory=list)
    primary_evaluated_node_logical_ids: list[str] = Field(default_factory=list)
    supporting_context_node_logical_ids: list[str] = Field(default_factory=list)
    legacy_ambiguous_container_ids: list[str] = Field(default_factory=list)
    moved_legacy_node_references: list[str] = Field(default_factory=list)
    compatibility_notes: list[ReviewCompatibilityNote] = Field(default_factory=list)
    review: ReviewSummary
    cards: list[ReviewCardSummary]


class DeleteReviewResponse(BaseModel):
    """Success payload for DELETE /reviews/{review_id}."""

    ok: bool


class ReviewListItem(BaseModel):
    """Single review entry for the reviews list page."""

    id: UUID
    status: ReviewStatus
    overall_rating: ReviewRating | None
    created_at: str
    call_name: str
    node_title: str


class ReviewsListResponse(BaseModel):
    """Response for GET /reviews."""

    reviews: list[ReviewListItem]
