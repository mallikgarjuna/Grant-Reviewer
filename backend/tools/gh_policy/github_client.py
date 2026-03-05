from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GitHubApiError(Exception):
    kind: str
    message: str
    endpoint: str
    status_code: int

    def __str__(self) -> str:
        return f"{self.kind}: {self.message} (endpoint={self.endpoint}, status={self.status_code})"


Fetcher = Callable[[str], tuple[int, dict[str, Any] | list[Any]]]


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
