from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts.ci_policy_inventory import EVENT_SCOPE_PULL_REQUEST_ONLY, GOVERNED_STEPS

pytestmark = [pytest.mark.no_db]


def _load_ci_workflow() -> dict[str, Any]:
    workflow_path = Path(__file__).resolve().parents[3] / ".github/workflows/ci.yml"
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


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
