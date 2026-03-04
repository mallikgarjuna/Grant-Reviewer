"""Database-backed ingestion tests for WF-0021 V1/V2 behavior."""

from __future__ import annotations

import os
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import psycopg
import pytest
import yaml
from psycopg import errors as psycopg_errors
from psycopg import sql
from sqlmodel import SQLModel, select

from app.db import engine, get_session
from app.models.domain import (
    CallDefinition,
    EvaluationCriterion,
    EvaluationElement,
    FundingCall,
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
    yaml_path = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml")

    first = ingest_call(yaml_path, dry_run=True)
    second = ingest_call(yaml_path, dry_run=True)

    assert first["schema_version"] == "v2"
    assert first["checksum"] == second["checksum"]
    assert first["canonical_json"] == second["canonical_json"]


def test_v1_ingest_preserves_nullable_logical_ids() -> None:
    """V1 ingest should still succeed with NULL logical IDs."""
    reset_database()

    result = ingest_call(Path("tests/fixtures/edge_case_call.yaml"), dry_run=False)

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

    source = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml")
    first = ingest_call(source, dry_run=False)
    second = ingest_call(source, dry_run=False)

    assert first["schema_version"] == "v2"
    assert first["skipped"] is False
    assert second["skipped"] is True

    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    removed_node = payload["proposal_nodes"].pop()
    # Keep the mutated YAML schema-valid by removing stale reviewer-policy refs.
    reviewer_policy = payload.get("reviewer_policy", [])
    if isinstance(reviewer_policy, list):
        for rule in reviewer_policy:
            if not isinstance(rule, dict):
                continue
            applies_to_node_ids = rule.get("applies_to_node_ids")
            if not isinstance(applies_to_node_ids, list):
                continue
            rule["applies_to_node_ids"] = [
                node_id
                for node_id in applies_to_node_ids
                if node_id != removed_node["id"]
            ]

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
    ingest_call(Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"), dry_run=False)

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


def test_v2_ingest_sets_parent_node_id_and_preorder_order_index() -> None:
    """Hierarchy ingest should persist parent links and deterministic preorder index."""
    reset_database()

    ingest_call(Path("tests/fixtures/hierarchy_v2.yaml"), dry_run=False)

    session = get_session()
    try:
        nodes = list(session.exec(select(ProposalNode)).all())
        by_logical_id = {node.logical_id: node for node in nodes}
        assert set(by_logical_id) == {"root", "child_1", "child_2", "grandchild"}

        root = by_logical_id["root"]
        child_2 = by_logical_id["child_2"]
        child_1 = by_logical_id["child_1"]
        grandchild = by_logical_id["grandchild"]

        assert root.parent_node_id is None
        assert child_2.parent_node_id == root.id
        assert child_1.parent_node_id == root.id
        assert grandchild.parent_node_id == child_1.id

        ordered = sorted(nodes, key=lambda item: item.order_index)
        assert [node.logical_id for node in ordered] == [
            "root",
            "child_2",
            "child_1",
            "grandchild",
        ]
    finally:
        session.close()


def test_v2_ingest_rolls_back_when_parent_reference_is_invalid(tmp_path: Path) -> None:
    """Any hierarchy validation failure should rollback all V2 DB writes."""
    reset_database()

    payload = yaml.safe_load(Path("tests/fixtures/hierarchy_v2.yaml").read_text())
    assert isinstance(payload, dict)
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)
    first_node["parent_logical_id"] = "missing_parent"

    invalid_path = tmp_path / "invalid_hierarchy.yaml"
    invalid_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="Unknown parent_logical_id"):
        ingest_call(invalid_path, dry_run=False)

    session = get_session()
    try:
        assert session.exec(select(FundingCall)).first() is None
        assert session.exec(select(ProposalNode)).first() is None
        assert session.exec(select(CallDefinition)).first() is None
    finally:
        session.close()


