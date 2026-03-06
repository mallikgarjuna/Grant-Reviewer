"""Pydantic models for structured review request contracts."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

MAX_NODE_TEXT_CHARS = 10_000
MAX_STRUCTURED_PAYLOAD_CHARS = 30_000


class StructuredReviewNodeInput(BaseModel):
    """Single node payload for structured review."""

    model_config = ConfigDict(extra="forbid")

    node_logical_id: str = Field(min_length=1)
    text: str


class StructuredReviewHierarchicalNodeInput(BaseModel):
    """Recursive node payload accepted at the request boundary."""

    model_config = ConfigDict(extra="forbid")

    node_logical_id: str = Field(min_length=1)
    text: str
    children: list["StructuredReviewHierarchicalNodeInput"] = Field(default_factory=list)


StructuredReviewHierarchicalNodeInput.model_rebuild()


def _flatten_structured_nodes(
    raw_nodes: Any,
) -> list[StructuredReviewNodeInput]:
    typed_nodes = TypeAdapter(list[StructuredReviewHierarchicalNodeInput]).validate_python(
        raw_nodes
    )
    flattened_nodes: list[StructuredReviewNodeInput] = []

    def visit(node: StructuredReviewHierarchicalNodeInput) -> None:
        flattened_nodes.append(
            StructuredReviewNodeInput(
                node_logical_id=node.node_logical_id,
                text=node.text,
            )
        )
        for child in node.children:
            visit(child)

    for typed_node in typed_nodes:
        visit(typed_node)

    return flattened_nodes


class StructuredReviewRequest(BaseModel):
    """Input contract for POST /api/structured-review."""

    review_stage: Literal["STEP_1", "STEP_2"]
    call_id: UUID
    nodes: list[StructuredReviewNodeInput] = Field(default_factory=list)

    @field_validator("nodes", mode="before")
    @classmethod
    def flatten_hierarchical_nodes(
        cls,
        value: Any,
    ) -> list[StructuredReviewNodeInput]:
        return _flatten_structured_nodes(value)
