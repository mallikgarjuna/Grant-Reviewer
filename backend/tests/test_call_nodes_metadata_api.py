"""backend/tests/test_call_nodes_metadata_api.py
API tests for public node metadata contract.
"""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import select

import main as main_module
from app.db import get_session
from app.models.domain import FundingCall
from main import app
from scripts.ingest_call import ingest_call
from tests.test_api import (
    TEST_BFF_SHARED_SECRET,
    create_client_with_seed,
    reset_database,
)


def _create_client_with_erc_stg_seed(monkeypatch) -> TestClient:
    """Create test client with ERC StG 2026 call ingested from canonical YAML."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    ingest_call(Path("data/calls/canonical/erc/erc_stg_2026_full.yaml"), dry_run=False)
    session = get_session()
    try:
        call = session.exec(
            select(FundingCall).where(FundingCall.code == "erc_stg_2026_full")
        ).first()
        assert call is not None
    finally:
        session.close()
    return TestClient(app)


def _create_client_with_erc_cog_seed(monkeypatch) -> TestClient:
    """Create test client with ERC CoG 2026 call ingested from canonical YAML."""
    monkeypatch.setenv("LLM_MODE", "stub")
    monkeypatch.setenv("BFF_SHARED_SECRET", TEST_BFF_SHARED_SECRET)
    reset_database()
    ingest_call(Path("data/calls/canonical/erc/erc_cog_2026_full.yaml"), dry_run=False)
    session = get_session()
    try:
        call = session.exec(
            select(FundingCall).where(FundingCall.code == "erc_cog_2026_full")
        ).first()
        assert call is not None
    finally:
        session.close()
    return TestClient(app)


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


def test_wf0060_erc_metadata_moves_resources_under_budget_without_changing_leaf_identity(
    monkeypatch,
) -> None:
    """WF-0060: metadata preserves leaf IDs and corrected resources parent chain."""
    client = _create_client_with_erc_stg_seed(monkeypatch)

    response = client.get("/api/public/calls/erc_stg_2026_full/nodes/metadata")

    assert response.status_code == 200
    payload = response.json()
    nodes_by_logical_id = {node["logical_id"]: node for node in payload["nodes"]}

    assert nodes_by_logical_id["resources_time_commitment"]["parent_logical_id"] == "budget"
    assert nodes_by_logical_id["budget"]["parent_logical_id"] == "part_a"
    assert nodes_by_logical_id["part_b"]["parent_logical_id"] is None
    assert nodes_by_logical_id["b1"]["parent_logical_id"] == "part_b"
    assert nodes_by_logical_id["b2"]["parent_logical_id"] == "part_b"

    leaf_ids = {
        "proposal_summary",
        "b1_part1_scientific_proposal",
        "b1_cv_track_record",
        "b2_part2_scientific_proposal",
        "resources_time_commitment",
    }
    assert leaf_ids.issubset(nodes_by_logical_id.keys())
    assert nodes_by_logical_id["proposal_summary"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["b1_part1_scientific_proposal"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["b1_cv_track_record"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["b2_part2_scientific_proposal"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["resources_time_commitment"]["review_stage"] == "STEP_2"
    assert nodes_by_logical_id["part_a"]["review_stage"] is None


def test_wf0062_erc_cog_metadata_exposes_corrected_hierarchy_and_leaf_review_stages(
    monkeypatch,
) -> None:
    """WF-0062: CoG metadata exposes corrected hierarchy and leaf review stages."""
    client = _create_client_with_erc_cog_seed(monkeypatch)

    response = client.get("/api/public/calls/erc_cog_2026_full/nodes/metadata")

    assert response.status_code == 200
    payload = response.json()
    nodes_by_logical_id = {node["logical_id"]: node for node in payload["nodes"]}

    assert nodes_by_logical_id["resources_time_commitment"]["parent_logical_id"] == "budget"
    assert nodes_by_logical_id["budget"]["parent_logical_id"] == "part_a"
    assert nodes_by_logical_id["part_b"]["parent_logical_id"] is None
    assert nodes_by_logical_id["b1"]["parent_logical_id"] == "part_b"
    assert nodes_by_logical_id["b2"]["parent_logical_id"] == "part_b"

    leaf_ids = {
        "proposal_summary",
        "b1_part1_scientific_proposal",
        "b1_cv_track_record",
        "b2_part2_scientific_proposal",
        "resources_time_commitment",
    }
    assert leaf_ids.issubset(nodes_by_logical_id.keys())
    assert nodes_by_logical_id["proposal_summary"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["b1_part1_scientific_proposal"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["b1_cv_track_record"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["b2_part2_scientific_proposal"]["review_stage"] == "BOTH"
    assert nodes_by_logical_id["resources_time_commitment"]["review_stage"] == "STEP_2"
    assert nodes_by_logical_id["part_a"]["review_stage"] is None
