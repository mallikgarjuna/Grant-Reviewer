"""API tests for public node metadata contract."""

import main as main_module

from tests.test_api import create_client_with_seed


def test_call_nodes_metadata_missing_definition_returns_409(monkeypatch) -> None:
    """Calls without canonical definitions should return explicit 409."""
    client, _ = create_client_with_seed(monkeypatch)

    response = client.get("/api/public/calls/ERC-2026-COG/nodes/metadata")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CALL_DEFINITION_MISSING"


def test_call_nodes_metadata_bulk_success(monkeypatch) -> None:
    """Structured call should return metadata DTOs for all canonical nodes."""
    client, seeded_ids = create_client_with_seed(monkeypatch)

    response = client.get(
        f"/api/public/calls/{seeded_ids.structured_call_code}/nodes/metadata"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["call_logical_id"] == seeded_ids.structured_call_code
    assert isinstance(payload["nodes"], list)
    assert payload["nodes"]
    first = payload["nodes"][0]
    assert "logical_id" in first
    assert "node_id" in first
    assert "label" in first
    assert "node_type" in first
    assert "parent_logical_id" in first
    assert "guidance_text" in first
    assert "content_constraints" in first
    assert "compliance_rules" in first
    assert "source_section" in first


def test_call_nodes_metadata_filter_returns_unknowns(monkeypatch) -> None:
    """Filter should return known subset and explicit unknown logical IDs."""
    client, seeded_ids = create_client_with_seed(monkeypatch)

    response = client.get(
        f"/api/public/calls/{seeded_ids.structured_call_code}/nodes/metadata",
        params=[
            ("node_logical_ids", "academic_profile"),
            ("node_logical_ids", "unknown_node"),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert [node["logical_id"] for node in payload["nodes"]] == ["academic_profile"]
    assert payload["unknown_node_logical_ids"] == ["unknown_node"]


def test_call_nodes_metadata_route_delegates_to_service(monkeypatch) -> None:
    """Route should delegate projection logic to NodeMetadataService."""
    client, seeded_ids = create_client_with_seed(monkeypatch)

    class FakeNodeMetadataService:
        def build_metadata_response(self, *, call, definition, node_logical_ids, repository):
            assert call.code == seeded_ids.structured_call_code
            assert definition is not None
            return {
                "call_logical_id": call.code,
                "config_version": "v2",
                "nodes": [
                    {
                        "logical_id": "sentinel_node",
                        "node_id": None,
                        "label": None,
                        "node_type": None,
                        "parent_logical_id": None,
                        "guidance_text": None,
                        "content_constraints": {},
                        "compliance_rules": [],
                        "source_section": None,
                    }
                ],
                "unknown_node_logical_ids": None,
            }

    monkeypatch.setattr(main_module, "NodeMetadataService", FakeNodeMetadataService)

    response = client.get(
        f"/api/public/calls/{seeded_ids.structured_call_code}/nodes/metadata"
    )

    assert response.status_code == 200
    assert response.json()["nodes"][0]["logical_id"] == "sentinel_node"
