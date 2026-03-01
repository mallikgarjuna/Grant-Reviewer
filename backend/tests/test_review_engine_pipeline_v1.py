from __future__ import annotations

import hashlib
import json

import pytest

from app.engine.contracts import ReviewRequestV1
from app.engine.pipeline_v1 import run_review_pipeline
from app.engine.review_request_validator import (
    ReviewRequestValidationError,
    canonicalize_for_digest,
    validate_review_request_payload,
)
from scripts.evaluate_rollout_health import evaluate_rollout_health
from scripts.replay_structured_rollout import build_replay_artifact

pytestmark = pytest.mark.no_db


def _minimal_request() -> ReviewRequestV1:
    return ReviewRequestV1(
        request_id="req-001",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                }
            ]
        },
        proposal_nodes={"research_idea": "Clear proposal text."},
    )


def test_tracer_bullet_deterministic_pipeline_path() -> None:
    request = _minimal_request()

    result_a = run_review_pipeline(request)
    result_b = run_review_pipeline(request)

    assert len(result_a.findings) == 1
    assert len(result_a.review_cards) == 1

    assert json.dumps(result_a.to_dict(), sort_keys=True) == json.dumps(
        result_b.to_dict(),
        sort_keys=True,
    )


def test_mode_projection_in_pipeline_strict_filters_non_errors() -> None:
    request = ReviewRequestV1(
        request_id="req-002",
        mode="STRICT",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.missing",
                    "required": True,
                },
                {
                    "expectation_id": "exp-2",
                    "node_logical_id": "academic_profile",
                    "check_id": "check.present",
                    "required": True,
                },
            ]
        },
        proposal_nodes={
            "research_idea": "",
            "academic_profile": "some text",
        },
    )

    result = run_review_pipeline(request)

    assert [item.check_id for item in result.findings] == ["check.missing"]


def test_pipeline_stress_archetype_smoke() -> None:
    request = ReviewRequestV1(
        request_id="stress-smoke",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.required",
                    "required": True,
                }
            ]
        },
        proposal_nodes={"research_idea": ""},
    )
    result = run_review_pipeline(request)
    assert result.findings[0].severity == "ERROR"


def test_pipeline_runtime_ordering_uses_severity_and_expectation_order() -> None:
    request = ReviewRequestV1(
        request_id="req-ordering-1",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-note",
                    "node_logical_id": "academic_profile",
                    "check_id": "check.note",
                    "required": True,
                },
                {
                    "expectation_id": "exp-error",
                    "node_logical_id": "research_idea",
                    "check_id": "check.error",
                    "required": True,
                },
            ]
        },
        proposal_nodes={
            "academic_profile": "present text",
            "research_idea": "",
        },
    )

    result = run_review_pipeline(request)

    assert [item.check_id for item in result.findings] == ["check.error", "check.note"]


def test_canary_rollout_replay_artifact_and_health_decision() -> None:
    legacy_payload = {
        "status": "COMPLETED",
        "cards": [
            {
                "node_logical_id": "academic_profile",
                "node_expectation_id": "exp-1",
                "rating": "NOTE",
            }
        ],
    }
    pipeline_payload = {
        "status": "COMPLETED",
        "cards": [
            {
                "node_logical_id": "academic_profile",
                "node_expectation_id": "exp-1",
                "rating": "NOTE",
            }
        ],
    }

    artifact = build_replay_artifact(
        legacy_payload=legacy_payload,
        pipeline_payload=pipeline_payload,
        replays=2,
    )
    artifact["metrics"] = {
        "legacy": {
            "error_rate": 0.02,
            "contract_error_rate": 0.01,
            "p95_latency_ms": 1000.0,
        },
        "pipeline_v1": {
            "error_rate": 0.025,
            "contract_error_rate": 0.011,
            "p95_latency_ms": 1100.0,
        },
    }

    proceed = evaluate_rollout_health(artifact)
    assert proceed["overall"]["pass"] is True
    assert proceed["overall"]["recommended_action"] == "proceed"

    artifact["summary"]["structural_parity_passes"] = 1
    rollback = evaluate_rollout_health(artifact)
    assert rollback["overall"]["pass"] is False
    assert rollback["overall"]["recommended_action"] == "rollback"
    assert "structural_parity_failure" in rollback["overall"]["reasons"]


def test_review_request_validator_rejects_digest_mismatch() -> None:
    payload = {
        "request_id": "req-digest-mismatch",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_digest": "sha256:not-the-real-digest",
        "call_config_snapshot": {
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                }
            ]
        },
        "proposal_nodes": {"research_idea": "Clear proposal text."},
    }

    with pytest.raises(ReviewRequestValidationError) as err:
        validate_review_request_payload(payload)

    assert err.value.code == "CALL_CONFIG_DIGEST_MISMATCH"


def test_review_request_validator_allows_same_check_id_for_different_expectations() -> None:
    payload = {
        "request_id": "req-shared-check-id",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": {
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                },
                {
                    "expectation_id": "exp-2",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                },
            ]
        },
        "proposal_nodes": {"research_idea": "text"},
    }
    canonical = canonicalize_for_digest(payload["call_config_snapshot"])
    payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    validated = validate_review_request_payload(payload)
    assert validated.request_id == "req-shared-check-id"


def test_review_request_validator_rejects_duplicate_expectation_finding_identity() -> None:
    payload = {
        "request_id": "req-duplicate-identity",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": {
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                },
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                },
            ]
        },
        "proposal_nodes": {"research_idea": "text"},
    }
    canonical = canonicalize_for_digest(payload["call_config_snapshot"])
    payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    with pytest.raises(ReviewRequestValidationError) as err:
        validate_review_request_payload(payload)

    assert err.value.code == "MALFORMED_REVIEW_REQUEST"
    assert "Duplicate expectation finding identity" in err.value.message
