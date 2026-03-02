"""Regression checks for V1/V2 dry-run ingestion without DB configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.ingest_call import ingest_call


@pytest.mark.no_db
def test_dry_run_supports_v1_and_v2_without_database_url(
    monkeypatch,
) -> None:
    """V1/V2 dry-run should validate YAML without requiring DATABASE_URL."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    v2_result = ingest_call(
        Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"),
        dry_run=True,
    )
    assert v2_result["dry_run"] is True
    assert v2_result["schema_version"] == "v2"
    assert v2_result["source_path"] == "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"

    v1_result = ingest_call(
        Path("tests/fixtures/edge_case_call.yaml"),
        dry_run=True,
    )
    assert v1_result["dry_run"] is True
    assert v1_result["schema_version"] == "v1"
    assert v1_result["source_path"] == "tests/fixtures/edge_case_call.yaml"


@pytest.mark.no_db
def test_dry_run_ingests_erc_cog_2026_full_canonical_v2(
    monkeypatch,
) -> None:
    """ERC CoG canonical v2 call should dry-run ingest without DATABASE_URL."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    result = ingest_call(
        Path("data/calls/canonical/erc/erc_cog_2026_full.yaml"),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["schema_version"] == "v2"
    assert result["source_path"] == "data/calls/canonical/erc/erc_cog_2026_full.yaml"
