#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ERROR_RATE_MULTIPLIER_THRESHOLD = 1.5
ERROR_RATE_ABSOLUTE_DELTA_THRESHOLD = 0.02
LATENCY_MULTIPLIER_THRESHOLD = 1.2
STAGING_MIN_GREEN_HOURS = 24
PROD_MIN_GREEN_DAYS = 7
PROD_MIN_COMPLETED_REQUESTS_PER_CALL = 50


def _as_float(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def evaluate_rollout_health(
    artifact: dict[str, Any],
    *,
    require_retirement_gate: bool = False,
) -> dict[str, Any]:
    summary = artifact.get("summary")
    metrics = artifact.get("metrics")
    if not isinstance(summary, dict) or not isinstance(metrics, dict):
        return {
            "overall": {
                "pass": False,
                "recommended_action": "rollback",
                "reasons": ["insufficient_data"],
            }
        }

    total_runs = int(summary.get("total_runs", 0))
    parity_passes = int(summary.get("structural_parity_passes", 0))
    parity_ok = total_runs > 0 and parity_passes == total_runs

    legacy_metrics = metrics.get("legacy")
    pipeline_metrics = metrics.get("pipeline_v1")
    if not isinstance(legacy_metrics, dict) or not isinstance(pipeline_metrics, dict):
        return {
            "overall": {
                "pass": False,
                "recommended_action": "rollback",
                "reasons": ["insufficient_data"],
            }
        }

    legacy_error = _as_float(legacy_metrics, "error_rate")
    pipeline_error = _as_float(pipeline_metrics, "error_rate")
    legacy_contract_error = _as_float(legacy_metrics, "contract_error_rate")
    pipeline_contract_error = _as_float(pipeline_metrics, "contract_error_rate")
    legacy_p95 = _as_float(legacy_metrics, "p95_latency_ms")
    pipeline_p95 = _as_float(pipeline_metrics, "p95_latency_ms")

    required_values = [
        legacy_error,
        pipeline_error,
        legacy_contract_error,
        pipeline_contract_error,
        legacy_p95,
        pipeline_p95,
    ]
    if any(value is None for value in required_values):
        return {
            "overall": {
                "pass": False,
                "recommended_action": "rollback",
                "reasons": ["insufficient_data"],
            }
        }

    # mypy doesn't narrow union elements via `any(...)` checks; assert for type safety.
    assert legacy_error is not None
    assert pipeline_error is not None
    assert legacy_contract_error is not None
    assert pipeline_contract_error is not None
    assert legacy_p95 is not None
    assert pipeline_p95 is not None

    error_rate_regression = (
        pipeline_error >= legacy_error * ERROR_RATE_MULTIPLIER_THRESHOLD
        and (pipeline_error - legacy_error) >= ERROR_RATE_ABSOLUTE_DELTA_THRESHOLD
    )
    contract_error_rate_regression = (
        pipeline_contract_error
        >= legacy_contract_error * ERROR_RATE_MULTIPLIER_THRESHOLD
        and (pipeline_contract_error - legacy_contract_error)
        >= ERROR_RATE_ABSOLUTE_DELTA_THRESHOLD
    )
    latency_regression = pipeline_p95 > legacy_p95 * LATENCY_MULTIPLIER_THRESHOLD

    reasons: list[str] = []
    if not parity_ok:
        reasons.append("structural_parity_failure")
    if error_rate_regression:
        reasons.append("error_rate_regression")
    if contract_error_rate_regression:
        reasons.append("contract_error_rate_regression")
    if latency_regression:
        reasons.append("latency_regression")

    retirement_gate = artifact.get("retirement_gate")
    gate_checks = {
        "staging_window_ok": True,
        "prod_window_ok": True,
        "prod_sample_size_ok": True,
    }
    if require_retirement_gate and not isinstance(retirement_gate, dict):
        gate_checks["staging_window_ok"] = False
        gate_checks["prod_window_ok"] = False
        gate_checks["prod_sample_size_ok"] = False
        reasons.append("retirement_gate_missing")
    elif isinstance(retirement_gate, dict):
        environment = str(retirement_gate.get("environment", "")).strip().lower()
        if environment == "staging":
            staging_green_hours = retirement_gate.get("staging_green_hours", 0)
            staging_hours = (
                int(staging_green_hours)
                if isinstance(staging_green_hours, (int, float))
                else 0
            )
            gate_checks["staging_window_ok"] = (
                staging_hours >= STAGING_MIN_GREEN_HOURS
            )
            if not gate_checks["staging_window_ok"]:
                reasons.append("staging_window_incomplete")
        elif environment in {"prod", "production"}:
            production_green_days = retirement_gate.get("production_green_days", 0)
            production_days = (
                int(production_green_days)
                if isinstance(production_green_days, (int, float))
                else 0
            )
            gate_checks["prod_window_ok"] = production_days >= PROD_MIN_GREEN_DAYS
            if not gate_checks["prod_window_ok"]:
                reasons.append("prod_window_incomplete")

            completed_requests_by_call = retirement_gate.get("completed_requests_by_call")
            if not isinstance(completed_requests_by_call, dict) or not completed_requests_by_call:
                gate_checks["prod_sample_size_ok"] = False
            else:
                gate_checks["prod_sample_size_ok"] = all(
                    isinstance(count, (int, float))
                    and int(count) >= PROD_MIN_COMPLETED_REQUESTS_PER_CALL
                    for count in completed_requests_by_call.values()
                )
            if not gate_checks["prod_sample_size_ok"]:
                reasons.append("prod_sample_size_insufficient")
        elif environment:
            gate_checks["staging_window_ok"] = False
            gate_checks["prod_window_ok"] = False
            gate_checks["prod_sample_size_ok"] = False
            reasons.append("invalid_retirement_gate_environment")

    overall_pass = len(reasons) == 0

    return {
        "checks": {
            "parity_ok": parity_ok,
            "error_rate_regression": error_rate_regression,
            "contract_error_rate_regression": contract_error_rate_regression,
            "latency_regression": latency_regression,
            "staging_window_ok": gate_checks["staging_window_ok"],
            "prod_window_ok": gate_checks["prod_window_ok"],
            "prod_sample_size_ok": gate_checks["prod_sample_size_ok"],
        },
        "overall": {
            "pass": overall_pass,
            "recommended_action": "proceed" if overall_pass else "rollback",
            "reasons": reasons,
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate rollout health thresholds from replay artifact JSON."
    )
    parser.add_argument("--input", type=Path, required=True, help="Replay artifact JSON path")
    parser.add_argument(
        "--require-retirement-gate",
        action="store_true",
        help="Require retirement_gate metadata (WF-0040 deletion gate strict mode).",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object")
    result = evaluate_rollout_health(
        payload,
        require_retirement_gate=args.require_retirement_gate,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
