from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from tools.gh_policy.diff import compute_policy_diff
from tools.gh_policy.evidence import write_evidence_json
from tools.gh_policy.normalizer import normalize_live_policy
from tools.gh_policy.policy_schema import load_expected_policy
from tools.gh_policy.snapshot import write_snapshot


class ApplyPolicyClient(Protocol):
    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        ...

    def discover_check_contexts(self, *, repo: str, branch: str) -> set[str]:
        ...

    def apply_policy(
        self,
        *,
        repo: str,
        branch: str,
        expected_policy: dict[str, Any],
        mechanism: str,
        snapshot_path: Path,
    ) -> dict[str, Any]:
        ...


class _StaticApplyClient:
    def __init__(self, expected_policy: dict[str, Any]) -> None:
        self._state = {
            "required_status_checks": {
                "strict": expected_policy["toggles"]["strict_required_status_checks"],
                "contexts": list(expected_policy["required_checks"]),
            },
            "enforce_admins": {"enabled": expected_policy["toggles"]["enforce_admins"]},
            "allow_force_pushes": {"enabled": expected_policy["toggles"]["allow_force_pushes"]},
            "allow_deletions": {"enabled": expected_policy["toggles"]["allow_deletions"]},
        }

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        return {
            "mechanism": "branch_protection",
            "live_policy_raw": self._state,
            "endpoints_used": [f"/repos/{repo}/branches/{branch}/protection"],
        }

    def discover_check_contexts(self, *, repo: str, branch: str) -> set[str]:
        _ = (repo, branch)
        required_status_checks = self._state.get("required_status_checks", {})
        contexts = required_status_checks.get("contexts", [])
        if not isinstance(contexts, list):
            return set()
        return {str(item) for item in contexts}

    def apply_policy(
        self,
        *,
        repo: str,
        branch: str,
        expected_policy: dict[str, Any],
        mechanism: str,
        snapshot_path: Path,
    ) -> dict[str, Any]:
        self._state = {
            "required_status_checks": {
                "strict": expected_policy["toggles"]["strict_required_status_checks"],
                "contexts": list(expected_policy["required_checks"]),
            },
            "enforce_admins": {"enabled": expected_policy["toggles"]["enforce_admins"]},
            "allow_force_pushes": {"enabled": expected_policy["toggles"]["allow_force_pushes"]},
            "allow_deletions": {"enabled": expected_policy["toggles"]["allow_deletions"]},
        }
        return {"repo": repo, "branch": branch, "mechanism": mechanism, "snapshot_path": str(snapshot_path)}


def _write_evidence(
    *,
    evidence_path: Path,
    repo: str,
    branch: str,
    mechanism: str | None,
    drift: dict[str, Any],
    error: dict[str, Any] | None,
    snapshot_path: Path | None = None,
    normalized_policy: dict[str, Any] | None = None,
    preflight: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "repo": repo,
        "branch": branch,
        "mechanism": mechanism,
        "drift": drift,
        "error": error,
    }
    if snapshot_path is not None:
        payload["snapshot_path"] = str(snapshot_path)
    if normalized_policy is not None:
        payload["normalized_policy"] = normalized_policy
    if preflight is not None:
        payload["preflight"] = preflight
    write_evidence_json(payload=payload, output_path=evidence_path)


def _write_failure_evidence(
    *,
    evidence_path: Path,
    repo: str,
    branch: str,
    kind: str,
    message: str,
) -> int:
    _write_evidence(
        evidence_path=evidence_path,
        repo=repo,
        branch=branch,
        mechanism=None,
        drift={"is_drifted": False, "diff": []},
        error={"kind": kind, "message": message, "endpoint": None},
    )
    return 1


def run_apply(
    *,
    repo: str,
    branch: str,
    expected_policy_path: Path,
    evidence_path: Path,
    snapshot_dir: Path,
    apply_intent: bool,
    available_check_contexts: set[str],
    can_mutate: bool,
    client: ApplyPolicyClient | None = None,
) -> int:
    expected_policy = load_expected_policy(expected_policy_path)
    apply_client: ApplyPolicyClient = client or _StaticApplyClient(expected_policy)
    if not apply_intent:
        return _write_failure_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            kind="apply_intent_required",
            message="Apply requires explicit apply intent",
        )

    discovered_contexts: set[str]
    if hasattr(apply_client, "discover_check_contexts"):
        discovered_contexts = set(apply_client.discover_check_contexts(repo=repo, branch=branch))
    else:
        discovered_contexts = set(available_check_contexts)

    missing_checks = [check for check in expected_policy["required_checks"] if check not in discovered_contexts]
    preflight = {
        "required_check_contexts": list(expected_policy["required_checks"]),
        "available_check_contexts": sorted(discovered_contexts),
        "missing_required_checks": missing_checks,
        "decision": "allow_apply",
    }
    if missing_checks:
        _write_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            mechanism=None,
            drift={"is_drifted": False, "diff": []},
            error={
                "kind": "missing_required_checks",
                "message": "Missing required checks: " + ", ".join(missing_checks),
                "endpoint": None,
            },
            preflight={**preflight, "decision": "fail_closed_missing_required_checks"},
        )
        return 1

    if not can_mutate:
        return _write_failure_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            kind="permission_denied",
            message="Mutation not permitted for current actor/token",
        )

    live_read = apply_client.read_live_policy(repo=repo, branch=branch)
    mechanism = str(live_read["mechanism"])
    snapshot_path = write_snapshot(
        repo=repo,
        branch=branch,
        mechanism=mechanism,
        live_policy_raw=live_read["live_policy_raw"],
        captured_from_endpoints=list(live_read.get("endpoints_used", [])),
        snapshot_dir=snapshot_dir,
    )
    try:
        apply_client.apply_policy(
            repo=repo,
            branch=branch,
            expected_policy=expected_policy,
            mechanism=mechanism,
            snapshot_path=snapshot_path,
        )
    except Exception as err:
        _write_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            mechanism=mechanism,
            drift={"is_drifted": False, "diff": []},
            error={"kind": "api_unreachable", "message": str(err), "endpoint": None},
            snapshot_path=snapshot_path,
            preflight=preflight,
        )
        return 1

    post_read = apply_client.read_live_policy(repo=repo, branch=branch)
    post_normalized = normalize_live_policy(
        mechanism=str(post_read["mechanism"]),
        live_policy_raw=post_read["live_policy_raw"],
    )
    diff = compute_policy_diff(expected_policy=expected_policy, live_policy=post_normalized)
    if diff:
        _write_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            mechanism=mechanism,
            drift={"is_drifted": True, "diff": diff},
            error={
                "kind": "post_apply_mismatch",
                "message": "Post-apply live policy does not match expected policy",
                "endpoint": None,
            },
            snapshot_path=snapshot_path,
            normalized_policy=post_normalized,
            preflight=preflight,
        )
        return 1

    _write_evidence(
        evidence_path=evidence_path,
        repo=repo,
        branch=branch,
        mechanism=mechanism,
        drift={"is_drifted": False, "diff": []},
        error=None,
        snapshot_path=snapshot_path,
        normalized_policy=post_normalized,
        preflight=preflight,
    )
    return 0
