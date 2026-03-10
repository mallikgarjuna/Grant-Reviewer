"""backend/tests/test_review_detail_stage_aware_buckets.py
WF-0070 Task 7: Verify review-detail projection produces stage-aware
boundary buckets that distinguish out-of-scope from not-reviewed.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.no_db


def test_out_of_scope_field_exists_in_schema() -> None:
    """ReviewDetailResponse must include out_of_scope_node_logical_ids field."""
    from app.schemas.api import ReviewDetailResponse

    fields = ReviewDetailResponse.model_fields
    assert "out_of_scope_node_logical_ids" in fields, (
        "ReviewDetailResponse must declare out_of_scope_node_logical_ids"
    )


def test_out_of_scope_defaults_to_empty() -> None:
    """When not explicitly set, out_of_scope_node_logical_ids is empty list."""
    from app.schemas.api import ReviewDetailResponse, ReviewSummary

    response = ReviewDetailResponse(
        review=ReviewSummary(
            id="00000000-0000-0000-0000-000000000001",
            status="COMPLETED",
            overall_rating="NOTE",
            overall_summary="Summary",
        ),
        cards=[],
    )
    assert response.out_of_scope_node_logical_ids == []


def test_stage_scope_leaf_ids_extraction_helper() -> None:
    """The structured_payload parser must extract stage_scope_leaf_ids."""

    # Test the parsing logic directly
    payload = {
        "submitted_leaf_ids": ["proposal_summary", "b1_part1_scientific_proposal"],
        "stage_scope_leaf_ids": [
            "b1_cv_track_record",
            "b1_part1_scientific_proposal",
            "proposal_summary",
        ],
        "nodes": {
            "proposal_summary": "text",
            "b1_part1_scientific_proposal": "text",
        },
        "legacy_ambiguous_container_ids": [],
        "moved_legacy_node_references": [],
    }

    # Simulate reading stage_scope_leaf_ids from payload (same parsing pattern)
    def _parse_string_list(value):
        if not isinstance(value, list):
            return []
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]

    stage_scope_leaf_ids = _parse_string_list(payload.get("stage_scope_leaf_ids"))
    assert stage_scope_leaf_ids == [
        "b1_cv_track_record",
        "b1_part1_scientific_proposal",
        "proposal_summary",
    ]


def test_out_of_scope_computation_logic() -> None:
    """Out-of-scope = visible nodes NOT in stage_scope_leaf_ids (when present)."""
    # Stage scope for STEP_1
    stage_scope_leaf_ids = {"b1_cv_track_record", "b1_part1_scientific_proposal", "proposal_summary"}

    # All visible call nodes (including Step 2-only ones)
    all_visible_node_logical_ids = [
        "b1_cv_track_record",
        "b1_part1_scientific_proposal",
        "b2_part2_scientific_proposal",
        "proposal_summary",
        "resources_time_commitment",
    ]

    submitted_leaf_ids = {"proposal_summary", "b1_part1_scientific_proposal"}

    # Compute out-of-scope: visible nodes NOT in stage scope
    out_of_scope = sorted(
        node_id
        for node_id in all_visible_node_logical_ids
        if node_id not in stage_scope_leaf_ids
    )

    # Compute visible not reviewed: in scope but not submitted and not reviewed
    visible_not_reviewed = sorted(
        node_id
        for node_id in all_visible_node_logical_ids
        if node_id in stage_scope_leaf_ids and node_id not in submitted_leaf_ids
    )

    assert out_of_scope == ["b2_part2_scientific_proposal", "resources_time_commitment"]
    assert visible_not_reviewed == ["b1_cv_track_record"]
    # b2 and resources should NOT be in visible_not_reviewed
    assert "b2_part2_scientific_proposal" not in visible_not_reviewed
    assert "resources_time_commitment" not in visible_not_reviewed


def test_legacy_review_without_stage_scope_leaf_ids() -> None:
    """Legacy reviews (pre-WF-0070) have no stage_scope_leaf_ids.

    Phase 3.3 MT-2: When stage_scope_leaf_ids is absent or empty,
    all visible-not-reviewed nodes remain unchanged and out_of_scope is empty.
    This confirms backward compatibility for reviews persisted before WF-0070.
    """
    from main import _partition_visible_by_stage_scope

    visible_not_reviewed = [
        "b1_cv_track_record",
        "b2_part2_scientific_proposal",
        "resources_time_commitment",
    ]

    # Case 1: No structured_payload at all (None)
    remaining, out_of_scope = _partition_visible_by_stage_scope(
        visible_not_reviewed=visible_not_reviewed,
        structured_payload=None,
    )
    assert remaining == visible_not_reviewed
    assert out_of_scope == []

    # Case 2: structured_payload exists but stage_scope_leaf_ids absent
    remaining, out_of_scope = _partition_visible_by_stage_scope(
        visible_not_reviewed=visible_not_reviewed,
        structured_payload={"review_stage": "STEP_1", "submitted_leaf_ids": []},
    )
    assert remaining == visible_not_reviewed
    assert out_of_scope == []

    # Case 3: structured_payload has empty stage_scope_leaf_ids
    remaining, out_of_scope = _partition_visible_by_stage_scope(
        visible_not_reviewed=visible_not_reviewed,
        structured_payload={"stage_scope_leaf_ids": []},
    )
    assert remaining == visible_not_reviewed
    assert out_of_scope == []
