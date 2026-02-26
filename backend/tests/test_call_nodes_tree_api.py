"""API tests for call nodes flat/tree response contracts."""

from fastapi.testclient import TestClient

from app.db import get_session
from app.models.domain import NodeType, ProposalNode
from tests.test_api import SeededIDs, create_client_with_seed


def _seed_child_node(seeded_ids: SeededIDs) -> None:
    """Attach one child node to create a nested tree shape for assertions."""
    session = get_session()
    try:
        child = ProposalNode(
            funding_call_id=seeded_ids.call_id,
            parent_node_id=seeded_ids.section_with_expectations_id,
            logical_id="section_1_child",
            node_type=NodeType.SUBSECTION,
            title="Section 1.1",
            order_index=10,
        )
        session.add(child)
        session.commit()
    finally:
        session.close()


def _get_call_nodes_tree(client: TestClient, call_id: str) -> dict:
    response = client.get(f"/calls/{call_id}/nodes?view=tree")
    assert response.status_code == 200
    return response.json()


def test_call_nodes_view_tree_returns_nested_children(monkeypatch) -> None:
    """`view=tree` should return roots with nested children arrays."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    _seed_child_node(seeded_ids)

    payload = _get_call_nodes_tree(client, str(seeded_ids.call_id))

    roots = payload["nodes"]
    assert roots
    root_ids = {root["id"] for root in roots}
    assert str(seeded_ids.section_with_expectations_id) in root_ids
    section_1 = next(
        item
        for item in roots
        if item["id"] == str(seeded_ids.section_with_expectations_id)
    )
    assert section_1["children"]
    assert section_1["children"][0]["title"] == "Section 1.1"
    assert section_1["children"][0]["children"] == []


def test_call_nodes_flat_includes_logical_id_field(monkeypatch) -> None:
    """Flat response keeps compatibility and includes additive logical_id."""
    client, seeded_ids = create_client_with_seed(monkeypatch)
    response = client.get(f"/calls/{seeded_ids.call_id}/nodes")
    assert response.status_code == 200
    nodes = response.json()["nodes"]
    assert nodes
    assert "logical_id" in nodes[0]
