"""Pydantic models for deterministic compliance checking contracts."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ViolationSeverity = Literal["ERROR", "WARNING"]


class DraftNode(BaseModel):
    """Single node payload provided by the caller for compliance evaluation."""

    node_logical_id: str = Field(min_length=1)
    text: str


class ComplianceViolation(BaseModel):
    """Structured compliance finding for one node/rule pair."""

    node_logical_id: str = Field(min_length=1)
    rule_id: str = Field(min_length=1)
    severity: ViolationSeverity
    actual: str
    expected: str
    message: str
    is_blocking: bool


class ComplianceCheckRequest(BaseModel):
    """Input contract for POST /api/check-compliance."""

    call_id: UUID
    domain: str | None = None
    draft_nodes: list[DraftNode] = Field(default_factory=list)


class ComplianceCheckResponse(BaseModel):
    """Output contract for deterministic compliance checks."""

    is_compliant: bool
    errors: list[ComplianceViolation] = Field(default_factory=list)
    warnings: list[ComplianceViolation] = Field(default_factory=list)
