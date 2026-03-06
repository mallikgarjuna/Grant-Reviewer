"""backend/tests/test_reviewer_policy.py
Tests for reviewer-policy extraction and enforcement.
"""

from uuid import uuid4

import pytest

from app.models.domain import CallDefinition
from app.services.reviewer_policy import (
    find_policy_violations,
    get_applicable_reviewer_policy_rules,
    infer_review_stage,
    matches_review_stage,
)

pytestmark = pytest.mark.no_db


def _build_call_definition() -> CallDefinition:
    return CallDefinition(
        funding_call_id=uuid4(),
        schema_version="v2",
        checksum="checksum",
        canonical_json={
            "reviewer_policy": [
                {
                    "id": "pol_global",
                    "applies_to_stage": "BOTH",
                    "applies_to_node_ids": [],
                    "rule_type": "criterion_scope",
                    "instruction": "Assess only defined evaluation criteria/elements.",
                    "severity": "WARNING",
                    "enforcement_mode": "PROMPT_ONLY",
                    "forbidden_terms": [],
                },
                {
                    "id": "pol_step1_budget",
                    "applies_to_stage": "STEP_1",
                    "applies_to_node_ids": ["b1_part1_scientific_proposal"],
                    "rule_type": "stage_scope",
                    "instruction": "Do not assess budget at Step 1.",
                    "severity": "WARNING",
                    "enforcement_mode": "BLOCKING",
                    "forbidden_terms": ["insufficient budget"],
                },
            ]
        },
        source_path="tests",
    )


def _build_wf0060_stage_definition() -> CallDefinition:
    return CallDefinition(
        funding_call_id=uuid4(),
        schema_version="v2",
        checksum="wf0060-stage-checksum",
        canonical_json={
            "evaluation_criteria": [
                {
                    "id": "crit1",
                    "evaluation_elements": [
                        {"id": "elem.step1", "stage": "STEP_1"},
                        {"id": "elem.step2", "stage": "STEP_2"},
                        {"id": "elem.both", "stage": "BOTH"},
                    ],
                }
            ],
            "proposal_nodes": [
                {
                    "id": "proposal_summary",
                    "node_expectations": [
                        {"evaluation_element_id": "elem.both"},
                    ],
                },
                {
                    "id": "b1_part1_scientific_proposal",
                    "node_expectations": [
                        {"evaluation_element_id": "elem.both"},
                    ],
                },
                {
                    "id": "b1_cv_track_record",
                    "node_expectations": [
                        {"evaluation_element_id": "elem.both"},
                    ],
                },
                {
                    "id": "b2_part2_scientific_proposal",
                    "node_expectations": [
                        {"evaluation_element_id": "elem.step2"},
                    ],
                },
                {
                    "id": "resources_time_commitment",
                    "node_expectations": [
                        {"evaluation_element_id": "elem.step2"},
                    ],
                },
                {
                    "id": "budget",
                    "node_expectations": [],
                },
            ],
        },
        source_path="tests",
    )


def test_infer_review_stage_detects_step_2_nodes() -> None:
    assert infer_review_stage("b2_part2_scientific_proposal") == "STEP_2"
    assert infer_review_stage("b1_part1_scientific_proposal") == "STEP_1"


def test_get_applicable_reviewer_policy_rules_filters_by_stage_and_node() -> None:
    call_definition = _build_call_definition()

    rules = get_applicable_reviewer_policy_rules(
        call_definition=call_definition,
        node_logical_id="b1_part1_scientific_proposal",
        review_stage="STEP_1",
    )

    assert {rule.id for rule in rules} == {"pol_global", "pol_step1_budget"}


def test_find_policy_violations_separates_blocking_and_warning() -> None:
    call_definition = _build_call_definition()
    rules = get_applicable_reviewer_policy_rules(
        call_definition=call_definition,
        node_logical_id="b1_part1_scientific_proposal",
        review_stage="STEP_1",
    )

    blocking, warning = find_policy_violations(
        feedback_texts=["The proposal has insufficient budget for objectives."],
        policy_rules=rules,
    )

    assert len(blocking) == 1
    assert warning == []


def test_policy_blocking_violation_classification() -> None:
    call_definition = _build_call_definition()
    rules = get_applicable_reviewer_policy_rules(
        call_definition=call_definition,
        node_logical_id="b1_part1_scientific_proposal",
        review_stage="STEP_1",
    )
    blocking, warning = find_policy_violations(
        feedback_texts=["The proposal has insufficient budget for objectives."],
        policy_rules=rules,
    )
    assert blocking == [
        "pol_step1_budget: forbidden term 'insufficient budget' detected in feedback #1"
    ]
    assert warning == []


def test_wf0060_reviewer_policy_uses_corrected_erc_leaf_stage_scope() -> None:
    assert infer_review_stage("proposal_summary") == "STEP_1"
    assert infer_review_stage("b1_part1_scientific_proposal") == "STEP_1"
    assert infer_review_stage("b1_cv_track_record") == "STEP_1"
    assert infer_review_stage("b2") == "STEP_1"
    assert infer_review_stage("b2_part2_scientific_proposal") == "STEP_2"
    assert infer_review_stage("resources_time_commitment") == "STEP_2"


def test_infer_review_stage_prefers_call_definition_node_stage_map() -> None:
    call_definition = _build_wf0060_stage_definition()

    assert (
        infer_review_stage(
            "proposal_summary",
            call_definition=call_definition,
        )
        == "BOTH"
    )
    assert (
        infer_review_stage(
            "resources_time_commitment",
            call_definition=call_definition,
        )
        == "STEP_2"
    )
    assert (
        infer_review_stage(
            "budget",
            call_definition=call_definition,
        )
        == "STEP_1"
    )


def test_matches_review_stage_allows_both_nodes_and_blocks_cross_stage_leafs() -> None:
    call_definition = _build_wf0060_stage_definition()

    assert matches_review_stage(
        node_logical_id="proposal_summary",
        review_stage="STEP_1",
        call_definition=call_definition,
    )
    assert matches_review_stage(
        node_logical_id="proposal_summary",
        review_stage="STEP_2",
        call_definition=call_definition,
    )
    assert not matches_review_stage(
        node_logical_id="resources_time_commitment",
        review_stage="STEP_1",
        call_definition=call_definition,
    )
    assert matches_review_stage(
        node_logical_id="resources_time_commitment",
        review_stage="STEP_2",
        call_definition=call_definition,
    )
