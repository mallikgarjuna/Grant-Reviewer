from __future__ import annotations

from app.engine.compat.review_card_mapper import map_findings_to_review_cards
from app.engine.contracts import DiagnosticFindingV1, PipelineResult, ReviewRequestV1, SubjectRef
from app.engine.findings.aggregator import aggregate_findings
from app.engine.modes import project_findings_for_mode
from app.engine.telemetry import build_pipeline_telemetry


def _compute_diagnostic_findings(request: ReviewRequestV1) -> list[DiagnosticFindingV1]:
    expectations = list(request.call_config_snapshot.get("expectations", []))
    findings: list[DiagnosticFindingV1] = []

    for expectation in expectations:
        expectation_id = str(expectation["expectation_id"])
        node_logical_id = str(expectation["node_logical_id"])
        check_id = str(expectation.get("check_id", "check.unspecified"))
        node_text = request.proposal_nodes.get(node_logical_id, "")
        is_missing = not node_text.strip() and bool(expectation.get("required", False))

        findings.append(
            DiagnosticFindingV1(
                finding_id=f"{node_logical_id}:{expectation_id}:{check_id}",
                primary_expectation_ref=expectation_id,
                subject_ref=SubjectRef(node_logical_id=node_logical_id),
                check_id=check_id,
                finding_kind="MISSING_CONTENT" if is_missing else "PRESENT_CONTENT",
                severity="ERROR" if is_missing else "NOTE",
                assessment_status="ASSESSED",
                reason="Missing required content" if is_missing else "Content present",
            )
        )

    expectation_order = {
        str(expectation["expectation_id"]): index
        for index, expectation in enumerate(expectations)
    }
    findings = aggregate_findings(
        findings=findings,
        expectation_order=expectation_order,
    )
    return findings


def run_review_pipeline(request: ReviewRequestV1) -> PipelineResult:
    expectations = list(request.call_config_snapshot.get("expectations", []))
    resolvable_expectation_refs = {
        str(expectation["expectation_id"])
        for expectation in expectations
    }

    diagnostic_findings = _compute_diagnostic_findings(request)
    projected_findings = project_findings_for_mode(
        findings=diagnostic_findings,
        mode=request.mode,
    )
    cards = map_findings_to_review_cards(
        findings=projected_findings,
        resolvable_expectation_refs=resolvable_expectation_refs,
    )

    telemetry = build_pipeline_telemetry(
        request=request,
        findings=projected_findings,
        status="success",
    )

    return PipelineResult(
        findings=projected_findings,
        review_cards=cards,
        telemetry=telemetry,
    )
