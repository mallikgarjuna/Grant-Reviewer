from __future__ import annotations

import pytest

from scripts.evaluate_rollout_health import evaluate_rollout_health

pytestmark = pytest.mark.no_db


def _artifact(
    *,
    total_runs: int = 20,
    parity_passes: int = 20,
    legacy_error_rate: float = 0.02,
    pipeline_error_rate: float = 0.02,
    legacy_contract_error_rate: float = 0.01,
    pipeline_contract_error_rate: float = 0.01,
    legacy_p95_latency_ms: float = 1000.0,
    pipeline_p95_latency_ms: float = 1100.0,
) -> dict[str, object]:
    return {
        "summary": {
            "total_runs": total_runs,
            "structural_parity_passes": parity_passes,
        },
        "metrics": {
            "legacy": {
                "error_rate": legacy_error_rate,
                "contract_error_rate": legacy_contract_error_rate,
                "p95_latency_ms": legacy_p95_latency_ms,
            },
            "pipeline_v1": {
                "error_rate": pipeline_error_rate,
                "contract_error_rate": pipeline_contract_error_rate,
                "p95_latency_ms": pipeline_p95_latency_ms,
            },
        },
    }


def test_evaluate_rollout_health_returns_rollback_on_threshold_breach() -> None:
    result = evaluate_rollout_health(
        _artifact(
            legacy_error_rate=0.02,
            pipeline_error_rate=0.06,  # >=1.5x and >=+0.02
            legacy_p95_latency_ms=1000.0,
            pipeline_p95_latency_ms=1300.0,  # >20% regression
        )
    )

    assert result["overall"]["pass"] is False
    assert result["overall"]["recommended_action"] == "rollback"
    assert "error_rate_regression" in result["overall"]["reasons"]


def test_evaluate_rollout_health_returns_proceed_when_within_thresholds() -> None:
    result = evaluate_rollout_health(
        _artifact(
            legacy_error_rate=0.02,
            pipeline_error_rate=0.025,
            legacy_contract_error_rate=0.01,
            pipeline_contract_error_rate=0.012,
            legacy_p95_latency_ms=1000.0,
            pipeline_p95_latency_ms=1150.0,
        )
    )

    assert result["overall"]["pass"] is True
    assert result["overall"]["recommended_action"] == "proceed"
