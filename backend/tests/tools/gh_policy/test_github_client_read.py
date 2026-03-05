from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.gh_policy.github_client import GitHubApiError, GitHubPolicyClient

pytestmark = [pytest.mark.no_db]


def _fixture_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / "fixtures" / filename


def test_read_live_policy_prefers_rulesets() -> None:
    observed_endpoints: list[str] = []

    def fetcher(endpoint: str) -> tuple[int, dict[str, Any] | list[Any]]:
        observed_endpoints.append(endpoint)
        if endpoint.endswith("/rulesets?targets=branch"):
            return 200, [{"id": 10, "name": "main-policy"}]
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    client = GitHubPolicyClient(fetcher=fetcher)
    result = client.read_live_policy(repo="octo-org/octo-repo", branch="main")

    assert result["mechanism"] == "rulesets"
    assert result["live_policy_raw"] == [{"id": 10, "name": "main-policy"}]
    assert observed_endpoints == ["/repos/octo-org/octo-repo/rulesets?targets=branch"]


def test_read_live_policy_falls_back_to_branch_protection() -> None:
    observed_endpoints: list[str] = []

    def fetcher(endpoint: str) -> tuple[int, dict[str, Any] | list[Any]]:
        observed_endpoints.append(endpoint)
        if endpoint.endswith("/rulesets?targets=branch"):
            return 404, {"message": "Not Found"}
        if endpoint.endswith("/branches/main/protection"):
            return 200, {"required_status_checks": {"strict": True, "contexts": []}}
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    client = GitHubPolicyClient(fetcher=fetcher)
    result = client.read_live_policy(repo="octo-org/octo-repo", branch="main")

    assert result["mechanism"] == "branch_protection"
    assert result["live_policy_raw"]["required_status_checks"]["strict"] is True
    assert observed_endpoints == [
        "/repos/octo-org/octo-repo/rulesets?targets=branch",
        "/repos/octo-org/octo-repo/branches/main/protection",
    ]


def test_read_live_policy_plan_gated_maps_error_kind() -> None:
    plan_gated_payload = json.loads(_fixture_path("rulesets_plan_gated.json").read_text())

    def fetcher(endpoint: str) -> tuple[int, dict[str, Any] | list[Any]]:
        if endpoint.endswith("/rulesets?targets=branch"):
            return 403, plan_gated_payload
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    client = GitHubPolicyClient(fetcher=fetcher)

    with pytest.raises(GitHubApiError, match="plan_gated"):
        client.read_live_policy(repo="octo-org/octo-repo", branch="main")


def test_read_live_policy_permission_denied_maps_error_kind() -> None:
    def fetcher(endpoint: str) -> tuple[int, dict[str, Any] | list[Any]]:
        if endpoint.endswith("/rulesets?targets=branch"):
            return 403, {"message": "Resource not accessible by integration"}
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    client = GitHubPolicyClient(fetcher=fetcher)

    with pytest.raises(GitHubApiError, match="permission_denied"):
        client.read_live_policy(repo="octo-org/octo-repo", branch="main")
