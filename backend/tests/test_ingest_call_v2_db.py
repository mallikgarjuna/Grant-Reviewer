"""Database-backed ingestion tests for WF-0021 V1/V2 behavior."""

from __future__ import annotations

from pathlib import Path

import yaml
from sqlmodel import SQLModel, select

from app.db import engine, get_session
from app.models.domain import (
    CallDefinition,
    EvaluationCriterion,
    EvaluationElement,
    ProposalNode,
)
from app.services.call_definition_service import CallDefinitionService
from scripts.ingest_call import ingest_call


def reset_database() -> None:
    """Reset all tables for isolated ingestion tests."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_v2_dry_run_reports_deterministic_checksum() -> None:
    """V2 dry-run should emit deterministic checksum and canonical JSON payload."""
    yaml_path = Path("data/calls/nwo/nwo_veni_2025_preproposal.yaml")

    first = ingest_call(yaml_path, dry_run=True)
    second = ingest_call(yaml_path, dry_run=True)

    assert first["schema_version"] == "v2"
    assert first["checksum"] == second["checksum"]
    assert first["canonical_json"] == second["canonical_json"]


def test_v1_ingest_preserves_nullable_logical_ids() -> None:
    """V1 ingest should still succeed with NULL logical IDs."""
    reset_database()

    result = ingest_call(Path("data/calls/erc_cog_2026_full.yaml"), dry_run=False)

    assert result["schema_version"] == "v1"
    session = get_session()
    try:
        node = session.exec(select(ProposalNode)).first()
        criterion = session.exec(select(EvaluationCriterion)).first()
        element = session.exec(select(EvaluationElement)).first()

        assert node is not None
        assert criterion is not None
        assert element is not None
        assert node.logical_id is None
        assert criterion.logical_id is None
        assert element.logical_id is None
    finally:
        session.close()


def test_v2_ingest_is_idempotent_and_soft_deletes_removed_nodes(tmp_path: Path) -> None:
    """Second ingest should skip on checksum match and archive removed nodes."""
    reset_database()

    source = Path("data/calls/nwo/nwo_veni_2025_preproposal.yaml")
    first = ingest_call(source, dry_run=False)
    second = ingest_call(source, dry_run=False)

    assert first["schema_version"] == "v2"
    assert first["skipped"] is False
    assert second["skipped"] is True

    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    removed_node = payload["proposal_nodes"].pop()
    modified_path = tmp_path / "nwo_modified.yaml"
    modified_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    third = ingest_call(modified_path, dry_run=False)
    assert third["skipped"] is False

    session = get_session()
    try:
        archived = session.exec(
            select(ProposalNode).where(ProposalNode.logical_id == removed_node["id"])
        ).first()
        assert archived is not None
        assert archived.archived_at is not None
    finally:
        session.close()


def test_call_definition_service_hydrates_node_constraints() -> None:
    """Hydration service should merge canonical node config by logical_id."""
    reset_database()
    ingest_call(Path("data/calls/nwo/nwo_veni_2025_preproposal.yaml"), dry_run=False)

    session = get_session()
    try:
        call_definition = session.exec(select(CallDefinition)).first()
        assert call_definition is not None

        service = CallDefinitionService(session)
        hydrated = service.get_hydrated_nodes(call_definition.funding_call_id)
        assert hydrated

        matching = [
            item for item in hydrated if item.node.logical_id == "academic_profile"
        ]
        assert matching
        config = matching[0].config
        assert "content_constraints" in config
        assert "compliance_rules" in config
    finally:
        session.close()
