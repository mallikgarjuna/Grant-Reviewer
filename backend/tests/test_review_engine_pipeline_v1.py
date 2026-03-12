"""backend/tests/test_review_engine_pipeline_v1.py
Pipeline v1 deterministic and contract tests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from app.engine.contracts import ActivatedCallConfigSnapshotV1, ReviewRequestV1
from app.engine.pipeline_v1 import CORE_STAGE_SEQUENCE, run_review_pipeline
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


def _wf0065_representative_cases() -> list[dict[str, str]]:
    return [
        {
            "case_id": "nwo_veni_2025_preproposal",
            "call_path": "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml",
            "stage": "STEP_1",
            "node_logical_id": "key_outputs",
            "node_text": "Representative proof text for NWO key outputs.",
        },
        {
            "case_id": "erc_stg_2026_full",
            "call_path": "data/calls/canonical/erc/erc_stg_2026_full.yaml",
            "stage": "STEP_1",
            "node_logical_id": "proposal_summary",
            "node_text": "Representative proof text for ERC proposal summary.",
        },
        {
            "case_id": "MSCA-PF-2025",
            "call_path": "data/calls/canonical/msca/msca_pf_2025_full.yaml",
            "stage": "STEP_1",
            "node_logical_id": "excellence",
            "node_text": "Representative proof text for MSCA excellence.",
        },
    ]


def _wf0065_snapshot_from_call(call_path: str) -> dict[str, object]:
    call_snapshot = yaml.safe_load(Path(call_path).read_text(encoding="utf-8"))
    expectations: list[dict[str, object]] = []
    for node in call_snapshot["proposal_nodes"]:
        node_logical_id = node["id"]
        for node_expectation in node.get("node_expectations", []):
            expectation_payload: dict[str, object] = {
                "expectation_id": f"{node_logical_id}:{node_expectation['evaluation_element_id']}",
                "node_logical_id": node_logical_id,
            }
            if node_expectation.get("expectation_strength") == "MANDATORY":
                expectation_payload["required"] = True
            expectations.append(expectation_payload)
    return {
        "schema_version": "v1",
        "expectations": expectations,
    }


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


def test_wf0045_contract_tracer_happy_path() -> None:
    request = _minimal_request()

    first = run_review_pipeline(request)
    second = run_review_pipeline(request)

    assert first.request_id == request.request_id
    assert first.pipeline_status == "SUCCESS"
    assert first.failure_code is None
    assert first.diagnostics == []
    assert first.compatibility_output["status"] == "COMPLETED"
    assert first.compatibility_output["cards"] == [card.__dict__ for card in first.review_cards]
    assert first.telemetry["run"]["planned_stage_sequence"] == list(CORE_STAGE_SEQUENCE)
    assert first.telemetry["run"]["executed_stages"] == list(CORE_STAGE_SEQUENCE)

    assert json.dumps(first.to_dict(), sort_keys=True) == json.dumps(
        second.to_dict(),
        sort_keys=True,
    )


def test_wf0065_nwo_pipeline_v1_tracer_uses_real_canonical_snapshot() -> None:
    """WF-0065 tracer: pipeline_v1 executes against NWO canonical activated snapshot."""
    canonical_snapshot = _wf0065_snapshot_from_call(
        "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"
    )
    digest = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(canonical_snapshot).encode("utf-8")
    ).hexdigest()
    payload = {
        "request_id": "wf0065-nwo-pipeline",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_digest": digest,
        "call_config_snapshot": canonical_snapshot,
        "proposal_nodes": {
            "key_outputs": "Tracer bullet text proving the real canonical path.",
        },
    }

    request = validate_review_request_payload(payload)
    result = run_review_pipeline(request)

    assert result.pipeline_status == "SUCCESS"
    assert result.failure_code is None
    assert result.compatibility_output["status"] == "COMPLETED"
    assert len(result.review_cards) >= 1
    assert any(
        finding.subject_ref.node_logical_id == "key_outputs" for finding in result.findings
    )


@pytest.mark.parametrize(
    "case",
    _wf0065_representative_cases(),
    ids=lambda case: f"wf0065_pipeline_representative_{case['case_id']}",
)
def test_wf0065_pipeline_v1_representative_success_matrix(case: dict[str, str]) -> None:
    """WF-0065 matrix: pipeline_v1 parity for locked representative calls."""
    canonical_snapshot = _wf0065_snapshot_from_call(case["call_path"])
    digest = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(canonical_snapshot).encode("utf-8")
    ).hexdigest()
    payload = {
        "request_id": f"wf0065-pipeline-{case['case_id']}",
        "mode": "DIAGNOSTIC",
        "stage_ref": case["stage"],
        "call_config_digest": digest,
        "call_config_snapshot": canonical_snapshot,
        "proposal_nodes": {
            case["node_logical_id"]: case["node_text"],
        },
    }

    request = validate_review_request_payload(payload)
    result = run_review_pipeline(request)

    assert result.pipeline_status == "SUCCESS"
    assert result.failure_code is None
    assert result.compatibility_output["status"] == "COMPLETED"
    assert isinstance(result.compatibility_output["cards"], list)
    assert len(result.review_cards) >= 1
    assert len(result.findings) >= 1
    assert any(
        finding.subject_ref.node_logical_id == case["node_logical_id"]
        for finding in result.findings
    )


def test_wf0045_contract_compliance_gate_blocks_downstream() -> None:
    request = ReviewRequestV1(
        request_id="req-wf0045-compliance-block",
        mode="DIAGNOSTIC",
        stage_ref="BAD_STAGE",
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

    result = run_review_pipeline(request)

    assert result.pipeline_status == "FAILURE"
    assert result.failure_code == "CONTRACT_FAILURE"
    assert result.findings == []
    assert result.review_cards == []
    assert result.telemetry["run"]["planned_stage_sequence"] == list(CORE_STAGE_SEQUENCE)
    assert result.telemetry["run"]["executed_stages"] == ["structural_validation"]


def test_wf0045_contract_expectation_not_assessable() -> None:
    request = ReviewRequestV1(
        request_id="req-wf0045-expectation-not-assessable",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "budget_plan",
                    "check_id": "check.presence",
                    "required": True,
                }
            ]
        },
        proposal_nodes={},
    )

    result = run_review_pipeline(request)

    assert len(result.findings) == 1
    assert result.findings[0].assessment_status == "NOT_ASSESSABLE"
    assert result.findings[0].reason.endswith("missing_context:budget_plan")


def test_wf0045_contract_alignment_not_assessable() -> None:
    request = ReviewRequestV1(
        request_id="req-wf0045-alignment-not-assessable",
        mode="DIAGNOSTIC",
        stage_ref="STEP_1",
        call_config_digest="sha256:demo",
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "elem_cv_idea_alignment",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                    "required": True,
                }
            ],
            "proposal_nodes": [
                {
                    "id": "research_idea",
                    "node_expectations": [
                        {
                            "evaluation_element_id": "elem_cv_idea_alignment",
                            "dependencies": ["academic_profile"],
                        }
                    ],
                }
            ],
        },
        proposal_nodes={"research_idea": "My research idea text"},
    )

    result = run_review_pipeline(request)

    assert any(
        finding.check_id == "check.dependency.context_missing"
        and finding.assessment_status == "NOT_ASSESSABLE"
        for finding in result.findings
    )


def test_wf0045_contract_alignment_overlap_merges_without_execution_failure() -> None:
    request = ReviewRequestV1(
        request_id="req-wf0045-alignment-overlap",
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
            ],
            "proposal_nodes": [
                {
                    "id": "research_idea",
                    "node_expectations": [
                        {
                            "evaluation_element_id": "exp-1",
                            "dependencies": [],
                        }
                    ],
                }
            ],
        },
        proposal_nodes={"research_idea": "clear text"},
    )

    result = run_review_pipeline(request)

    assert result.pipeline_status == "SUCCESS"
    assert result.failure_code is None
    assert len(result.findings) == 1


def test_wf0045_contract_diagnostic_ordering_stable() -> None:
    request = ReviewRequestV1(
        request_id="req-wf0045-diagnostic-ordering",
        mode="DIAGNOSTIC",
        stage_ref="BAD_STAGE",
        call_config_digest="sha256:demo",
        call_config_snapshot={"expectations": []},
        proposal_nodes={},
    )

    first = run_review_pipeline(request)
    second = run_review_pipeline(request)

    assert first.pipeline_status == "FAILURE"
    assert first.diagnostics == second.diagnostics
    assert first.compatibility_output["failure_class"] == "contract-failure"


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
            "schema_version": "v1",
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
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
            "schema_version": "v1",
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                },
                {
                    "expectation_id": "exp-2",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                },
            ]
        },
        "proposal_nodes": {"research_idea": "text"},
    }
    canonical = canonicalize_for_digest(
        ActivatedCallConfigSnapshotV1.model_validate(
            payload["call_config_snapshot"]
        ).to_canonical_payload()
    )
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
            "schema_version": "v1",
            "expectations": [
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                },
                {
                    "expectation_id": "exp-1",
                    "node_logical_id": "research_idea",
                    "check_id": "check.presence",
                },
            ]
        },
        "proposal_nodes": {"research_idea": "text"},
    }
    canonical = canonicalize_for_digest(
        ActivatedCallConfigSnapshotV1.model_validate(
            payload["call_config_snapshot"]
        ).to_canonical_payload()
    )
    payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    with pytest.raises(ReviewRequestValidationError) as err:
        validate_review_request_payload(payload)

    assert err.value.code == "MALFORMED_REVIEW_REQUEST"
    assert "Duplicate expectation finding identity" in err.value.message


def test_wf0049_contract_scope_pipeline_semantics_stable() -> None:
    base_snapshot = {
        "schema_version": "v1",
        "expectations": [
            {
                "expectation_id": "exp-1",
                "node_logical_id": "research_idea",
                "check_id": "check.presence",
                "required": True,
            }
        ],
    }
    strict_nested_snapshot = {
        "schema_version": "v1",
        "expectations": [
            {
                "expectation_id": "exp-1",
                "node_logical_id": "research_idea",
                "check_id": "check.presence",
                "required": True,
            }
        ],
        "evaluation_criteria": [
            {
                "id": "crit-1",
                "name": "Criterion 1",
                "stage": "STEP_1",
                "weight_percent": 50,
                "evaluation_elements": [
                    {
                        "id": "elem-1",
                        "name": "Element 1",
                        "description": "Element description",
                        "stage": "STEP_1",
                    }
                ],
            }
        ],
        "reviewer_policy": [
            {
                "id": "policy-1",
                "applies_to_stage": "STEP_1",
                "applies_to_node_ids": ["research_idea"],
                "rule_type": "tone",
                "instruction": "Keep language specific.",
                "severity": "WARNING",
                "enforcement_mode": "PROMPT_ONLY",
            }
        ],
        "prompt_knobs": {
            "temperature": 0.2,
            "max_tokens": 300,
        },
    }

    base_payload = {
        "request_id": "req-wf0049-scope-base",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": base_snapshot,
        "proposal_nodes": {"research_idea": ""},
    }
    base_payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(
            ActivatedCallConfigSnapshotV1.model_validate(base_snapshot).to_canonical_payload()
        ).encode("utf-8")
    ).hexdigest()

    strict_payload = {
        "request_id": "req-wf0049-scope-strict",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": strict_nested_snapshot,
        "proposal_nodes": {"research_idea": ""},
    }
    strict_payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(
            ActivatedCallConfigSnapshotV1.model_validate(
                strict_nested_snapshot
            ).to_canonical_payload()
        ).encode("utf-8")
    ).hexdigest()

    base_result = run_review_pipeline(validate_review_request_payload(base_payload))
    strict_result = run_review_pipeline(validate_review_request_payload(strict_payload))

    assert base_result.pipeline_status == strict_result.pipeline_status
    assert base_result.failure_code == strict_result.failure_code
    assert [finding.check_id for finding in base_result.findings] == [
        finding.check_id for finding in strict_result.findings
    ]
    assert [card.rating for card in base_result.review_cards] == [
        card.rating for card in strict_result.review_cards
    ]


def test_wf0076_pipeline_reason_and_review_card_feedback_include_subordinate_prompt_signal() -> None:
    payload = {
        "request_id": "req-wf0076-positive",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": {
            "schema_version": "v1",
            "expectations": [
                {
                    "expectation_id": "exp-wf0076-innovation",
                    "node_logical_id": "poc_idea_innovation",
                    "check_id": "check.presence",
                    "required": True,
                    "subordinate_prompts": [
                        {
                            "id": "prompt_wf0076_a",
                            "prompt": "Prompt A",
                        },
                        {
                            "id": "prompt_wf0076_b",
                            "prompt": "Prompt B",
                        },
                    ],
                }
            ],
        },
        "proposal_nodes": {"poc_idea_innovation": "Innovation narrative"},
    }
    payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(
            ActivatedCallConfigSnapshotV1.model_validate(
                payload["call_config_snapshot"]
            ).to_canonical_payload()
        ).encode("utf-8")
    ).hexdigest()

    result = run_review_pipeline(validate_review_request_payload(payload))

    assert result.pipeline_status == "SUCCESS"
    assert result.failure_code is None
    assert len(result.findings) == 1
    finding_reason = result.findings[0].reason
    assert finding_reason.startswith("content_evaluated")
    assert "subordinate_prompt_ids=prompt_wf0076_a,prompt_wf0076_b" in finding_reason
    assert "prompt_wf0076_a" in finding_reason
    assert "prompt_wf0076_b" in finding_reason

    assert len(result.review_cards) == 1
    assert "prompt_wf0076_a" in result.review_cards[0].feedback
    assert "prompt_wf0076_b" in result.review_cards[0].feedback


def test_wf0076_pipeline_subordinate_prompt_signal_disappears_without_carriage() -> None:
    payload = {
        "request_id": "req-wf0076-negative",
        "mode": "DIAGNOSTIC",
        "stage_ref": "STEP_1",
        "call_config_snapshot": {
            "schema_version": "v1",
            "expectations": [
                {
                    "expectation_id": "exp-wf0076-innovation",
                    "node_logical_id": "poc_idea_innovation",
                    "check_id": "check.presence",
                    "required": True,
                }
            ],
        },
        "proposal_nodes": {"poc_idea_innovation": "Innovation narrative"},
    }
    payload["call_config_digest"] = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(
            ActivatedCallConfigSnapshotV1.model_validate(
                payload["call_config_snapshot"]
            ).to_canonical_payload()
        ).encode("utf-8")
    ).hexdigest()

    result = run_review_pipeline(validate_review_request_payload(payload))

    assert result.pipeline_status == "SUCCESS"
    assert result.failure_code is None
    assert len(result.findings) == 1
    assert result.findings[0].reason == "content_evaluated"
    assert len(result.review_cards) == 1
    assert result.review_cards[0].feedback == "content_evaluated"
