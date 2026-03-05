from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from tools.gh_policy.diff import compute_policy_diff
from tools.gh_policy.evidence import write_evidence_json
from tools.gh_policy.normalizer import normalize_live_policy
from tools.gh_policy.policy_schema import load_expected_policy


class ReadPolicyClient(Protocol):
    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        ...


class _StaticReadClient:
    def __init__(self, expected_policy: dict[str, Any]) -> None:
        self._expected_policy = expected_policy

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        return {
            "mechanism": "branch_protection",
            "live_policy_raw": {
                "required_status_checks": {
                    "strict": self._expected_policy["toggles"]["strict_required_status_checks"],
                    "contexts": list(self._expected_policy["required_checks"]),
                },
                "enforce_admins": {"enabled": self._expected_policy["toggles"]["enforce_admins"]},
                "allow_force_pushes": {
                    "enabled": self._expected_policy["toggles"]["allow_force_pushes"]
                },
                "allow_deletions": {"enabled": self._expected_policy["toggles"]["allow_deletions"]},
            },
            "endpoints_used": [f"/repos/{repo}/branches/{branch}/protection"],
        }


def run_verify(
    *,
    repo: str,
    branch: str,
    expected_policy_path: Path,
    evidence_path: Path,
    client: ReadPolicyClient | None = None,
) -> int:
    expected_policy = load_expected_policy(expected_policy_path)
    policy_client: ReadPolicyClient = client or _StaticReadClient(expected_policy)
    live_read = policy_client.read_live_policy(repo=repo, branch=branch)
    mechanism = str(live_read["mechanism"])
    live_policy_raw = live_read["live_policy_raw"]
    normalized_policy = normalize_live_policy(
        mechanism=mechanism,
        live_policy_raw=live_policy_raw,
    )
    diff = compute_policy_diff(expected_policy=expected_policy, live_policy=normalized_policy)
    is_drifted = bool(diff)

    write_evidence_json(
        payload={
            "repo": repo,
            "branch": branch,
            "mechanism": mechanism,
            "required_checks": normalized_policy["required_checks"],
            "toggles": normalized_policy["toggles"],
            "live_policy_raw": live_policy_raw,
            "normalized_policy": normalized_policy,
            "drift": {"is_drifted": is_drifted, "diff": diff},
            "error": None,
        },
        output_path=evidence_path,
    )
    return 1 if is_drifted else 0
