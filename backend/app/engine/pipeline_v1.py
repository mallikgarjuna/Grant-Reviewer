from __future__ import annotations

from app.engine.compat.review_card_mapper import map_findings_to_review_cards
from app.engine.contracts import (
    DiagnosticFindingV1,
    PipelineResult,
    ReviewRequestV1,
)
from app.engine.errors import (
    PipelineContractFailure,
    PipelineExecutionFailure,
    map_failure_code,
)
from app.engine.findings.aggregator import aggregate_findings
from app.engine.findings.evaluator import evaluate_expectations
from app.engine.modes import project_findings_for_mode
from app.engine.telemetry import build_pipeline_telemetry

CORE_STAGE_SEQUENCE: tuple[str, ...] = (
    "structural_validation",
    "compliance_gate",
    "expectation_evaluation",
    "cross_node_alignment",
    "risk_audit",
    "output_aggregation",
)
_SUPPORTED_STAGE_REFS = {"STEP_1"}


def _build_failure_result(
    *,
    request: ReviewRequestV1,
    stage_transitions: list[str],
    error: Exception,
) -> PipelineResult:
    failure_code = map_failure_code(error)
    failure_class = (
        "contract-failure" if failure_code == "CONTRACT_FAILURE" else "execution-failure"
    )
    telemetry = build_pipeline_telemetry(
        request=request,
        findings=[],
        status="failure",
        stage_transitions=stage_transitions,
    )
    return PipelineResult(
        request_id=request.request_id,
        pipeline_status="FAILURE",
        failure_code=failure_code,
        diagnostics=[str(error)],
        compatibility_output={
            "status": "FAILED",
            "failure_class": failure_class,
            "cards": [],
        },
        findings=[],
        review_cards=[],
        telemetry=telemetry,
    )


def _run_compliance_gate(request: ReviewRequestV1) -> None:
    if request.stage_ref not in _SUPPORTED_STAGE_REFS:
        raise PipelineContractFailure(f"Unsupported stage_ref: {request.stage_ref}")


def _compute_diagnostic_findings(request: ReviewRequestV1) -> list[DiagnosticFindingV1]:
    expectations = list(request.call_config_snapshot.get("expectations", []))
    findings = evaluate_expectations(
        call_config_snapshot=request.call_config_snapshot,
        proposal_nodes=request.proposal_nodes,
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
    stage_transitions = [CORE_STAGE_SEQUENCE[0], CORE_STAGE_SEQUENCE[1]]
    try:
        _run_compliance_gate(request)
        stage_transitions = list(CORE_STAGE_SEQUENCE)

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
            stage_transitions=stage_transitions,
        )

        return PipelineResult(
            request_id=request.request_id,
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output={
                "status": "COMPLETED",
                "cards": [card.__dict__ for card in cards],
            },
            findings=projected_findings,
            review_cards=cards,
            telemetry=telemetry,
        )
    except PipelineContractFailure as err:
        return _build_failure_result(
            request=request,
            stage_transitions=stage_transitions,
            error=err,
        )
    except Exception as err:
        return _build_failure_result(
            request=request,
            stage_transitions=stage_transitions,
            error=PipelineExecutionFailure(str(err)),
        )
