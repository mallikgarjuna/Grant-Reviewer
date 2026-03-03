from __future__ import annotations

import pytest

from app.engine.compat.review_card_mapper import (
    ReviewCardMappingError,
    build_compatibility_output,
    map_findings_to_review_cards,
)
from app.engine.contracts import DiagnosticFindingV1, SubjectRef

pytestmark = pytest.mark.no_db


def _finding(
    *,
    expectation_ref: str,
    subject_ref: str,
    check_id: str,
    severity: str,
    reason: str,
) -> DiagnosticFindingV1:
    return DiagnosticFindingV1(
        finding_id=f"{subject_ref}:{expectation_ref}:{check_id}",
        primary_expectation_ref=expectation_ref,
        subject_ref=SubjectRef(node_logical_id=subject_ref),
        check_id=check_id,
        finding_kind="MISSING_CONTENT",
        severity=severity,
        assessment_status="ASSESSED",
        reason=reason,
    )


def test_mapper_creates_one_card_per_subject_expectation_tuple() -> None:
    findings = [
        _finding(
            expectation_ref="exp-1",
            subject_ref="node-1",
            check_id="check.a",
            severity="ERROR",
            reason="A",
        ),
        _finding(
            expectation_ref="exp-1",
            subject_ref="node-1",
            check_id="check.b",
            severity="WARNING",
            reason="B",
        ),
    ]

    cards = map_findings_to_review_cards(
        findings=findings,
        resolvable_expectation_refs={"exp-1"},
    )

    assert len(cards) == 1
    assert cards[0].rating == "CRITICAL"


def test_mapper_raises_unresolvable_expectation_contract_error() -> None:
    findings = [
        _finding(
            expectation_ref="exp-missing",
            subject_ref="node-1",
            check_id="check.a",
            severity="ERROR",
            reason="A",
        )
    ]

    with pytest.raises(ReviewCardMappingError) as err_info:
        map_findings_to_review_cards(
            findings=findings,
            resolvable_expectation_refs={"exp-1"},
        )

    assert err_info.value.code == "EXPECTATION_REF_UNRESOLVABLE"


def test_wf0045_contract_aggregation_failure_passthrough() -> None:
    contract_output = build_compatibility_output(
        review_cards=[],
        failure_class="contract-failure",
        diagnostics=["invalid contract input"],
    )
    execution_output = build_compatibility_output(
        review_cards=[],
        failure_class="execution-failure",
        diagnostics=["engine crashed"],
    )

    assert contract_output["status"] == "FAILED"
    assert contract_output["failure_class"] == "contract-failure"
    assert execution_output["failure_class"] == "execution-failure"


def test_wf0045_contract_diagnostic_ordering_stable() -> None:
    output_a = build_compatibility_output(
        review_cards=[],
        failure_class="execution-failure",
        diagnostics=["z-last", "a-first", "m-mid", "a-first"],
    )
    output_b = build_compatibility_output(
        review_cards=[],
        failure_class="execution-failure",
        diagnostics=["m-mid", "z-last", "a-first"],
    )

    assert output_a["diagnostics"] == ["a-first", "m-mid", "z-last"]
    assert output_a["diagnostics"] == output_b["diagnostics"]
