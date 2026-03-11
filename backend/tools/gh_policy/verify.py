from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from tools.gh_policy.diff import compute_policy_diff
from tools.gh_policy.evidence import write_evidence_json
from tools.gh_policy.github_client import (
    GitHubApiError,
    GitHubPolicyClient,
    make_github_rest_fetcher,
)
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
    offline: bool = False,
) -> int:
    expected_policy = load_expected_policy(expected_policy_path)
    if client is not None:
        policy_client: ReadPolicyClient = client
    elif offline:
        policy_client = _StaticReadClient(expected_policy)
    else:
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if not token:
            write_evidence_json(
                payload={
                    "timestamp_utc": datetime.now(UTC).isoformat(),
                    "repo": repo,
                    "branch": branch,
                    "mechanism": None,
                    "drift": {"is_drifted": False, "diff": []},
                    "error": {
                        "kind": "permission_denied",
                        "message": "GITHUB_TOKEN is required for live verify mode",
                        "endpoint": None,
                    },
                },
                output_path=evidence_path,
            )
            return 1
        policy_client = GitHubPolicyClient(fetcher=make_github_rest_fetcher(token=token))

    try:
        live_read = policy_client.read_live_policy(repo=repo, branch=branch)
    except GitHubApiError as err:
        write_evidence_json(
            payload={
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "repo": repo,
                "branch": branch,
                "mechanism": None,
                "drift": {"is_drifted": False, "diff": []},
                "error": {
                    "kind": err.kind,
                    "message": err.message,
                    "endpoint": err.endpoint,
                },
            },
            output_path=evidence_path,
        )
        # Repos without rulesets access cannot perform live drift verify.
        # Record evidence, but do not fail the CI gate for this plan limitation.
        if err.kind == "plan_gated":
            return 0
        return 1

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
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "repo": repo,
            "branch": branch,
            "mechanism": mechanism,
            "required_checks": normalized_policy["required_checks"],
            "toggles": normalized_policy["toggles"],
            "live_policy_raw": live_policy_raw,
            "normalized_policy": normalized_policy,
            "drift": {"is_drifted": is_drifted, "diff": diff},
            "error": None,
            "tooling": {"command_path": "tools.gh_policy.verify.run_verify"},
            "actor": os.getenv("GITHUB_ACTOR", "unknown"),
            "endpoints_used": list(live_read.get("endpoints_used", [])),
        },
        output_path=evidence_path,
    )
    return 1 if is_drifted else 0
