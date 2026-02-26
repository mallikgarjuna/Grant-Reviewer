"""Projection service for public node metadata DTO responses."""

from __future__ import annotations

from typing import Any

from app.models.domain import CallDefinition, FundingCall
from app.repositories.review_repository import ReviewRepository
from app.schemas.api import NodeMetadataDTO, NodeMetadataResponse


class NodeMetadataService:
    """Build metadata DTO responses from canonical JSON + active node projection."""

    def build_metadata_response(
        self,
        *,
        call: FundingCall,
        definition: CallDefinition,
        node_logical_ids: list[str] | None,
        repository: ReviewRepository,
    ) -> NodeMetadataResponse:
        """Build response payload for `/api/public/calls/{call_logical_id}/nodes/metadata`."""
        proposal_nodes = definition.canonical_json.get("proposal_nodes")
        if not isinstance(proposal_nodes, list):
            proposal_nodes = []

        active_nodes = repository.get_nodes_for_call(call.id)
        node_id_by_logical_id = {
            node.logical_id: node.id
            for node, _ in active_nodes
            if isinstance(node.logical_id, str) and node.logical_id
        }

        metadata_nodes: list[NodeMetadataDTO] = []
        for item in proposal_nodes:
            if not isinstance(item, dict):
                continue
            logical_id = item.get("id")
            if not isinstance(logical_id, str) or not logical_id.strip():
                continue
            compliance_rules = item.get("compliance_rules")
            if not isinstance(compliance_rules, list):
                compliance_rules = []

            metadata_nodes.append(
                NodeMetadataDTO(
                    logical_id=logical_id,
                    node_id=node_id_by_logical_id.get(logical_id),
                    label=item.get("label") if isinstance(item.get("label"), str) else None,
                    node_type=(
                        item.get("node_type")
                        if isinstance(item.get("node_type"), str)
                        else None
                    ),
                    parent_logical_id=(
                        item.get("parent_logical_id")
                        if isinstance(item.get("parent_logical_id"), str)
                        else None
                    ),
                    guidance_text=(
                        item.get("guidance_text")
                        if isinstance(item.get("guidance_text"), str)
                        else None
                    ),
                    content_constraints=(
                        item.get("content_constraints")
                        if isinstance(item.get("content_constraints"), dict)
                        else {}
                    ),
                    compliance_rules=[
                        rule for rule in compliance_rules if isinstance(rule, dict)
                    ],
                    source_section=(
                        item.get("source_section")
                        if isinstance(item.get("source_section"), str)
                        else None
                    ),
                )
            )

        unknown_node_logical_ids: list[str] | None = None
        if node_logical_ids:
            requested_ids: list[str] = []
            for node_logical_id in node_logical_ids:
                normalized = node_logical_id.strip()
                if not normalized:
                    continue
                if normalized not in requested_ids:
                    requested_ids.append(normalized)

            metadata_by_logical_id = {node.logical_id: node for node in metadata_nodes}
            metadata_nodes = [
                metadata_by_logical_id[node_logical_id]
                for node_logical_id in requested_ids
                if node_logical_id in metadata_by_logical_id
            ]
            unknown_node_logical_ids = sorted(
                [
                    node_logical_id
                    for node_logical_id in requested_ids
                    if node_logical_id not in metadata_by_logical_id
                ]
            )
            if not unknown_node_logical_ids:
                unknown_node_logical_ids = None

        return NodeMetadataResponse(
            call_logical_id=call.code,
            config_version=definition.schema_version,
            nodes=metadata_nodes,
            unknown_node_logical_ids=unknown_node_logical_ids,
        )
