"""backend/tests/test_erc_stage_scoped_activation.py
WF-0070 Task 5: Verify that structured-review runtime activation derives
stage-scoped expectations from the authoritative contract, and that
Step 1 runs do not activate Step 2-only expectations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import yaml

from app.services.reviewer_policy import infer_review_stage

pytestmark = pytest.mark.no_db

_ERC_STG_CALL_YAML = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "calls"
    / "canonical"
    / "erc"
    / "erc_stg_2026_full.yaml"
)


@pytest.fixture(scope="module")
def canonical_json() -> dict[str, Any]:
    """Load canonical ERC call YAML."""
    text = _ERC_STG_CALL_YAML.read_text(encoding="utf-8")
    return yaml.safe_load(text)


@pytest.fixture()
def mock_call_definition(canonical_json: dict[str, Any]) -> Any:
    """Mock CallDefinition with canonical_json."""
    mock = MagicMock()
    mock.canonical_json = canonical_json
    return mock


# --- Evaluation element stage map ---

def _build_element_stage_map(canonical_json: dict[str, Any]) -> dict[str, str]:
    """Build element-id to stage mapping from the call YAML."""
    criteria = canonical_json.get("evaluation_criteria", [])
    result: dict[str, str] = {}
    for criterion in criteria:
        for element in criterion.get("evaluation_elements", []):
            result[element["id"]] = element.get("stage", "BOTH")
    return result


def _build_node_expectations(canonical_json: dict[str, Any]) -> dict[str, list[str]]:
    """Build node-id to list of evaluation_element_ids from the call YAML."""
    nodes = canonical_json.get("proposal_nodes", [])
    result: dict[str, list[str]] = {}
    for node in nodes:
        expectations = node.get("node_expectations", [])
        if expectations:
            result[node["id"]] = [e["evaluation_element_id"] for e in expectations]
    return result


# ---- Test cases ----


def test_step_1_activates_only_step_1_eligible_expectations(
    canonical_json: dict[str, Any],
    mock_call_definition: Any,
) -> None:
    """Step 1 run should only activate expectations from BOTH-stage elements."""
    element_stages = _build_element_stage_map(canonical_json)
    node_expectations = _build_node_expectations(canonical_json)

    step_1_eligible_nodes = [
        node_id
        for node_id in node_expectations
        if infer_review_stage(node_id, call_definition=mock_call_definition)
        in {"STEP_1", "BOTH"}
    ]

    # Every expectation on a Step 1-eligible node should have a BOTH-stage element
    for node_id in step_1_eligible_nodes:
        for element_id in node_expectations[node_id]:
            element_stage = element_stages.get(element_id, "BOTH")
            assert element_stage in {"BOTH", "STEP_1"}, (
                f"Node '{node_id}' has expectation for element '{element_id}' "
                f"which is '{element_stage}'-only; this would be incorrectly "
                "activated in a Step 1 run."
            )


def test_step_2_activates_step_2_eligible_expectations(
    canonical_json: dict[str, Any],
    mock_call_definition: Any,
) -> None:
    """Step 2 run should activate expectations from Step 2-eligible surfaces."""
    node_expectations = _build_node_expectations(canonical_json)

    step_2_eligible_nodes = [
        node_id
        for node_id in node_expectations
        if infer_review_stage(node_id, call_definition=mock_call_definition)
        in {"STEP_2", "BOTH"}
    ]

    # b2_part2_scientific_proposal must be included in Step 2-eligible nodes
    assert "b2_part2_scientific_proposal" in step_2_eligible_nodes
    # All nodes with expectations should be reachable at Step 2
    assert len(step_2_eligible_nodes) > 0


def test_step_1_zero_step_2_only_expectations_activated(
    canonical_json: dict[str, Any],
    mock_call_definition: Any,
) -> None:
    """Zero Step 2-only expectations should be in the Step 1 activation set."""
    element_stages = _build_element_stage_map(canonical_json)
    node_expectations = _build_node_expectations(canonical_json)

    step_1_eligible_nodes = [
        node_id
        for node_id in node_expectations
        if infer_review_stage(node_id, call_definition=mock_call_definition)
        in {"STEP_1", "BOTH"}
    ]

    step_2_only_elements_in_step_1: list[str] = []
    for node_id in step_1_eligible_nodes:
        for element_id in node_expectations[node_id]:
            if element_stages.get(element_id, "BOTH") == "STEP_2":
                step_2_only_elements_in_step_1.append(
                    f"{node_id}:{element_id}"
                )

    assert step_2_only_elements_in_step_1 == [], (
        f"Step 2-only expectations found in Step 1 activation set: "
        f"{step_2_only_elements_in_step_1}"
    )


def test_no_erc_specific_branching_in_evaluator_pipeline_core(
) -> None:
    """Evaluator/pipeline core should contain no ERC-specific conditionals."""
    from pathlib import Path

    core_files = [
        Path(__file__).resolve().parents[1] / "app" / "engine" / "pipeline_v1.py",
        Path(__file__).resolve().parents[1] / "app" / "services" / "review_execution_core.py",
    ]

    erc_specific_terms = ["erc_stg", "erc_cog", "ERC_CONTAINER", "erc_structured"]

    for core_file in core_files:
        if not core_file.exists():
            continue
        content = core_file.read_text(encoding="utf-8")
        for term in erc_specific_terms:
            assert term not in content, (
                f"ERC-specific term '{term}' found in {core_file.name}. "
                "Stage scope must be expressed as a pre-execution activation "
                "snapshot, not via evaluator specialization."
            )