def test_v2_ingest_persists_stage_in_canonical_json() -> None:
    """Evaluation element stage should persist in canonical_json for future routing."""
    reset_database()

    ingest_call(Path("tests/fixtures/hierarchy_v2.yaml"), dry_run=False)

    session = get_session()
    try:
        definition = session.exec(select(CallDefinition)).first()
        assert definition is not None
        criteria = definition.canonical_json["evaluation_criteria"]
        assert isinstance(criteria, list)
        first_criterion = criteria[0]
        assert isinstance(first_criterion, dict)
        elements = first_criterion["evaluation_elements"]
        assert isinstance(elements, list)
        first_element = elements[0]
        assert isinstance(first_element, dict)
        assert first_element["stage"] == "STEP_1"
    finally:
        session.close()


def test_v2_ingest_supports_erc_cog_2026_full() -> None:
    """ERC CoG canonical v2 should ingest and persist as active call definition."""
    reset_database()

    result = ingest_call(
        Path("data/calls/canonical/erc/erc_cog_2026_full.yaml"),
        dry_run=False,
    )
    assert result["schema_version"] == "v2"

    session = get_session()
    try:
        funding_call = session.exec(
            select(FundingCall).where(FundingCall.code == "erc_cog_2026_full")
        ).first()
        assert funding_call is not None

        call_definition = session.exec(
            select(CallDefinition).where(CallDefinition.funding_call_id == funding_call.id)
        ).first()
        assert call_definition is not None
        assert call_definition.schema_version == "v2"
    finally:
        session.close()


def test_v2_ingest_handles_concurrent_idempotency_collision() -> None:
    """Concurrent ingest of the same v2 payload should not duplicate persisted state."""
    reset_database()
    source = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml")

    def _ingest_once() -> dict[str, object]:
        return ingest_call(source, dry_run=False)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_future = pool.submit(_ingest_once)
        second_future = pool.submit(_ingest_once)
        first = first_future.result()
        second = second_future.result()

    session = get_session()
    try:
        definitions = list(session.exec(select(CallDefinition)).all())
        calls = list(session.exec(select(FundingCall)).all())

        assert len(definitions) == 1
        assert len(calls) == 1
        assert definitions[0].funding_call_id == calls[0].id
    finally:
        session.close()

    outcomes = {bool(first.get("skipped")), bool(second.get("skipped"))}
    assert outcomes.issubset({False, True})
    assert False in outcomes


def test_wf0021_migration_downgrade_reupgrade_smoke(tmp_path: Path) -> None:
    """WF-0021 migration path should support upgrade->downgrade->upgrade on clean DB."""
    current_db_url = os.getenv("DATABASE_URL", "").strip()
    if not (
        current_db_url.startswith("postgres://")
        or current_db_url.startswith("postgresql://")
        or current_db_url.startswith("postgresql+psycopg://")
    ):
        pytest.skip("Migration smoke requires PostgreSQL test DATABASE_URL.")

    def _replace_db_name(url: str, db_name: str) -> str:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(path=f"/{db_name}"))

    temp_db_name = f"wf0021_migration_smoke_test_{uuid.uuid4().hex[:8]}"
    admin_db_url = _replace_db_name(current_db_url, "postgres")
    temp_db_url = _replace_db_name(current_db_url, temp_db_name)

    try:
        with psycopg.connect(admin_db_url, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(temp_db_name)))
    except psycopg_errors.InsufficientPrivilege:
        pytest.skip("Current PostgreSQL test user cannot create temporary databases.")

    env = dict(os.environ)
    env["DATABASE_URL"] = temp_db_url
    commands = [
        ["uv", "run", "alembic", "upgrade", "head"],
        ["uv", "run", "alembic", "downgrade", "-1"],
        ["uv", "run", "alembic", "upgrade", "head"],
    ]
    try:
        for command in commands:
            completed = subprocess.run(
                command,
                cwd=Path.cwd(),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert completed.returncode == 0, (
                f"Command failed: {' '.join(command)}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
    finally:
        with psycopg.connect(admin_db_url, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                    sql.Identifier(temp_db_name)
                )
            )
