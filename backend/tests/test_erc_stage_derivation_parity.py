"""backend/tests/test_erc_stage_derivation_parity.py
WF-0070 Task 2: Verify that stage-eligibility derivation uses the
authoritative proposal_surface_stage_scope contract, and that both UI
and runtime activation produce the same stage label for each surface.
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
    """Load canonical ERC call YAML as the canonical_json dict."""
    text = _ERC_STG_CALL_YAML.read_text(encoding="utf-8")
    return yaml.safe_load(text)


@pytest.fixture()
def mock_call_definition(canonical_json: dict[str, Any]) -> Any:
    """Build a mock CallDefinition with canonical_json attribute."""
    mock = MagicMock()
    mock.canonical_json = canonical_json
    return mock


# Expected stage from authoritative contract
AUTHORITATIVE_STAGES = {
    "proposal_summary": "BOTH",
    "b1_part1_scientific_proposal": "BOTH",
    "b1_cv_track_record": "BOTH",
    "b2_part2_scientific_proposal": "STEP_2",
    "resources_time_commitment": "STEP_2",
}


def test_infer_review_stage_derives_from_authoritative_contract(
    mock_call_definition: Any,
) -> None:
    """infer_review_stage must return authoritative stage for each ERC surface."""
    for surface_id, expected_stage in AUTHORITATIVE_STAGES.items():
        actual = infer_review_stage(surface_id, call_definition=mock_call_definition)
        assert actual == expected_stage, (
            f"Surface '{surface_id}': expected '{expected_stage}', got '{actual}'. "
            "Derivation must trace to the authoritative proposal_surface_stage_scope contract."
        )


def test_b2_part2_scientific_proposal_is_not_both(
    mock_call_definition: Any,
) -> None:
    """b2_part2_scientific_proposal must never infer as BOTH for ERC STG."""
    actual = infer_review_stage(
        "b2_part2_scientific_proposal", call_definition=mock_call_definition
    )
    assert actual != "BOTH", (
        "b2_part2_scientific_proposal must be STEP_2, not BOTH. "
        "The authoritative contract overrides element-based inference."
    )
    assert actual == "STEP_2"
