from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from app.engine.contracts import ActivatedCallConfigSnapshotV1, ReviewRequestV1

_FIELD_ERROR_MESSAGE_TEMPLATES = {
    "unknown_field": "Unknown field is not allowed.",
    "missing_field": "Field is required.",
    "type_error": "Invalid field type.",
    "value_error": "Invalid field value.",
}


class _StrictRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    mode: Literal["DIAGNOSTIC", "STRICT"]
    stage_ref: str
    call_config_snapshot: ActivatedCallConfigSnapshotV1
    call_config_digest: str
    proposal_nodes: dict[str, str]


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


def _raise_malformed_request(
    message: str,
    *,
    details: dict | None = None,
) -> None:
    raise ReviewRequestValidationError(
        code="MALFORMED_REVIEW_REQUEST",
        message=message,
        details=details,
    )


def canonicalize_for_digest(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _to_json_pointer(location: tuple[Any, ...]) -> str:
    if not location:
        return "/"
    escaped = [str(token).replace("~", "~0").replace("/", "~1") for token in location]
    return "/" + "/".join(escaped)


def _map_error_kind(error_type: str) -> str:
    if error_type == "extra_forbidden":
        return "unknown_field"
    if error_type == "missing":
        return "missing_field"
    if error_type.endswith("_type") or error_type.endswith("_parsing"):
        return "type_error"
    if error_type == "literal_error" or error_type.startswith("value_error"):
        return "value_error"
    return "value_error"


def _normalize_validation_error_entry(error: dict[str, Any]) -> dict[str, str]:
    kind = _map_error_kind(str(error["type"]))
    return {
        "path": _to_json_pointer(tuple(error["loc"])),
        "kind": kind,
        "message": _FIELD_ERROR_MESSAGE_TEMPLATES[kind],
    }


def _normalize_field_errors(validation_error: ValidationError) -> list[dict[str, str]]:
    field_errors = [
        _normalize_validation_error_entry(error)
        for error in validation_error.errors(include_url=False)
    ]
    return sorted(field_errors, key=lambda item: (item["path"], item["kind"], item["message"]))


def _parse_request_schema(payload: dict) -> _StrictRequestModel:
    try:
        return _StrictRequestModel.model_validate(payload)
    except ValidationError as err:
        _raise_malformed_request(
            "Review request failed schema validation",
            details={"field_errors": _normalize_field_errors(err)},
        )


def _validate_digest(
    call_config_snapshot: dict[str, object],
    call_config_digest: str,
) -> None:
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


def _validate_snapshot_shape(call_config_snapshot: ActivatedCallConfigSnapshotV1) -> None:
    expectations = call_config_snapshot.expectations
    seen_expectation_ids: set[str] = set()
    seen_finding_identities: set[tuple[str, str, str]] = set()
    for index, expectation in enumerate(expectations):
        expectation_id = expectation.expectation_id
        node_logical_id = expectation.node_logical_id
        check_id = expectation.check_id

        identity = (expectation_id, node_logical_id, check_id)
        if identity in seen_finding_identities:
            raise ReviewRequestValidationError(
                code="MALFORMED_REVIEW_REQUEST",
                message=f"Duplicate expectation finding identity at expectations[{index}]",
                details={
                    "expectation_id": expectation_id,
                    "node_logical_id": node_logical_id,
                    "check_id": check_id,
                    "index": index,
                },
            )
        seen_finding_identities.add(identity)
        if expectation_id in seen_expectation_ids:
            _raise_malformed_request(
                f"Duplicate expectation_id at expectations[{index}]",
                details={"expectation_id": expectation_id, "index": index},
            )
        seen_expectation_ids.add(expectation_id)


def _validate_post_schema_contract(validated_payload: _StrictRequestModel) -> None:
    _validate_snapshot_shape(validated_payload.call_config_snapshot)
    _validate_digest(
        validated_payload.call_config_snapshot.model_dump(
            mode="json",
            exclude_none=True,
            exclude_unset=True,
        ),
        validated_payload.call_config_digest,
    )


def validate_review_request_payload(payload: dict) -> ReviewRequestV1:
    if not isinstance(payload, dict):
        _raise_malformed_request("Review request payload must be an object")

    validated_payload = _parse_request_schema(payload)

    call_config_snapshot = validated_payload.call_config_snapshot
    _validate_post_schema_contract(validated_payload)

    return ReviewRequestV1(
        request_id=validated_payload.request_id,
        mode=validated_payload.mode,
        stage_ref=validated_payload.stage_ref,
        call_config_digest=validated_payload.call_config_digest,
        call_config_snapshot=call_config_snapshot,
        proposal_nodes=validated_payload.proposal_nodes,
    )
