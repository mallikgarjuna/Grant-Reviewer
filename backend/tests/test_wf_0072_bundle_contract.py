"""backend/tests/test_wf_0072_bundle_contract.py
WF-0072 verification-matrix contract tests.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.validate_wf_0072_bundle import validate_matrix_payload

pytestmark = [pytest.mark.no_db]

_MATRIX_PATH = Path("../docs/walkthroughs/evidence/WF-0072/verification-matrix.json")


def _seed_matrix() -> dict[str, object]:
    return json.loads(_MATRIX_PATH.read_text(encoding="utf-8"))


def test_wf0072_bundle_seed_matrix_contract_passes() -> None:
    matrix = _seed_matrix()
    validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_rejects_unlocked_representative_call() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["rows"][0]["call_id"] = "not_locked_call"

    with pytest.raises(ValueError, match="LOCKED_REPRESENTATIVE_SET_VIOLATION"):
        validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_requires_row_fields_and_evidence_ref() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["rows"][0]["scenario_scope_note"] = ""
    matrix["rows"][0]["evidence_ref"] = ""

    with pytest.raises(ValueError, match="REQUIRED_ROW_FIELD_MISSING|EVIDENCE_REF_REQUIRED"):
        validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_rejects_invalid_proof_surface() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["rows"][0]["proof_surface"] = "ui"

    with pytest.raises(ValueError, match="PROOF_SURFACE_INVALID"):
        validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_requires_replay_metadata() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["rows"][0]["deterministic_replay"]["command"] = ""

    with pytest.raises(ValueError, match="REPLAY_METADATA_INCOMPLETE"):
        validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_requires_explicit_lane_labeling() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    del matrix["rows"][0]["auth_lane"]

    with pytest.raises(ValueError, match="AUTH_LANE_LABEL_REQUIRED"):
        validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_requires_paired_negative_semantics() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["rows"][0]["scenario_type"] = "negative"
    matrix["rows"][0]["negative_case"] = {
        "visible_block_asserted": False,
        "no_side_effect_asserted": False,
    }

    with pytest.raises(ValueError, match="NEGATIVE_PAIRING_REQUIRED"):
        validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_requires_protected_lane_parity_or_explicit_skip() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["rows"] = [matrix["rows"][0]]
    matrix["rows"][0]["proof_item_id"] = "nwo_veni_2025_preproposal:happy_path"
    matrix["rows"][0]["protected_surface"] = True
    matrix["rows"][0]["entrypoint"] = "/app -> /api/bff/structured-review"
    matrix["rows"][0]["auth_lane"] = "test_bypass"
    matrix["rows"][0]["lane_status"] = "executed"

    with pytest.raises(ValueError, match="PROTECTED_LANE_PARITY_MISSING"):
        validate_matrix_payload(matrix=matrix, require_protected_lanes=True)


def test_wf0072_bundle_closure_requires_protected_parity() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["closure_artifacts"]["baseline_scope_ref"] = "docs/walkthroughs/evidence/WF-0072/baseline_scope.json#baseline"
    matrix["closure_artifacts"]["audit_disposition_ref"] = "docs/walkthroughs/evidence/WF-0072/audit_disposition.md#audit"
    matrix["rows"] = [
        row
        for row in matrix["rows"]
        if not (
            row["proof_item_id"] == "MSCA-PF-2025:happy_path"
            and row["auth_lane"] == "clerk"
        )
    ]

    with pytest.raises(ValueError, match="PROTECTED_LANE_PARITY_MISSING"):
        validate_matrix_payload(matrix=matrix, require_closure=True)


def test_wf0072_bundle_closure_rejects_non_replayable_closure_refs() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["closure_artifacts"]["baseline_scope_ref"] = "baseline"
    matrix["closure_artifacts"]["audit_disposition_ref"] = "audit"

    with pytest.raises(ValueError, match="CLOSURE_ARTIFACT_REF_INVALID"):
        validate_matrix_payload(matrix=matrix, require_closure=True)


def test_wf0072_bundle_rejects_non_object_rows() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["rows"].append("not-a-row-object")

    with pytest.raises(ValueError, match="ROW_OBJECT_REQUIRED"):
        validate_matrix_payload(matrix=matrix)


def test_wf0072_bundle_closure_requires_existing_artifact_refs_and_anchor() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["closure_artifacts"]["baseline_scope_ref"] = "docs/walkthroughs/completed/does-not-exist.md#baseline-sha-or-commit-range"
    matrix["closure_artifacts"]["audit_disposition_ref"] = "docs/walkthroughs/completed/walkthrough-WF-0072-e2e-trust-proof-nwo-erc-msca.md#not-a-real-anchor"

    with pytest.raises(ValueError, match="CLOSURE_ARTIFACT_REF_MISSING|CLOSURE_ARTIFACT_ANCHOR_INVALID"):
        validate_matrix_payload(matrix=matrix, require_closure=True)


def test_wf0072_bundle_closure_rejects_mismatched_closure_status_counts() -> None:
    matrix = _seed_matrix()
    matrix = deepcopy(matrix)
    matrix["closure_status"]["rows_pass"] = 999

    with pytest.raises(ValueError, match="CLOSURE_STATUS_MISMATCH"):
        validate_matrix_payload(matrix=matrix, require_closure=True)
