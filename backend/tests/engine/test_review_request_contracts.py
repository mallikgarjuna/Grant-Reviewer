from __future__ import annotations

import hashlib

import pytest

from app.engine.contracts import ActivatedCallConfigSnapshotV1
from app.engine.review_request_validator import (
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


def test_wf0048_contract_tracer_valid_snapshot_digest_ok() -> None:
    payload = _build_payload()

    validated = validate_review_request_payload(payload)

    assert isinstance(validated.call_config_snapshot, ActivatedCallConfigSnapshotV1)
    assert validated.call_config_snapshot.schema_version == "v1"
