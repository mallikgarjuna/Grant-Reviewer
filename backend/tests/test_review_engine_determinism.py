from __future__ import annotations

import json

import pytest

from app.engine.contracts import ReviewRequestV1
from app.engine.pipeline_v1 import run_review_pipeline

pytestmark = pytest.mark.no_db



def _request(mode: str) -> ReviewRequestV1:
    return ReviewRequestV1(
        request_id="det-1",
        mode=mode,
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.required",
                    "required": True,
                },
                {
                    "expectation_id": "exp-2",
                    "node_logical_id": "academic_profile",
                    "check_id": "check.required",
                    "required": True,
                },
            ]
        },
        proposal_nodes={"research_idea": "", "academic_profile": "present"},
    )



def test_repeated_runs_are_byte_stable_for_diagnostic_output() -> None:
    first = run_review_pipeline(_request("DIAGNOSTIC"))
    second = run_review_pipeline(_request("DIAGNOSTIC"))

    assert json.dumps(first.to_dict(), sort_keys=True) == json.dumps(
        second.to_dict(),
        sort_keys=True,
    )



def test_strict_is_exact_subset_of_diagnostic_for_same_input() -> None:
    diagnostic = run_review_pipeline(_request("DIAGNOSTIC"))
    strict = run_review_pipeline(_request("STRICT"))

    diagnostic_ids = {item.finding_id for item in diagnostic.findings}
    strict_ids = {item.finding_id for item in strict.findings}
    assert strict_ids.issubset(diagnostic_ids)



def test_anchor_metadata_hash_and_locator_are_stable_across_runs() -> None:
    first = run_review_pipeline(_request("DIAGNOSTIC"))
    second = run_review_pipeline(_request("DIAGNOSTIC"))

    assert first.telemetry["redacted_nodes"] == second.telemetry["redacted_nodes"]
