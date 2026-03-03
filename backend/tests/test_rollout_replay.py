from __future__ import annotations

import json

import pytest

from scripts.replay_structured_rollout import (
    build_replay_artifact,
    compare_structured_runs,
    write_json_deterministic,
)

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


def test_build_replay_artifact_schema_and_counts() -> None:
    artifact = build_replay_artifact(
        legacy_payload=_completed_payload(),
        pipeline_payload=_completed_payload(),
        replays=3,
    )
    assert artifact["meta"]["replays"] == 3
    assert artifact["summary"]["total_runs"] == 3
    assert len(artifact["runs"]) == 3
    assert "checks" in artifact["runs"][0]["comparison"]


def test_write_json_deterministic_has_stable_ordering(tmp_path) -> None:
    output_path = tmp_path / "artifact.json"
    payload = {"z": 1, "a": {"c": 2, "b": 1}}

    write_json_deterministic(output_path, payload)
    first = output_path.read_text(encoding="utf-8")
    write_json_deterministic(output_path, payload)
    second = output_path.read_text(encoding="utf-8")

    assert first == second
    assert first.index('"a"') < first.index('"z"')


def test_wf0045_contract_optional_extension_noop() -> None:
    legacy_payload = _completed_payload()
    pipeline_payload = {
        **_completed_payload(),
        "optional_extensions": {
            "program_specific_policy": True,
            "deep_alignment": True,
        },
    }

    result = compare_structured_runs(
        legacy_payload=legacy_payload,
        pipeline_payload=pipeline_payload,
    )

    assert result["checks"]["structural_parity"] is True
    assert result["checks"]["status_match"] is True
    assert result["checks"]["error_code_match"] is True
