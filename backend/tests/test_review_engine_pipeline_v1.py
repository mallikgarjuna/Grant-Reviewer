from __future__ import annotations

import json

import pytest

from app.engine.contracts import ReviewRequestV1
from app.engine.pipeline_v1 import run_review_pipeline

pytestmark = pytest.mark.no_db


def _minimal_request() -> ReviewRequestV1:
    return ReviewRequestV1(
        request_id="req-001",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                }
            ]
        },
        proposal_nodes={"research_idea": "Clear proposal text."},
    )


def test_tracer_bullet_deterministic_pipeline_path() -> None:
    request = _minimal_request()

    result_a = run_review_pipeline(request)
    result_b = run_review_pipeline(request)

    assert len(result_a.findings) == 1
    assert len(result_a.review_cards) == 1

    assert json.dumps(result_a.to_dict(), sort_keys=True) == json.dumps(
        result_b.to_dict(),
        sort_keys=True,
    )
