from __future__ import annotations

from copy import deepcopy

import pytest

from app.engine.contracts import DiagnosticFindingV1, SubjectRef
from app.engine.modes import project_findings_for_mode

pytestmark = pytest.mark.no_db



def _finding(check_id: str, severity: str) -> DiagnosticFindingV1:
    return DiagnosticFindingV1(
        finding_id=f"id:{check_id}",
        primary_expectation_ref="exp-1",
        subject_ref=SubjectRef(node_logical_id="research_idea"),
        check_id=check_id,
        finding_kind="MISSING_CONTENT",
        severity=severity,
        assessment_status="ASSESSED",
        reason="reason",
    )



def test_strict_mode_is_exact_error_subset_of_diagnostic() -> None:
    diagnostic = [
        _finding("check.a", "ERROR"),
        _finding("check.b", "WARNING"),
        _finding("check.c", "ERROR"),
    ]

    strict = project_findings_for_mode(findings=diagnostic, mode="STRICT")

    assert [item.check_id for item in strict] == ["check.a", "check.c"]



def test_mode_projection_does_not_mutate_findings() -> None:
    diagnostic = [_finding("check.a", "ERROR"), _finding("check.b", "WARNING")]
    before = deepcopy(diagnostic)

    _ = project_findings_for_mode(findings=diagnostic, mode="STRICT")

    assert diagnostic == before


def test_strict_subset_invariant_against_diagnostic_set() -> None:
    diagnostic = [
        _finding("check.a", "ERROR"),
        _finding("check.b", "WARNING"),
        _finding("check.c", "NOTE"),
    ]

    strict = project_findings_for_mode(findings=diagnostic, mode="STRICT")

    assert {item.check_id for item in strict}.issubset(
        {item.check_id for item in diagnostic}
    )
