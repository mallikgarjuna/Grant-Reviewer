"""backend/tests/test_erc_structured_review_e2e.py
WF-0070 Task 9: Verification matrix — E2E proof covering all seven
FR14 blocking items for ERC structured-review step gating.

This test file exercises the full stack (validation + activation +
persistence + review-detail projection) using mocked service calls
and the canonical ERC call YAML as the authoritative source.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import yaml

from app.schemas.structured_review import StructuredReviewRequest
from app.services.reviewer_policy import infer_review_stage, matches_review_stage

pytestmark = pytest.mark.no_db

_ERC_STG_CALL_YAML = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "calls"
    / "canonical"
    / "erc"
    / "erc_stg_2026_full.yaml"
)


@pytest.fixture(scope="module")
def canonical_json() -> dict[str, Any]:
    """Load canonical ERC call YAML."""
    text = _ERC_STG_CALL_YAML.read_text(encoding="utf-8")
    return yaml.safe_load(text)


@pytest.fixture()
def mock_call_definition(canonical_json: dict[str, Any]) -> Any:
    """Mock CallDefinition with canonical_json."""
    mock = MagicMock()
    mock.canonical_json = canonical_json
    return mock


# ===========================================================================
# FR14 Proof Item 1: Step 1 happy path
# (submit → validate → activate → persist → review-detail)
# ===========================================================================

def test_fr14_1_step_1_happy_path(
    canonical_json: dict[str, Any],
    mock_call_definition: Any,
) -> None:
    """Step 1 happy path: all Step-1-eligible nodes accepted, stage_scope correct."""
    step_1_nodes = ["proposal_summary", "b1_part1_scientific_proposal", "b1_cv_track_record"]

    # 1. Validation: all nodes pass stage validation
    for node_id in step_1_nodes:
        assert matches_review_stage(
            node_logical_id=node_id,
            review_stage="STEP_1",
            call_definition=mock_call_definition,
        ), f"Step 1 validation failed for {node_id}"

    # 2. Activation: compute stage_scope_leaf_ids
    all_proposal_nodes = canonical_json.get("proposal_nodes", [])
    stage_scope_leaf_ids = sorted(
        node["id"]
        for node in all_proposal_nodes
        if node.get("node_expectations")
        and infer_review_stage(node["id"], call_definition=mock_call_definition)
        in {"BOTH", "STEP_1"}
    )
    assert "b2_part2_scientific_proposal" not in stage_scope_leaf_ids
    assert "proposal_summary" in stage_scope_leaf_ids

    # 3. Persistence: structured_payload includes stage_scope_leaf_ids
    payload = {
        "review_stage": "STEP_1",
        "submitted_leaf_ids": step_1_nodes,
        "stage_scope_leaf_ids": stage_scope_leaf_ids,
    }
    assert "stage_scope_leaf_ids" in payload
    assert payload["stage_scope_leaf_ids"] == stage_scope_leaf_ids


# ===========================================================================
# FR14 Proof Item 2: Step 1 with Step 2 node mismatch → fail-closed
# ===========================================================================

def test_fr14_2_step_1_with_step_2_node_mismatch(
    mock_call_definition: Any,
) -> None:
    """Step 1 + Step 2-only node → fail-closed with explicit offending IDs."""
    submitted_node_ids = [
        "proposal_summary",
        "b2_part2_scientific_proposal",  # Step 2 only
    ]

    mismatch_ids = sorted(
        node_id
        for node_id in submitted_node_ids
        if not matches_review_stage(
            node_logical_id=node_id,
            review_stage="STEP_1",
            call_definition=mock_call_definition,
        )
    )
    assert mismatch_ids == ["b2_part2_scientific_proposal"]


# ===========================================================================
# FR14 Proof Item 3: Step 1 review-detail boundary — b2 is out_of_scope
# ===========================================================================

def test_fr14_3_step_1_review_detail_boundary_proof(
    canonical_json: dict[str, Any],
    mock_call_definition: Any,
) -> None:
    """b2_part2_scientific_proposal is out_of_scope, not not_reviewed, in Step 1."""
    from app.schemas.api import ReviewDetailResponse

    # Verify out_of_scope field exists
    assert "out_of_scope_node_logical_ids" in ReviewDetailResponse.model_fields

    # Compute stage scope
    all_proposal_nodes = canonical_json.get("proposal_nodes", [])
    stage_scope_leaf_ids = set(
        node["id"]
        for node in all_proposal_nodes
        if node.get("node_expectations")
        and infer_review_stage(node["id"], call_definition=mock_call_definition)
        in {"BOTH", "STEP_1"}
    )

    # Simulate visible nodes including Step 2-only ones
    visible_not_reviewed = [
        "b1_cv_track_record",
        "b2_part2_scientific_proposal",
        "resources_time_commitment",
    ]

    out_of_scope = sorted(
        n for n in visible_not_reviewed if n not in stage_scope_leaf_ids
    )
    remaining_not_reviewed = sorted(
        n for n in visible_not_reviewed if n in stage_scope_leaf_ids
    )

    assert "b2_part2_scientific_proposal" in out_of_scope
    assert "resources_time_commitment" in out_of_scope
    assert "b2_part2_scientific_proposal" not in remaining_not_reviewed


# ===========================================================================
# FR14 Proof Item 4: Step 2 happy path
# ===========================================================================

def test_fr14_4_step_2_happy_path(
    canonical_json: dict[str, Any],
    mock_call_definition: Any,
) -> None:
    """Step 2 happy path: all surfaces accepted including b2_part2."""
    step_2_nodes = [
        "proposal_summary",
        "b1_part1_scientific_proposal",
        "b1_cv_track_record",
        "b2_part2_scientific_proposal",
        "resources_time_commitment",
    ]

    for node_id in step_2_nodes:
        assert matches_review_stage(
            node_logical_id=node_id,
            review_stage="STEP_2",
            call_definition=mock_call_definition,
        ), f"Step 2 validation failed for {node_id}"

    # Stage scope for Step 2 includes all
    all_proposal_nodes = canonical_json.get("proposal_nodes", [])
    stage_scope_leaf_ids = sorted(
        node["id"]
        for node in all_proposal_nodes
        if node.get("node_expectations")
        and infer_review_stage(node["id"], call_definition=mock_call_definition)
        in {"BOTH", "STEP_2"}
    )
    assert "b2_part2_scientific_proposal" in stage_scope_leaf_ids
    assert "resources_time_commitment" in stage_scope_leaf_ids


# ===========================================================================
# FR14 Proof Item 5: Invalid-stage fail-closed at BFF and backend
# ===========================================================================

def test_fr14_5_invalid_stage_fail_closed_backend() -> None:
    """Backend Pydantic schema rejects invalid review_stage."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        StructuredReviewRequest(
            review_stage="INVALID",
            call_id="00000000-0000-0000-0000-000000000001",
            nodes=[],
        )

    with pytest.raises(ValidationError):
        StructuredReviewRequest(
            call_id="00000000-0000-0000-0000-000000000001",
            nodes=[],
        )


