from __future__ import annotations

import pytest

from tools.gh_policy.diff import compute_policy_diff
from tools.gh_policy.normalizer import normalize_live_policy
from tools.gh_policy.policy_schema import REQUIRED_CHECK_CONTEXTS

pytestmark = [pytest.mark.no_db]


def test_normalize_rulesets_and_branch_protection_equivalence() -> None:
    rulesets_payload = [
        {
            "name": "main-policy",
            "rules": [
                {
                    "type": "required_status_checks",
                    "parameters": {
                        "required_status_checks": [
                            {"context": check} for check in REQUIRED_CHECK_CONTEXTS
                        ],
                        "strict_required_status_checks_policy": True,
                    },
                }
            ],
            "enforcement": "active",
            "allows_deletions": False,
            "allows_force_pushes": False,
            "enforce_admins": True,
            "bypass_actors": [],
        }
    ]
    branch_payload = {
        "required_status_checks": {"strict": True, "contexts": list(REQUIRED_CHECK_CONTEXTS)},
        "enforce_admins": {"enabled": True},
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
    }

    rulesets_normalized = normalize_live_policy(
        mechanism="rulesets",
        live_policy_raw=rulesets_payload,
    )
    branch_normalized = normalize_live_policy(
        mechanism="branch_protection",
        live_policy_raw=branch_payload,
    )

    assert rulesets_normalized == branch_normalized


def test_compute_policy_diff_is_minimal_and_deterministic() -> None:
    expected = {
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
    live = {
        "required_checks": list(REQUIRED_CHECK_CONTEXTS[:-1]),
        "toggles": {
            **expected["toggles"],
            "enforce_admins": False,
        },
    }

    diff = compute_policy_diff(expected_policy=expected, live_policy=live)

    assert diff == [
        {
            "field": "required_checks",
            "expected": list(REQUIRED_CHECK_CONTEXTS),
            "actual": list(REQUIRED_CHECK_CONTEXTS[:-1]),
        },
        {
            "field": "toggles.enforce_admins",
            "expected": True,
            "actual": False,
        },
    ]
