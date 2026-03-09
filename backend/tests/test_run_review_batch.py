"""backend/tests/test_run_review_batch.py
WF-0068 tests for locked-batch raw-output runner.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts.run_review_batch import run_review_batch

pytestmark = [pytest.mark.no_db]


def _fixture_manifest() -> dict[str, Any]:
    fixture_path = Path("tests/fixtures/wf_0068_review_batch.json")
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _baseline_payload(*, baseline_id: str = "wf0068_baseline_v1") -> dict[str, Any]:
    return {
        "source_path": "docs/walkthroughs/evidence/WF-0068/baseline.json",
        "baseline_id": baseline_id,
        "app_commit_sha": "ce6c8cf3df4aa664f3dc3eb81846dc1b321723b3",
        "app_branch_ref": "wf/WF-0068-review-quality-evaluation-loop",
        "prompt_config_ref": "backend/app/services/prompt_builder.py::build_prompt_from_node",
        "model_runtime_ref": "backend/app/services/llm_client.py::LLM_MODE=stub",
        "reviewer_instruction_ref": "backend/data/calls/canonical/{nwo,erc,msca}/*.yaml::reviewer_policy",
        "evidence_template_version": "wf0068_evidence_template_v1",
        "dimension_scale": ["pass", "weak", "fail", "insufficient_evidence"],
    }


def test_wf0068_batch_runner_persists_locked_batch_outputs(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    baseline_path = tmp_path / "baseline.json"
    output_path = tmp_path / "raw_outputs.json"

    _write_json(manifest_path, _fixture_manifest())
    _write_json(baseline_path, _baseline_payload())

    payload = run_review_batch(
        manifest_path=manifest_path,
        baseline_path=baseline_path,
        output_path=output_path,
    )

    assert payload["batch_id"] == "wf0068_fixture_batch_v1"
    assert len(payload["items"]) == 9
    assert output_path.exists()
    assert {item["baseline_id"] for item in payload["items"]} == {"wf0068_baseline_v1"}


def test_wf0068_batch_runner_rejects_wedge_drift(tmp_path: Path) -> None:
    manifest = _fixture_manifest()
    manifest["items"][0]["call_id"] = "erc_cog_2026_full"

    manifest_path = tmp_path / "manifest_wedge_drift.json"
    baseline_path = tmp_path / "baseline.json"
    output_path = tmp_path / "raw_outputs.json"

    _write_json(manifest_path, manifest)
    _write_json(baseline_path, _baseline_payload())

    with pytest.raises(ValueError, match="WEDGE_DRIFT"):
        run_review_batch(
            manifest_path=manifest_path,
            baseline_path=baseline_path,
            output_path=output_path,
        )


def test_wf0068_batch_runner_rejects_baseline_reference_mismatch(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    baseline_path = tmp_path / "baseline_mismatch.json"
    output_path = tmp_path / "raw_outputs.json"

    _write_json(manifest_path, _fixture_manifest())
    _write_json(baseline_path, _baseline_payload(baseline_id="wf0068_baseline_other"))

    with pytest.raises(ValueError, match="BASELINE_REFERENCE_MISMATCH"):
        run_review_batch(
            manifest_path=manifest_path,
            baseline_path=baseline_path,
            output_path=output_path,
        )


def test_wf0068_batch_runner_rejects_invalid_batch_order(tmp_path: Path) -> None:
    manifest = _fixture_manifest()
    manifest["items"][0]["batch_order"] = "first"
    manifest["items"][1]["batch_order"] = 1

    manifest_path = tmp_path / "manifest_bad_order.json"
    baseline_path = tmp_path / "baseline.json"
    output_path = tmp_path / "raw_outputs.json"

    _write_json(manifest_path, manifest)
    _write_json(baseline_path, _baseline_payload())

    with pytest.raises(ValueError, match="BATCH_ORDER_INVALID"):
        run_review_batch(
            manifest_path=manifest_path,
            baseline_path=baseline_path,
            output_path=output_path,
        )


def test_wf0068_batch_runner_rejects_duplicate_item_ids(tmp_path: Path) -> None:
    manifest = _fixture_manifest()
    manifest["items"][1]["item_id"] = manifest["items"][0]["item_id"]

    manifest_path = tmp_path / "manifest_duplicate_item_id.json"
    baseline_path = tmp_path / "baseline.json"
    output_path = tmp_path / "raw_outputs.json"

    _write_json(manifest_path, manifest)
    _write_json(baseline_path, _baseline_payload())

    with pytest.raises(ValueError, match="ITEM_ID_INVALID"):
        run_review_batch(
            manifest_path=manifest_path,
            baseline_path=baseline_path,
            output_path=output_path,
        )
