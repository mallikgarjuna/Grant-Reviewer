"""Pure graph/order validation tests for V2 node hierarchy ingestion."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.schemas.call_definitions_v2 import CallDefinitionV2
from scripts.ingest_call import _resolve_v2_node_preorder

pytestmark = pytest.mark.no_db


def _load_hierarchy_payload() -> dict[str, object]:
    raw = Path("tests/fixtures/hierarchy_v2.yaml").read_text(encoding="utf-8")
    loaded = yaml.safe_load(raw)
    assert isinstance(loaded, dict)
    return loaded


def test_resolve_v2_node_preorder_is_deterministic_from_yaml_order() -> None:
    payload = _load_hierarchy_payload()
    call_def = CallDefinitionV2.model_validate(payload)

    ordered = _resolve_v2_node_preorder(call_def.proposal_nodes)
    assert [node.id for node in ordered] == ["root", "child_2", "child_1", "grandchild"]


def test_resolve_v2_node_preorder_rejects_missing_parent() -> None:
    payload = _load_hierarchy_payload()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)
    first_node["parent_logical_id"] = "missing_parent"
    call_def = CallDefinitionV2.model_validate(payload)

    with pytest.raises(ValueError, match="Unknown parent_logical_id"):
        _resolve_v2_node_preorder(call_def.proposal_nodes)


def test_resolve_v2_node_preorder_rejects_self_parent() -> None:
    payload = _load_hierarchy_payload()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)
    first_node["parent_logical_id"] = first_node["id"]
    call_def = CallDefinitionV2.model_validate(payload)

    with pytest.raises(ValueError, match="cannot reference itself"):
        _resolve_v2_node_preorder(call_def.proposal_nodes)


def test_resolve_v2_node_preorder_rejects_duplicate_ids() -> None:
    payload = _load_hierarchy_payload()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)
    proposal_nodes.append(dict(first_node))

    with pytest.raises(ValueError, match="Duplicate proposal node id"):
        CallDefinitionV2.model_validate(payload)


def test_resolve_v2_node_preorder_rejects_cycle() -> None:
    payload = _load_hierarchy_payload()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)

    child_1 = next(
        node for node in proposal_nodes if isinstance(node, dict) and node["id"] == "child_1"
    )
    child_2 = next(
        node for node in proposal_nodes if isinstance(node, dict) and node["id"] == "child_2"
    )
    child_1["parent_logical_id"] = "child_2"
    child_2["parent_logical_id"] = "child_1"

    call_def = CallDefinitionV2.model_validate(payload)

    with pytest.raises(ValueError, match="Cycle detected in proposal node hierarchy"):
        _resolve_v2_node_preorder(call_def.proposal_nodes)
