"""backend/scripts/run_review_batch.py
WF-0068 locked-batch runner for raw review outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.engine.pipeline_v1 import run_review_pipeline
from app.engine.review_request_validator import (
    canonicalize_for_digest,
    validate_review_request_payload,
)

LOCKED_CALL_TO_PATH: dict[str, str] = {
    "nwo_veni_2025_preproposal": "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml",
    "erc_stg_2026_full": "data/calls/canonical/erc/erc_stg_2026_full.yaml",
    "MSCA-PF-2025": "data/calls/canonical/msca/msca_pf_2025_full.yaml",
}
REQUIRED_ROLES: set[str] = {
    "baseline_representative",
    "traceability_specificity_stress",
    "actionability_prioritization_stress",
}
REQUIRED_ITEM_COUNT = 9


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"INVALID_JSON_OBJECT: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _validate_baseline(baseline: dict[str, Any]) -> str:
    baseline_id = baseline.get("baseline_id")
    if not isinstance(baseline_id, str) or not baseline_id.strip():
        raise ValueError("BASELINE_INVALID: missing baseline_id")
    return baseline_id


def _validate_manifest(
    manifest: dict[str, Any],
    *,
    baseline_id: str,
) -> list[dict[str, Any]]:
    coverage_status = manifest.get("coverage_status")
    if coverage_status != "locked":
        raise ValueError("COVERAGE_STATUS_NOT_LOCKED")

    baseline_id_ref = manifest.get("baseline_id_ref")
    if baseline_id_ref != baseline_id:
        raise ValueError("BASELINE_REFERENCE_MISMATCH: manifest baseline_id_ref differs")

    locked_call_ids = manifest.get("locked_call_ids")
    if not isinstance(locked_call_ids, list):
        raise ValueError("WEDGE_DRIFT: missing locked_call_ids")
    locked_call_set = {str(call_id) for call_id in locked_call_ids}
    expected_call_set = set(LOCKED_CALL_TO_PATH)
    if locked_call_set != expected_call_set:
        raise ValueError("WEDGE_DRIFT: locked_call_ids must match representative wedge")

    raw_items = manifest.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("ITEM_COUNT_DRIFT: items must be a list")
    if len(raw_items) != REQUIRED_ITEM_COUNT:
        raise ValueError("ITEM_COUNT_DRIFT: expected exactly 9 items")

    items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            raise ValueError(f"INVALID_ITEM: items[{index}] must be object")
        item = dict(raw_item)
        call_id = str(item.get("call_id", ""))
        if call_id not in expected_call_set:
            raise ValueError("WEDGE_DRIFT: item call_id outside locked wedge")
        if "baseline_id" in item and item["baseline_id"] != baseline_id:
            raise ValueError("BASELINE_REFERENCE_MISMATCH: per-item baseline_id override")
        if "baseline_id_ref" in item and item["baseline_id_ref"] != baseline_id:
            raise ValueError("BASELINE_REFERENCE_MISMATCH: per-item baseline_id_ref override")
        items.append(item)

    call_to_roles: dict[str, set[str]] = {call_id: set() for call_id in expected_call_set}
    for item in items:
        call_to_roles[str(item["call_id"])].add(str(item.get("role", "")))
    for call_id, roles in call_to_roles.items():
        if roles != REQUIRED_ROLES:
            raise ValueError(f"ROLE_MATRIX_DRIFT: roles mismatch for {call_id}")

    batch_orders: list[int] = []
    for item in items:
        batch_order = item.get("batch_order")
        if not isinstance(batch_order, int) or batch_order < 1:
            raise ValueError("BATCH_ORDER_INVALID: batch_order must be positive integer")
        batch_orders.append(batch_order)
    if len(set(batch_orders)) != len(batch_orders):
        raise ValueError("BATCH_ORDER_INVALID: duplicate batch_order detected")
    expected_orders = set(range(1, REQUIRED_ITEM_COUNT + 1))
    if set(batch_orders) != expected_orders:
        raise ValueError("BATCH_ORDER_INVALID: batch_order must be contiguous 1..9")

    return items


def _build_snapshot_from_call_yaml(call_path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(call_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"INVALID_CALL_YAML: {call_path}")

    proposal_nodes = payload.get("proposal_nodes")
    if not isinstance(proposal_nodes, list):
        raise ValueError(f"INVALID_CALL_YAML_PROPOSAL_NODES: {call_path}")

    expectations: list[dict[str, Any]] = []
    for node in proposal_nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            continue
        node_expectations = node.get("node_expectations", [])
        if not isinstance(node_expectations, list):
            continue
        for node_expectation in node_expectations:
            if not isinstance(node_expectation, dict):
                continue
            evaluation_element_id = node_expectation.get("evaluation_element_id")
            if not isinstance(evaluation_element_id, str) or not evaluation_element_id:
                continue
            expectation_payload: dict[str, Any] = {
                "expectation_id": f"{node_id}:{evaluation_element_id}",
                "node_logical_id": node_id,
            }
            if node_expectation.get("expectation_strength") == "MANDATORY":
                expectation_payload["required"] = True
            expectations.append(expectation_payload)

    return {
        "schema_version": "v1",
        "expectations": expectations,
    }


def _run_manifest_item(
    *,
    item: dict[str, Any],
    baseline_id: str,
    batch_id: str,
) -> dict[str, Any]:
    call_id = str(item["call_id"])
    call_path = Path(LOCKED_CALL_TO_PATH[call_id])
    stage_ref = str(item.get("review_stage", "STEP_1"))
    node_logical_id = str(item.get("node_logical_id", ""))
    snippet_text = str(item.get("snippet_text", ""))

    if not node_logical_id:
        raise ValueError(f"INVALID_ITEM: missing node_logical_id for {item.get('item_id')}")

    snapshot = _build_snapshot_from_call_yaml(call_path)
    digest = "sha256:" + hashlib.sha256(
        canonicalize_for_digest(snapshot).encode("utf-8")
    ).hexdigest()
    request_payload = {
        "request_id": f"{batch_id}:{item.get('item_id', 'unknown')}",
        "mode": "DIAGNOSTIC",
        "stage_ref": stage_ref,
        "call_config_digest": digest,
        "call_config_snapshot": snapshot,
        "proposal_nodes": {node_logical_id: snippet_text},
    }
    request = validate_review_request_payload(request_payload)
    pipeline_result = run_review_pipeline(request)

    return {
        "item_id": item.get("item_id"),
        "batch_order": item.get("batch_order"),
        "call_id": call_id,
        "role": item.get("role"),
        "snippet_id": item.get("snippet_id"),
        "review_stage": stage_ref,
        "node_logical_id": node_logical_id,
        "baseline_id": baseline_id,
        "call_config_snapshot_ref": str(call_path),
        "call_config_digest": digest,
        "raw_review_output": pipeline_result.to_dict(),
    }


def run_review_batch(
    *,
    manifest_path: Path,
    baseline_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    manifest = _load_json_object(manifest_path)
    baseline = _load_json_object(baseline_path)

    baseline_id = _validate_baseline(baseline)
    batch_id = str(manifest.get("batch_id", ""))
    if not batch_id:
        raise ValueError("INVALID_BATCH_ID")

    items = _validate_manifest(manifest, baseline_id=baseline_id)

    sorted_items = sorted(items, key=lambda item: int(item.get("batch_order", 0)))
    outputs = [
        _run_manifest_item(item=item, baseline_id=baseline_id, batch_id=batch_id)
        for item in sorted_items
    ]

    payload = {
        "source_path": str(output_path),
        "artifact_type": "wf0068_raw_review_outputs",
        "batch_id": batch_id,
        "coverage_status": manifest.get("coverage_status"),
        "baseline_id": baseline_id,
        "manifest_ref": str(manifest_path),
        "baseline_ref": str(baseline_path),
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "items": outputs,
    }
    _write_json(output_path, payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WF-0068 locked-batch runner for raw review outputs.",
    )
    parser.add_argument("manifest", type=Path, help="Locked snippet batch manifest path")
    parser.add_argument("--baseline", type=Path, required=True, help="Baseline JSON path")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    run_review_batch(
        manifest_path=args.manifest,
        baseline_path=args.baseline,
        output_path=args.output,
    )
    print(f"Wrote WF-0068 raw review outputs: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