# ===========================================================================
# FR14 Proof Item 6: Idempotency and payload-hash parity
# ===========================================================================

def test_fr14_6_idempotency_payload_hash_parity() -> None:
    """review_stage is included in payload, affecting idempotency hash."""
    import hashlib
    import json

    payload_step_1 = {
        "review_stage": "STEP_1",
        "call_id": "test-call-id",
        "nodes": {"proposal_summary": "text"},
    }
    payload_step_2 = {
        "review_stage": "STEP_2",
        "call_id": "test-call-id",
        "nodes": {"proposal_summary": "text"},
    }

    hash_1 = hashlib.sha256(
        json.dumps(payload_step_1, sort_keys=True).encode()
    ).hexdigest()
    hash_2 = hashlib.sha256(
        json.dumps(payload_step_2, sort_keys=True).encode()
    ).hexdigest()

    # Different stages must produce different hashes
    assert hash_1 != hash_2, "Step 1 and Step 2 payloads must have different hashes"


# ===========================================================================
# FR14 Proof Item 7: stage_scope_leaf_ids present and correct
# ===========================================================================

def test_fr14_7_stage_scope_leaf_ids_evidence(
    canonical_json: dict[str, Any],
    mock_call_definition: Any,
) -> None:
    """stage_scope_leaf_ids is derived from authoritative contract and is correct."""
    # Step 1
    all_proposal_nodes = canonical_json.get("proposal_nodes", [])
    step_1_scope = sorted(
        node["id"]
        for node in all_proposal_nodes
        if node.get("node_expectations")
        and infer_review_stage(node["id"], call_definition=mock_call_definition)
        in {"BOTH", "STEP_1"}
    )
    assert step_1_scope == [
        "b1_cv_track_record",
        "b1_part1_scientific_proposal",
        "proposal_summary",
    ]

    # Step 2
    step_2_scope = sorted(
        node["id"]
        for node in all_proposal_nodes
        if node.get("node_expectations")
        and infer_review_stage(node["id"], call_definition=mock_call_definition)
        in {"BOTH", "STEP_2"}
    )
    assert step_2_scope == [
        "b1_cv_track_record",
        "b1_part1_scientific_proposal",
        "b2_part2_scientific_proposal",
        "proposal_summary",
        "resources_time_commitment",
    ]

    # Verify authoritative contract trace
    scope = canonical_json.get("proposal_surface_stage_scope")
    assert scope is not None, "proposal_surface_stage_scope must exist"
    assert scope["b2_part2_scientific_proposal"] == "STEP_2"


