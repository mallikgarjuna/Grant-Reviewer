from __future__ import annotations

import pytest

from app.engine.contracts import DiagnosticFindingV1, SubjectRef
from app.engine.findings.aggregator import aggregate_findings

pytestmark = pytest.mark.no_db


def _finding(
    *,
    expectation_ref: str,
    subject_ref: str,
    check_id: str,
    severity: str,
) -> DiagnosticFindingV1:
    return DiagnosticFindingV1(
        finding_id=f"{subject_ref}:{expectation_ref}:{check_id}",
        primary_expectation_ref=expectation_ref,
        subject_ref=SubjectRef(node_logical_id=subject_ref),
        check_id=check_id,
        finding_kind="MISSING_CONTENT",
        severity=severity,
        assessment_status="ASSESSED",
        reason="reason",
    )


def test_duplicate_identity_tuple_merges_deterministically() -> None:
    findings = [
        _finding(
            expectation_ref="exp-1",
            subject_ref="node-1",
            check_id="check.presence",
            severity="ERROR",
        ),
        _finding(
            expectation_ref="exp-1",
            subject_ref="node-1",
            check_id="check.presence",
            severity="ERROR",
        ),
        DiagnosticFindingV1(
            finding_id="finding:obs:node-1:exp-1:check.presence",
            primary_expectation_ref="exp-1",
            subject_ref=SubjectRef(node_logical_id="node-1"),
            check_id="check.presence",
            finding_kind="PRESENT_CONTENT",
            severity="NOTE",
            assessment_status="ASSESSED",
            reason="alignment_reason",
        ),
    ]

    merged = aggregate_findings(findings=findings, expectation_order={"exp-1": 1})

    assert len(merged) == 1
    assert merged[0].severity == "ERROR"
    assert merged[0].reason == "alignment_reason | reason"


def test_deterministic_order_uses_severity_then_expectation_order_then_check_id() -> None:
    findings = [
        _finding(
            expectation_ref="exp-2",
            subject_ref="node-1",
            check_id="check.z",
            severity="WARNING",
        ),
        _finding(
            expectation_ref="exp-1",
            subject_ref="node-1",
            check_id="check.y",
            severity="ERROR",
        ),
        _finding(
            expectation_ref="exp-1",
            subject_ref="node-1",
            check_id="check.a",
            severity="ERROR",
        ),
    ]

    ordered = aggregate_findings(
        findings=findings,
        expectation_order={"exp-1": 1, "exp-2": 2},
    )

    assert [item.check_id for item in ordered] == ["check.a", "check.y", "check.z"]


def test_wf0045_contract_risk_taxonomy_deterministic() -> None:
    findings = [
        _finding(
            expectation_ref="exp-2",
            subject_ref="node-2",
            check_id="check.presence",
            severity="NOTE",
        ),
        DiagnosticFindingV1(
            finding_id="node-3:exp-3:check.dependency.context_missing",
            primary_expectation_ref="exp-3",
            subject_ref=SubjectRef(node_logical_id="node-3"),
            check_id="check.dependency.context_missing",
            finding_kind="MISSING_CONTENT",
            severity="ERROR",
            assessment_status="NOT_ASSESSABLE",
            reason="missing_dependencies=['academic_profile']",
        ),
    ]

    first = aggregate_findings(
        findings=findings,
        expectation_order={"exp-2": 1, "exp-3": 2},
    )
    second = aggregate_findings(
        findings=findings,
        expectation_order={"exp-2": 1, "exp-3": 2},
    )

    assert [item.reason for item in first] == [item.reason for item in second]
    assert all(item.risk_taxonomy is not None for item in first)
    assert all(not item.reason.startswith("risk_taxonomy=") for item in first)
    assert any(item.assessment_status == "NOT_ASSESSABLE" for item in first)
