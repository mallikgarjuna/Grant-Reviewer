from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts.ci_policy_inventory import (
    EVENT_SCOPE_PULL_REQUEST_ONLY,
    GOVERNED_STEPS,
    evaluate_workflow_event_scope,
)

pytestmark = [pytest.mark.no_db]

WF0047_COMPLETED_STATUS_VALUES = {"completed", "done"}


def _load_ci_workflow() -> dict[str, Any]:
    workflow_path = Path(__file__).resolve().parents[3] / ".github/workflows/ci.yml"
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def _read_header_status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip()
    pytest.fail(f"Missing 'Status:' header in {path}")


def _read_wf0047_index_status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| WF-0047 "):
            columns = [column.strip() for column in line.split("|")]
            if len(columns) < 3:
                pytest.fail("WF-0047 index row has unexpected table shape")
            return columns[-2]
    pytest.fail("WF-0047 row missing from docs/index.md")


def _backend_steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return workflow["jobs"]["backend"]["steps"]


def _find_step_if_expression(
    steps: list[dict[str, Any]],
    step_name: str,
) -> str:
    for step in steps:
        if step.get("name") == step_name:
            if_expression = step.get("if")
            assert isinstance(if_expression, str), (
                f"Step '{step_name}' must define an explicit string if-expression"
            )
            return if_expression.strip()
    pytest.fail(f"Unable to locate governed step '{step_name}' in backend CI workflow")


def test_wf0054_ci_policy_inventory_pr_only_tracer() -> None:
    workflow = _load_ci_workflow()
    steps = _backend_steps(workflow)

    governed_pr_steps = [
        item for item in GOVERNED_STEPS if item["event_scope"] == EVENT_SCOPE_PULL_REQUEST_ONLY
    ]
    assert governed_pr_steps, "Inventory must define at least one pull_request-only governed step"

    tracer_step = governed_pr_steps[0]
    if_expression = _find_step_if_expression(steps, tracer_step["check_name"])

    assert if_expression == "github.event_name == 'pull_request'"


def test_wf0054_ci_policy_event_scope_pr_positive() -> None:
    workflow = _load_ci_workflow()

    violations = evaluate_workflow_event_scope(workflow=workflow, event_name="pull_request")

    assert violations == []


def test_wf0054_ci_policy_event_scope_push_negative() -> None:
    workflow = _load_ci_workflow()

    violations = evaluate_workflow_event_scope(workflow=workflow, event_name="push")

    assert violations == []


def test_wf0054_ci_policy_negative_removed_pr_guard_fails() -> None:
    workflow = _load_ci_workflow()
    backend_steps = _backend_steps(workflow)
    step_name = "Contract Boundary Governance Check"

    for step in backend_steps:
        if step.get("name") == step_name:
            step.pop("if", None)
            break
    else:
        pytest.fail(f"Unable to locate step '{step_name}' to remove PR guard")

    violations = evaluate_workflow_event_scope(workflow=workflow, event_name="push")

    assert any(
        "missing PR-only guard" in violation and step_name in violation
        for violation in violations
    )


def test_wf0054_ci_policy_wf0047_status_alignment() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    task_status = _read_header_status(
        repo_root / "docs/tasks/completed/task-WF-0047-git-hooks-rule-enforcement.md"
    )
    walkthrough_status = _read_header_status(
        repo_root
        / "docs/walkthroughs/completed/walkthrough-WF-0047-git-hooks-rule-enforcement.md"
    )
    index_status = _read_wf0047_index_status(repo_root / "docs/index.md")

    mismatches: list[str] = []
    if task_status.lower() not in WF0047_COMPLETED_STATUS_VALUES:
        mismatches.append(
            f"task_status={task_status!r} is not one of {sorted(WF0047_COMPLETED_STATUS_VALUES)}"
        )
    if walkthrough_status.lower() not in WF0047_COMPLETED_STATUS_VALUES:
        mismatches.append(
            "walkthrough_status="
            f"{walkthrough_status!r} is not one of {sorted(WF0047_COMPLETED_STATUS_VALUES)}"
        )
    if index_status.lower() not in WF0047_COMPLETED_STATUS_VALUES:
        mismatches.append(
            f"index_status={index_status!r} is not one of {sorted(WF0047_COMPLETED_STATUS_VALUES)}"
        )

    assert not mismatches, "WF-0047 status mismatch: " + "; ".join(mismatches)
