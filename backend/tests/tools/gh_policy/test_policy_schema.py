from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.gh_policy.policy_schema import (
    REQUIRED_CHECK_CONTEXTS,
    load_expected_policy,
)

pytestmark = [pytest.mark.no_db]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_load_expected_policy_success() -> None:
    policy_path = _repo_root() / "config/platform_policy/main_policy.yaml"

    policy = load_expected_policy(policy_path)

    assert policy["schema_version"] == "v1"
    assert policy["target_branch"] == "main"
    assert policy["required_checks"] == list(REQUIRED_CHECK_CONTEXTS)
    assert policy["toggles"]["enforce_admins"] is True
    assert policy["toggles"]["strict_required_status_checks"] is True


def test_load_expected_policy_missing_required_field_fails(tmp_path: Path) -> None:
    invalid_policy = {
        "schema_version": "v1",
        "required_checks": list(REQUIRED_CHECK_CONTEXTS),
        "toggles": {
            "enforce_admins": True,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "strict_required_status_checks": True,
            "required_pull_request_reviews": False,
            "require_conversation_resolution": False,
            "require_linear_history": False,
            "require_signed_commits": False,
            "bypass_allowances": [],
        },
    }
    policy_path = tmp_path / "missing-target-branch.yaml"
    policy_path.write_text(yaml.safe_dump(invalid_policy, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="missing required field: target_branch"):
        load_expected_policy(policy_path)
