from __future__ import annotations

import json

import pytest

from app.engine.contracts import ReviewRequestV1
from app.engine.pipeline_v1 import run_review_pipeline

pytestmark = pytest.mark.no_db



def test_telemetry_includes_run_metadata_and_counters() -> None:
    request = ReviewRequestV1(
        request_id="req-telemetry-1",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.missing",
                    "required": True,
                }
            ]
        },
        proposal_nodes={"research_idea": ""},
    )

    result = run_review_pipeline(request)

    assert result.telemetry["run"]["request_id"] == "req-telemetry-1"
    assert result.telemetry["counters"]["severity"]["ERROR"] == 1



def test_telemetry_redacts_raw_text_and_is_deterministic() -> None:
    proposal_text = "This is sensitive proposal text that must not leak."
    request = ReviewRequestV1(
        request_id="req-telemetry-2",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.present",
                    "required": True,
                }
            ]
        },
        proposal_nodes={"research_idea": proposal_text},
    )

    first = run_review_pipeline(request)
    second = run_review_pipeline(request)

    first_payload = json.dumps(first.telemetry, sort_keys=True)
    second_payload = json.dumps(second.telemetry, sort_keys=True)

    assert proposal_text not in first_payload
    assert first_payload == second_payload
