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


def _load_workflow(filename: str) -> dict[str, Any]:
    workflow_path = Path(__file__).resolve().parents[3] / ".github/workflows" / filename
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def _load_ci_workflow() -> dict[str, Any]:
    return _load_workflow("ci.yml")


def _load_verify_platform_policy_workflow() -> dict[str, Any]:
    return _load_workflow("verify-platform-policy.yml")


def _load_live_rehearsal_workflow() -> dict[str, Any]:
    return _load_workflow("platform-policy-live-rehearsal.yml")


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


def test_wf0054_ci_policy_accepts_double_quoted_pr_guard() -> None:
    workflow = _load_ci_workflow()
    backend_steps = _backend_steps(workflow)
    step_name = "Contract Boundary Governance Check"

    for step in backend_steps:
        if step.get("name") == step_name:
            step["if"] = 'github.event_name == "pull_request"'
            break
    else:
        pytest.fail(f"Unable to locate step '{step_name}' to update guard expression")

    violations = evaluate_workflow_event_scope(workflow=workflow, event_name="push")

    assert not any(
        "missing PR-only guard" in violation and step_name in violation
        for violation in violations
    )


def test_wf0054_ci_policy_missing_governed_step_fails() -> None:
    workflow = _load_ci_workflow()
    backend_steps = _backend_steps(workflow)
    step_name = "Contract Boundary Governance Check"

    filtered_steps = [step for step in backend_steps if step.get("name") != step_name]
    workflow["jobs"]["backend"]["steps"] = filtered_steps
    violations = evaluate_workflow_event_scope(workflow=workflow, event_name="push")

    assert f"missing governed step: {step_name}" in violations


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


def _wf0055_verify_workflow_violations(workflow: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if workflow.get("name") != "verify-platform-policy":
        violations.append("workflow name must be verify-platform-policy")

    trigger_config = workflow.get("on")
    if trigger_config is None:
        trigger_config = workflow.get(True, {})
    pull_request_trigger = trigger_config.get("pull_request") if isinstance(trigger_config, dict) else None
    if not isinstance(pull_request_trigger, dict):
        violations.append("workflow must define pull_request trigger mapping")
    else:
        branches = pull_request_trigger.get("branches")
        if branches != ["main"]:
            violations.append("workflow pull_request trigger must target main branch")

    jobs = workflow.get("jobs", {})
    verify_job = jobs.get("verify_platform_policy", {})
    if not isinstance(verify_job, dict):
        violations.append("workflow must define verify_platform_policy job")
        return violations

    if verify_job.get("name") != "backend / Verify Platform Policy":
        violations.append("verify job context name mismatch")

    steps = verify_job.get("steps", [])
    verify_step = None
    for step in steps:
        if isinstance(step, dict) and step.get("name") == "Verify platform policy (verify-only)":
            verify_step = step
            break
    if verify_step is None:
        violations.append("missing verify-only execution step")
        return violations

    run_command = verify_step.get("run")
    if not isinstance(run_command, str):
        violations.append("verify-only step must define string run command")
    else:
        if "python -m tools.gh_policy.cli verify" not in run_command:
            violations.append("verify-only step must run policy verify CLI")
        if "--verify-only" not in run_command:
            violations.append("verify-only step must pass --verify-only")

    env_config = verify_step.get("env")
    if not isinstance(env_config, dict) or env_config.get("GITHUB_TOKEN") != "${{ github.token }}":
        violations.append("verify-only step must export GITHUB_TOKEN from github.token")

    return violations


def test_wf0055_platform_policy_verify_workflow_contract() -> None:
    workflow = _load_verify_platform_policy_workflow()
    violations = _wf0055_verify_workflow_violations(workflow)

    assert violations == []


def test_wf0055_platform_policy_verify_workflow_missing_pr_trigger_fails() -> None:
    workflow = _load_verify_platform_policy_workflow()
    workflow["on"] = {"push": {"branches": ["main"]}}

    violations = _wf0055_verify_workflow_violations(workflow)

    assert "workflow must define pull_request trigger mapping" in violations


def _wf0056_live_rehearsal_verify_tracer_violations(workflow: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    trigger_config = workflow.get("on")
    if trigger_config is None:
        trigger_config = workflow.get(True, {})
    if not isinstance(trigger_config, dict) or "workflow_dispatch" not in trigger_config:
        violations.append("workflow must define workflow_dispatch trigger")

    jobs = workflow.get("jobs", {})
    verify_job = jobs.get("verify-main")
    if not isinstance(verify_job, dict):
        violations.append("workflow must define verify-main job")
        return violations

    steps = verify_job.get("steps", [])
    verify_command_found = False
    evidence_upload_found = False
    for step in steps:
        if not isinstance(step, dict):
            continue
        run_command = step.get("run")
        if isinstance(run_command, str) and "python -m tools.gh_policy.cli verify" in run_command:
            if "--branch main" in run_command:
                verify_command_found = True
        uses = step.get("uses")
        with_config = step.get("with")
        if isinstance(uses, str) and uses.startswith("actions/upload-artifact@"):
            if isinstance(with_config, dict) and with_config.get(
                "path"
            ) == "docs/walkthroughs/evidence/WF-0056/":
                evidence_upload_found = True

    if not verify_command_found:
        violations.append("verify-main job must run verify CLI against --branch main")
    if not evidence_upload_found:
        violations.append("verify-main job must upload WF-0056 evidence artifact path")

    return violations


def test_wf0056_live_rehearsal_verify_tracer_contract() -> None:
    workflow = _load_live_rehearsal_workflow()
    violations = _wf0056_live_rehearsal_verify_tracer_violations(workflow)

    assert violations == []


def _wf0056_live_rehearsal_apply_violations(workflow: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    jobs = workflow.get("jobs", {})
    apply_job = jobs.get("apply-rehearsal")
    if not isinstance(apply_job, dict):
        violations.append("workflow must define apply-rehearsal job")
        return violations

    steps = apply_job.get("steps", [])
    apply_command_found = False
    apply_evidence_upload_found = False
    snapshot_upload_found = False
    for step in steps:
        if not isinstance(step, dict):
            continue
        run_command = step.get("run")
        if isinstance(run_command, str) and "python -m tools.gh_policy.cli apply" in run_command:
            if "--branch policy-rehearsal" in run_command and "--apply-intent" in run_command:
                apply_command_found = True
        uses = step.get("uses")
        with_config = step.get("with")
        if isinstance(uses, str) and uses.startswith("actions/upload-artifact@"):
            if not isinstance(with_config, dict):
                continue
            path = with_config.get("path")
            if path == "docs/walkthroughs/evidence/WF-0056/apply_evidence.json":
                apply_evidence_upload_found = True
            if path == "docs/walkthroughs/evidence/WF-0056/snapshots":
                snapshot_upload_found = True

    if not apply_command_found:
        violations.append(
            "apply-rehearsal job must run apply CLI for --branch policy-rehearsal with --apply-intent"
        )
    if not apply_evidence_upload_found:
        violations.append("apply-rehearsal job must upload apply evidence artifact")
    if not snapshot_upload_found:
        violations.append("apply-rehearsal job must upload snapshot artifact")

    return violations


def test_wf0056_live_rehearsal_apply_contract() -> None:
    workflow = _load_live_rehearsal_workflow()
    violations = _wf0056_live_rehearsal_apply_violations(workflow)

    assert violations == []
