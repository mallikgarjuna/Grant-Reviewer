"""Tree construction service for proposal nodes."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.schemas.api import NodeSummary, NodeTreeNode


class NodeTreeService:
    """Build nested node trees from canonical V2 call-definition content."""

    def build_tree_from_canonical(
        self,
        canonical_json: dict[str, Any],
        flat_nodes: list[NodeSummary],
    ) -> list[NodeTreeNode] | None:
        """Build tree from `proposal_nodes` + `parent_logical_id` if available."""
        proposal_nodes = canonical_json.get("proposal_nodes")
        if not isinstance(proposal_nodes, list):
            return None

        canonical_entries: list[tuple[str, str | None]] = []
        for item in proposal_nodes:
            if not isinstance(item, dict):
                continue
            logical_id = item.get("id")
            if not isinstance(logical_id, str) or not logical_id.strip():
                continue
            parent_logical_id = item.get("parent_logical_id")
            if not isinstance(parent_logical_id, str):
                parent_logical_id = None
            canonical_entries.append((logical_id, parent_logical_id))

        if not canonical_entries:
            return None

        nodes_by_logical_id = {
            node.logical_id: node
            for node in flat_nodes
            if isinstance(node.logical_id, str) and node.logical_id
        }

        if not nodes_by_logical_id:
            return None

        children_by_parent: dict[str | None, list[NodeSummary]] = defaultdict(list)
        for logical_id, parent_logical_id in canonical_entries:
            node = nodes_by_logical_id.get(logical_id)
            if node is None:
                continue
            children_by_parent[parent_logical_id].append(node)

        if not children_by_parent:
            return None

        def build_subtree(parent_logical_id: str | None) -> list[NodeTreeNode]:
            children = children_by_parent.get(parent_logical_id, [])
            return [
                NodeTreeNode(
                    id=child.id,
                    logical_id=child.logical_id,
                    parent_node_id=child.parent_node_id,
                    title=child.title,
                    node_type=child.node_type,
                    order_index=child.order_index,
                    has_expectations=child.has_expectations,
                    children=build_subtree(child.logical_id),
                )
                for child in children
            ]

        return build_subtree(parent_logical_id=None)
