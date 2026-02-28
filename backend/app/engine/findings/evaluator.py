from __future__ import annotations

from app.engine.contracts import DiagnosticFindingV1, ObservationV1
from app.engine.findings.check_catalog import ALLOWED_CHECK_IDS


class FindingEvaluationError(ValueError):
    def __init__(self, *, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _build_reason(observation: ObservationV1) -> str:
    if observation.observation_kind == "DEPENDENCY_CONTEXT_MISSING":
        return f"missing_dependencies={observation.details.get('missing_dependencies', [])}"
    return "content_evaluated"


def evaluate_observations(
    *,
    observations: list[ObservationV1],
    expectation_to_check_id: dict[str, str],
) -> list[DiagnosticFindingV1]:
    findings: list[DiagnosticFindingV1] = []
    for observation in observations:
        expectation_ref = observation.expectation_ref
        check_id = expectation_to_check_id.get(expectation_ref, "check.presence")
        if check_id not in ALLOWED_CHECK_IDS:
            raise FindingEvaluationError(
                code="UNKNOWN_CHECK_ID",
                message=f"Unknown check_id: {check_id}",
            )

        is_dependency_missing = observation.observation_kind == "DEPENDENCY_CONTEXT_MISSING"
        findings.append(
            DiagnosticFindingV1(
                finding_id=f"finding:{observation.observation_id}:{check_id}",
                primary_expectation_ref=expectation_ref,
                subject_ref=observation.subject_ref,
                check_id=check_id,
                finding_kind=(
                    "MISSING_CONTENT" if is_dependency_missing else "PRESENT_CONTENT"
                ),
                severity="ERROR" if is_dependency_missing else "NOTE",
                assessment_status=(
                    "NOT_ASSESSABLE" if is_dependency_missing else "ASSESSED"
                ),
                reason=_build_reason(observation),
            )
        )

    return findings
