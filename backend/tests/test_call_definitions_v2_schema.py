"""Schema-level tests for CallDefinitionV2 WF-0032 fields and validators."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.schemas.call_definitions_v2 import CallDefinitionV2

pytestmark = pytest.mark.no_db


def _load_nwo_v2_yaml() -> dict[str, object]:
    raw = Path("data/calls/nwo/nwo_veni_2025_preproposal.yaml").read_text(
        encoding="utf-8"
    )
    loaded = yaml.safe_load(raw)
    assert isinstance(loaded, dict)
    return loaded


def test_v2_schema_accepts_wf0032_optional_fields() -> None:
    payload = _load_nwo_v2_yaml()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)
    first_node["parent_logical_id"] = None

    constraints = first_node.get("content_constraints")
    assert isinstance(constraints, dict)
    constraints["max_pages"] = 3

    criteria = payload["evaluation_criteria"]
    assert isinstance(criteria, list)
    first_criterion = criteria[0]
    assert isinstance(first_criterion, dict)
    elements = first_criterion["evaluation_elements"]
    assert isinstance(elements, list)
    first_element = elements[0]
    assert isinstance(first_element, dict)
    first_element["stage"] = "STEP_1"

    model = CallDefinitionV2.model_validate(payload)
    assert model.proposal_nodes[0].parent_logical_id is None
    assert model.proposal_nodes[0].content_constraints is not None
    assert model.proposal_nodes[0].content_constraints.max_pages == 3
    assert model.evaluation_criteria[0].evaluation_elements[0].stage == "STEP_1"


def test_v2_schema_rejects_duplicate_node_ids() -> None:
    payload = _load_nwo_v2_yaml()
    proposal_nodes = payload["proposal_nodes"]
    assert isinstance(proposal_nodes, list)
    first_node = proposal_nodes[0]
    assert isinstance(first_node, dict)

    duplicate_node = dict(first_node)
    proposal_nodes.append(duplicate_node)

    with pytest.raises(ValueError, match="Duplicate proposal node id"):
        CallDefinitionV2.model_validate(payload)
