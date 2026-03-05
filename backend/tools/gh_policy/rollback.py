from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from tools.gh_policy.evidence import write_evidence_json


class RollbackClient(Protocol):
    def restore_policy(self, *, repo: str, branch: str, mechanism: str, live_policy_raw: Any) -> None:
        ...

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        ...


class _StaticRollbackClient:
    def __init__(self) -> None:
        self._state: Any = {}

    def restore_policy(self, *, repo: str, branch: str, mechanism: str, live_policy_raw: Any) -> None:
        _ = (repo, branch, mechanism)
        self._state = live_policy_raw

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        return {
            "mechanism": "branch_protection",
            "live_policy_raw": self._state,
            "endpoints_used": [f"/repos/{repo}/branches/{branch}/protection"],
        }


def _load_snapshot(snapshot_path: Path) -> dict[str, Any]:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a mapping")
    if "mechanism" not in snapshot:
        raise ValueError("snapshot missing mechanism")
    if "live_policy_raw" not in snapshot:
        raise ValueError("snapshot missing live_policy_raw")
    return snapshot


def _build_rollback_evidence_payload(
    *,
    repo: str,
    branch: str,
    mechanism: str,
    drift: dict[str, Any],
    error: dict[str, Any] | None,
    snapshot_path: Path,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    source_snapshot: dict[str, Any] = {"path": str(snapshot_path)}
    snapshot_sha = snapshot.get("snapshot_sha256")
    if isinstance(snapshot_sha, str):
        source_snapshot["snapshot_sha256"] = snapshot_sha
    return {
        "repo": repo,
        "branch": branch,
        "mechanism": mechanism,
        "drift": drift,
        "error": error,
        "source_snapshot": source_snapshot,
        "linked_artifacts": [str(snapshot_path)],
    }


def run_rollback(
    *,
    repo: str,
    branch: str,
    snapshot_path: Path,
    evidence_path: Path,
    client: RollbackClient | None = None,
) -> int:
    rollback_client: RollbackClient = client or _StaticRollbackClient()
    snapshot = _load_snapshot(snapshot_path)
    mechanism = str(snapshot["mechanism"])
    snapshot_raw = snapshot["live_policy_raw"]

    try:
        rollback_client.restore_policy(
            repo=repo,
            branch=branch,
            mechanism=mechanism,
            live_policy_raw=snapshot_raw,
        )
        post_restore = rollback_client.read_live_policy(repo=repo, branch=branch)
    except Exception as err:
        write_evidence_json(
            payload=_build_rollback_evidence_payload(
                repo=repo,
                branch=branch,
                mechanism=mechanism,
                drift={"is_drifted": True, "diff": []},
                error={"kind": "api_unreachable", "message": str(err), "endpoint": None},
                snapshot_path=snapshot_path,
                snapshot=snapshot,
            ),
            output_path=evidence_path,
        )
        return 1

    post_raw = post_restore.get("live_policy_raw")
    if post_raw != snapshot_raw:
        write_evidence_json(
            payload=_build_rollback_evidence_payload(
                repo=repo,
                branch=branch,
                mechanism=mechanism,
                drift={"is_drifted": True, "diff": [{"field": "live_policy_raw"}]},
                error={
                    "kind": "restore_mismatch",
                    "message": "Rollback restore verification failed",
                    "endpoint": None,
                },
                snapshot_path=snapshot_path,
                snapshot=snapshot,
            ),
            output_path=evidence_path,
        )
        return 1

    write_evidence_json(
        payload=_build_rollback_evidence_payload(
            repo=repo,
            branch=branch,
            mechanism=mechanism,
            drift={"is_drifted": False, "diff": []},
            error=None,
            snapshot_path=snapshot_path,
            snapshot=snapshot,
        ),
        output_path=evidence_path,
    )
    return 0
