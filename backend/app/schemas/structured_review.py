"""Pydantic models for structured review request contracts."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

MAX_NODE_TEXT_CHARS = 10_000
MAX_STRUCTURED_PAYLOAD_CHARS = 30_000


class StructuredReviewNodeInput(BaseModel):
    """Single node payload for structured review."""

    node_logical_id: str = Field(min_length=1)
    text: str


class StructuredReviewRequest(BaseModel):
    """Input contract for POST /api/structured-review."""

    review_stage: Literal["STEP_1", "STEP_2"]
    call_id: UUID
    nodes: list[StructuredReviewNodeInput] = Field(default_factory=list)
