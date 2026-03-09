"""backend/tests/test_validate_wf_0068_evidence_bundle.py
WF-0068 evidence-bundle validator tests.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from scripts.validate_wf_0068_evidence_bundle import validate_bundle_payload, validate_records_payload

pytestmark = [pytest.mark.no_db]


def _cases() -> dict[str, Any]:
    payload = json.loads(
        Path("tests/fixtures/wf_0068_evidence_bundle_cases.json").read_text(encoding="utf-8")
    )
    return payload["cases"]


def test_wf0068_evidence_bundle_records_require_exact_dimension_scale() -> None:
    cases = _cases()
    valid = cases["valid_records"]

    validate_records_payload(
        records=deepcopy(valid["records"]),
        raw_output=deepcopy(valid["raw_output"]),
        baseline=deepcopy(valid["baseline"]),
    )

    invalid = deepcopy(valid)
    invalid["records"]["items"][0]["dimension_scores"]["unexpected_dimension"] = "pass"

    with pytest.raises(ValueError, match="DIMENSION_SCALE_INVALID"):
        validate_records_payload(
            records=invalid["records"],
            raw_output=invalid["raw_output"],
            baseline=invalid["baseline"],
        )


def test_wf0068_evidence_bundle_bundle_requires_repeated_failure_pattern() -> None:
    cases = _cases()
    valid = cases["valid_bundle"]

    validate_bundle_payload(
        summary=deepcopy(valid["summary"]),
        records=deepcopy(valid["records"]),
        raw_output=deepcopy(valid["raw_output"]),
        baseline=deepcopy(valid["baseline"]),
    )

    invalid = deepcopy(valid)
    invalid["records"]["items"][1]["follow_on_pattern_class"] = "none"

    with pytest.raises(ValueError, match="REPEATED_PATTERN_REQUIRED"):
        validate_bundle_payload(
            summary=invalid["summary"],
            records=invalid["records"],
            raw_output=invalid["raw_output"],
            baseline=invalid["baseline"],
        )

    single_call_overclaim = deepcopy(valid)
    single_call_overclaim["records"]["items"][1]["call_id"] = "nwo_veni_2025_preproposal"
    single_call_overclaim["summary"]["recommended_follow_on_boundary"] = "traceability_cluster"

    with pytest.raises(ValueError, match="CROSS_WEDGE_OVERCLAIM"):
        validate_bundle_payload(
            summary=single_call_overclaim["summary"],
            records=single_call_overclaim["records"],
            raw_output=single_call_overclaim["raw_output"],
            baseline=single_call_overclaim["baseline"],
        )

    unsupported_boundary = deepcopy(valid)
    unsupported_boundary["summary"]["recommended_follow_on_boundary"] = "unknown_cluster"

    with pytest.raises(ValueError, match="FOLLOW_ON_BOUNDARY_UNSUPPORTED"):
        validate_bundle_payload(
            summary=unsupported_boundary["summary"],
            records=unsupported_boundary["records"],
            raw_output=unsupported_boundary["raw_output"],
            baseline=unsupported_boundary["baseline"],
        )
