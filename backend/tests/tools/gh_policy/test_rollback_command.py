from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.gh_policy.rollback import run_rollback

pytestmark = [pytest.mark.no_db]


class _RollbackClient:
    def __init__(self, *, mismatch_after_restore: bool) -> None:
        self.mismatch_after_restore = mismatch_after_restore
        self.state: dict[str, Any] = {"required_status_checks": {"strict": False, "contexts": []}}

    def restore_policy(self, *, repo: str, branch: str, mechanism: str, live_policy_raw: Any) -> None:
        _ = (repo, branch, mechanism)
        self.state = live_policy_raw

    def read_live_policy(self, *, repo: str, branch: str) -> dict[str, Any]:
        _ = (repo, branch)
        raw = self.state
        if self.mismatch_after_restore:
            raw = {"required_status_checks": {"strict": False, "contexts": ["unexpected"]}}
        return {"mechanism": "branch_protection", "live_policy_raw": raw}


def test_rollback_restore_mismatch_emits_error_evidence(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_payload = {
        "mechanism": "branch_protection",
        "live_policy_raw": {
            "required_status_checks": {"strict": True, "contexts": ["backend / Test (Pytest no_db)"]}
        },
    }
    snapshot_path.write_text(json.dumps(snapshot_payload), encoding="utf-8")

    evidence_path = tmp_path / "rollback-evidence.json"
    exit_code = run_rollback(
        repo="octo-org/octo-repo",
        branch="main",
        snapshot_path=snapshot_path,
        evidence_path=evidence_path,
        client=_RollbackClient(mismatch_after_restore=True),
    )

    assert exit_code == 1
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["error"]["kind"] == "restore_mismatch"
