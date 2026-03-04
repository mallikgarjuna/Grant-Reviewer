from __future__ import annotations

import pytest

from scripts.check_contract_boundary_governance import (
    evaluate_governance,
)

pytestmark = [pytest.mark.no_db]


def test_wf0053_contract_tracer_missing_evidence_fails() -> None:
    result = evaluate_governance(
        changed_paths=["backend/app/engine/contracts.py"],
        evidence_bundle_ids=[],
    )

    assert result.exit_code == 1
    assert result.triggered_classes == ["request_boundary_contract_surface"]
    assert result.missing_bundle_ids == ["contract_gate_evidence"]
    assert "MISSING_REQUIRED_EVIDENCE_BUNDLES" in result.message
    assert "contract_gate_evidence" in result.message


@pytest.mark.parametrize(
    ("changed_path", "expected_trigger"),
    [
        ("backend/app/engine/contracts.py", "request_boundary_contract_surface"),
        (
            "backend/tests/engine/test_review_request_contracts.py",
            "contract_gate_selector_surface",
        ),
        (".github/workflows/ci.yml", "ci_contract_gate_wiring_surface"),
        (
            "docs/tasks/task-WF-0053-contract-boundary-governance-enforcement.md",
            "workflow_traceability_surface",
        ),
    ],
)
def test_wf0053_contract_trigger_inventory(
    changed_path: str,
    expected_trigger: str,
) -> None:
    result = evaluate_governance(
        changed_paths=[changed_path],
        evidence_bundle_ids=["contract_gate_evidence"],
    )

    assert result.triggered_classes == [expected_trigger]


def test_wf0053_contract_no_trigger_path() -> None:
    result = evaluate_governance(
        changed_paths=["backend/app/services/non_boundary_service.py"],
        evidence_bundle_ids=[],
    )

    assert result.exit_code == 0
    assert result.triggered_classes == []
    assert result.missing_bundle_ids == []
    assert result.message == "GOVERNANCE_CHECK_OK"
