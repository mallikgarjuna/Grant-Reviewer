from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from tools.gh_policy.evidence import write_evidence_json
from tools.gh_policy.policy_schema import load_expected_policy
from tools.gh_policy.snapshot import write_snapshot


class ApplyPolicyClient(Protocol):
    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
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


def _write_failure_evidence(
    *,
    evidence_path: Path,
    repo: str,
    branch: str,
    kind: str,
    message: str,
) -> int:
    write_evidence_json(
        payload={
            "repo": repo,
            "branch": branch,
            "mechanism": None,
            "drift": {"is_drifted": False, "diff": []},
            "error": {"kind": kind, "message": message, "endpoint": None},
        },
        output_path=evidence_path,
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
    client: ApplyPolicyClient,
) -> int:
    expected_policy = load_expected_policy(expected_policy_path)
    if not apply_intent:
        return _write_failure_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            kind="apply_intent_required",
            message="Apply requires explicit apply intent",
        )

    missing_checks = [
        check for check in expected_policy["required_checks"] if check not in available_check_contexts
    ]
    if missing_checks:
        return _write_failure_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            kind="missing_required_checks",
            message="Missing required checks: " + ", ".join(missing_checks),
        )

    if not can_mutate:
        return _write_failure_evidence(
            evidence_path=evidence_path,
            repo=repo,
            branch=branch,
            kind="permission_denied",
            message="Mutation not permitted for current actor/token",
        )

    live_read = client.read_live_policy(repo=repo, branch=branch)
    mechanism = str(live_read["mechanism"])
    snapshot_path = write_snapshot(
        repo=repo,
        branch=branch,
        mechanism=mechanism,
        live_policy_raw=live_read["live_policy_raw"],
        captured_from_endpoints=list(live_read.get("endpoints_used", [])),
        snapshot_dir=snapshot_dir,
    )
    client.apply_policy(
        repo=repo,
        branch=branch,
        expected_policy=expected_policy,
        mechanism=mechanism,
        snapshot_path=snapshot_path,
    )
    write_evidence_json(
        payload={
            "repo": repo,
            "branch": branch,
            "mechanism": mechanism,
            "drift": {"is_drifted": False, "diff": []},
            "error": None,
            "snapshot_path": str(snapshot_path),
        },
        output_path=evidence_path,
    )
    return 0
