from __future__ import annotations

import hashlib
import operator

import pytest

from app.engine.contracts import ActivatedCallConfigSnapshotV1
from app.engine.review_request_validator import (
    ReviewRequestValidationError,
    canonicalize_for_digest,
    validate_review_request_payload,
)

pytestmark = pytest.mark.no_db


def _build_snapshot() -> dict[str, object]:
    return {
        "schema_version": "v1",
        "expectations": [
            {
                "expectation_id": "exp-1",
                "node_logical_id": "research_idea",
                "check_id": "check.presence",
            }
        ],
    }


def _build_payload() -> dict[str, object]:
    snapshot = _build_snapshot()
    digest = hashlib.sha256(canonicalize_for_digest(snapshot).encode("utf-8")).hexdigest()
    return {
        "request_id": "req-1",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": snapshot,
        "call_config_digest": f"sha256:{digest}",
        "proposal_nodes": {"research_idea": "text"},
    }


def _assert_field_errors_are_sorted(errors: list[dict[str, str]]) -> None:
    assert errors == sorted(
        errors,
        key=operator.itemgetter("path", "kind", "message"),
    )


def test_wf0048_contract_tracer_valid_snapshot_digest_ok() -> None:
    payload = _build_payload()

    validated = validate_review_request_payload(payload)

    assert isinstance(validated.call_config_snapshot, ActivatedCallConfigSnapshotV1)
    assert validated.call_config_snapshot.schema_version == "v1"


def test_wf0048_contract_unknown_field_stable_pointer() -> None:
    payload = _build_payload()
    payload["unknown_top_level"] = "bad"
    payload["call_config_snapshot"]["expectations"][0]["unknown_nested"] = True

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert err_info.value.details["field_errors"] == [
        {
            "path": "/call_config_snapshot/expectations/0/unknown_nested",
            "kind": "unknown_field",
            "message": "Unknown field is not allowed.",
        },
        {
            "path": "/unknown_top_level",
            "kind": "unknown_field",
            "message": "Unknown field is not allowed.",
        },
    ]


def test_wf0048_contract_field_error_sort_order() -> None:
    payload = _build_payload()
    payload["unknown_top_level"] = "bad"
    del payload["request_id"]
    payload["call_config_snapshot"]["schema_version"] = "v2"
    payload["proposal_nodes"] = {"research_idea": 123}

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    errors = err_info.value.details["field_errors"]
    _assert_field_errors_are_sorted(errors)


def test_wf0048_contract_kind_message_templates() -> None:
    payload = _build_payload()
    del payload["request_id"]
    payload["unknown_top_level"] = "bad"
    payload["proposal_nodes"] = {"research_idea": 123}
    payload["call_config_snapshot"]["schema_version"] = "v2"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    field_errors = err_info.value.details["field_errors"]
    actual_kind_to_message = {error["kind"]: error["message"] for error in field_errors}

    assert actual_kind_to_message["unknown_field"] == "Unknown field is not allowed."
    assert actual_kind_to_message["missing_field"] == "Field is required."
    assert actual_kind_to_message["type_error"] == "Invalid field type."
    assert actual_kind_to_message["value_error"] == "Invalid field value."


def test_wf0048_contract_schema_precedes_digest() -> None:
    payload = _build_payload()
    payload["call_config_digest"] = "sha256:deadbeef"
    del payload["request_id"]

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert "field_errors" in err_info.value.details


def test_wf0048_contract_digest_mismatch_post_schema() -> None:
    payload = _build_payload()
    payload["call_config_digest"] = "sha256:deadbeef"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "CALL_CONFIG_DIGEST_MISMATCH"
