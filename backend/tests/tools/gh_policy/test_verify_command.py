from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.gh_policy.verify import run_verify

pytestmark = [pytest.mark.no_db]


class _FakeClient:
    def __init__(self) -> None:
        self.mutation_attempted = False

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        return {
            "mechanism": "branch_protection",
            "live_policy_raw": {
                "required_status_checks": {"strict": False, "contexts": []},
                "enforce_admins": {"enabled": False},
                "allow_force_pushes": {"enabled": False},
                "allow_deletions": {"enabled": False},
            },
            "endpoints_used": [f"/repos/{repo}/branches/{branch}/protection"],
        }

    def apply_policy(self, *_args: Any, **_kwargs: Any) -> None:
        self.mutation_attempted = True
        raise AssertionError("verify must never call mutation methods")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_verify_drift_returns_nonzero_and_no_mutation(tmp_path: Path) -> None:
    client = _FakeClient()
    evidence_path = tmp_path / "verify-evidence.json"

    exit_code = run_verify(
        repo="octo-org/octo-repo",
        branch="main",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        client=client,
    )

    assert exit_code == 1
    assert client.mutation_attempted is False

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["drift"]["is_drifted"] is True
    assert payload["drift"]["diff"]
    assert "error" in payload and "kind" in payload["error"]
    assert "workflow_run_id" in payload
    assert "commit_sha" in payload
    assert "linked_artifacts" in payload


def test_verify_live_mode_without_token_fails_closed_error_kind_permission_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    evidence_path = tmp_path / "verify-live-evidence.json"

    exit_code = run_verify(
        repo="octo-org/octo-repo",
        branch="main",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
    )

    assert exit_code == 1
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "permission_denied"
    assert "workflow_run_id" in payload
    assert "commit_sha" in payload
    assert "linked_artifacts" in payload


def test_verify_offline_success_includes_linked_artifacts_contract(tmp_path: Path) -> None:
    evidence_path = tmp_path / "verify-offline-evidence.json"

    exit_code = run_verify(
        repo="octo-org/octo-repo",
        branch="main",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        offline=True,
    )

    assert exit_code == 0
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] is None
    assert "workflow_run_id" in payload
    assert "commit_sha" in payload
    assert "linked_artifacts" in payload