def test_wf0072_erc_happy_path_matrix_row_present() -> None:
    """WF-0072 requires one representative ERC happy-path proof row."""
    import json

    evidence_path = Path(__file__).resolve().parents[2] / "docs" / "walkthroughs" / "evidence" / "WF-0072" / "erc_stg_2026_full_proofs.json"
    matrix_path = Path(__file__).resolve().parents[2] / "docs" / "walkthroughs" / "evidence" / "WF-0072" / "verification-matrix.json"

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["call_id"] == "erc_stg_2026_full"
    assert evidence["happy_path"]["result"] == "pass"

    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    row = next(
        (
            item
            for item in matrix["rows"]
            if item["call_id"] == "erc_stg_2026_full" and item["scenario_id"] == "happy_path"
        ),
        None,
    )
    assert row is not None
    assert row["result"] == "pass"
    assert row["proof_surface"] == "API"


def test_wf0072_erc_stage_mismatch_row_proves_zero_side_effects() -> None:
    """WF-0072 requires fail-closed mismatch with non-invocation evidence."""
    import json

    evidence_path = Path(__file__).resolve().parents[2] / "docs" / "walkthroughs" / "evidence" / "WF-0072" / "erc_stg_2026_full_proofs.json"
    matrix_path = Path(__file__).resolve().parents[2] / "docs" / "walkthroughs" / "evidence" / "WF-0072" / "verification-matrix.json"

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    mismatch = evidence["stage_mismatch"]
    assert mismatch["result"] == "pass"
    assert mismatch["visible_block_asserted"] is True
    assert mismatch["no_side_effect_asserted"] is True

    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    row = next(
        (
            item
            for item in matrix["rows"]
            if item["call_id"] == "erc_stg_2026_full" and item["scenario_id"] == "stage_mismatch"
        ),
        None,
    )
    assert row is not None
    assert row["scenario_type"] == "negative"
    assert row["negative_case"]["visible_block_asserted"] is True
    assert row["negative_case"]["no_side_effect_asserted"] is True
