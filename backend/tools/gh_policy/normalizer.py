from __future__ import annotations

from typing import Any

from tools.gh_policy.policy_schema import REQUIRED_CHECK_CONTEXTS, REQUIRED_TOGGLE_KEYS


def _canonicalize_required_checks(raw_checks: list[str]) -> list[str]:
    observed = set(raw_checks)
    canonical = [check for check in REQUIRED_CHECK_CONTEXTS if check in observed]
    extras = sorted(check for check in observed if check not in REQUIRED_CHECK_CONTEXTS)
    return canonical + extras


def _base_toggles() -> dict[str, Any]:
    return {
        "enforce_admins": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "strict_required_status_checks": False,
        "required_pull_request_reviews": False,
        "require_conversation_resolution": False,
        "require_linear_history": False,
        "require_signed_commits": False,
        "bypass_allowances": [],
    }


def _normalize_rulesets_payload(live_policy_raw: list[dict[str, Any]]) -> dict[str, Any]:
    primary = live_policy_raw[0] if live_policy_raw else {}
    required_checks: list[str] = []
    strict = False
    for rule in primary.get("rules", []):
        if rule.get("type") != "required_status_checks":
            continue
        parameters = rule.get("parameters", {})
        required_checks = [
            item.get("context")
            for item in parameters.get("required_status_checks", [])
            if isinstance(item, dict) and isinstance(item.get("context"), str)
        ]
        strict = bool(parameters.get("strict_required_status_checks_policy", False))
        break

    toggles = _base_toggles()
    toggles["strict_required_status_checks"] = strict
    toggles["enforce_admins"] = bool(primary.get("enforce_admins", False))
    toggles["allow_force_pushes"] = bool(primary.get("allows_force_pushes", False))
    toggles["allow_deletions"] = bool(primary.get("allows_deletions", False))
    toggles["bypass_allowances"] = list(primary.get("bypass_actors", []))

    return {
        "required_checks": _canonicalize_required_checks(required_checks),
        "toggles": {key: toggles[key] for key in REQUIRED_TOGGLE_KEYS},
    }


def _normalize_branch_protection_payload(live_policy_raw: dict[str, Any]) -> dict[str, Any]:
    required_status_checks = live_policy_raw.get("required_status_checks", {})
    raw_contexts = required_status_checks.get("contexts", []) if isinstance(
        required_status_checks, dict
    ) else []
    required_checks = [context for context in raw_contexts if isinstance(context, str)]

    toggles = _base_toggles()
    toggles["strict_required_status_checks"] = bool(
        required_status_checks.get("strict", False)
        if isinstance(required_status_checks, dict)
        else False
    )
    toggles["enforce_admins"] = bool(live_policy_raw.get("enforce_admins", {}).get("enabled", False))
    toggles["allow_force_pushes"] = bool(
        live_policy_raw.get("allow_force_pushes", {}).get("enabled", False)
    )
    toggles["allow_deletions"] = bool(live_policy_raw.get("allow_deletions", {}).get("enabled", False))

    return {
        "required_checks": _canonicalize_required_checks(required_checks),
        "toggles": {key: toggles[key] for key in REQUIRED_TOGGLE_KEYS},
    }


def normalize_live_policy(*, mechanism: str, live_policy_raw: Any) -> dict[str, Any]:
    if mechanism == "rulesets":
        if not isinstance(live_policy_raw, list):
            raise ValueError("rulesets payload must be a list")
        return _normalize_rulesets_payload(live_policy_raw)

    if mechanism == "branch_protection":
        if not isinstance(live_policy_raw, dict):
            raise ValueError("branch protection payload must be a mapping")
        return _normalize_branch_protection_payload(live_policy_raw)

    raise ValueError(f"unsupported mechanism: {mechanism}")
