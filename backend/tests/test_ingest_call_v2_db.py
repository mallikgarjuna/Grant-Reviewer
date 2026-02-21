"""Database-backed ingestion tests for WF-0021 V2 hydration."""

from __future__ import annotations

from pathlib import Path

from sqlmodel import SQLModel, select

from app.db import engine, get_session
from app.models.domain import CallDefinition
from app.services.call_definition_service import CallDefinitionService
from scripts.ingest_call import ingest_call


def reset_database() -> None:
    """Reset all tables for isolated ingestion tests."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


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

        matching = [item for item in hydrated if item.node.logical_id == "academic_profile"]
        assert matching
        config = matching[0].config
        assert "content_constraints" in config
        assert "compliance_rules" in config
    finally:
        session.close()
