from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.check_contract_boundary_governance import (
    derive_evidence_bundle_ids,
    evaluate_governance,
    resolve_governance_inputs,
)

pytestmark = [pytest.mark.no_db]


def test_wf0053_contract_tracer_missing_evidence_fails() -> None:
    result = evaluate_governance(
        changed_paths=["backend/app/engine/contracts.py"],
        evidence_bundle_ids=[],
    )

    assert result.exit_code == 1
    assert result.triggered_classes == ["request_boundary_contract_surface"]
    assert result.missing_bundle_ids == [
        "artifact_traceability_evidence",
        "contract_gate_evidence",
        "negative_smoke_evidence",
    ]
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


def test_wf0053_contract_missing_bundle_diagnostics() -> None:
    result_single_missing = evaluate_governance(
        changed_paths=["backend/app/engine/contracts.py"],
        evidence_bundle_ids=[
            "artifact_traceability_evidence",
            "negative_smoke_evidence",
        ],
    )

    assert result_single_missing.exit_code == 1
    assert result_single_missing.missing_bundle_ids == ["contract_gate_evidence"]
    assert result_single_missing.reason_code == "MISSING_REQUIRED_EVIDENCE_BUNDLES"
    assert result_single_missing.message == (
        "MISSING_REQUIRED_EVIDENCE_BUNDLES: contract_gate_evidence"
    )

    result_multiple_missing = evaluate_governance(
        changed_paths=["backend/app/engine/contracts.py"],
        evidence_bundle_ids=["contract_gate_evidence"],
    )

    assert result_multiple_missing.exit_code == 1
    assert result_multiple_missing.missing_bundle_ids == [
        "artifact_traceability_evidence",
        "negative_smoke_evidence",
    ]
    assert result_multiple_missing.reason_code == "MISSING_REQUIRED_EVIDENCE_BUNDLES"
    assert result_multiple_missing.message == (
        "MISSING_REQUIRED_EVIDENCE_BUNDLES: "
        "artifact_traceability_evidence,negative_smoke_evidence"
    )


def test_wf0053_contract_required_bundle_ids() -> None:
    result = evaluate_governance(
        changed_paths=["backend/app/engine/contracts.py"],
        evidence_bundle_ids=[],
    )

    assert result.missing_bundle_ids == [
        "artifact_traceability_evidence",
        "contract_gate_evidence",
        "negative_smoke_evidence",
    ]


def test_wf0053_contract_selector_marker_trigger() -> None:
    result = evaluate_governance(
        changed_paths=["backend/pyproject.toml"],
        evidence_bundle_ids=[],
    )

    assert result.exit_code == 1
    assert result.triggered_classes == ["contract_gate_selector_surface"]


def test_wf0053_contract_negative_smoke_reason() -> None:
    proc = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/check_contract_boundary_governance.py",
            "--changed-path",
            "backend/app/engine/contracts.py",
            "--evidence-bundle",
            "contract_gate_evidence",
            "--evidence-bundle",
            "artifact_traceability_evidence",
        ],
        cwd=".",
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert "reason_code=MISSING_REQUIRED_EVIDENCE_BUNDLES" in proc.stdout
    assert (
        "MISSING_REQUIRED_EVIDENCE_BUNDLES: negative_smoke_evidence" in proc.stdout
    )


def test_wf0053_contract_derived_bundle_ids_from_changed_paths() -> None:
    evidence_bundle_ids = derive_evidence_bundle_ids(
        [
            ".github/workflows/ci.yml",
            "docs/tasks/task-WF-0053-contract-boundary-governance-enforcement.md",
            "docs/walkthroughs/walkthrough-WF-0053-contract-boundary-governance-enforcement.md",
        ]
    )

    assert evidence_bundle_ids == [
        "artifact_traceability_evidence",
        "contract_gate_evidence",
        "negative_smoke_evidence",
    ]


def test_wf0053_contract_resolve_inputs_changed_path_file(tmp_path: Path) -> None:
    changed_path_file = tmp_path / "changed_paths.txt"
    changed_path_file.write_text(
        "\n".join(
            [
                "backend/app/engine/contracts.py",
                ".github/workflows/ci.yml",
                "docs/tasks/task-WF-0053-contract-boundary-governance-enforcement.md",
                "docs/walkthroughs/walkthrough-WF-0053-contract-boundary-governance-enforcement.md",
            ]
        ),
        encoding="utf-8",
    )

    changed_paths, evidence_bundle_ids = resolve_governance_inputs(
        changed_paths=[],
        evidence_bundle_ids=[],
        changed_path_file=str(changed_path_file),
    )
    result = evaluate_governance(
        changed_paths=changed_paths,
        evidence_bundle_ids=evidence_bundle_ids,
    )

    assert result.exit_code == 0
