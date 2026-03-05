from __future__ import annotations

from typing import Any

from tools.gh_policy.policy_schema import REQUIRED_TOGGLE_KEYS


def compute_policy_diff(
    *, expected_policy: dict[str, Any], live_policy: dict[str, Any]
) -> list[dict[str, Any]]:
    diff: list[dict[str, Any]] = []

    expected_checks = expected_policy.get("required_checks", [])
    actual_checks = live_policy.get("required_checks", [])
    if expected_checks != actual_checks:
        diff.append(
            {
                "field": "required_checks",
                "expected": expected_checks,
                "actual": actual_checks,
            }
        )

    expected_toggles = expected_policy.get("toggles", {})
    actual_toggles = live_policy.get("toggles", {})
    for key in REQUIRED_TOGGLE_KEYS:
        expected_value = expected_toggles.get(key)
        actual_value = actual_toggles.get(key)
        if expected_value != actual_value:
            diff.append(
                {
                    "field": f"toggles.{key}",
                    "expected": expected_value,
                    "actual": actual_value,
                }
            )

    return diff
