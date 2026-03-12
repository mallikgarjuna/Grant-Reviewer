"""backend/tests/test_ingest_call_dry_run.py
Regression checks for V1/V2 dry-run ingestion without DB configuration.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.ingest_call as ingest_call_module
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
    monkeypatch.setattr(
        ingest_call_module,
        "WF0061_MSCA_PF_2025_MANIFEST_PATH",
        tmp_path / "missing.sources.md",
    )

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
    monkeypatch.setattr(
        ingest_call_module,
        "WF0061_MSCA_PF_2025_MANIFEST_PATH",
        tmp_path / "missing.sources.md",
    )

    with pytest.raises(ValueError, match="source-upload gate"):
        ingest_call(msca_yaml, dry_run=True)


@pytest.mark.no_db
def test_wf0061_contract_non_dry_run_ingest_stops_before_db_when_manifest_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """WF-0061 gate should block non-dry-run ingest before any DB wiring is required."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    source_yaml = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml")
    yaml_text = source_yaml.read_text(encoding="utf-8").replace(
        "code: nwo_veni_2025_preproposal",
        "code: MSCA-PF-2025",
        1,
    )
    msca_yaml = tmp_path / "msca_pf_2025_full.yaml"
    msca_yaml.write_text(yaml_text, encoding="utf-8")
    monkeypatch.setattr(
        ingest_call_module,
        "WF0061_MSCA_PF_2025_MANIFEST_PATH",
        tmp_path / "missing.sources.md",
    )

    with pytest.raises(ValueError, match="source-upload gate"):
        ingest_call(msca_yaml, dry_run=False)


@pytest.mark.no_db
def test_wf0073_contract_erc_poc_2026_manifest_gate_fails_closed_on_missing_required_traceability(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """WF-0073 gate should fail closed when PoC source traceability is incomplete."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    source_yaml = Path("data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml")
    yaml_text = source_yaml.read_text(encoding="utf-8").replace(
        "code: nwo_veni_2025_preproposal",
        "code: ERC-2026-PoC",
        1,
    )
    poc_yaml = tmp_path / "erc_poc_2026_full.yaml"
    poc_yaml.write_text(yaml_text, encoding="utf-8")

    invalid_manifest_cases = (
        (
            "missing_used_for",
            """# temp manifest
## Source 1
- SHA256: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Used for:
  - proposal structure
## Source 2
- SHA256: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
""",
        ),
        (
            "missing_sha256",
            """# temp manifest
1) **Application Form (PoC)**
- Used for:
  - proposal structure
2) **ERC Work Programme 2026 (Primary for evaluation criteria/elements)**
- SHA256: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- Used for:
  - evaluation criteria/elements
3) **Information for Applicants (PoC)**
- SHA256: `cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc`
- Used for:
  - cross-check only
""",
        ),
        (
            "missing_required_source_class",
            """# temp manifest
1) **Application Form (PoC)**
- SHA256: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Used for:
  - proposal structure
2) **Information for Applicants (PoC)**
- SHA256: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- Used for:
  - proposal structure cross-check
""",
        ),
        (
            "single_entry_claims_both_required_classes",
            """# temp manifest
1) **Combined source**
- SHA256: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Used for:
  - proposal/application structure and evaluation criteria/elements
""",
        ),
        (
            "missing_used_for_in_required_evaluation_block_with_optional_present",
            """# temp manifest
1) **Application Form (PoC)**
- SHA256: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Used for:
  - proposal structure
2) **ERC Work Programme 2026 (Primary for evaluation criteria/elements)**
- SHA256: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
3) **Information for Applicants (PoC)**
- SHA256: `cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc`
- Used for:
  - cross-check only
""",
        ),
    )

    for case_name, manifest_text in invalid_manifest_cases:
        manifest_path = tmp_path / f"{case_name}.sources.md"
        manifest_path.write_text(manifest_text, encoding="utf-8")
        monkeypatch.setattr(
            ingest_call_module,
            "WF0073_ERC_POC_2026_MANIFEST_PATH",
            manifest_path,
            raising=False,
        )
        with pytest.raises(ValueError, match="ERC-2026-PoC source-manifest gate"):
            ingest_call(poc_yaml, dry_run=True)


@pytest.mark.no_db
def test_wf0073_contract_erc_poc_2026_dry_run_passes_with_single_step_source_grounded_yaml(
    monkeypatch,
) -> None:
    """WF-0073 should dry-run the PoC canonical YAML with single-step semantics."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    result = ingest_call(
        Path("data/calls/canonical/erc/erc_poc_2026_full.yaml"),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["schema_version"] == "v2"
    assert result["source_path"] == "data/calls/canonical/erc/erc_poc_2026_full.yaml"
    assert result["funding_call"]["code"] == "ERC-2026-PoC"
    assert result["funding_call"]["stage"] == "single-step"
    assert (
        result["canonical_json"]["runtime_config"]["split_visibility_reviewability_enabled"]
        is False
    )


@pytest.mark.no_db
def test_wf0074_contract_erc_poc_2026_subordinate_prompt_proof_call_dry_run(
    monkeypatch,
) -> None:
    """WF-0074 proof-call should dry-run with subordinate prompt fidelity intact."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    result = ingest_call(
        Path("data/calls/canonical/erc/erc_poc_2026_full.yaml"),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["schema_version"] == "v2"
    assert result["source_path"] == "data/calls/canonical/erc/erc_poc_2026_full.yaml"

    funding_call = result["funding_call"]
    assert funding_call["code"] == "ERC-2026-PoC"

    canonical_json = result["canonical_json"]
    criteria = canonical_json["evaluation_criteria"]
    assert isinstance(criteria, list)
    first_criterion = criteria[0]
    assert isinstance(first_criterion, dict)
    elements = first_criterion["evaluation_elements"]
    assert isinstance(elements, list)
    first_element = elements[0]
    second_element = elements[1]
    third_element = elements[2]
    assert isinstance(first_element, dict)
    assert isinstance(second_element, dict)
    assert isinstance(third_element, dict)
    first_subordinate_prompts = first_element["subordinate_prompts"]
    second_subordinate_prompts = second_element["subordinate_prompts"]
    third_subordinate_prompts = third_element["subordinate_prompts"]
    assert isinstance(first_subordinate_prompts, list)
    assert isinstance(second_subordinate_prompts, list)
    assert isinstance(third_subordinate_prompts, list)
    assert [prompt["id"] for prompt in first_subordinate_prompts] == [
        "prompt_innovation_business_or_societal_impact",
        "prompt_expected_outcomes_distinctiveness",
        "prompt_high_risk_high_gain",
        "prompt_breakthrough_innovation_outcome",
        "prompt_overcome_difficult_aspects",
    ]
    assert [prompt["id"] for prompt in second_subordinate_prompts] == [
        "prompt_activities_and_planning_path_to_innovation",
        "prompt_timescales_resources_qualified_personnel",
    ]
    assert [prompt["id"] for prompt in third_subordinate_prompts] == [
        "prompt_pi_clear_vision_strategic_decisions_risk_contingency"
    ]

    assert set(canonical_json["runtime_config"]) == {
        "split_visibility_reviewability_enabled"
    }
