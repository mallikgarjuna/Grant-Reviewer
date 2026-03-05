from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.gh_policy.apply import run_apply
from tools.gh_policy.cli import main
from tools.gh_policy.policy_schema import REQUIRED_CHECK_CONTEXTS

pytestmark = [pytest.mark.no_db]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


class _MismatchClient:
    def __init__(self) -> None:
        self.read_count = 0

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        self.read_count += 1
        if self.read_count == 1:
            return {
                "mechanism": "branch_protection",
                "live_policy_raw": {
                    "required_status_checks": {"strict": True, "contexts": list(REQUIRED_CHECK_CONTEXTS)},
                    "enforce_admins": {"enabled": True},
                    "allow_force_pushes": {"enabled": False},
                    "allow_deletions": {"enabled": False},
                },
                "endpoints_used": [f"/repos/{repo}/branches/{branch}/protection"],
            }
        return {
            "mechanism": "branch_protection",
            "live_policy_raw": {
                "required_status_checks": {"strict": False, "contexts": list(REQUIRED_CHECK_CONTEXTS)},
                "enforce_admins": {"enabled": True},
                "allow_force_pushes": {"enabled": False},
                "allow_deletions": {"enabled": False},
            },
            "endpoints_used": [f"/repos/{repo}/branches/{branch}/protection"],
        }

    def apply_policy(self, **_kwargs: Any) -> dict[str, Any]:
        return {"ok": True}


class _FailingApplyClient(_MismatchClient):
    def apply_policy(self, **_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("simulated mutation failure")


def test_apply_post_apply_mismatch_returns_nonzero(tmp_path: Path) -> None:
    evidence_path = tmp_path / "apply-evidence.json"
    exit_code = run_apply(
        repo="octo-org/octo-repo",
        branch="main",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        snapshot_dir=tmp_path / "snapshots",
        apply_intent=True,
        available_check_contexts=set(REQUIRED_CHECK_CONTEXTS),
        can_mutate=True,
        client=_MismatchClient(),
    )

    assert exit_code == 1
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "post_apply_mismatch"
    assert payload["drift"]["is_drifted"] is True
    assert "workflow_run_id" in payload
    assert "commit_sha" in payload
    assert "linked_artifacts" in payload


def test_apply_failure_still_writes_evidence_error_kind_api_failure(tmp_path: Path) -> None:
    evidence_path = tmp_path / "apply-evidence.json"
    exit_code = run_apply(
        repo="octo-org/octo-repo",
        branch="main",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        snapshot_dir=tmp_path / "snapshots",
        apply_intent=True,
        available_check_contexts=set(REQUIRED_CHECK_CONTEXTS),
        can_mutate=True,
        client=_FailingApplyClient(),
    )

    assert exit_code == 1
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "api_failure"
    assert "simulated mutation failure" in payload["error"]["message"]
    assert "workflow_run_id" in payload
    assert "commit_sha" in payload
    assert "linked_artifacts" in payload


def test_apply_success_writes_linked_artifacts_contract_fields(tmp_path: Path) -> None:
    evidence_path = tmp_path / "apply-evidence-success.json"
    exit_code = run_apply(
        repo="octo-org/octo-repo",
        branch="policy-rehearsal",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        snapshot_dir=tmp_path / "snapshots",
        apply_intent=True,
        available_check_contexts=set(REQUIRED_CHECK_CONTEXTS),
        can_mutate=True,
    )

    assert exit_code == 0
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] is None
    assert "workflow_run_id" in payload
    assert "commit_sha" in payload
    assert "linked_artifacts" in payload


def test_apply_rejects_main_branch_for_live_rehearsal(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    evidence_path = tmp_path / "apply-evidence.json"
    snapshot_dir = tmp_path / "snapshots"

    exit_code = main(
        [
            "apply",
            "--repo",
            "octo-org/octo-repo",
            "--branch",
            "main",
            "--apply-intent",
            "--evidence-path",
            str(evidence_path),
            "--snapshot-dir",
            str(snapshot_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "apply forbids --branch main during WF-0056 live rehearsal" in captured.err
