from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class GitHubApiError(Exception):
    kind: str
    message: str
    endpoint: str
    status_code: int

    def __str__(self) -> str:
        return f"{self.kind}: {self.message} (endpoint={self.endpoint}, status={self.status_code})"


Fetcher = Callable[[str], tuple[int, dict[str, Any] | list[Any]]]


def make_github_rest_fetcher(
    *,
    token: str,
    api_base: str = "https://api.github.com",
) -> Fetcher:
    def _fetch(endpoint: str) -> tuple[int, dict[str, Any] | list[Any]]:
        url = api_base.rstrip("/") + endpoint
        req = request.Request(
            url=url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "wf-0055-platform-policy-enforcement",
            },
            method="GET",
        )
        try:
            with request.urlopen(req, timeout=30) as resp:  # noqa: S310
                body = resp.read().decode("utf-8")
                return int(resp.status), json.loads(body) if body else {}
        except HTTPError as err:
            body = err.read().decode("utf-8")
            payload: dict[str, Any] | list[Any]
            if not body:
                payload = {"message": str(err)}
            else:
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = {"message": body}
            return int(err.code), payload
        except URLError as err:
            return 503, {"message": str(err)}

    return _fetch


def _classify_error_kind(*, status_code: int, payload: dict[str, Any]) -> str:
    message = str(payload.get("message", "")).lower()
    if status_code == 403 and ("upgrade" in message or "public" in message):
        return "plan_gated"
    if status_code == 403:
        return "permission_denied"
    return "api_unreachable"


class GitHubPolicyClient:
    def __init__(self, *, fetcher: Fetcher) -> None:
        self._fetcher = fetcher

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        rulesets_endpoint = f"/repos/{repo}/rulesets?targets=branch"
        status_code, payload = self._fetcher(rulesets_endpoint)
        if status_code == 200:
            if not isinstance(payload, list):
                raise GitHubApiError(
                    kind="api_unreachable",
                    message="rulesets response must be a list",
                    endpoint=rulesets_endpoint,
                    status_code=status_code,
                )
            return {
                "mechanism": "rulesets",
                "live_policy_raw": payload,
                "endpoints_used": [rulesets_endpoint],
            }

        if status_code not in (404, 422):
            if not isinstance(payload, dict):
                payload = {"message": "Unexpected non-object error payload"}
            kind = _classify_error_kind(status_code=status_code, payload=payload)
            raise GitHubApiError(
                kind=kind,
                message=str(payload.get("message", "GitHub API request failed")),
                endpoint=rulesets_endpoint,
                status_code=status_code,
            )

        branch_endpoint = f"/repos/{repo}/branches/{branch}/protection"
        branch_status, branch_payload = self._fetcher(branch_endpoint)
        if branch_status == 200:
            if not isinstance(branch_payload, dict):
                raise GitHubApiError(
                    kind="api_unreachable",
                    message="branch protection response must be an object",
                    endpoint=branch_endpoint,
                    status_code=branch_status,
                )
            return {
                "mechanism": "branch_protection",
                "live_policy_raw": branch_payload,
                "endpoints_used": [rulesets_endpoint, branch_endpoint],
            }

        if not isinstance(branch_payload, dict):
            branch_payload = {"message": "Unexpected non-object error payload"}
        kind = _classify_error_kind(status_code=branch_status, payload=branch_payload)
        raise GitHubApiError(
            kind=kind,
            message=str(branch_payload.get("message", "GitHub API request failed")),
            endpoint=branch_endpoint,
            status_code=branch_status,
        )

    def discover_check_contexts(self, *, repo: str, branch: str) -> set[str]:
        endpoint = f"/repos/{repo}/commits/{branch}/check-runs"
        status_code, payload = self._fetcher(endpoint)
        if status_code != 200:
            if not isinstance(payload, dict):
                payload = {"message": "Unexpected non-object error payload"}
            kind = _classify_error_kind(status_code=status_code, payload=payload)
            raise GitHubApiError(
                kind=kind,
                message=str(payload.get("message", "GitHub API request failed")),
                endpoint=endpoint,
                status_code=status_code,
            )
        if not isinstance(payload, dict):
            raise GitHubApiError(
                kind="api_unreachable",
                message="check-runs response must be an object",
                endpoint=endpoint,
                status_code=status_code,
            )
        check_runs = payload.get("check_runs", [])
        if not isinstance(check_runs, list):
            raise GitHubApiError(
                kind="api_unreachable",
                message="check-runs payload must include a list check_runs field",
                endpoint=endpoint,
                status_code=status_code,
            )

        contexts: set[str] = set()
        for check_run in check_runs:
            if not isinstance(check_run, dict):
                continue
            name = check_run.get("name")
            if isinstance(name, str) and name.strip():
                contexts.add(name)
        return contexts
