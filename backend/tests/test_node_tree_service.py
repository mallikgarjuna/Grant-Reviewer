"""Unit tests for canonical tree construction service."""

from uuid import uuid4

from app.models.domain import NodeType
from app.schemas.api import NodeSummary
from app.services.node_tree_service import NodeTreeService


def test_build_tree_from_parent_logical_id_orders_siblings_by_definition_order() -> None:
    """Canonical proposal_nodes order drives sibling order in tree output."""
    flat_nodes = [
        NodeSummary(
            id=uuid4(),
            logical_id="academic_profile",
            parent_node_id=None,
            title="Academic profile",
            node_type=NodeType.SECTION,
            order_index=1,
            has_expectations=True,
        ),
        NodeSummary(
            id=uuid4(),
            logical_id="knowledge_utilisation",
            parent_node_id=None,
            title="Knowledge utilisation",
            node_type=NodeType.SECTION,
            order_index=2,
            has_expectations=True,
        ),
        NodeSummary(
            id=uuid4(),
            logical_id="scientific_proposal",
            parent_node_id=None,
            title="Scientific proposal",
            node_type=NodeType.SECTION,
            order_index=3,
            has_expectations=True,
        ),
    ]
    canonical_json = {
        "proposal_nodes": [
            {"id": "knowledge_utilisation"},
            {"id": "scientific_proposal", "parent_logical_id": "knowledge_utilisation"},
            {"id": "academic_profile", "parent_logical_id": "knowledge_utilisation"},
        ]
    }

    tree = NodeTreeService().build_tree_from_canonical(canonical_json, flat_nodes)

    assert tree is not None
    assert len(tree) == 1
    assert tree[0].logical_id == "knowledge_utilisation"
    assert [child.logical_id for child in tree[0].children] == [
        "scientific_proposal",
        "academic_profile",
    ]
