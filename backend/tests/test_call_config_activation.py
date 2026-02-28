from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.engine.call_config_activation import (
    CallConfigActivationError,
    activate_expectations_for_stage,
)

pytestmark = pytest.mark.no_db


def _load_call(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_stage_activation_and_ordering_from_authored_erc_call() -> None:
    call_snapshot = _load_call("data/calls/erc/erc_stg_2026_full.yaml")

    result = activate_expectations_for_stage(call_snapshot, stage_ref="STEP_1")

    assert "b1_part1_scientific_proposal" in result.expectation_order_by_subject
    b2_expectations = result.expectation_order_by_subject["b2_part2_scientific_proposal"]
    assert (
        "b2_part2_scientific_proposal:elem_project_methodology_arrangements"
        not in b2_expectations
    )


def test_unknown_expectation_ref_fails_deterministically() -> None:
    call_snapshot = _load_call("data/calls/nwo/nwo_veni_2025_preproposal.yaml")
    broken = deepcopy(call_snapshot)
    broken["proposal_nodes"][0]["node_expectations"][0]["evaluation_element_id"] = "elem_unknown"

    with pytest.raises(CallConfigActivationError) as err_info:
        activate_expectations_for_stage(broken, stage_ref="STEP_1")

    assert err_info.value.code == "UNKNOWN_EXPECTATION_ID"


def test_duplicate_expectation_ref_fails_deterministically() -> None:
    call_snapshot = _load_call("data/calls/nwo/nwo_vidi_2025_full_proposal.yaml")
    broken = deepcopy(call_snapshot)
    node = broken["proposal_nodes"][0]
    node["node_expectations"].append(deepcopy(node["node_expectations"][0]))

    with pytest.raises(CallConfigActivationError) as err_info:
        activate_expectations_for_stage(broken, stage_ref="STEP_1")

    assert err_info.value.code == "DUPLICATE_EXPECTATION_ID"


def test_conformance_uses_authored_call_structures() -> None:
    veni = _load_call("data/calls/nwo/nwo_veni_2025_preproposal.yaml")
    vidi = _load_call("data/calls/nwo/nwo_vidi_2025_full_proposal.yaml")
    erc = _load_call("data/calls/erc/erc_stg_2026_full.yaml")

    assert veni["funding_call"]["code"] == "nwo_veni_2025_preproposal"
    assert vidi["funding_call"]["code"] == "nwo_vidi_2025_full_proposal"
    assert erc["funding_call"]["code"] == "erc_stg_2026_full"

    assert activate_expectations_for_stage(veni, stage_ref="STEP_1").expectation_order_by_subject
    assert activate_expectations_for_stage(vidi, stage_ref="STEP_1").expectation_order_by_subject
    assert activate_expectations_for_stage(erc, stage_ref="STEP_2").expectation_order_by_subject
