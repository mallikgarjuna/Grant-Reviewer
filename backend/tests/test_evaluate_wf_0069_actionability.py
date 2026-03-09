"""backend/tests/test_evaluate_wf_0069_actionability.py
Tests for WF-0069 deterministic actionability evaluator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts.evaluate_wf_0069_actionability import (
    _classify_dimensions,
    _extract_required_items,
    _is_test_database_url,
    _meets_floor,
    _validate_safe_database_url_for_reset,
)

pytestmark = [pytest.mark.no_db]


def _cases() -> dict[str, Any]:
    payload = json.loads(
        Path("tests/fixtures/wf_0069_actionability_cases.json").read_text(encoding="utf-8")
    )
    return payload["cases"]


def test_wf0069_actionability_classifier_pass_and_fail_paths() -> None:
    cases = _cases()

    passing = cases["pass_with_context_gap"]
    scores, _ = _classify_dimensions(passing["cards"])
    assert scores == passing["expected_scores"]

    failing = cases["fail_flat_status"]
    scores, _ = _classify_dimensions(failing["cards"])
    assert scores == failing["expected_scores"]


def test_wf0069_actionability_classifier_flags_fail_closed_missing_reason() -> None:
    case = _cases()["fail_closed_missing_reason"]
    _, signals = _classify_dimensions(case["cards"])
    assert signals.fail_closed_missing_reason_indices == case["expected_missing_reason_indices"]


def test_wf0069_actionability_baseline_floor_tie_handling() -> None:
    case = _cases()["baseline_floor_tie_handling"]

    assert _meets_floor(
        case["observed_floor_equal"]["revision_actionability"],
        case["required_floor"]["revision_actionability"],
    )
    assert _meets_floor(
        case["observed_floor_equal"]["prioritization_quality"],
        case["required_floor"]["prioritization_quality"],
    )

    assert not _meets_floor(
        case["observed_below_floor"]["revision_actionability"],
        case["required_floor"]["revision_actionability"],
    )


def test_wf0069_actionability_extract_required_items_rejects_item_call_id_mismatch() -> None:
    batch_payload = json.loads(
        Path("../docs/walkthroughs/evidence/WF-0068/snippet-batch.json").read_text(encoding="utf-8")
    )
    for item in batch_payload["items"]:
        if item["item_id"] == "wf0068_erc_actionability_prioritization_stress":
            item["call_id"] = "nwo_veni_2025_preproposal"
            break

    with pytest.raises(ValueError, match="ITEM_CALL_ID_MISMATCH"):
        _extract_required_items(batch_payload)


def test_wf0069_actionability_rejects_non_test_database_reset(monkeypatch) -> None:
    assert _is_test_database_url("postgresql://user:pass@localhost:5433/grant_reviewer_test")
    assert not _is_test_database_url("postgresql://user:pass@localhost:5432/grant_reviewer_dev")

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost:5432/grant_reviewer_dev",
    )
    with pytest.raises(ValueError, match="UNSAFE_DATABASE_URL_FOR_RESET"):
        _validate_safe_database_url_for_reset()
