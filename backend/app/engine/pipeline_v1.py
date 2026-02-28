from __future__ import annotations

from app.engine.contracts import (
    DiagnosticFindingV1,
    PipelineResult,
    ReviewCard,
    ReviewRequestV1,
    SubjectRef,
)


def _severity_to_rating(severity: str) -> str:
    if severity == "ERROR":
        return "CRITICAL"
    if severity == "WARNING":
        return "WARNING"
    return "NOTE"


def run_review_pipeline(request: ReviewRequestV1) -> PipelineResult:
    expectations = list(request.call_config_snapshot.get("expectations", []))
    findings: list[DiagnosticFindingV1] = []

    for expectation in expectations:
        expectation_id = str(expectation["expectation_id"])
        node_logical_id = str(expectation["node_logical_id"])
        check_id = str(expectation.get("check_id", "check.unspecified"))
        node_text = request.proposal_nodes.get(node_logical_id, "")
        is_missing = not node_text.strip() and bool(expectation.get("required", False))

        finding = DiagnosticFindingV1(
            finding_id=f"{node_logical_id}:{expectation_id}:{check_id}",
            primary_expectation_ref=expectation_id,
            subject_ref=SubjectRef(node_logical_id=node_logical_id),
            check_id=check_id,
            finding_kind="MISSING_CONTENT" if is_missing else "PRESENT_CONTENT",
            severity="ERROR" if is_missing else "NOTE",
            assessment_status="ASSESSED",
            reason="Missing required content" if is_missing else "Content present",
        )
        findings.append(finding)

    findings.sort(
        key=lambda item: (
            item.subject_ref.node_logical_id,
            item.primary_expectation_ref,
            item.check_id,
        )
    )

    cards = [
        ReviewCard(
            node_logical_id=finding.subject_ref.node_logical_id,
            expectation_id=finding.primary_expectation_ref,
            rating=_severity_to_rating(finding.severity),
            feedback=finding.reason,
        )
        for finding in findings
    ]

    return PipelineResult(findings=findings, review_cards=cards)
