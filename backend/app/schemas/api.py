"""backend/app/schemas/api.py
Pydantic models for FastAPI request/response contracts.
"""

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.domain import NodeType, ReviewDetailMode, ReviewRating, ReviewStatus


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
    support_trace: "SupportTraceMetadata | None" = None


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
    synthesized_companion_text: str | None = None
    assessment_status: str | None = None
    not_assessable_reason: str | None = None
    source_basis_label: str | None = None
    source_basis_state: Literal["available", "unavailable", "legacy_fallback"]


class ReviewFindingSummary(BaseModel):
    """Atomic review finding payload exposed to API consumers."""

    finding_id: UUID
    evaluation_criterion: str
    evaluation_element: str
    severity: ReviewRating
    assessment_status: str
    issue_summary: str
    evidence_basis: str
    actionable_feedback: str


class ReviewedNodeSummary(BaseModel):
    """Grouped reviewed-node payload for atomic findings reviews."""

    proposal_node_id: UUID
    proposal_node_logical_id: str
    proposal_node_title: str
    node_role: Literal["PRIMARY", "SUPPORTING"] | None = None
    findings: list[ReviewFindingSummary] = Field(default_factory=list)


class ReviewCompatibilityNote(BaseModel):
    """Compatibility annotation for mixed-version review records."""

    note_type: Literal[
        "deprecated_container_submission",
        "moved_legacy_node_reference",
        "mixed_version_review",
    ]
    node_logical_ids: list[str] = Field(default_factory=list)
    message: str


class SupportTraceMetadata(BaseModel):
    """Minimal maintainer-only trace contract for WF-0080 supportability."""

    contract: Literal["wf0080_support_trace_v1"]
    trace_id: str
    visibility: Literal["maintainer_support_only"]


class ReviewDetailProjection(BaseModel):
    """Bounded launch-wedge projection for action-first review detail UX."""

    version: Literal["wf0080_launch_wedge_v1"]
    headline_state: Literal["action_required", "no_critical_blockers"]
    ordered_card_ids: list[UUID] = Field(default_factory=list)
    top_action_card_ids: list[UUID] = Field(default_factory=list)
    ranking_basis: Literal["assessment_status_then_rating_then_existing_order"]


class ReviewDetailResponse(BaseModel):
    """Response for GET /reviews/{review_id}."""

    detail_mode: ReviewDetailMode
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
    visible_not_reviewed_node_logical_ids: list[str] = Field(default_factory=list)
    out_of_scope_node_logical_ids: list[str] = Field(default_factory=list)
    no_generated_cards_node_logical_ids: list[str] = Field(default_factory=list)
    legacy_ambiguous_container_ids: list[str] = Field(default_factory=list)
    moved_legacy_node_references: list[str] = Field(default_factory=list)
    compatibility_notes: list[ReviewCompatibilityNote] = Field(default_factory=list)
    detail_projection: ReviewDetailProjection | None = None
    support_trace: SupportTraceMetadata | None = None
    review: ReviewSummary
    cards: list[ReviewCardSummary] | None = None
    reviewed_nodes: list[ReviewedNodeSummary] | None = None


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
