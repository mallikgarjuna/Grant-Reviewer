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


def _retirement_gate(
    *,
    environment: str,
    staging_green_hours: int = 24,
    production_green_days: int = 7,
    completed_requests_by_call: dict[str, int] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "environment": environment,
        "staging_green_hours": staging_green_hours,
        "production_green_days": production_green_days,
    }
    if completed_requests_by_call is not None:
        payload["completed_requests_by_call"] = completed_requests_by_call
    return payload


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


def test_evaluate_rollout_health_rolls_back_when_staging_window_below_24h() -> None:
    artifact = _artifact()
    artifact["retirement_gate"] = _retirement_gate(
        environment="staging",
        staging_green_hours=12,
    )

    result = evaluate_rollout_health(artifact)

    assert result["overall"]["pass"] is False
    assert result["overall"]["recommended_action"] == "rollback"
    assert "staging_window_incomplete" in result["overall"]["reasons"]


def test_evaluate_rollout_health_rolls_back_when_prod_window_below_7d() -> None:
    artifact = _artifact()
    artifact["retirement_gate"] = _retirement_gate(
        environment="prod",
        production_green_days=5,
        completed_requests_by_call={"nwo_veni_2025_preproposal": 55},
    )

    result = evaluate_rollout_health(artifact)

    assert result["overall"]["pass"] is False
    assert result["overall"]["recommended_action"] == "rollback"
    assert "prod_window_incomplete" in result["overall"]["reasons"]


def test_evaluate_rollout_health_rolls_back_when_prod_call_samples_below_50() -> None:
    artifact = _artifact()
    artifact["retirement_gate"] = _retirement_gate(
        environment="prod",
        production_green_days=7,
        completed_requests_by_call={
            "nwo_veni_2025_preproposal": 50,
            "erc_stg_2026_full": 22,
        },
    )

    result = evaluate_rollout_health(artifact)

    assert result["overall"]["pass"] is False
    assert result["overall"]["recommended_action"] == "rollback"
    assert "prod_sample_size_insufficient" in result["overall"]["reasons"]


def test_evaluate_rollout_health_proceeds_when_prod_gate_defaults_met() -> None:
    artifact = _artifact()
    artifact["retirement_gate"] = _retirement_gate(
        environment="prod",
        production_green_days=7,
        completed_requests_by_call={
            "nwo_veni_2025_preproposal": 64,
            "erc_stg_2026_full": 50,
        },
    )

    result = evaluate_rollout_health(artifact)

    assert result["overall"]["pass"] is True
    assert result["overall"]["recommended_action"] == "proceed"


def test_evaluate_rollout_health_strict_mode_rolls_back_without_retirement_gate() -> None:
    artifact = _artifact()

    result = evaluate_rollout_health(artifact, require_retirement_gate=True)

    assert result["overall"]["pass"] is False
    assert result["overall"]["recommended_action"] == "rollback"
    assert "retirement_gate_missing" in result["overall"]["reasons"]


def test_evaluate_rollout_health_rolls_back_when_prod_samples_missing() -> None:
    artifact = _artifact()
    artifact["retirement_gate"] = _retirement_gate(
        environment="prod",
        production_green_days=7,
    )

    result = evaluate_rollout_health(artifact)

    assert result["overall"]["pass"] is False
    assert result["overall"]["recommended_action"] == "rollback"
    assert "prod_sample_size_insufficient" in result["overall"]["reasons"]
