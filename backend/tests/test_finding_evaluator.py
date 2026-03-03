from __future__ import annotations

import pytest

from app.engine.contracts import AnchorV1, ObservationV1, SubjectRef
from app.engine.findings.evaluator import (
    FindingEvaluationError,
    evaluate_expectations,
    evaluate_observations,
)

pytestmark = pytest.mark.no_db


def _dependency_missing_observation() -> ObservationV1:
    return ObservationV1(
        observation_id="obs-1",
        subject_ref=SubjectRef(node_logical_id="research_idea"),
        expectation_ref="elem_cv_idea_alignment",
        observation_kind="DEPENDENCY_CONTEXT_MISSING",
        anchor=AnchorV1(
            anchor_type="TEXT_SPAN",
            locator="text-span:abc",
            text_hash="hash",
        ),
        details={"missing_dependencies": ["academic_profile"]},
    )


def test_unknown_check_id_fails_deterministically() -> None:
    with pytest.raises(FindingEvaluationError) as err_info:
        evaluate_observations(
            observations=[_dependency_missing_observation()],
            expectation_to_check_id={"elem_cv_idea_alignment": "check.unknown"},
        )

    assert err_info.value.code == "UNKNOWN_CHECK_ID"


def test_missing_dependency_context_maps_to_not_assessable() -> None:
    findings = evaluate_observations(
        observations=[_dependency_missing_observation()],
        expectation_to_check_id={
            "elem_cv_idea_alignment": "check.dependency.context_missing"
        },
    )

    assert findings[0].assessment_status == "NOT_ASSESSABLE"
    assert "missing_dependencies" in findings[0].reason


def test_wf0045_contract_expectation_assessed() -> None:
    findings = evaluate_expectations(
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
        proposal_nodes={"research_idea": "present text"},
    )

    assert len(findings) == 1
    assert findings[0].assessment_status == "ASSESSED"
    assert findings[0].reason == "content_evaluated"


def test_wf0045_contract_expectation_not_assessable() -> None:
    findings = evaluate_expectations(
        call_config_snapshot={
            "expectations": [
                {
                    "expectation_id": "exp-2",
                    "node_logical_id": "budget_plan",
                    "check_id": "check.presence",
                    "required": True,
                }
            ]
        },
        proposal_nodes={},
    )

    assert len(findings) == 1
    assert findings[0].assessment_status == "NOT_ASSESSABLE"
    assert findings[0].reason == "missing_context:budget_plan"
