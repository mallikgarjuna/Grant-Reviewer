from __future__ import annotations

import hashlib
import json

import pytest

from app.engine.review_request_validator import (
    ReviewRequestValidationError,
    canonicalize_for_digest,
    validate_review_request_payload,
)

pytestmark = pytest.mark.no_db


def _payload() -> dict:
    snapshot = {
        "expectations": [
            {
                "expectation_id": "exp-1",
                "node_logical_id": "research_idea",
                "required": True,
            }
        ]
    }
    digest = hashlib.sha256(canonicalize_for_digest(snapshot).encode("utf-8")).hexdigest()
    return {
        "request_id": "req-1",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": snapshot,
        "call_config_digest": f"sha256:{digest}",
        "proposal_nodes": {"research_idea": "text"},
    }


def test_validator_rejects_digest_mismatch_with_contract_error_code() -> None:
    payload = _payload()
    payload["call_config_digest"] = "sha256:deadbeef"

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "CALL_CONFIG_DIGEST_MISMATCH"


def test_validator_rejects_malformed_payload_with_deterministic_code() -> None:
    payload = _payload()
    del payload["request_id"]

    with pytest.raises(ReviewRequestValidationError) as err_info:
        validate_review_request_payload(payload)

    assert err_info.value.code == "MALFORMED_REVIEW_REQUEST"
    assert json.dumps(err_info.value.to_dict(), sort_keys=True) == json.dumps(
        err_info.value.to_dict(),
        sort_keys=True,
    )
