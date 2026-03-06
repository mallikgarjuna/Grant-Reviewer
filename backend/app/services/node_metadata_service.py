"""backend/app/services/node_metadata_service.py
Projection service for public node metadata DTO responses.
"""

from __future__ import annotations

from typing import Any, cast

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
        element_stage_by_id = self._build_element_stage_map(definition.canonical_json)

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
                    review_stage=self._resolve_node_review_stage(
                        node_item=item,
                        element_stage_by_id=element_stage_by_id,
                    ),
                    content_constraints=(
                        cast(dict[str, Any], item.get("content_constraints"))
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

    def _build_element_stage_map(self, canonical_json: dict[str, Any]) -> dict[str, str]:
        """Index evaluation element stage by logical id."""
        raw_criteria = canonical_json.get("evaluation_criteria")
        if not isinstance(raw_criteria, list):
            return {}

        stage_by_id: dict[str, str] = {}
        for criterion in raw_criteria:
            if not isinstance(criterion, dict):
                continue
            raw_elements = criterion.get("evaluation_elements")
            if not isinstance(raw_elements, list):
                continue
            for element in raw_elements:
                if not isinstance(element, dict):
                    continue
                element_id = element.get("id")
                if not isinstance(element_id, str) or not element_id.strip():
                    continue
                stage = element.get("stage")
                if stage in {"STEP_1", "STEP_2", "BOTH"}:
                    stage_by_id[element_id] = stage
                else:
                    stage_by_id[element_id] = "BOTH"
        return stage_by_id

    def _resolve_node_review_stage(
        self,
        *,
        node_item: dict[str, Any],
        element_stage_by_id: dict[str, str],
    ) -> str | None:
        """Resolve node review-stage from linked expectation element stages."""
        raw_expectations = node_item.get("node_expectations")
        if not isinstance(raw_expectations, list) or len(raw_expectations) == 0:
            return None

        stages: set[str] = set()
        for expectation in raw_expectations:
            if not isinstance(expectation, dict):
                continue
            element_id = expectation.get("evaluation_element_id")
            if not isinstance(element_id, str) or not element_id.strip():
                continue
            stages.add(element_stage_by_id.get(element_id, "BOTH"))

        if not stages:
            return None
        if stages == {"STEP_2"}:
            return "STEP_2"
        if stages == {"STEP_1"}:
            return "STEP_1"
        return "BOTH"
