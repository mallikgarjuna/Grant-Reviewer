from __future__ import annotations

import re
from typing import Any, Final, TypedDict

EVENT_SCOPE_PULL_REQUEST_ONLY: Final[str] = "pull_request_only"
EVENT_SCOPE_PUSH_SAFE: Final[str] = "push_safe"


class GovernedStep(TypedDict):
    check_id: str
    check_name: str
    event_scope: str


GOVERNED_STEPS: Final[list[GovernedStep]] = [
    {
        "check_id": "contract_boundary_governance_check",
        "check_name": "Contract Boundary Governance Check",
        "event_scope": EVENT_SCOPE_PULL_REQUEST_ONLY,
    },
    {
        "check_id": "wf0053_negative_smoke",
        "check_name": "WF-0053 Negative Smoke (Expected Fail-Closed)",
        "event_scope": EVENT_SCOPE_PULL_REQUEST_ONLY,
    },
    {
        "check_id": "contract_gate_marker",
        "check_name": "Contract Gate (Marker)",
        "event_scope": EVENT_SCOPE_PUSH_SAFE,
    },
    {
        "check_id": "pytest_no_db",
        "check_name": "Test (Pytest no_db)",
        "event_scope": EVENT_SCOPE_PUSH_SAFE,
    },
]


def _normalized_expression(expression: Any) -> str:
    if not isinstance(expression, str):
        return ""
    return " ".join(expression.split())


def _is_pull_request_only_guard(expression: Any) -> bool:
    normalized_expression = _normalized_expression(expression)
    return bool(
        re.search(
            r"github\.event_name\s*==\s*['\"]pull_request['\"]",
            normalized_expression,
        )
    )


def evaluate_workflow_event_scope(
    workflow: dict[str, Any],
    event_name: str,
) -> list[str]:
    backend_job = workflow.get("jobs", {}).get("backend", {})
    step_list = backend_job.get("steps", [])

    if not isinstance(step_list, list):
        return ["Workflow backend.steps must be a list"]

    steps_by_name: dict[str, dict[str, Any]] = {}
    for step in step_list:
        if not isinstance(step, dict):
            continue
        step_name = step.get("name")
        if isinstance(step_name, str):
            steps_by_name[step_name] = step

    violations: list[str] = []
    for governed_step in GOVERNED_STEPS:
        step_name = governed_step["check_name"]
        workflow_step = steps_by_name.get(step_name)
        if workflow_step is None:
            violations.append(f"missing governed step: {step_name}")
            continue

        has_pr_only_guard = _is_pull_request_only_guard(workflow_step.get("if"))
        event_scope = governed_step["event_scope"]

        if event_scope == EVENT_SCOPE_PULL_REQUEST_ONLY and not has_pr_only_guard:
            violations.append(f"missing PR-only guard: {step_name}")

        if (
            event_scope == EVENT_SCOPE_PUSH_SAFE
            and event_name == "push"
            and has_pr_only_guard
        ):
            violations.append(f"push-safe step incorrectly PR-gated: {step_name}")

    return violations
