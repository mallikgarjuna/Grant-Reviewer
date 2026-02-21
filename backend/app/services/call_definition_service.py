"""Call definition hydration service.

Loads active projection rows and enriches them with canonical JSON configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.models.domain import CallDefinition, ProposalNode


@dataclass(frozen=True)
class HydratedNode:
    """Projection node plus merged configuration from canonical JSON."""

    node: ProposalNode
    config: dict[str, Any]


class CallDefinitionService:
    """Service for single-read hydration of active proposal nodes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_hydrated_nodes(self, call_id: UUID) -> list[HydratedNode]:
        """Load active nodes and merge node-level config by logical_id."""
        nodes = list(
            self.session.exec(
                select(ProposalNode)
                .where(ProposalNode.funding_call_id == call_id)
                .where(ProposalNode.archived_at.is_(None))
                .order_by(ProposalNode.order_index)
            ).all()
        )

        definition = self.session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        ).first()
        if definition is None:
            return [HydratedNode(node=node, config={}) for node in nodes]

        proposal_nodes = definition.canonical_json.get("proposal_nodes", [])
        if not isinstance(proposal_nodes, list):
            proposal_nodes = []

        config_by_logical_id: dict[str, dict[str, Any]] = {}
        for item in proposal_nodes:
            if not isinstance(item, dict):
                continue
            logical_id = item.get("id")
            if not isinstance(logical_id, str):
                continue
            config_by_logical_id[logical_id] = {
                "content_constraints": item.get("content_constraints") or {},
                "compliance_rules": item.get("compliance_rules") or [],
                "source_section": item.get("source_section"),
            }

        return [
            HydratedNode(
                node=node,
                config=config_by_logical_id.get(node.logical_id or "", {}),
            )
            for node in nodes
        ]
