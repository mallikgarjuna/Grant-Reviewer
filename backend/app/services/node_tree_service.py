"""Tree construction service for proposal nodes."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.schemas.api import NodeSummary, NodeTreeNode


class NodeTreeMismatchError(ValueError):
    """Raised when canonical tree references cannot map to active DB nodes."""

    def __init__(self, *, node_logical_ids: list[str]) -> None:
        self.node_logical_ids = node_logical_ids
        super().__init__("Canonical tree references unknown or invalid node logical IDs.")


class NodeTreeCycleError(ValueError):
    """Raised when canonical parent graph contains a cycle."""


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

        nodes_by_logical_id: dict[str, NodeSummary] = {}
        duplicate_db_ids: set[str] = set()
        for node in flat_nodes:
            logical_id = node.logical_id
            if not isinstance(logical_id, str) or not logical_id:
                continue
            if logical_id in nodes_by_logical_id:
                duplicate_db_ids.add(logical_id)
                continue
            nodes_by_logical_id[logical_id] = node

        if not nodes_by_logical_id:
            return None

        if duplicate_db_ids:
            raise NodeTreeMismatchError(node_logical_ids=sorted(duplicate_db_ids))

        canonical_ids = [logical_id for logical_id, _ in canonical_entries]
        duplicate_canonical_ids = {
            logical_id for logical_id in canonical_ids if canonical_ids.count(logical_id) > 1
        }
        if duplicate_canonical_ids:
            raise NodeTreeMismatchError(node_logical_ids=sorted(duplicate_canonical_ids))

        missing_ids = sorted(
            logical_id for logical_id in canonical_ids if logical_id not in nodes_by_logical_id
        )
        if missing_ids:
            raise NodeTreeMismatchError(node_logical_ids=missing_ids)

        canonical_id_set = set(canonical_ids)
        unknown_parent_ids = sorted(
            parent_logical_id
            for _, parent_logical_id in canonical_entries
            if parent_logical_id is not None and parent_logical_id not in canonical_id_set
        )
        if unknown_parent_ids:
            raise NodeTreeMismatchError(node_logical_ids=unknown_parent_ids)

        parent_by_node = {logical_id: parent for logical_id, parent in canonical_entries}
        self._assert_acyclic(parent_by_node)

        children_by_parent: dict[str | None, list[NodeSummary]] = defaultdict(list)
        for logical_id, parent_logical_id in canonical_entries:
            resolved_node = nodes_by_logical_id.get(logical_id)
            if resolved_node is None:
                raise NodeTreeMismatchError(node_logical_ids=[logical_id])
            children_by_parent[parent_logical_id].append(resolved_node)

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
                    node_role=child.node_role,
                    children=build_subtree(child.logical_id),
                )
                for child in children
            ]

        return build_subtree(parent_logical_id=None)

    def _assert_acyclic(self, parent_by_node: dict[str, str | None]) -> None:
        """Raise when any canonical parent chain loops back to a seen logical ID."""
        for logical_id in parent_by_node:
            seen: set[str] = set()
            current: str | None = logical_id
            while current is not None:
                if current in seen:
                    raise NodeTreeCycleError("Canonical parent_logical_id cycle detected.")
                seen.add(current)
                current = parent_by_node.get(current)
