from __future__ import annotations

import re

from app.engine.compat.review_card_mapper import (
    ReviewCardMappingError,
    build_compatibility_output,
    map_findings_to_review_cards,
)
from app.engine.contracts import (
    PipelineResult,
    ReviewRequestV1,
)
from app.engine.errors import (
    PipelineContractFailure,
    PipelineExecutionFailure,
    map_failure_code,
)
from app.engine.findings.aggregator import aggregate_findings
from app.engine.findings.evaluator import evaluate_expectations, evaluate_observations
from app.engine.modes import project_findings_for_mode
from app.engine.observations.extractor import extract_observations
from app.engine.telemetry import build_pipeline_telemetry

CORE_STAGE_SEQUENCE: tuple[str, ...] = (
    "structural_validation",
    "compliance_gate",
    "expectation_evaluation",
    "cross_node_alignment",
    "risk_audit",
    "output_aggregation",
)


def _build_failure_result(
    *,
    request: ReviewRequestV1,
    executed_stages: list[str],
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
        planned_stage_sequence=list(CORE_STAGE_SEQUENCE),
        executed_stages=executed_stages,
    )
    return PipelineResult(
        request_id=request.request_id,
        pipeline_status="FAILURE",
        failure_code=failure_code,
        diagnostics=[str(error)],
        compatibility_output=build_compatibility_output(
            review_cards=[],
            failure_class=failure_class,
            diagnostics=[str(error)],
        ),
        findings=[],
        review_cards=[],
        telemetry=telemetry,
    )


def _run_structural_validation(request: ReviewRequestV1) -> None:
    expectations = request.call_config_snapshot.get("expectations", [])
    if not isinstance(expectations, list):
        raise PipelineContractFailure("call_config_snapshot.expectations must be a list")
    for index, expectation in enumerate(expectations):
        if not isinstance(expectation, dict):
            raise PipelineContractFailure(f"expectations[{index}] must be an object")
        if "expectation_id" not in expectation or "node_logical_id" not in expectation:
            raise PipelineContractFailure(
                f"expectations[{index}] missing expectation_id/node_logical_id"
            )


def _run_compliance_gate(request: ReviewRequestV1) -> None:
    if not re.fullmatch(r"STEP_[0-9]+", request.stage_ref.strip()):
        raise PipelineContractFailure(f"Unsupported stage_ref: {request.stage_ref}")

def run_review_pipeline(request: ReviewRequestV1) -> PipelineResult:
    executed_stages: list[str] = []
    try:
        _run_structural_validation(request)
        executed_stages.append(CORE_STAGE_SEQUENCE[0])

        _run_compliance_gate(request)
        executed_stages.append(CORE_STAGE_SEQUENCE[1])

        expectations = list(request.call_config_snapshot.get("expectations", []))
        resolvable_expectation_refs = {
            str(expectation["expectation_id"])
            for expectation in expectations
        }
        expectation_findings = evaluate_expectations(
            call_config_snapshot=request.call_config_snapshot,
            proposal_nodes=request.proposal_nodes,
        )
        executed_stages.append(CORE_STAGE_SEQUENCE[2])

        alignment_observations = extract_observations(
            request.call_config_snapshot,
            request.proposal_nodes,
        )
        expectation_to_check_id = {
            str(expectation["expectation_id"]): str(
                expectation.get("check_id", "check.presence")
            )
            for expectation in expectations
        }
        for observation in alignment_observations:
            if observation.observation_kind == "DEPENDENCY_CONTEXT_MISSING":
                expectation_to_check_id[observation.expectation_ref] = (
                    "check.dependency.context_missing"
                )
                continue
            expectation_to_check_id.setdefault(observation.expectation_ref, "check.presence")
        alignment_findings = evaluate_observations(
            observations=alignment_observations,
            expectation_to_check_id=expectation_to_check_id,
        )
        executed_stages.append(CORE_STAGE_SEQUENCE[3])

        expectation_order = {
            str(expectation["expectation_id"]): index
            for index, expectation in enumerate(expectations)
        }
        diagnostic_findings = aggregate_findings(
            findings=expectation_findings + alignment_findings,
            expectation_order=expectation_order,
        )
        executed_stages.append(CORE_STAGE_SEQUENCE[4])
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
            planned_stage_sequence=list(CORE_STAGE_SEQUENCE),
            executed_stages=executed_stages + [CORE_STAGE_SEQUENCE[5]],
        )

        return PipelineResult(
            request_id=request.request_id,
            pipeline_status="SUCCESS",
            failure_code=None,
            diagnostics=[],
            compatibility_output=build_compatibility_output(review_cards=cards),
            findings=projected_findings,
            review_cards=cards,
            telemetry=telemetry,
        )
    except ReviewCardMappingError as err:
        return _build_failure_result(
            request=request,
            executed_stages=executed_stages + [CORE_STAGE_SEQUENCE[5]],
            error=PipelineContractFailure(str(err)),
        )
    except PipelineContractFailure as err:
        return _build_failure_result(
            request=request,
            executed_stages=executed_stages,
            error=err,
        )
    except Exception as err:
        return _build_failure_result(
            request=request,
            executed_stages=executed_stages,
            error=PipelineExecutionFailure(str(err)),
        )
