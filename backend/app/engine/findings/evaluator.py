from __future__ import annotations

from app.engine.contracts import DiagnosticFindingV1, ObservationV1, SubjectRef
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


def _expectation_reason(*, is_missing_context: bool) -> str:
    if is_missing_context:
        return "missing_context"
    return "content_evaluated"


def _expectation_subordinate_prompt_ids(expectation: dict) -> tuple[str, ...]:
    subordinate_prompts = expectation.get("subordinate_prompts")
    if not isinstance(subordinate_prompts, list):
        return ()

    prompt_ids: list[str] = []
    for prompt in subordinate_prompts:
        if not isinstance(prompt, dict):
            continue
        prompt_id = prompt.get("id")
        if not isinstance(prompt_id, str):
            continue
        normalized_prompt_id = prompt_id.strip()
        if normalized_prompt_id:
            prompt_ids.append(normalized_prompt_id)
    return tuple(prompt_ids)


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


def evaluate_expectations(
    *,
    call_config_snapshot: dict,
    proposal_nodes: dict[str, str],
) -> list[DiagnosticFindingV1]:
    findings: list[DiagnosticFindingV1] = []
    for expectation in call_config_snapshot.get("expectations", []):
        expectation_id = str(expectation["expectation_id"])
        node_logical_id = str(expectation["node_logical_id"])
        check_id = str(expectation.get("check_id", "check.presence"))

        if node_logical_id not in proposal_nodes:
            findings.append(
                DiagnosticFindingV1(
                    finding_id=f"{node_logical_id}:{expectation_id}:{check_id}",
                    primary_expectation_ref=expectation_id,
                    subject_ref=SubjectRef(node_logical_id=node_logical_id),
                    check_id=check_id,
                    finding_kind="PRESENT_CONTENT",
                    severity="NOTE",
                    assessment_status="NOT_ASSESSABLE",
                    reason=f"{_expectation_reason(is_missing_context=True)}:{node_logical_id}",
                )
            )
            continue

        node_text = proposal_nodes.get(node_logical_id, "")
        is_missing = not node_text.strip() and bool(expectation.get("required", False))
        subordinate_prompt_ids = _expectation_subordinate_prompt_ids(expectation)
        reason = _expectation_reason(is_missing_context=False)
        if subordinate_prompt_ids:
            reason = (
                f"{reason};subordinate_prompt_ids="
                + ",".join(subordinate_prompt_ids)
            )
        findings.append(
            DiagnosticFindingV1(
                finding_id=f"{node_logical_id}:{expectation_id}:{check_id}",
                primary_expectation_ref=expectation_id,
                subject_ref=SubjectRef(node_logical_id=node_logical_id),
                check_id=check_id,
                finding_kind="MISSING_CONTENT" if is_missing else "PRESENT_CONTENT",
                severity="ERROR" if is_missing else "NOTE",
                assessment_status="ASSESSED",
                reason=reason,
            )
        )
    return findings
