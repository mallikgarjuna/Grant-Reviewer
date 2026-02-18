"""Pydantic models for FastAPI request/response contracts."""

from typing import Any
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
    parent_node_id: UUID | None
    title: str
    node_type: NodeType
    order_index: int
    has_expectations: bool


class NodesResponse(BaseModel):
    """Response for GET /calls/{call_id}/nodes."""

    nodes: list[NodeSummary]


class CreateReviewRequest(BaseModel):
    """Request payload for POST /reviews."""

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
    criterion: str
    criterion_description: str | None
    rating: ReviewRating
    feedback_text: str


class ReviewDetailResponse(BaseModel):
    """Response for GET /reviews/{review_id}."""

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
