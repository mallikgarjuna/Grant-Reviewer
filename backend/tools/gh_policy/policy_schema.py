from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED_CHECK_CONTEXTS: tuple[str, ...] = (
    "backend / Contract Boundary Governance Check",
    "backend / WF-0054 CI Policy Regression Sweep",
    "backend / Contract Gate (Marker)",
    "backend / Test (Pytest no_db)",
    "frontend / Lint",
    "frontend / Build",
)

REQUIRED_TOGGLE_KEYS: tuple[str, ...] = (
    "enforce_admins",
    "allow_force_pushes",
    "allow_deletions",
    "strict_required_status_checks",
    "required_pull_request_reviews",
    "require_conversation_resolution",
    "require_linear_history",
    "require_signed_commits",
    "bypass_allowances",
)


def _normalize_toggles(raw_toggles: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key in REQUIRED_TOGGLE_KEYS:
        if key not in raw_toggles:
            raise ValueError(f"missing required toggle: {key}")
        normalized[key] = raw_toggles[key]
    return normalized


def load_expected_policy(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("policy must be a mapping")

    for required_field in ("schema_version", "target_branch", "required_checks", "toggles"):
        if required_field not in parsed:
            raise ValueError(f"missing required field: {required_field}")

    required_checks = parsed["required_checks"]
    if required_checks != list(REQUIRED_CHECK_CONTEXTS):
        raise ValueError("required_checks must match WF-0055 canonical contexts in order")

    toggles = parsed["toggles"]
    if not isinstance(toggles, dict):
        raise ValueError("toggles must be a mapping")

    return {
        **parsed,
        "required_checks": list(REQUIRED_CHECK_CONTEXTS),
        "toggles": _normalize_toggles(toggles),
    }
