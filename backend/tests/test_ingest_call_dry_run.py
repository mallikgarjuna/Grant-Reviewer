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


@pytest.mark.no_db
def test_dry_run_ingests_nwo_veni_2025_preproposal_with_wf0044_manifest_traceability(
    monkeypatch,
) -> None:
    """NWO Veni dry-run should validate and expose WF-0044 source-copy traceability."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    result = ingest_call(
        Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["schema_version"] == "v2"
    assert (
        result["source_path"]
        == "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml"
    )

    manifest = Path("data/calls/sources/nwo_veni_2025_preproposal.sources.md").read_text(
        encoding="utf-8"
    )
    assert (
        "Path (copied local): "
        "`backend/data/calls/source_files/WF-0044/nwo_veni_2025_preproposal/"
        in manifest
    )


@pytest.mark.no_db
def test_dry_run_ingests_nwo_vidi_2025_full_proposal_with_wf0044_manifest_traceability(
    monkeypatch,
) -> None:
    """NWO Vidi dry-run should validate and expose WF-0044 source-copy traceability."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    result = ingest_call(
        Path("data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml"),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["schema_version"] == "v2"
    assert (
        result["source_path"]
        == "data/calls/canonical/nwo/nwo_vidi_2025_full_proposal.yaml"
    )

    manifest = Path(
        "data/calls/sources/nwo_vidi_2025_full_proposal.sources.md"
    ).read_text(encoding="utf-8")
    assert (
        "Path (copied local): "
        "`backend/data/calls/source_files/WF-0044/nwo_vidi_2025_full_proposal/"
        in manifest
    )


@pytest.mark.no_db
def test_dry_run_ingests_erc_stg_2026_full_with_wf0044_manifest_traceability(
    monkeypatch,
) -> None:
    """ERC StG dry-run should validate and expose WF-0044 source-copy traceability."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    result = ingest_call(
        Path("data/calls/canonical/erc/erc_stg_2026_full.yaml"),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["schema_version"] == "v2"
    assert result["source_path"] == "data/calls/canonical/erc/erc_stg_2026_full.yaml"

    manifest = Path("data/calls/sources/erc_stg_2026_full.sources.md").read_text(
        encoding="utf-8"
    )
    assert (
        "Path (copied local): "
        "`backend/data/calls/source_files/WF-0044/erc_stg_2026_full/"
        in manifest
    )


@pytest.mark.no_db
def test_wf0061_contract_ingest_blocks_msca_pf_2025_without_two_uploaded_sources(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """WF-0061 gate should fail closed without the required MSCA source manifest."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    source_yaml = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml")
    yaml_text = source_yaml.read_text(encoding="utf-8").replace(
        "code: nwo_veni_2025_preproposal",
        "code: MSCA-PF-2025",
        1,
    )
    msca_yaml = tmp_path / "msca_pf_2025_full.yaml"
    msca_yaml.write_text(yaml_text, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="MSCA-PF-2025 source-upload gate"):
        ingest_call(msca_yaml, dry_run=True)


@pytest.mark.no_db
def test_wf0061_contract_msca_pf_2025_dry_run_passes_with_uploaded_sources(
    monkeypatch,
) -> None:
    """WF-0061 should dry-run the real MSCA-PF-2025 canonical call after upload gate."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    result = ingest_call(
        Path("data/calls/canonical/msca/msca_pf_2025_full.yaml"),
        dry_run=True,
    )
    assert result["dry_run"] is True
    assert result["schema_version"] == "v2"
    assert result["source_path"] == "data/calls/canonical/msca/msca_pf_2025_full.yaml"

    manifest = Path("data/calls/sources/msca_pf_2025_full.sources.md").read_text(
        encoding="utf-8"
    )
    assert "MSCA" in manifest
    assert "Used for:" in manifest
    assert "SHA256:" in manifest


@pytest.mark.no_db
def test_wf0061_contract_ingest_gate_blocks_runtime_credit_without_uploaded_msca_manifest(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """WF-0061 runtime-credit guard: no manifest means no ingest proof credit."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    source_yaml = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml")
    yaml_text = source_yaml.read_text(encoding="utf-8").replace(
        "code: nwo_veni_2025_preproposal",
        "code: MSCA-PF-2025",
        1,
    )
    msca_yaml = tmp_path / "msca_pf_2025_full.yaml"
    msca_yaml.write_text(yaml_text, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="source-upload gate"):
        ingest_call(msca_yaml, dry_run=True)
