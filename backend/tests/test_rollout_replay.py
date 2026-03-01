from __future__ import annotations

import json

import pytest

from scripts.replay_structured_rollout import compare_structured_runs

pytestmark = pytest.mark.no_db


def _completed_payload(*, rating: str = "NOTE") -> dict[str, object]:
    return {
        "status": "COMPLETED",
        "cards": [
            {
                "node_logical_id": "academic_profile",
                "node_expectation_id": "exp-1",
                "rating": rating,
            }
        ],
    }


def test_compare_structured_runs_parity_detects_structural_mismatch() -> None:
    legacy_payload = _completed_payload(rating="NOTE")
    pipeline_payload = _completed_payload(rating="WARNING")

    result = compare_structured_runs(
        legacy_payload=legacy_payload,
        pipeline_payload=pipeline_payload,
    )

    assert result["checks"]["structural_parity"] is False
    assert "card_signature_mismatch" in result["differences"]


def test_compare_structured_runs_comparator_output_is_deterministic() -> None:
    legacy_payload = _completed_payload()
    pipeline_payload = _completed_payload()

    first = compare_structured_runs(
        legacy_payload=legacy_payload,
        pipeline_payload=pipeline_payload,
    )
    second = compare_structured_runs(
        legacy_payload=legacy_payload,
        pipeline_payload=pipeline_payload,
    )

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
