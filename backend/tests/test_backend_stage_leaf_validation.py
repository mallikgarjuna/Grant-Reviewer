"""backend/tests/test_backend_stage_leaf_validation.py
WF-0070 Task 4: Backend structured-review endpoint validates submitted
ERC leaf ids against the authoritative stage-truth contract before execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import yaml

from app.services.reviewer_policy import matches_review_stage

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


# ---- (a) Valid Step 1 → passes ----

def test_valid_step_1_nodes_pass(mock_call_definition: Any) -> None:
    """Step 1-eligible nodes should pass stage validation."""
    step_1_nodes = ["proposal_summary", "b1_part1_scientific_proposal", "b1_cv_track_record"]
    for node_id in step_1_nodes:
        assert matches_review_stage(
            node_logical_id=node_id,
            review_stage="STEP_1",
            call_definition=mock_call_definition,
        ), f"'{node_id}' should pass STEP_1 validation"


# ---- (b) Step 1 + Step 2 leaf id → rejection ----

def test_step_1_with_step_2_only_node_fails(mock_call_definition: Any) -> None:
    """Step 2-only node submitted with STEP_1 must fail validation."""
    assert not matches_review_stage(
        node_logical_id="b2_part2_scientific_proposal",
        review_stage="STEP_1",
        call_definition=mock_call_definition,
    ), "b2_part2_scientific_proposal must NOT pass STEP_1 validation (it's STEP_2 only)"

    assert not matches_review_stage(
        node_logical_id="resources_time_commitment",
        review_stage="STEP_1",
        call_definition=mock_call_definition,
    ), "resources_time_commitment must NOT pass STEP_1 validation (it's STEP_2 only)"


# ---- (c) Valid Step 2 → passes ----

def test_valid_step_2_nodes_pass(mock_call_definition: Any) -> None:
    """Step 2-eligible nodes should pass stage validation."""
    step_2_nodes = [
        "b2_part2_scientific_proposal",
        "resources_time_commitment",
        # BOTH nodes are also eligible for Step 2
        "proposal_summary",
        "b1_part1_scientific_proposal",
        "b1_cv_track_record",
    ]
    for node_id in step_2_nodes:
        assert matches_review_stage(
            node_logical_id=node_id,
            review_stage="STEP_2",
            call_definition=mock_call_definition,
        ), f"'{node_id}' should pass STEP_2 validation"


# ---- (d) Invalid or missing stage → Pydantic handles at schema level ----
# The StructuredReviewRequest schema uses Literal["STEP_1", "STEP_2"]
# so invalid stages are rejected by Pydantic before reaching the handler.

def test_schema_rejects_invalid_stage() -> None:
    """StructuredReviewRequest rejects non-STEP_1/STEP_2 values."""
    from pydantic import ValidationError

    from app.schemas.structured_review import StructuredReviewRequest

    with pytest.raises(ValidationError):
        StructuredReviewRequest(
            review_stage="INVALID",
            call_id="00000000-0000-0000-0000-000000000001",
            nodes=[],
        )


def test_schema_rejects_missing_stage() -> None:
    """StructuredReviewRequest requires review_stage."""
    from pydantic import ValidationError

    from app.schemas.structured_review import StructuredReviewRequest

    with pytest.raises(ValidationError):
        StructuredReviewRequest(
            call_id="00000000-0000-0000-0000-000000000001",
            nodes=[],
        )


# ---- Tracer-bullet: Stage validation flow produces correct mismatch ids ----

def test_stage_mismatch_detection_produces_offending_ids(
    mock_call_definition: Any,
) -> None:
    """Simulating the main.py validation logic: Step 1 + Step 2 leaf → mismatch list."""
    submitted_node_ids = [
        "proposal_summary",
        "b1_part1_scientific_proposal",
        "b2_part2_scientific_proposal",  # Step 2 only
    ]
    stage_mismatch_ids = sorted(
        node_id
        for node_id in submitted_node_ids
        if not matches_review_stage(
            node_logical_id=node_id,
            review_stage="STEP_1",
            call_definition=mock_call_definition,
        )
    )
    assert stage_mismatch_ids == ["b2_part2_scientific_proposal"], (
        f"Expected only b2_part2_scientific_proposal as mismatch, got {stage_mismatch_ids}"
    )
