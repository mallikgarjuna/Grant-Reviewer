#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ERROR_RATE_MULTIPLIER_THRESHOLD = 1.5
ERROR_RATE_ABSOLUTE_DELTA_THRESHOLD = 0.02
LATENCY_MULTIPLIER_THRESHOLD = 1.2


def _as_float(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def evaluate_rollout_health(artifact: dict[str, Any]) -> dict[str, Any]:
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

    overall_pass = len(reasons) == 0

    return {
        "checks": {
            "parity_ok": parity_ok,
            "error_rate_regression": error_rate_regression,
            "contract_error_rate_regression": contract_error_rate_regression,
            "latency_regression": latency_regression,
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
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object")
    result = evaluate_rollout_health(payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
