from __future__ import annotations

import hashlib

import pytest

from app.engine.compat.review_card_mapper import ReviewCardMappingError, map_findings_to_review_cards
from app.engine.contracts import DiagnosticFindingV1, SubjectRef
from app.engine.errors import EngineErrorCode
from app.engine.review_request_validator import (
    ReviewRequestValidationError,
    canonicalize_for_digest,
    validate_review_request_payload,
)

pytestmark = pytest.mark.no_db


def _finding(expectation_ref: str) -> DiagnosticFindingV1:
    return DiagnosticFindingV1(
        finding_id="f-1",
        primary_expectation_ref=expectation_ref,
        subject_ref=SubjectRef(node_logical_id="node-1"),
        check_id="check.presence",
        finding_kind="MISSING_CONTENT",
        severity="ERROR",
        assessment_status="ASSESSED",
        reason="reason",
    )


def test_error_contract_matrix_includes_required_codes() -> None:
    assert EngineErrorCode.CALL_CONFIG_DIGEST_MISMATCH.value == "CALL_CONFIG_DIGEST_MISMATCH"
    assert EngineErrorCode.MALFORMED_REVIEW_REQUEST.value == "MALFORMED_REVIEW_REQUEST"
    assert EngineErrorCode.EXPECTATION_REF_UNRESOLVABLE.value == "EXPECTATION_REF_UNRESOLVABLE"
    assert EngineErrorCode.ENGINE_EXECUTION_FAILED.value == "ENGINE_EXECUTION_FAILED"
    assert EngineErrorCode.TIMEOUT.value == "TIMEOUT"


def test_error_contract_malformed_request_is_deterministic() -> None:
    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload({"mode": "DIAGNOSTIC"})

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert err_info.value.to_dict() == err_info.value.to_dict()


def test_error_contract_digest_mismatch_classification() -> None:
    snapshot = {"expectations": []}
    digest = hashlib.sha256(canonicalize_for_digest(snapshot).encode("utf-8")).hexdigest()
    payload = {
        "request_id": "req-1",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": snapshot,
        "call_config_digest": f"sha256:{digest}bad",
        "proposal_nodes": {},
    }

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "CALL_CONFIG_DIGEST_MISMATCH"


def test_error_contract_expectation_ref_unresolvable() -> None:
    with pytest.raises(ReviewCardMappingError) as err_info:
        map_findings_to_review_cards(
            findings=[_finding("exp-missing")],
            resolvable_expectation_refs={"exp-1"},
        )

    assert err_info.value.code == "EXPECTATION_REF_UNRESOLVABLE"
