from __future__ import annotations

import hashlib
import json

from app.engine.contracts import ReviewRequestV1

_REQUIRED_FIELDS = {
    "request_id",
    "mode",
    "stage_ref",
    "call_config_snapshot",
    "call_config_digest",
    "proposal_nodes",
}


class ReviewRequestValidationError(ValueError):
    def __init__(self, *, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{code}: {message}")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


def canonicalize_for_digest(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _validate_required_fields(payload: dict) -> None:
    missing = sorted(field for field in _REQUIRED_FIELDS if field not in payload)
    if missing:
        raise ReviewRequestValidationError(
            code="MALFORMED_REVIEW_REQUEST",
            message="Missing required fields",
            details={"missing_fields": missing},
        )


def _validate_digest(call_config_snapshot: dict, call_config_digest: str) -> None:
    canonical = canonicalize_for_digest(call_config_snapshot)
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    expected_with_prefix = f"sha256:{expected}"
    if call_config_digest != expected_with_prefix:
        raise ReviewRequestValidationError(
            code="CALL_CONFIG_DIGEST_MISMATCH",
            message="call_config_digest does not match call_config_snapshot",
            details={
                "expected": expected_with_prefix,
                "received": call_config_digest,
            },
        )


def _validate_snapshot_shape(call_config_snapshot: dict) -> None:
    expectations = call_config_snapshot.get("expectations")
    if not isinstance(expectations, list):
        raise ReviewRequestValidationError(
            code="MALFORMED_REVIEW_REQUEST",
            message="call_config_snapshot.expectations must be a list",
        )

    required_fields = {"expectation_id", "node_logical_id"}
    for index, expectation in enumerate(expectations):
        if not isinstance(expectation, dict):
            raise ReviewRequestValidationError(
                code="MALFORMED_REVIEW_REQUEST",
                message=f"expectations[{index}] must be an object",
            )
        missing = sorted(field for field in required_fields if field not in expectation)
        if missing:
            raise ReviewRequestValidationError(
                code="MALFORMED_REVIEW_REQUEST",
                message=f"expectations[{index}] missing required fields",
                details={"missing_fields": missing, "index": index},
            )


def _validate_proposal_nodes_shape(proposal_nodes: dict) -> None:
    for key, value in proposal_nodes.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ReviewRequestValidationError(
                code="MALFORMED_REVIEW_REQUEST",
                message="proposal_nodes must map string keys to string values",
            )


def validate_review_request_payload(payload: dict) -> ReviewRequestV1:
    if not isinstance(payload, dict):
        raise ReviewRequestValidationError(
            code="MALFORMED_REVIEW_REQUEST",
            message="Review request payload must be an object",
        )

    _validate_required_fields(payload)

    mode = payload["mode"]
    if mode not in {"DIAGNOSTIC", "STRICT"}:
        raise ReviewRequestValidationError(
            code="MALFORMED_REVIEW_REQUEST",
            message="mode must be DIAGNOSTIC or STRICT",
        )

    call_config_snapshot = payload["call_config_snapshot"]
    proposal_nodes = payload["proposal_nodes"]
    if not isinstance(call_config_snapshot, dict) or not isinstance(proposal_nodes, dict):
        raise ReviewRequestValidationError(
            code="MALFORMED_REVIEW_REQUEST",
            message="call_config_snapshot and proposal_nodes must be objects",
        )

    _validate_snapshot_shape(call_config_snapshot)
    _validate_proposal_nodes_shape(proposal_nodes)
    _validate_digest(call_config_snapshot, str(payload["call_config_digest"]))

    return ReviewRequestV1(
        request_id=str(payload["request_id"]),
        mode=mode,
        stage_ref=str(payload["stage_ref"]),
        call_config_digest=str(payload["call_config_digest"]),
        call_config_snapshot=call_config_snapshot,
        proposal_nodes={str(key): str(value) for key, value in proposal_nodes.items()},
    )
