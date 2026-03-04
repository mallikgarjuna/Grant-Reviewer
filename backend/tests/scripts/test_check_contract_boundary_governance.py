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
