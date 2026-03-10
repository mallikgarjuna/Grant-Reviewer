"""backend/tests/test_erc_call_stage_scope_contract.py
WF-0070 Task 1: Verify the canonical ERC call YAML contains an authoritative
proposal_surface_stage_scope section with correct per-surface stage labels.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.no_db

_ERC_STG_CALL_YAML = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "calls"
    / "canonical"
    / "erc"
    / "erc_stg_2026_full.yaml"
)

VALID_STAGES = {"STEP_1", "STEP_2", "BOTH"}


@pytest.fixture(scope="module")
def call_yaml() -> dict:
    """Load the canonical ERC STG call YAML once per module."""
    text = _ERC_STG_CALL_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict), "call YAML root must be a dict"
    return data


# ---- T1 contract assertions ------------------------------------------------


def test_proposal_surface_stage_scope_key_exists(call_yaml: dict) -> None:
    """proposal_surface_stage_scope section must be present."""
    assert "proposal_surface_stage_scope" in call_yaml, (
        "Missing 'proposal_surface_stage_scope' key in ERC call YAML"
    )


def test_each_surface_has_exactly_one_valid_stage(call_yaml: dict) -> None:
    """Every surface must declare exactly one of STEP_1 | STEP_2 | BOTH."""
    scope = call_yaml.get("proposal_surface_stage_scope")
    if scope is None:
        pytest.skip("proposal_surface_stage_scope absent (blocked by prior test)")  # pragma: no cover
    assert isinstance(scope, dict), "proposal_surface_stage_scope must be a mapping"
    assert len(scope) > 0, "proposal_surface_stage_scope must not be empty"
    for surface_id, stage in scope.items():
        assert stage in VALID_STAGES, (
            f"Surface '{surface_id}' has invalid stage '{stage}'; "
            f"must be one of {VALID_STAGES}"
        )


def test_b2_part2_scientific_proposal_is_step_2(call_yaml: dict) -> None:
    """b2_part2_scientific_proposal must be classified as STEP_2 (not BOTH)."""
    scope = call_yaml.get("proposal_surface_stage_scope")
    if scope is None:
        pytest.skip("proposal_surface_stage_scope absent (blocked by prior test)")  # pragma: no cover
    assert scope.get("b2_part2_scientific_proposal") == "STEP_2", (
        "b2_part2_scientific_proposal must be STEP_2 per ERC source docs; "
        f"got '{scope.get('b2_part2_scientific_proposal')}'"
    )
