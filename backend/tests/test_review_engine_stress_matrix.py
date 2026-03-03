from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.engine.pipeline_v1 import run_review_pipeline
from app.engine.review_request_validator import validate_review_request_payload

pytestmark = pytest.mark.no_db



def _with_valid_digest(payload: dict) -> dict:
    import hashlib
    import json

    snapshot = payload["call_config_snapshot"]
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload



def test_review_engine_stress_matrix_archetypes_call_agnostic() -> None:
    fixture = yaml.safe_load(
        Path("tests/fixtures/review_engine_stress_matrix.yaml").read_text(encoding="utf-8")
    )

    for scenario in fixture["scenarios"]:
        payload = _with_valid_digest(dict(scenario["request"]))
        request = validate_review_request_payload(payload)
        result = run_review_pipeline(request)
        assert [finding.severity for finding in result.findings] == scenario["expected"][
            "severities"
        ]



def test_no_funder_specific_branching_in_stress_harness() -> None:
    fixture = yaml.safe_load(
        Path("tests/fixtures/review_engine_stress_matrix.yaml").read_text(encoding="utf-8")
    )
    archetypes = {scenario["archetype"] for scenario in fixture["scenarios"]}
    assert archetypes == {"NWO", "ERC", "MSCA"}

    source_calls = {scenario["source_call"] for scenario in fixture["scenarios"]}
    assert "nwo_veni_2025_preproposal" in source_calls
    assert "erc_stg_2026_full" in source_calls


def test_wf0045_contract_stage_ref_variants_supported() -> None:
    payload = _with_valid_digest(
        {
            "request_id": "wf0045-stage-variant",
            "mode": "DIAGNOSTIC",
            "stage_ref": "STEP_2",
            "call_config_digest": "sha256:fixture",
            "call_config_snapshot": {
                "expectations": [
                    {
                        "expectation_id": "exp-stage-2",
                        "node_logical_id": "b1_part1_scientific_proposal",
                        "check_id": "check.required",
                        "required": True,
                    }
                ]
            },
            "proposal_nodes": {
                "b1_part1_scientific_proposal": "Detailed scientific proposal text"
            },
        }
    )
    request = validate_review_request_payload(payload)
    result = run_review_pipeline(request)
    assert result.pipeline_status == "SUCCESS"
    assert [finding.severity for finding in result.findings] == ["NOTE"]
