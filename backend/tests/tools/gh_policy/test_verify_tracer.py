from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.gh_policy.cli import main

pytestmark = [pytest.mark.no_db]


def test_verify_tracer_writes_evidence_json(tmp_path: Path) -> None:
    evidence_path = tmp_path / "evidence.json"

    exit_code = main(
        [
            "verify",
            "--repo",
            "octo-org/octo-repo",
            "--branch",
            "main",
            "--verify-only",
            "--evidence-path",
            str(evidence_path),
        ]
    )

    assert exit_code == 0
    assert evidence_path.exists()

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["mechanism"] == "branch_protection"
    assert payload["drift"] == {"is_drifted": False, "diff": []}
    assert isinstance(payload["evidence_sha256"], str)
    assert len(payload["evidence_sha256"]) == 64
