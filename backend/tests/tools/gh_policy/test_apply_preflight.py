from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.gh_policy.apply import run_apply
from tools.gh_policy.policy_schema import REQUIRED_CHECK_CONTEXTS

pytestmark = [pytest.mark.no_db]


class _FakeApplyClient:
    def __init__(self) -> None:
        self.apply_calls = 0
        self.apply_snapshot_seen = False
        self.discover_calls = 0
        self._discovered_contexts: set[str] = set(REQUIRED_CHECK_CONTEXTS)

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
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

    def apply_policy(
        self,
        *,
        repo: str,
        branch: str,
        expected_policy: dict[str, Any],
        mechanism: str,
        snapshot_path: Path,
    ) -> dict[str, Any]:
        self.apply_calls += 1
        self.apply_snapshot_seen = snapshot_path.exists()
        return {"repo": repo, "branch": branch, "mechanism": mechanism, "expected": expected_policy}

    def discover_check_contexts(self, *, repo: str, branch: str) -> set[str]:
        _ = (repo, branch)
        self.discover_calls += 1
        return set(self._discovered_contexts)


class _DiscoveryFailingClient(_FakeApplyClient):
    def discover_check_contexts(self, *, repo: str, branch: str) -> set[str]:
        _ = (repo, branch)
        raise RuntimeError("simulated discovery outage")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_apply_requires_explicit_intent(tmp_path: Path) -> None:
    client = _FakeApplyClient()
    evidence_path = tmp_path / "apply-evidence.json"

    exit_code = run_apply(
        repo="octo-org/octo-repo",
        branch="main",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        snapshot_dir=tmp_path / "snapshots",
        apply_intent=False,
        available_check_contexts=set(REQUIRED_CHECK_CONTEXTS),
        can_mutate=True,
        client=client,
    )

    assert exit_code != 0
    assert client.apply_calls == 0
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "apply_intent_required"


def test_apply_preflight_missing_required_checks(tmp_path: Path) -> None:
    client = _FakeApplyClient()
    client._discovered_contexts = set(REQUIRED_CHECK_CONTEXTS[:-1])
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
        client=client,
    )

    assert exit_code == 1
    assert client.apply_calls == 0
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "missing_required_checks"


def test_apply_writes_snapshot_before_mutation(tmp_path: Path) -> None:
    client = _FakeApplyClient()
    evidence_path = tmp_path / "apply-evidence.json"
    snapshots_dir = tmp_path / "snapshots"

    exit_code = run_apply(
        repo="octo-org/octo-repo",
        branch="main",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        snapshot_dir=snapshots_dir,
        apply_intent=True,
        available_check_contexts=set(REQUIRED_CHECK_CONTEXTS),
        can_mutate=True,
        client=client,
    )

    assert exit_code == 0
    assert client.apply_calls == 1
    assert client.apply_snapshot_seen is True
    snapshot_files = sorted(snapshots_dir.glob("snapshot_*.json"))
    assert snapshot_files
    snapshot_payload = json.loads(snapshot_files[0].read_text(encoding="utf-8"))
    assert isinstance(snapshot_payload["snapshot_sha256"], str)


def test_apply_preflight_uses_live_context_discovery_and_fails_closed(tmp_path: Path) -> None:
    client = _FakeApplyClient()
    client._discovered_contexts = set(REQUIRED_CHECK_CONTEXTS[:-1])
    evidence_path = tmp_path / "apply-evidence.json"

    exit_code = run_apply(
        repo="octo-org/octo-repo",
        branch="policy-rehearsal",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        snapshot_dir=tmp_path / "snapshots",
        apply_intent=True,
        available_check_contexts=set(REQUIRED_CHECK_CONTEXTS),
        can_mutate=True,
        client=client,
    )

    assert exit_code == 1
    assert client.discover_calls == 1
    assert client.apply_calls == 0
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "missing_required_checks"
    assert payload["preflight"]["decision"] == "fail_closed_missing_required_checks"
    assert payload["preflight"]["available_check_contexts"] == sorted(client._discovered_contexts)
    assert payload["preflight"]["missing_required_checks"] == [REQUIRED_CHECK_CONTEXTS[-1]]


def test_apply_preflight_discovery_error_fails_closed_with_evidence(tmp_path: Path) -> None:
    client = _DiscoveryFailingClient()
    evidence_path = tmp_path / "apply-evidence.json"

    exit_code = run_apply(
        repo="octo-org/octo-repo",
        branch="policy-rehearsal",
        expected_policy_path=_repo_root() / "config/platform_policy/main_policy.yaml",
        evidence_path=evidence_path,
        snapshot_dir=tmp_path / "snapshots",
        apply_intent=True,
        available_check_contexts=set(REQUIRED_CHECK_CONTEXTS),
        can_mutate=True,
        client=client,
    )

    assert exit_code == 1
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "api_failure"
    assert "simulated discovery outage" in payload["error"]["message"]
    assert payload["preflight"]["decision"] == "fail_closed_discovery_error"
